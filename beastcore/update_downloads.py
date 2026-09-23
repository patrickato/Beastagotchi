from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .update_sources import GitHubReleaseChecker, TrustedSourcePolicy, normalize_repo


class UpdateStageError(RuntimeError):
    pass


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_SIDECAR_LINE_RE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")


class _RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    ALLOWED = {
        "github.com",
        "www.github.com",
        "release-assets.githubusercontent.com",
        "objects.githubusercontent.com",
        "github-releases.githubusercontent.com",
    }

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        p = urllib.parse.urlsplit(newurl)
        if p.scheme != "https" or (p.hostname or "").lower() not in self.ALLOWED:
            raise UpdateStageError("release download redirected outside GitHub asset infrastructure")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class GitHubAssetFetcher:
    """Bounded HTTPS fetcher restricted to GitHub release infrastructure."""

    ALLOWED_INITIAL = {"github.com", "www.github.com"}

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = float(timeout)
        self.opener = urllib.request.build_opener(_RestrictedRedirect())

    @classmethod
    def validate_url(cls, url: str) -> str:
        raw = str(url or "").strip()
        p = urllib.parse.urlsplit(raw)
        if p.scheme != "https" or (p.hostname or "").lower() not in cls.ALLOWED_INITIAL:
            raise UpdateStageError("release asset URL is not an allowed GitHub HTTPS URL")
        return raw

    def fetch_bytes(self, url: str, *, max_bytes: int) -> bytes:
        url = self.validate_url(url)
        req = urllib.request.Request(url, headers={"User-Agent": "Beastagotchi-Verified-Stager/0.19"})
        with self.opener.open(req, timeout=self.timeout) as response:
            length = response.headers.get("Content-Length")
            if length and int(length) > int(max_bytes):
                raise UpdateStageError("release asset exceeds configured size limit")
            data = response.read(int(max_bytes) + 1)
        if len(data) > int(max_bytes):
            raise UpdateStageError("release asset exceeds configured size limit")
        return data


