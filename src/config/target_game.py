from __future__ import annotations

import os


# Default to the in-repo demo game server.
TARGET_GAME_URL = os.getenv("TARGET_GAME_URL", "http://127.0.0.1:4173")

DEFAULT_VIEWPORT = {
    "width": int(os.getenv("GAME_VIEWPORT_WIDTH", "1280")),
    "height": int(os.getenv("GAME_VIEWPORT_HEIGHT", "720")),
}

# Optional selectors so we don't hardcode them in agents later.
GAME_ROOT_SELECTOR = os.getenv("GAME_ROOT_SELECTOR", "#game-root")
GAME_STATE_LABEL_SELECTOR = os.getenv("GAME_STATE_LABEL_SELECTOR", "#stateLabel")
PRIMARY_ACTION_SELECTOR = os.getenv("PRIMARY_ACTION_SELECTOR", "#startBtn")
