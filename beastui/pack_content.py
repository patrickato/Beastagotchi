from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .customization import validate_custom_boards, validate_dashboard_widgets

_SAFE_PART = re.compile(r"[^a-z0-9_-]+")


def _enabled_pack_dirs(installed_root: str | Path, pack_type: str):
    root = Path(installed_root)
    try:
        packs = sorted(root.iterdir())
    except OSError:
        return []
    out = []
    for pack in packs:
        if not pack.is_dir():
            continue
        try:
            state = json.loads((pack / "state.json").read_text())
            manifest = json.loads((pack / "manifest.json").read_text())
            if not bool(state.get("enabled")):
                continue
            if str(manifest.get("pack_type") or manifest.get("type") or "").lower() != pack_type:
                continue
            out.append((pack, manifest))
        except Exception:
            continue
    return out


def _scoped_id(pack_id: str, local_id: str) -> str:
    p = _SAFE_PART.sub("_", str(pack_id).lower()).strip("_") or "pack"
    l = _SAFE_PART.sub("_", str(local_id).lower()).strip("_") or "item"
    raw = f"pack_{p}_{l}"
    if len(raw) <= 40:
        return raw
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return f"{raw[:31]}_{digest}"


def discover_enabled_pack_boards(
    installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
    *,
    catalog: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Discover read-only dashboard destinations supplied by enabled Board Packs."""
    out: list[dict[str, Any]] = []
    used: set[str] = set()
    for pack, manifest in _enabled_pack_dirs(installed_root, "board"):
        pack_id = str(manifest.get("id") or pack.name)
        for fp in sorted((pack / "boards").glob("*.json"))[:64]:
            try:
                obj = json.loads(fp.read_text())
                rows = obj.get("boards") if isinstance(obj, dict) and isinstance(obj.get("boards"), list) else [obj]
                for row in validate_custom_boards(rows, catalog=catalog):
                    local_id = str(row.get("id") or fp.stem)
                    bid = _scoped_id(pack_id, local_id)
                    if bid in used:
                        continue
                    used.add(bid)
                    out.append({
                        **row,
                        "id": bid,
                        "local_id": local_id,
                        "source_pack": pack_id,
                        "source_file": str(fp),
                        "readonly": True,
                        "source_kind": "pack_board",
                    })
            except Exception:
                continue
    return out


def discover_enabled_pack_layouts(
    installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
    *,
    catalog: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Discover reusable Board templates supplied by enabled Layout Packs."""
    out: list[dict[str, Any]] = []
    used: set[str] = set()
    for pack, manifest in _enabled_pack_dirs(installed_root, "layout"):
        pack_id = str(manifest.get("id") or pack.name)
        for fp in sorted((pack / "layouts").glob("*.json"))[:64]:
            try:
                obj = json.loads(fp.read_text())
                rows = obj.get("layouts") if isinstance(obj, dict) and isinstance(obj.get("layouts"), list) else [obj]
                for idx, raw in enumerate(rows[:64]):
                    if not isinstance(raw, dict):
                        continue
                    local_id = str(raw.get("id") or f"{fp.stem}_{idx+1}")
                    lid = _scoped_id(pack_id, local_id)
                    if lid in used:
                        continue
                    widgets = validate_dashboard_widgets(raw.get("widgets") or [], catalog=catalog)
                    if not widgets:
                        continue
                    used.add(lid)
                    out.append({
                        "id": lid,
                        "local_id": local_id,
                        "label": str(raw.get("label") or local_id).strip()[:22] or local_id[:22],
                        "description": str(raw.get("description") or "").strip()[:160],
                        "widgets": widgets,
                        "source_pack": pack_id,
                        "source_file": str(fp),
                        "readonly": True,
                        "source_kind": "pack_layout",
                    })
            except Exception:
                continue
    return out
