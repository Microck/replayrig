from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import urllib.error
import urllib.parse
import urllib.request


class GitHubIssueClient:
    def __init__(
        self,
        *,
        repo: str | None = None,
        token: str | None = None,
        dry_run: bool = False,
        timeout_seconds: int = 20,
    ) -> None:
        self.repo = repo or os.getenv("GITHUB_REPO", "")
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.dry_run = dry_run
        self.timeout_seconds = timeout_seconds

    def _require_repo(self) -> str:
        if not self.repo and self.dry_run:
            return "owner/replayrig-dry-run"
        if not self.repo:
            raise RuntimeError("GITHUB_REPO is required (format: owner/repo)")
        return self.repo

    def _require_token(self) -> str:
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is required for non-dry-run GitHub calls")
        return self.token

    def _request_json(
        self,
        *,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
        accept: str = "application/vnd.github+json",
    ) -> dict[str, Any]:
        token = self._require_token()
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=body, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", accept)
        if body is not None:
            request.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub HTTP {exc.code}: {body_text[:240]}") from exc

        if not raw:
            return {}
        return json.loads(raw)

    def render_issue(
        self, bug: dict[str, Any], evidence_refs: list[dict[str, Any]]
    ) -> tuple[str, str]:
        detector = bug.get("detector", "bug")
        reason = str(bug.get("reason", "Unexpected behavior")).strip()
        run_id = str(bug.get("run_id", "unknown-run"))
        title = f"[{detector.upper()}] {reason[:80]}"

        repro_steps = bug.get("repro_steps", []) or ["Reproduction steps unavailable"]
        repro_section = "\n".join(
            f"{idx}. {step}" for idx, step in enumerate(repro_steps, start=1)
        )

        evidence_lines: list[str] = []
        for ref in evidence_refs:
            kind = str(ref.get("kind", "evidence"))
            url = ref.get("url")
            path = ref.get("path")
            if url:
                evidence_lines.append(f"- {kind}: {url}")
            elif path:
                evidence_lines.append(f"- {kind}: {path}")

        if not evidence_lines:
            evidence_lines.append("- No evidence provided")

        body = (
            "## Summary\n"
            f"- Detector: `{detector}`\n"
            f"- Reason: {reason}\n"
            f"- Run ID: `{run_id}`\n\n"
            "## Steps to Reproduce\n"
            f"{repro_section}\n\n"
            "## Expected Behavior\n"
            "Game should continue without crashing, hanging, or fatal console errors.\n\n"
            "## Actual Behavior\n"
            f"{reason}\n\n"
            "## Evidence\n"
            f"{'\n'.join(evidence_lines)}\n\n"
            "## Environment\n"
            "- Browser: Chromium (Playwright)\n"
            "- OS: Linux\n"
            f"- Run ID: `{run_id}`\n"
        )
        return title, body

    def create_issue(
        self,
        *,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        repo = self._require_repo()
        payload = {"title": title, "body": body, "labels": labels or []}

        if self.dry_run:
            return {
                "url": f"https://github.com/{repo}/issues/dry-run",
                "number": 0,
                "payload": payload,
            }

        response = self._request_json(
            method="POST",
            url=f"https://api.github.com/repos/{repo}/issues",
            payload=payload,
        )
        return {
            "url": response.get("html_url"),
            "number": response.get("number"),
            "payload": payload,
        }

    def comment(self, issue_number: int, body: str) -> dict[str, Any]:
        repo = self._require_repo()
        payload = {"body": body}
        if self.dry_run:
            return {
                "url": f"https://github.com/{repo}/issues/{issue_number}#dry-run-comment"
            }

        response = self._request_json(
            method="POST",
            url=f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
            payload=payload,
        )
        return {"url": response.get("html_url")}

    def get_or_create_release(self, *, tag: str, name: str) -> dict[str, Any]:
        repo = self._require_repo()
        if self.dry_run:
            return {
                "id": 0,
                "tag_name": tag,
                "name": name,
                "upload_url": f"https://uploads.github.com/repos/{repo}/releases/0/assets{{?name,label}}",
                "html_url": f"https://github.com/{repo}/releases/tag/{tag}",
            }

        tag_url = f"https://api.github.com/repos/{repo}/releases/tags/{urllib.parse.quote(tag)}"
        try:
            return self._request_json(method="GET", url=tag_url)
        except RuntimeError as exc:
            if "HTTP 404" not in str(exc):
                raise

        return self._request_json(
            method="POST",
            url=f"https://api.github.com/repos/{repo}/releases",
            payload={"tag_name": tag, "name": name, "prerelease": True},
        )

    def upload_release_asset(
        self,
        *,
        release_id: int,
        name: str,
        content_type: str,
        content: bytes,
    ) -> dict[str, Any]:
        repo = self._require_repo()
        if self.dry_run:
            return {
                "browser_download_url": (
                    f"https://github.com/{repo}/releases/download/dry-run/{urllib.parse.quote(name)}"
                )
            }

        token = self._require_token()
        upload_url = (
            f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets"
            f"?name={urllib.parse.quote(name)}"
        )
        request = urllib.request.Request(upload_url, data=content, method="POST")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("Content-Type", content_type)

        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"GitHub upload HTTP {exc.code}: {body_text[:240]}"
            ) from exc


def guess_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix == ".jpg" or suffix == ".jpeg":
        return "image/jpeg"
    if suffix == ".mp4":
        return "video/mp4"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".json":
        return "application/json"
    return "application/octet-stream"
