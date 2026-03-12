#!/usr/bin/env python3
"""
fetch-bedrock.py
Curated Amazon Bedrock models with pricing from aws.amazon.com/bedrock/pricing.
Bedrock has no machine-readable pricing API — prices are manually curated.

Użycie:
  python3 scripts/fetch-bedrock.py [ścieżka-wyjściowa]

Źródło cen: https://aws.amazon.com/bedrock/pricing/
Aktualizacja: 2026-03-12
"""

import json, sys
from datetime import datetime
from pathlib import Path

OUTPUT_DEFAULT = "data/bedrock-raw.json"
BASE_URL = "https://aws.amazon.com/bedrock/"

# Ceny on-demand (us-east-1) w USD. Cross-region inference może być droższe.
# Źródło: https://aws.amazon.com/bedrock/pricing/
# Aktualizacja: 2026-03-12
BEDROCK_MODELS = [
    # ── Amazon Nova (Bedrock-exclusive) ───────────────────────────────
    {
        "id": "amazon-nova-pro",
        "name": "Amazon Nova Pro",
        "category": "llm",
        "description": "Amazon's most capable Nova model. Multimodal (text, image, video input). 300k context.",
        "tags": ["amazon", "nova", "multimodal"],
        "capabilities": ["vision", "function_calling"],
        "pricing": {"input_per_1m": 0.80, "output_per_1m": 3.20},
        "url": "https://aws.amazon.com/bedrock/nova/",
    },
    {
        "id": "amazon-nova-lite",
        "name": "Amazon Nova Lite",
        "category": "llm",
        "description": "Fast and cost-effective multimodal model from Amazon. Text, image, video input.",
        "tags": ["amazon", "nova", "multimodal", "fast"],
        "capabilities": ["vision", "function_calling"],
        "pricing": {"input_per_1m": 0.06, "output_per_1m": 0.24},
        "url": "https://aws.amazon.com/bedrock/nova/",
    },
    {
        "id": "amazon-nova-micro",
        "name": "Amazon Nova Micro",
        "category": "llm",
        "description": "Ultra-low cost text-only model from Amazon. Fastest in the Nova family.",
        "tags": ["amazon", "nova", "fast", "cheap"],
        "capabilities": ["function_calling"],
        "pricing": {"input_per_1m": 0.035, "output_per_1m": 0.14},
        "url": "https://aws.amazon.com/bedrock/nova/",
    },
    {
        "id": "amazon-nova-canvas",
        "name": "Amazon Nova Canvas",
        "category": "image_generation",
        "description": "Amazon's image generation model. Text-to-image and image editing.",
        "tags": ["amazon", "nova", "image"],
        "capabilities": ["image_editing"],
        "pricing": {"per_image": 0.04, "notes": "$0.04/image (512px). $0.08/image (1024px)."},
        "url": "https://aws.amazon.com/bedrock/nova/",
    },
    {
        "id": "amazon-nova-reel",
        "name": "Amazon Nova Reel",
        "category": "video_generation",
        "description": "Amazon's video generation model via Bedrock. Text-to-video and image-to-video.",
        "tags": ["amazon", "nova", "video"],
        "capabilities": ["text_to_video", "image_to_video"],
        "pricing": {"per_second": 0.96},
        "url": "https://aws.amazon.com/bedrock/nova/",
    },
    # ── Anthropic on Bedrock ──────────────────────────────────────────
    {
        "id": "claude-3-7-sonnet",
        "name": "Claude 3.7 Sonnet",
        "category": "llm",
        "description": "Anthropic Claude 3.7 Sonnet on Amazon Bedrock. Extended thinking support.",
        "tags": ["anthropic", "claude"],
        "capabilities": ["vision", "reasoning", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 3.00, "output_per_1m": 15.00},
        "url": "https://aws.amazon.com/bedrock/claude/",
    },
    {
        "id": "claude-3-5-sonnet-v2",
        "name": "Claude 3.5 Sonnet v2",
        "category": "llm",
        "description": "Anthropic Claude 3.5 Sonnet v2 on Amazon Bedrock.",
        "tags": ["anthropic", "claude"],
        "capabilities": ["vision", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 3.00, "output_per_1m": 15.00},
        "url": "https://aws.amazon.com/bedrock/claude/",
    },
    {
        "id": "claude-3-5-haiku",
        "name": "Claude 3.5 Haiku",
        "category": "llm",
        "description": "Anthropic Claude 3.5 Haiku on Amazon Bedrock. Fast and affordable.",
        "tags": ["anthropic", "claude", "fast"],
        "capabilities": ["vision", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 0.80, "output_per_1m": 4.00},
        "url": "https://aws.amazon.com/bedrock/claude/",
    },
    {
        "id": "claude-3-opus",
        "name": "Claude 3 Opus",
        "category": "llm",
        "description": "Anthropic Claude 3 Opus on Amazon Bedrock.",
        "tags": ["anthropic", "claude"],
        "capabilities": ["vision", "function_calling", "prompt_caching"],
        "pricing": {"input_per_1m": 15.00, "output_per_1m": 75.00},
        "url": "https://aws.amazon.com/bedrock/claude/",
    },
    # ── Meta Llama on Bedrock ─────────────────────────────────────────
    {
        "id": "llama-3-3-70b-instruct",
        "name": "Llama 3.3 70B Instruct",
        "category": "llm",
        "description": "Meta Llama 3.3 70B on Amazon Bedrock.",
        "tags": ["meta", "llama", "open-source"],
        "capabilities": ["function_calling"],
        "pricing": {"input_per_1m": 0.72, "output_per_1m": 0.72},
        "url": "https://aws.amazon.com/bedrock/llama/",
    },
    {
        "id": "llama-3-1-405b-instruct",
        "name": "Llama 3.1 405B Instruct",
        "category": "llm",
        "description": "Meta Llama 3.1 405B on Amazon Bedrock. Largest open model.",
        "tags": ["meta", "llama", "open-source"],
        "capabilities": ["function_calling"],
        "pricing": {"input_per_1m": 2.40, "output_per_1m": 2.40},
        "url": "https://aws.amazon.com/bedrock/llama/",
    },
    {
        "id": "llama-3-2-90b-vision",
        "name": "Llama 3.2 90B Vision",
        "category": "llm",
        "description": "Meta Llama 3.2 90B multimodal on Amazon Bedrock.",
        "tags": ["meta", "llama", "multimodal", "open-source"],
        "capabilities": ["vision"],
        "pricing": {"input_per_1m": 2.00, "output_per_1m": 2.00},
        "url": "https://aws.amazon.com/bedrock/llama/",
    },
    # ── Mistral on Bedrock ────────────────────────────────────────────
    {
        "id": "mistral-large-2",
        "name": "Mistral Large 2",
        "category": "llm",
        "description": "Mistral Large 2 on Amazon Bedrock.",
        "tags": ["mistral"],
        "capabilities": ["function_calling"],
        "pricing": {"input_per_1m": 3.00, "output_per_1m": 9.00},
        "url": "https://aws.amazon.com/bedrock/mistral/",
    },
    # ── DeepSeek on Bedrock ───────────────────────────────────────────
    {
        "id": "deepseek-r1",
        "name": "DeepSeek R1",
        "category": "llm",
        "description": "DeepSeek R1 reasoning model on Amazon Bedrock.",
        "tags": ["deepseek", "reasoning", "open-source"],
        "capabilities": ["reasoning"],
        "pricing": {"input_per_1m": 1.35, "output_per_1m": 5.40},
        "url": "https://aws.amazon.com/bedrock/",
    },
    # ── Amazon Titan Embeddings ───────────────────────────────────────
    {
        "id": "amazon-titan-embed-text-v2",
        "name": "Amazon Titan Embed Text v2",
        "category": "embedding",
        "description": "Amazon Titan text embeddings v2. 1024/512/256 dimensions.",
        "tags": ["amazon", "titan", "embedding"],
        "capabilities": [],
        "pricing": {"notes": "$0.02/1M tokens"},
        "url": "https://aws.amazon.com/bedrock/titan/",
    },
    # ── Stability AI on Bedrock ───────────────────────────────────────
    {
        "id": "stable-image-ultra",
        "name": "Stable Image Ultra",
        "category": "image_generation",
        "description": "Stability AI Stable Image Ultra on Amazon Bedrock. Highest quality.",
        "tags": ["stability-ai", "image"],
        "capabilities": [],
        "pricing": {"per_image": 0.14},
        "url": "https://aws.amazon.com/bedrock/stability-ai/",
    },
    {
        "id": "stable-diffusion-3-5-large",
        "name": "Stable Diffusion 3.5 Large",
        "category": "image_generation",
        "description": "Stability AI SD 3.5 Large on Amazon Bedrock.",
        "tags": ["stability-ai", "image"],
        "capabilities": [],
        "pricing": {"per_image": 0.08},
        "url": "https://aws.amazon.com/bedrock/stability-ai/",
    },
]


def build_output(models: list) -> dict:
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
            "pricing": m["pricing"],
            "url": m["url"],
            "updated_at": today,
            "source": "bedrock",
        }
        out.append(entry)
    return {"models": out, "updated_at": today, "source": "bedrock", "count": len(out)}


def main():
    output_path = Path(sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DEFAULT)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = build_output(BEDROCK_MODELS)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✓ Amazon Bedrock: {data['count']} modeli → {output_path}")


if __name__ == "__main__":
    main()
