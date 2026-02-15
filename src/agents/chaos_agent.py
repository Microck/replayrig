from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Callable

from src.automation.browser import BrowserGameDriver
from src.automation.recorder import SessionRecorder
from src.config.target_game import DEFAULT_VIEWPORT, TARGET_GAME_URL
from src.core.run_context import RunContext
from src.detection.crash import CrashDetector
from src.detection.hang import HangDetector
from src.evidence.capture import capture_bug_evidence
from src.models.bug import BugEvidence, BugReport
from src.vision.game_state import GameState, UIElement


class ChaosAgent:
    def __init__(
        self,
        *,
        url: str = TARGET_GAME_URL,
        run_context: RunContext | None = None,
        record_video: bool = True,
        random_seed: int = 13,
    ) -> None:
        self.url = url
        self.record_video = record_video
        self.run_context = run_context or RunContext(
            run_id=SessionRecorder.new_run_id()
        )
        self._rng = random.Random(random_seed)

        self.crash_detector = CrashDetector()
        self.hang_detector = HangDetector(
            max_same_screen_steps=8, max_loading_seconds=6.0
        )

    def _read_state(self, page: Any) -> GameState:
        try:
            screen = page.locator("#stateLabel").inner_text(timeout=300).strip().upper()
        except Exception:
            screen = "UNKNOWN"

        try:
            labels = [
                txt.strip()
                for txt in page.locator("button").all_inner_texts()
                if txt.strip()
            ]
        except Exception:
            labels = []

        return GameState(
            screen_id=screen,
            summary=f"Chaos observed {screen}",
            action_hints=[f"click {label}" for label in labels],
            ui_elements=[UIElement(label=label, type="button") for label in labels],
            is_loading=False,
            warnings=[],
        )

    def _adversarial_actions(
        self, driver: BrowserGameDriver
    ) -> list[tuple[str, Callable[[], None]]]:
        def rapid_boost() -> None:
            for _ in range(6):
                driver.click("#boostBtn")

        def boost_seven() -> None:
            for _ in range(7):
                driver.click("#boostBtn")

        def random_click() -> None:
            x = self._rng.randint(50, 700)
            y = self._rng.randint(80, 560)
            driver.click((x, y))

        def spam_keys() -> None:
            driver.type("!@#$%^&*" * 8)

        def escape_back() -> None:
            if driver.page is not None:
                driver.page.keyboard.press("Escape")
            driver.click("#backBtn")

        return [
            ("START", lambda: driver.click("#startBtn")),
            ("BOOST x7", boost_seven),
            ("FIRE", lambda: driver.click("#fireBtn")),
            ("RAPID BOOST BURST", rapid_boost),
            ("RANDOM CLICK", random_click),
            ("SPAM KEYS", spam_keys),
            ("ESCAPE/BACK", escape_back),
        ]

    def run(
        self,
        *,
        steps: int | None = None,
        duration_seconds: int | None = None,
        headless: bool = True,
    ) -> Path | None:
        driver = BrowserGameDriver()
        recorder = SessionRecorder(artifacts_root=self.run_context.artifacts_root)
        self.run_context.metadata["recorder"] = recorder

        context_kwargs: dict[str, Any] = {}
        if self.record_video:
            context_kwargs = recorder.attach_to_context(self.run_context.run_id)

        actions_taken: list[str] = []
        actions = self._adversarial_actions(driver)
        limit_steps = steps if steps is not None else len(actions)
        start_ts = time.time()

        video_path: str | None = None
        try:
            driver.start(
                self.url,
                headless=headless,
                viewport=DEFAULT_VIEWPORT,
                context_kwargs=context_kwargs,
            )
            if driver.page is None:
                raise RuntimeError(
                    "ChaosAgent requires an active page after driver.start"
                )
            self.crash_detector.attach(driver.page)

            step_idx = 0
            while True:
                if (
                    duration_seconds is not None
                    and time.time() - start_ts > duration_seconds
                ):
                    break
                if limit_steps is not None and step_idx >= limit_steps:
                    break

                action_name, action_fn = actions[step_idx % len(actions)]
                actions_taken.append(action_name)

                try:
                    last_shot = (
                        self.run_context.screenshots_dir()
                        / f"chaos-step-{step_idx:03d}.png"
                    )
                    driver.screenshot(last_shot)
                    self.run_context.metadata["last_screenshot_path"] = str(last_shot)
                except Exception:
                    pass

                try:
                    action_fn()
                except Exception as exc:
                    self.crash_detector.observe_exception(exc)

                state = self._read_state(driver.page)
                now = time.time()
                self.hang_detector.observe(state, now)

                crash_reason = self.crash_detector.check()
                hang_reason = self.hang_detector.check(now)
                reason = crash_reason or hang_reason
                if reason:
                    if self.record_video and driver.context is not None:
                        try:
                            video_file = recorder.finalize(
                                driver.context,
                                page=driver.page,
                                run_id=self.run_context.run_id,
                            )
                            video_path = str(video_file)
                            self.run_context.metadata["video_path"] = video_path
                        except Exception:
                            video_path = None

                    evidence_paths = capture_bug_evidence(
                        self.run_context,
                        driver.page,
                        state,
                        "chaos-trigger",
                    )
                    if video_path:
                        evidence_paths["video_path"] = video_path

                    bug = BugReport(
                        run_id=self.run_context.run_id,
                        detector="crash" if crash_reason else "hang",
                        reason=reason,
                        last_state=state.to_dict(),
                        repro_steps=actions_taken,
                        evidence=BugEvidence(
                            screenshot_path=evidence_paths.get("screenshot_path"),
                            state_path=evidence_paths.get("state_path"),
                            video_path=evidence_paths.get("video_path"),
                        ),
                    )
                    bug_path = self.run_context.bugs_dir() / f"{bug.bug_id}.json"
                    bug.to_json(bug_path)
                    return bug_path

                step_idx += 1
                time.sleep(0.08)

        finally:
            driver.close()

        return None
