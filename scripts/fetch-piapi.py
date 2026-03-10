#!/usr/bin/env python3
"""
fetch-piapi.py
Pobiera modele z piapi.ai (scraped + curated pricing).
piapi.ai nie ma publicznego API katalogu — ceny są pobierane ze stron produktowych.

Użycie:
  python3 scripts/fetch-piapi.py [ścieżka-wyjściowa]
"""

import json, sys, re, urllib.request, urllib.error, time
from pathlib import Path

OUTPUT_DEFAULT = "data/piapi-raw.json"
BASE_URL = "https://piapi.ai"

# Curated model list z cenami (aktualizuj po zmianach na piapi.ai/pricing)
# Ceny PAYG w USD. Kling: cena za 5-sekundowe video.
# Aktualizacja: 2026-03-08
PIAPI_MODELS = [
    # ── Video ─────────────────────────────────────────────────────
    {
        "id": "kling-3-0",
        "name": "Kling 3.0",
        "category": "video_generation",
        "description": "Kling 3.0 video generation model by Kuaishou. High quality text-to-video and image-to-video.",
        "tags": ["video", "kling"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.46, "unit": "per_video_5s"},
        "notes": "5-second video. Pro tier.",
        "url": "https://piapi.ai/kling-api",
    },
    {
        "id": "kling-2-1",
        "name": "Kling 2.1",
        "category": "video_generation",
        "description": "Kling 2.1 by Kuaishou. Standard and Pro quality tiers.",
        "tags": ["video", "kling"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.26, "unit": "per_video_5s"},
        "notes": "5-second video. Standard tier $0.26, Pro $0.46.",
        "url": "https://piapi.ai/kling-api",
    },
    {
        "id": "seedance-2-0",
        "name": "Seedance 2.0",
        "category": "video_generation",
        "description": "ByteDance Seedance 2.0 — state-of-the-art text-to-video and image-to-video model.",
        "tags": ["video", "seedance", "bytedance"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.40, "unit": "per_video_5s"},
        "notes": "5-second video. Check piapi.ai for latest pricing.",
        "url": "https://piapi.ai/seedance-2-0",
    },
    {
        "id": "wan-2-5",
        "name": "WAN 2.5",
        "category": "video_generation",
        "description": "Wan 2.5 by Wan-AI. Powerful open-source text-to-video model.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.20, "unit": "per_video_5s"},
        "notes": "5-second video.",
        "url": "https://piapi.ai/wan-api",
    },
    {
        "id": "wan-2-2",
        "name": "WAN 2.2",
        "category": "video_generation",
        "description": "Wan 2.2 by Wan-AI. High quality video generation.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.20, "unit": "per_video_5s"},
        "notes": "5-second video.",
        "url": "https://piapi.ai/wan-api",
    },
    {
        "id": "hailuo-2-3",
        "name": "Hailuo 2.3",
        "category": "video_generation",
        "description": "MiniMax Hailuo video generation model.",
        "tags": ["video", "hailuo", "minimax"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_6s": 0.28, "unit": "per_video_6s"},
        "notes": "6-second video.",
        "url": "https://piapi.ai/",
    },
    {
        "id": "luma-ray-2",
        "name": "Luma Ray 2",
        "category": "video_generation",
        "description": "Luma Dream Machine Ray 2 — cinematic quality video generation.",
        "tags": ["video", "luma"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.30, "unit": "per_video_5s"},
        "notes": "5-second video.",
        "url": "https://piapi.ai/",
    },
    {
        "id": "sora-2",
        "name": "Sora 2",
        "category": "video_generation",
        "description": "OpenAI Sora 2 — cinematic long-form video generation.",
        "tags": ["video", "openai", "sora"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.50, "unit": "per_video_5s"},
        "notes": "5-second video.",
        "url": "https://piapi.ai/",
    },
    # ── Image ─────────────────────────────────────────────────────
    {
        "id": "flux-1-pro",
        "name": "FLUX.1 Pro",
        "category": "image_generation",
        "description": "Black Forest Labs FLUX.1 Pro — top-tier image generation.",
        "tags": ["image", "flux", "bfl"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.05, "unit": "per_image"},
        "url": "https://piapi.ai/image-api",
    },
    {
        "id": "flux-1-dev",
        "name": "FLUX.1 Dev",
        "category": "image_generation",
        "description": "Black Forest Labs FLUX.1 Dev — open-source, high quality.",
        "tags": ["image", "flux", "bfl", "open-source"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.025, "unit": "per_image"},
        "url": "https://piapi.ai/image-api",
    },
    # ── Audio ─────────────────────────────────────────────────────
    {
        "id": "udio-v1",
        "name": "Udio v1",
        "category": "music_generation",
        "description": "Udio music generation — high quality AI music from text prompts.",
        "tags": ["music", "udio"],
        "capabilities": [],
        "pricing": {"notes": "Credit-based, check piapi.ai"},
        "url": "https://piapi.ai/",
    },
]


def fetch(output_path: str):
    print("→ piapi.ai — ładowanie curated modeli...")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": PIAPI_MODELS, "source": "piapi", "note": "Curated — update manually from piapi.ai/pricing"}, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(PIAPI_MODELS)} modeli piapi.ai zapisano: {out_path}")
    return PIAPI_MODELS


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
