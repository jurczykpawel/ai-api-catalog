#!/usr/bin/env python3
"""
merge-data.py
Scala dane z LiteLLM, OpenRouter i ręcznych wpisów w models-manual.json.
Generuje finalny data/models.json.

Użycie:
  python3 scripts/merge-data.py \
      --litellm data/litellm-raw.json \
      --openrouter data/openrouter-raw.json \
      --manual data/models-manual.json \
      --output data/models.json
"""

import json
import argparse
import re
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
    "bedrock":        None,
    "azure":          None,
    "vertex_ai_beta": None,
}

# ── Modele z LiteLLM które zachowujemy ──────────────────────────
# Zamiast białej listy (KEEP_MODELS) używamy czarnej listy wzorców do pominięcia.
# Dzięki temu nowe modele pojawiają się automatycznie gdy LiteLLM je doda.
LITELLM_SKIP_PATTERNS = [
    # Fine-tuning variants — nie są standardowymi modelami API
    r"^ft:",
    # Stare, wycofane snapshot-daty (pre-2024) — nieaktualne, zaśmiecają katalog
    r"-(0301|0314|0613|1106|0125|032|0720)$",
    r"-(0301|0314|0613|1106|0125|032|0720)-",
    # Modele bez ceny — nie ma czego porównywać
    # (obsługiwane w logice parse_litellm)
]

# ── Mapowanie mode → category ────────────────────────────────────
MODE_TO_CATEGORY = {
    "chat":                "llm",
    "completion":          "llm",
    "embedding":           "embedding",
    "image_generation":    "image_generation",
    "audio_transcription": "audio_stt",
    "audio_speech":        "audio_tts",
    "moderation":          "moderation",
    "rerank":              "embedding",
}

# ── Mapowanie OpenRouter modality → category ─────────────────────
OR_MODALITY_TO_CATEGORY = {
    "text->text":                "llm",
    "text+image->text":          "llm",
    "text+image+file->text":     "llm",
    "text->image":               "image_generation",
    "text->audio":               "audio_tts",
    "text+image->image":         "image_generation",
}

# ── OR model ID → nasz internal ID (deduplication z LiteLLM) ────
OR_TO_INTERNAL_ID = {
    "openai/gpt-4o":                    "gpt-4o",
    "openai/gpt-4o-mini":               "gpt-4o-mini",
    "openai/o1":                        "o1",
    "openai/o1-mini":                   "o1-mini",
    "openai/o3":                        "o3",
    "openai/o3-mini":                   "o3-mini",
    "openai/o4-mini":                   "o4-mini",
    "openai/o3-pro":                    "o3-pro",
    "openai/chatgpt-4o-latest":         "chatgpt-4o-latest",
    "anthropic/claude-opus-4":          "claude-opus-4-6",
    "anthropic/claude-sonnet-4-5":      "claude-sonnet-4-5",
    "anthropic/claude-3-5-sonnet":      "claude-3-5-sonnet",
    "anthropic/claude-3-5-haiku":       "claude-3-5-haiku",
    "anthropic/claude-3-haiku":         "claude-3-haiku",
    "google/gemini-2.5-pro":            "gemini-gemini-2-5-pro",
    "google/gemini-2.0-flash":          "gemini-gemini-2-0-flash",
    "google/gemini-2.0-flash-lite":     "gemini-gemini-2-0-flash-lite",
    "google/gemini-1.5-pro":            "gemini-gemini-1-5-pro",
    "google/gemini-1.5-flash":          "gemini-gemini-1-5-flash",
    "mistralai/mistral-large-2411":     "mistral-mistral-large-latest",
    "mistralai/mistral-small-3.1":      "mistral-mistral-small-latest",
    "deepseek/deepseek-chat":           "deepseek-deepseek-chat",
    "deepseek/deepseek-r1":             "deepseek-reasoner",
    "x-ai/grok-3":                      "xai-grok-3",
    "x-ai/grok-3-mini":                 "xai-grok-3-mini",
    "perplexity/sonar-pro":             "perplexity-sonar-pro",
    "perplexity/sonar":                 "perplexity-sonar",
}

# ── OR modele do pominięcia (stare, duplikaty routery) ───────────
OR_SKIP_PATTERNS = [
    ":extended", ":nitro", ":floor",
    "openrouter/auto", "openrouter/free",
]


def slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r'[/:\\. ]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


# Segmenty ścieżki fal.ai oznaczające modalność — do odfiltrowania przy budowaniu ID/nazwy
FAL_MODALITY_SEGS = {
    "text-to-video", "image-to-video", "reference-to-video",
    "video-to-video", "text-to-image", "image-to-image",
    "inpainting", "editing", "edit",
}

# Regex do usuwania frazy modalności z display_name (zachowuje kwalifikator jakości po niej)
_FAL_MODALITY_STRIP_RE = re.compile(
    r'[\s,]*[\(\[]?\s*(?:text[\s\-]+to[\s\-]+video|image[\s\-]+to[\s\-]+video|'
    r'reference[\s\-]+to[\s\-]+video|video[\s\-]+to[\s\-]+video|'
    r'text[\s\-]+to[\s\-]+image|image[\s\-]+to[\s\-]+image|'
    r'image[\s\-]*editing|inpainting)\s*[\)\]]?'
    r'(\s*[\[\(]\s*[\w.]+\s*[\]\)])?$',
    re.IGNORECASE
)


def _strip_fal_modality(name: str) -> str:
    """Usuwa frazę modalności z końca nazwy, zachowując kwalifikator jakości ([Pro], [Standard] itp.)."""
    m = _FAL_MODALITY_STRIP_RE.search(name)
    if not m:
        return name
    quality = (m.group(1) or "").strip()
    result = name[:m.start()] + (" " + quality if quality else "")
    return re.sub(r"\s+", " ", result).strip()


# ── Fal.ai category → nasza category ─────────────────────────────
FAL_CATEGORY_MAP = {
    "text-to-image":  "image_generation",
    "image-to-image": "image_generation",
    "image-editing":  "image_generation",
    "text-to-video":  "video_generation",
    "image-to-video": "video_generation",
    "video-to-video": "video_generation",
    "text-to-speech": "audio_tts",
    "speech-to-text": "audio_stt",
    "text-to-music":  "music_generation",
    "text-to-audio":  "music_generation",
    "audio-to-audio": "music_generation",
}

