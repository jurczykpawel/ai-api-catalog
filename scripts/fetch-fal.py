#!/usr/bin/env python3
"""
fetch-fal.py
Pobiera modele z fal.ai API i zapisuje jako data/fal-raw.json.
Nie wymaga klucza API.

Użycie:
  python3 scripts/fetch-fal.py [ścieżka-wyjściowa]
"""

import json, sys, urllib.request, urllib.parse
from pathlib import Path

FAL_API   = "https://api.fal.ai/v1/models"
OUTPUT_DEFAULT = "data/fal-raw.json"

# Kategorie fal.ai → nasze kategorie
CATEGORY_MAP = {
    "text-to-image":    "image_generation",
    "image-to-image":   "image_generation",
    "image-editing":    "image_generation",
    "text-to-video":    "video_generation",
    "image-to-video":   "video_generation",
    "video-to-video":   "video_generation",
    "text-to-speech":   "audio_tts",
    "speech-to-text":   "audio_stt",
    "text-to-music":    "music_generation",
    "text-to-audio":    "music_generation",
    "audio-to-audio":   "music_generation",
}

# Kategorie do pominięcia
SKIP_CATEGORIES = {
    "text-generation", "chat", "embedding", "code-generation",
    "3d", "background-removal", "image-restoration", "image-upscaling",
    "face-restoration", "segmentation", "depth-estimation",
    "object-detection", "pose-estimation", "style-transfer",
    "controlnet", "lora-training", "model-training",
}


def fetch(output_path: str):
    all_models = []
    cursor = None
    page = 0

    print("→ Pobieranie modeli z fal.ai API...")

    while True:
        params = {"page_size": 100}
        if cursor:
            params["cursor"] = cursor

        url = FAL_API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        models = data.get("models", [])
        all_models.extend(models)
        page += 1

        if not data.get("has_more") or not models:
            break
        cursor = data.get("next_cursor")

    # Filtrujemy do kategorii które nas interesują
    filtered = []
    for m in all_models:
        meta = m.get("metadata", {})
        cat_raw = meta.get("category", "")
        if cat_raw in SKIP_CATEGORIES:
            continue
        if meta.get("status") not in ("active", None, ""):
            continue
        our_cat = CATEGORY_MAP.get(cat_raw)
        if our_cat is None:
            continue
        m["_our_category"] = our_cat
        filtered.append(m)

    print(f"✓ Pobrano {len(all_models)} modeli, po filtrze: {len(filtered)}")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": filtered, "total_fetched": len(all_models)}, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return filtered


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
