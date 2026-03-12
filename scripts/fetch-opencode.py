#!/usr/bin/env python3
"""
fetch-opencode.py
Pobiera modele z OpenCode Zen public API i matchuje z curated pricing.

API: https://opencode.ai/zen/v1/models (public, no auth)
Pricing: curated z https://opencode.ai/docs/zen/#pricing

Strategia:
  - Lista modeli zawsze aktualna (z API)
  - Pricing curated — nowe modele bez wpisu dostają pricing=unknown
  - Modele z "free" w ID → pricing $0

Użycie:
  python3 scripts/fetch-opencode.py [ścieżka-wyjściowa]
"""

import json, re, sys
import urllib.request
from pathlib import Path

OUTPUT_DEFAULT = "data/opencode-raw.json"
API_URL = "https://opencode.ai/zen/v1/models"

# Pricing curated z https://opencode.ai/docs/zen/#pricing (2026-03-12)
# Klucz = model ID z API (z dotami jak leci)
PRICING: dict[str, dict] = {
    # Free
    "big-pickle":               {"input_per_1m": 0.0,  "output_per_1m": 0.0,   "notes": "Free"},
    "mimo-v2-flash-free":       {"input_per_1m": 0.0,  "output_per_1m": 0.0,   "notes": "Free"},
    "nemotron-3-super-free":    {"input_per_1m": 0.0,  "output_per_1m": 0.0,   "notes": "Free"},
    "minimax-m2.5-free":        {"input_per_1m": 0.0,  "output_per_1m": 0.0,   "notes": "Free"},
    "gpt-5-nano":               {"input_per_1m": 0.0,  "output_per_1m": 0.0,   "notes": "Free"},
    "trinity-large-preview-free": {"input_per_1m": 0.0, "output_per_1m": 0.0,  "notes": "Free"},
    # Claude
    "claude-haiku-4-5":         {"input_per_1m": 1.00, "output_per_1m": 5.00},
    "claude-3-5-haiku":         {"input_per_1m": 0.80, "output_per_1m": 4.00},
    "claude-sonnet-4-6":        {"input_per_1m": 3.00, "output_per_1m": 15.00, "notes": ">200K ctx: $6/$22.50"},
    "claude-sonnet-4-5":        {"input_per_1m": 3.00, "output_per_1m": 15.00, "notes": ">200K ctx: $6/$22.50"},
    "claude-sonnet-4":          {"input_per_1m": 3.00, "output_per_1m": 15.00, "notes": ">200K ctx: $6/$22.50"},
    "claude-opus-4-6":          {"input_per_1m": 5.00, "output_per_1m": 25.00, "notes": ">200K ctx: $10/$37.50"},
    "claude-opus-4-5":          {"input_per_1m": 5.00, "output_per_1m": 25.00},
    "claude-opus-4-1":          {"input_per_1m": 15.00,"output_per_1m": 75.00},
    # Gemini
    "gemini-3.1-pro":           {"input_per_1m": 2.00, "output_per_1m": 12.00, "notes": ">200K ctx: $4/$18"},
    "gemini-3-pro":             {"input_per_1m": 2.00, "output_per_1m": 12.00, "notes": ">200K ctx: $4/$18"},
    "gemini-3-flash":           {"input_per_1m": 0.50, "output_per_1m": 3.00},
    # GPT-5
    "gpt-5.4-pro":              {"input_per_1m": 30.00,"output_per_1m": 180.00},
    "gpt-5.4":                  {"input_per_1m": 2.50, "output_per_1m": 15.00},
    "gpt-5.3-codex-spark":      {"input_per_1m": 1.75, "output_per_1m": 14.00},
    "gpt-5.3-codex":            {"input_per_1m": 1.75, "output_per_1m": 14.00},
    "gpt-5.2":                  {"input_per_1m": 1.75, "output_per_1m": 14.00},
    "gpt-5.2-codex":            {"input_per_1m": 1.75, "output_per_1m": 14.00},
    "gpt-5.1":                  {"input_per_1m": 1.07, "output_per_1m": 8.50},
    "gpt-5.1-codex":            {"input_per_1m": 1.07, "output_per_1m": 8.50},
    "gpt-5.1-codex-max":        {"input_per_1m": 1.25, "output_per_1m": 10.00},
    "gpt-5.1-codex-mini":       {"input_per_1m": 0.25, "output_per_1m": 2.00},
    "gpt-5":                    {"input_per_1m": 1.07, "output_per_1m": 8.50},
    "gpt-5-codex":              {"input_per_1m": 1.07, "output_per_1m": 8.50},
    # Chinese
    "minimax-m2.5":             {"input_per_1m": 0.30, "output_per_1m": 1.20},
    "minimax-m2.1":             {"input_per_1m": 0.30, "output_per_1m": 1.20},
    "glm-5":                    {"input_per_1m": 1.00, "output_per_1m": 3.20},
    "glm-4.7":                  {"input_per_1m": 0.60, "output_per_1m": 2.20},
    "glm-4.6":                  {"input_per_1m": 0.60, "output_per_1m": 2.20},
    "kimi-k2.5":                {"input_per_1m": 0.60, "output_per_1m": 3.00},
    "kimi-k2-thinking":         {"input_per_1m": 0.40, "output_per_1m": 2.50},
    "kimi-k2":                  {"input_per_1m": 0.40, "output_per_1m": 2.50},
    "qwen3-coder":              {"input_per_1m": 0.45, "output_per_1m": 1.50},
}

