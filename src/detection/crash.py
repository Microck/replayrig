from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrashDetector:
    fatal_console_patterns: list[str] = field(
        default_factory=lambda: [
            "DEMO_CRASH",
            "TypeError",
            "ReferenceError",
            "Unhandled",
        ]
    )
    _reasons: list[str] = field(default_factory=list)
    _attached: bool = False

    def mark(self, reason: str) -> None:
        if reason not in self._reasons:
            self._reasons.append(reason)

    def observe_exception(self, error: Exception | str) -> None:
        self.mark(f"exception: {error}")

    def observe_console(self, message_text: str) -> None:
        for pattern in self.fatal_console_patterns:
            if pattern.lower() in message_text.lower():
                self.mark(f"console fatal pattern matched: {pattern}")
                break

    def observe_http_status(self, status_code: int) -> None:
        if status_code >= 500:
            self.mark(f"http status >=500 observed: {status_code}")

    def attach(self, page: Any) -> None:
        if self._attached:
            return
        page.on("pageerror", lambda err: self.mark(f"pageerror: {err}"))
        page.on("crash", lambda: self.mark("playwright crash event"))

        def _on_console(msg: Any) -> None:
            msg_type = getattr(msg, "type", "console")
            msg_text = getattr(msg, "text", "")
            if callable(msg_text):
                msg_text = msg_text()
            self.observe_console(f"{msg_type}: {msg_text}")

        page.on("console", _on_console)

        def _on_response(resp: Any) -> None:
            status = getattr(resp, "status", None)
            if callable(status):
                status = status()
            if isinstance(status, int):
                self.observe_http_status(status)

        page.on("response", _on_response)
        self._attached = True

    def check(self) -> str | None:
        if not self._reasons:
            return None
        return self._reasons[0]

    def reasons(self) -> list[str]:
        return list(self._reasons)
