#!/usr/bin/env python3
"""
verify-models.py
Weryfikuje kandydatów na nowe modele z news-radar.py przez LLM (Anthropic -> OpenAI fallback).
Dla każdego kandydata sprawdza: API, provider, cenę, kategorię.
Zwraca decyzję: ADD / SKIP / REVIEW

Użycie:
  python3 scripts/verify-models.py                          # wczytuje /tmp/news-radar-proposals.json
  python3 scripts/verify-models.py --input proposals.json  # własny plik wejściowy
  python3 scripts/verify-models.py --dry-run               # pokaż kandydatów bez weryfikacji
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import llm_complete

KNOWN_PROVIDERS = [
    "openai", "anthropic", "google", "mistral", "deepseek", "xai", "groq",
    "cohere", "perplexity", "openrouter", "together", "fireworks", "replicate",
    "fal", "huggingface", "aimlapi", "runway", "minimax", "piapi", "wavespeed",
    "kie", "stabilityai", "bfl", "elevenlabs", "deepgram", "assemblyai", "suno",
]

VERIFY_SYSTEM = """You are a strict AI model catalog curator. Your job is to verify whether a detected AI model candidate should be added to a catalog of models available via public API.

Catalog criteria — a model MUST have ALL of the following:
1. Public API access (not just a product/feature/app)
2. Clear provider (one of the known providers or a new one with real API docs)
3. It's a model (LLM, image gen, video gen, TTS, STT, music, embedding) — NOT a product feature, agent, or app wrapper

Known providers (use their IDs as-is):
openai, anthropic, google, mistral, deepseek, xai, groq, cohere, perplexity,
openrouter, together, fireworks, replicate, fal, huggingface, aimlapi, runway,
minimax, piapi, wavespeed, kie, stabilityai, bfl, elevenlabs, deepgram, assemblyai, suno

Categories: llm | image_generation | video_generation | audio_tts | audio_stt | music_generation | embedding | moderation

For each candidate return a JSON object:
{
  "verdict": "ADD" | "SKIP" | "REVIEW",
  "reason": "one sentence why",
  "corrected": {
    "name": "corrected model name if needed",
    "provider_id": "correct provider_id from known list or new provider slug",
    "category": "correct category",
    "description": "concise 1-sentence description for catalog",
    "pricing_notes": "pricing info if found in article, else null",
    "api_url": "direct API/docs URL if known, else null"
  }
}

Verdicts:
- ADD: clearly a model with public API, ready to add
- SKIP: not a model (product feature, wrapper, research only, no public API)
- REVIEW: uncertain — API exists but pricing/provider unclear, or very new announcement

Return ONLY valid JSON, no other text."""


def verify_candidate(candidate: dict, article_context: str) -> dict:
    prompt = f"""Verify this AI model candidate:

Name: {candidate.get('name')}
Detected provider: {candidate.get('provider', '')}
Category: {candidate.get('category', '')}
Notes from article: {candidate.get('notes', '')}
Source article: {candidate.get('source_title', '')}
Source URL: {candidate.get('source_url', '')}

Additional article context:
{article_context}

