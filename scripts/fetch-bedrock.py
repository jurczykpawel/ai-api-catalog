#!/usr/bin/env python3
"""
fetch-bedrock.py
Auto-generates Amazon Bedrock model list from litellm-raw.json.
LiteLLM already tracks Bedrock pricing (keys: anthropic.*, amazon.nova*, meta.llama*, etc.)

Użycie:
  python3 scripts/fetch-bedrock.py [ścieżka-wyjściowa]

Źródło: litellm-raw.json (generowany przez update-litellm.sh krok [1/9])
Ręczne overrides (per-image / per-second) w PRICING_OVERRIDES poniżej.
"""

import json, re, sys
from datetime import datetime
from pathlib import Path

OUTPUT_DEFAULT = "data/bedrock-raw.json"
BASE_URL = "https://aws.amazon.com/bedrock/"

# Prefixes that identify Bedrock models in LiteLLM
BEDROCK_PREFIXES = [
    "anthropic.",
    "amazon.",
    "meta.",
    "mistral.",
    "deepseek.",
    "stability.",
    "cohere.",
    "writer.",
]

# Cross-region prefixes to skip (these are the same models at higher price)
SKIP_PREFIXES = ("us.", "eu.", "au.", "ap", "global.", "jp.", "me.", "sa.")

# Models where LiteLLM has $0 (per-image / per-second pricing not tracked)
# Source: https://aws.amazon.com/bedrock/pricing/
PRICING_OVERRIDES = {
    "amazon.nova-canvas-v1:0": {"per_image": 0.04, "notes": "$0.04/image (512px), $0.08/image (1024px)"},
    "amazon.titan-image-generator-v1": {"per_image": 0.008},
    "amazon.titan-image-generator-v2": {"per_image": 0.008},
    "amazon.titan-image-generator-v2:0": {"per_image": 0.008},
    "stability.stable-image-ultra-v1:0": {"per_image": 0.14},
    "stability.stable-image-ultra-v1:1": {"per_image": 0.14},
    "stability.sd3-5-large-v1:0": {"per_image": 0.08},
    "stability.sd3-large-v1:0": {"per_image": 0.065},
    "stability.stable-image-core-v1:0": {"per_image": 0.04},
    "stability.stable-image-core-v1:1": {"per_image": 0.04},
}

