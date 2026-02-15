# Buggy Web Game (Deterministic Target)

This tiny static game is intentionally designed for browser automation.

Visible states used by screenshots: `TITLE`, `PLAY`, and `CRASH`.

## Serve locally

```bash
python3 scripts/serve_buggy_web_game.py --port 4173
```

Open: `http://127.0.0.1:4173/`

## Deterministic crash path

Crash sequence (uncaught exception, Playwright should emit `pageerror`):

1. Click `START`
2. Click `BOOST` exactly 7 times
3. Click `FIRE`

Expected: the page throws an uncaught error containing `DEMO_CRASH:`.

There is also an immediate `CRASH NOW` button.
