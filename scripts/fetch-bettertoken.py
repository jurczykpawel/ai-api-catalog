#!/usr/bin/env python3
"""
fetch-bettertoken.py
Pobiera modele i ceny z publicznego API BetterToken.

API: https://bettertoken.ai/api/pricing (public, no auth)

Format (new-api):
  - quota_type 0 = rozliczanie za tokeny:
      input  USD / 1M = model_ratio * 2 * group_ratio
      output USD / 1M = input * completion_ratio
      cache  USD / 1M = input * cache_ratio
  - quota_type 1 = cena za wywołanie: model_price * group_ratio (USD)
  - group_ratio = najniższy ratio spośród enable_groups modelu
  - Modele bez stałej ceny (ratio 0, ceny progowe) dostają notes z linkiem do cennika

Użycie:
  python3 scripts/fetch-bettertoken.py [ścieżka-wyjściowa]
"""

import json, re, sys
import urllib.request
from pathlib import Path

OUTPUT_DEFAULT = "data/bettertoken-raw.json"
API_URL = "https://bettertoken.ai/api/pricing"
PRICING_PAGE = "https://bettertoken.ai/en/pricing/"

IMAGE_HINTS = ("image", "banana")


def _category(model_id: str, endpoints: list) -> str:
    mid = model_id.lower()
    if any(h in mid for h in IMAGE_HINTS) or "image-generation" in endpoints:
        return "image_generation"
    return "llm"


def _catalog_id(model_id: str) -> str:
    return model_id.lower().replace(".", "-")


def _make_name(model_id: str) -> str:
    parts = []
    for p in model_id.split("-"):
        if p.lower() in ("gpt", "glm"):
            parts.append(p.upper())
        elif re.match(r"^\d", p):
            parts.append(p)
        elif p.isupper():
            parts.append(p)
        else:
            parts.append(p[:1].upper() + p[1:])
    return " ".join(parts)


def _tags(model_id: str) -> list:
    mid = model_id.lower()
    tags = ["bettertoken"]
    for key, tag in (("claude", "anthropic"), ("gpt", "openai"), ("gemini", "google"),
                     ("banana", "google"), ("deepseek", "deepseek"), ("qwen", "alibaba"),
                     ("glm", "zhipu"), ("kimi", "moonshot"), ("minimax", "minimax")):
        if key in mid:
            tags.append(tag)
    if "flash" in mid or "haiku" in mid:
        tags.append("fast")
    return list(dict.fromkeys(tags))


def _round(x: float) -> float:
    return round(x, 4)


def fetch(output_path: str):
    print("→ BetterToken — pobieranie cennika z API...")
    req = urllib.request.Request(API_URL, headers={"User-Agent": "ai-api-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())

    if data.get("currency", "USD") != "USD":
        raise SystemExit(f"Nieoczekiwana waluta: {data.get('currency')}")

    group_ratio = data.get("group_ratio", {}) or {}
    items = data.get("data", [])
    print(f"  API zwróciło {len(items)} modeli")

    models, no_price = [], []
    for item in items:
        mid = item.get("model_name")
        if not mid:
            continue
        groups = item.get("enable_groups") or []
        ratios = [group_ratio[g] for g in groups if g in group_ratio]
        g = min(ratios) if ratios else 1.0
        endpoints = item.get("supported_endpoint_types") or []

        if item.get("quota_type") == 1 and item.get("model_price"):
            pricing = {"per_request": _round(item["model_price"] * g)}
        elif item.get("model_ratio"):
            inp = item["model_ratio"] * 2 * g
            pricing = {
                "input_per_1m": _round(inp),
                "output_per_1m": _round(inp * (item.get("completion_ratio") or 1)),
            }
            if item.get("cache_ratio"):
                pricing["notes"] = f"Cache read: ${_round(inp * item['cache_ratio'])}/1M"
        else:
            no_price.append(mid)
            pricing = {"notes": f"Tiered pricing, see {PRICING_PAGE}"}

        name = _make_name(mid)
        models.append({
            "id":           _catalog_id(mid),
            "name":         name,
            "category":     _category(mid, endpoints),
            "description":  f"{name} via BetterToken (OpenAI- and Anthropic-compatible gateway).",
            "tags":         _tags(mid),
            "capabilities": [],
            "pricing":      pricing,
            "context_k":    None,
            "url":          PRICING_PAGE,
            "_api_id":      mid,
        })

    if no_price:
        print(f"  ⚠ Brak stałej ceny dla {len(no_price)} modeli (progi): {no_price}")
    print(f"  {len(models)} modeli")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "models": models,
            "source": "bettertoken",
            "base_url": "https://bettertoken.ai/v1/",
            "note": f"Models and pricing from {API_URL}",
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ Zapisano: {out_path}")
    return models


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
