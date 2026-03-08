# AI API Katalog

Kompletny katalog modeli AI dostępnych przez API. Filtrowanie po kategorii, dostawcy, cenie, możliwościach.

**Hosting:** `modele.techskills.academy` (mikrus, nginx static)
**Brand:** TechSkills Academy
**Aktualizacja:** co tydzień (agent/cron)

---

## Struktura

```
ai-api-catalog/
├── index.html              # Strona katalogu (single-file, fetch z data/)
├── data/
│   ├── models.json         # Wszystkie modele (GENEROWANY przez merge-data.py)
│   ├── models-manual.json  # Ręczne wpisy: video, image, audio gen (edytuj tutaj)
│   ├── providers.json      # Metadane dostawców (logo_color, URL, affiliate)
│   ├── categories.json     # Definicje kategorii z ikonami
│   └── litellm-raw.json    # Cache danych LiteLLM (gitignore opcjonalnie)
└── scripts/
    ├── update-litellm.sh   # Główny skrypt update (uruchamiaj co tydzień)
    ├── merge-data.py       # Scala LiteLLM + manual → models.json
    └── validate-schema.py  # Walidacja przed commitem
```

---

## Jak uruchomić lokalnie

```bash
# Potrzebny serwer HTTP (nie otwieraj jako file://)
python3 -m http.server 8080
# lub
npx serve .

# Otwórz: http://localhost:8080
```

---

## Tygodniowa aktualizacja (dla agentów)

```bash
cd /Users/pavvel/workspace/projects/ai-api-catalog
bash scripts/update-litellm.sh
git add data/models.json data/litellm-raw.json
git commit -m "chore: update model pricing $(date +%Y-%m-%d)"
```

Skrypt:
1. Pobiera aktualne ceny z LiteLLM GitHub
2. Scala z ręcznymi wpisami z `data/models-manual.json`
3. Waliduje schemat
4. Zapisuje `data/models.json`

---

## Jak dodać nowy model ręcznie

Edytuj `data/models-manual.json`. Schemat:

```json
{
  "models": [
    {
      "id": "unique-slug",
      "name": "Nazwa Modelu",
      "category": "video_generation",
      "description": "Krótki opis po polsku (1-2 zdania).",
      "tags": ["text-to-video", "high-quality"],
      "capabilities": ["text_to_video", "image_to_video"],
      "context_k": null,
      "updated_at": "2026-03-08",
      "source": "manual",
      "providers": [
        {
          "provider_id": "piapi",
          "pricing": {
            "per_second": 0.15,
            "notes": "Opcjonalna uwaga"
          },
          "url": "https://piapi.ai/model-name",
          "affiliate_url": "https://piapi.ai?ref=tsa",
          "available": true,
          "notes": "Opcjonalna uwaga do wiersza"
        }
      ]
    }
  ]
}
```

### Dostępne kategorie

| id | Nazwa |
|----|-------|
| `llm` | LLM / Chat |
| `image_generation` | Generowanie obrazów |
| `video_generation` | Generowanie wideo |
| `audio_tts` | Text-to-Speech |
| `audio_stt` | Speech-to-Text |
| `music_generation` | Generowanie muzyki |
| `embedding` | Embeddingi |
| `moderation` | Moderacja |

### Dostępne capabilities

`vision`, `reasoning`, `function_calling`, `web_search`, `prompt_caching`, `audio_input`, `streaming`, `multilingual`, `voice_cloning`, `text_in_image`, `image_editing`, `image_to_video`, `text_to_video`, `camera_control`, `audio_generation`, `translation`

### Typy pricing

| Pole | Zastosowanie |
|------|--------------|
| `input_per_1m` + `output_per_1m` | LLM (per 1M tokenów) |
| `per_image` | Generowanie obrazów |
| `per_megapixel` | Obraz (per megapixel) |
| `per_second` | Wideo (per sekunda outputu) |
| `per_video` | Wideo (per klip) |
| `per_1m_chars` | TTS (per 1M znaków) |
| `per_minute` | STT (per minutę audio) |
| `notes` | Gdy cena jest skomplikowana/wymaga sprawdzenia |

---

## Jak dodać nowego dostawcę

Edytuj `data/providers.json`. Dodaj wpis:

```json
{
  "id": "unique-id",
  "name": "Nazwa Dostawcy",
  "description": "Krótki opis (1-2 zdania po polsku).",
  "url": "https://example.com",
  "affiliate_url": "https://example.com?ref=tsa",
  "logo_color": "#hex-kolor",
  "categories": ["llm", "image_generation"],
  "type": "aggregator",
  "hq": "USA"
}
```

`type`: `"direct"` (własne modele) lub `"aggregator"` (hosting cudzych modeli).

Po dodaniu dostawcy możesz odwoływać się do niego przez `provider_id` w modelach.

---

## Affiliate linki

Pole `affiliate_url` w providerze modelu (nie w providers.json — tam URL bazowy).
Jeśli ustawione, link w katalogu będzie oznaczony gwiazdką i żółtym kolorem.

Aktualne programy partnerskie:
- **OpenRouter**: `https://openrouter.ai/?ref=tsa`
- **Replicate**: `https://replicate.com?utm_source=tsa`
- **fal.ai**: `https://fal.ai?ref=tsa`
- **ElevenLabs**: `https://elevenlabs.io?ref=tsa`
- **piapi.ai**: `https://piapi.ai?ref=tsa`
- **kie.ai**: `https://kie.ai?ref=tsa`
- **aimlapi.com**: `https://aimlapi.com?via=tsa`

---

## Deploy na mikrus

```bash
# Jednorazowa konfiguracja nginx
# W /etc/nginx/sites-available/modele.techskills.academy:
# root /home/user/sites/ai-api-catalog;

# Deploy
rsync -avz --exclude '.git' --exclude 'node_modules' \
  /Users/pavvel/workspace/projects/ai-api-catalog/ \
  mikrus:~/sites/ai-api-catalog/
```

---

## Walidacja przed commitem

```bash
python3 scripts/validate-schema.py data/models.json
python3 scripts/validate-schema.py data/models-manual.json
```
