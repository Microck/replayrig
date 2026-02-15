from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.storage.evidence import LocalEvidenceStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["local"], default="local")
    args = parser.parse_args()

    sample_path = Path("artifacts/evidence/local-smoke.txt")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path.write_text("local evidence smoke", encoding="utf-8")

    store = LocalEvidenceStore()
    ref = store.publish(sample_path, kind="log")

    print(json.dumps(ref.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
