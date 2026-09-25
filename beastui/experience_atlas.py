from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)

# Atlas intentionally avoids the legacy neon/grid palette. These are semantic
# proof colors only; a future Experience Pack/Theme will own the final styling.
_BG = (27, 31, 26)
_FIELD = (55, 61, 43)
_FIELD_2 = (72, 77, 51)
_PAPER = (218, 211, 177)
_MUTED = (159, 158, 128)
_INK = (235, 230, 201)
_ACCENT = (205, 177, 92)
_ALERT = (206, 119, 85)
_WATER = (75, 116, 121)


def _font(size: int = 12):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _ival(state: dict[str, Any], key: str, default=0) -> int:
    try:
        return int(float(state.get(key, default) or default))
    except Exception:
        return int(default)


def _fval(state: dict[str, Any], key: str, default=0.0) -> float:
    try:
        return float(state.get(key, default) or default)
    except Exception:
        return float(default)


def atlas_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    """Truth-only metadata used by the Atlas proof and regression tests."""
    gps_fix = bool(state.get("gps.fix"))
    route_points = _ival(state, "expedition.route_points")
    return {
        "gps_fix": gps_fix,
        "route_points": route_points,
        "draw_route": bool(gps_fix and route_points >= 2),
        "gps_status": "GPS FIX" if gps_fix else "GPS SEARCHING",
        "expedition_active": bool(state.get("expedition.active")),
        "ap_unique": _ival(state, "expedition.ap_unique", _ival(state, "wifi.ap_count")),
        "distance_m": _fval(state, "expedition.distance_m"),
        "duration_sec": _fval(state, "expedition.duration_sec"),
        "channel": _ival(state, "radio.primary.channel"),
        "band": str(state.get("radio.primary.band") or "?"),
        "stage": str(state.get("progression.stage") or "BEAST"),
        "level": _ival(state, "progression.level"),
        "expression": str(state.get("beast.expression") or state.get("pwnagotchi.mood") or "awake"),
    }


def _register(rt: SceneRuntime | None, spec: SceneLayerSpec) -> None:
    if rt is not None:
        rt.register(spec)


def _draw_contours(draw: ImageDraw.ImageDraw, phase: float) -> None:
    """Decorative terrain language. Explicitly not location or measured elevation."""
    for row in range(6):
        base_y = 55 + row * 31
        pts = []
        for x in range(8, 350, 8):
            y = base_y + math.sin((x * 0.027) + row * 0.8 + phase * 0.18) * (6 + row)
            pts.append((x, int(y)))
        draw.line(pts, fill=_FIELD_2, width=1)


def _draw_compass(draw: ImageDraw.ImageDraw, center=(305, 85), radius=28) -> None:
    cx, cy = center
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=_MUTED, width=1)
    draw.line((cx, cy-radius+4, cx, cy+radius-4), fill=_PAPER, width=1)
    draw.line((cx-radius+4, cy, cx+radius-4, cy), fill=_PAPER, width=1)
    draw.polygon([(cx, cy-radius+3), (cx-4, cy-10), (cx+4, cy-10)], fill=_ACCENT)
    draw.text((cx-4, cy-radius-13), "N", fill=_INK, font=_font(9))


def _draw_rf_observations(draw: ImageDraw.ImageDraw, state: dict[str, Any]) -> None:
    """Project real AP observations into a field diagram, not a geographic map."""
    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)]
    origin = (169, 156)
    draw.ellipse((origin[0]-5, origin[1]-5, origin[0]+5, origin[1]+5), fill=_ACCENT)
    for idx, ap in enumerate(aps[:12]):
        ch = _ival(ap, "channel", 1) if False else int(ap.get("channel") or 1)
        try:
            rssi = float(ap.get("rssi") or -90)
        except Exception:
            rssi = -90.0
        # Deterministic diagram placement from real channel/RSSI. It communicates
        # relative RF context only and is never labelled as physical position.
        angle = math.radians((ch * 23 + idx * 47) % 360)
        radius = max(24, min(112, int((abs(rssi) - 28) * 1.55)))
        x = int(origin[0] + math.cos(angle) * radius)
        y = int(origin[1] + math.sin(angle) * radius * 0.68)
        color = _WATER if bool(ap.get("handshake")) else _PAPER
        draw.ellipse((x-3, y-3, x+3, y+3), outline=color, fill=_BG)
        draw.line((origin[0], origin[1], x, y), fill=(68, 72, 54), width=1)


def _draw_beast_marker(draw: ImageDraw.ImageDraw, meta: dict[str, Any]) -> None:
    """Small supporting companion marker; Atlas is field-first, not portrait-first."""
    x, y = 22, 220
    draw.ellipse((x, y, x+66, y+62), fill=(43, 47, 39), outline=_ACCENT, width=2)
    draw.polygon([(x+10, y+10), (x+18, y-2), (x+25, y+12)], fill=(43, 47, 39), outline=_ACCENT)
    draw.polygon([(x+41, y+12), (x+49, y-2), (x+57, y+10)], fill=(43, 47, 39), outline=_ACCENT)
    draw.ellipse((x+21, y+27, x+25, y+31), fill=_INK)
    draw.ellipse((x+43, y+27, x+47, y+31), fill=_INK)
    draw.text((x+3, y+67), f"{meta['stage'].upper()} · LV {meta['level']}", fill=_INK, font=_font(9))


