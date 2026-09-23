from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path
from typing import Any


PACK_TYPES = (
    "theme", "face", "animation", "audio", "layout", "board", "app",
    "hardware", "mission", "data", "map", "renderer", "integration",
    "developer", "experimental",
)
RESOURCE_CLASSES = ("none", "low", "medium", "high")
THERMAL_CLASSES = ("static", "animated", "compute", "heavy")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class PackManifestError(ValueError):
    pass


def _string_list(value: Any, *, limit: int = 64) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(x).strip()[:128] for x in value[:limit] if str(x).strip()]


def _safe_url(value: Any) -> str:
    raw = str(value or "").strip()[:1024]
    if not raw:
        return ""
    try:
        p = urllib.parse.urlsplit(raw)
        host = p.hostname or ""
        if p.port:
            host += f":{p.port}"
        return urllib.parse.urlunsplit((p.scheme, host, p.path, p.query, ""))
    except Exception:
        return ""


def clean_manifest(obj: dict[str, Any], *, source_path: str = "") -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise PackManifestError("manifest must be an object")
    pack_id = str(obj.get("id") or "").strip().lower()
    if not _ID_RE.fullmatch(pack_id):
        raise PackManifestError("invalid pack id")
    label = str(obj.get("label") or "").strip()
    if not label:
        raise PackManifestError("pack label is required")
    pack_type = str(obj.get("pack_type") or obj.get("type") or "").strip().lower()
    if pack_type not in PACK_TYPES:
        raise PackManifestError(f"unsupported pack type: {pack_type or 'missing'}")
    resource = str(obj.get("resource_class") or "low").strip().lower()
    thermal = str(obj.get("thermal_class") or "static").strip().lower()
    if resource not in RESOURCE_CLASSES:
        raise PackManifestError("invalid resource_class")
    if thermal not in THERMAL_CLASSES:
        raise PackManifestError("invalid thermal_class")

    compatibility = obj.get("compatibility") if isinstance(obj.get("compatibility"), dict) else {}
    source = obj.get("source") if isinstance(obj.get("source"), dict) else {}
    return {
        "id": pack_id,
        "label": label[:80],
        "version": str(obj.get("version") or "0").strip()[:48],
        "pack_type": pack_type,
        "description": str(obj.get("description") or "").strip()[:320],
        "author": str(obj.get("author") or "").strip()[:96],
        "license": str(obj.get("license") or "").strip()[:64],
        "homepage": _safe_url(obj.get("homepage")),
        "dependencies": _string_list(obj.get("dependencies")),
        "conflicts": _string_list(obj.get("conflicts")),
        "capabilities": _string_list(obj.get("capabilities")),
        "permissions": _string_list(obj.get("permissions")),
        "services": _string_list(obj.get("services")),
        "restart_services": _string_list(obj.get("restart_services")),
        "supported_displays": _string_list(obj.get("supported_displays")),
        "background_service": bool(obj.get("background_service", False)),
        "enabled_by_default": bool(obj.get("enabled_by_default", False)),
        "resource_class": resource,
        "thermal_class": thermal,
        "compatibility": {
            "beast_min": str(compatibility.get("beast_min") or "")[:48],
            "beast_max": str(compatibility.get("beast_max") or "")[:48],
            "pwnagotchi_min": str(compatibility.get("pwnagotchi_min") or "")[:48],
            "pwnagotchi_max": str(compatibility.get("pwnagotchi_max") or "")[:48],
        },
        "source": {
            "type": str(source.get("type") or "local").strip().lower()[:32],
            "url": _safe_url(source.get("url")),
            "channel": str(source.get("channel") or "stable").strip().lower()[:32],
        },
        "source_path": str(source_path),
    }


