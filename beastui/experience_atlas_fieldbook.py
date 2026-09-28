from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import (
    BeastShellModel,
    SHELL_TYPE,
    build_shell_model,
    format_reading,
    reading,
)
from .experience_atlas import atlas_home_metadata
from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)

# Atlas Fieldbook v2 deliberately keeps the muted expedition palette while
# replacing the earlier flat panel treatment with an authored field-instrument
# language. All geographic/RF marks remain explicitly relative/decorative unless
# backed by live state.
_BG = (24, 28, 24)
_HEADER = (31, 35, 29)
_FIELD = (50, 56, 40)
_FIELD_DEEP = (38, 43, 34)
_CONTOUR = (75, 81, 55)
_PAPER = (224, 216, 178)
_INK = (238, 232, 202)
_MUTED = (154, 155, 125)
_ACCENT = (211, 181, 91)
_ALERT = (210, 119, 84)
_WATER = (78, 124, 127)
_EDGE = (91, 91, 64)


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


def _text_right(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, font, fill) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((x - (box[2] - box[0]), y), text, font=font, fill=fill)


def _header(draw: ImageDraw.ImageDraw, shell: BeastShellModel, *, recon: bool = False, rt=None) -> None:
    draw.rectangle((0, 0, 479, 33), fill=_HEADER)
    draw.line((0, 32, 479, 32), fill=_EDGE)
    draw.rectangle((8, 5, 59, 27), outline=_ACCENT)
    draw.text((15, 8), "ATLAS", fill=_ACCENT, font=_font(12))
    draw.text((70, 7), "FIELD / 02" if recon else "FIELD / 01", fill=_PAPER, font=_font(10))
    draw.text((70, 19), "RF SURVEY" if recon else "EXPEDITION NOTEBOOK", fill=_MUTED, font=_font(8))

    col = _attention_color(shell)
    draw.ellipse((303, 11, 311, 19), fill=col)
    status = str(shell.status_sentence or "").upper()[:25]
    _text_right(draw, 470, 8, status, font=_font(9), fill=_INK if shell.attention.level != "notice" else _MUTED)

    _register(rt, SceneLayerSpec(
        "atlas_v2.recon.header" if recon else "atlas_v2.home.header",
        "text", (0, 0, 480, 34),
        signals=("health.core.state", "system.temp.cpu_c", "dock.state"),
        update_class="live",
    ))


