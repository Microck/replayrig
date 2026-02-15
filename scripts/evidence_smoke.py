from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.integrations.github import GitHubIssueClient
from src.storage.evidence import GitHubReleaseEvidenceStore, LocalEvidenceStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["local", "github-release"], default="local")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-id", default="evidence-smoke")
    args = parser.parse_args()

    sample_path = Path("artifacts/evidence/local-smoke.txt")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path.write_text("local evidence smoke", encoding="utf-8")

    if args.mode == "local":
        store = LocalEvidenceStore()
    else:
        github = GitHubIssueClient(
            dry_run=args.dry_run or not bool(os.getenv("GITHUB_TOKEN"))
        )
        store = GitHubReleaseEvidenceStore(
            github=github,
            run_id=args.run_id,
            dry_run=args.dry_run,
        )

    ref = store.publish(sample_path, kind="log")

    print(json.dumps(ref.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