class PackRegistryEngine:
    """Read-only catalog of installed/staged Beast Packs.

    v0.19 deliberately separates understanding a package from installing one.
    This engine never downloads, executes, enables, or removes code.
    """

    def __init__(self, state, roots: dict[str, str | Path] | None = None) -> None:
        self.state = state
        roots = roots or {
            "builtin": "/opt/beast-ui/packs",
            "installed": "/var/lib/beastagotchi/packs/installed",
            "staged": "/var/lib/beastagotchi/packs/staged",
        }
        self.roots = {str(k): Path(v) for k, v in roots.items()}

    @staticmethod
    def _status(manifest_path: Path, origin: str, manifest: dict[str, Any]) -> tuple[str, bool]:
        enabled = bool(manifest.get("enabled_by_default", False)) if origin == "builtin" else False
        state = "staged" if origin == "staged" else "installed"
        fp = manifest_path.parent / "state.json"
        try:
            obj = json.loads(fp.read_text())
            if isinstance(obj, dict):
                enabled = bool(obj.get("enabled", enabled))
                requested = str(obj.get("state") or "").strip().lower()
                if requested in {"staged", "verified", "installed", "enabled", "disabled", "error"}:
                    state = requested
        except Exception:
            pass
        if origin != "staged" and enabled:
            state = "enabled"
        elif origin != "staged" and state == "enabled" and not enabled:
            state = "installed"
        return state, enabled

    def catalog(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for origin, root in self.roots.items():
            try:
                manifests = sorted(root.glob("*/manifest.json"))[:256]
            except Exception:
                manifests = []
            for fp in manifests:
                try:
                    obj = json.loads(fp.read_text(errors="replace"))
                    row = clean_manifest(obj, source_path=str(fp))
                    key = (origin, row["id"])
                    if key in seen:
                        continue
                    seen.add(key)
                    lifecycle, enabled = self._status(fp, origin, row)
                    row.update({"origin": origin, "lifecycle": lifecycle, "enabled": enabled})
                    rows.append(row)
                except Exception as exc:
                    errors.append({
                        "origin": origin,
                        "path": str(fp),
                        "error": f"{type(exc).__name__}: {exc}"[:320],
                    })
        priority = {"builtin": 0, "installed": 1, "staged": 2}
        rows.sort(key=lambda r: (priority.get(str(r.get("origin")), 9), str(r.get("label") or r.get("id")).lower()))
        return rows, errors

    def tick(self) -> dict[str, Any]:
        rows, errors = self.catalog()
        capabilities = set(self.state.get("capabilities.present", []) or [])
        active_ids = {
            str(r.get("id")) for r in rows
            if r.get("origin") != "staged" and r.get("lifecycle") in {"installed", "enabled", "disabled"}
        }
        enabled_ids = {str(r.get("id")) for r in rows if r.get("enabled")}
        for row in rows:
            req_caps = set(row.get("capabilities") or [])
            deps = set(row.get("dependencies") or [])
            conflicts = set(row.get("conflicts") or [])
            blockers = []
            missing_caps = sorted(req_caps - capabilities)
            missing_deps = sorted(deps - active_ids)
            present_conflicts = sorted(conflicts & enabled_ids)
            if missing_caps:
                blockers.append("missing capabilities: " + ", ".join(missing_caps))
            if missing_deps:
                blockers.append("missing dependencies: " + ", ".join(missing_deps))
            if present_conflicts:
                blockers.append("enabled conflicts: " + ", ".join(present_conflicts))
            row["missing_capabilities"] = missing_caps
            row["missing_dependencies"] = missing_deps
            row["present_conflicts"] = present_conflicts
            row["requirements_met"] = not blockers
            row["blockers"] = blockers
            row["version_compatibility_checked"] = False

        resource_counts = {name: sum(1 for r in rows if r.get("resource_class") == name) for name in RESOURCE_CLASSES}
        thermal_counts = {name: sum(1 for r in rows if r.get("thermal_class") == name) for name in THERMAL_CLASSES}
        return {
            "packs.count": len(rows),
            "packs.enabled_count": sum(1 for r in rows if r.get("enabled")),
            "packs.staged_count": sum(1 for r in rows if r.get("origin") == "staged"),
            "packs.compatible_count": sum(1 for r in rows if r.get("requirements_met")),
            "packs.error_count": len(errors),
            "packs.items": rows,
            "packs.errors": errors,
            "packs.resource_counts": resource_counts,
            "packs.thermal_counts": thermal_counts,
            "packs.executor_enabled": False,
            "packs.executor_reason": "v0.19 catalog-only foundation; installs/removals require a future transactional Action Broker",
        }
