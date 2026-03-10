#!/usr/bin/env python3
"""
fetch-fireworks.py
Pobiera listę modeli z Fireworks AI API i zapisuje jako fireworks-raw.json.

Użycie:
  python3 scripts/fetch-fireworks.py data/fireworks-raw.json
  FIREWORKS_API_KEY=fw_xxx python3 scripts/fetch-fireworks.py data/fireworks-raw.json

API nie zwraca cen — pricing pochodzi z LiteLLM (merge-data.py łączy po model ID).
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

API_BASE = "https://api.fireworks.ai/v1/accounts/fireworks/models"
OUTPUT_DEFAULT = "data/fireworks-raw.json"


def fetch(output_path: str, api_key: str):
    print("→ Pobieranie listy modeli z Fireworks AI API...")

    all_models = []
    page_token = ""

    while True:
        url = API_BASE + ("?pageToken=" + page_token if page_token else "")
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.load(response)

        models = data.get("models", [])
        all_models.extend(models)
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break

    # Filtruj tylko publiczne i aktywne
    public_models = [m for m in all_models if m.get("public") and m.get("state") == "READY"]
    print(f"✓ Pobrano {len(public_models)} publicznych modeli (z {len(all_models)} łącznie)")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": public_models}, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return public_models


if __name__ == "__main__":
    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        print("✗ Brak FIREWORKS_API_KEY w środowisku", file=sys.stderr)
        print("  Użycie: FIREWORKS_API_KEY=fw_xxx python3 scripts/fetch-fireworks.py", file=sys.stderr)
        sys.exit(1)

    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output, api_key)
