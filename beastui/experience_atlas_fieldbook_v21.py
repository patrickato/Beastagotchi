from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw

from .beast_shell import format_reading, reading
from .experience_atlas import atlas_home_metadata
from .experience_atlas_fieldbook import (
    SIZE,
    _ACCENT,
    _ALERT,
    _BG,
    _CONTOUR,
    _EDGE,
    _FIELD,
    _FIELD_DEEP,
    _HEADER,
    _INK,
    _MUTED,
    _PAPER,
    _WATER,
    _font,
    _fmt,
    _register,
    _shell,
    _text_right,
    _valid_aps,
)
from .scene_runtime import SceneLayerSpec, SceneRuntime


# Atlas Fieldbook v2.1 keeps v2's truth model and palette, but gives each visual
# layer a single job: terrain is quiet context, RF lives in its own instrument,
# route/GPS state owns the field center, and the Beast reads as a field partner.


def _header(draw: ImageDraw.ImageDraw, shell, *, recon: bool = False, rt=None) -> None:
    draw.rectangle((0, 0, 479, 33), fill=_HEADER)
    draw.line((0, 32, 479, 32), fill=_EDGE)
    draw.rectangle((7, 5, 64, 27), outline=_ACCENT, width=2)
    draw.text((14, 8), "ATLAS", fill=_ACCENT, font=_font(12))
    draw.text((76, 6), "SURVEY / 02" if recon else "FIELD / 01", fill=_PAPER, font=_font(10))
    draw.text((76, 19), "SIGNAL RECON" if recon else "EXPEDITION FIELD BOOK", fill=_MUTED, font=_font(8))

    level = str(shell.attention.level or "notice")
    col = _ALERT if level in {"critical", "warning"} else _ACCENT if level == "normal" else _MUTED
    draw.rectangle((299, 11, 306, 18), fill=col)
    status = str(shell.status_sentence or "").upper()[:25]
    _text_right(draw, 470, 8, status, font=_font(9), fill=_INK if level != "notice" else _MUTED)
    _register(rt, SceneLayerSpec(
        "atlas_v21.recon.header" if recon else "atlas_v21.home.header",
        "text", (0, 0, 480, 34),
        signals=("health.core.state", "system.temp.cpu_c", "dock.state"),
        update_class="live",
    ))