# fal endpoint_id → nasz internal model ID
FAL_TO_INTERNAL = {
    "fal-ai/flux-pro":                    "flux-1-pro",
    "fal-ai/flux/schnell":                "flux-1-schnell",
    "fal-ai/flux-lora":                   "flux-1-dev",
    "fal-ai/stable-diffusion-v3-medium":  "stable-diffusion-3",
    "fal-ai/stable-diffusion-3-5-large":  "stable-diffusion-3-5",
    "fal-ai/cogvideox-5b":                "cogvideox-5b",
    "fal-ai/ltx-video":                   "ltx-video",
    "fal-ai/kling-video/v2.1/standard/text-to-video": "kling-2-1",
    "fal-ai/kling-video/v2.1/standard/image-to-video":"kling-2-1",
    "fal-ai/wan/t2v-14b":                 "wan-2-2",
    "fal-ai/wan/image-to-video":          "wan-2-2",
    "fal-ai/kokoro":                      "kokoro-tts",
    "fal-ai/whisper":                     "whisper-large-v3-turbo",
    "fal-ai/nano-banana-2":               "nano-banana-2",
    "fal-ai/nano-banana-2/edit":          "nano-banana-2",
    "fal-ai/nano-banana":                 "nano-banana",
    "fal-ai/ideogram/v2":                 "ideogram-v2",
    "fal-ai/recraft-v3":                  "recraft-v3",
    "fal-ai/playground-v25":              "playground-v25",
    "fal-ai/aura-flow":                   "flux-1-dev",
    "fal-ai/luma-dream-machine":          "luma-ray-2",
    "fal-ai/luma-dream-machine/image-to-video": "luma-ray-2",
    "fal-ai/minimax/video-01":            "hailuo-2-3",
    "fal-ai/sora":                        "sora-2",
}

# HuggingFace pipeline_tag → nasza category
HF_PIPELINE_MAP = {
    "text-to-image":                "image_generation",
    "text-to-video":                "video_generation",
    "image-to-video":               "video_generation",
    "text-to-speech":               "audio_tts",
    "automatic-speech-recognition": "audio_stt",
    "text-generation":              "llm",
    "text2text-generation":         "llm",
    "feature-extraction":           "embedding",
    "audio-generation":             "music_generation",
}

# HF model ID → nasz internal ID (najważniejsze modele)
HF_TO_INTERNAL = {
    "black-forest-labs/FLUX.1-schnell":              "flux-1-schnell",
    "black-forest-labs/FLUX.1-dev":                  "flux-1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0":      "stable-diffusion-xl",
    "stabilityai/stable-diffusion-3-medium-diffusers":"stable-diffusion-3",
    "stabilityai/stable-diffusion-3.5-large":        "stable-diffusion-3-5",
    "Wan-AI/Wan2.2-T2V-A14B-Diffusers":             "wan-2-2",
    "Wan-AI/Wan2.1-T2V-14B-Diffusers":              "wan-2-1",
    "meta-llama/Llama-3.1-70B-Instruct":            "llama-3-1-70b",
    "meta-llama/Llama-3.1-8B-Instruct":             "llama-3-1-8b",
    "meta-llama/Llama-3.1-405B-Instruct":           "llama-3-1-405b",
    "mistralai/Mistral-7B-Instruct-v0.3":           "mistral-7b",
    "google/gemma-3-27b-it":                        "gemma-3-27b",
    "google/gemma-3-12b-it":                        "gemma-3-12b",
    "google/gemma-3-4b-it":                         "gemma-3-4b",
    "Qwen/Qwen2.5-72B-Instruct":                    "qwen3-235b",
    "microsoft/phi-4":                              "phi-4",
    "openai/whisper-large-v3":                      "whisper-large-v3-turbo",
    "openai/whisper-large-v3-turbo":                "whisper-large-v3-turbo",
    "sentence-transformers/all-MiniLM-L6-v2":       "text-embedding-ada-002",
    "thenlper/gte-large":                           "nomic-embed",
}

# HF library_name → local_tool
HF_LOCAL_TOOL = {
    "diffusers":              "ComfyUI / diffusers",
    "transformers":           "Ollama / transformers",
    "sentence-transformers":  "sentence-transformers",
    "gguf":                   "Ollama / llama.cpp",
}


# AIMLAPI model type → nasza category (media modele)
AIMLAPI_CATEGORY_MAP = {
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
    # LLM - tylko dla deduplication
    "chat-completion":       "llm",
    "language-model":        "llm",
}

# AIMLAPI feature → capability
AIMLAPI_FEAT_CAP = {
    "openai/chat-completion.vision":   "vision",
    "openai/chat-completion.function": "function_calling",
}

# AIMLAPI model ID → nasz internal ID (deduplication)
AIMLAPI_TO_INTERNAL = {
    "openai/gpt-4o":                    "gpt-4o",
    "openai/gpt-4o-mini":               "gpt-4o-mini",
    "anthropic/claude-opus-4":          "claude-opus-4-6",
    "anthropic/claude-sonnet-4-5":      "claude-sonnet-4-5",
    "google/gemini-2.5-pro":            "gemini-gemini-2-5-pro",
    "google/gemini-2.0-flash":          "gemini-gemini-2-0-flash",
    "black-forest-labs/flux-pro":       "flux-1-pro",
    "black-forest-labs/flux-dev":       "flux-1-dev",
    "black-forest-labs/flux-schnell":   "flux-1-schnell",
    "openai/whisper-1":                 "whisper-large-v3-turbo",
    "openai/sora":                      "sora-2",
}


def parse_aimlapi(data: dict) -> list:
    """Konwertuje AIMLAPI JSON do naszego formatu."""
    models = []
    raw = data.get("models", [])

    # Typy dla których dodajemy aimlapi jako provider (reszta pochodzi z OR/LiteLLM)
    MEDIA_TYPES = {"image-generation", "text-to-image", "video-generation", "text-to-video",
                   "text-to-speech", "speech-to-text", "automatic-speech-recognition",
                   "music-generation", "text-to-music", "embedding", "embeddings"}

    for item in raw:
        mid   = item.get("id", "")
        mtype = item.get("type", "")
        cat   = AIMLAPI_CATEGORY_MAP.get(mtype)
        if not cat:
            continue

        # Dla LLM tylko jeśli nie mamy już z OR/LiteLLM
        # Dla media - zawsze dodajemy (nowe źródło dla pricing)
        caps = [AIMLAPI_FEAT_CAP[f] for f in item.get("_caps", []) + item.get("features", [])
                if f in AIMLAPI_FEAT_CAP]
        caps = list(set(caps))

        internal_id = AIMLAPI_TO_INTERNAL.get(mid)
        if internal_id is None:
            # Generuj slug z ID
            parts = mid.split("/")
            base = parts[-1] if len(parts) > 1 else mid
            internal_id = slugify(base)

        desc = item.get("description") or ""
        if len(desc) > 300:
            desc = desc[:297] + "..."

        models.append({
            "_internal_id": internal_id,
            "id":           internal_id,
            "name":         item.get("name", mid),
            "category":     cat,
            "description":  desc,
            "tags":         [],
            "capabilities": caps,
            "context_k":    item.get("context_length"),
            "updated_at":   str(date.today()),
            "source":       "aimlapi",
            "providers": [
                {
                    "provider_id":   "aimlapi",
                    "pricing":       {"notes": "Check aimlapi.com for current pricing"},
                    "url":           item.get("url") or f"https://aimlapi.com/models/{slugify(mid)}",
                    "affiliate_url": None,
                    "available":     True,
                }
            ]
        })

    return models


