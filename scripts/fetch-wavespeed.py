#!/usr/bin/env python3
"""
fetch-wavespeed.py
Pobiera modele z WaveSpeed AI (wavespeed.ai).
Scraper strony /models — ceny w USD/image lub USD/second.

Użycie:
  python3 scripts/fetch-wavespeed.py [ścieżka-wyjściowa]
"""

import json, sys, re, urllib.request
from pathlib import Path

OUTPUT_DEFAULT = "data/wavespeed-raw.json"

# WaveSpeed modele z cenami USD.
# Ceny z: https://wavespeed.ai/pricing (marzec 2026)
# 1 unit = $0.000001 (1M units = $1), ale podajemy ceny w USD.
WAVESPEED_MODELS = [
    # ── Video ─────────────────────────────────────────────────────
    {
        "id": "sora-2",
        "name": "Sora 2",
        "category": "video_generation",
        "description": "OpenAI Sora 2 cinematic video generation via WaveSpeed API.",
        "tags": ["video", "openai", "sora"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_second": 0.10, "unit": "per_second"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "seedance-1-5-pro",
        "name": "Seedance 1.5 Pro",
        "category": "video_generation",
        "description": "ByteDance Seedance 1.5 Pro — high quality video generation.",
        "tags": ["video", "seedance", "bytedance"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.26, "unit": "per_video_5s"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "wan-2-6",
        "name": "WAN 2.6",
        "category": "video_generation",
        "description": "Wan 2.6 by Wan-AI. Latest open-source video generation.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.50, "unit": "per_video_5s"},
        "notes": "500,000 units per 5s video",
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "kling-3-0",
        "name": "Kling O3",
        "category": "video_generation",
        "description": "Kling O3 (latest Kling generation) — standard and pro quality.",
        "tags": ["video", "kling"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.42, "unit": "per_video_5s"},
        "notes": "O3 Standard. Pro is $0.56/5s.",
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "wan-2-5",
        "name": "WAN 2.5",
        "category": "video_generation",
        "description": "Wan 2.5 open-source video generation.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.25, "unit": "per_video_5s"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "wan-2-2",
        "name": "WAN 2.2",
        "category": "video_generation",
        "description": "Wan 2.2 open-source video generation.",
        "tags": ["video", "wan", "open-source"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.15, "unit": "per_video_5s"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "grok-imagine-video",
        "name": "Grok Imagine Video",
        "category": "video_generation",
        "description": "xAI Grok Imagine Video — text-to-video and image-to-video by xAI.",
        "tags": ["video", "grok", "xai"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_video_5s": 0.065, "unit": "per_video_5s"},
        "url": "https://wavespeed.ai/models",
    },
    # ── Image ─────────────────────────────────────────────────────
    {
        "id": "flux-1-dev",
        "name": "FLUX.1 Dev Ultra Fast",
        "category": "image_generation",
        "description": "FLUX.1 Dev ultra-fast variant via WaveSpeed AI.",
        "tags": ["image", "flux", "bfl", "open-source"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.005, "unit": "per_image"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "grok-2-image",
        "name": "Grok 2 Image",
        "category": "image_generation",
        "description": "xAI Grok 2 image generation model.",
        "tags": ["image", "grok", "xai"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.07, "unit": "per_image"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "qwen-image-2-pro",
        "name": "Qwen Image 2.0 Pro",
        "category": "image_generation",
        "description": "Alibaba Qwen Image 2.0 Pro — high quality text-to-image.",
        "tags": ["image", "qwen", "alibaba"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.07, "unit": "per_image"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "seedream-4-5",
        "name": "Seedream v4.5",
        "category": "image_generation",
        "description": "ByteDance Seedream v4.5 image generation.",
        "tags": ["image", "seedream", "bytedance"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.04, "unit": "per_image"},
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "nano-banana-2",
        "name": "Nano Banana 2",
        "category": "image_generation",
        "description": "Google Nano Banana 2 — ultra-fast experimental image generation.",
        "tags": ["image", "google", "fast"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.022, "unit": "per_image"},
        "notes": "Grok Imagine price; Nano Banana 2 may vary",
        "url": "https://wavespeed.ai/models",
    },
    {
        "id": "dall-e-3",
        "name": "DALL-E 3",
        "category": "image_generation",
        "description": "OpenAI DALL-E 3 via WaveSpeed API.",
        "tags": ["image", "openai", "dalle"],
        "capabilities": ["text_to_image"],
        "pricing": {"per_image": 0.04, "unit": "per_image"},
        "url": "https://wavespeed.ai/models",
    },
]


def fetch(output_path: str):
    print("→ WaveSpeed — ładowanie curated modeli...")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": WAVESPEED_MODELS, "source": "wavespeed",
                   "note": "Curated — update from wavespeed.ai/pricing"}, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(WAVESPEED_MODELS)} modeli WaveSpeed zapisano: {out_path}")
    return WAVESPEED_MODELS


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
