# ReplayRig Demo Checklist

## Pre-demo checks

- [ ] Python virtualenv active and dependencies installed
- [ ] Playwright Chromium installed (`python3 -m playwright install chromium`)
- [ ] `ffmpeg` available on PATH (`ffmpeg -version`)
- [ ] Port `4173` is free if using `--serve`
- [ ] Optional GitHub env vars set for live issue creation:
  - [ ] `GITHUB_TOKEN`
  - [ ] `GITHUB_REPO`

## Recording flow

- [ ] Start demo run:

```bash
python3 scripts/run_demo.py --serve --mode demo --headless --dry-run-github
```

- [ ] Confirm output contains:
  - [ ] `bug_path=...`
  - [ ] `issue_url=...`
  - [ ] `coverage_percent` inside JSON summary
- [ ] Verify artifacts exist:
  - [ ] `artifacts/bugs/*.json`
  - [ ] `artifacts/runs/<run_id>/summary.json`
  - [ ] `artifacts/runs/<run_id>/issue_body.md`
- [ ] Generate submission video:

```bash
python3 scripts/record_demo_video.py --headless --out demo/video.mp4
```

- [ ] Verify `demo/video.mp4` exists and is non-empty

## Fallback plan (no GitHub token)

- [ ] Keep `--dry-run-github` enabled in demo commands
- [ ] Show rendered markdown issue body in `artifacts/runs/<run_id>/issue_body.md`
- [ ] Explain that live issue creation activates automatically when `GITHUB_TOKEN` + `GITHUB_REPO` are set
