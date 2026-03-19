"""
llm_client.py
Shared LLM client with Anthropic -> OpenAI fallback.

Tries Anthropic first (if ANTHROPIC_API_KEY is set), falls back to OpenAI
(if OPENAI_API_KEY is set). Raises RuntimeError if both fail or neither key is set.

Usage:
    from llm_client import llm_complete
    text = llm_complete(system="You are...", user="Extract...", tier="fast")
"""

import json
import os
import urllib.request
import urllib.error

# tier -> (anthropic_model, openai_model)
MODELS = {
    "fast": ("claude-haiku-4-5-20251001", "gpt-4o-mini"),
    "smart": ("claude-sonnet-4-6", "gpt-4o"),
}


def _call_anthropic(system: str, user: str, model: str, max_tokens: int = 2048) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Anthropic HTTP {e.code}: {body}") from e

    return result["content"][0]["text"].strip()


def _call_openai(system: str, user: str, model: str, max_tokens: int = 2048) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"OpenAI HTTP {e.code}: {body}") from e

    return result["choices"][0]["message"]["content"].strip()


def llm_complete(system: str, user: str, tier: str = "fast", max_tokens: int = 2048) -> str:
    """Call LLM with Anthropic -> OpenAI fallback.

    Args:
        system: System prompt.
        user: User message.
        tier: "fast" (Haiku/gpt-4o-mini) or "smart" (Sonnet/gpt-4o).
        max_tokens: Max output tokens.

    Returns:
        LLM response text.
    """
    anthropic_model, openai_model = MODELS[tier]

    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if not has_anthropic and not has_openai:
        raise RuntimeError("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set")

    if has_anthropic:
        try:
            result = _call_anthropic(system, user, anthropic_model, max_tokens)
            print(f"  [llm] Anthropic ({anthropic_model}) OK")
            return result
        except RuntimeError as e:
            if not has_openai:
                raise
            print(f"  [llm] Anthropic failed: {e}")
            print(f"  [llm] Falling back to OpenAI ({openai_model})...")

    result = _call_openai(system, user, openai_model, max_tokens)
    print(f"  [llm] OpenAI ({openai_model}) OK")
    return result