def render_atlas_home(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Render the first Atlas Home proof from canonical live/captured state."""
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:atlas:home", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    # Header / orientation.
    d.rectangle((0, 0, 479, 31), fill=(35, 39, 31))
    d.text((10, 7), "ATLAS", fill=_ACCENT, font=_font(15))
    d.text((70, 9), "FIELD EXPEDITION", fill=_MUTED, font=_font(10))
    dock = str(state.get("dock.state") or "field").upper()
    d.text((400, 9), dock, fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "atlas.header", "text", (0, 0, 480, 32),
        signals=("dock.state", "expedition.active"), update_class="live",
    ))

    # Dominant field canvas.
    d.rounded_rectangle((8, 38, 350, 278), radius=12, fill=_FIELD, outline=(92, 94, 67), width=1)
    _draw_contours(d, phase)
    d.text((18, 47), "FIELD CONTEXT", fill=_PAPER, font=_font(10))
    d.text((18, 62), "RF OBSERVATIONS · NOT GEOGRAPHIC POSITION", fill=_MUTED, font=_font(8))
    _draw_compass(d)
    _draw_rf_observations(d, state)
    _register(rt, SceneLayerSpec(
        "atlas.field", "environment", (8, 38, 350, 278),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))

    # No route is fabricated without fix + enough actual route points.
    if meta["draw_route"]:
        d.line((56, 192, 106, 171, 154, 176, 205, 138, 253, 145), fill=_ACCENT, width=3)
        d.text((20, 248), "ROUTE ACTIVE", fill=_ACCENT, font=_font(9))
    else:
        d.rounded_rectangle((18, 86, 116, 108), radius=6, fill=(43, 47, 39), outline=_ALERT)
        d.text((26, 92), meta["gps_status"], fill=_ALERT, font=_font(9))
        sats = _ival(state, "gps.satellites_used")
        d.text((20, 112), f"SATS USED {sats}", fill=_MUTED, font=_font(8))

    _draw_beast_marker(d, meta)
    _register(rt, SceneLayerSpec(
        "atlas.beast", "creature", (18, 210, 94, 306),
        signals=("progression.stage", "progression.level", "beast.expression", "pwnagotchi.mood"),
        update_class="live",
    ))

    # Edge instruments: compact and subordinate to the spatial canvas.
    x1, x2 = 360, 472
    panels = [
        ("RADIO", f"CH {meta['channel']}", meta["band"]),
        ("DISCOVERY", f"{meta['ap_unique']} UNIQUE", f"{_ival(state, 'wifi.ap_count')} NEARBY"),
        ("JOURNEY", f"{meta['distance_m']:.0f} m", f"{meta['duration_sec']:.0f} sec"),
        ("SYSTEM", f"{_fval(state, 'system.temp.cpu_c'):.0f} C", str(state.get("governor.mode") or "?")),
    ]
    y = 42
    for title, primary, secondary in panels:
        d.rounded_rectangle((x1, y, x2, y+50), radius=8, fill=(38, 43, 35), outline=(87, 89, 65))
        d.text((x1+8, y+6), title, fill=_MUTED, font=_font(8))
        d.text((x1+8, y+20), primary, fill=_INK, font=_font(12))
        d.text((x1+8, y+36), secondary, fill=_ACCENT, font=_font(8))
        y += 58

    _register(rt, SceneLayerSpec(
        "atlas.radio", "instrument", (360, 42, 472, 92),
        signals=("radio.primary.channel", "radio.primary.band"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.discovery", "instrument", (360, 100, 472, 150),
        signals=("expedition.ap_unique", "wifi.ap_count"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.journey", "instrument", (360, 158, 472, 208),
        signals=("expedition.distance_m", "expedition.duration_sec"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.system", "instrument", (360, 216, 472, 266),
        signals=("system.temp.cpu_c", "governor.mode"), update_class="live",
    ))

    # Journey strip is not a generic nav bar; it summarizes the current expedition.
    d.rectangle((104, 286, 472, 313), fill=(38, 43, 35))
    active = "ACTIVE" if meta["expedition_active"] else "IDLE"
    d.text((114, 294), f"EXPEDITION {active}", fill=_ACCENT if meta["expedition_active"] else _MUTED, font=_font(9))
    d.text((222, 294), f"DISC {meta['ap_unique']}", fill=_INK, font=_font(9))
    d.text((296, 294), f"CAP +{_ival(state, 'expedition.captures_delta')}", fill=_INK, font=_font(9))
    d.text((372, 294), f"XP +{_ival(state, 'expedition.xp_delta')}", fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "atlas.expedition_strip", "timeline", (104, 286, 472, 314),
        signals=("expedition.active", "expedition.ap_unique", "expedition.captures_delta", "expedition.xp_delta"),
        update_class="live",
    ))

    return im
