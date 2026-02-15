from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RunContext:
    run_id: str
    artifacts_root: Path = Path("artifacts")
    metadata: dict[str, Any] = field(default_factory=dict)

    def run_dir(self) -> Path:
        path = self.artifacts_root / "runs" / self.run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def screenshots_dir(self) -> Path:
        path = self.artifacts_root / "screenshots" / self.run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def videos_dir(self) -> Path:
        path = self.artifacts_root / "videos" / self.run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def bugs_dir(self) -> Path:
        path = self.artifacts_root / "bugs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def coverage_path(self) -> Path:
        path = self.artifacts_root / "coverage"
        path.mkdir(parents=True, exist_ok=True)
        return path / f"{self.run_id}.json"
