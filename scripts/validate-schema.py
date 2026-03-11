#!/usr/bin/env python3
"""
validate-schema.py
Waliduje models.json pod kątem wymaganych pól i spójności danych.

Użycie:
  python3 scripts/validate-schema.py data/models.json
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["id", "name", "category", "description", "providers"]
VALID_CATEGORIES = {
    "llm", "image_generation", "video_generation",
    "audio_tts", "audio_stt", "music_generation",
    "embedding", "moderation"
}
VALID_CAPABILITIES = {
    "vision", "reasoning", "function_calling", "web_search",
    "prompt_caching", "audio_input", "streaming", "multilingual",
    "voice_cloning", "text_in_image", "image_editing",
    "image_to_video", "text_to_video", "camera_control",
    "audio_generation", "translation", "json_mode"
}
REQUIRED_PROVIDER_FIELDS = ["provider_id", "pricing", "available"]

errors = []
warnings = []


def validate(path: str):
    data_path = Path(path)
    if not data_path.exists():
        print(f"✗ Plik nie istnieje: {data_path}")
        sys.exit(1)

    with open(data_path) as f:
        data = json.load(f)

    models = data.get("models", [])
    if not models:
        errors.append("Brak modeli w pliku")
        return

    count = len(models)
    print(f"Walidacja {count} modeli z {data_path}...\n")

    # Count regression check — fail if model count dropped by >10% vs git HEAD
    try:
        import subprocess
        result = subprocess.run(
            ["git", "show", "HEAD:data/models.json"],
            capture_output=True, text=True, cwd=data_path.parent.parent
        )
        if result.returncode == 0:
            prev = json.loads(result.stdout)
            prev_count = len(prev.get("models", []))
            if prev_count > 0:
                drop_pct = (prev_count - count) / prev_count * 100
                if drop_pct > 10:
                    errors.append(
                        f"REGRESJA: {count} modeli vs {prev_count} w HEAD "
                        f"(spadek o {drop_pct:.0f}%). "
                        f"Sprawdź czy wszystkie źródła danych zostały użyte."
                    )
    except Exception:
        pass  # git unavailable — skip check

    ids = []
    for i, model in enumerate(models):
        ctx = f"Model #{i+1} ({model.get('id', '?')})"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in model:
                errors.append(f"{ctx}: brak pola '{field}'")

        # Category
        cat = model.get("category")
        if cat and cat not in VALID_CATEGORIES:
            errors.append(f"{ctx}: nieznana kategoria '{cat}'")

        # Duplicate IDs
        mid = model.get("id")
        if mid in ids:
            errors.append(f"{ctx}: duplikat id '{mid}'")
        if mid:
            ids.append(mid)

        # Capabilities
        for cap in model.get("capabilities", []):
            if cap not in VALID_CAPABILITIES:
                warnings.append(f"{ctx}: nieznana capability '{cap}' (może być OK)")

        # Providers
        providers = model.get("providers", [])
        if not providers:
            warnings.append(f"{ctx}: brak dostawców")

        for j, prov in enumerate(providers):
            pctx = f"{ctx} provider #{j+1}"
            for field in REQUIRED_PROVIDER_FIELDS:
                if field not in prov:
                    errors.append(f"{pctx}: brak pola '{field}'")

            # Pricing sanity
            pricing = prov.get("pricing", {})
            if not pricing:
                warnings.append(f"{pctx}: puste pricing")
            else:
                for key in ["input_per_1m", "output_per_1m", "per_image", "per_second", "per_minute"]:
                    val = pricing.get(key)
                    if val is not None and val < 0:
                        errors.append(f"{pctx}: ujemna cena '{key}' = {val}")

    # Report
    print(f"  Błędy:    {len(errors)}")
    print(f"  Ostrzeżenia: {len(warnings)}")

    if warnings:
        print("\n⚠ Ostrzeżenia:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n✗ Błędy:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✓ Walidacja przeszła pomyślnie!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python3 validate-schema.py <ścieżka-do-models.json>")
        sys.exit(1)
    validate(sys.argv[1])