def _nav(draw: ImageDraw.ImageDraw, shell, rt=None) -> None:
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=_HEADER)
    draw.line((0, y, 479, y), fill=_EDGE)

    if nav.previous_enabled:
        draw.line((10, y + 8, 10, 311, 20, 311), fill=_ACCENT, width=2)
        draw.text((27, y + 15), f"‹ {nav.previous_page.upper()}", fill=_ACCENT, font=_font(10))
        _register(rt, SceneLayerSpec(
            f"atlas_v21.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))
    else:
        draw.text((14, y + 17), "FIELD START", fill=_EDGE, font=_font(8))

    center = f"{nav.position_text} / ATLAS"
    bb = draw.textbbox((0, 0), center, font=_font(9))
    draw.text((240 - (bb[2] - bb[0]) // 2, y + 17), center, fill=_MUTED, font=_font(9))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        bb = draw.textbbox((0, 0), text, font=_font(10))
        draw.text((452 - (bb[2] - bb[0]), y + 15), text, fill=_ACCENT, font=_font(10))
        draw.line((469, y + 8, 469, 311, 459, 311), fill=_ACCENT, width=2)
        _register(rt, SceneLayerSpec(
            f"atlas_v21.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))
    else:
        text = "FIELD END"
        bb = draw.textbbox((0, 0), text, font=_font(8))
        draw.text((466 - (bb[2] - bb[0]), y + 17), text, fill=_EDGE, font=_font(8))


def _field_frame(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((8, 40, 350, 226), fill=_FIELD, outline=_EDGE)
    # Survey corner marks remain the strongest geometry; intermediate ticks are
    # deliberately sparse so they read as a field instrument, not graph paper.
    for x, y, sx, sy in ((8, 40, 1, 1), (350, 40, -1, 1), (8, 226, 1, -1), (350, 226, -1, -1)):
        draw.line((x, y, x + sx * 13, y), fill=_PAPER, width=2)
        draw.line((x, y, x, y + sy * 13), fill=_PAPER, width=2)
    for x in (72, 136, 200, 264, 328):
        draw.line((x, 40, x, 44), fill=_EDGE)
        draw.line((x, 222, x, 226), fill=_EDGE)


def _quiet_terrain(draw: ImageDraw.ImageDraw, phase: float) -> None:
    """Sparse broken contour traces: atmosphere only, never map/elevation data."""
    for row, base in enumerate((92, 122, 154, 188, 211)):
        pts: list[tuple[int, int]] = []
        for x in range(15, 341, 7):
            wave = math.sin(x * 0.029 + row * 1.11 + phase * 0.05)
            wave += 0.35 * math.sin(x * 0.067 - row * 0.42)
            y = int(base + wave * (3.0 + row * 0.45))
            pts.append((x, y))
        # Break each contour into short field-sketch fragments. The gaps stop the
        # terrain layer from competing with route and RF marks on the TFT.
        for start in range((row % 2) * 4, len(pts) - 5, 13):
            seg = pts[start:start + 7]
            if len(seg) > 1:
                draw.line(seg, fill=_CONTOUR)


def _mini_rf(draw: ImageDraw.ImageDraw, state: dict[str, Any]) -> int:
    box = (218, 78, 339, 146)
    draw.rectangle(box, fill=_FIELD_DEEP, outline=_WATER)
    draw.text((225, 83), "RF FIELD", fill=_WATER, font=_font(8))
    valid = _valid_aps(state)
    draw.text((299, 83), f"{len(valid):02d}", fill=_PAPER, font=_font(8))
    cx, cy = 278, 118
    for radius in (18, 35, 51):
        draw.ellipse((cx - radius, cy - int(radius * .48), cx + radius, cy + int(radius * .48)), outline=(61, 79, 61))
    draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=_ACCENT)
    for idx, (ap, ch, rssi) in enumerate(valid[:10]):
        angle = math.radians((ch * 23 + idx * 43) % 360)
        radius = max(10, min(49, int((abs(rssi) - 28) * .72)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .48)
        col = _WATER if bool(ap.get("handshake")) else _PAPER
        draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=col)
    return len(valid)


def _companion(draw: ImageDraw.ImageDraw, meta: dict[str, Any]) -> None:
    # Larger than v2, but still a field partner rather than the page's whole job.
    x, y = 22, 151
    mood = str(meta.get("expression") or "awake").lower()
    alert = mood in {"focused", "hunting", "intense", "angry"}
    draw.line((x, y - 5, x, y + 67), fill=_ACCENT, width=2)
    draw.text((x + 10, y - 4), "FIELD PARTNER", fill=_MUTED, font=_font(8))

    head = [
        (x + 13, y + 31), (x + 20, y + 17), (x + 35, y + 12),
        (x + 51, y + 18), (x + 58, y + 32), (x + 53, y + 49),
        (x + 39, y + 57), (x + 24, y + 54), (x + 14, y + 44),
    ]
    draw.polygon(head, fill=_FIELD_DEEP, outline=_PAPER)
    draw.polygon([(x + 18, y + 23), (x + 16, y + 5), (x + 29, y + 16)], fill=_FIELD_DEEP, outline=_ACCENT)
    draw.polygon([(x + 43, y + 16), (x + 54, y + 4), (x + 55, y + 26)], fill=_FIELD_DEEP, outline=_ACCENT)
    eye = _ALERT if alert else _INK
    draw.line((x + 24, y + 32, x + 31, y + 30), fill=eye, width=2)
    draw.line((x + 42, y + 30, x + 49, y + 32), fill=eye, width=2)
    if alert:
        draw.line((x + 28, y + 44, x + 45, y + 44), fill=_ACCENT, width=2)
    else:
        draw.arc((x + 28, y + 39, x + 45, y + 49), 10, 170, fill=_MUTED)

    stage = str(meta.get("stage") or "BEAST").upper()[:12]
    level = "—" if meta.get("level") is None else str(meta["level"])
    draw.text((x + 72, y + 20), stage, fill=_INK, font=_font(11))
    draw.text((x + 72, y + 38), f"LV {level}", fill=_ACCENT, font=_font(9))
    draw.text((x + 72, y + 52), mood.upper()[:12], fill=_MUTED, font=_font(8))


def _instrument_spine(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((355, 40, 471, 268), fill=_FIELD_DEEP, outline=_EDGE)
    draw.rectangle((355, 40, 361, 268), fill=_ACCENT)
    for y in (96, 152, 208):
        draw.line((370, y, 463, y), fill=_EDGE)


def _instrument(draw: ImageDraw.ImageDraw, index: str, y: int, label: str, primary: str, secondary: str = "", *, accent=False) -> None:
    col = _ACCENT if accent else _INK
    draw.text((369, y), index, fill=_EDGE, font=_font(8))
    draw.text((389, y), label, fill=_MUTED, font=_font(8))
    draw.text((369, y + 15), primary[:15], fill=col, font=_font(12))
    if secondary:
        draw.text((369, y + 32), secondary[:18], fill=_MUTED, font=_font(8))


def _journey_strip(draw: ImageDraw.ImageDraw, state: dict[str, Any], meta: dict[str, Any]) -> None:
    draw.rectangle((8, 231, 350, 268), fill=_HEADER, outline=_EDGE)
    draw.rectangle((8, 231, 13, 268), fill=_ACCENT)
    if meta["expedition_active"] is True:
        active, col = "ACTIVE", _ACCENT
    elif meta["expedition_active"] is False:
        active, col = "IDLE", _MUTED
    else:
        active, col = "—", _MUTED
    captures = reading(state, "expedition.captures_delta")
    xp = reading(state, "expedition.xp_delta")
    draw.text((22, 237), "EXPEDITION", fill=_MUTED, font=_font(8))
    draw.text((22, 250), active, fill=col, font=_font(10))
    draw.text((119, 237), "CAPTURE", fill=_MUTED, font=_font(8))
    draw.text((119, 250), f"+{format_reading(captures)}", fill=_INK if captures.known else _MUTED, font=_font(10))
    draw.text((205, 237), "XP", fill=_MUTED, font=_font(8))
    draw.text((205, 250), f"+{format_reading(xp)}", fill=_INK if xp.known else _MUTED, font=_font(10))
    draw.text((270, 237), "LOG", fill=_MUTED, font=_font(8))
    draw.line((270, 257, 337, 257), fill=_EDGE, width=2)


def render_atlas_home(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "home")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:atlas:home", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _header(d, shell, rt=rt)
    _field_frame(d)
    _quiet_terrain(d, phase)

    draw_route = bool(meta["draw_route"])
    if draw_route:
        # Symbolic route trace is only admitted by the validated GPS/route truth gate.
        route = [(112, 195), (146, 177), (177, 184), (199, 157), (219, 160)]
        d.line(route, fill=_ACCENT, width=4)
        for x, y in route:
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=_PAPER)
        d.rectangle((18, 76, 120, 108), fill=_FIELD_DEEP, outline=_ACCENT)
        d.text((25, 81), "ROUTE LIVE", fill=_ACCENT, font=_font(9))
        d.text((25, 96), "GPS VERIFIED", fill=_MUTED, font=_font(8))
    else:
        status_col = _ALERT if meta["gps_fix"] is False else _MUTED
        d.rectangle((18, 76, 126, 111), fill=_FIELD_DEEP, outline=_EDGE)
        d.text((25, 81), meta["gps_status"], fill=status_col, font=_font(9))
        sats = reading(state, "gps.satellites_used")
        d.text((25, 97), f"SATS {format_reading(sats)}", fill=_MUTED, font=_font(8))
        d.text((143, 105), "ROUTE AWAITS POSITION", fill=_MUTED, font=_font(8))

    _mini_rf(d, state)
    _companion(d, meta)
    d.text((18, 48), "TERRAIN CONTEXT / SYMBOLIC", fill=_MUTED, font=_font(8))
    d.line((18, 62, 202, 62), fill=_EDGE)

    _register(rt, SceneLayerSpec(
        "atlas_v21.home.field", "environment", (8, 40, 351, 227),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))
    _register(rt, SceneLayerSpec(
        "atlas_v21.home.beast", "creature", (18, 145, 205, 225),
        signals=("progression.stage", "progression.level", "beast.expression", "pwnagotchi.mood"),
        update_class="live",
    ))

    _instrument_spine(d)
    channel = format_reading(meta["channel_reading"])
    band = meta["band"] if meta["band"] != "?" else "BAND —"
    _instrument(d, "01", 50, "RADIO", f"CH {channel}", band, accent=meta["channel"] is not None)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    nearby = format_reading(meta["nearby_reading"])
    _instrument(d, "02", 106, "DISCOVERY", f"{unique} UNIQUE", f"{nearby} NEARBY")
    _instrument(d, "03", 162, "JOURNEY", _fmt(meta["distance_m"], " m"), _fmt(meta["duration_sec"], " sec"))
    temp = format_reading(meta["temp_reading"])
    gov = format_reading(meta["governor_reading"])
    _instrument(d, "04", 218, "READINESS", temp, f"GOV {gov}")

    _register(rt, SceneLayerSpec(
        "atlas_v21.home.instruments", "instrument", (355, 40, 472, 269),
        signals=(
            "radio.primary.channel", "radio.primary.band", "expedition.ap_unique",
            "wifi.ap_count", "expedition.distance_m", "expedition.duration_sec",
            "system.temp.cpu_c", "governor.mode",
        ),
        update_class="live",
    ))

    _journey_strip(d, state, meta)
    _register(rt, SceneLayerSpec(
        "atlas_v21.home.log", "timeline", (8, 231, 351, 269),
        signals=("expedition.active", "expedition.captures_delta", "expedition.xp_delta"),
        update_class="live",
    ))
    _nav(d, shell, rt)
    return im


def render_atlas_recon(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "recon")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="recon", scene_id="experience:atlas:recon", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _header(d, shell, recon=True, rt=rt)
    _field_frame(d)

    # Recon is intentionally pure RF instrumentation: no terrain contours.
    d.rectangle((18, 70, 340, 216), fill=_FIELD_DEEP, outline=_WATER)
    d.text((26, 48), "RF RELATIVE SURVEY / NOT GEOGRAPHIC POSITION", fill=_MUTED, font=_font(8))
    cx, cy = 177, 145
    for radius in (38, 72, 112):
        d.ellipse((cx - radius, cy - int(radius * .52), cx + radius, cy + int(radius * .52)), outline=(61, 79, 61))
    d.line((cx - 145, cy, cx + 145, cy), fill=(61, 79, 61))
    d.line((cx, 80, cx, 210), fill=(61, 79, 61))
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        d.line((cx, cy, int(cx + math.cos(a) * 110), int(cy + math.sin(a) * 57)), fill=(51, 67, 53))

    sweep = (phase * 0.55) % (math.pi * 2)
    sx = int(cx + math.cos(sweep) * 110)
    sy = int(cy + math.sin(sweep) * 58)
    d.line((cx, cy, sx, sy), fill=_WATER, width=2)

    valid = _valid_aps(state)
    band_counts = {"2.4": 0, "5": 0}
    for idx, (ap, ch, rssi) in enumerate(valid[:24]):
        band_counts["2.4" if ch <= 14 else "5"] += 1
        angle = math.radians((ch * 19 + idx * 31) % 360)
        radius = max(18, min(108, int((abs(rssi) - 26) * 1.34)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .52)
        handshake = bool(ap.get("handshake"))
        col = _WATER if handshake else _PAPER
        if handshake:
            d.rectangle((x - 5, y - 5, x + 5, y + 5), outline=col, width=2)
        else:
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=_FIELD_DEEP, outline=col, width=2)
        d.text((x + 7, y - 5), str(ch), fill=_MUTED, font=_font(8))

    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=_ACCENT)
    d.text((cx - 18, cy + 14), "BEAST", fill=_INK, font=_font(8))
    if not valid:
        d.text((116, 192), "NO RF OBSERVATIONS", fill=_MUTED, font=_font(9))

    _register(rt, SceneLayerSpec(
        "atlas_v21.recon.survey", "graph", (8, 40, 351, 227),
        signals=("wifi.aps", "wifi.ap_count"), update_class="live", decorative=False,
    ))

    _instrument_spine(d)
    _instrument(d, "01", 50, "BANDS", f"2.4G {band_counts['2.4']}", f"5G   {band_counts['5']}")
    hs = reading(state, "wifi.handshake_ap_count")
    hidden = reading(state, "wifi.hidden_count")
    _instrument(d, "02", 106, "SURVEY", f"HS {format_reading(hs)}", f"HID {format_reading(hidden)}")
    sats = reading(state, "gps.satellites_used")
    _instrument(d, "03", 162, "POSITION", meta["gps_status"], f"SATS {format_reading(sats)}", accent=meta["gps_fix"] is True)
    channel = format_reading(meta["channel_reading"])
    _instrument(d, "04", 218, "TUNED", f"CH {channel}", meta["band"] if meta["band"] != "?" else "BAND —", accent=meta["channel"] is not None)

    d.rectangle((8, 231, 350, 268), fill=_HEADER, outline=_EDGE)
    d.rectangle((8, 231, 13, 268), fill=_WATER)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    d.text((22, 238), f"SESSION {unique} UNIQUE", fill=_ACCENT, font=_font(9))
    d.text((22, 253), "CIRCLE=OBSERVED  SQUARE=HANDSHAKE  RING=RSSI", fill=_MUTED, font=_font(8))

    _register(rt, SceneLayerSpec(
        "atlas_v21.recon.instruments", "instrument", (355, 40, 472, 269),
        signals=(
            "wifi.aps", "wifi.handshake_ap_count", "wifi.hidden_count",
            "gps.fix", "gps.satellites_used", "radio.primary.channel", "radio.primary.band",
        ),
        update_class="live",
    ))
    _nav(d, shell, rt)
    return im
