from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.bug import BugEvidence, BugReport


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/bug_smoke.json")
    args = parser.parse_args()

    report = BugReport(
        run_id="smoke-run",
        detector="crash",
        reason="DEMO_CRASH: smoke scenario",
        last_state={"screen_id": "CRASH", "summary": "Forced smoke crash"},
        repro_steps=["Open page", "Click START", "Click CRASH NOW"],
        evidence=BugEvidence(
            screenshot_path="artifacts/screenshots/smoke.png",
            state_path="artifacts/runs/smoke/state.json",
            video_path="artifacts/videos/smoke.mp4",
        ),
    )

    output = report.to_json(args.out)
    round_tripped = BugReport.from_json(output)
    print(f"Wrote bug report: {output}")
    print(json.dumps(round_tripped.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
