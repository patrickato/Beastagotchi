from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)
_BG = (40, 37, 31)
_SOIL = (75, 65, 49)
_LEAF = (95, 124, 82)
_LEAF_2 = (125, 150, 98)
_WARM = (219, 186, 116)
_INK = (242, 232, 201)
_MUTED = (169, 159, 128)
_HEALTH = (133, 179, 119)


def _font(size=11):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _f(state: dict[str, Any], key: str, default=0.0) -> float:
    try:
        return float(state.get(key, default) or default)
    except Exception:
        return float(default)


def _i(state: dict[str, Any], key: str, default=0) -> int:
    try:
        return int(float(state.get(key, default) or default))
    except Exception:
        return int(default)


def habitat_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": str(state.get("progression.stage") or "Beast"),
        "level": _i(state, "progression.level"),
        "progress_pct": _f(state, "progression.level_progress_pct"),
        "mood": str(state.get("pwnagotchi.mood") or "awake"),
        "expression": str(state.get("beast.expression") or ""),
        "discoveries": _i(state, "wifi.encounters.session_unique", _i(state, "wifi.ap_count")),
        "lifetime": _i(state, "wifi.encounters.lifetime_unique"),
        "captures": _i(state, "captures.total"),
        "health": str(state.get("health.core.state") or "unknown"),
        "expedition_active": bool(state.get("expedition.active")),
    }


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _draw_habitat(draw, phase):
    # Organic backdrop. Decorative and intentionally not telemetry.
    for radius, tone in ((130, _SOIL), (105, (67, 72, 51)), (82, (58, 68, 50))):
        cx = 238 + int(math.sin(phase * 0.2 + radius) * 2)
        cy = 157
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=tone)
    for x, y, r in ((55,72,22),(414,73,25),(52,244,28),(425,239,20),(102,45,14),(374,270,16)):
        draw.ellipse((x-r, y-r, x+r, y+r), outline=_LEAF, width=2)


def _draw_creature(draw, meta):
    cx, cy = 240, 150
    # Deliberately enormous creature footprint.
    draw.ellipse((135, 65, 345, 255), fill=(46, 48, 39), outline=_WARM, width=3)
    draw.polygon([(158,92),(183,40),(205,94)], fill=(46,48,39), outline=_WARM)
    draw.polygon([(275,94),(299,40),(323,92)], fill=(46,48,39), outline=_WARM)
    draw.ellipse((190, 130, 205, 145), fill=_INK)
    draw.ellipse((275, 130, 290, 145), fill=_INK)
    if meta["mood"].lower() in {"awake","happy","excited"}:
        draw.arc((203,142,278,196), 18, 162, fill=_LEAF_2, width=3)
    else:
        draw.line((212,177,268,177), fill=_LEAF_2, width=3)
    draw.text((195, 211), meta["stage"].upper(), fill=_INK, font=_font(14))
    draw.text((219, 232), f"LV {meta['level']}", fill=_WARM, font=_font(11))


def render_habitat_home(state: dict[str, Any], *, phase: float = 0.0,
                        scene_runtime: SceneRuntime | None = None) -> Image.Image:
    state = dict(state or {})
    meta = habitat_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:habitat:home", theme_id="experience.habitat")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_habitat(d, phase)
    _register(rt, SceneLayerSpec(
        "habitat.environment", "environment", (0, 0, 480, 320),
        update_class="ambient", decorative=True,
    ))

    d.text((12, 10), "HABITAT", fill=_LEAF_2, font=_font(14))
    health = meta["health"].upper()
    d.text((405, 11), health, fill=_HEALTH if health=="HEALTHY" else _WARM, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.health", "text", (390, 5, 472, 28),
        signals=("health.core.state",), update_class="live",
    ))

    _draw_creature(d, meta)
    _register(rt, SceneLayerSpec(
        "habitat.beast", "creature", (130, 40, 350, 260),
        signals=("progression.stage","progression.level","pwnagotchi.mood","beast.expression"),
        update_class="live",
    ))

    # Context is distributed as habitat objects, not dashboard panels.
    d.ellipse((18, 48, 112, 142), fill=(50,49,40), outline=_LEAF)
    d.text((38, 69), "TODAY", fill=_MUTED, font=_font(8))
    d.text((39, 87), str(meta["discoveries"]), fill=_INK, font=_font(22))
    d.text((30, 116), "DISCOVERIES", fill=_LEAF_2, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.discovery", "instrument", (18,48,112,142),
        signals=("wifi.encounters.session_unique","wifi.ap_count"), update_class="live",
    ))

    d.ellipse((370, 55, 462, 147), fill=(50,49,40), outline=_LEAF)
    d.text((391, 74), "MEMORY", fill=_MUTED, font=_font(8))
    d.text((393, 91), str(meta["lifetime"]), fill=_INK, font=_font(20))
    d.text((387, 120), "ENCOUNTERS", fill=_LEAF_2, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.memory", "instrument", (370,55,462,147),
        signals=("wifi.encounters.lifetime_unique",), update_class="live",
    ))

    # Growth vine is backed by genuine level progress.
    x1,y1,x2,y2 = 28, 188, 104, 272
    d.arc((x1,y1,x2,y2), 90, 270, fill=_LEAF, width=4)
    pct=max(0.0,min(100.0,meta["progress_pct"]))
    end_y=int(y2 - (y2-y1)*(pct/100.0))
    d.ellipse((43,end_y-6,55,end_y+6), fill=_WARM)
    d.text((24, 278), f"GROWTH {pct:.0f}%", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.growth", "instrument", (18,180,112,296),
        signals=("progression.level_progress_pct",), update_class="live",
    ))

    # Expedition is a small environmental cue, not a mode banner.
    if meta["expedition_active"]:
        d.ellipse((394, 202, 449, 257), outline=_WARM, width=2)
        d.text((407, 219), "OUT", fill=_WARM, font=_font(10))
        d.text((400, 235), "ROAMING", fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "habitat.expedition", "ambient", (388,196,456,264),
        signals=("expedition.active",), update_class="live",
    ))

    # Truth strip remains deliberately small.
    d.rounded_rectangle((142, 277, 338, 310), radius=12, fill=(48,47,39), outline=_SOIL)
    d.text((158, 287), meta["mood"].upper(), fill=_INK, font=_font(9))
    d.text((230, 287), f"CAP {meta['captures']}", fill=_INK, font=_font(9))
    d.text((288, 287), meta["expression"].replace("-"," ").upper()[:10], fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "habitat.truth", "text", (142,277,338,310),
        signals=("pwnagotchi.mood","captures.total","beast.expression"), update_class="live",
    ))
    return im
