#!/usr/bin/env python3
"""
fetch-huggingface.py
Pobiera top modele open-source z HuggingFace Hub API.
Nie wymaga tokena (opcjonalnie HF_TOKEN dla wyższych limitów).

Filtruje do modeli z Inference API lub godnych local-run.
Zapisuje jako data/huggingface-raw.json.

Użycie:
  python3 scripts/fetch-huggingface.py [ścieżka-wyjściowa]
"""

import json, sys, os, urllib.request, urllib.parse
from pathlib import Path

HF_API = "https://huggingface.co/api/models"
OUTPUT_DEFAULT = "data/huggingface-raw.json"

# pipeline_tag → nasza kategoria
PIPELINE_MAP = {
    "text-to-image":               "image_generation",
    "text-to-video":               "video_generation",
    "image-to-video":              "video_generation",
    "text-to-speech":              "audio_tts",
    "automatic-speech-recognition":"audio_stt",
    "text-generation":             "llm",
    "text2text-generation":        "llm",
    "feature-extraction":          "embedding",
    "audio-generation":            "music_generation",
}

# Ile top modeli brać z każdej kategorii
LIMITS = {
    "text-to-image":                30,
    "text-to-video":                15,
    "image-to-video":               10,
    "text-to-speech":               10,
    "automatic-speech-recognition": 10,
    "text-generation":              25,
    "feature-extraction":           10,
    "audio-generation":             5,
}

# Minimalny próg downloads
MIN_DOWNLOADS = 5_000

# Pomijamy modele-finetune/quantize (te nie mają własnej wartości w katalogu)
SKIP_TAGS = {"gguf", "ggml", "awq", "gptq", "mlx"}

# library_name które nas interesują (pomijamy np. peft, bnb)
GOOD_LIBRARIES = {"diffusers", "transformers", "sentence-transformers", "huggingface_hub", None}


def hf_fetch(pipeline_tag: str, limit: int, token: str | None) -> list:
    params = {
        "pipeline_tag": pipeline_tag,
        "sort": "downloads",
        "direction": "-1",
        "limit": min(limit * 3, 100),  # fetch more, filter later
    }
    url = HF_API + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "ai-api-catalog/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        models = json.loads(resp.read())

    # Filter
    filtered = []
    for m in models:
        if m.get("private") or m.get("gated"):
            continue
        if m.get("downloads", 0) < MIN_DOWNLOADS:
            continue

        tags = set(m.get("tags", []))
        if tags & SKIP_TAGS:
            continue

        lib = m.get("library_name")
        if lib not in GOOD_LIBRARIES:
            continue

        filtered.append(m)
        if len(filtered) >= limit:
            break

    return filtered


def fetch(output_path: str):
    token = os.environ.get("HF_TOKEN")

    print("→ Pobieranie modeli z HuggingFace Hub API...")
    all_results = []

    for pipeline_tag, limit in LIMITS.items():
        try:
            models = hf_fetch(pipeline_tag, limit, token)
            for m in models:
                m["_our_category"] = PIPELINE_MAP[pipeline_tag]
            all_results.extend(models)
            print(f"  {pipeline_tag}: {len(models)} modeli")
        except Exception as e:
            print(f"  ✗ {pipeline_tag}: {e}", file=sys.stderr)

    print(f"✓ Razem: {len(all_results)} modeli z HuggingFace")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": all_results}, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return all_results


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
