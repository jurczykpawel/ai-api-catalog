#!/usr/bin/env python3
"""
merge-data.py
Scala dane z LiteLLM z ręcznymi wpisami w models-manual.json.
Generuje finalny data/models.json.

Użycie:
  python3 scripts/merge-data.py \\
      --litellm data/litellm-raw.json \\
      --manual data/models-manual.json \\
      --output data/models.json
"""

import json
import argparse
import sys
from datetime import date
from pathlib import Path

# ── Mapowanie: litellm_provider → nasz provider_id ──────────────
PROVIDER_MAP = {
    "openai":         "openai",
    "anthropic":      "anthropic",
    "gemini":         "google",
    "vertex_ai":      "google",
    "mistral_chat":   "mistral",
    "mistral":        "mistral",
    "groq":           "groq",
    "deepseek":       "deepseek",
    "cohere_chat":    "cohere",
    "cohere":         "cohere",
    "xai":            "xai",
    "perplexity":     "perplexity",
    "together_ai":    "together",
    "fireworks_ai":   "fireworks",
    "bedrock":        None,    # pomijamy — zbyt dużo modeli
    "azure":          None,    # pomijamy — zbyt dużo modeli
    "vertex_ai_beta": None,
}

# ── Modele, które chcemy zachować z LiteLLM ─────────────────────
KEEP_MODELS = {
    # OpenAI
    "gpt-4o", "gpt-4o-mini", "o1", "o1-mini", "o3", "o3-mini", "o4-mini", "o3-pro",
    "chatgpt-4o-latest",
    # Anthropic
    "claude-opus-4-6", "claude-opus-4-5", "claude-sonnet-4-5",
    "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
    "claude-3-haiku-20240307",
    # Google
    "gemini/gemini-2.5-pro", "gemini/gemini-2.0-flash",
    "gemini/gemini-2.0-flash-lite", "gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash",
    # Mistral
    "mistral/mistral-large-latest", "mistral/mistral-large-3",
    "mistral/mistral-small-latest", "mistral/codestral-2508",
    "mistral/mistral-medium-latest",
    # Groq
    "groq/llama-3.3-70b-versatile", "groq/llama-3.1-70b-versatile",
    # DeepSeek
    "deepseek-chat", "deepseek-reasoner", "deepseek/deepseek-chat",
    # Cohere
    "command-r-plus", "command-r-plus-08-2024", "command-r",
    # xAI
    "xai/grok-4", "xai/grok-4-1-fast", "xai/grok-3", "xai/grok-3-mini",
    # Perplexity
    "perplexity/sonar-pro", "perplexity/sonar", "perplexity/sonar-reasoning-pro",
}

# ── Mapowanie mode → category ────────────────────────────────────
MODE_TO_CATEGORY = {
    "chat":               "llm",
    "completion":         "llm",
    "embedding":          "embedding",
    "image_generation":   "image_generation",
    "audio_transcription":"audio_stt",
    "audio_speech":       "audio_tts",
    "moderation":         "moderation",
    "rerank":             "embedding",
}


def slugify(name: str) -> str:
    return name.lower().replace("/", "-").replace(":", "-").replace(".", "-").replace(" ", "-")


def parse_litellm(litellm_data: dict) -> list:
    """Konwertuje LiteLLM JSON do naszego formatu."""
    models = []

    for model_key, data in litellm_data.items():
        # Pomijamy spec entry
        if model_key == "sample_spec":
            continue

        provider_raw = data.get("litellm_provider", "")
        provider_id = PROVIDER_MAP.get(provider_raw)

        # Pomijamy nieznanych lub wykluczonych dostawców
        if provider_id is None:
            continue

        # Tylko wybrane modele (jeśli lista jest pusta, bierz wszystkie)
        if KEEP_MODELS and model_key not in KEEP_MODELS:
            continue

        mode = data.get("mode", "chat")
        category = MODE_TO_CATEGORY.get(mode, "llm")

        # Pricing
        pricing = {}
        if data.get("input_cost_per_token"):
            pricing["input_per_1m"] = round(data["input_cost_per_token"] * 1_000_000, 4)
        if data.get("output_cost_per_token"):
            pricing["output_per_1m"] = round(data["output_cost_per_token"] * 1_000_000, 4)
        if data.get("output_cost_per_image"):
            pricing["per_image"] = round(data["output_cost_per_image"], 4)
        if data.get("input_cost_per_audio_token"):
            # per minute estimate (100 tokens ≈ 1 second audio)
            pricing["per_minute"] = round(data["input_cost_per_audio_token"] * 1500, 4)

        # Context
        context_k = None
        max_tokens = data.get("max_input_tokens") or data.get("max_tokens")
        if max_tokens:
            context_k = round(max_tokens / 1000)

        # Capabilities
        caps = []
        if data.get("supports_vision"):        caps.append("vision")
        if data.get("supports_reasoning"):     caps.append("reasoning")
        if data.get("supports_function_calling"): caps.append("function_calling")

        model_id = slugify(model_key)
        display_name = model_key.split("/")[-1] if "/" in model_key else model_key

        models.append({
            "id": model_id,
            "name": display_name,
            "category": category,
            "description": f"Model {provider_id.capitalize()} — {mode}.",
            "tags": [],
            "capabilities": caps,
            "context_k": context_k,
            "updated_at": str(date.today()),
            "source": "litellm",
            "providers": [
                {
                    "provider_id": provider_id,
                    "pricing": pricing,
                    "url": data.get("source", ""),
                    "affiliate_url": None,
                    "available": True
                }
            ]
        })

    return models


def merge(litellm_models: list, manual_models: list) -> list:
    """
    Scala dwie listy. Manual models mają pierwszeństwo —
    jeśli oba mają ten sam id, manual wygrywa.
    Modele z LiteLLM, których nie ma w manual, są dodawane.
    """
    manual_ids = {m["id"] for m in manual_models}
    result = list(manual_models)

    for lm in litellm_models:
        if lm["id"] not in manual_ids:
            result.append(lm)

    return result


def main():
    parser = argparse.ArgumentParser(description="Merge LiteLLM + manual model data")
    parser.add_argument("--litellm", required=True, help="Ścieżka do litellm-raw.json")
    parser.add_argument("--manual", required=True, help="Ścieżka do models-manual.json")
    parser.add_argument("--output", required=True, help="Ścieżka wyjściowa models.json")
    args = parser.parse_args()

    # Load LiteLLM
    litellm_path = Path(args.litellm)
    if not litellm_path.exists():
        print(f"✗ Brak pliku: {litellm_path}", file=sys.stderr)
        sys.exit(1)

    with open(litellm_path) as f:
        litellm_raw = json.load(f)

    litellm_models = parse_litellm(litellm_raw)
    print(f"  LiteLLM: {len(litellm_models)} modeli")

    # Load manual
    manual_path = Path(args.manual)
    if manual_path.exists():
        with open(manual_path) as f:
            manual_data = json.load(f)
        manual_models = manual_data.get("models", [])
        print(f"  Manual:  {len(manual_models)} modeli")
    else:
        print(f"  Manual:  brak (plik {manual_path} nie istnieje, pomijam)")
        manual_models = []

    merged = merge(litellm_models, manual_models)
    merged.sort(key=lambda m: m["name"].lower())
    print(f"  Razem:   {len(merged)} modeli po merge")

    output = {
        "updated_at": str(date.today()),
        "models": merged
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {args.output}")


if __name__ == "__main__":
    main()