Based on this, verify if it should be added to an AI API catalog."""

    text = llm_complete(
        system=VERIFY_SYSTEM,
        user=prompt,
        tier="smart",
        max_tokens=512,
    )

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def build_entry(candidate: dict, verification: dict) -> dict:
    """Build a models-manual.json entry from verified candidate."""
    corrected = verification.get("corrected", {})
    today = datetime.now().strftime("%Y-%m-%d")

    name = corrected.get("name") or candidate.get("name", "")
    provider_id = corrected.get("provider_id") or candidate.get("provider", "").lower().replace(" ", "")
    category = corrected.get("category") or candidate.get("category", "llm")
    description = corrected.get("description") or candidate.get("notes", "")
    pricing_notes = corrected.get("pricing_notes")
    api_url = corrected.get("api_url") or candidate.get("source_url", "")

    pricing = {"notes": pricing_notes} if pricing_notes else {"notes": "Check current pricing"}

    return {
        "id": name.lower().replace(" ", "-").replace("/", "-").replace(".", "-"),
        "name": name,
        "category": category,
        "description": description,
        "tags": [provider_id] if provider_id else [],
        "capabilities": [],
        "updated_at": today,
        "source": "news-radar",
        "providers": [
            {
                "provider_id": provider_id,
                "pricing": pricing,
                "url": api_url,
                "affiliate_url": None,
                "available": True,
            }
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   default="/tmp/news-radar-proposals.json",
                        help="Input proposals JSON (default: /tmp/news-radar-proposals.json)")
    parser.add_argument("--output",  default="/tmp/verified-proposals.json",
                        help="Output verified JSON (default: /tmp/verified-proposals.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show candidates without calling Claude")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ Brak pliku wejściowego: {input_path}", file=sys.stderr)
        print("  Uruchom najpierw: python3 scripts/news-radar.py", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        # news-radar saves entries in models-manual format, we need original candidates
        # Try to load as raw candidates first (from news-radar internal format)
        raw = json.load(f)

    # news-radar saves in models-manual format — convert back to candidate format for display
    candidates = []
    for entry in raw:
        candidates.append({
            "name": entry.get("name", ""),
            "provider": entry.get("tags", [""])[0] if entry.get("tags") else "",
            "category": entry.get("category", "llm"),
            "notes": entry.get("description", ""),
            "source_title": entry.get("name", ""),
            "source_url": entry.get("providers", [{}])[0].get("url", "") if entry.get("providers") else "",
        })

    print(f"→ {len(candidates)} kandydatów do weryfikacji\n")

    if args.dry_run:
        for c in candidates:
            print(f"  [{c['category']}] {c['name']} ({c['provider']})")
            print(f"    {c['notes']}")
            print()
        return

    print("→ Weryfikacja przez LLM...\n")

    results = {"add": [], "skip": [], "review": []}
    verified_entries = []

    for c in candidates:
        print(f"  Sprawdzam: {c['name']} ({c['provider']})...")
        try:
            verification = verify_candidate(c, "")
        except Exception as e:
            print(f"    ✗ Błąd API: {e}", file=sys.stderr)
            verification = {"verdict": "REVIEW", "reason": f"API error: {e}", "corrected": {}}

        verdict = verification.get("verdict", "REVIEW")
        reason = verification.get("reason", "")

        icon = {"ADD": "✅", "SKIP": "❌", "REVIEW": "⚠️"}.get(verdict, "❓")
        print(f"    {icon} {verdict}: {reason}")

        results[verdict.lower()].append(c["name"])

        if verdict in ("ADD", "REVIEW"):
            entry = build_entry(c, verification)
            verified_entries.append({
                "verdict": verdict,
                "reason": reason,
                "entry": entry,
            })

    print(f"\n{'='*60}")
    print(f"WYNIKI WERYFIKACJI:")
    print(f"  ✅ ADD:    {len(results['add'])} modeli")
    print(f"  ⚠️  REVIEW: {len(results['review'])} modeli")
    print(f"  ❌ SKIP:   {len(results['skip'])} modeli")
    print(f"{'='*60}\n")

    if not verified_entries:
        print("✓ Brak modeli do dodania.")
        return

    # Show ADD entries
    add_entries = [v for v in verified_entries if v["verdict"] == "ADD"]
    review_entries = [v for v in verified_entries if v["verdict"] == "REVIEW"]

    if add_entries:
        print(f"✅ DO DODANIA ({len(add_entries)}):\n")
        for v in add_entries:
            print(f"  {v['entry']['name']} [{v['entry']['category']}]")
            print(f"  → {v['reason']}")
            print(f"  {json.dumps(v['entry'], ensure_ascii=False, indent=4)}\n")

    if review_entries:
        print(f"⚠️  DO SPRAWDZENIA ({len(review_entries)}):\n")
        for v in review_entries:
            print(f"  {v['entry']['name']} [{v['entry']['category']}]")
            print(f"  → {v['reason']}\n")

    # Save verified ADD entries to output
    out_entries = [v["entry"] for v in add_entries]
    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(out_entries, f, ensure_ascii=False, indent=2)
    print(f"✓ Zweryfikowane wpisy (ADD) zapisane: {out_path}")
    print(f"  Aby dodać do katalogu:")
    print(f"  python3 scripts/apply-proposals.py --input {out_path}")


if __name__ == "__main__":
    main()