# Nova Reel not yet in LiteLLM — add manually
EXTRA_MODELS = [
    {
        "id": "amazon-nova-reel",
        "name": "Amazon Nova Reel",
        "category": "video_generation",
        "tags": ["amazon", "nova", "video"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_second": 0.96},
        "url": "https://aws.amazon.com/bedrock/nova/",
        "description": "Amazon's video generation model via Bedrock. Text-to-video and image-to-video.",
    },
]

# Provider → URL mapping
PROVIDER_URLS = {
    "anthropic": "https://aws.amazon.com/bedrock/claude/",
    "amazon": "https://aws.amazon.com/bedrock/nova/",
    "meta": "https://aws.amazon.com/bedrock/llama/",
    "mistral": "https://aws.amazon.com/bedrock/mistral/",
    "deepseek": "https://aws.amazon.com/bedrock/",
    "stability": "https://aws.amazon.com/bedrock/stability-ai/",
    "cohere": "https://aws.amazon.com/bedrock/cohere/",
    "writer": "https://aws.amazon.com/bedrock/",
}


def get_provider(raw_key: str) -> str:
    for p in BEDROCK_PREFIXES:
        if raw_key.startswith(p):
            # e.g. "anthropic." → "anthropic", "meta." → "meta"
            return p.strip(".")
    return "amazon"


def normalize_id(raw_key: str, provider: str) -> str:
    """Strip provider prefix and version suffixes to get a clean model ID."""
    key = raw_key
    # Remove provider prefix
    for p in BEDROCK_PREFIXES:
        if key.startswith(p):
            key = key[len(p):]
            break

    # Remove date+version combos: -20250514-v1:0
    key = re.sub(r"-\d{8}-v\d+[:\d]*$", "", key)
    # Remove @date: @20251001
    key = re.sub(r"@\d+$", "", key)
    # Remove -v1:0 or -v2:0
    key = re.sub(r"-v\d+[:\d]*$", "", key)
    # Remove trailing :0
    key = re.sub(r":\d+$", "", key)
    # Remove -v1 suffix
    key = re.sub(r"-v\d+$", "", key)

    # Normalize llama2/llama3 → llama-2/llama-3
    key = re.sub(r"llama(\d)", r"llama-\1", key)

    # Keep amazon prefix for Nova/Titan models
    if provider == "amazon":
        key = "amazon-" + key

    # Keep deepseek prefix
    if provider == "deepseek":
        key = "deepseek-" + key

    return key.lower()


def make_name(model_id: str) -> str:
    """Generate a human-readable name from model ID."""
    # Collapse X-Y where both X and Y are single digits → X.Y (version numbers)
    key = re.sub(r"(?<![a-z\d])(\d)-(\d)(?![\db])", r"\1.\2", model_id)

    parts = key.replace("-", " ").split()
    caps = {"amazon", "claude", "llama", "mistral", "deepseek", "cohere",
            "nova", "titan", "stable", "writer", "palmyra", "command",
            "maverick", "scout"}
    result = []
    for p in parts:
        pl = p.lower()
        if pl in caps:
            result.append(p.capitalize())
        elif re.match(r"^\d+[bkm]$", pl):  # 70b, 8k → uppercase
            result.append(p.upper())
        elif pl in ("instruct", "chat", "vision", "lite", "pro", "micro",
                    "mini", "plus", "ultra", "large", "small", "medium",
                    "embed", "text", "image", "core", "light", "premier",
                    "express", "flash", "turbo", "mini", "nano"):
            result.append(p.capitalize())
        else:
            result.append(p.upper() if re.match(r"^[a-z]+\d", p) and len(p) <= 5 else p.capitalize())
    return " ".join(result)


def get_category(mode: str, key: str) -> str:
    if mode == "embedding":
        return "embedding"
    if mode == "image_generation":
        return "image_generation"
    if mode == "image_edit":
        return "image_generation"
    if "audio" in key:
        return "audio_tts"
    return "llm"


def get_capabilities(entry: dict) -> list:
    caps = []
    if entry.get("supports_vision"):
        caps.append("vision")
    if entry.get("supports_reasoning"):
        caps.append("reasoning")
    if entry.get("supports_function_calling"):
        caps.append("function_calling")
    if entry.get("supports_prompt_caching"):
        caps.append("prompt_caching")
    if entry.get("supports_computer_use"):
        caps.append("computer_use")
    return caps


def get_tags(provider: str, key: str) -> list:
    tag_map = {
        "anthropic": ["anthropic", "claude"],
        "amazon": ["amazon", "nova" if "nova" in key else "titan"],
        "meta": ["meta", "llama", "open-source"],
        "mistral": ["mistral"],
        "deepseek": ["deepseek", "open-source"],
        "stability": ["stability-ai", "image"],
        "cohere": ["cohere"],
        "writer": ["writer"],
    }
    tags = tag_map.get(provider, [provider])
    if "instruct" in key:
        pass  # already implied
    if "embed" in key or "embed" in key:
        if "embedding" not in tags:
            tags = tags + ["embedding"]
    return tags


def get_description(model_id: str, name: str, provider: str, category: str) -> str:
    provider_names = {
        "anthropic": "Anthropic", "amazon": "Amazon", "meta": "Meta",
        "mistral": "Mistral", "deepseek": "DeepSeek", "stability": "Stability AI",
        "cohere": "Cohere", "writer": "Writer",
    }
    pname = provider_names.get(provider, provider.capitalize())
    cat_labels = {
        "llm": "language model", "embedding": "embedding model",
        "image_generation": "image generation model",
    }
    clabel = cat_labels.get(category, "model")
    return f"{pname} {name} on Amazon Bedrock."


def parse_litellm(litellm_path: Path) -> list:
    data = json.loads(litellm_path.read_text())
    today = datetime.now().strftime("%Y-%m-%d")
    seen_ids = set()
    models = []

    for raw_key, entry in data.items():
        # Skip cross-region variants
        if any(raw_key.startswith(p) for p in SKIP_PREFIXES):
            continue
        # Must match a Bedrock prefix
        if not any(raw_key.startswith(p) for p in BEDROCK_PREFIXES):
            continue
        # Must be from bedrock provider (LiteLLM marks them)
        if entry.get("litellm_provider") not in ("bedrock", "bedrock_converse"):
            continue

        provider = get_provider(raw_key)
        model_id = normalize_id(raw_key, provider)
        category = get_category(entry.get("mode", "chat"), raw_key)

        # Deduplicate (versioned + unversioned keys map to same ID)
        if model_id in seen_ids:
            continue
        seen_ids.add(model_id)

        # Build pricing
        override = PRICING_OVERRIDES.get(raw_key)
        if override:
            pricing = override
        else:
            ict = entry.get("input_cost_per_token", 0) or 0
            oct_ = entry.get("output_cost_per_token", 0) or 0
            if ict == 0 and oct_ == 0:
                # No pricing data — include with notes
                pricing = {"notes": "See aws.amazon.com/bedrock/pricing/"}
            else:
                pricing = {
                    "input_per_1m": round(ict * 1_000_000, 4),
                    "output_per_1m": round(oct_ * 1_000_000, 4),
                }
                # Cache pricing if available
                cache_write = entry.get("cache_creation_input_token_cost", 0)
                cache_read = entry.get("cache_read_input_token_cost", 0)
                if cache_write:
                    pricing["cache_write_per_1m"] = round(cache_write * 1_000_000, 4)
                if cache_read:
                    pricing["cache_read_per_1m"] = round(cache_read * 1_000_000, 4)

        name = make_name(model_id)
        models.append({
            "id": model_id,
            "name": name,
            "category": category,
            "description": get_description(model_id, name, provider, category),
            "tags": get_tags(provider, raw_key),
            "capabilities": get_capabilities(entry),
            "open_source": False,
            "local_available": False,
            "pricing": pricing,
            "url": PROVIDER_URLS.get(provider, BASE_URL),
            "updated_at": today,
            "source": "bedrock",
        })

    # Add manual extra models (not in LiteLLM)
    extra_ids = seen_ids.copy()
    for m in EXTRA_MODELS:
        if m["id"] not in extra_ids:
            models.append({
                **m,
                "open_source": False,
                "local_available": False,
                "updated_at": today,
                "source": "bedrock",
            })

    return models


def main():
    output_path = Path(sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT)
    # litellm-raw.json is in the same data/ dir
    litellm_path = output_path.parent / "litellm-raw.json"
    if not litellm_path.exists():
        print(f"✗ Brak {litellm_path} — uruchom najpierw krok [1/9]", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    models = parse_litellm(litellm_path)
    today = datetime.now().strftime("%Y-%m-%d")
    out = {"models": models, "updated_at": today, "source": "bedrock", "count": len(models)}
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✓ Amazon Bedrock: {len(models)} modeli → {output_path}")


if __name__ == "__main__":
    main()
