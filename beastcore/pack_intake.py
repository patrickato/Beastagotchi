from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

from .packs import clean_manifest, PackManifestError


class PackIntakeError(RuntimeError):
    pass


class PackIntakeManager:
    """Verify and stage local Beast Pack archives without executing pack code.

    Intake is intentionally split from installation. Archives arrive in a bounded
    inbox, are inspected for path traversal/link/archive-bomb risks, their
    manifest is normalized with the canonical Beast Pack schema, and only then
    may be extracted into the *staged* registry. No service is restarted, no
    plugin is enabled, and no file outside staged_root is changed.
    """

    ALLOWED_SUFFIXES = (".tar.gz", ".tgz", ".zip")

    def __init__(
        self,
        inbox_root: str | Path = "/var/lib/beastagotchi/packs/inbox",
        staged_root: str | Path = "/var/lib/beastagotchi/packs/staged",
        *,
        max_archive_bytes: int = 128 * 1024 * 1024,
        max_unpacked_bytes: int = 512 * 1024 * 1024,
        max_members: int = 2048,
        clock=time.time,
    ) -> None:
        self.inbox_root = Path(inbox_root)
        self.staged_root = Path(staged_root)
        self.max_archive_bytes = int(max_archive_bytes)
        self.max_unpacked_bytes = int(max_unpacked_bytes)
        self.max_members = int(max_members)
        self.clock = clock

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _safe_member(name: str) -> bool:
        p = Path(str(name or ""))
        return bool(name) and not p.is_absolute() and ".." not in p.parts

    def _resolve_inbox(self, name: str) -> Path:
        base = Path(str(name or "").strip()).name
        if not base or not base.lower().endswith(self.ALLOWED_SUFFIXES):
            raise PackIntakeError("unsupported or invalid Beast Pack archive name")
        root = self.inbox_root.resolve()
        path = (root / base).resolve()
        if path.parent != root or not path.is_file():
            raise PackIntakeError("Beast Pack archive not found in intake inbox")
        if path.stat().st_size > self.max_archive_bytes:
            raise PackIntakeError("Beast Pack archive exceeds configured size limit")
        return path

    @staticmethod
    def _strip_root(name: str, prefix: str) -> str:
        if prefix and name.startswith(prefix):
            return name[len(prefix):]
        return name

    @staticmethod
    def _manifest_root(names: list[str]) -> tuple[str, str]:
        candidates = [n for n in names if n == "manifest.json" or n.endswith("/manifest.json")]
        candidates = [n for n in candidates if len(Path(n).parts) <= 2]
        if len(candidates) != 1:
            raise PackIntakeError("archive must contain exactly one root manifest.json")
        manifest_name = candidates[0]
        parts = Path(manifest_name).parts
        prefix = f"{parts[0]}/" if len(parts) == 2 else ""
        return manifest_name, prefix

    def _inspect_tar(self, path: Path) -> dict[str, Any]:
        members_out: list[dict[str, Any]] = []
        with tarfile.open(path, "r:*") as tf:
            members = tf.getmembers()
            if len(members) > self.max_members:
                raise PackIntakeError("archive contains too many members")
            names: list[str] = []
            total = 0
            for m in members:
                name = str(m.name or "")
                if not self._safe_member(name):
                    raise PackIntakeError(f"unsafe archive path: {name[:120]}")
                if m.issym() or m.islnk() or m.isdev():
                    raise PackIntakeError(f"links/devices are not allowed in Beast Packs: {name[:120]}")
                if m.isfile():
                    total += max(0, int(m.size))
                    if total > self.max_unpacked_bytes:
                        raise PackIntakeError("archive exceeds unpacked size limit")
                names.append(name)
                if len(members_out) < 128:
                    members_out.append({"path": name, "size_bytes": int(m.size or 0), "kind": "file" if m.isfile() else "dir"})
            manifest_name, prefix = self._manifest_root(names)
            fh = tf.extractfile(manifest_name)
            if fh is None:
                raise PackIntakeError("manifest.json could not be read")
            manifest_obj = json.loads(fh.read().decode("utf-8"))
            manifest = clean_manifest(manifest_obj, source_path=str(path))
            return {
                "archive_type": "tar",
                "manifest": manifest,
                "manifest_member": manifest_name,
                "content_prefix": prefix,
                "member_count": len(members),
                "unpacked_bytes": total,
                "members_preview": members_out,
            }

    def _inspect_zip(self, path: Path) -> dict[str, Any]:
        members_out: list[dict[str, Any]] = []
        with zipfile.ZipFile(path, "r") as zf:
            infos = zf.infolist()
            if len(infos) > self.max_members:
                raise PackIntakeError("archive contains too many members")
            names: list[str] = []
            total = 0
            for info in infos:
                name = str(info.filename or "")
                if not self._safe_member(name):
                    raise PackIntakeError(f"unsafe archive path: {name[:120]}")
                mode = (int(info.external_attr) >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    raise PackIntakeError(f"links are not allowed in Beast Packs: {name[:120]}")
                total += max(0, int(info.file_size))
                if total > self.max_unpacked_bytes:
                    raise PackIntakeError("archive exceeds unpacked size limit")
                names.append(name)
                if len(members_out) < 128:
                    members_out.append({"path": name, "size_bytes": int(info.file_size), "kind": "dir" if info.is_dir() else "file"})
            manifest_name, prefix = self._manifest_root(names)
            manifest_obj = json.loads(zf.read(manifest_name).decode("utf-8"))
            manifest = clean_manifest(manifest_obj, source_path=str(path))
            return {
                "archive_type": "zip",
                "manifest": manifest,
                "manifest_member": manifest_name,
                "content_prefix": prefix,
                "member_count": len(infos),
                "unpacked_bytes": total,
                "members_preview": members_out,
            }

    def inspect(self, name: str) -> dict[str, Any]:
        path = self._resolve_inbox(name)
        try:
            detail = self._inspect_zip(path) if path.suffix.lower() == ".zip" else self._inspect_tar(path)
        except (PackManifestError, json.JSONDecodeError, tarfile.TarError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
            raise PackIntakeError(f"invalid Beast Pack: {type(exc).__name__}: {exc}") from exc
        manifest = detail["manifest"]
        destination = self.staged_root / str(manifest["id"])
        return {
            "ok": True,
            "ready_to_stage": True,
            "name": path.name,
            "path": str(path),
            "archive_bytes": int(path.stat().st_size),
            "sha256": self._sha256(path),
            "destination": str(destination),
            **detail,
            "executes_code": False,
            "installs_files": False,
            "enables_pack": False,
        }

    def plan_stage(self, name: str, *, replace: bool = False) -> dict[str, Any]:
        check = self.inspect(name)
        destination = Path(check["destination"])
        blockers: list[str] = []
        if destination.exists() and not replace:
            blockers.append("a staged pack with this id already exists; explicit replace is required")
        return {
            "allowed": not blockers,
            "operation": "pack.stage",
            "inspection": check,
            "replace": bool(replace),
            "blockers": blockers,
            "warnings": [
                "Staging verifies and extracts the archive but does not install, enable, restart, or execute the pack."
            ],
        }

    def stage(self, name: str, *, replace: bool = False) -> dict[str, Any]:
        plan = self.plan_stage(name, replace=replace)
        if not plan["allowed"]:
            raise PackIntakeError("; ".join(plan["blockers"]))
        check = plan["inspection"]
        src = self._resolve_inbox(name)
        manifest = dict(check["manifest"])
        destination = self.staged_root / str(manifest["id"])
        self.staged_root.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="beast-pack-intake-") as td:
            scratch = Path(td)
            prefix = str(check.get("content_prefix") or "")
            if check["archive_type"] == "zip":
                with zipfile.ZipFile(src, "r") as zf:
                    for info in zf.infolist():
                        name2 = str(info.filename or "")
                        if not self._safe_member(name2):
                            raise PackIntakeError("unsafe member during staging")
                        mode = (int(info.external_attr) >> 16) & 0xFFFF
                        if stat.S_ISLNK(mode):
                            raise PackIntakeError("link detected during staging")
                        rel = self._strip_root(name2, prefix)
                        if not rel:
                            continue
                        target = (scratch / rel).resolve()
                        if scratch.resolve() not in target.parents and target != scratch.resolve():
                            raise PackIntakeError("staging path escaped scratch directory")
                        if info.is_dir():
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(info, "r") as rf, target.open("wb") as wf:
                                shutil.copyfileobj(rf, wf)
            else:
                with tarfile.open(src, "r:*") as tf:
                    for m in tf.getmembers():
                        name2 = str(m.name or "")
                        if not self._safe_member(name2) or m.issym() or m.islnk() or m.isdev():
                            raise PackIntakeError("unsafe member during staging")
                        rel = self._strip_root(name2, prefix)
                        if not rel:
                            continue
                        target = (scratch / rel).resolve()
                        if scratch.resolve() not in target.parents and target != scratch.resolve():
                            raise PackIntakeError("staging path escaped scratch directory")
                        if m.isdir():
                            target.mkdir(parents=True, exist_ok=True)
                        elif m.isfile():
                            target.parent.mkdir(parents=True, exist_ok=True)
                            rf = tf.extractfile(m)
                            if rf is None:
                                raise PackIntakeError(f"could not extract {name2[:120]}")
                            with rf, target.open("wb") as wf:
                                shutil.copyfileobj(rf, wf)

            staged_manifest = scratch / "manifest.json"
            if not staged_manifest.is_file():
                raise PackIntakeError("normalized staged content is missing manifest.json")
            clean_manifest(json.loads(staged_manifest.read_text()), source_path=str(staged_manifest))

            if destination.exists():
                if not replace:
                    raise PackIntakeError("staged pack already exists")
                shutil.rmtree(destination)
            shutil.copytree(scratch, destination)

        state = {
            "schema": 1,
            "state": "verified",
            "enabled": False,
            "verified_at": float(self.clock()),
            "archive_name": src.name,
            "archive_sha256": check["sha256"],
            "archive_bytes": check["archive_bytes"],
            "unpacked_bytes": check["unpacked_bytes"],
        }
        state_path = destination / "state.json"
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
        os.chmod(state_path, 0o600)
        return {
            "ok": True,
            "staged": True,
            "installed": False,
            "enabled": False,
            "pack": manifest,
            "path": str(destination),
            "state": state,
        }
