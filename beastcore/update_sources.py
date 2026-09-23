from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")


def normalize_repo(value: str | None) -> str:
    raw = str(value or "").strip()
    if _REPO_RE.fullmatch(raw):
        return raw
    try:
        p = urllib.parse.urlsplit(raw)
        if (p.hostname or "").lower() not in {"github.com", "www.github.com"}:
            return ""
        parts = [x for x in p.path.split("/") if x]
        if len(parts) < 2:
            return ""
        repo = f"{parts[0]}/{parts[1]}"
        if repo.endswith(".git"):
            repo = repo[:-4]
        return repo if _REPO_RE.fullmatch(repo) else ""
    except Exception:
        return ""


class TrustedSourcePolicy:
    """Small explicit trust boundary for unattended update *checks*.

    Built-in project sources are trusted for metadata lookup. Third-party Beast
    Packs are not automatically trusted merely because their manifest contains a
    GitHub URL. Users can add repositories to the local trust file later.
    """

    BUILTIN = {
        "patrickato/beastagotchi",
        "korrie71/pwnagotchi-theme-manager",
        "jayofelony/pwnagotchi",
    }

    def __init__(self, path: str | Path = "/var/lib/beastagotchi/ui/trusted_sources.json") -> None:
        self.path = Path(path)

    def repositories(self) -> list[str]:
        repos = set(self.BUILTIN)
        try:
            obj = json.loads(self.path.read_text())
            rows = obj.get("github_repositories") if isinstance(obj, dict) else []
            if isinstance(rows, list):
                for value in rows[:256]:
                    repo = normalize_repo(str(value))
                    if repo:
                        repos.add(repo.lower())
        except Exception:
            pass
        return sorted(repos)

    def trusted(self, repo: str) -> bool:
        normalized = normalize_repo(repo).lower()
        return bool(normalized and normalized in set(self.repositories()))


class GitHubReleaseChecker:
    """Read-only bounded GitHub release metadata client."""

    def __init__(self, *, timeout: float = 8.0, max_bytes: int = 1024 * 1024) -> None:
        self.timeout = float(timeout)
        self.max_bytes = int(max_bytes)

    def latest(self, repo: str) -> dict[str, Any]:
        repo = normalize_repo(repo)
        if not repo:
            raise ValueError("invalid GitHub repository")
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Beastagotchi-Update-Metadata/0.19",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            raw = response.read(self.max_bytes + 1)
        if len(raw) > self.max_bytes:
            raise ValueError("GitHub release metadata exceeded size limit")
        obj = json.loads(raw.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("invalid GitHub release response")
        tag = str(obj.get("tag_name") or obj.get("name") or "").strip()
        if not tag:
            raise ValueError("release metadata has no tag")
        assets = []
        for asset in (obj.get("assets") or [])[:128]:
            if not isinstance(asset, dict):
                continue
            assets.append({
                "name": str(asset.get("name") or "")[:180],
                "size_bytes": int(asset.get("size") or 0),
                "digest": str(asset.get("digest") or "")[:160],
            })
        has_digest = any(str(a.get("digest") or "").lower().startswith("sha256:") for a in assets)
        has_sidecar = any(str(a.get("name") or "").lower().endswith((".sha256", ".sha256.txt", "_sha256.txt")) for a in assets)
        return {
            "repository": repo,
            "version": tag,
            "published_at": obj.get("published_at"),
            "prerelease": bool(obj.get("prerelease")),
            "draft": bool(obj.get("draft")),
            "assets": assets,
            "verification": {
                "sha256_digest_asset": has_digest,
                "sha256_sidecar_asset": has_sidecar,
                "sha256_path_available": bool(has_digest or has_sidecar),
            },
        }
