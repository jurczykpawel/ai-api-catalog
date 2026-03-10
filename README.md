# AI API Catalog

> Compare prices, providers, and capabilities for 2,000+ AI models available via API — from LLMs to video generation.

**[Live Catalog](https://aiapi.techskills.academy)** · [Report an Issue](https://github.com/jurczykpawel/ai-api-catalog/issues) · [Add a Model](#contributing)

![License](https://img.shields.io/badge/License-MIT-green)
![Models](https://img.shields.io/badge/Models-2000%2B-blue)
![Providers](https://img.shields.io/badge/Providers-25%2B-blue)
![Updated](https://img.shields.io/badge/Updated-weekly-brightgreen)
![Open Source](https://img.shields.io/badge/Open%20Source-100%25-brightgreen)

---

## Why AI API Catalog?

- **One place, all providers** — LiteLLM, OpenRouter, fal.ai, Replicate, Fireworks, Runway, kie.ai, piapi.ai, and 17 more aggregated into a single searchable catalog
- **Real pricing** — per-token, per-second, per-image, per-video with best-price highlighting across providers
- **Beyond LLMs** — video generation, image generation, TTS, STT, music generation, embeddings all in one place
- **Weekly auto-updates** — scripts pull fresh data from provider APIs every Monday
- **Community-maintained** — missing a model or wrong price? Open a PR

---

## What's in the catalog

| Category | Examples | Models |
|---|---|---|
| 💬 LLM / Chat | GPT-4o, Claude 4, Gemini 2.5 Pro, DeepSeek R1 | 800+ |
| 🎨 Image generation | FLUX.1, Stable Diffusion, DALL-E 3, Midjourney | 500+ |
| 🎬 Video generation | Veo 3.1, Kling 2.1, Sora 2, WAN 2.1, Seedance | 200+ |
| 🔊 TTS | ElevenLabs, OpenAI TTS, Kokoro, Cartesia | 100+ |
| 🎤 STT | Whisper, Deepgram, AssemblyAI | 30+ |
| 🎵 Music | Suno, Udio, MusicGen | 20+ |
| 📊 Embeddings | text-embedding-3, Voyage-4, Cohere Embed | 50+ |

**25+ providers** including: OpenAI, Anthropic, Google, Mistral, Groq, DeepSeek, OpenRouter, Together AI, Fireworks AI, Replicate, fal.ai, HuggingFace, Runway, Stability AI, ElevenLabs, Deepgram, piapi.ai, wavespeed.ai, kie.ai, aimlapi.com

---

## Quick Start

No build step. No dependencies. Open directly in browser:

```bash
git clone https://github.com/jurczykpawel/ai-api-catalog.git
cd ai-api-catalog
python3 -m http.server 8080
# Open http://localhost:8080
```

> **Note:** Must be served via HTTP, not opened as `file://` (fetch() calls won't work).

---

## Updating data

Run once a week to pull fresh pricing from all provider APIs:

```bash
bash scripts/update-litellm.sh
```

This runs 9 steps: fetches LiteLLM pricing, OpenRouter (640+ models via frontend API), fal.ai (700+ models), HuggingFace, AIMLAPI, piapi.ai, WaveSpeed, kie.ai, Runway — then merges and validates.

**Optional env vars:**

```bash
export HF_TOKEN=hf_xxx              # Higher HuggingFace rate limits
export REPLICATE_API_TOKEN=r8_xxx   # Enable Replicate fetch (450+ models)
export FIREWORKS_API_KEY=fw_xxx     # Enable Fireworks fetch (250 models)
export RUNWAY_API_KEY=key_xxx       # Enable Runway fetch
export OR_NOTIFY_WEBHOOK=https://...  # Discord/Slack alert if OpenRouter API changes
```

After updating:

```bash
git add data/ && git commit -m "chore: update catalog $(date +%Y-%m-%d)"
```

---

## Project structure

```
ai-api-catalog/
├── index.html                  # Single-file frontend (Tailwind CDN + vanilla JS)
├── data/
│   ├── models.json             # Generated — 2000+ models with pricing (do not edit)
│   ├── models-manual.json      # Hand-curated models: video, image, audio, niche LLMs
│   ├── providers.json          # Provider metadata: name, logo color, type
│   ├── categories.json         # Categories with icons and EN/PL translations
│   ├── provider-patches.json   # Manual provider additions for specific model IDs
│   └── *-raw.json              # Raw API responses (auto-fetched, do not edit)
├── scripts/
│   ├── update-litellm.sh       # Main update script — run this weekly
│   ├── merge-data.py           # Merges all sources into models.json
│   ├── validate-schema.py      # JSON schema validation before deploy
│   ├── model-radar.py          # Detects new models vs last snapshot
│   ├── fetch-openrouter.py     # OpenRouter (640+ models, frontend + v1 fallback)
│   ├── fetch-fal.py            # fal.ai (700+ models)
│   ├── fetch-huggingface.py    # HuggingFace Inference API
│   ├── fetch-aimlapi.py        # AIMLAPI
│   ├── fetch-replicate.py      # Replicate (requires token)
│   ├── fetch-fireworks.py      # Fireworks AI (requires key)
│   ├── fetch-piapi.py          # piapi.ai curated pricing
│   ├── fetch-wavespeed.py      # WaveSpeed AI curated pricing
│   ├── fetch-kie.py            # kie.ai curated pricing
│   └── fetch-runway.py         # Runway ML curated pricing
└── n8n/
    ├── model-radar-workflow.json   # Weekly update + change detection
    └── news-radar-workflow.json    # Daily AI news → extract new models → Discord
```

---

## Data schema

### Model entry (`data/models-manual.json` — source of truth for manual entries)

```json
{
  "id": "veo-3-1",
  "name": "Veo 3.1",
  "category": "video_generation",
  "description": "Google video model with synchronized native audio.",
  "tags": ["text-to-video", "google", "audio-sync"],
  "capabilities": ["text_to_video", "audio_generation"],
  "open_source": false,
  "local_available": false,
  "providers": [
    {
      "provider_id": "google",
      "pricing": { "per_second": 0.40, "notes": "720p/1080p via Gemini API" },
      "url": "https://ai.google.dev/gemini-api/docs/video",
      "affiliate_url": null,
      "available": true
    }
  ],
  "updated_at": "2026-03-10",
  "source": "manual"
}
```

**Categories:** `llm` · `image_generation` · `video_generation` · `audio_tts` · `audio_stt` · `music_generation` · `embedding` · `moderation`

**Capabilities:** `vision` · `reasoning` · `function_calling` · `web_search` · `prompt_caching` · `text_to_video` · `image_to_video` · `image_editing` · `audio_generation` · `json_mode`

**Pricing units:** `input_per_1m` · `output_per_1m` · `per_image` · `per_second` · `per_video` · `per_minute` · `per_song` · `notes`

---

## Contributing

Contributions are welcome — especially pricing corrections and missing models.

### Fix a price or add a provider to an existing model

Edit `data/models-manual.json`. Find the model by `id` and add/update the provider entry. Then validate:

```bash
python3 scripts/validate-schema.py data/models.json
```

### Add a new model (video, image, audio, niche LLM)

1. Add an entry to `data/models-manual.json` following the schema above
2. Run `bash scripts/update-litellm.sh` to regenerate `models.json`
3. Run `python3 scripts/validate-schema.py data/models.json` — must return zero errors
4. Open a PR with a brief description of the model and source for the pricing

### Add a new provider (automated fetch)

1. Add provider metadata to `data/providers.json`
2. Create `scripts/fetch-PROVIDER.py` (use `fetch-piapi.py` as a template for curated providers, or `fetch-fal.py` for API-based fetch)
3. Add a step to `scripts/update-litellm.sh`
4. Add `--provider` argument and parser in `scripts/merge-data.py` (use `parse_curated()`)

### Provider patches (manual additions without a full fetch script)

For models that exist in LiteLLM but are missing a provider entry, use `data/provider-patches.json`:

```json
{
  "patches": [
    {
      "model_id": "some-model",
      "provider": {
        "provider_id": "fireworks",
        "pricing": { "per_second": 0.05 },
        "url": "https://fireworks.ai/models/fireworks/some-model",
        "available": true
      }
    }
  ]
}
```

---

## Tech stack

- **Frontend:** vanilla JavaScript, [Tailwind CSS](https://tailwindcss.com/) (CDN), [Syne](https://fonts.google.com/specimen/Syne) + [DM Sans](https://fonts.google.com/specimen/DM+Sans) + [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono)
- **Data pipeline:** Python 3 scripts (stdlib only — no pip install required)
- **Primary data sources:** [LiteLLM model prices](https://github.com/BerriAI/litellm), [OpenRouter API](https://openrouter.ai/api/frontend/models), [fal.ai API](https://fal.ai)
- **Automation:** [n8n](https://n8n.io) workflows for weekly updates and news radar
- **Hosting:** nginx static file serving

---

## Roadmap

- [x] 2000+ models across 8 categories
- [x] 25+ providers with live pricing
- [x] Weekly automated updates via shell scripts
- [x] OpenRouter frontend API (640 models including image gen)
- [x] Fireworks AI as full data source
- [x] Free API detection (`free_type: open` vs `tier`)
- [x] OSS/local availability auto-detection
- [x] Model Radar — weekly diff and change detection
- [x] AI News Radar — daily RSS → Claude → Discord
- [ ] Price change history (track over time)
- [ ] Affiliate links (OpenRouter, Replicate, fal.ai, ElevenLabs, piapi.ai)
- [ ] Email alerts for price changes
- [ ] B2B catalog API (programmatic access)

---

## Deployment

```bash
rsync -avz --exclude='.git' . mikrus:~/sites/ai-api-catalog/
```

nginx config:
```nginx
server {
    root /home/ubuntu/sites/ai-api-catalog;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```

---

## Acknowledgments

- [LiteLLM](https://github.com/BerriAI/litellm) — the primary source for LLM pricing data
- [OpenRouter](https://openrouter.ai) — 640+ models including multimodal
- [TechSkills Academy](https://techskills.academy) — maintainer

---

## License

MIT — see [LICENSE](LICENSE)
