from __future__ import annotations

import json
import os
import stat
import time
from pathlib import Path
from typing import Any

from .packs import clean_manifest, PackManifestError


class PackActivationError(RuntimeError):
    pass


CONTENT_ONLY_TYPES = {
    "theme", "face", "animation", "audio", "layout", "board", "data", "map",
}

_FORBIDDEN_SUFFIXES = {
    ".py", ".pyc", ".pyo", ".so", ".sh", ".bash", ".zsh", ".fish",
    ".service", ".timer", ".socket", ".path", ".mount", ".desktop",
    ".exe", ".dll", ".dylib", ".bin", ".elf",
}


class PackActivationManager:
    """Enable/disable installed content-only Packs without copying into /opt."""

    def __init__(
        self,
        state,
        *,
        installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
        clock=time.time,
    ) -> None:
        self.state = state
        self.installed_root = Path(installed_root)
        self.clock = clock

    @staticmethod
    def _safe_id(pack_id: str) -> str:
        value = str(pack_id or "").strip().lower()
        if not value or "/" in value or "\\" in value or value in {".", ".."}:
            raise PackActivationError("invalid Beast Pack id")
        if any(c not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for c in value):
            raise PackActivationError("invalid Beast Pack id")
        return value[:64]

    def _dir(self, pack_id: str) -> Path:
        pack_id = self._safe_id(pack_id)
        root = self.installed_root.resolve()
        path = (root / pack_id).resolve()
        if path.parent != root or not path.is_dir():
            raise PackActivationError("installed Beast Pack not found")
        return path

    @staticmethod
    def _json(path: Path) -> dict[str, Any]:
        try:
            obj = json.loads(path.read_text())
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _manifest(self, path: Path) -> dict[str, Any]:
        fp = path / "manifest.json"
        try:
            row = clean_manifest(json.loads(fp.read_text()), source_path=str(fp))
        except (OSError, json.JSONDecodeError, PackManifestError) as exc:
            raise PackActivationError(f"invalid installed manifest: {type(exc).__name__}: {exc}") from exc
        if row["id"] != path.name:
            raise PackActivationError("installed manifest id does not match registry directory")
        return row

    @staticmethod
    def _content_scan(path: Path) -> list[str]:
        blockers: list[str] = []
        for fp in path.rglob("*"):
            if not fp.is_file():
                continue
            rel = str(fp.relative_to(path))
            if fp.name in {"manifest.json", "state.json"}:
                continue
            if fp.suffix.lower() in _FORBIDDEN_SUFFIXES:
                blockers.append(f"executable/code-like content is not allowed in content-only activation: {rel}")
                continue
            try:
                if fp.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                    blockers.append(f"executable permission is not allowed in content-only activation: {rel}")
            except OSError:
                blockers.append(f"cannot inspect Pack content: {rel}")
        return blockers[:32]

    def plan(self, pack_id: str, enabled: bool) -> dict[str, Any]:
        path = self._dir(pack_id)
        manifest = self._manifest(path)
        state = self._json(path / "state.json")
        blockers: list[str] = []
        ptype = str(manifest.get("pack_type") or "")
        if ptype not in CONTENT_ONLY_TYPES:
            blockers.append(f"{ptype or 'unknown'} Packs require a dedicated activation adapter")
        if manifest.get("background_service"):
            blockers.append("content-only Packs may not declare a background service")
        if manifest.get("services") or manifest.get("restart_services"):
            blockers.append("content-only Packs may not declare service changes")
        if manifest.get("permissions"):
            blockers.append("content-only Packs may not request privileged permissions")
        blockers.extend(self._content_scan(path))

        if ptype == "theme":
            theme_dir = path / "themes"
            themes = sorted(theme_dir.glob("*.json")) if theme_dir.is_dir() else []
            if not themes:
                blockers.append("theme Pack contains no themes/*.json files")
            for fp in themes[:64]:
                try:
                    obj = json.loads(fp.read_text())
                    tid = str(obj.get("id") or "").strip()
                    if not tid or fp.stem != tid:
                        blockers.append(f"theme id must match filename: {fp.name}")
                    colors = obj.get("colors")
                    if not isinstance(colors, dict) or not colors:
                        blockers.append(f"theme is missing a color map: {fp.name}")
                except Exception:
                    blockers.append(f"theme JSON is unreadable: {fp.name}")

        current = bool(state.get("enabled", False))
        return {
            "allowed": not blockers,
            "operation": "pack.activate" if enabled else "pack.deactivate",
            "pack": manifest,
            "path": str(path),
            "current_enabled": current,
            "requested_enabled": bool(enabled),
            "no_change": current == bool(enabled),
            "activation_tier": "content_only",
            "executes_code": False,
            "service_restart_required": False,
            "blockers": blockers,
            "warnings": [],
        }

    def set_enabled(self, pack_id: str, enabled: bool) -> dict[str, Any]:
        plan = self.plan(pack_id, enabled)
        if not plan["allowed"]:
            raise PackActivationError("; ".join(plan["blockers"]))
        path = Path(plan["path"])
        state_path = path / "state.json"
        row = self._json(state_path)
        before = bool(row.get("enabled", False))
        row.update({
            "schema": 1,
            "state": "enabled" if enabled else "disabled",
            "enabled": bool(enabled),
            "activation_state": "active" if enabled else "inactive",
            "activation_tier": "content_only",
            "activation_changed_at": float(self.clock()),
        })
        tmp = state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(state_path)
        return {
            "ok": True,
            "changed": before != bool(enabled),
            "pack": plan["pack"],
            "enabled": bool(enabled),
            "activation_tier": "content_only",
            "executes_code": False,
            "service_restart_performed": False,
            "state": row,
        }