def parse_replicate(data: dict) -> list:
    """Konwertuje Replicate API JSON do naszego formatu."""
    models = []
    results = data.get("results", [])

    # Słowa kluczowe → kategoria
    IMAGE_KW  = {"image", "flux", "sdxl", "stable-diffusion", "dall-e", "midjourney",
                 "txt2img", "text-to-image", "inpainting", "upscale", "photo", "portrait"}
    VIDEO_KW  = {"video", "animate", "motion", "wan", "kling", "sora", "hailuo",
                 "txt2vid", "img2vid", "text-to-video", "image-to-video"}
    AUDIO_KW  = {"tts", "speech", "voice", "whisper", "audio", "transcribe", "asr"}
    MUSIC_KW  = {"music", "musicgen", "audiogen", "song", "melody"}
    EMBED_KW  = {"embed", "embedding", "similarity", "clip", "sentence"}
    LLM_KW    = {"llm", "chat", "llama", "mistral", "gpt", "language-model", "text-generation"}

    def guess_category(name: str, desc: str, inp: dict) -> str | None:
        text = (name + " " + (desc or "")).lower()
        inp_keys = set((inp or {}).keys())
        if any(k in text for k in VIDEO_KW) or "video" in inp_keys:
            return "video_generation"
        if any(k in text for k in MUSIC_KW):
            return "music_generation"
        if any(k in text for k in AUDIO_KW):
            return "audio_stt" if any(k in text for k in {"whisper","transcribe","asr","speech-to-text"}) else "audio_tts"
        if any(k in text for k in EMBED_KW):
            return "embedding"
        if any(k in text for k in IMAGE_KW) or "prompt" in inp_keys:
            return "image_generation"
        if any(k in text for k in LLM_KW):
            return "llm"
        return None

    for item in results:
        if item.get("visibility") != "public":
            continue
        run_count = item.get("run_count", 0) or 0
        # Skip obscure fine-tunes — keep official or popular
        if not item.get("is_official") and run_count < 10_000:
            continue

        owner = item.get("owner", "")
        name  = item.get("name", "")
        url   = item.get("url", "")
        desc  = (item.get("description") or "")[:300]
        ex    = item.get("default_example") or {}
        inp   = ex.get("input", {})

        cat = guess_category(name, desc, inp)
        if not cat:
            continue

        # Internal ID: owner/name → slug
        full_name = f"{owner}/{name}"
        internal_id = "replicate-" + slugify(name)

        # Open source hints (github_url with "proxy" or "cog-" wrappers are not real OSS)
        gh_url = item.get("github_url") or ""
        is_proxy = any(kw in gh_url.lower() for kw in ("proxy", "cog-"))
        is_oss = bool(item.get("weights_url") or (gh_url and not is_proxy))

        models.append({
            "_internal_id": internal_id,
            "id":           internal_id,
            "name":         name.replace("-", " ").title(),
            "category":     cat,
            "description":  desc,
            "tags":         ["open-source"] if is_oss else [],
            "capabilities": [],
            "context_k":    None,
            "open_source":  is_oss,
            "local_available": False,
            "updated_at":   str(date.today()),
            "source":       "replicate",
            "providers": [
                {
                    "provider_id":   "replicate",
                    "pricing":       {"notes": f"Run count: {run_count:,}. Check replicate.com for pricing."},
                    "url":           url,
                    "affiliate_url": "https://replicate.com?utm_source=tsa",
                    "available":     True,
                }
            ]
        })

    return models


def parse_curated(data: dict, provider_id: str, affiliate_url: str | None = None) -> list:
    """
    Generyczny parser dla curated źródeł (piapi, wavespeed, kie, runway).
    Modele mają już strukturę bliską naszemu schematowi.
    """
    models = []
    raw = data.get("models", [])

    for item in raw:
        mid     = item.get("id", "")
        cat     = item.get("category", "")
        pricing = item.get("pricing", {})
        af_url  = item.get("affiliate_url", affiliate_url)

        if not mid or not cat:
            continue

        # Usuń pola które nie należą do schematu
        clean = {k: v for k, v in item.items()
                 if k not in ("credits", "notes", "affiliate_url")}

        clean["_internal_id"] = mid
        clean["source"]       = provider_id
        clean["updated_at"]   = str(date.today())
        clean.setdefault("tags", [])
        clean.setdefault("capabilities", [])
        clean.setdefault("context_k", None)

        prov_entry = {
            "provider_id":   provider_id,
            "pricing":       pricing,
            "url":           item.get("url", ""),
            "affiliate_url": af_url,
            "available":     True,
        }
        if item.get("notes"):
            prov_entry["notes"] = item["notes"]

        clean["providers"] = [prov_entry]
        models.append(clean)

    return models


def parse_fal(fal_data: dict) -> list:
    """Konwertuje fal.ai raw JSON do naszego formatu.

    Warianty modelu (text-to-video / image-to-video itp.) są scalane
    w jeden wpis z unią capabilities, bo to ten sam model na tym samym
    providerze — różni się tylko endpoint.
    """
    by_id: dict = {}  # internal_id → model dict
    raw = fal_data.get("models", [])

    for item in raw:
        eid = item.get("endpoint_id", "")
        meta = item.get("metadata", {})
        cat_raw = meta.get("category", "")
        our_cat = FAL_CATEGORY_MAP.get(cat_raw)
        if not our_cat:
            continue

        caps = []
        if "edit" in eid or cat_raw in ("image-to-image", "image-editing"):
            caps.append("image_editing")
        if cat_raw == "image-to-video":
            caps.append("image_to_video")
        if cat_raw == "text-to-video":
            caps.append("text_to_video")

        display_name = meta.get("display_name") or ""
        path_parts = eid.replace("fal-ai/", "").split("/")

        # Usuń WSZYSTKIE segmenty modalności ze ścieżki (może być w środku: /text-to-video/pro)
        base_parts = [p for p in path_parts if p.lower() not in FAL_MODALITY_SEGS]

        # Gdy display_name to tylko nazwa firmy/org (pierwszy segment ścieżki),
        # budujemy czytelną nazwę z reszty endpoint_id (bez segmentów modalności)
        if not display_name or (len(path_parts) > 1 and display_name.lower().strip() == path_parts[0].lower().strip()):
            rest = base_parts[1:]
            # Normalizuj wersje: v1.5 → 1.5, v1 → 1.0 (spójność wyświetlania)
            rest = [re.sub(r'^v(\d)', r'\1', p) for p in rest]
            rest = [re.sub(r'^(\d+)$', r'\1.0', p) for p in rest]
            raw_name = " ".join(rest).replace("-", " ").title()
            # Przywróć kropki w wersjach: "1 5" → "1.5" (ale nie "5 B" → "5.B")
            display_name = re.sub(r'(\d) (\d)(?!\w)', r'\1.\2', raw_name)
        if not display_name:
            display_name = "/".join(base_parts[1:]).replace("/", " ").replace("-", " ").title()

        # Usuń frazę modalności z display_name (także gdy pochodzi z metadata)
        display_name = _strip_fal_modality(display_name)

        description = meta.get("description") or ""
        if len(description) > 300:
            description = description[:297] + "..."

        # Sprawdź mapowanie na istniejący model
        internal_id = FAL_TO_INTERNAL.get(eid)
        if internal_id is None:
            # Budujemy ID ze ścieżki bez segmentów modalności
            internal_id = slugify("/".join(base_parts))

        if internal_id in by_id:
            # Scalamy capabilities wariantów tego samego modelu
            existing = by_id[internal_id]
            existing_caps = set(existing.get("capabilities", []))
            existing_caps.update(caps)
            existing["capabilities"] = sorted(existing_caps)
            # Lepsza descripja wygrywa
            if description and len(description) > len(existing.get("description", "")):
                existing["description"] = description
        else:
            by_id[internal_id] = {
                "_fal_eid":      eid,
                "_internal_id":  internal_id,
                "id":            internal_id,
                "name":          display_name,
                "category":      our_cat,
                "description":   description,
                "tags":          [],
                "capabilities":  caps,
                "context_k":     None,
                "updated_at":    str(date.today()),
                "source":        "fal",
                "providers": [
                    {
                        "provider_id":   "fal",
                        "pricing":       {"notes": "Check fal.ai for current pricing"},
                        "url":           f"https://fal.ai/models/{eid}",
                        "affiliate_url": "https://fal.ai?ref=tsa",
                        "available":     True,
                    }
                ]
            }

    return list(by_id.values())


