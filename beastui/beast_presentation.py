from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Any, Mapping

from PIL import Image, ImageChops, ImageEnhance, ImageOps

from .concept_creatures import concept_creature_scene


@dataclass(frozen=True)
class BeastVisualIdentity:
    name: str
    kind: str
    lineage: str
    generation: int
    stage: str
    level: int | None
    expression: str
    mood: str
    aura: str


@dataclass(frozen=True)
class BeastPalette:
    body_dark: tuple[int, int, int]
    body_mid: tuple[int, int, int]
    highlight: tuple[int, int, int]
    accent: tuple[int, int, int]
    alert: tuple[int, int, int]
    dim: tuple[int, int, int]

    @classmethod
    def atlas_default(cls) -> "BeastPalette":
        return cls(
            body_dark=(14, 22, 20),
            body_mid=(77, 137, 139),
            highlight=(226, 219, 183),
            accent=(214, 181, 83),
            alert=(213, 112, 77),
            dim=(86, 98, 76),
        )


def _int(value: Any) -> int | None:
    try:
        return None if value is None or value == "" else int(value)
    except (TypeError, ValueError):
        return None


def resolve_beast_identity(state: Mapping[str, Any]) -> BeastVisualIdentity:
    stage = str(state.get("progression.stage") or state.get("beast.stage") or "Beast").strip() or "Beast"
    name = str(state.get("progression.beast.name") or state.get("beast.name") or stage).strip() or stage
    kind = str(state.get("progression.beast.kind") or state.get("beast.kind") or "beast").strip().lower() or "beast"
    lineage = str(state.get("progression.beast.lineage") or "legacy").strip() or "legacy"
    generation = _int(state.get("progression.beast.generation")) or 0
    expression = str(state.get("beast.expression") or state.get("pwnagotchi.mood") or "awake").strip().lower() or "awake"
    mood = str(state.get("pwnagotchi.mood") or expression).strip().lower() or "awake"
    aura = str(state.get("progression.aura") or "none").strip().lower() or "none"
    return BeastVisualIdentity(
        name=name,
        kind=kind,
        lineage=lineage,
        generation=max(0, generation),
        stage=stage,
        level=_int(state.get("progression.level")),
        expression=expression,
        mood=mood,
        aura=aura,
    )


def _stage_presence(identity: BeastVisualIdentity) -> float:
    # Presentation scale, not literal body size. Keep early stages prominent while
    # allowing later stages to feel more imposing without changing layout geometry.
    stage = identity.stage.strip().lower()
    if identity.kind == "monster":
        return 1.00
    if stage in {"hatchling", "cub", "origin"}:
        return 0.91
    if stage in {"scout", "awakened"}:
        return 0.95
    if stage in {"stalker", "morph", "adapted"}:
        return 0.98
    return 1.00


def _reaction_color(identity: BeastVisualIdentity, palette: BeastPalette) -> tuple[int, int, int]:
    if identity.expression in {"warning", "overheated", "hunting", "angry", "intense", "fault"}:
        return palette.alert
    if identity.expression in {"gps-searching", "focused", "reconnecting", "waiting"}:
        return palette.body_mid
    return palette.accent


@lru_cache(maxsize=64)
def _prepared_concept(
    concept_style: str,
    width: int,
    height: int,
    body_dark: tuple[int, int, int],
    body_mid: tuple[int, int, int],
    highlight: tuple[int, int, int],
) -> Image.Image | None:
    """Cache decode, resize, feather and palette mapping; never repeat per frame."""
    art = concept_creature_scene(concept_style, int(width), int(height), edge_feather=8)
    if art is None:
        return None
    alpha = art.getchannel("A")
    gray = ImageOps.grayscale(art.convert("RGB"))
    tinted = ImageOps.colorize(
        gray,
        black=body_dark,
        white=highlight,
        mid=body_mid,
        midpoint=138,
    )
    tinted.putalpha(alpha)
    return tinted


def draw_beast_presence(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    state: Mapping[str, Any],
    phase: float,
    *,
    palette: BeastPalette | None = None,
    concept_style: str = "classic",
    opacity: int = 250,
    traits: Mapping[str, Any] | None = None,
) -> BeastVisualIdentity:
    """Render the active Beast as a scene layer, not a dashboard icon.

    `traits` is deliberately an optional presentation input. The current Core
    publishes stable identity/progression keys; future lineage/Monster appearance
    traits can feed this seam without coupling an Experience to roster storage.
    """
    palette = palette or BeastPalette.atlas_default()
    identity = resolve_beast_identity(state)
    x1, y1, x2, y2 = (int(v) for v in box)
    w, h = max(1, x2 - x1), max(1, y2 - y1)

    # Cheap aura geometry sits behind the cached raster and reacts to existing
    # progression/expression truth. It remains decorative, never telemetry.
    draw = __import__("PIL.ImageDraw", fromlist=["ImageDraw"]).Draw(canvas)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    react = _reaction_color(identity, palette)
    aura = str((traits or {}).get("aura") or identity.aura or "none").lower()
    if aura not in {"", "none", "off"} or identity.expression in {"focused", "gps-searching", "hunting", "excited"}:
        for idx in range(3):
            r = int(min(w, h) * (0.34 + idx * 0.09))
            start = int((phase * 23 + idx * 71) % 360)
            draw.arc((cx-r, cy-r, cx+r, cy+r), start, start + 78, fill=palette.dim, width=1)
        if aura in {"spark", "orbital", "scan", "glow"}:
            for idx in range(5):
                a = phase * 0.32 + idx * (math.tau / 5)
                rx, ry = w * 0.39, h * 0.36
                px = int(cx + math.cos(a) * rx)
                py = int(cy + math.sin(a) * ry)
                draw.ellipse((px-1, py-1, px+1, py+1), fill=react)

    presence = _stage_presence(identity)
    target_w, target_h = max(1, int(w * presence)), max(1, int(h * presence))
    prepared = _prepared_concept(
        str(concept_style).lower(), target_w, target_h,
        palette.body_dark, palette.body_mid, palette.highlight,
    )
    if prepared is None:
        return identity

    # Per-frame work stays intentionally cheap: copy + luminance + alpha + paste.
    img = prepared.copy()
    pulse = 0.975 + 0.025 * (0.5 + 0.5 * math.sin(float(phase) * 1.15))
    img = ImageEnhance.Brightness(img).enhance(pulse)
    if opacity < 255:
        a = img.getchannel("A").point(lambda v: int(v * max(0, min(255, opacity)) / 255))
        img.putalpha(a)
    px = x1 + (w - img.width) // 2
    # breathing/bob is translation only—no per-frame resample
    bob = int(round(math.sin(float(phase) * 0.72) * 1.5))
    py = y1 + (h - img.height) // 2 + bob
    base = canvas.convert("RGBA")
    base.alpha_composite(img, (px, py))
    canvas.paste(base.convert("RGB"))

    # Expression and aura currently affect the surrounding presentation layer.
    # Pack/lineage renderers may later supply explicit eye animation metadata.
    return identity


def presentation_snapshot(identity: BeastVisualIdentity) -> dict[str, Any]:
    return {
        "name": identity.name,
        "kind": identity.kind,
        "lineage": identity.lineage,
        "generation": identity.generation,
        "stage": identity.stage,
        "level": identity.level,
        "expression": identity.expression,
        "mood": identity.mood,
        "aura": identity.aura,
    }
