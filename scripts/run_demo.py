from __future__ import annotations

import argparse
import functools
import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.orchestrator import TestOrchestrator
from src.core.run_config import RunConfig


def _start_server(port: int) -> ThreadingHTTPServer:
    directory = Path("demo/buggy_web_game").resolve()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "soak"], default="demo")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--dry-run-github", action="store_true")
    args = parser.parse_args()

    server = None
    base_url = os.getenv("TARGET_GAME_URL", f"http://127.0.0.1:{args.port}/")
    if args.serve:
        server = _start_server(args.port)
        base_url = f"http://127.0.0.1:{args.port}/"

    try:
        run_config = RunConfig.for_mode(
            mode=args.mode,
            url=base_url,
            headless=args.headless,
            record_video=True,
            dry_run_github=args.dry_run_github or not bool(os.getenv("GITHUB_TOKEN")),
        )
        orchestrator = TestOrchestrator(config=run_config)
        result = orchestrator.run()
        print(json.dumps(result, indent=2, sort_keys=True))
        if result.get("bug_path"):
            print(f"bug_path={result['bug_path']}")
        if result.get("issue_url"):
            print(f"issue_url={result['issue_url']}")
        return 0
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