def parse_huggingface(hf_data: dict) -> list:
    """Konwertuje HuggingFace raw JSON do naszego formatu."""
    models = []
    raw = hf_data.get("models", [])

    for item in raw:
        hf_id = item.get("id", "")
        pipeline = item.get("pipeline_tag", "")
        our_cat  = HF_PIPELINE_MAP.get(pipeline)
        if not our_cat:
            continue

        tags = item.get("tags", [])
        lib  = item.get("library_name", "")

        # Caps
        caps = []
        if "vision" in tags or "image-text-to-text" in tags:
            caps.append("vision")
        if pipeline in ("text-to-video", "image-to-video"):
            caps.append("text_to_video" if pipeline == "text-to-video" else "image_to_video")

        # License
        lic = next((t for t in tags if t.startswith("license:")), "")
        is_open = bool(lic) and "proprietary" not in lic

        # Local tool
        local_tool = HF_LOCAL_TOOL.get(lib, "transformers / diffusers")

        # Name — use last segment of HF ID
        name = hf_id.split("/")[-1].replace("-", " ").replace("_", " ")

        # Description
        downloads = item.get("downloads", 0)
        likes     = item.get("likes", 0)
        desc = f"Open-source model on HuggingFace. {downloads:,} downloads · {likes:,} likes. License: {lic.replace('license:','')}."

        # Internal ID mapping
        internal_id = HF_TO_INTERNAL.get(hf_id)
        if internal_id is None:
            internal_id = "hf-" + slugify(hf_id.split("/")[-1])

        providers = []
        if "endpoints_compatible" in tags:
            providers.append({
                "provider_id":   "huggingface",
                "pricing":       {"notes": "Via HF Inference API — check hf.co/pricing"},
                "url":           f"https://huggingface.co/{hf_id}",
                "affiliate_url": None,
                "available":     True,
            })

        models.append({
            "_hf_id":       hf_id,
            "_internal_id": internal_id,
            "id":           internal_id,
            "name":         name,
            "category":     our_cat,
            "description":  desc,
            "tags":         ["open-source"] + (["local"] if is_open else []),
            "capabilities": caps,
            "context_k":    None,
            "open_source":  is_open,
            "local_available": is_open,
            "local_tool":   local_tool if is_open else None,
            "updated_at":   str(date.today()),
            "source":       "huggingface",
            "providers":    providers,
        })

    return models


def parse_fireworks(fw_data: dict, litellm_data: dict = None) -> list:
    """Konwertuje Fireworks AI API JSON do naszego formatu.
    Ceny pobiera z LiteLLM (fireworks_ai/accounts/fireworks/models/{id}).
    """
    # Buduj lookup cen z LiteLLM
    fw_prices: dict = {}
    if litellm_data:
        prefix = "fireworks_ai/accounts/fireworks/models/"
        for key, val in litellm_data.items():
            if key.startswith(prefix):
                model_id = key[len(prefix):]
                inp = val.get("input_cost_per_token", 0) or 0
                out = val.get("output_cost_per_token", 0) or 0
                if inp > 0 or out > 0:
                    fw_prices[model_id] = {
                        "input_per_1m": round(inp * 1_000_000, 4),
                        "output_per_1m": round(out * 1_000_000, 4),
                    }

    models = []
    for item in fw_data.get("models", []):
        # name format: "accounts/fireworks/models/deepseek-r1"
        name_path = item.get("name", "")
        model_id = name_path.split("/")[-1] if "/" in name_path else name_path
        if not model_id:
            continue

        display_name = item.get("displayName", model_id)
        description = (item.get("description", "") or "")[:300]
        context_k = round(item["contextLength"] / 1000) if item.get("contextLength") else None

        caps = []
        if item.get("supportsImageInput"):
            caps.append("vision")
        if item.get("supportsTools"):
            caps.append("function_calling")

        pricing = fw_prices.get(model_id, {"notes": "Check fireworks.ai for pricing"})

        internal_id = slugify(f"fireworks-{model_id}")

        models.append({
            "_internal_id": internal_id,
            "id": internal_id,
            "name": display_name,
            "category": "llm",
            "description": description,
            "tags": [],
            "capabilities": caps,
            "context_k": context_k,
            "updated_at": str(date.today()),
            "source": "fireworks",
            "providers": [{
                "provider_id": "fireworks",
                "pricing": pricing,
                "url": f"https://fireworks.ai/models/fireworks/{model_id}",
                "affiliate_url": None,
                "available": True,
            }],
        })

    return models


