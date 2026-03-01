# Repatrol - Test & Smoke Checklist

Goal: run the exact checks needed before recording the submission video and submitting.

## 0) Repo sanity

```bash
cd projects/repatrol
git status --porcelain
```

Expected: no output.

## 1) Install deps + browser

```bash
cd projects/repatrol
npm ci
npx playwright install chromium
```

## 2) Automated checks

```bash
cd projects/repatrol
npm run check
npm run build
```

## 3) Smoke run

```bash
cd projects/repatrol
npm run smoke
```

## 4) Full demo run (judge-safe)

```bash
cd projects/repatrol
npm run demo
```

Expected:
- console output includes a `bug_path=...`
- run directory exists under `artifacts/runs/<run_id>/`
- issue draft exists at `artifacts/runs/<run_id>/issue_body.md`

## 5) Artifact verification

```bash
cd projects/repatrol
ls -1 artifacts/bugs | head -n 5
ls -1 artifacts/runs | head -n 5
```

## 6) Optional integrations

- Foundry smoke (skips unless all `FOUNDRY_*` env vars are set):
  - `npm run foundry:smoke`
- GitHub live issue creation (optional): set `GITHUB_TOKEN` + `GITHUB_REPO` and run the demo script without `--dry-run-github`.

## 7) Submission artifacts

- README: `README.md`
- Architecture diagram: `docs/architecture.svg` (source: `docs/architecture.mmd`)
- Demo checklist: `demo/demo_checklist.md`
- Demo script: `demo/demo_script.md`
- Optional local video artifact: `demo/video.mp4`
