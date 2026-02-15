from __future__ import annotations

from dataclasses import dataclass

from src.vision.game_state import GameState


@dataclass
class HangDetector:
    max_same_screen_steps: int = 8
    max_loading_seconds: float = 6.0

    _last_screen_id: str | None = None
    _same_screen_steps: int = 0
    _last_change_ts: float = 0.0
    _loading_since_ts: float | None = None

    def observe(self, state: GameState, now: float) -> None:
        screen_id = state.screen_id

        if self._last_screen_id == screen_id:
            self._same_screen_steps += 1
        else:
            self._same_screen_steps = 0
            self._last_change_ts = now
            self._last_screen_id = screen_id

        if state.is_loading:
            if self._loading_since_ts is None:
                self._loading_since_ts = now
        else:
            self._loading_since_ts = None

    def check(self, now: float) -> str | None:
        if (
            self._same_screen_steps >= self.max_same_screen_steps
            and self._last_screen_id
        ):
            return (
                f"hang: screen {self._last_screen_id!r} repeated "
                f"{self._same_screen_steps + 1} steps"
            )

        if self._loading_since_ts is not None:
            loading_duration = now - self._loading_since_ts
            if loading_duration > self.max_loading_seconds:
                return f"hang: loading timeout {loading_duration:.1f}s"

        return None
