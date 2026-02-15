from __future__ import annotations

import argparse
import functools
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.automation.browser import BrowserGameDriver
from src.config.target_game import DEFAULT_VIEWPORT, TARGET_GAME_URL


def _serve_game_ephemeral() -> tuple[ThreadingHTTPServer, str]:
    directory = Path("demo/buggy_web_game").resolve()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    port = server.server_address[1]
    return server, f"http://127.0.0.1:{port}/"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--type-text", default="")
    args = parser.parse_args()

    server = None
    url = args.url or ""
    if not url:
        server, url = _serve_game_ephemeral()
    else:
        url = TARGET_GAME_URL if url == "" else url

    driver = BrowserGameDriver()
    try:
        driver.start(url, headless=args.headless, viewport=DEFAULT_VIEWPORT)
        # Basic interaction
        driver.click("#startBtn")
        driver.click("#boostBtn")
        if args.type_text:
            driver.type(args.type_text)

        ts = time.strftime("%Y%m%d-%H%M%S")
        out = Path("artifacts/screenshots") / f"smoke-{ts}.png"
        driver.screenshot(out)
        print(f"OK: wrote screenshot: {out}")
        return 0
    except Exception as exc:
        print(f"ERROR: smoke run failed: {exc}")
        return 2
    finally:
        driver.close()
        if server is not None:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
