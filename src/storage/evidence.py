from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.integrations.github import GitHubIssueClient, guess_content_type


@dataclass
class EvidenceRef:
    kind: str
    path: str
    url: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {"kind": self.kind, "path": self.path, "url": self.url}


class EvidenceStore:
    def publish(self, path: str | Path, *, kind: str) -> EvidenceRef:
        raise NotImplementedError


class LocalEvidenceStore(EvidenceStore):
    def publish(self, path: str | Path, *, kind: str) -> EvidenceRef:
        local_path = Path(path)
        return EvidenceRef(kind=kind, path=str(local_path), url=None)


class GitHubReleaseEvidenceStore(EvidenceStore):
    def __init__(
        self,
        *,
        github: GitHubIssueClient,
        run_id: str,
        dry_run: bool = False,
    ) -> None:
        self.github = github
        self.run_id = run_id
        self.dry_run = dry_run
        self._release_cache: dict[str, str | int] | None = None

    def _release(self) -> dict[str, str | int]:
        if self._release_cache is not None:
            return self._release_cache
        tag = f"evidence-{self.run_id}"
        release = self.github.get_or_create_release(
            tag=tag,
            name=f"ReplayRig Evidence {self.run_id}",
        )
        self._release_cache = release
        return release

    def publish(self, path: str | Path, *, kind: str) -> EvidenceRef:
        file_path = Path(path)
        release = self._release()
        asset = self.github.upload_release_asset(
            release_id=int(release.get("id", 0)),
            name=file_path.name,
            content_type=guess_content_type(file_path),
            content=file_path.read_bytes(),
        )
        return EvidenceRef(
            kind=kind,
            path=str(file_path),
            url=str(asset.get("browser_download_url")),
        )
