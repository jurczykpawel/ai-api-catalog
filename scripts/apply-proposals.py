#!/usr/bin/env python3
"""
apply-proposals.py
Dodaje zweryfikowane propozycje modeli do data/models-manual.json.
Sprawdza duplikaty przed dodaniem.

Użycie:
  python3 scripts/apply-proposals.py                          # wczytuje /tmp/verified-proposals.json
  python3 scripts/apply-proposals.py --input proposals.json  # własny plik
  python3 scripts/apply-proposals.py --dry-run               # pokaż co zostanie dodane, nie zapisuj
"""

import json
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   default="/tmp/verified-proposals.json",
                        help="Zweryfikowane propozycje z verify-models.py")
    parser.add_argument("--manual",  default="data/models-manual.json",
                        help="Plik docelowy (default: data/models-manual.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Pokaż co zostanie dodane bez zapisywania")
    args = parser.parse_args()

    input_path = Path(args.input)
    manual_path = Path(args.manual)

    if not input_path.exists():
        print(f"✗ Brak pliku: {input_path}", file=sys.stderr)
        print("  Uruchom najpierw: python3 scripts/verify-models.py", file=sys.stderr)
        sys.exit(1)

    if not manual_path.exists():
        print(f"✗ Brak pliku: {manual_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        proposals = json.load(f)

    with open(manual_path) as f:
        manual = json.load(f)

    existing_ids = {m["id"] for m in manual.get("models", [])}
    existing_names = {m["name"].lower() for m in manual.get("models", [])}

    to_add = []
    skipped = []

    for p in proposals:
        pid = p.get("id", "")
        pname = p.get("name", "").lower()
        if pid in existing_ids or pname in existing_names:
            skipped.append(p["name"])
        else:
            to_add.append(p)

    if skipped:
        print(f"⏭  Pominięto (już w katalogu): {', '.join(skipped)}")

    if not to_add:
        print("✓ Brak nowych modeli do dodania.")
        return

    print(f"\n{'+'*50}")
    print(f"  Zostaną dodane ({len(to_add)}):")
    for p in to_add:
        print(f"  + {p['name']} [{p['category']}] via {p['providers'][0]['provider_id']}")
    print(f"{'+'*50}\n")

    if args.dry_run:
        print("DRY RUN — nic nie zapisano.")
        return

    manual["models"].extend(to_add)

    with open(manual_path, "w") as f:
        json.dump(manual, f, ensure_ascii=False, indent=2)

    print(f"✓ Dodano {len(to_add)} modeli do {manual_path}")
    print(f"  Łącznie w katalogu: {len(manual['models'])} modeli (manual)")
    print(f"\n  Następny krok: bash scripts/update-litellm.sh")


if __name__ == "__main__":
    main()
