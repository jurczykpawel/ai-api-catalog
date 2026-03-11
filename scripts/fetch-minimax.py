#!/usr/bin/env python3
"""
fetch-minimax.py
Curated MiniMax models with pricing from platform.minimax.io.
MiniMax has no machine-readable pricing API — prices are manually curated.

Użycie:
  python3 scripts/fetch-minimax.py [ścieżka-wyjściowa]

Źródło cen: https://platform.minimax.io/docs/pricing/overview
Aktualizacja: 2026-03-11
"""

import json, sys
from datetime import datetime
from pathlib import Path

OUTPUT_DEFAULT = "data/minimax-raw.json"
BASE_URL = "https://platform.minimax.io"

# Ceny w USD/1M tokenów, per second, per character.
# Źródło: https://platform.minimax.io/docs/pricing/overview
# Aktualizacja: 2026-03-11
MINIMAX_MODELS = [
    # ── LLM ───────────────────────────────────────────────────────────
    {
        "id": "minimax-m2-5",
        "name": "MiniMax M2.5",
        "category": "llm",
        "description": "MiniMax flagship LLM with 196k context. OpenAI-compatible API.",
        "tags": ["minimax", "llm", "long-context"],
        "capabilities": ["vision", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 0.30, "output_per_1m": 1.20},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    {
        "id": "minimax-m2-5-lightning",
        "name": "MiniMax M2.5 Lightning",
        "category": "llm",
        "description": "High-speed variant of MiniMax M2.5. ~100 tokens/sec.",
        "tags": ["minimax", "llm", "fast"],
        "capabilities": ["function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 0.30, "output_per_1m": 2.40},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    {
        "id": "minimax-m2-1",
        "name": "MiniMax M2.1",
        "category": "llm",
        "description": "MiniMax M2.1 LLM. Also available on AWS Bedrock and Fireworks.",
        "tags": ["minimax", "llm"],
        "capabilities": ["function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 0.30, "output_per_1m": 1.20},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    {
        "id": "minimax-m2-1-lightning",
        "name": "MiniMax M2.1 Lightning",
        "category": "llm",
        "description": "High-speed variant of MiniMax M2.1.",
        "tags": ["minimax", "llm", "fast"],
        "capabilities": ["function_calling"],
        "pricing": {"input_per_1m": 0.30, "output_per_1m": 2.40},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    {
        "id": "minimax-m2",
        "name": "MiniMax M2",
        "category": "llm",
        "description": "MiniMax M2 — 200k context, 128k max output. OpenAI-compatible.",
        "tags": ["minimax", "llm", "long-context"],
        "capabilities": ["vision", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 0.30, "output_per_1m": 1.20},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    # ── TTS ───────────────────────────────────────────────────────────
    {
        "id": "minimax-speech-2-8-hd",
        "name": "MiniMax Speech-2.8 HD",
        "category": "audio_tts",
        "description": "High-quality TTS by MiniMax. 40 languages, 7 emotion variants, voice cloning.",
        "tags": ["minimax", "tts", "multilingual", "voice-cloning"],
        "capabilities": [],
        "pricing": {"notes": "Per-character pricing — check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/pricing/overview",
    },
    {
        "id": "minimax-speech-2-8-turbo",
        "name": "MiniMax Speech-2.8 Turbo",
        "category": "audio_tts",
        "description": "Fast TTS by MiniMax. 40 languages, lower latency than HD.",
        "tags": ["minimax", "tts", "multilingual", "fast"],
        "capabilities": [],
        "pricing": {"notes": "Per-character pricing — check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/pricing/overview",
    },
    {
        "id": "minimax-speech-2-6-hd",
        "name": "MiniMax Speech-2.6 HD",
        "category": "audio_tts",
        "description": "MiniMax TTS 2.6 HD. 40 languages, high quality.",
        "tags": ["minimax", "tts", "multilingual"],
        "capabilities": [],
        "pricing": {"notes": "Per-character pricing — check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/pricing/overview",
    },
    # ── Video ──────────────────────────────────────────────────────────
    {
        "id": "hailuo-2-3",
        "name": "MiniMax Hailuo 2.3",
        "category": "video_generation",
        "description": "MiniMax latest video model. 1080p 6s or 768p up to 10s at 24fps.",
        "tags": ["minimax", "hailuo", "video"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"notes": "Check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    {
        "id": "hailuo-2-3-fast",
        "name": "MiniMax Hailuo 2.3 Fast",
        "category": "video_generation",
        "description": "Faster variant of Hailuo 2.3 with slightly lower quality.",
        "tags": ["minimax", "hailuo", "video", "fast"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"notes": "Check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
    # ── Music ──────────────────────────────────────────────────────────
    {
        "id": "minimax-music-2-5",
        "name": "MiniMax Music-2.5",
        "category": "music_generation",
        "description": "MiniMax music generation model. Multi-genre, expressive vocals.",
        "tags": ["minimax", "music"],
        "capabilities": [],
        "pricing": {"notes": "Check platform.minimax.io/docs/pricing/overview"},
        "url": "https://platform.minimax.io/docs/guides/models-intro",
    },
]


def build_output(models: list) -> dict:
    """Build output in flat format expected by parse_curated() in merge-data.py."""
    today = datetime.now().strftime("%Y-%m-%d")
    out = []
    for m in models:
        entry = {
            "id": m["id"],
            "name": m["name"],
            "category": m["category"],
            "description": m["description"],
            "tags": m.get("tags", []),
            "capabilities": m.get("capabilities", []),
            "open_source": False,
            "local_available": False,
            "pricing": m["pricing"],   # flat — read by parse_curated()
            "url": m["url"],
            "updated_at": today,
            "source": "minimax",
        }
        out.append(entry)
    return {"models": out, "updated_at": today, "source": "minimax", "count": len(out)}


def main():
    output_path = Path(sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = build_output(MINIMAX_MODELS)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✓ MiniMax: {data['count']} modeli → {output_path}")


if __name__ == "__main__":
    main()
