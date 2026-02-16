# Repatrol

Repatrol is a TypeScript + Playwright multi-agent QA swarm that plays an intentionally buggy web game, detects deterministic failures, captures evidence, and drafts GitHub issues.

Built for: Microsoft AI Dev Days Hackathon 2026
Categories: Agentic DevOps, Best Multi-Agent System
Demo video: <paste hosted link>

## Quickstart

```bash
npm install
npx playwright install chromium
npm run demo
```

This runs:

```bash
tsx scripts/run-demo.ts --serve --mode demo --headless --dry-run-github
```

## What It Does

Agents and roles:

- Explorer: navigates systematically to maximize coverage
- Chaos: tries adversarial/edge-case inputs to trigger crashes/hangs
- Reporter: writes a GitHub issue body with repro steps and evidence

## Artifacts

Expected output paths:

- `artifacts/bugs/bug-*.json`
- `artifacts/runs/<run_id>/summary.json`
- `artifacts/runs/<run_id>/issue_body.md`
- `artifacts/videos/<run_id>/*.webm`

## Verification

```bash
npm run check
npm run build
npm run smoke
```

## Commands

```bash
# Full demo run
npm run demo

# Serve demo game manually
npm run serve

# Optional Foundry smoke (requires env vars)
npm run foundry:smoke
```

## GitHub Integration

Repatrol defaults to dry-run issue generation.

To enable real issue creation, set:

- `GITHUB_TOKEN`
- `GITHUB_REPO` (e.g. `owner/repo`)

## Demo Video

The submission video should be human-recorded.

- Script: `demo/demo_script.md`
- Checklist: `demo/demo_checklist.md`

## License

Apache-2.0 (see `LICENSE`).
