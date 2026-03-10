#!/usr/bin/env python3
"""
fetch-openrouter.py
Pobiera listę modeli z OpenRouter API i zapisuje jako openrouter-raw.json.

Użycie:
  python3 scripts/fetch-openrouter.py [ścieżka-wyjściowa]
  python3 scripts/fetch-openrouter.py data/openrouter-raw.json
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Frontend API zwraca 642+ modeli (vs 346 w /api/v1/models) — w tym image gen i experimental.
# Nieudokumentowany endpoint, dlatego fallback na v1 jeśli nie odpowie.
OR_FRONTEND_URL = "https://openrouter.ai/api/frontend/models"
OR_V1_URL = "https://openrouter.ai/api/v1/models"
OUTPUT_DEFAULT = "data/openrouter-raw.json"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ai-api-catalog/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


def fetch(output_path: str):
    print("→ Pobieranie listy modeli z OpenRouter API...")

    used_fallback = False
    fallback_reason = ""

    try:
        data = _get(OR_FRONTEND_URL)
        models = data.get("data", [])
        if len(models) < 400:
            raise ValueError(f"Za mało modeli ({len(models)}) — frontend API mogło się zmienić")
        print(f"✓ Pobrano {len(models)} modeli z OpenRouter (frontend API)")
    except Exception as e:
        used_fallback = True
        fallback_reason = str(e)
        print(f"⚠ Frontend API niedostępny: {e}")
        print("  → Fallback na v1 API...")
        data = _get(OR_V1_URL)
        models = data.get("data", [])
        print(f"✓ Pobrano {len(models)} modeli z OpenRouter (v1 API — FALLBACK)")

    # Zapisz status (do monitoringu / healthchecku)
    status_path = Path(output_path).parent / "or-api-status.json"
    status = {
        "endpoint": "v1" if used_fallback else "frontend",
        "model_count": len(models),
        "fallback": used_fallback,
        "fallback_reason": fallback_reason if used_fallback else None,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(status_path, "w") as f:
        json.dump(status, f, indent=2)

    if used_fallback:
        # Powiadomienie przez webhook (opcjonalne — ustaw OR_NOTIFY_WEBHOOK w env)
        webhook = os.environ.get("OR_NOTIFY_WEBHOOK")
        if webhook:
            try:
                payload = json.dumps({
                    "text": f"⚠️ AI Catalog: OpenRouter frontend API niedostępny\nPrzyczyna: {fallback_reason}\nUżyto fallback na v1 ({len(models)} modeli)"
                }).encode()
                req = urllib.request.Request(webhook, data=payload,
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10)
                print("✓ Powiadomienie wysłane")
            except Exception as we:
                print(f"⚠ Powiadomienie nieudane: {we}")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return models


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
