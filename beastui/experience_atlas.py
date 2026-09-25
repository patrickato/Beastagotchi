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


def _edge_metric(draw, y, label, primary, secondary="", *, accent=False):
    """Notebook-margin instrument: no card container, just field annotation."""
    draw.line((412, y, 470, y), fill=(82, 84, 62), width=1)
    draw.text((414, y+5), label, fill=_MUTED, font=_font(7))
    draw.text((414, y+18), primary, fill=_ACCENT if accent else _INK, font=_font(11))
    if secondary:
        draw.text((414, y+34), secondary, fill=_MUTED, font=_font(7))


def render_atlas_home(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Atlas Home as a field notebook/canvas with edge annotations, not dashboard cards."""
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:atlas:home", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    # Header reads like an expedition folio tab.
    d.rectangle((0, 0, 479, 31), fill=(34, 38, 30))
    d.text((10, 7), "ATLAS", fill=_ACCENT, font=_font(15))
    d.text((70, 9), "FIELD EXPEDITION // LIVE NOTEBOOK", fill=_MUTED, font=_font(8))
    dock = str(state.get("dock.state") or "field").upper()
    d.text((430, 9), dock[:8], fill=_INK, font=_font(8))
    _register(rt, SceneLayerSpec(
        "atlas.header", "text", (0, 0, 480, 32),
        signals=("dock.state", "expedition.active"), update_class="live",
    ))

    # Immersive field canvas fills the body. A single ruled notebook margin
    # carries instruments on the right instead of separate cards.
    d.rectangle((0, 32, 407, 281), fill=_FIELD)
    d.line((407, 32, 407, 281), fill=_ACCENT, width=1)
    for row in range(7):
        base_y = 48 + row * 31
        pts = []
        for x in range(0, 408, 8):
            y = base_y + math.sin((x * 0.027) + row * 0.8 + phase * 0.18) * (6 + row)
            pts.append((x, int(y)))
        d.line(pts, fill=_FIELD_2, width=1)
    d.text((14, 43), "FIELD CONTEXT", fill=_PAPER, font=_font(9))
    d.text((14, 57), "RF OBSERVATIONS // DIAGRAMMATIC, NOT GEOGRAPHIC", fill=_MUTED, font=_font(7))

    # Compass floats inside the map rather than occupying its own panel.
    _draw_compass(d, center=(365, 74), radius=23)
    _draw_rf_observations(d, state)
    _register(rt, SceneLayerSpec(
        "atlas.field", "environment", (0, 32, 408, 282),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))

    # Truthful route/GPS status stamped directly onto the field.
    if meta["draw_route"]:
        d.line((64, 196, 116, 173, 166, 180, 222, 140, 282, 148, 330, 118), fill=_ACCENT, width=3)
        d.text((16, 87), "ROUTE // LIVE", fill=_ACCENT, font=_font(8))
    else:
        d.line((16, 84, 103, 84), fill=_ALERT, width=2)
        d.text((16, 89), meta["gps_status"], fill=_ALERT, font=_font(8))
        d.text((16, 103), f"SATS USED {_ival(state, 'gps.satellites_used')}", fill=_MUTED, font=_font(7))

    _draw_beast_marker(d, meta)
    _register(rt, SceneLayerSpec(
        "atlas.beast", "creature", (18, 210, 94, 306),
        signals=("progression.stage", "progression.level", "beast.expression", "pwnagotchi.mood"),
        update_class="live",
    ))

    # Ruled field-note margin. These are annotations, not four independent widgets.
    d.rectangle((408, 32, 479, 281), fill=(31, 35, 29))
    _edge_metric(d, 42, "RADIO", f"CH {meta['channel']}", meta["band"], accent=True)
    _edge_metric(d, 98, "DISCOVERY", f"{meta['ap_unique']} UNIQUE", f"{_ival(state, 'wifi.ap_count')} NEARBY")
    _edge_metric(d, 154, "JOURNEY", f"{meta['distance_m']:.0f} m", f"{meta['duration_sec']:.0f} sec")
    temp = _fval(state, "system.temp.cpu_c")
    _edge_metric(d, 210, "READINESS", f"{temp:.0f} C", str(state.get("governor.mode") or "?").upper())
    d.line((412, 266, 470, 266), fill=(82,84,62))

    _register(rt, SceneLayerSpec(
        "atlas.radio", "instrument", (408, 42, 479, 96),
        signals=("radio.primary.channel", "radio.primary.band"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.discovery", "instrument", (408, 98, 479, 152),
        signals=("expedition.ap_unique", "wifi.ap_count"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.journey", "instrument", (408, 154, 479, 208),
        signals=("expedition.distance_m", "expedition.duration_sec"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.system", "instrument", (408, 210, 479, 266),
        signals=("system.temp.cpu_c", "governor.mode"), update_class="live",
    ))

    # Expedition ledger spans the full page like the bottom of a field notebook.
    d.rectangle((0, 282, 479, 319), fill=(34, 38, 30))
    d.line((0, 282, 479, 282), fill=_ACCENT, width=1)
    active = "ACTIVE" if meta["expedition_active"] else "IDLE"
    d.text((14, 291), f"EXPEDITION {active}", fill=_ACCENT if meta["expedition_active"] else _MUTED, font=_font(9))
    d.text((126, 291), f"DISC {meta['ap_unique']}", fill=_INK, font=_font(8))
    d.text((196, 291), f"CAP +{_ival(state, 'expedition.captures_delta')}", fill=_INK, font=_font(8))
    d.text((274, 291), f"XP +{_ival(state, 'expedition.xp_delta')}", fill=_INK, font=_font(8))
    d.text((363, 291), meta["gps_status"], fill=_ACCENT if meta["gps_fix"] else _ALERT, font=_font(7))
    d.text((14, 306), "FIELD LOG // LIVE CANONICAL STATE", fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "atlas.expedition_strip", "timeline", (0, 282, 480, 320),
        signals=("expedition.active", "expedition.ap_unique", "expedition.captures_delta", "expedition.xp_delta", "gps.fix"),
        update_class="live",
    ))

    return im



def render_atlas_recon(
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Atlas translation of Recon: a field survey, never a target/radar fiction."""
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="recon", scene_id="experience:atlas:recon", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 479, 31), fill=(35, 39, 31))
    d.text((10, 7), "ATLAS", fill=_ACCENT, font=_font(15))
    d.text((70, 9), "FIELD SURVEY", fill=_MUTED, font=_font(10))
    d.text((393, 9), f"{_ival(state, 'wifi.ap_count')} OBS", fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "atlas_recon.header", "text", (0, 0, 480, 32),
        signals=("wifi.ap_count",), update_class="live",
    ))

    # Large survey field. Position is diagrammatic: channel determines bearing,
    # RSSI determines radius. It is explicitly not a geographic/radar claim.
    field = (10, 42, 352, 276)
    d.rounded_rectangle(field, radius=12, fill=_FIELD, outline=(92, 94, 67))
    d.text((20, 51), "NEARBY RF SURVEY", fill=_PAPER, font=_font(10))
    d.text((20, 66), "RELATIVE SIGNAL DIAGRAM · NOT RANGE OR POSITION", fill=_MUTED, font=_font(8))
    cx, cy = 180, 168
    for radius in (38, 72, 108):
        d.ellipse((cx-radius, cy-int(radius*.66), cx+radius, cy+int(radius*.66)),
                  outline=(82, 86, 61), width=1)
    d.line((cx-120, cy, cx+120, cy), fill=(82, 86, 61))
    d.line((cx, cy-78, cx, cy+78), fill=(82, 86, 61))

    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)]
    band_counts = {"2.4": 0, "5": 0}
    for idx, ap in enumerate(aps[:24]):
        try:
            ch = int(ap.get("channel") or 1)
            rssi = float(ap.get("rssi") or -90)
        except Exception:
            continue
        band_counts["2.4" if ch <= 14 else "5"] += 1
        angle = math.radians((ch * 19 + idx * 31) % 360)
        radius = max(18, min(108, int((abs(rssi) - 26) * 1.42)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .66)
        color = _WATER if bool(ap.get("handshake")) else _PAPER
        d.ellipse((x-5, y-5, x+5, y+5), fill=_BG, outline=color, width=2)
        d.text((x+6, y-5), str(ch), fill=_MUTED, font=_font(7))

    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=_ACCENT)
    d.text((cx-19, cy+12), "BEAST", fill=_INK, font=_font(8))
    _register(rt, SceneLayerSpec(
        "atlas_recon.survey", "graph", field,
        signals=("wifi.aps", "wifi.ap_count"), update_class="live", decorative=False,
    ))

    # Field notebook strip uses real counts and truth states.
    d.rounded_rectangle((362, 44, 470, 112), radius=8, fill=(38,43,35), outline=(87,89,65))
    d.text((372, 53), "BANDS", fill=_MUTED, font=_font(8))
    d.text((372, 72), f"2.4  {band_counts['2.4']}", fill=_INK, font=_font(11))
    d.text((372, 91), f"5G   {band_counts['5']}", fill=_INK, font=_font(11))
    _register(rt, SceneLayerSpec(
        "atlas_recon.bands", "instrument", (362,44,470,112),
        signals=("wifi.aps",), update_class="live",
    ))

    d.rounded_rectangle((362, 122, 470, 190), radius=8, fill=(38,43,35), outline=(87,89,65))
    d.text((372, 131), "SURVEY", fill=_MUTED, font=_font(8))
    d.text((372, 150), f"HS  {_ival(state, 'wifi.handshake_ap_count')}", fill=_INK, font=_font(11))
    d.text((372, 169), f"HID {_ival(state, 'wifi.hidden_count')}", fill=_INK, font=_font(11))
    _register(rt, SceneLayerSpec(
        "atlas_recon.summary", "instrument", (362,122,470,190),
        signals=("wifi.handshake_ap_count", "wifi.hidden_count"), update_class="live",
    ))

    d.rounded_rectangle((362, 200, 470, 268), radius=8, fill=(38,43,35), outline=(87,89,65))
    d.text((372, 209), "POSITION", fill=_MUTED, font=_font(8))
    d.text((372, 228), meta["gps_status"], fill=_ACCENT if meta["gps_fix"] else _ALERT, font=_font(9))
    d.text((372, 246), f"SATS {_ival(state, 'gps.satellites_used')}", fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "atlas_recon.position", "instrument", (362,200,470,268),
        signals=("gps.fix", "gps.satellites_used"), update_class="live",
    ))

    d.rectangle((10, 287, 470, 312), fill=(38,43,35))
    d.text((20, 295), f"FIELD SESSION · {meta['ap_unique']} UNIQUE · CH {meta['channel']} · {meta['band']}",
           fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "atlas_recon.footer", "text", (10,287,470,312),
        signals=("expedition.ap_unique", "radio.primary.channel", "radio.primary.band"),
        update_class="live",
    ))
    return im
