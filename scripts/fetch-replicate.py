#!/usr/bin/env python3
"""
fetch-replicate.py
Pobiera modele z Replicate API i zapisuje jako data/replicate-raw.json.
WYMAGA zmiennej środowiskowej REPLICATE_API_TOKEN.

Użycie:
  REPLICATE_API_TOKEN=r8_xxx python3 scripts/fetch-replicate.py [ścieżka-wyjściowa]
"""

import json, sys, os, urllib.request, urllib.parse
from pathlib import Path

REPLICATE_API = "https://api.replicate.com/v1/models"
OUTPUT_DEFAULT = "data/replicate-raw.json"

CATEGORY_HINTS = {
    "text-to-image":  "image_generation",
    "image-to-image": "image_generation",
    "image-editing":  "image_generation",
    "text-to-video":  "video_generation",
    "image-to-video": "video_generation",
    "video-generation": "video_generation",
    "text-to-speech": "audio_tts",
    "speech-to-text": "audio_stt",
    "audio":          "music_generation",
    "text-generation": "llm",
    "language-model": "llm",
    "embedding":      "embedding",
}


def fetch(output_path: str):
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("✗ Brak REPLICATE_API_TOKEN. Ustaw zmienną środowiskową.", file=sys.stderr)
        sys.exit(1)

    all_models = []
    url = REPLICATE_API + "?limit=100"

    print("→ Pobieranie modeli z Replicate API...")

    while url:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Token {token}",
            "User-Agent": "ai-api-catalog/1.0",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        results = data.get("results", [])
        all_models.extend(results)
        url = data.get("next")  # Replicate uses full URL for next page

        if len(all_models) >= 2000:  # safety cap
            break

    print(f"✓ Pobrano {len(all_models)} modeli z Replicate")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": all_models}, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return all_models


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
