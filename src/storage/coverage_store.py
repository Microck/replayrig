from __future__ import annotations

import json
from pathlib import Path

from src.models.coverage import CoverageTracker


def save_coverage(path: str | Path, tracker: CoverageTracker) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(tracker.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )
    return out_path


def load_coverage(path: str | Path) -> CoverageTracker:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    return CoverageTracker.from_dict(payload)
