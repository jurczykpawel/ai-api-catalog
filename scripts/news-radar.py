#!/usr/bin/env python3
"""
news-radar.py
Pobiera RSS z serwisów AI, wykrywa nowe modele przez LLM (Anthropic → OpenAI fallback),
wypisuje propozycje wpisów do models-manual.json.

Użycie:
  python3 scripts/news-radar.py
  python3 scripts/news-radar.py --hours 48   # artykuły z ostatnich 48h
  python3 scripts/news-radar.py --dry-run    # bez wywołania LLM (pokaż artykuły)
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import llm_complete

RSS_FEEDS = [
    ("The Decoder",      "https://the-decoder.com/feed/"),
    ("VentureBeat AI",   "https://venturebeat.com/feed/"),
    ("HuggingFace Blog", "https://huggingface.co/blog/feed.xml"),
    ("TechCrunch AI",    "https://techcrunch.com/category/artificial-intelligence/feed"),
    ("The Verge AI",     "https://www.theverge.com/rss/index.xml"),
    ("OpenAI Blog",      "https://openai.com/news/rss.xml"),
]

PROPOSALS_PATH = Path("/tmp/news-radar-proposals.json")

SYSTEM_PROMPT = """You are an AI model tracker. Your job is to extract newly announced or released AI models from news articles.

Focus ONLY on:
- New AI models with API access (LLMs, image gen, video gen, audio, embeddings)
- New versions of existing models
- Models newly available on a provider API

Ignore:
- Research papers without API availability
- Open-source models without clear API provider
- Generic AI features (not specific models)
- Marketing announcements without actual model release

For each model found, return a JSON array with objects like:
{
  "name": "Model Name",
  "provider": "company/provider name",
  "category": "llm|image_generation|video_generation|audio_tts|audio_stt|music_generation|embedding",
  "source_title": "article title",
  "source_url": "article url",
  "notes": "brief description, pricing if mentioned"
}

