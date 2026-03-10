#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# update-litellm.sh
# Pobiera aktualne dane ze wszystkich źródeł i generuje models.json.
# Uruchamiaj raz w tygodniu (np. przez cron lub n8n).
#
# Użycie:
#   cd projects/ai-api-catalog
#   bash scripts/update-litellm.sh
# ─────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$ROOT_DIR/data"
LITELLM_URL="https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AI API Catalog — tygodniowy update"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "[1/9] Pobieranie LiteLLM..."
curl -s --fail "$LITELLM_URL" -o "$DATA_DIR/litellm-raw.json"
echo "✓ litellm-raw.json"

echo ""
echo "[2/9] Pobieranie OpenRouter..."
python3 "$SCRIPT_DIR/fetch-openrouter.py" "$DATA_DIR/openrouter-raw.json"

echo ""
echo "[3/9] Pobieranie fal.ai..."
python3 "$SCRIPT_DIR/fetch-fal.py" "$DATA_DIR/fal-raw.json"

echo ""
echo "[4/9] Pobieranie HuggingFace..."
python3 "$SCRIPT_DIR/fetch-huggingface.py" "$DATA_DIR/huggingface-raw.json"

echo ""
echo "[5/9] Pobieranie AIMLAPI..."
python3 "$SCRIPT_DIR/fetch-aimlapi.py" "$DATA_DIR/aimlapi-raw.json"

echo ""
echo "[6/9] Pobieranie piapi.ai (curated)..."
python3 "$SCRIPT_DIR/fetch-piapi.py" "$DATA_DIR/piapi-raw.json"

echo ""
echo "[7/9] Pobieranie WaveSpeed (curated)..."
python3 "$SCRIPT_DIR/fetch-wavespeed.py" "$DATA_DIR/wavespeed-raw.json"

echo ""
echo "[8/9] Pobieranie kie.ai + Runway ML + Replicate + Fireworks (curated/API)..."
python3 "$SCRIPT_DIR/fetch-kie.py" "$DATA_DIR/kie-raw.json"
python3 "$SCRIPT_DIR/fetch-runway.py" "$DATA_DIR/runway-raw.json"
if [ -n "$REPLICATE_API_TOKEN" ]; then
  python3 "$SCRIPT_DIR/fetch-replicate.py" "$DATA_DIR/replicate-raw.json"
else
  echo "  ⚠ Brak REPLICATE_API_TOKEN — pomijam Replicate"
fi
if [ -n "$FIREWORKS_API_KEY" ]; then
  python3 "$SCRIPT_DIR/fetch-fireworks.py" "$DATA_DIR/fireworks-raw.json"
else
  echo "  ⚠ Brak FIREWORKS_API_KEY — używam istniejącego fireworks-raw.json"
fi

echo ""
echo "[9/9] Merge + walidacja..."
python3 "$SCRIPT_DIR/merge-data.py" \
    --litellm     "$DATA_DIR/litellm-raw.json" \
    --openrouter  "$DATA_DIR/openrouter-raw.json" \
    --fal         "$DATA_DIR/fal-raw.json" \
    --huggingface "$DATA_DIR/huggingface-raw.json" \
    --aimlapi     "$DATA_DIR/aimlapi-raw.json" \
    --piapi       "$DATA_DIR/piapi-raw.json" \
    --wavespeed   "$DATA_DIR/wavespeed-raw.json" \
    --kie         "$DATA_DIR/kie-raw.json" \
    --runway      "$DATA_DIR/runway-raw.json" \
    --replicate   "$DATA_DIR/replicate-raw.json" \
    --fireworks   "$DATA_DIR/fireworks-raw.json" \
    --manual      "$DATA_DIR/models-manual.json" \
    --output      "$DATA_DIR/models.json"

python3 "$SCRIPT_DIR/validate-schema.py" "$DATA_DIR/models.json"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Gotowe! Katalog zaktualizowany."
echo "  Commit: git add data/ && git commit -m 'chore: update catalog $(date +%Y-%m-%d)'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
