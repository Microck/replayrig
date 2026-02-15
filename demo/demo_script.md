# ReplayRig 2-minute Demo Script

## Target Duration

2 minutes total.

## Shot List + Narration

### 0:00-0:20 - Setup and intent

- Show the repo root.
- Narration: "ReplayRig runs a swarm of QA agents against a game, captures a real bug, and drafts a GitHub issue with evidence."

### 0:20-0:50 - Start full demo run

- Run:

```bash
python3 scripts/run_demo.py --serve --mode demo --headless --dry-run-github
```

- Highlight output fields as they appear:
  - `run_id`
  - `coverage.coverage_percent`
  - `bug_path`
  - `issue_url` (dry-run URL when token is not set)

### 0:50-1:20 - Show generated artifacts

- Open bug artifact from `artifacts/bugs/<bug_id>.json`.
- Open run summary from `artifacts/runs/<run_id>/summary.json`.
- Open rendered issue markdown from `artifacts/runs/<run_id>/issue_body.md`.
- Narration: "Explorer mapped the game, Chaos forced failure, Reporter produced reproducible issue details with evidence paths."

### 1:20-1:45 - Show deterministic bug target

- Open `demo/buggy_web_game/README.md` and point at the trigger sequence:
  - `START -> BOOST x7 -> FIRE`
- Narration: "The bug is deterministic so the demo is stable and reproducible."

### 1:45-2:00 - Submission video artifact

- Run:

```bash
python3 scripts/record_demo_video.py --headless --out demo/video.mp4
```

- Show `demo/video.mp4` exists and can be played.
- Closing narration: "ReplayRig turns autonomous gameplay into actionable bug reports with evidence in one command."
