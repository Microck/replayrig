from __future__ import annotations

import secrets
import time
from pathlib import Path
from typing import Any


class SessionRecorder:
    def __init__(self, *, artifacts_root: str | Path = "artifacts") -> None:
        self.artifacts_root = Path(artifacts_root)

    @staticmethod
    def new_run_id() -> str:
        ts = time.strftime("%Y%m%d-%H%M%S")
        return f"{ts}-{secrets.token_hex(3)}"

    def video_dir(self, run_id: str) -> Path:
        return self.artifacts_root / "videos" / run_id

    def screenshot_dir(self, run_id: str) -> Path:
        return self.artifacts_root / "screenshots" / run_id

    def attach_to_context(
        self, run_id: str, context_kwargs: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        kwargs = dict(context_kwargs or {})
        video_dir = self.video_dir(run_id)
        video_dir.mkdir(parents=True, exist_ok=True)
        kwargs["record_video_dir"] = str(video_dir)
        return kwargs

    def capture_screenshot(self, page, run_id: str, label: str) -> Path:
        out_dir = self.screenshot_dir(run_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in label)
        out = out_dir / f"{int(time.time())}-{safe}.png"
        page.screenshot(path=str(out), full_page=True)
        return out

    def finalize(self, context, page=None, run_id: str | None = None) -> Path:
        """Close Playwright context and return best-effort video path."""

        video_path = None
        try:
            if page is not None and getattr(page, "video", None) is not None:
                try:
                    video_path = Path(page.video.path())
                except Exception:
                    video_path = None
        finally:
            context.close()

        if video_path and video_path.exists():
            return video_path

        # Fallback: find the newest file under the expected directory.
        if run_id:
            vdir = self.video_dir(run_id)
            if vdir.exists():
                files = sorted(
                    vdir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True
                )
                if files:
                    return files[0]

        raise FileNotFoundError("video not found after context close")
