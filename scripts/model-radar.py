#!/usr/bin/env python3
"""
model-radar.py
Porównuje aktualny models.json z poprzednim snapshotem.
Wykrywa nowe modele, nowych dostawców, zmiany cen.
Generuje raport i opcjonalnie wysyła webhook.

Użycie:
  python3 scripts/model-radar.py
  python3 scripts/model-radar.py --webhook https://n8n.example.com/webhook/model-radar
  python3 scripts/model-radar.py --output report.json
"""

import json, sys, os, argparse, urllib.request
from pathlib import Path
from datetime import date

CATALOG_PATH  = Path("data/models.json")
SNAPSHOT_PATH = Path("data/models-snapshot.json")
CATEGORIES = {
    "llm": "LLM",
    "image_generation": "Image",
    "video_generation": "Video",
    "audio_tts": "TTS",
    "audio_stt": "STT",
    "music_generation": "Music",
    "embedding": "Embedding",
    "moderation": "Moderation",
}


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def index_by_id(models: list) -> dict:
    return {m["id"]: m for m in models}


def get_min_price(model: dict) -> float | None:
    best = None
    for p in model.get("providers", []):
        pr = p.get("pricing", {})
        for key in ("input_per_1m", "per_image", "per_second", "per_video_5s", "per_song"):
            val = pr.get(key)
            if val and isinstance(val, (int, float)) and val > 0:
                if best is None or val < best:
                    best = val
    return best


def detect_changes(old_models: list, new_models: list) -> dict:
    old_idx = index_by_id(old_models)
    new_idx = index_by_id(new_models)

    new_model_ids   = set(new_idx) - set(old_idx)
    removed_ids     = set(old_idx) - set(new_idx)
    updated_ids     = set(new_idx) & set(old_idx)

    new_models_list = []
    for mid in sorted(new_model_ids):
        m = new_idx[mid]
        new_models_list.append({
            "id":       mid,
            "name":     m.get("name", mid),
            "category": m.get("category", ""),
            "providers": [p["provider_id"] for p in m.get("providers", [])],
        })

    new_providers = []
    for mid in sorted(updated_ids):
        old_pids = {p["provider_id"] for p in old_idx[mid].get("providers", [])}
        new_pids = {p["provider_id"] for p in new_idx[mid].get("providers", [])}
        added = new_pids - old_pids
        if added:
            new_providers.append({
                "model_id":   mid,
                "model_name": new_idx[mid].get("name", mid),
                "new_providers": sorted(added),
            })

    price_changes = []
    for mid in sorted(updated_ids):
        old_price = get_min_price(old_idx[mid])
        new_price = get_min_price(new_idx[mid])
        if old_price and new_price and abs(old_price - new_price) / old_price > 0.05:
            direction = "↓" if new_price < old_price else "↑"
            price_changes.append({
                "model_id":   mid,
                "model_name": new_idx[mid].get("name", mid),
                "old_price":  round(old_price, 6),
                "new_price":  round(new_price, 6),
                "direction":  direction,
                "change_pct": round((new_price - old_price) / old_price * 100, 1),
            })

    # Category breakdown of new models
    cat_breakdown = {}
    for m in new_models_list:
        cat = CATEGORIES.get(m["category"], m["category"])
        cat_breakdown[cat] = cat_breakdown.get(cat, 0) + 1

    return {
        "date":           str(date.today()),
        "total_new":      len(new_model_ids),
        "total_removed":  len(removed_ids),
        "total_old":      len(old_models),
        "total_new_total":len(new_models),
        "new_models":     new_models_list[:50],  # max 50 in report
        "new_providers":  new_providers[:20],
        "price_changes":  price_changes[:20],
        "removed_ids":    sorted(removed_ids)[:20],
        "category_breakdown": cat_breakdown,
    }


def format_report(changes: dict) -> str:
    lines = [
        f"AI API Catalog — Model Radar ({changes['date']})",
        "=" * 50,
        f"Total models: {changes['total_old']} → {changes['total_new_total']} (+{changes['total_new']})",
        "",
    ]

    if changes["new_models"]:
        lines.append(f"NEW MODELS ({changes['total_new']}):")
        breakdown = changes.get("category_breakdown", {})
        if breakdown:
            lines.append("  Categories: " + ", ".join(f"{k}: {v}" for k, v in sorted(breakdown.items())))
        lines.append("")
        for m in changes["new_models"][:20]:
            cat = CATEGORIES.get(m["category"], m["category"])
            provs = ", ".join(m["providers"][:3]) + (f" +{len(m['providers'])-3}" if len(m["providers"]) > 3 else "")
            lines.append(f"  [{cat}] {m['name']} — {provs}")
        if len(changes["new_models"]) > 20:
            lines.append(f"  ... and {len(changes['new_models'])-20} more")
        lines.append("")

    if changes["new_providers"]:
        lines.append(f"NEW PROVIDERS FOR EXISTING MODELS ({len(changes['new_providers'])}):")
        for p in changes["new_providers"][:10]:
            lines.append(f"  {p['model_name']}: +{', '.join(p['new_providers'])}")
        lines.append("")

    if changes["price_changes"]:
        lines.append(f"PRICE CHANGES ({len(changes['price_changes'])}):")
        for p in changes["price_changes"][:10]:
            lines.append(f"  {p['direction']} {p['model_name']}: ${p['old_price']} → ${p['new_price']} ({p['change_pct']:+.1f}%)")
        lines.append("")

    if changes["removed_ids"]:
        lines.append(f"REMOVED ({changes['total_removed']}): {', '.join(changes['removed_ids'][:10])}")

    return "\n".join(lines)


def send_webhook(webhook_url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "ai-api-catalog/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"  Webhook: {resp.status} OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog",  default=str(CATALOG_PATH))
    parser.add_argument("--snapshot", default=str(SNAPSHOT_PATH))
    parser.add_argument("--webhook",  help="n8n/Slack webhook URL")
    parser.add_argument("--output",   help="Zapisz raport JSON do pliku")
    parser.add_argument("--update-snapshot", action="store_true",
                        help="Zaktualizuj snapshot po analizie")
    args = parser.parse_args()

    catalog_path  = Path(args.catalog)
    snapshot_path = Path(args.snapshot)

    if not catalog_path.exists():
        print(f"✗ Brak katalogu: {catalog_path}", file=sys.stderr)
        sys.exit(1)

    catalog  = load_json(catalog_path)
    snapshot = load_json(snapshot_path)

    new_models = catalog.get("models", [])

    if snapshot is None:
        print("⚠ Brak snapshotu — tworzę nowy, następny run wykryje zmiany.")
        old_models = []
    else:
        old_models = snapshot.get("models", [])

    changes = detect_changes(old_models, new_models)
    report  = format_report(changes)

    print(report)

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"report": report, "changes": changes}, f, indent=2)
        print(f"\n✓ Raport zapisany: {args.output}")

    if args.webhook and (changes["total_new"] > 0 or changes["price_changes"]):
        print(f"\n→ Wysyłam webhook ({changes['total_new']} nowych modeli)...")
        payload = {
            "text":    report,
            "changes": changes,
        }
        try:
            send_webhook(args.webhook, payload)
        except Exception as e:
            print(f"  ✗ Webhook error: {e}", file=sys.stderr)
    elif args.webhook:
        print("\n  Brak zmian — nie wysyłam webhooka.")

    if args.update_snapshot or snapshot is None:
        import shutil
        shutil.copy2(catalog_path, snapshot_path)
        print(f"✓ Snapshot zaktualizowany: {snapshot_path}")

    return changes


if __name__ == "__main__":
    main()
