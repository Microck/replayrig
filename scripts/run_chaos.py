from __future__ import annotations

import argparse
import functools
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.chaos_agent import ChaosAgent


def _serve_demo_ephemeral() -> tuple[ThreadingHTTPServer, str]:
    directory = Path("demo/buggy_web_game").resolve()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    parser.add_argument("--steps", type=int, default=16)
    parser.add_argument("--duration-seconds", type=int, default=0)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    server = None
    url = args.url
    if not url:
        server, url = _serve_demo_ephemeral()

    try:
        agent = ChaosAgent(url=url)
        bug_path = agent.run(
            steps=args.steps,
            duration_seconds=(args.duration_seconds or None),
            headless=args.headless,
        )
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()

    if bug_path is not None:
        print(f"Bug detected and saved: {bug_path}")
        return 2

    print("No bug detected during chaos run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
