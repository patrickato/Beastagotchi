from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
RENDERERS = {"glyph", "vector"}
COLOR_ROLES = {
    "bg", "ink", "panel", "panel2", "edge", "grid", "primary", "secondary",
    "accent", "info", "warn", "danger", "text", "dim", "scanline",
}
PRIMITIVES = {"line", "ellipse", "rectangle", "rounded_rectangle", "polygon", "arc"}


class FacePackError(ValueError):
    pass


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        return float(default)
    return max(0.0, min(1000.0, v))


def _role(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    value = str(value).strip().lower()
    return value if value in COLOR_ROLES else default


def _clean_box(value: Any) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise FacePackError("primitive box must contain four normalized values")
    return [_safe_number(x) for x in value]


def _clean_points(value: Any) -> list[list[float]]:
    if not isinstance(value, list) or not 2 <= len(value) <= 16:
        raise FacePackError("primitive points must contain 2-16 points")
    out = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise FacePackError("each primitive point must contain x and y")
        out.append([_safe_number(point[0]), _safe_number(point[1])])
    return out


def _clean_primitive(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise FacePackError("vector primitive must be an object")
    kind = str(obj.get("type") or "").strip().lower()
    if kind not in PRIMITIVES:
        raise FacePackError(f"unsupported vector primitive: {kind or 'missing'}")
    row: dict[str, Any] = {
        "type": kind,
        "stroke": _role(obj.get("stroke"), "primary"),
        "fill": _role(obj.get("fill"), None),
        "width": max(1, min(8, int(obj.get("width") or 1))),
    }
    if kind in {"ellipse", "rectangle", "rounded_rectangle", "arc"}:
        row["box"] = _clean_box(obj.get("box"))
    if kind in {"line", "polygon"}:
        row["points"] = _clean_points(obj.get("points"))
    if kind == "rounded_rectangle":
        row["radius"] = max(0.0, min(250.0, _safe_number(obj.get("radius"), 40.0)))
    if kind == "arc":
        try:
            row["start"] = float(obj.get("start", 0.0)) % 360.0
            row["end"] = float(obj.get("end", 180.0)) % 360.0
        except Exception as exc:
            raise FacePackError("arc start/end must be numeric") from exc
    return row


def clean_face_profile(
    obj: dict[str, Any],
    *,
    source_pack: str = "",
    source_file: str = "",
) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise FacePackError("face definition must be an object")
    local_id = str(obj.get("id") or "").strip().lower()
    if not _ID_RE.fullmatch(local_id):
        raise FacePackError("invalid face id")
    label = str(obj.get("label") or local_id).strip()[:64] or local_id
    renderer = str(obj.get("renderer") or "").strip().lower()
    if renderer not in RENDERERS:
        raise FacePackError("face renderer must be glyph or vector")
    fallback = str(obj.get("fallback") or "awake").strip().lower()[:32] or "awake"
    background = str(obj.get("background") or "transparent").strip().lower()
    if background not in {"transparent", "panel"}:
        background = "transparent"
    expressions = obj.get("expressions")
    if not isinstance(expressions, dict) or not expressions:
        raise FacePackError("face expressions must be a non-empty object")
    if len(expressions) > 64:
        raise FacePackError("face definition contains too many expressions")

    cleaned: dict[str, Any] = {}
    if renderer == "glyph":
        for mood, glyph in expressions.items():
            mood = str(mood).strip().lower()[:32]
            if not mood or not isinstance(glyph, str):
                continue
            cleaned[mood] = glyph[:64]
        if not cleaned:
            raise FacePackError("glyph face contains no usable expressions")
    else:
        for mood, primitives in expressions.items():
            mood = str(mood).strip().lower()[:32]
            if not mood or not isinstance(primitives, list) or not primitives:
                continue
            if len(primitives) > 64:
                raise FacePackError("face expression contains too many vector primitives")
            cleaned[mood] = [_clean_primitive(x) for x in primitives]
        if not cleaned:
            raise FacePackError("vector face contains no usable expressions")

    if fallback not in cleaned:
        fallback = "awake" if "awake" in cleaned else next(iter(cleaned))

    font_ratio = obj.get("font_size_ratio", 0.30)
    try:
        font_ratio = max(0.12, min(0.65, float(font_ratio)))
    except Exception:
        font_ratio = 0.30

    return {
        "local_id": local_id,
        "label": label,
        "renderer": renderer,
        "fallback": fallback,
        "background": background,
        "color_role": _role(obj.get("color_role"), "primary"),
        "font_size_ratio": font_ratio,
        "expressions": cleaned,
        "source_pack": str(source_pack or ""),
        "source_file": str(source_file or ""),
    }


def _runtime_id(pack_id: str, local_id: str) -> str:
    raw = f"pack_{pack_id}_{local_id}".lower()
    safe = re.sub(r"[^a-z0-9_-]+", "_", raw).strip("_")
    if len(safe) <= 64:
        return safe
    digest = hashlib.sha256(safe.encode()).hexdigest()[:8]
    return f"{safe[:55]}_{digest}"


def discover_enabled_face_profiles(
    installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
) -> dict[str, dict[str, Any]]:
    root = Path(installed_root)
    out: dict[str, dict[str, Any]] = {}
    try:
        packs = sorted(root.iterdir())
    except OSError:
        return out
    for pack in packs:
        if not pack.is_dir():
            continue
        try:
            state = json.loads((pack / "state.json").read_text())
            manifest = json.loads((pack / "manifest.json").read_text())
            if not bool(state.get("enabled")):
                continue
            if str(manifest.get("pack_type") or manifest.get("type") or "").lower() != "face":
                continue
            pack_id = str(manifest.get("id") or pack.name)
            for fp in sorted((pack / "faces").glob("*.json"))[:64]:
                obj = json.loads(fp.read_text())
                profile = clean_face_profile(obj, source_pack=pack_id, source_file=str(fp))
                if profile["local_id"] != fp.stem:
                    continue
                rid = _runtime_id(pack_id, profile["local_id"])
                if rid not in out:
                    out[rid] = {**profile, "id": rid}
        except Exception:
            continue
    return out
