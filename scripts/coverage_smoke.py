from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.coverage import CoverageTracker
from src.storage.coverage_store import load_coverage, save_coverage
from src.vision.game_state import GameState


def _sample_states() -> list[GameState]:
    return [
        GameState(
            screen_id="TITLE",
            summary="Title screen",
            action_hints=["click START"],
            ui_elements=[],
            is_loading=False,
            warnings=[],
        ),
        GameState(
            screen_id="PLAY",
            summary="Gameplay screen",
            action_hints=["click BOOST", "click FIRE"],
            ui_elements=[],
            is_loading=False,
            warnings=[],
        ),
        GameState(
            screen_id="PLAY",
            summary="Gameplay screen",
            action_hints=["click BACK"],
            ui_elements=[],
            is_loading=False,
            warnings=[],
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/coverage_smoke.json")
    args = parser.parse_args()

    tracker = CoverageTracker(expected_screens=["TITLE", "PLAY", "CRASH"])
    for state in _sample_states():
        tracker.observe(state)

    output_path = save_coverage(args.out, tracker)
    reloaded = load_coverage(output_path)
    summary = reloaded.summary()
    print(f"Wrote coverage file: {output_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
