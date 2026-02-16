# Repatrol

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Repatrol is a TypeScript + Playwright multi-agent QA swarm.

It plays a deterministic target web game, detects failures, captures evidence (screenshots + video), and drafts GitHub issues with reproduction steps.

## Features

- Playwright-driven game automation
- Deterministic crash path for repeatable bug detection
- Evidence artifacts: JSON, markdown issue body, videos
- Optional GitHub issue creation (dry-run by default)

## Installation

Prereqs:
- Node.js 20+

```bash
npm install
npx playwright install chromium
```

## Quick Start

Run the full demo flow (serves the target game + records video):

```bash
npm run demo
```

## Usage

Typecheck and build:

```bash
npm run check
npm run build
```

Run a fast smoke pass:

```bash
npm run smoke
```

## Artifacts

Expected output paths:

- `artifacts/bugs/bug-*.json`
- `artifacts/runs/<run_id>/summary.json`
- `artifacts/runs/<run_id>/issue_body.md`
- `artifacts/videos/<run_id>/*.webm`

## GitHub Integration

Repatrol defaults to dry-run issue generation.

To enable real issue creation, set:

- `GITHUB_TOKEN`
- `GITHUB_REPO` (e.g. `owner/repo`)

## Demo

- Video: TBD
- Script and checklist:
  - `demo/demo_script.md`
  - `demo/demo_checklist.md`

## Contributing

Issues and pull requests are welcome.

## License

Apache-2.0 (see `LICENSE`).
