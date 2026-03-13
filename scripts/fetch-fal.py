#!/usr/bin/env python3
"""
fetch-fal.py
Pobiera modele z fal.ai API i zapisuje jako data/fal-raw.json.
Nie wymaga klucza API.

Użycie:
  python3 scripts/fetch-fal.py [ścieżka-wyjściowa]
"""

import json, subprocess, sys, time, urllib.parse
from pathlib import Path

FAL_API   = "https://api.fal.ai/v1/models"
OUTPUT_DEFAULT = "data/fal-raw.json"

CURL_HEADERS = [
    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept: application/json",
    "Accept-Language: en-US,en;q=0.9",
]

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


def curl_get(url: str) -> dict:
    cmd = ["curl", "-s", "--compressed", "--fail", "--max-time", "30"]
    for h in CURL_HEADERS:
        cmd += ["-H", h]
    cmd.append(url)
    for attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if result.returncode == 0:
            return json.loads(result.stdout)
        if attempt < 2:
            print(f"  ↻ fal.ai 429 na stronie, retry za 30s... (attempt {attempt+1}/3)")
            time.sleep(30)
    raise RuntimeError(f"curl failed after 3 attempts (exit {result.returncode})")


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
        data = curl_get(url)

        models = data.get("models", [])
        all_models.extend(models)
        page += 1

        if not data.get("has_more") or not models:
            break
        cursor = data.get("next_cursor")
        time.sleep(1)

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
