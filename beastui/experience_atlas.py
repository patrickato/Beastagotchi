from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import BeastShellModel, SHELL_TYPE, build_shell_model, format_reading, reading
from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)
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


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    n = _number(value)
    return None if n is None else int(n)


def _register(rt: SceneRuntime | None, spec: SceneLayerSpec) -> None:
    if rt is not None:
        rt.register(spec)


def _shell(state: dict[str, Any], page_id: str) -> BeastShellModel:
    shell = state.get("_beast_shell")
    if isinstance(shell, BeastShellModel) and shell.page_id == page_id:
        return shell
    return build_shell_model("atlas", page_id, state, ("home", "recon"))


def _attention_color(shell: BeastShellModel):
    if shell.attention.level in {"critical", "warning"}:
        return _ALERT
    if shell.attention.level == "normal":
        return _ACCENT
    return _MUTED


def atlas_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    """Truth-only Atlas metadata. Missing observations remain unknown."""
    state = dict(state or {})
    gps = reading(state, "gps.fix")
    route = reading(state, "expedition.route_points")
    expedition = reading(state, "expedition.active")
    unique = reading(state, "expedition.ap_unique")
    nearby = reading(state, "wifi.ap_count")
    distance = reading(state, "expedition.distance_m", unit=" m")
    duration = reading(state, "expedition.duration_sec", unit=" sec")
    channel = reading(state, "radio.primary.channel")
    temp = reading(state, "system.temp.cpu_c", unit="°C")
    governor = reading(state, "governor.mode")
    level = reading(state, "progression.level")

    gps_fix = bool(gps.value) if gps.known else None
    route_points = _int_or_none(route.value) if route.known else None
    ap_unique = _int_or_none(unique.value) if unique.known else _int_or_none(nearby.value) if nearby.known else None

    if gps_fix is True:
        gps_status = "GPS FIX"
    elif gps_fix is False:
        gps_status = "GPS SEARCHING"
    else:
        gps_status = "GPS —"

    return {
        "gps_fix": gps_fix,
        "route_points": route_points,
        "draw_route": bool(gps_fix is True and route_points is not None and route_points >= 2),
        "gps_status": gps_status,
        "expedition_active": bool(expedition.value) if expedition.known else None,
        "ap_unique": ap_unique,
        "distance_m": _number(distance.value) if distance.known else None,
        "duration_sec": _number(duration.value) if duration.known else None,
        "channel": _int_or_none(channel.value) if channel.known else None,
        "band": str(state.get("radio.primary.band") or "?") if "radio.primary.band" in state else "?",
        "stage": str(state.get("progression.stage") or "BEAST"),
        "level": _int_or_none(level.value) if level.known else None,
        "expression": str(state.get("beast.expression") or state.get("pwnagotchi.mood") or "awake"),
        "gps_reading": gps,
        "route_reading": route,
        "expedition_reading": expedition,
        "unique_reading": unique,
        "nearby_reading": nearby,
        "distance_reading": distance,
        "duration_reading": duration,
        "channel_reading": channel,
        "temp_reading": temp,
        "governor_reading": governor,
        "level_reading": level,
    }


def _draw_header(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None, *, recon=False):
    col = _attention_color(shell)
    draw.rectangle((0, 0, 479, 33), fill=(34, 38, 30))
    draw.line((0, 32, 479, 32), fill=_FIELD_2)
    draw.text((10, 6), "ATLAS", fill=_ACCENT, font=_font(SHELL_TYPE.label))
    draw.text((70, 9), "FIELD SURVEY" if recon else "FIELD EXPEDITION",
              fill=_MUTED, font=_font(SHELL_TYPE.caption))
    draw.ellipse((292, 11, 302, 21), fill=col)
    box = draw.textbbox((0, 0), shell.status_sentence, font=_font(SHELL_TYPE.caption))
    draw.text((468 - (box[2] - box[0]), 8), shell.status_sentence,
              fill=_INK if shell.attention.level != "notice" else _MUTED,
              font=_font(SHELL_TYPE.caption))
    layer_id = "atlas_recon.header" if recon else "atlas.header"
    _register(rt, SceneLayerSpec(
        layer_id, "text", (0, 0, 480, 34),
        signals=("health.core.state", "system.temp.cpu_c", "dock.state"), update_class="live",
    ))