def _nav(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None) -> None:
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=_HEADER)
    draw.line((0, y, 479, y), fill=_EDGE)

    if nav.previous_enabled:
        draw.line((12, y + 9, 12, 310, 20, 310), fill=_ACCENT, width=2)
        draw.text((26, y + 15), f"‹ {nav.previous_page.upper()}", fill=_ACCENT, font=_font(10))
        _register(rt, SceneLayerSpec(
            f"atlas_v2.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))

    center = f"{nav.position_text}  /  ATLAS"
    box = draw.textbbox((0, 0), center, font=_font(9))
    draw.text((240 - (box[2] - box[0]) // 2, y + 17), center, fill=_MUTED, font=_font(9))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        box = draw.textbbox((0, 0), text, font=_font(10))
        draw.text((452 - (box[2] - box[0]), y + 15), text, fill=_ACCENT, font=_font(10))
        draw.line((468, y + 9, 468, 310, 460, 310), fill=_ACCENT, width=2)
        _register(rt, SceneLayerSpec(
            f"atlas_v2.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))


def _field_frame(draw: ImageDraw.ImageDraw, box=(8, 40, 350, 226)) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=_FIELD, outline=_EDGE)
    # Surveyor corner marks and edge ticks make the field feel like an instrument,
    # without implying real map coordinates.
    mark = 12
    for x, y, sx, sy in (
        (x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)
    ):
        draw.line((x, y, x + sx * mark, y), fill=_PAPER)
        draw.line((x, y, x, y + sy * mark), fill=_PAPER)
    for x in range(x1 + 28, x2, 32):
        draw.line((x, y1, x, y1 + 4), fill=_EDGE)
        draw.line((x, y2 - 4, x, y2), fill=_EDGE)
    for y in range(y1 + 25, y2, 27):
        draw.line((x1, y, x1 + 4, y), fill=_EDGE)
        draw.line((x2 - 4, y, x2, y), fill=_EDGE)


def _contours(draw: ImageDraw.ImageDraw, phase: float, *, box=(8, 40, 350, 226)) -> None:
    x1, y1, x2, y2 = box
    # Decorative fieldbook contours only: no geographic/elevation claim.
    for row in range(7):
        base = y1 + 17 + row * 25
        pts = []
        for x in range(x1 + 2, x2 - 1, 6):
            wave = math.sin((x * 0.031) + row * 0.83 + phase * 0.09)
            wave += 0.45 * math.sin((x * 0.063) - row * 0.51)
            y = int(base + wave * (4 + row * 0.6))
            pts.append((x, max(y1 + 2, min(y2 - 2, y))))
        if len(pts) > 1:
            draw.line(pts, fill=_CONTOUR)


def _compass(draw: ImageDraw.ImageDraw, center=(317, 72)) -> None:
    cx, cy = center
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), outline=_MUTED)
    draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=_ACCENT)
    draw.line((cx, cy - 14, cx, cy + 14), fill=_PAPER)
    draw.line((cx - 14, cy, cx + 14, cy), fill=_PAPER)
    draw.polygon([(cx, cy - 17), (cx - 4, cy - 8), (cx + 4, cy - 8)], fill=_ACCENT)
    draw.text((cx - 3, cy - 29), "N", fill=_INK, font=_font(8))


def _valid_aps(state: dict[str, Any]) -> list[tuple[dict[str, Any], int, float]]:
    aps = state.get("wifi.aps") if isinstance(state.get("wifi.aps"), list) else []
    out = []
    for ap in aps:
        if not isinstance(ap, dict):
            continue
        ch = _int_or_none(ap.get("channel"))
        rssi = _number(ap.get("rssi"))
        if ch is None or rssi is None:
            continue
        out.append((ap, ch, rssi))
    return out


def _rf_plot(draw: ImageDraw.ImageDraw, state: dict[str, Any], *, origin=(181, 146)) -> int:
    valid = _valid_aps(state)
    ox, oy = origin
    for radius in (34, 65, 94):
        draw.ellipse((ox - radius, oy - int(radius * .55), ox + radius, oy + int(radius * .55)), outline=(68, 74, 52))
    draw.ellipse((ox - 5, oy - 5, ox + 5, oy + 5), fill=_ACCENT)
    for idx, (ap, ch, rssi) in enumerate(valid[:16]):
        angle = math.radians((ch * 23 + idx * 47) % 360)
        radius = max(22, min(92, int((abs(rssi) - 27) * 1.34)))
        x = int(ox + math.cos(angle) * radius)
        y = int(oy + math.sin(angle) * radius * .55)
        col = _WATER if bool(ap.get("handshake")) else _PAPER
        draw.line((ox, oy, x, y), fill=(66, 71, 51))
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=_FIELD_DEEP, outline=col)
    return len(valid)


def _beast_fieldmark(draw: ImageDraw.ImageDraw, meta: dict[str, Any]) -> None:
    # Deliberately a field-sketch companion, not a dashboard avatar.
    x, y = 22, 168
    mood = str(meta.get("expression") or "awake").lower()
    alert = mood in {"focused", "hunting", "intense", "angry"}

    draw.line((x, y + 55, x + 128, y + 55), fill=_EDGE)
    draw.text((x, y + 2), "COMPANION", fill=_MUTED, font=_font(8))

    head = [
        (x + 12, y + 28), (x + 19, y + 17), (x + 31, y + 14),
        (x + 43, y + 19), (x + 49, y + 29), (x + 45, y + 42),
        (x + 34, y + 48), (x + 21, y + 46), (x + 13, y + 38),
    ]
    draw.polygon(head, fill=_FIELD_DEEP, outline=_PAPER)
    draw.polygon([(x + 16, y + 22), (x + 14, y + 8), (x + 25, y + 17)], fill=_FIELD_DEEP, outline=_ACCENT)
    draw.polygon([(x + 36, y + 17), (x + 45, y + 7), (x + 46, y + 24)], fill=_FIELD_DEEP, outline=_ACCENT)
    eye = _ALERT if alert else _INK
    draw.line((x + 21, y + 29, x + 27, y + 28), fill=eye, width=2)
    draw.line((x + 35, y + 28, x + 41, y + 29), fill=eye, width=2)
    if alert:
        draw.line((x + 25, y + 38, x + 39, y + 38), fill=_ACCENT)
    else:
        draw.arc((x + 25, y + 34, x + 39, y + 42), 15, 165, fill=_MUTED)

    level = "—" if meta.get("level") is None else str(meta["level"])
    draw.text((x + 58, y + 16), str(meta.get("stage") or "BEAST").upper()[:12], fill=_INK, font=_font(10))
    draw.text((x + 58, y + 31), f"LV {level} / {mood.upper()[:10]}", fill=_ACCENT, font=_font(8))


def _instrument_spine(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((355, 40, 471, 268), fill=_FIELD_DEEP, outline=_EDGE)
    draw.line((366, 48, 366, 259), fill=_ACCENT, width=2)
    for y in range(50, 260, 14):
        length = 8 if ((y - 50) // 14) % 4 == 0 else 4
        draw.line((366, y, 366 + length, y), fill=_EDGE)


def _instrument(draw: ImageDraw.ImageDraw, y: int, label: str, primary: str, secondary: str = "", *, accent=False) -> None:
    draw.text((382, y), label, fill=_MUTED, font=_font(8))
    draw.text((382, y + 13), primary[:14], fill=_ACCENT if accent else _INK, font=_font(12))
    if secondary:
        draw.text((382, y + 30), secondary[:16], fill=_MUTED, font=_font(8))
    draw.ellipse((362, y + 5, 370, y + 13), fill=_ACCENT if accent else _EDGE)


def _fmt(value: float | None, unit: str) -> str:
    return "—" if value is None else f"{value:.0f}{unit}"


def _journey_strip(draw: ImageDraw.ImageDraw, state: dict[str, Any], meta: dict[str, Any]) -> None:
    draw.rectangle((8, 231, 350, 268), fill=_HEADER, outline=_EDGE)
    draw.line((18, 237, 18, 262), fill=_ACCENT, width=2)
    if meta["expedition_active"] is True:
        active, col = "EXPEDITION ACTIVE", _ACCENT
    elif meta["expedition_active"] is False:
        active, col = "EXPEDITION IDLE", _MUTED
    else:
        active, col = "EXPEDITION —", _MUTED
    draw.text((29, 238), active, fill=col, font=_font(9))
    captures = reading(state, "expedition.captures_delta")
    xp = reading(state, "expedition.xp_delta")
    draw.text((29, 252), f"CAP +{format_reading(captures)}", fill=_INK if captures.known else _MUTED, font=_font(8))
    draw.text((115, 252), f"XP +{format_reading(xp)}", fill=_INK if xp.known else _MUTED, font=_font(8))
    draw.text((224, 244), "FIELD LOG", fill=_MUTED, font=_font(8))
    draw.line((278, 249, 337, 249), fill=_EDGE)


def render_atlas_home(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Atlas Home v2: authored expedition fieldbook using only truthful telemetry."""
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
    _contours(d, phase)
    _compass(d)

    d.rectangle((17, 47, 135, 67), fill=_FIELD_DEEP, outline=_EDGE)
    d.text((24, 52), "FIELD CONTEXT", fill=_PAPER, font=_font(9))
    d.text((144, 52), "RELATIVE RF / NOT POSITION", fill=_MUTED, font=_font(8))

    observed = _rf_plot(d, state)
    if observed == 0:
        d.text((137, 137), "NO RF OBSERVATIONS", fill=_MUTED, font=_font(9))

    # A route is only drawn when GPS fix + route-point truth support it.
    if meta["draw_route"]:
        route = [(82, 188), (119, 166), (158, 174), (207, 134), (260, 144), (308, 111)]
        d.line(route, fill=_ACCENT, width=3)
        for x, y in route:
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=_PAPER)
        d.rectangle((18, 76, 91, 93), fill=_FIELD_DEEP)
        d.text((24, 80), "ROUTE LIVE", fill=_ACCENT, font=_font(8))
    else:
        status_col = _ALERT if meta["gps_fix"] is False else _MUTED
        d.rectangle((18, 76, 112, 111), fill=_FIELD_DEEP, outline=_EDGE)
        d.text((24, 81), meta["gps_status"], fill=status_col, font=_font(8))
        sats = reading(state, "gps.satellites_used")
        d.text((24, 96), f"SATS {format_reading(sats)}", fill=_MUTED, font=_font(8))

    _beast_fieldmark(d, meta)
    _register(rt, SceneLayerSpec(
        "atlas_v2.home.field", "environment", (8, 40, 351, 227),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))
    _register(rt, SceneLayerSpec(
        "atlas_v2.home.beast", "creature", (18, 168, 151, 226),
        signals=("progression.stage", "progression.level", "beast.expression", "pwnagotchi.mood"),
        update_class="live",
    ))

    _instrument_spine(d)
    channel = format_reading(meta["channel_reading"])
    band = meta["band"] if meta["band"] != "?" else "BAND —"
    _instrument(d, 51, "RADIO", f"CH {channel}", band, accent=meta["channel"] is not None)

    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    nearby = format_reading(meta["nearby_reading"])
    _instrument(d, 103, "DISCOVERY", f"{unique} UNIQUE", f"{nearby} NEARBY")

    _instrument(d, 155, "JOURNEY", _fmt(meta["distance_m"], " m"), _fmt(meta["duration_sec"], " sec"))

    temp = format_reading(meta["temp_reading"])
    gov = format_reading(meta["governor_reading"])
    _instrument(d, 207, "READINESS", temp, f"GOV {gov}")

    _register(rt, SceneLayerSpec(
        "atlas_v2.home.instruments", "instrument", (355, 40, 472, 269),
        signals=(
            "radio.primary.channel", "radio.primary.band", "expedition.ap_unique",
            "wifi.ap_count", "expedition.distance_m", "expedition.duration_sec",
            "system.temp.cpu_c", "governor.mode",
        ),
        update_class="live",
    ))

    _journey_strip(d, state, meta)
    _register(rt, SceneLayerSpec(
        "atlas_v2.home.log", "timeline", (8, 231, 351, 269),
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
    """Atlas Recon v2: relative RF survey; screen geometry never claims location."""
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

    d.rectangle((17, 47, 127, 67), fill=_FIELD_DEEP, outline=_EDGE)
    d.text((24, 52), "RF SURVEY", fill=_PAPER, font=_font(9))
    d.text((138, 52), "RSSI RELATIVE / NOT POSITION", fill=_MUTED, font=_font(8))

    cx, cy = 178, 146
    for radius in (36, 70, 104):
        d.ellipse((cx - radius, cy - int(radius * .58), cx + radius, cy + int(radius * .58)), outline=_CONTOUR)
    d.line((cx - 122, cy, cx + 122, cy), fill=_CONTOUR)
    d.line((cx, cy - 70, cx, cy + 70), fill=_CONTOUR)

    # A subtle sweep supplies motion language only; AP positions remain RSSI-relative.
    sweep = (phase * 0.55) % (math.pi * 2)
    sx = int(cx + math.cos(sweep) * 108)
    sy = int(cy + math.sin(sweep) * 60)
    d.line((cx, cy, sx, sy), fill=_WATER)

    valid = _valid_aps(state)
    band_counts = {"2.4": 0, "5": 0}
    for idx, (ap, ch, rssi) in enumerate(valid[:24]):
        band_counts["2.4" if ch <= 14 else "5"] += 1
        angle = math.radians((ch * 19 + idx * 31) % 360)
        radius = max(18, min(102, int((abs(rssi) - 26) * 1.34)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .58)
        col = _WATER if bool(ap.get("handshake")) else _PAPER
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=_FIELD_DEEP, outline=col, width=2)
        d.text((x + 6, y - 5), str(ch), fill=_MUTED, font=_font(8))

    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=_ACCENT)
    d.text((cx - 17, cy + 13), "BEAST", fill=_INK, font=_font(8))
    if not valid:
        d.text((119, 199), "NO RF OBSERVATIONS", fill=_MUTED, font=_font(9))

    _register(rt, SceneLayerSpec(
        "atlas_v2.recon.survey", "graph", (8, 40, 351, 227),
        signals=("wifi.aps", "wifi.ap_count"), update_class="live", decorative=False,
    ))

    _instrument_spine(d)
    _instrument(d, 51, "BANDS", f"2.4G  {band_counts['2.4']}", f"5G    {band_counts['5']}")
    hs = reading(state, "wifi.handshake_ap_count")
    hidden = reading(state, "wifi.hidden_count")
    _instrument(d, 103, "SURVEY", f"HS {format_reading(hs)}", f"HID {format_reading(hidden)}")
    sats = reading(state, "gps.satellites_used")
    _instrument(d, 155, "POSITION", meta["gps_status"], f"SATS {format_reading(sats)}", accent=meta["gps_fix"] is True)
    channel = format_reading(meta["channel_reading"])
    _instrument(d, 207, "TUNED", f"CH {channel}", meta["band"] if meta["band"] != "?" else "BAND —", accent=meta["channel"] is not None)

    d.rectangle((8, 231, 350, 268), fill=_HEADER, outline=_EDGE)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    d.text((20, 239), f"FIELD SESSION / {unique} UNIQUE", fill=_ACCENT, font=_font(9))
    d.text((20, 254), "RINGS = SIGNAL DISTANCE  •  DOTS = OBSERVED AP", fill=_MUTED, font=_font(8))

    _register(rt, SceneLayerSpec(
        "atlas_v2.recon.instruments", "instrument", (355, 40, 472, 269),
        signals=(
            "wifi.aps", "wifi.handshake_ap_count", "wifi.hidden_count",
            "gps.fix", "gps.satellites_used", "radio.primary.channel", "radio.primary.band",
        ),
        update_class="live",
    ))

    _nav(d, shell, rt)
    return im