If no relevant models found, return empty array: []
Return ONLY valid JSON, no other text."""


def fetch_feed(name: str, url: str, cutoff: datetime) -> list[dict]:
    """Fetch RSS feed and return articles newer than cutoff."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ai-api-catalog/1.0)",
            "Accept": "application/rss+xml, application/xml, text/xml",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
    except Exception as e:
        print(f"  ⚠ {name}: {e}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"  ⚠ {name}: XML parse error: {e}", file=sys.stderr)
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    articles = []

    # RSS 2.0
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link") or "").strip()
        pub   = item.findtext("pubDate") or ""
        desc  = (item.findtext("description") or "").strip()[:500]
        try:
            pub_dt = parsedate_to_datetime(pub).astimezone(timezone.utc) if pub else None
        except Exception:
            pub_dt = None
        if pub_dt and pub_dt < cutoff:
            continue
        if title and link:
            articles.append({"title": title, "url": link, "desc": desc, "source": name})

    # Atom
    for entry in root.findall(".//atom:entry", ns):
        title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
        link_el = entry.find("atom:link", ns)
        link  = (link_el.get("href", "") if link_el is not None else "").strip()
        pub   = entry.findtext("atom:updated", namespaces=ns) or entry.findtext("atom:published", namespaces=ns) or ""
        desc  = (entry.findtext("atom:summary", namespaces=ns) or "").strip()[:500]
        try:
            pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00")).astimezone(timezone.utc) if pub else None
        except Exception:
            pub_dt = None
        if pub_dt and pub_dt < cutoff:
            continue
        if title and link:
            articles.append({"title": title, "url": link, "desc": desc, "source": name})

    return articles


def _save_empty_proposals():
    """Save empty proposals file so downstream steps don't fail."""
    with open(PROPOSALS_PATH, "w") as f:
        json.dump([], f)


def detect_models(articles: list[dict]) -> list[dict]:
    """Send articles to LLM and get model suggestions."""
    articles_text = "\n\n".join(
        f"[{a['source']}] {a['title']}\nURL: {a['url']}\n{a['desc']}"
        for a in articles
    )

    text = llm_complete(
        system=SYSTEM_PROMPT,
        user=f"Extract new AI models from these articles:\n\n{articles_text}",
        tier="fast",
    )

    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def check_existing(model_name: str, provider: str) -> bool:
    """Check if model already exists in models.json."""
    models_path = Path("data/models.json")
    if not models_path.exists():
        return False
    with open(models_path) as f:
        data = json.load(f)
    name_lower = model_name.lower()
    for m in data.get("models", []):
        if name_lower in m.get("name", "").lower():
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours",   type=int, default=24, help="Look back N hours (default: 24)")
    parser.add_argument("--dry-run", action="store_true",  help="Fetch articles but skip Claude call")
    args = parser.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    print(f"→ Szukam artykułów z ostatnich {args.hours}h (od {cutoff.strftime('%Y-%m-%d %H:%M UTC')})")
    print()

    # 1. Fetch feeds
    all_articles = []
    for name, url in RSS_FEEDS:
        articles = fetch_feed(name, url, cutoff)
        print(f"  {name}: {len(articles)} artykułów")
        all_articles.extend(articles)

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in all_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    print(f"\n  Łącznie: {len(unique)} unikalnych artykułów")

    if not unique:
        print("\n✓ Brak nowych artykułów.")
        _save_empty_proposals()
        return

    if args.dry_run:
        print("\n--- DRY RUN: artykuły (bez wywołania Claude) ---")
        for a in unique:
            print(f"  [{a['source']}] {a['title']}")
            print(f"    {a['url']}")
        _save_empty_proposals()
        return

    # 2. Call LLM (Anthropic → OpenAI fallback)
    print("\n→ Wysyłam do LLM...")
    try:
        models = detect_models(unique)
    except Exception as e:
        print(f"✗ LLM error: {e}", file=sys.stderr)
        sys.exit(1)

    if not models:
        print("✓ Brak nowych modeli AI w artykułach.")
        _save_empty_proposals()
        return

    print(f"\n✓ LLM wykrył {len(models)} potencjalnych nowych modeli:\n")

    # 3. Check which already exist
    new_models = []
    for m in models:
        exists = check_existing(m.get("name", ""), m.get("provider", ""))
        status = "⚠ JUŻ W KATALOGU" if exists else "✨ NOWY"
        print(f"  {status}: {m.get('name')} ({m.get('provider')}) [{m.get('category')}]")
        print(f"    {m.get('notes', '')}")
        print(f"    Źródło: {m.get('source_title')} — {m.get('source_url')}")
        print()
        if not exists:
            new_models.append(m)

    if not new_models:
        print("✓ Wszystkie wykryte modele już są w katalogu.")
        _save_empty_proposals()
        return

    # 4. Show what would go into models-manual.json
    print(f"\n{'='*60}")
    print(f"PROPOZYCJA dla models-manual.json ({len(new_models)} wpisów):")
    print(f"{'='*60}\n")

    today = datetime.now().strftime("%Y-%m-%d")
    proposals = []
    for m in new_models:
        entry = {
            "id": m.get("name", "").lower().replace(" ", "-").replace("/", "-"),
            "name": m.get("name", ""),
            "category": m.get("category", "llm"),
            "description": m.get("notes", ""),
            "tags": [m.get("provider", "").lower()],
            "capabilities": [],
            "updated_at": today,
            "source": "news-radar",
            "providers": [
                {
                    "provider_id": m.get("provider", "").lower().replace(" ", ""),
                    "pricing": {"notes": "Sprawdź aktualną cenę"},
                    "url": m.get("source_url", ""),
                    "affiliate_url": None,
                    "available": True
                }
            ]
        }
        proposals.append(entry)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        print()

    # Save proposals to temp file
    with open(PROPOSALS_PATH, "w") as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)
    print(f"✓ Propozycje zapisane: {PROPOSALS_PATH}")


if __name__ == "__main__":
    main()