def _draw_nav(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=(34, 38, 30))
    draw.line((0, y, 479, y), fill=_ACCENT)
    draw.line((160, y + 8, 160, 312), fill=_FIELD_2)
    draw.line((320, y + 8, 320, 312), fill=_FIELD_2)

    if nav.previous_enabled:
        text = f"‹ {nav.previous_page.upper()}"
        draw.text((18, y + 18), text, fill=_ACCENT, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"atlas.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))

    center = nav.position_text
    box = draw.textbbox((0, 0), center, font=_font(SHELL_TYPE.body))
    draw.text((240 - (box[2] - box[0]) // 2, y + 18), center,
              fill=_MUTED, font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        f"atlas.{nav.page_id}.nav_position", "text", nav.center_box, update_class="static",
    ))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        box = draw.textbbox((0, 0), text, font=_font(SHELL_TYPE.caption))
        draw.text((462 - (box[2] - box[0]), y + 18), text,
                  fill=_ACCENT, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"atlas.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))


def _draw_contours(draw: ImageDraw.ImageDraw, phase: float, *, width=360, bottom=229) -> None:
    """Decorative terrain language; never presented as geographic/elevation truth."""
    for row in range(6):
        base_y = 52 + row * 31
        pts = []
        for x in range(0, width, 8):
            y = base_y + math.sin((x * 0.027) + row * 0.8 + phase * 0.18) * (6 + row)
            pts.append((x, min(bottom, int(y))))
        draw.line(pts, fill=_FIELD_2, width=1)


def _draw_compass(draw: ImageDraw.ImageDraw, center=(323, 75), radius=22) -> None:
    cx, cy = center
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=_MUTED)
    draw.line((cx, cy-radius+4, cx, cy+radius-4), fill=_PAPER)
    draw.line((cx-radius+4, cy, cx+radius-4, cy), fill=_PAPER)
    draw.polygon([(cx, cy-radius+3), (cx-4, cy-9), (cx+4, cy-9)], fill=_ACCENT)
    draw.text((cx-4, cy-radius-12), "N", fill=_INK, font=_font(9))


def _draw_rf_observations(draw: ImageDraw.ImageDraw, state: dict[str, Any], *, origin=(165, 145)) -> None:
    """Plot only observations that really contain channel and RSSI."""
    aps = state.get("wifi.aps") if isinstance(state.get("wifi.aps"), list) else []
    valid = []
    for ap in aps:
        if not isinstance(ap, dict):
            continue
        ch = _int_or_none(ap.get("channel"))
        rssi = _number(ap.get("rssi"))
        if ch is None or rssi is None:
            continue
        valid.append((ap, ch, rssi))

    draw.ellipse((origin[0]-5, origin[1]-5, origin[0]+5, origin[1]+5), fill=_ACCENT)
    for idx, (ap, ch, rssi) in enumerate(valid[:12]):
        angle = math.radians((ch * 23 + idx * 47) % 360)
        radius = max(24, min(100, int((abs(rssi) - 28) * 1.45)))
        x = int(origin[0] + math.cos(angle) * radius)
        y = int(origin[1] + math.sin(angle) * radius * 0.60)
        color = _WATER if bool(ap.get("handshake")) else _PAPER
        draw.ellipse((x-3, y-3, x+3, y+3), outline=color, fill=_FIELD)
        draw.line((origin[0], origin[1], x, y), fill=(68, 72, 54))


def _draw_beast_marker(draw: ImageDraw.ImageDraw, meta: dict[str, Any]) -> None:
    """Field-sketch companion; deliberately secondary to the expedition canvas."""
    x, y = 22, 173
    mood = str(meta.get("expression") or "awake").lower()
    alert = mood in {"focused", "hunting", "intense", "angry"}

    body = [
        (x+28,y+18),(x+40,y+16),(x+52,y+22),(x+58,y+34),
        (x+55,y+48),(x+45,y+54),(x+29,y+53),(x+18,y+48),
        (x+15,y+36),(x+19,y+26),
    ]
    draw.polygon(body, fill=(40,44,36), outline=_PAPER)
    draw.polygon([(x+20,y+25),(x+20,y+8),(x+30,y+19)], fill=(40,44,36), outline=_ACCENT)
    draw.polygon([(x+42,y+18),(x+51,y+7),(x+53,y+25)], fill=(40,44,36), outline=_ACCENT)
    eye = _ALERT if alert else _INK
    draw.line((x+28,y+29,x+34,y+28), fill=eye, width=2)
    draw.line((x+42,y+28,x+47,y+29), fill=eye, width=2)
    draw.line((x+37,y+31,x+38,y+35), fill=_ACCENT)
    if alert:
        draw.line((x+31,y+40,x+46,y+40), fill=_ACCENT)
    else:
        draw.arc((x+31,y+34,x+46,y+43), 15, 165, fill=_MUTED)

    level = "—" if meta["level"] is None else str(meta["level"])
    label = f"{meta['stage'].upper()} / LV {level}"
    draw.line((x+60,y+24,x+77,y+14), fill=_ACCENT)
    draw.text((x+81,y+4), label, fill=_INK, font=_font(10))
    draw.text((x+81,y+20), mood.upper()[:11], fill=_MUTED, font=_font(9))


def _edge_metric(draw, y, label, primary, secondary="", *, accent=False):
    """Readable notebook-margin annotation, not a dashboard card."""
    draw.line((370, y, 470, y), fill=(82, 84, 62))
    draw.text((372, y + 5), label, fill=_MUTED, font=_font(10))
    draw.text((372, y + 20), primary, fill=_ACCENT if accent else _INK, font=_font(SHELL_TYPE.body))
    if secondary:
        draw.text((372, y + 38), secondary, fill=_MUTED, font=_font(9))


def _fmt_number(value: float | None, unit: str) -> str:
    return "—" if value is None else f"{value:.0f}{unit}"


def render_atlas_home(state: dict[str, Any], *, phase: float = 0.0,
                      scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Atlas Home: a truthful field notebook with readable margin instruments."""
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "home")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:atlas:home", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_header(d, shell, rt)

    # Field canvas remains dominant; margin is wide enough to communicate legibly.
    d.rectangle((0, 34, 359, 229), fill=_FIELD)
    d.line((359, 34, 359, 263), fill=_ACCENT)
    _draw_contours(d, phase)
    d.text((14, 44), "FIELD CONTEXT", fill=_PAPER, font=_font(SHELL_TYPE.caption))
    d.text((14, 61), "RELATIVE RF OBSERVATIONS", fill=_MUTED, font=_font(9))
    _draw_compass(d)
    _draw_rf_observations(d, state)
    _register(rt, SceneLayerSpec(
        "atlas.field", "environment", (0, 34, 360, 230),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))

    # Route/GPS truth is explicit. No fix does not become a fake line on the map.
    if meta["draw_route"]:
        d.line((70, 188, 118, 166, 165, 174, 218, 136, 276, 145, 326, 112), fill=_ACCENT, width=3)
        d.text((16, 84), "ROUTE LIVE", fill=_ACCENT, font=_font(SHELL_TYPE.caption))
    else:
        status_col = _ALERT if meta["gps_fix"] is False else _MUTED
        d.line((16, 82, 118, 82), fill=status_col, width=2)
        d.text((16, 89), meta["gps_status"], fill=status_col, font=_font(SHELL_TYPE.caption))
        sats = reading(state, "gps.satellites_used")
        d.text((16, 108), f"SATS {format_reading(sats)}", fill=_MUTED, font=_font(10))

    _draw_beast_marker(d, meta)
    _register(rt, SceneLayerSpec(
        "atlas.beast", "creature", (16, 168, 160, 229),
        signals=("progression.stage", "progression.level", "beast.expression", "pwnagotchi.mood"),
        update_class="live",
    ))

    # Notebook margin.
    d.rectangle((360, 34, 479, 263), fill=(31, 35, 29))
    channel = format_reading(meta["channel_reading"])
    band = meta["band"] if meta["band"] != "?" else "BAND —"
    _edge_metric(d, 43, "RADIO", f"CH {channel}", band, accent=meta["channel"] is not None)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    nearby = format_reading(meta["nearby_reading"])
    _edge_metric(d, 96, "DISCOVERY", f"{unique} UNIQUE", f"{nearby} NEARBY")
    _edge_metric(d, 149, "JOURNEY", _fmt_number(meta["distance_m"], " m"),
                 _fmt_number(meta["duration_sec"], " sec"))
    temp = format_reading(meta["temp_reading"])
    gov = format_reading(meta["governor_reading"])
    _edge_metric(d, 202, "READINESS", temp, f"GOV {gov}")

    _register(rt, SceneLayerSpec(
        "atlas.radio", "instrument", (360, 43, 479, 94),
        signals=("radio.primary.channel", "radio.primary.band"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.discovery", "instrument", (360, 96, 479, 147),
        signals=("expedition.ap_unique", "wifi.ap_count"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.journey", "instrument", (360, 149, 479, 200),
        signals=("expedition.distance_m", "expedition.duration_sec"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas.system", "instrument", (360, 202, 479, 263),
        signals=("system.temp.cpu_c", "governor.mode"), update_class="live",
    ))

    # Field ledger sits inside the Experience body; shell navigation remains separate.
    d.rectangle((0, 230, 359, 263), fill=(34, 38, 30))
    d.line((0, 230, 359, 230), fill=_ACCENT)
    if meta["expedition_active"] is True:
        active, active_col = "EXPEDITION ACTIVE", _ACCENT
    elif meta["expedition_active"] is False:
        active, active_col = "EXPEDITION IDLE", _MUTED
    else:
        active, active_col = "EXPEDITION —", _MUTED
    d.text((14, 239), active, fill=active_col, font=_font(SHELL_TYPE.caption))
    captures = reading(state, "expedition.captures_delta")
    xp = reading(state, "expedition.xp_delta")
    d.text((174, 239), f"CAP +{format_reading(captures)}", fill=_INK if captures.known else _MUTED,
           font=_font(10))
    d.text((266, 239), f"XP +{format_reading(xp)}", fill=_INK if xp.known else _MUTED,
           font=_font(10))
    _register(rt, SceneLayerSpec(
        "atlas.expedition_strip", "timeline", (0, 230, 360, 264),
        signals=("expedition.active", "expedition.ap_unique", "expedition.captures_delta", "expedition.xp_delta", "gps.fix"),
        update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im


def render_atlas_recon(state: dict[str, Any], *, scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Atlas Recon: relative RF survey in the same notebook language as Home."""
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "recon")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="recon", scene_id="experience:atlas:recon", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_header(d, shell, rt, recon=True)

    d.rectangle((0, 34, 359, 229), fill=_FIELD)
    d.line((359, 34, 359, 263), fill=_ACCENT)
    d.text((14, 44), "NEARBY RF SURVEY", fill=_PAPER, font=_font(SHELL_TYPE.caption))
    d.text((14, 61), "RSSI RELATIVE / NOT POSITION", fill=_MUTED, font=_font(9))

    cx, cy = 178, 145
    for radius in (38, 72, 106):
        d.ellipse((cx-radius, cy-int(radius*.60), cx+radius, cy+int(radius*.60)), outline=(82, 86, 61))
    d.line((cx-124, cy, cx+124, cy), fill=(82,86,61))
    d.line((cx, cy-75, cx, cy+75), fill=(82,86,61))

    aps = state.get("wifi.aps") if isinstance(state.get("wifi.aps"), list) else []
    band_counts = {"2.4": 0, "5": 0}
    for idx, ap in enumerate(aps[:24]):
        if not isinstance(ap, dict):
            continue
        ch = _int_or_none(ap.get("channel"))
        rssi = _number(ap.get("rssi"))
        if ch is None or rssi is None:
            continue
        band_counts["2.4" if ch <= 14 else "5"] += 1
        angle = math.radians((ch * 19 + idx * 31) % 360)
        radius = max(18, min(104, int((abs(rssi) - 26) * 1.35)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .60)
        color = _WATER if bool(ap.get("handshake")) else _PAPER
        d.ellipse((x-4, y-4, x+4, y+4), fill=_FIELD, outline=color, width=2)
        d.text((x+6, y-5), str(ch), fill=_MUTED, font=_font(9))

    d.ellipse((cx-7, cy-7, cx+7, cy+7), fill=_ACCENT)
    d.text((cx-21, cy+14), "BEAST", fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "atlas_recon.survey", "graph", (0, 34, 360, 230),
        signals=("wifi.aps", "wifi.ap_count"), update_class="live", decorative=False,
    ))

    d.rectangle((360, 34, 479, 263), fill=(31,35,29))
    _edge_metric(d, 43, "BANDS", f"2.4  {band_counts['2.4']}", f"5G   {band_counts['5']}")
    hs = reading(state, "wifi.handshake_ap_count")
    hidden = reading(state, "wifi.hidden_count")
    _edge_metric(d, 96, "SURVEY", f"HS {format_reading(hs)}", f"HID {format_reading(hidden)}")
    sats = reading(state, "gps.satellites_used")
    _edge_metric(d, 149, "POSITION", meta["gps_status"], f"SATS {format_reading(sats)}",
                 accent=meta["gps_fix"] is True)
    channel = format_reading(meta["channel_reading"])
    _edge_metric(d, 202, "TUNED", f"CH {channel}", meta["band"] if meta["band"] != "?" else "BAND —",
                 accent=meta["channel"] is not None)

    _register(rt, SceneLayerSpec(
        "atlas_recon.bands", "instrument", (360, 43, 479, 94), signals=("wifi.aps",), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas_recon.summary", "instrument", (360, 96, 479, 147),
        signals=("wifi.handshake_ap_count", "wifi.hidden_count"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "atlas_recon.position", "instrument", (360, 149, 479, 200),
        signals=("gps.fix", "gps.satellites_used"), update_class="live",
    ))

    d.rectangle((0, 230, 359, 263), fill=(34,38,30))
    d.line((0,230,359,230), fill=_ACCENT)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    d.text((14, 239), f"FIELD SESSION / {unique} UNIQUE", fill=_ACCENT, font=_font(SHELL_TYPE.caption))
    d.text((221, 239), "RELATIVE RF", fill=_MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "atlas_recon.footer", "text", (0,230,360,264),
        signals=("expedition.ap_unique", "radio.primary.channel", "radio.primary.band"), update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im
