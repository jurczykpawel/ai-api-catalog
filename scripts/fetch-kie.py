#!/usr/bin/env python3
"""
fetch-kie.py
Pobiera modele z kie.ai.
kie.ai nie ma publicznego API — dane są curated z marketplace.
1 credit = $0.005 USD.

Użycie:
  python3 scripts/fetch-kie.py [ścieżka-wyjściowa]
"""

import json, sys
from pathlib import Path

OUTPUT_DEFAULT = "data/kie-raw.json"

# 1 credit = $0.005 USD
CREDIT_PRICE = 0.005

# Curated z kie.ai/market (marzec 2026)
KIE_MODELS = [
    # ── Image ─────────────────────────────────────────────────────
    {
        "id": "nano-banana-2",
        "name": "Nano Banana 2",
        "category": "image_generation",
        "description": "Google Nano Banana 2 — ultra-fast experimental image generation model. Unique creative style with rapid generation.",
        "tags": ["image", "google", "fast", "experimental"],
        "capabilities": ["text_to_image"],
        "credits": 8,  # 8 credits = $0.04 per image
        "pricing": {"per_image": 0.04, "unit": "per_image"},
        "url": "https://kie.ai/nano-banana-2",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    {
        "id": "nano-banana",
        "name": "Nano Banana",
        "category": "image_generation",
        "description": "Google Nano Banana — original fast experimental image generation.",
        "tags": ["image", "google", "fast", "experimental"],
        "capabilities": ["text_to_image"],
        "credits": 6,
        "pricing": {"per_image": 0.03, "unit": "per_image"},
        "url": "https://kie.ai/nano-banana",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    {
        "id": "flux-1-pro",
        "name": "FLUX.1 Pro",
        "category": "image_generation",
        "description": "Black Forest Labs FLUX.1 Pro via kie.ai.",
        "tags": ["image", "flux", "bfl"],
        "capabilities": ["text_to_image"],
        "credits": 10,
        "pricing": {"per_image": 0.05, "unit": "per_image"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    {
        "id": "ideogram-v2",
        "name": "Ideogram v2",
        "category": "image_generation",
        "description": "Ideogram v2 — known for excellent text rendering in images.",
        "tags": ["image", "ideogram", "text-rendering"],
        "capabilities": ["text_to_image"],
        "credits": 8,
        "pricing": {"per_image": 0.04, "unit": "per_image"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    {
        "id": "recraft-v3",
        "name": "Recraft v3",
        "category": "image_generation",
        "description": "Recraft v3 — professional design-oriented image generation with style control.",
        "tags": ["image", "recraft", "design"],
        "capabilities": ["text_to_image"],
        "credits": 8,
        "pricing": {"per_image": 0.04, "unit": "per_image"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    # ── Video ─────────────────────────────────────────────────────
    {
        "id": "kling-2-1",
        "name": "Kling 2.1",
        "category": "video_generation",
        "description": "Kling 2.1 video generation via kie.ai API.",
        "tags": ["video", "kling"],
        "capabilities": ["text_to_video", "image_to_video"],
        "credits": 52,  # standard 5s
        "pricing": {"per_video_5s": 0.26, "unit": "per_video_5s"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    {
        "id": "wan-2-2",
        "name": "WAN 2.2",
        "category": "video_generation",
        "description": "Wan 2.2 open-source video generation via kie.ai.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "credits": 30,
        "pricing": {"per_video_5s": 0.15, "unit": "per_video_5s"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
    # ── Music ─────────────────────────────────────────────────────
    {
        "id": "suno-v4-5",
        "name": "Suno v4.5",
        "category": "music_generation",
        "description": "Suno v4.5 — latest music generation model from Suno AI.",
        "tags": ["music", "suno"],
        "capabilities": [],
        "credits": 5,
        "pricing": {"per_song": 0.025, "unit": "per_song"},
        "url": "https://kie.ai/market",
        "affiliate_url": "https://kie.ai/?ref=tsa",
    },
]


def fetch(output_path: str):
    print("→ kie.ai — ładowanie curated modeli...")

    # Normalize pricing using credit price
    for m in KIE_MODELS:
        if "credits" in m and "pricing" not in m:
            cost = round(m["credits"] * CREDIT_PRICE, 4)
            m["pricing"] = {"notes": f"{m['credits']} credits = ${cost}"}

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": KIE_MODELS, "source": "kie",
                   "credit_price_usd": CREDIT_PRICE,
                   "note": "Curated — update from kie.ai/market"}, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(KIE_MODELS)} modeli kie.ai zapisano: {out_path}")
    return KIE_MODELS


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