# Metadata hints by prefix
def _guess_tags(model_id: str) -> list[str]:
    tags = ["opencode"]
    mid = model_id.lower()
    if "free" in mid:               tags.append("free")
    if "claude" in mid:             tags += ["anthropic", "claude"]
    if "gemini" in mid:             tags += ["google", "gemini"]
    if "gpt" in mid:                tags += ["openai", "gpt"]
    if "codex" in mid:              tags += ["coding", "codex"]
    if "minimax" in mid:            tags.append("minimax")
    if "glm" in mid:                tags += ["zhipu", "glm"]
    if "kimi" in mid:               tags += ["moonshot", "kimi"]
    if "qwen" in mid:               tags += ["alibaba", "qwen"]
    if "nemotron" in mid:           tags.append("nvidia")
    if "flash" in mid or "mini" in mid or "spark" in mid: tags.append("fast")
    if "thinking" in mid:           tags.append("reasoning")
    if "opus" in mid or "pro" in mid or "max" in mid:     tags.append("powerful")
    return list(dict.fromkeys(tags))  # deduplicate preserving order

def _guess_capabilities(model_id: str) -> list[str]:
    mid = model_id.lower()
    caps = []
    if any(x in mid for x in ["claude", "gemini", "gpt"]):
        caps.append("function_calling")
    if any(x in mid for x in ["claude", "gemini", "gpt-5.4"]):
        caps.append("vision")
    if "thinking" in mid:
        caps.append("reasoning")
    return caps

def _make_name(model_id: str) -> str:
    """Convert API model ID to display name."""
    name = model_id
    # Normalize: dots back to display-friendly version
    # e.g. "gpt-5.4-pro" → "GPT-5.4 Pro", "gemini-3.1-pro" → "Gemini 3.1 Pro"
    name = name.replace("-free", " Free")
    parts = name.split("-")
    result = []
    for p in parts:
        if p.upper() in ("GPT", "GLM"):
            result.append(p.upper())
        elif p in ("pro", "max", "mini", "flash", "spark", "preview", "free", "super", "large"):
            result.append(p.title())
        elif re.match(r"^\d", p):
            result.append(p)  # keep version numbers as-is
        else:
            result.append(p.title())
    return " ".join(result)

def fetch(output_path: str):
    print("→ OpenCode Zen — pobieranie listy modeli z API...")

    req = urllib.request.Request(API_URL, headers={"User-Agent": "ai-api-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        api_data = json.loads(resp.read())

    api_models = api_data.get("data", [])
    print(f"  API zwróciło {len(api_models)} modeli")

    models = []
    missing_pricing = []

    for item in api_models:
        mid = item["id"]
        pricing = PRICING.get(mid)

        if pricing is None:
            # Auto-detect free by name convention
            if "free" in mid.lower():
                pricing = {"input_per_1m": 0.0, "output_per_1m": 0.0, "notes": "Free"}
            else:
                missing_pricing.append(mid)
                pricing = {"notes": "pricing unknown — update PRICING dict"}

        # Normalize ID for our catalog: replace dots with dashes
        catalog_id = mid.replace(".", "-")

        models.append({
            "id":           catalog_id,
            "name":         _make_name(mid),
            "category":     "llm",
            "description":  f"{_make_name(mid)} via OpenCode Zen curated gateway.",
            "tags":         _guess_tags(mid),
            "capabilities": _guess_capabilities(mid),
            "pricing":      pricing,
            "context_k":    200 if any(x in mid for x in ["claude", "gemini"]) else None,
            "url":          "https://opencode.ai/docs/zen/",
            "_api_id":      mid,  # original API ID (dots preserved)
        })

    if missing_pricing:
        print(f"  ⚠ Brak pricing dla {len(missing_pricing)} modeli: {missing_pricing}")
        print(f"    → Zaktualizuj PRICING dict w fetch-opencode.py")

    free_count = sum(1 for m in models if m["pricing"].get("input_per_1m") == 0.0)
    print(f"  {len(models)} modeli ({free_count} free)")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "models": models,
            "source": "opencode",
            "base_url": "https://opencode.ai/zen/v1/",
            "note": "Models from API, pricing curated from https://opencode.ai/docs/zen/#pricing",
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return models


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
