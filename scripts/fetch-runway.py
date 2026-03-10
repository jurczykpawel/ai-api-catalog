#!/usr/bin/env python3
"""
fetch-runway.py
Pobiera modele z Runway ML API.
Wymaga zmiennej RUNWAY_API_KEY lub jest curated jeśli brak klucza.

Użycie:
  RUNWAY_API_KEY=key_xxx python3 scripts/fetch-runway.py [ścieżka-wyjściowa]
  python3 scripts/fetch-runway.py  # bez klucza — curated dane
"""

import json, sys, os, urllib.request, urllib.error
from pathlib import Path

OUTPUT_DEFAULT = "data/runway-raw.json"
RUNWAY_API = "https://api.runwayml.com"

# Curated — Runway ML nie ma publicznego /models endpointu
# Ceny: https://runwayml.com/pricing (marzec 2026)
# Gen-4 Turbo: $0.05/sekunda wideo
RUNWAY_MODELS = [
    {
        "id": "runway-gen-4-turbo",
        "name": "Runway Gen-4 Turbo",
        "category": "video_generation",
        "description": "Runway Gen-4 Turbo — cinematic AI video generation. Text-to-video and image-to-video with reference consistency.",
        "tags": ["video", "runway", "cinematic"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_second": 0.05, "unit": "per_second"},
        "notes": "5-second video = $0.25. 10-second = $0.50.",
        "url": "https://runwayml.com",
        "affiliate_url": None,
    },
    {
        "id": "runway-gen-3-alpha",
        "name": "Runway Gen-3 Alpha",
        "category": "video_generation",
        "description": "Runway Gen-3 Alpha — high fidelity video generation from text or image.",
        "tags": ["video", "runway"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_second": 0.05, "unit": "per_second"},
        "notes": "Legacy model, Gen-4 Turbo recommended.",
        "url": "https://runwayml.com",
        "affiliate_url": None,
    },
    {
        "id": "runway-act-one",
        "name": "Runway Act-One",
        "category": "video_generation",
        "description": "Runway Act-One — character animation from single image using reference video performance.",
        "tags": ["video", "runway", "animation", "avatar"],
        "capabilities": ["image_to_video"],
        "pricing": {"per_second": 0.05, "unit": "per_second"},
        "url": "https://runwayml.com",
        "affiliate_url": None,
    },
]


def try_api_fetch(api_key: str) -> list | None:
    """Próba pobrania modeli z API jeśli jest klucz."""
    try:
        url = f"{RUNWAY_API}/v1/models"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {api_key}",
            "X-Runway-Version": "2024-11-06",
            "User-Agent": "ai-api-catalog/1.0",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("data", data) if isinstance(data, dict) else data
    except urllib.error.HTTPError as e:
        print(f"  API error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  API error: {e}", file=sys.stderr)
        return None


def fetch(output_path: str):
    api_key = os.environ.get("RUNWAY_API_KEY")
    models = None

    if api_key:
        print("→ Runway ML — próba API...")
        models = try_api_fetch(api_key)
        if models:
            print(f"  Pobrano z API: {len(models)} modeli")

    if not models:
        print("→ Runway ML — brak klucza lub błąd API, ładowanie curated...")
        models = RUNWAY_MODELS

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": models, "source": "runway",
                   "note": "Curated — Runway API /v1/models endpoint may exist with key"}, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(models)} modeli Runway zapisano: {out_path}")
    return models


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
