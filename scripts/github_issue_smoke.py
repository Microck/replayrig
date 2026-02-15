from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.integrations.github import GitHubIssueClient
from src.models.bug import BugReport


def _evidence_refs_from_bug(bug: BugReport) -> list[dict[str, str | None]]:
    refs: list[dict[str, str | None]] = []
    evidence = bug.evidence

    if evidence.screenshot_path:
        refs.append(
            {"kind": "screenshot", "path": evidence.screenshot_path, "url": None}
        )
    if evidence.state_path:
        refs.append({"kind": "state", "path": evidence.state_path, "url": None})
    if evidence.video_path:
        video_path = Path(evidence.video_path)
        if not video_path.exists():
            raise RuntimeError(f"video_path does not exist: {video_path}")
        refs.append({"kind": "video", "path": str(video_path), "url": None})
    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bug", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--labels", default="bug,qa-swarm")
    args = parser.parse_args()

    bug = BugReport.from_json(args.bug)
    evidence_refs = _evidence_refs_from_bug(bug)

    use_dry_run = args.dry_run or not bool(os.getenv("GITHUB_TOKEN"))
    client = GitHubIssueClient(dry_run=use_dry_run)

    title, body = client.render_issue(bug.to_dict(), evidence_refs)
    print(body)

    if use_dry_run:
        return 0

    issue = client.create_issue(
        title=title,
        body=body,
        labels=[label.strip() for label in args.labels.split(",") if label.strip()],
    )
    print(f"Issue URL: {issue.get('url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
