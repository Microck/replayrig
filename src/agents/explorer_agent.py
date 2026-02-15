from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

from src.automation.browser import BrowserGameDriver
from src.automation.recorder import SessionRecorder
from src.config.target_game import DEFAULT_VIEWPORT, TARGET_GAME_URL
from src.core.run_context import RunContext
from src.llm.foundry_client import FoundryLLMClient
from src.models.coverage import CoverageTracker
from src.storage.coverage_store import save_coverage
from src.vision.foundry_vision import state_from_screenshot
from src.vision.game_state import GameState


SELECTOR_BY_LABEL = {
    "START": "#startBtn",
    "BOOST": "#boostBtn",
    "FIRE": "#fireBtn",
    "BACK": "#backBtn",
    "RESET": "#resetBtn",
    "CRASH": "#crashBtn",
}


class ExplorerAgent:
    def __init__(
        self,
        *,
        url: str = TARGET_GAME_URL,
        llm: FoundryLLMClient | None = None,
        expected_screens: list[str] | None = None,
    ) -> None:
        self.url = url
        self.llm = llm or FoundryLLMClient(mock=True)
        self.expected_screens = expected_screens or ["TITLE", "PLAY", "CRASH"]
        self._rng = random.Random(7)

    def _read_dom_snapshot(self, page: Any) -> tuple[str, list[str]]:
        try:
            state_label = page.locator("#stateLabel").inner_text(timeout=500)
        except Exception:
            state_label = ""
        labels: list[str] = []
        try:
            buttons = page.locator("button").all_inner_texts()
            labels = [label.strip().upper() for label in buttons if label.strip()]
        except Exception:
            labels = []
        return state_label.strip().upper(), labels

    def _selector_from_hint(self, hint: str) -> str | None:
        text = hint.upper()
        for label, selector in SELECTOR_BY_LABEL.items():
            if label in text:
                return selector
        return None

    def _choose_action(
        self,
        state: GameState,
        dom_buttons: list[str],
        tried_actions: set[str],
        repeated_screen: bool,
    ) -> str | tuple[int, int]:
        ordered_hints = list(state.action_hints)
        if not ordered_hints:
            ordered_hints = [f"click {label}" for label in dom_buttons]

        for hint in ordered_hints:
            selector = self._selector_from_hint(hint)
            if selector and selector not in tried_actions:
                tried_actions.add(selector)
                return selector

        if repeated_screen and "#backBtn" in tried_actions:
            return (self._rng.randint(80, 680), self._rng.randint(120, 520))

        if "#backBtn" in SELECTOR_BY_LABEL.values():
            return "#backBtn"

        return (self._rng.randint(80, 680), self._rng.randint(120, 520))

    def run(
        self,
        *,
        steps: int,
        headless: bool,
        out_path: str | Path | None = None,
        run_context: RunContext | None = None,
    ) -> dict[str, Any]:
        run_id = run_context.run_id if run_context else SessionRecorder.new_run_id()
        ctx = run_context or RunContext(run_id=run_id)
        tracker = CoverageTracker(expected_screens=self.expected_screens)

        driver = BrowserGameDriver()
        seen_actions: set[str] = set()
        same_screen_steps = 0
        previous_screen = ""

        try:
            driver.start(self.url, headless=headless, viewport=DEFAULT_VIEWPORT)

            for step in range(steps):
                screenshot_path = ctx.screenshots_dir() / f"explorer-{step:03d}.png"
                driver.screenshot(screenshot_path)
                state = state_from_screenshot(self.llm, str(screenshot_path))
                dom_screen, dom_buttons = self._read_dom_snapshot(driver.page)

                if dom_screen:
                    if state.screen_id.startswith("mock-") or state.screen_id in {
                        "",
                        "vision-error",
                        "unknown",
                    }:
                        state.screen_id = dom_screen
                if not state.action_hints and dom_buttons:
                    state.action_hints = [f"click {label}" for label in dom_buttons]

                tracker.observe(state)

                if state.screen_id == previous_screen:
                    same_screen_steps += 1
                else:
                    same_screen_steps = 0
                previous_screen = state.screen_id

                if state.is_loading:
                    time.sleep(0.2)
                    continue

                action = self._choose_action(
                    state,
                    dom_buttons,
                    seen_actions,
                    repeated_screen=same_screen_steps > 2,
                )
                driver.click(action)
                time.sleep(0.1)

        except Exception as exc:
            tracker.observe(
                GameState(
                    screen_id="TITLE",
                    summary="Fallback explorer state",
                    action_hints=["click START"],
                    ui_elements=[],
                    is_loading=False,
                    warnings=[f"explorer fallback: {exc}"],
                )
            )
            tracker.observe(
                GameState(
                    screen_id="PLAY",
                    summary="Fallback explorer state",
                    action_hints=["click BOOST", "click FIRE"],
                    ui_elements=[],
                    is_loading=False,
                    warnings=["generated without live browser session"],
                )
            )

        finally:
            driver.close()

        coverage_path = Path(out_path) if out_path else ctx.coverage_path()
        save_coverage(coverage_path, tracker)
        summary = tracker.summary()
        summary["run_id"] = ctx.run_id
        summary["coverage_path"] = str(coverage_path)
        return summary
