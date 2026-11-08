import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.main import app

SNAPSHOT = ROOT / "contracts" / "openapi.json"


def canonical_schema():
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Compare the generated OpenAPI schema with the committed snapshot.")
    parser.add_argument("--update", action="store_true", help="Replace the committed snapshot with the current schema.")
    args = parser.parse_args()
    current = canonical_schema()

    if args.update:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(current, encoding="utf-8")
        print(f"Updated {SNAPSHOT.relative_to(ROOT)}")
        return 0

    if not SNAPSHOT.exists():
        print(f"Missing contract snapshot: {SNAPSHOT}", file=sys.stderr)
        print("Run: python scripts/openapi_contract.py --update", file=sys.stderr)
        return 2

    if current != SNAPSHOT.read_text(encoding="utf-8"):
        print("OpenAPI contract drift detected. Review the API change and update contracts/openapi.json intentionally.", file=sys.stderr)
        return 1

    print(f"OpenAPI contract matches {SNAPSHOT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