def parse_litellm(litellm_data: dict) -> list:
    """Konwertuje LiteLLM JSON do naszego formatu."""
    models = []

    for model_key, data in litellm_data.items():
        if model_key == "sample_spec":
            continue

        provider_raw = data.get("litellm_provider", "")
        provider_id = PROVIDER_MAP.get(provider_raw)

        if provider_id is None:
            continue

        # Agregatory z LiteLLM: przepuszczamy modele z pełną nazwą (accounts/.../models/ID)
        # Pomijamy tier-based (np. fireworks-ai-4.1b-to-16b)
        AGGREGATOR_PROVIDERS = {"fireworks", "together"}
        if provider_id in AGGREGATOR_PROVIDERS:
            if "/models/" not in model_key:
                continue
            if model_key.endswith("/"):
                continue
        else:
            # Pomiń modele bez ceny
            if not data.get("input_cost_per_token") and not data.get("output_cost_per_token"):
                continue
            # Pomiń wzorce z czarnej listy (stare snapshoty, ft:, itp.)
            if any(re.search(pat, model_key) for pat in LITELLM_SKIP_PATTERNS):
                continue

        mode = data.get("mode", "chat")
        category = MODE_TO_CATEGORY.get(mode, "llm")

        pricing = {}
        if data.get("input_cost_per_token"):
            pricing["input_per_1m"] = round(data["input_cost_per_token"] * 1_000_000, 4)
        if data.get("output_cost_per_token"):
            pricing["output_per_1m"] = round(data["output_cost_per_token"] * 1_000_000, 4)
        if data.get("output_cost_per_image"):
            pricing["per_image"] = round(data["output_cost_per_image"], 4)
        if data.get("input_cost_per_audio_token"):
            pricing["per_minute"] = round(data["input_cost_per_audio_token"] * 1500, 4)

        context_k = None
        max_tokens = data.get("max_input_tokens") or data.get("max_tokens")
        if max_tokens:
            context_k = round(max_tokens / 1000)

        caps = []
        if data.get("supports_vision"):          caps.append("vision")
        if data.get("supports_reasoning"):       caps.append("reasoning")
        if data.get("supports_function_calling"): caps.append("function_calling")

        model_id = slugify(model_key)
        # Strip date suffixes for canonical IDs (dedup with Bedrock/OpenRouter)
        # e.g. claude-3-5-haiku-20241022 → claude-3-5-haiku
        #      o1-2024-12-17 → o1
        model_id = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', model_id)  # YYYY-MM-DD
        model_id = re.sub(r'-\d{8}$', '', model_id)               # YYYYMMDD

        # Dla agregatrów: nazwa = ostatni segment (np. deepseek-r1)
        # Dla bezpośrednich: nazwa = cały klucz lub ostatni segment po /
        raw_name = model_key.split("/")[-1] if "/" in model_key else model_key
        raw_name = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', raw_name)  # Remove date from display name
        raw_name = re.sub(r'-\d{8}$', '', raw_name)
        display_name = raw_name.replace("-", " ").replace("_", " ").title()

        models.append({
            "id": model_id,
            "name": display_name,
            "category": category,
            "description": f"{provider_id.capitalize()} {display_name} — {mode} model.",
            "description_pl": f"Model {provider_id.capitalize()} — {mode}.",
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


def _or_paid_slugs(raw_models: list) -> set:
    """Zwraca zbiór slugów OR które mają płatny endpoint (prompt > 0 lub img > 0).
    Używane do rozróżnienia free_type: tier vs open.
    """
    paid = set()
    for m in raw_models:
        ep = m.get("endpoint") or {}
        if ep.get("is_free"):
            continue
        p = ep.get("pricing") or m.get("pricing") or {}
        try:
            if (float(p.get("prompt", 0) or 0) > 0 or
                    float(p.get("completion", 0) or 0) > 0 or
                    float(p.get("image_output", 0) or 0) > 0):
                paid.add(m.get("slug") or m.get("id", ""))
        except (ValueError, TypeError):
            pass
    return paid


def parse_openrouter(or_data: dict) -> list:
    """Konwertuje OpenRouter API JSON do naszego formatu.

    Obsługuje oba formaty:
    - /api/v1/models: pola 'id', 'architecture', 'pricing' na top-level
    - /api/frontend/models: pola 'slug', modalities na top-level, pricing w 'endpoint'
    """
    models = []
    raw_models = or_data.get("data", [])

    # Pass 1: zbierz płatne slugi (do detekcji free_type)
    paid_slugs = _or_paid_slugs(raw_models)

    for data in raw_models:
        # Obsługa obu formatów: v1 używa 'id', frontend używa 'slug'
        model_id_or = data.get("id") or data.get("slug", "")
        if not model_id_or:
            continue

        # Pomijamy specjalne wpisy
        if any(pat in model_id_or for pat in OR_SKIP_PATTERNS):
            continue

        # Pomijamy modele ukryte (frontend API)
        if data.get("hidden"):
            continue

        # Wariant :free → strip suffix, zapamiętaj flagę (tylko w v1 API)
        is_free_tier = model_id_or.endswith(":free")
        model_id_base = model_id_or[:-5] if is_free_tier else model_id_or

        # Frontend API: is_free w endpoint
        endpoint = data.get("endpoint") or {}
        if endpoint.get("is_free"):
            is_free_tier = True

        # Modalities — frontend API ma je bezpośrednio, v1 API pod 'architecture'
        arch = data.get("architecture", {})
        out_mod = data.get("output_modalities") or arch.get("output_modalities", [])
        input_mod = data.get("input_modalities") or arch.get("input_modalities", [])

        # Mapujemy modality → category
        modality = arch.get("modality", "")
        category = OR_MODALITY_TO_CATEGORY.get(modality)
        if category is None:
            if "image" in out_mod:
                category = "image_generation"
            elif "audio" in out_mod:
                category = "audio_tts"
            else:
                category = "llm"

        # Pricing — frontend API: endpoint.pricing; v1 API: data.pricing
        p = endpoint.get("pricing") or data.get("pricing") or {}
        pricing = {}
        free_api = is_free_tier

        try:
            prompt_cost = float(p.get("prompt", 0) or 0)
            completion_cost = float(p.get("completion", 0) or 0)
            image_out_cost = float(p.get("image_output", 0) or 0)
            has_pricing = bool(p)  # Tylko jeśli mamy jakiekolwiek dane cennikowe

            if category == "image_generation" and image_out_cost > 0:
                # OR image models: szukaj cents_per_image_output w pricing_json
                pricing_json = endpoint.get("pricing_json") or {}
                per_image_cents = None
                for k, v in pricing_json.items():
                    if "cents_per_image" in k and str(v).isdigit():
                        per_image_cents = int(v)
                        break
                if per_image_cents is not None:
                    pricing["per_image"] = round(per_image_cents / 100, 4)
                else:
                    pricing["notes"] = "Check openrouter.ai for pricing"
            elif has_pricing and prompt_cost == 0 and completion_cost == 0 and not image_out_cost:
                # Tylko oznaczamy jako free jeśli mamy dane cennikowe i wynoszą 0
                # (nie gdy brak endpointu = brak danych)
                pricing["input_per_1m"] = 0
                pricing["output_per_1m"] = 0
                free_api = True
            elif has_pricing:
                if prompt_cost > 0:
                    pricing["input_per_1m"] = round(prompt_cost * 1_000_000, 4)
                if completion_cost > 0:
                    pricing["output_per_1m"] = round(completion_cost * 1_000_000, 4)
        except (ValueError, TypeError):
            pass

        # Context
        context_k = None
        ctx = data.get("context_length")
        if ctx:
            context_k = round(ctx / 1000)

        # Capabilities
        caps = []
        if "image" in input_mod:
            caps.append("vision")
        params = (endpoint.get("supported_parameters") or
                  data.get("supported_parameters") or [])
        if "tools" in params or "tool_choice" in params:
            caps.append("function_calling")
        if (data.get("supports_reasoning") or
                "reasoning" in params or "include_reasoning" in params):
            caps.append("reasoning")

        # Nazwa i ID
        display_name = (data.get("name") or data.get("short_name") or model_id_or).strip()
        # Usuń prefix providera ("OpenAI: GPT-4o" → "GPT-4o")
        if ": " in display_name:
            display_name = display_name.split(": ", 1)[1].strip()
        # Usuń "(free)" suffix
        if is_free_tier:
            display_name = re.sub(r'\s*\(free\)\s*$', '', display_name, flags=re.IGNORECASE).strip()

        internal_id = OR_TO_INTERNAL_ID.get(model_id_base) or OR_TO_INTERNAL_ID.get(model_id_or)
        if internal_id is None:
            internal_id = slugify(model_id_base)

        description = data.get("description", "") or ""
        if len(description) > 300:
            description = description[:297] + "..."

        models.append({
            "_or_id": model_id_or,
            "_internal_id": internal_id,
            "id": internal_id,
            "name": display_name,
            "category": category,
            "description": description,
            "tags": [],
            "capabilities": caps,
            "context_k": context_k,
            "updated_at": str(date.today()),
            "source": "openrouter",
            "providers": [
                {
                    "provider_id": "openrouter",
                    "pricing": pricing,
                    "url": f"https://openrouter.ai/{model_id_base}",
                    "affiliate_url": "https://openrouter.ai/?ref=tsa",
                    "available": True,
                    **({"free_api": True,
                        "free_type": "tier" if model_id_base in paid_slugs else "open"
                        } if free_api else {}),
                }
            ]
        })

    return models


def _infer_capabilities(models: list) -> None:
    """
    Uzupełnia capabilities na podstawie kategorii i nazwy modelu.
    Działa jako post-processing po merge — nie nadpisuje istniejących.
    """
    I2V_HINTS = {"image-to-video", "i2v", "img2vid", "image_to_video", "img-to-video",
                 "animate", "image2video", "img2video"}
    T2V_HINTS = {"text-to-video", "t2v", "txt2vid", "text_to_video", "txt-to-video",
                 "text2video", "txt2video"}
    EDIT_HINTS = {"edit", "inpaint", "outpaint", "erase", "remove", "replace",
                  "kontext", "fill", "retouch"}

    for m in models:
        cat  = m.get("category", "")
        name = (m.get("name", "") + " " + m.get("id", "")).lower()
        caps = set(m.get("capabilities") or [])

        if cat == "video_generation":
            # Domyślnie zakładamy text→video jeśli brak wskazówki
            if any(h in name for h in I2V_HINTS):
                caps.add("image_to_video")
            elif any(h in name for h in T2V_HINTS):
                caps.add("text_to_video")
            else:
                # Brak wskazówki → zakładamy oba (większość modeli wideo obsługuje obie)
                caps.add("text_to_video")
                if any(h in name for h in {"i2v", "image", "img", "animate"}):
                    caps.add("image_to_video")

        elif cat == "image_generation":
            if any(h in name for h in EDIT_HINTS):
                caps.add("image_editing")

        m["capabilities"] = sorted(caps)


LOCAL_TOOL_BY_CATEGORY = {
    "llm":              "Ollama / transformers",
    "embedding":        "Ollama / sentence-transformers",
    "image_generation": "ComfyUI / diffusers",
    "video_generation": "ComfyUI / diffusers",
    "audio_stt":        "faster-whisper / whisper.cpp",
    "audio_tts":        "kokoro-fastapi / transformers",
    "music_generation": "transformers / audiocraft",
}


def _infer_local(models: list) -> None:
    """Uzupełnia local_available i local_tool dla open-source modeli które ich nie mają."""
    for m in models:
        if not m.get("open_source"):
            continue
        if m.get("local_available"):
            continue  # Już ustawione (np. przez HF parser lub manual)
        cat = m.get("category", "")
        tool = LOCAL_TOOL_BY_CATEGORY.get(cat)
        if tool:
            m["local_available"] = True
            m["local_tool"] = tool


def merge(litellm_models: list, or_models: list, fal_models: list,
          hf_models: list, manual_models: list,
          aimlapi_models: list = None, piapi_models: list = None,
          wavespeed_models: list = None, kie_models: list = None,
          runway_models: list = None,
          minimax_models: list = None,
          bedrock_models: list = None,
          replicate_models: list = None,
          fireworks_models: list = None,
          opencode_models: list = None) -> list:
    """
    Scala trzy źródła. Priorytet: manual > litellm/openrouter.
    OR modele z mapowaniem są doklejane jako dodatkowy provider do istniejącego modelu.
    """
    # Budujemy słownik istniejących modeli (manual + litellm)
    result_by_id = {}

    # Manual ma najwyższy priorytet
    for m in manual_models:
        result_by_id[m["id"]] = m

    # LiteLLM
    for m in litellm_models:
        if m["id"] not in result_by_id:
            result_by_id[m["id"]] = m
        else:
            # Doklejamy provider do istniejącego modelu
            existing = result_by_id[m["id"]]
            existing_pids = {p["provider_id"] for p in existing["providers"]}
            for prov in m["providers"]:
                if prov["provider_id"] not in existing_pids:
                    existing["providers"].append(prov)

    def _merge_source(source_models: list, provider_key: str, id_field: str = "_internal_id", or_field: str = None):
        for m in source_models:
            internal_id = m.pop(id_field, m.get("id"))
            if or_field:
                m.pop(or_field, None)
            m.pop("_fal_eid", None)
            m.pop("_hf_id", None)

            if internal_id in result_by_id:
                existing = result_by_id[internal_id]
                existing_pids = {p["provider_id"] for p in existing.get("providers", [])}
                for prov in m.get("providers", []):
                    if prov["provider_id"] not in existing_pids:
                        existing.setdefault("providers", []).append(prov)
                # Upgrade weak descriptions
                if m.get("description") and (
                    not existing.get("description") or
                    existing.get("description", "").startswith("Model ") or
                    len(existing.get("description", "")) < 20
                ):
                    existing["description"] = m["description"]
                # Merge open_source flag
                if m.get("open_source") and not existing.get("open_source"):
                    existing["open_source"] = True
                    existing["local_available"] = m.get("local_available", False)
                    if m.get("local_tool"):
                        existing.setdefault("local_tool", m["local_tool"])
            else:
                m["id"] = internal_id
                result_by_id[internal_id] = m

    # OpenRouter
    _merge_source(or_models,  "openrouter", "_internal_id", "_or_id")
    # Fal.ai
    _merge_source(fal_models, "fal",        "_internal_id")
    # HuggingFace
    _merge_source(hf_models,  "huggingface","_internal_id")
    # AIMLAPI
    if aimlapi_models:
        _merge_source(aimlapi_models, "aimlapi", "_internal_id")
    # piapi.ai
    if piapi_models:
        _merge_source(piapi_models, "piapi", "_internal_id")
    # WaveSpeed
    if wavespeed_models:
        _merge_source(wavespeed_models, "wavespeed", "_internal_id")
    # kie.ai
    if kie_models:
        _merge_source(kie_models, "kie", "_internal_id")
    # Runway ML
    if runway_models:
        _merge_source(runway_models, "runway", "_internal_id")
    if minimax_models:
        _merge_source(minimax_models, "minimax", "_internal_id")
    if bedrock_models:
        _merge_source(bedrock_models, "bedrock", "_internal_id")
    # Replicate
    if replicate_models:
        _merge_source(replicate_models, "replicate", "_internal_id")
    if fireworks_models:
        _merge_source(fireworks_models, "fireworks", "_internal_id")
    if opencode_models:
        _merge_source(opencode_models, "opencode", "_internal_id")

    result = list(result_by_id.values())

    # ── Name-based deduplication ──────────────────────────────────
    # Gdy dwa modele mają identyczną nazwę (różne ID, różne źródła),
    # zachowujemy ten o wyższym priorytecie źródła i doklejamy
    # providerów z duplikatu. Priorytet: manual > litellm > curated > fal > replicate > hf > aimlapi
    SOURCE_PRIORITY = {"manual": 0, "litellm": 1, "openrouter": 1, "piapi": 2, "wavespeed": 2,
                       "kie": 2, "runway": 2, "opencode": 2, "aimlapi": 3, "fal": 4, "replicate": 5, "huggingface": 6}

    by_norm_name: dict = {}
    for m in result:
        # Normalizacja nazwy dla dedup: myślniki/podkreślenia → spacje, "1.0" → "1"
        norm = m["name"].strip().lower()
        norm = re.sub(r'[-_]', ' ', norm)
        norm = re.sub(r'\b(\d+)\.0\b', r'\1', norm)
        # Normalize "3.5" → "3 5" so "Claude 3.5 Haiku" == "Claude 3 5 Haiku"
        norm = re.sub(r'(\d)\.(\d)', r'\1 \2', norm)
        # Strip dates: "2024-10-22", "20241022", "2024 10 22" patterns
        norm = re.sub(r'\b20\d{2}[-\s]?\d{2}[-\s]?\d{2}\b', '', norm)
        norm = re.sub(r'\b20\d{6}\b', '', norm)
        # Strip parenthetical content: "(2024-10-22)", "(preview)", etc.
        norm = re.sub(r'\([^)]*\)', '', norm)
        # Sort tokens for word-order invariance on short model names
        # "claude haiku 4 5" == "claude 4 5 haiku" after sort
        tokens = norm.split()
        norm = ' '.join(sorted(tokens))
        norm = re.sub(r'\s+', ' ', norm).strip()
        if norm not in by_norm_name:
            by_norm_name[norm] = m
        else:
            existing = by_norm_name[norm]
            prio_existing = SOURCE_PRIORITY.get(existing.get("source", ""), 99)
            prio_new      = SOURCE_PRIORITY.get(m.get("source", ""), 99)
            # Wyższy priorytet wygrywa (niższy numer)
            if prio_new < prio_existing:
                winner, loser = m, existing
                by_norm_name[norm] = winner
            else:
                winner, loser = existing, m
            # Jeśli zwycięzca ma slug-like (lowercase) nazwę, a przegrany ma proper-case — używamy lepszej
            def _has_proper_case(name: str) -> bool:
                """True jeśli nazwa ma wielkie litery (nie jest czysto lowercase/slug)."""
                return any(c.isupper() for c in name)
            if not _has_proper_case(winner.get("name", "")) and _has_proper_case(loser.get("name", "")):
                winner["name"] = loser["name"]
            # Doklejamy unikalne providery z przegranego
            winner_pids = {p["provider_id"] for p in winner.get("providers", [])}
            for prov in loser.get("providers", []):
                if prov["provider_id"] not in winner_pids:
                    winner.setdefault("providers", []).append(prov)
                    winner_pids.add(prov["provider_id"])
            # Uzupełniamy brakujące metadane
            if not winner.get("description") and loser.get("description"):
                winner["description"] = loser["description"]
            if loser.get("open_source") and not winner.get("open_source"):
                winner["open_source"] = True
            if loser.get("versions") and not winner.get("versions"):
                winner["versions"] = loser["versions"]

    result = list(by_norm_name.values())
    # ─────────────────────────────────────────────────────────────

    # Post-processing: czyść nazwy i usuń puste
    cleaned = []
    for m in result:
        name = m.get("name", "").strip()
        if not name:
            continue  # Pomiń modele bez nazwy
        # Slug-like lowercase names (e.g. "o3", "o3-pro") → title-case them
        if name == name.lower() and not any(c in name for c in '/('):
            name = name.replace('-', ' ').replace('_', ' ').title()
        m["name"] = name
        # Nazwy za krótkie (1 znak) lub tylko cyfry — dodaj prefix z ID
        if len(name) <= 1 or (len(name) <= 3 and name.isdigit()):
            prefix = m["id"].split("-")[0].title()
            m["name"] = f"{prefix} {name}"
        cleaned.append(m)
    result = cleaned

    _infer_capabilities(result)
    _infer_local(result)
    return result


def main():
    parser = argparse.ArgumentParser(description="Merge LiteLLM + OpenRouter + fal.ai + HuggingFace + AIMLAPI + piapi + wavespeed + kie + runway + manual")
    parser.add_argument("--litellm",     required=True, help="Ścieżka do litellm-raw.json")
    parser.add_argument("--openrouter",  help="Ścieżka do openrouter-raw.json (opcjonalne)")
    parser.add_argument("--fal",         help="Ścieżka do fal-raw.json (opcjonalne)")
    parser.add_argument("--huggingface", help="Ścieżka do huggingface-raw.json (opcjonalne)")
    parser.add_argument("--aimlapi",     help="Ścieżka do aimlapi-raw.json (opcjonalne)")
    parser.add_argument("--piapi",       help="Ścieżka do piapi-raw.json (opcjonalne)")
    parser.add_argument("--wavespeed",   help="Ścieżka do wavespeed-raw.json (opcjonalne)")
    parser.add_argument("--kie",         help="Ścieżka do kie-raw.json (opcjonalne)")
    parser.add_argument("--runway",      help="Ścieżka do runway-raw.json (opcjonalne)")
    parser.add_argument("--minimax",     help="Ścieżka do minimax-raw.json (opcjonalne)")
    parser.add_argument("--bedrock",     help="Ścieżka do bedrock-raw.json (opcjonalne)")
    parser.add_argument("--replicate",   help="Ścieżka do replicate-raw.json (opcjonalne)")
    parser.add_argument("--fireworks",   help="Ścieżka do fireworks-raw.json (opcjonalne)")
    parser.add_argument("--opencode",    help="Ścieżka do opencode-raw.json (opcjonalne)")
    parser.add_argument("--manual",      required=True, help="Ścieżka do models-manual.json")
    parser.add_argument("--output",      required=True, help="Ścieżka wyjściowa models.json")
    args = parser.parse_args()

    # Load LiteLLM
    litellm_path = Path(args.litellm)
    if not litellm_path.exists():
        print(f"✗ Brak pliku: {litellm_path}", file=sys.stderr)
        sys.exit(1)

    with open(litellm_path) as f:
        litellm_raw = json.load(f)

    litellm_models = parse_litellm(litellm_raw)
    print(f"  LiteLLM:     {len(litellm_models)} modeli")

    def load_optional(path_str, parser_fn, label):
        if not path_str:
            return []
        p = Path(path_str)
        if not p.exists():
            print(f"  {label}: brak ({p} nie istnieje, pomijam)")
            return []
        with open(p) as f:
            raw = json.load(f)
        result = parser_fn(raw)
        print(f"  {label}: {len(result)} modeli")
        return result

    or_models       = load_optional(args.openrouter,  parse_openrouter,  "OpenRouter ")
    fal_models      = load_optional(args.fal,          parse_fal,         "fal.ai     ")
    hf_models       = load_optional(args.huggingface,  parse_huggingface, "HuggingFace")
    aimlapi_models  = load_optional(args.aimlapi,      parse_aimlapi,     "AIMLAPI    ")
    piapi_models    = load_optional(args.piapi,         lambda d: parse_curated(d, "piapi",     "https://piapi.ai/?ref=tsa"), "piapi.ai   ")
    wavespeed_models= load_optional(args.wavespeed,     lambda d: parse_curated(d, "wavespeed", None),                       "WaveSpeed  ")
    kie_models      = load_optional(args.kie,           lambda d: parse_curated(d, "kie",       "https://kie.ai/?ref=tsa"),  "kie.ai     ")
    runway_models   = load_optional(args.runway,        lambda d: parse_curated(d, "runway",    None),                       "Runway     ")
    minimax_models  = load_optional(args.minimax,       lambda d: parse_curated(d, "minimax",   None),                       "MiniMax    ")
    bedrock_models  = load_optional(args.bedrock,       lambda d: parse_curated(d, "bedrock",   None),                       "Bedrock    ")
    replicate_models= load_optional(args.replicate,     parse_replicate,                                                       "Replicate  ")
    fireworks_models= load_optional(args.fireworks,     lambda d: parse_fireworks(d, litellm_raw),                             "Fireworks  ")
    opencode_models = load_optional(args.opencode,      lambda d: parse_curated(d, "opencode",  None),                        "OpenCode   ")

    # Load manual
    manual_path = Path(args.manual)
    if manual_path.exists():
        with open(manual_path) as f:
            manual_data = json.load(f)
        manual_models = manual_data.get("models", [])
        print(f"  Manual:      {len(manual_models)} modeli")
    else:
        print(f"  Manual:      brak ({manual_path} nie istnieje, pomijam)")
        manual_models = []

    merged = merge(litellm_models, or_models, fal_models, hf_models, manual_models,
                   aimlapi_models, piapi_models, wavespeed_models, kie_models, runway_models,
                   minimax_models, bedrock_models, replicate_models,
                   fireworks_models, opencode_models)

    # Apply provider patches (data/provider-patches.json)
    patches_path = Path(args.output).parent / "provider-patches.json"
    if patches_path.exists():
        with open(patches_path) as f:
            patches_data = json.load(f)
        by_id = {m["id"]: m for m in merged}
        applied = 0
        for patch in patches_data.get("patches", []):
            model_id = patch.get("model_id")
            provider_id = patch.get("provider_id")
            if not model_id or not provider_id:
                continue
            target = by_id.get(model_id)
            if target is None:
                print(f"  ⚠ provider-patch: model '{model_id}' nie znaleziony, pomijam")
                continue
            existing_pids = {p["provider_id"] for p in target.get("providers", [])}
            if provider_id not in existing_pids:
                provider_entry = {k: v for k, v in patch.items() if k != "model_id"}
                target.setdefault("providers", []).append(provider_entry)
                applied += 1
        if applied:
            print(f"  Patche:      {applied} providerów dorzuconych")

    merged.sort(key=lambda m: m.get("name", "").lower())
    print(f"  Razem:       {len(merged)} modeli po merge")

    today = str(date.today())

    # Zlicz modele per źródło (po merge)
    source_counts: dict[str, int] = {}
    for m in merged:
        src = m.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1

    # Diff względem poprzedniej wersji katalogu + zachowanie first_seen_at
    update_stats: dict = {"added": 0, "removed": 0, "updated": 0, "unchanged": 0}
    prev_first_seen: dict[str, str] = {}
    out_path = Path(args.output)
    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            prev_map = {m["id"]: m for m in prev.get("models", [])}
            # Zachowaj first_seen_at (backfill z updated_at dla rekordów legacy)
            for pid, pm in prev_map.items():
                prev_first_seen[pid] = pm.get("first_seen_at") or pm.get("updated_at") or today
            new_map  = {m["id"]: m for m in merged}
            for mid, m in new_map.items():
                if mid not in prev_map:
                    update_stats["added"] += 1
                else:
                    # Porównaj providers (ceny mogły się zmienić)
                    if json.dumps(m.get("providers"), sort_keys=True) != json.dumps(prev_map[mid].get("providers"), sort_keys=True):
                        update_stats["updated"] += 1
                    else:
                        update_stats["unchanged"] += 1
            update_stats["removed"] = sum(1 for mid in prev_map if mid not in new_map)
            print(f"  Diff:        +{update_stats['added']} nowych, ~{update_stats['updated']} zmienionych, -{update_stats['removed']} usuniętych")
        except Exception:
            pass

    # Przypisz first_seen_at do każdego mergedowanego modelu
    # — zachowaj z prev jeśli istniał, dla nowych ustaw today
    for m in merged:
        m["first_seen_at"] = prev_first_seen.get(m["id"], today)

    output = {
        "updated_at": today,
        "source_counts": source_counts,
        "update_stats": update_stats,
        "models": merged
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Zapisano: {args.output}")

    # ── Opcja 1: individual model files + search index ──────────────
    output_dir = Path(args.output).parent
    models_dir = output_dir / "models"
    models_dir.mkdir(exist_ok=True)

    for model in merged:
        model_path = models_dir / f"{model['id']}.json"
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2)

    print(f"✓ Individual files: {len(merged)} plików w {models_dir}/")

    # Lekki indeks do discovery: tylko pola potrzebne do wyszukania modelu
    index = []
    for m in merged:
        best_price = None
        has_free_api = False
        for p in m.get("providers", []):
            if not p.get("available"):
                continue
            if p.get("free_api"):
                has_free_api = True
            pricing = p.get("pricing") or {}
            for key in ("input_per_1m", "per_image", "per_second", "per_video",
                        "per_video_5s", "per_video_6s", "per_minute", "per_song", "per_megapixel"):
                if key in pricing:
                    v = pricing[key]
                    if best_price is None or v < best_price:
                        best_price = v
                    break

        index.append({
            "id":              m["id"],
            "name":            m["name"],
            "category":        m.get("category"),
            "capabilities":    m.get("capabilities", []),
            "open_source":     m.get("open_source", False),
            "local_available": m.get("local_available", False),
            "free_api":        has_free_api,
            "providers":       [p["provider_id"] for p in m.get("providers", []) if p.get("available")],
            "best_price":      best_price,
            "tags":            m.get("tags", []),
        })

    index_output = {
        "updated_at": today,
        "count": len(index),
        "models": index,
    }
    index_path = output_dir / "models-index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_output, f, ensure_ascii=False, indent=2)

    index_kb = index_path.stat().st_size // 1024
    print(f"✓ Search index:     {index_path} ({index_kb} KB)")


if __name__ == "__main__":
    main()
