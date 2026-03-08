#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# update-litellm.sh
# Pobiera aktualne dane cenowe z LiteLLM i aktualizuje katalog.
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
CACHE_FILE="$DATA_DIR/litellm-raw.json"

echo "→ Pobieranie danych z LiteLLM..."
curl -s --fail "$LITELLM_URL" -o "$CACHE_FILE"
echo "✓ Pobrano: $CACHE_FILE"

echo "→ Uruchamiam merge-data.py..."
python3 "$SCRIPT_DIR/merge-data.py" \
    --litellm "$CACHE_FILE" \
    --manual "$DATA_DIR/models-manual.json" \
    --output "$DATA_DIR/models.json"

echo "→ Walidacja schematu..."
python3 "$SCRIPT_DIR/validate-schema.py" "$DATA_DIR/models.json"

echo "✓ Gotowe! Katalog zaktualizowany."
echo "  Commit zmian: git add data/models.json && git commit -m 'chore: update model pricing'"
