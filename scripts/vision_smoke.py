from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm.foundry_client import FoundryLLMClient
from src.vision.foundry_vision import (
    state_from_payload,
    state_from_screenshot,
    state_to_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--mock-response", default="")
    args = parser.parse_args()

    if args.mock_response:
        payload_path = Path(args.mock_response)
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        state = state_from_payload(payload)
        print(state_to_json(state))
        return 0

    if not args.image:
        raise SystemExit("--image is required unless --mock-response is provided")

    llm = FoundryLLMClient(mock=not args.live)
    state = state_from_screenshot(llm, args.image)
    print(state_to_json(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
