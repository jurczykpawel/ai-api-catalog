#!/usr/bin/env python3
"""
fetch-aimlapi.py
Pobiera modele z AIMLAPI publicznego endpointu (bez tokenu).
Zapisuje jako data/aimlapi-raw.json.

Użycie:
  python3 scripts/fetch-aimlapi.py [ścieżka-wyjściowa]
"""

import json, sys, urllib.request
from pathlib import Path

AIMLAPI_URL  = "https://api.aimlapi.com/v1/models"
OUTPUT_DEFAULT = "data/aimlapi-raw.json"

# type → nasza kategoria
TYPE_TO_CATEGORY = {
    "chat-completion":       "llm",
    "language-model":        "llm",
    "text-generation":       "llm",
    "image-generation":      "image_generation",
    "text-to-image":         "image_generation",
    "video-generation":      "video_generation",
    "text-to-video":         "video_generation",
    "text-to-speech":        "audio_tts",
    "speech-to-text":        "audio_stt",
    "automatic-speech-recognition": "audio_stt",
    "music-generation":      "music_generation",
    "text-to-music":         "music_generation",
    "embedding":             "embedding",
    "embeddings":            "embedding",
}

# Features → capabilities
FEATURE_CAPS = {
    "openai/chat-completion.vision": "vision",
    "openai/chat-completion.function": "function_calling",
    "reasoning": "reasoning",
    "web-search": "web_search",
}

# Pomijamy stare/space wersje i duplikaty
SKIP_PATTERNS = [
    "2024-", "2023-", "-preview", "-exp", "-beta",
    "gpt-3.5", "gpt-4-turbo-preview", "gpt-4-0314",
    "claude-3-opus", "claude-2", "claude-instant",
]

# Modele LLM które zachowujemy (reszta jest w OR/LiteLLM)
KEEP_LLM_TYPES = {"image-generation", "video-generation", "text-to-speech",
                  "speech-to-text", "music-generation", "text-to-image",
                  "text-to-video", "text-to-music", "embedding", "embeddings",
                  "automatic-speech-recognition"}


def fetch(output_path: str):
    print("→ Pobieranie modeli z AIMLAPI...")
    req = urllib.request.Request(AIMLAPI_URL, headers={"User-Agent": "ai-api-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    raw = data.get("data", data) if isinstance(data, dict) else data
    print(f"  Pobrano: {len(raw)} modeli")

    filtered = []
    for m in raw:
        mid  = m.get("id", "")
        mtype = m.get("type", "")

        # Pomijamy LLM które mamy z OR/LiteLLM
        if mtype not in KEEP_LLM_TYPES:
            # Zachowaj nowe/unikalne LLM których nie mamy gdzie indziej
            if any(skip in mid.lower() for skip in SKIP_PATTERNS):
                continue

        cat = TYPE_TO_CATEGORY.get(mtype)
        if not cat:
            continue

        # Capabilities
        caps = set()
        for feat in m.get("features", []):
            cap = FEATURE_CAPS.get(feat)
            if cap:
                caps.add(cap)

        info = m.get("info", {})
        filtered.append({
            "id":          mid,
            "type":        mtype,
            "name":        info.get("name", mid),
            "developer":   info.get("developer", ""),
            "description": info.get("description", ""),
            "context_length": info.get("contextLength"),
            "url":         info.get("url", ""),
            "_our_category": cat,
            "_caps":       list(caps),
        })

    print(f"  Po filtracji: {len(filtered)} modeli")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"models": filtered}, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {out_path}")
    return filtered


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT
    fetch(output)
