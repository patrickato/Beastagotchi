from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .packs import PACK_TYPES, RESOURCE_CLASSES, THERMAL_CLASSES
from .update_sources import normalize_repo


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_ASSET_RE = re.compile(r"^[A-Za-z0-9._*?+()\[\]-]{1,180}$")


class DepotCatalogError(ValueError):
    pass


def _strings(value: Any, limit: int = 32, width: int = 64) -> list[str]:
    if not isinstance(value, list):
        return []
    out = []
    for x in value[:limit]:
        s = str(x).strip()[:width]
        if s and s not in out:
            out.append(s)
    return out


def clean_depot_entry(obj: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise DepotCatalogError("catalog entry must be an object")
    pack_id = str(obj.get("id") or "").strip().lower()
    if not _ID_RE.fullmatch(pack_id):
        raise DepotCatalogError("invalid pack id")
    label = str(obj.get("label") or "").strip()
    if not label:
        raise DepotCatalogError("pack label is required")
    pack_type = str(obj.get("pack_type") or "").strip().lower()
    if pack_type not in PACK_TYPES:
        raise DepotCatalogError("unsupported pack type")
    version = str(obj.get("version") or "").strip()[:48]
    if not version:
        raise DepotCatalogError("pack version is required")

    resource = str(obj.get("resource_class") or "low").strip().lower()
    thermal = str(obj.get("thermal_class") or "static").strip().lower()
    if resource not in RESOURCE_CLASSES:
        raise DepotCatalogError("invalid resource_class")
    if thermal not in THERMAL_CLASSES:
        raise DepotCatalogError("invalid thermal_class")

    source = obj.get("source") if isinstance(obj.get("source"), dict) else {}
    source_type = str(source.get("type") or "").strip().lower()
    if source_type != "github_release":
        raise DepotCatalogError("v1 Depot entries must use github_release sources")
    repository = normalize_repo(str(source.get("repository") or source.get("url") or ""))
    if not repository:
        raise DepotCatalogError("invalid GitHub repository")
    asset = str(source.get("asset") or "").strip()
    if not _ASSET_RE.fullmatch(asset) or not asset.lower().endswith((".zip", ".tgz", ".tar.gz")):
        raise DepotCatalogError("source.asset must identify a Beast Pack archive")
    checksum_asset = str(source.get("sha256_asset") or "").strip()
    if checksum_asset and not _ASSET_RE.fullmatch(checksum_asset):
        raise DepotCatalogError("invalid sha256_asset pattern")

    compatibility = obj.get("compatibility") if isinstance(obj.get("compatibility"), dict) else {}
    return {
        "id": pack_id,
        "label": label[:80],
        "version": version,
        "pack_type": pack_type,
        "description": str(obj.get("description") or "").strip()[:320],
        "author": str(obj.get("author") or "").strip()[:96],
        "license": str(obj.get("license") or "").strip()[:64],
        "tags": _strings(obj.get("tags"), 24, 32),
        "resource_class": resource,
        "thermal_class": thermal,
        "compatibility": {
            "beast_min": str(compatibility.get("beast_min") or "")[:48],
            "beast_max": str(compatibility.get("beast_max") or "")[:48],
            "pwnagotchi_min": str(compatibility.get("pwnagotchi_min") or "")[:48],
            "pwnagotchi_max": str(compatibility.get("pwnagotchi_max") or "")[:48],
        },
        "source": {
            "type": "github_release",
            "repository": repository,
            "asset": asset,
            "sha256_asset": checksum_asset,
        },
        "featured": bool(obj.get("featured", False)),
    }


class DepotCatalog:
    """Bounded, read-only Beast Depot metadata parser.

    A catalog entry is discoverability metadata only. It does not grant source
    trust and cannot bypass TrustedSourcePolicy or the Pack intake/install gates.
    """

    def __init__(self, path: str | Path, *, max_bytes: int = 1024 * 1024, max_entries: int = 512) -> None:
        self.path = Path(path)
        self.max_bytes = int(max_bytes)
        self.max_entries = int(max_entries)

    def load(self) -> dict[str, Any]:
        raw = self.path.read_bytes()
        if len(raw) > self.max_bytes:
            raise DepotCatalogError("Depot catalog exceeds size limit")
        try:
            obj = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DepotCatalogError(f"invalid Depot catalog JSON: {exc}") from exc
        if not isinstance(obj, dict) or int(obj.get("schema") or 0) != 1:
            raise DepotCatalogError("unsupported Depot catalog schema")
        rows = obj.get("packs")
        if not isinstance(rows, list):
            raise DepotCatalogError("Depot catalog packs must be a list")

        items = []
        errors = []
        seen = set()
        for idx, raw_entry in enumerate(rows[: self.max_entries]):
            try:
                row = clean_depot_entry(raw_entry)
                if row["id"] in seen:
                    raise DepotCatalogError("duplicate pack id")
                seen.add(row["id"])
                items.append(row)
            except Exception as exc:
                errors.append({"index": idx, "error": f"{type(exc).__name__}: {exc}"[:240]})
        return {
            "schema": 1,
            "channel": str(obj.get("channel") or "stable").strip().lower()[:32],
            "generated_at": obj.get("generated_at"),
            "items": items,
            "errors": errors,
            "count": len(items),
            "error_count": len(errors),
            "grants_trust": False,
            "installs_packs": False,
        }