class VerifiedUpdateStager:
    """Download and SHA-256 verify trusted release assets without installing them."""

    def __init__(
        self,
        state,
        *,
        root: str | Path = "/var/lib/beastagotchi/updates/staged",
        trust_path: str | Path = "/var/lib/beastagotchi/ui/trusted_sources.json",
        checker=None,
        fetcher=None,
        max_artifact_bytes: int = 256 * 1024 * 1024,
        clock=time.time,
    ) -> None:
        self.state = state
        self.root = Path(root)
        self.trust = TrustedSourcePolicy(trust_path)
        self.checker = checker or GitHubReleaseChecker()
        self.fetcher = fetcher or GitHubAssetFetcher()
        self.max_artifact_bytes = int(max_artifact_bytes)
        self.clock = clock

    @staticmethod
    def _safe_component(value: str) -> str:
        raw = re.sub(r"[^A-Za-z0-9._:-]+", "_", str(value or "").strip())[:128]
        if not raw or raw.startswith("."):
            raise UpdateStageError("invalid update component")
        return raw.replace(":", "__")

    @staticmethod
    def _release_asset(name: str) -> bool:
        low = name.lower()
        if low.endswith((".sha256", ".sha256.txt", "_sha256.txt", ".sig", ".asc")):
            return False
        return low.endswith((".zip", ".tar.gz", ".tgz"))

    @staticmethod
    def _direct_digest(asset: dict[str, Any]) -> str:
        raw = str(asset.get("digest") or "").strip().lower()
        if raw.startswith("sha256:"):
            raw = raw.split(":", 1)[1].strip()
        return raw if _SHA256_RE.fullmatch(raw) else ""

    @staticmethod
    def _sidecar_for(asset: dict[str, Any], assets: list[dict[str, Any]]) -> dict[str, Any] | None:
        name = str(asset.get("name") or "")
        low = name.lower()
        preferred = {f"{low}.sha256", f"{low}.sha256.txt"}
        for row in assets:
            if str(row.get("name") or "").lower() in preferred:
                return row
        for row in assets:
            n = str(row.get("name") or "").lower()
            if n in {"sha256.txt", "sha256sums", "sha256sums.txt"} or n.endswith("_sha256.txt"):
                return row
        return None

    @staticmethod
    def _hash_from_sidecar(data: bytes, target_name: str) -> str:
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise UpdateStageError("SHA-256 sidecar is not UTF-8 text") from exc
        target = Path(target_name).name
        matches = []
        for line in text.splitlines():
            m = _SIDECAR_LINE_RE.match(line.strip())
            if not m:
                continue
            digest, name = m.group(1).lower(), Path(m.group(2).strip()).name
            if name == target:
                return digest
            matches.append((digest, name))
        if len(matches) == 1:
            return matches[0][0]
        raise UpdateStageError("SHA-256 sidecar does not identify the selected asset")

    def _component(self, component_id: str) -> dict[str, Any]:
        for row in self.state.get("updates.components", []) or []:
            if isinstance(row, dict) and str(row.get("id") or "") == component_id:
                return row
        raise UpdateStageError("update component is not present in current canonical state")

    def _select_asset(self, component: dict[str, Any], release: dict[str, Any], asset_name: str = "") -> tuple[dict[str, Any], dict[str, Any] | None, str]:
        assets = [x for x in (release.get("assets") or []) if isinstance(x, dict)]
        if str(component.get("id") or "") == "pwnagotchi":
            raise UpdateStageError("Pwnagotchi platform images require a dedicated platform-update adapter")
        candidates = [x for x in assets if self._release_asset(str(x.get("name") or "")) and x.get("download_url")]
        if asset_name:
            candidates = [x for x in candidates if str(x.get("name") or "") == asset_name]
        if len(candidates) != 1:
            if not candidates:
                raise UpdateStageError("no supported release archive is available for verified staging")
            raise UpdateStageError("release has multiple candidate archives; an explicit asset selection is required")
        asset = candidates[0]
        digest = self._direct_digest(asset)
        sidecar = None
        if not digest:
            sidecar = self._sidecar_for(asset, assets)
            if sidecar is None or not sidecar.get("download_url"):
                raise UpdateStageError("selected release asset has no SHA-256 verification path")
        return asset, sidecar, digest

    def plan(self, component_id: str, *, asset_name: str = "") -> dict[str, Any]:
        component = self._component(str(component_id or ""))
        blockers = []
        repo = normalize_repo(str(component.get("source") or component.get("repository") or ""))
        if component.get("source_type") != "github_release" or not repo:
            blockers.append("component is not backed by a supported GitHub release source")
        if repo and not self.trust.trusted(repo):
            blockers.append("component repository is not trusted for automatic release access")
        if component.get("update_available") is not True:
            blockers.append("component does not currently report a newer release")
        release = None
        selected = sidecar = None
        digest = ""
        if not blockers:
            try:
                release = self.checker.latest(repo)
                selected, sidecar, digest = self._select_asset(component, release, asset_name)
                if int(selected.get("size_bytes") or 0) > self.max_artifact_bytes:
                    blockers.append("selected release asset exceeds update staging size limit")
            except Exception as exc:
                blockers.append(f"{type(exc).__name__}: {exc}")
        return {
            "allowed": not blockers,
            "operation": "update.stage",
            "component": str(component.get("id") or component_id),
            "repository": repo,
            "installed_version": component.get("installed_version"),
            "available_version": component.get("available_version"),
            "release": release,
            "asset": selected,
            "sidecar": sidecar,
            "direct_sha256": bool(digest),
            "blockers": blockers,
            "warnings": [
                "Verified staging downloads a release archive but does not install or execute it.",
                "The running Beastagotchi/Pwnagotchi services are not restarted.",
            ],
        }

    def stage(self, component_id: str, *, asset_name: str = "") -> dict[str, Any]:
        plan = self.plan(component_id, asset_name=asset_name)
        if not plan["allowed"]:
            raise UpdateStageError("; ".join(plan["blockers"]))
        asset = dict(plan["asset"] or {})
        sidecar = plan.get("sidecar") if isinstance(plan.get("sidecar"), dict) else None
        expected = self._direct_digest(asset)
        if not expected and sidecar:
            sidecar_data = self.fetcher.fetch_bytes(str(sidecar.get("download_url") or ""), max_bytes=1024 * 1024)
            expected = self._hash_from_sidecar(sidecar_data, str(asset.get("name") or ""))
        if not expected:
            raise UpdateStageError("no usable SHA-256 expectation was resolved")

        data = self.fetcher.fetch_bytes(str(asset.get("download_url") or ""), max_bytes=self.max_artifact_bytes)
        actual = hashlib.sha256(data).hexdigest()
        if actual.lower() != expected.lower():
            raise UpdateStageError("downloaded release asset failed SHA-256 verification")

        component_dir = self.root / self._safe_component(str(plan["component"]))
        version = re.sub(r"[^A-Za-z0-9._-]+", "_", str(plan.get("available_version") or "unknown"))[:80] or "unknown"
        final_dir = component_dir / version
        self.root.mkdir(parents=True, exist_ok=True)
        component_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="beast-update-stage-", dir=str(component_dir)) as td:
            scratch = Path(td)
            artifact = scratch / Path(str(asset.get("name") or "update.bin")).name
            artifact.write_bytes(data)
            os.chmod(artifact, 0o600)
            metadata = {
                "schema": 1,
                "verified": True,
                "component": plan["component"],
                "repository": plan["repository"],
                "version": plan["available_version"],
                "asset_name": artifact.name,
                "size_bytes": len(data),
                "sha256": actual,
                "verified_at": float(self.clock()),
                "installed": False,
                "executed": False,
            }
            (scratch / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
            os.chmod(scratch / "metadata.json", 0o600)
            if final_dir.exists():
                shutil.rmtree(final_dir)
            os.replace(scratch, final_dir)

        return {
            "ok": True,
            "staged": True,
            "verified": True,
            "installed": False,
            "executed": False,
            "component": plan["component"],
            "version": plan["available_version"],
            "path": str(final_dir),
            "artifact": str(final_dir / Path(str(asset.get("name") or "")).name),
            "sha256": actual,
        }
