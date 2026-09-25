from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class PrototypeRegion:
    id: str
    kind: str
    bounds: tuple[int, int, int, int]
    weight: int = 1


@dataclass(frozen=True)
class PrototypeSilhouette:
    experience_id: str
    regions: tuple[PrototypeRegion, ...]


PROTOTYPE_SILHOUETTES: dict[str, PrototypeSilhouette] = {
    "atlas": PrototypeSilhouette("atlas", (
        PrototypeRegion("field_canvas", "canvas", (8, 34, 350, 278), 5),
        PrototypeRegion("creature_marker", "creature", (24, 204, 114, 292), 2),
        PrototypeRegion("heading", "instrument", (360, 44, 472, 112), 2),
        PrototypeRegion("nearby", "instrument", (360, 120, 472, 196), 2),
        PrototypeRegion("journey", "timeline", (124, 284, 470, 314), 1),
    )),
    "forge": PrototypeSilhouette("forge", (
        PrototypeRegion("compute", "module", (12, 40, 150, 142), 3),
        PrototypeRegion("radio", "module", (164, 40, 304, 142), 3),
        PrototypeRegion("power", "module", (318, 40, 468, 142), 3),
        PrototypeRegion("storage", "module", (12, 156, 228, 270), 3),
        PrototypeRegion("doctor", "module", (242, 156, 468, 270), 4),
        PrototypeRegion("machine_bus", "bus", (60, 276, 420, 306), 1),
    )),
    "observatory": PrototypeSilhouette("observatory", (
        PrototypeRegion("primary_plot", "plot", (10, 38, 336, 184), 5),
        PrototypeRegion("secondary_plot", "plot", (10, 196, 336, 284), 3),
        PrototypeRegion("observer", "creature", (350, 48, 468, 154), 2),
        PrototypeRegion("provenance", "instrument", (350, 168, 468, 284), 2),
    )),
    "habitat": PrototypeSilhouette("habitat", (
        PrototypeRegion("creature", "creature", (86, 46, 394, 264), 6),
        PrototypeRegion("mood", "ambient", (14, 46, 76, 116), 1),
        PrototypeRegion("memory", "ambient", (404, 48, 468, 132), 1),
        PrototypeRegion("growth", "ambient", (18, 204, 82, 270), 1),
        PrototypeRegion("truth_strip", "instrument", (112, 278, 368, 310), 1),
    )),
    "monolith": PrototypeSilhouette("monolith", (
        PrototypeRegion("focal", "creature", (132, 54, 348, 248), 6),
        PrototypeRegion("primary_fact", "instrument", (174, 258, 306, 286), 1),
        PrototypeRegion("status", "instrument", (196, 294, 284, 310), 1),
    )),
}


def silhouette_spec(experience_id: str) -> PrototypeSilhouette:
    key = str(experience_id or "").strip().lower()
    if key not in PROTOTYPE_SILHOUETTES:
        raise KeyError(key)
    return PROTOTYPE_SILHOUETTES[key]


def render_silhouette(
    experience_id: str,
    *,
    size: tuple[int, int] = (480, 320),
) -> Image.Image:
    """Render a grayscale structural proof, intentionally not a final UI."""
    spec = silhouette_spec(experience_id)
    logical_w, logical_h = 480, 320
    out = Image.new("L", (logical_w, logical_h), 245)
    draw = ImageDraw.Draw(out)

    # Structural chrome is deliberately minimal so the composition dominates.
    draw.rectangle((0, 0, logical_w - 1, logical_h - 1), outline=20, width=2)
    draw.line((0, 28, logical_w, 28), fill=80, width=1)

    tones = {
        "canvas": 205,
        "creature": 55,
        "instrument": 135,
        "module": 155,
        "plot": 190,
        "timeline": 115,
        "ambient": 220,
        "bus": 105,
    }
    for region in spec.regions:
        fill = tones.get(region.kind, 170)
        x1, y1, x2, y2 = region.bounds
        if region.kind == "creature":
            draw.ellipse((x1, y1, x2, y2), fill=fill, outline=25, width=2)
        elif region.kind == "bus":
            draw.rounded_rectangle((x1, y1, x2, y2), radius=12, fill=fill, outline=35, width=2)
        else:
            radius = 12 if region.kind in {"module", "instrument"} else 5
            draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=35, width=2)

    if size != (logical_w, logical_h):
        out = out.resize(size, Image.Resampling.NEAREST)
    return out.convert("RGB")


def render_all_silhouettes(output_dir: str | Path) -> list[Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for experience_id in PROTOTYPE_SILHOUETTES:
        path = root / f"{experience_id}.png"
        render_silhouette(experience_id).save(path)
        paths.append(path)
    return paths


def occupancy_signature(experience_id: str) -> tuple[int, int, int]:
    """Simple structural signature for tests/diagnostics, not visual scoring."""
    spec = silhouette_spec(experience_id)
    total_area = 0
    creature_area = 0
    regions = len(spec.regions)
    for region in spec.regions:
        x1, y1, x2, y2 = region.bounds
        area = max(0, x2 - x1) * max(0, y2 - y1)
        total_area += area
        if region.kind == "creature":
            creature_area += area
    return total_area, creature_area, regions
