<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/brand/logo-horizontal-dark.svg">
  <img alt="Repatrol" src="docs/brand/logo-horizontal.svg" width="640">
</picture>

# Repatrol

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Repatrol is a TypeScript + Playwright QA runner with a swarm-style workflow.

It plays a deterministic target web game, detects failures, captures evidence (screenshots + video), and drafts GitHub issues with reproduction steps.

## Quickstart

Prereqs:
- Node.js 20+

```bash
npm install
npx playwright install chromium
npm run demo
```

TODO: add what success looks like (which artifacts to inspect).

## Installation

```bash
npm install
npx playwright install chromium
```

## Usage

Run the full demo flow (serves target game + records video):

```bash
npm run demo
```

Serve only the target game:

```bash
npm run serve
```

Typecheck and build:

```bash
npm run check
npm run build
```

Run a fast smoke pass:

```bash
npm run smoke
```

Run the demo script directly (for flags):

```bash
npx tsx scripts/run-demo.ts --serve --mode demo --headless --dry-run-github
```

## Configuration

Environment variables:
- `.env.example`

Target game URL:

```bash
TARGET_GAME_URL="https://example.com/" npm run demo
```

GitHub integration (optional):
- Defaults to dry-run issue generation
- Set to enable real issue creation:
  - `GITHUB_TOKEN`
  - `GITHUB_REPO` (e.g. `owner/repo`)

Foundry smoke test (optional):

```bash
npm run foundry:smoke
```

It is skipped unless all are set:
- `FOUNDRY_ENDPOINT`
- `FOUNDRY_DEPLOYMENT`
- `FOUNDRY_API_VERSION`
- `FOUNDRY_API_KEY`

## Artifacts

Expected output paths:
- `artifacts/bugs/bug-*.json`
- `artifacts/coverage/<run_id>.json`
- `artifacts/runs/<run_id>/summary.json`
- `artifacts/runs/<run_id>/issue_body.md`
- `artifacts/screenshots/<run_id>/*.png`
- `artifacts/videos/<run_id>/*.webm`

TODO: add a short note about how to interpret `summary.json` / `bug-*.json`.

## How it works

TODO: add a short flow: serve -> explore -> crash -> artifacts -> issue draft.

## Development

TODO: add local dev notes (debugging Playwright, Node version manager).

## Testing

TODO: define what `npm run smoke` asserts.

## Contributing

Issues and pull requests are welcome.

## Support

TODO: add Issues/Discussions link.

## Security

TODO: add security policy (or add `SECURITY.md` and link it).

## License

Apache-2.0 (see `LICENSE`).

## Releases / Changelog

TODO: link to GitHub Releases or add `CHANGELOG.md`.

## Roadmap

TODO: add 3-5 near-term improvements (or link to issues/milestones).
