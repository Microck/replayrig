from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.core.run_context import RunContext
from src.vision.game_state import GameState


def capture_bug_evidence(
    ctx: RunContext,
    page: Any,
    state: GameState,
    label: str,
) -> dict[str, str | None]:
    safe_label = "".join(
        ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label
    )
    run_dir = ctx.run_dir()

    recorder = ctx.metadata.get("recorder")
    screenshot_path: Path
    if recorder is not None and page is not None:
        screenshot_path = recorder.capture_screenshot(page, ctx.run_id, safe_label)
    else:
        screenshot_path = run_dir / f"{safe_label}.png"
        if page is not None:
            page.screenshot(path=str(screenshot_path), full_page=True)

    state_path = run_dir / f"{safe_label}-state.json"
    state_path.write_text(
        json.dumps(state.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )

    video_path = ctx.metadata.get("video_path")
    return {
        "screenshot_path": str(screenshot_path),
        "state_path": str(state_path),
        "video_path": str(video_path) if video_path else None,
    }
