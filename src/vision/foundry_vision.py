from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.llm.client import LLMClient
from src.vision.game_state import GameState
from src.vision.prompts import GAME_STATE_PROMPT, GAME_STATE_SCHEMA


def _safe_state_from_dict(payload: dict[str, Any]) -> GameState:
    warnings: list[str] = []
    required = GAME_STATE_SCHEMA["required"]
    for key in required:
        if key not in payload:
            warnings.append(f"missing key: {key}")

    try:
        state = GameState.from_dict(payload)
    except Exception as exc:
        return GameState(
            screen_id="parse-error",
            summary="Failed to parse model response",
            action_hints=[],
            ui_elements=[],
            is_loading=False,
            warnings=[f"parse error: {exc}"],
        )

    if warnings:
        state.warnings.extend(warnings)
    return state


def state_from_payload(payload: dict[str, Any]) -> GameState:
    return _safe_state_from_dict(payload)


def state_from_screenshot(llm: LLMClient, image_path: str) -> GameState:
    path = Path(image_path)
    image_bytes = path.read_bytes()
    try:
        payload = llm.vision_json(
            prompt=GAME_STATE_PROMPT,
            image_bytes=image_bytes,
            schema=GAME_STATE_SCHEMA,
        )
    except Exception as exc:
        return GameState(
            screen_id="vision-error",
            summary="Vision extraction failed",
            action_hints=[],
            ui_elements=[],
            is_loading=False,
            warnings=[f"vision error: {exc}"],
        )

    return _safe_state_from_dict(payload)


def state_to_json(state: GameState) -> str:
    return json.dumps(state.to_dict(), indent=2, sort_keys=True)
