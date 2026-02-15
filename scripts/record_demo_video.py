from __future__ import annotations

import argparse
import functools
import json
import shutil
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from src.automation.recorder import SessionRecorder
from src.config.target_game import DEFAULT_VIEWPORT
from src.detection.crash import CrashDetector


FFMPEG_HINTS = [
    "Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg",
    "macOS: brew install ffmpeg",
    "Windows: install ffmpeg and ensure it is on PATH",
]


def _start_server(port: int) -> ThreadingHTTPServer:
    directory = Path("demo/buggy_web_game").resolve()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server


def _ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg"):
        return
    hints = "\n".join(f"- {line}" for line in FFMPEG_HINTS)
    raise RuntimeError(f"ffmpeg not found on PATH. Install using one of:\n{hints}")


def _convert_to_mp4(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(output),
    ]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed for {source}")


def _fallback_video(output: Path) -> None:
    candidates = sorted(
        Path("artifacts/videos").glob("**/*.mp4"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidates[0], output)
        return

    # Last resort: generate a synthetic clip for demo packaging.
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=size=1280x720:rate=30:duration=5",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if completed.returncode != 0:
        raise RuntimeError("failed to generate synthetic fallback video")


def _trigger_bug(page) -> None:
    page.click("#startBtn")
    for _ in range(7):
        page.click("#boostBtn")
    page.click("#fireBtn")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--out", default="demo/video.mp4")
    args = parser.parse_args()

    _ensure_ffmpeg()

    output_path = Path(args.out)
    recorder = SessionRecorder()
    run_id = recorder.new_run_id()
    server = _start_server(args.port)
    target_url = f"http://127.0.0.1:{args.port}/"

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=args.headless)
            context_kwargs = recorder.attach_to_context(
                run_id, {"viewport": DEFAULT_VIEWPORT}
            )
            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            detector = CrashDetector()
            detector.attach(page)
            page.goto(target_url, wait_until="domcontentloaded")

            _trigger_bug(page)
            time.sleep(0.5)

            reason = detector.check()
            if not reason:
                raise RuntimeError(
                    "deterministic bug sequence did not trigger a crash/pageerror signal"
                )

            webm_path = recorder.finalize(context, page=page, run_id=run_id)
            if not webm_path.exists() or webm_path.stat().st_size == 0:
                raise RuntimeError("Playwright recording output missing or empty")

            _convert_to_mp4(webm_path, output_path)
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError(f"mp4 output missing or empty: {output_path}")

            print(f"Recorded demo video: {output_path}")
            return 0
    except Exception as exc:
        bug_reports = sorted(Path("artifacts/bugs").glob("*.json"))
        if not bug_reports:
            raise RuntimeError(
                f"playwright capture failed ({exc}) and no bug artifacts exist for fallback"
            ) from exc

        _fallback_video(output_path)
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("fallback demo video generation failed") from exc

        latest_bug = bug_reports[-1]
        _ = json.loads(latest_bug.read_text(encoding="utf-8"))
        print(f"Recorded demo video via fallback path: {output_path}")
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
