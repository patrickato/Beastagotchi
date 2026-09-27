from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import (
    BeastShellModel,
    SHELL_TYPE,
    QUALITY_CAPTURED,
    QUALITY_LIVE,
    QUALITY_STALE,
    build_shell_model,
    format_reading,
    reading,
)
from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)
_BG = (18, 22, 24)
_PANEL = (28, 34, 36)
_PANEL_2 = (34, 41, 43)
_EDGE = (81, 96, 99)
_INK = (224, 232, 228)
_MUTED = (139, 153, 151)
_TRACE = (147, 195, 177)
_TRACE_2 = (111, 155, 181)
_WARN = (203, 150, 91)
_CRITICAL = (210, 104, 86)


def _font(size=11):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _shell(state: dict[str, Any], page_id: str) -> BeastShellModel:
    shell = state.get("_beast_shell")
    if isinstance(shell, BeastShellModel) and shell.page_id == page_id:
        return shell
    return build_shell_model("observatory", page_id, state, ("home", "spectrum"))


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


def _attention_color(shell: BeastShellModel):
    if shell.attention.level == "critical":
        return _CRITICAL
    if shell.attention.level == "warning":
        return _WARN
    if shell.attention.level == "normal":
        return _TRACE
    return _TRACE_2


def observatory_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state or {})
    aps_present = "wifi.aps" in state and isinstance(state.get("wifi.aps"), list)
    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)] if aps_present else []
    capture = state.get("_beast_capture") or {}

    channels = sorted({int(x.get("channel")) for x in aps if _int_or_none(x.get("channel")) is not None})
    rssis = [float(x["rssi"]) for x in aps if _number(x.get("rssi")) is not None]

    aps_reading = reading(state, "wifi.aps")
    ap_count = len(aps) if aps_present else None
    channel_reading = reading(state, "radio.primary.channel")
    cpu_reading = reading(state, "system.cpu.total", unit="%")
    temp_reading = reading(state, "system.temp.cpu_c", unit="°C")
    memory_reading = reading(state, "system.memory.used_pct", unit="%")

    capture_kind = str(capture.get("kind") or ("live" if aps_present else "unknown"))
    capture_date = str(capture.get("captured_date") or "")
    observation_quality = aps_reading.quality
    if capture and observation_quality == QUALITY_LIVE:
        observation_quality = QUALITY_CAPTURED

    return {
        # Preserve established metadata keys for callers/tests.
        "ap_count": ap_count,
        "channels": channels,
        "rssi_min": min(rssis) if rssis else None,
        "rssi_max": max(rssis) if rssis else None,
        "cpu_pct": _number(cpu_reading.value),
        "temp_c": _number(temp_reading.value),
        "memory_pct": _number(memory_reading.value),
        "capture_kind": capture_kind,
        "capture_date": capture_date,
        "gps_fix": bool(state.get("gps.fix")) if "gps.fix" in state else None,
        "channel": _int_or_none(channel_reading.value),
        # Truth-bearing forms used by the renderer.
        "aps": aps,
        "aps_reading": aps_reading,
        "channel_reading": channel_reading,
        "cpu_reading": cpu_reading,
        "temp_reading": temp_reading,
        "memory_reading": memory_reading,
        "observation_quality": observation_quality,
        "observation_source": str(state.get("wifi.aps.source") or capture_kind or ""),
        "observation_age_s": _number(state.get("wifi.aps.age_s")),
    }


def _draw_shell_status(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    col = _attention_color(shell)
    draw.line((10, 32, 470, 32), fill=_EDGE)
    draw.ellipse((12, 12, 22, 22), fill=col)
    draw.text((31, 9), shell.status_sentence, fill=_INK, font=_font(SHELL_TYPE.caption))
    draw.text((400, 9), "OBSERVE", fill=_TRACE, font=_font(SHELL_TYPE.caption))
    _register(rt, SceneLayerSpec(
        f"observatory.{shell.page_id}.shell_status", "text", (8, 4, 472, 34),
        signals=("health.core.state", "system.temp.cpu_c", "pwnagotchi.service.state",
                 "bettercap.service.state", "radio.monitor.state"), update_class="live",
    ))


def _draw_shell_nav(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=(15, 19, 21))
    draw.line((0, y, 479, y), fill=_TRACE_2)
    draw.line((160, y + 8, 160, 312), fill=_EDGE)
    draw.line((320, y + 8, 320, 312), fill=_EDGE)

    if nav.previous_enabled:
        text = f"‹ {nav.previous_page.upper()}"
        draw.text((18, y + 18), text, fill=_TRACE_2, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"observatory.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))

    center = nav.position_text
    box = draw.textbbox((0, 0), center, font=_font(SHELL_TYPE.body))
    draw.text((240 - (box[2] - box[0]) // 2, y + 18), center,
              fill=_TRACE, font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        f"observatory.{nav.page_id}.nav_position", "text", nav.center_box,
        update_class="static",
    ))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        box = draw.textbbox((0, 0), text, font=_font(SHELL_TYPE.caption))
        draw.text((462 - (box[2] - box[0]), y + 18), text,
                  fill=_TRACE_2, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"observatory.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))


def _channel_x(channel: int, x1: int, x2: int) -> int:
    """Split-band projection: never imply that Wi-Fi channel numbers are linear frequency."""
    span = x2 - x1
    split = x1 + int(span * 0.43)
    gap = 18
    if channel <= 14:
        return x1 + int(max(0, min(13, channel - 1)) / 13.0 * max(1, split - x1 - gap // 2))
    lo = split + gap // 2
    return lo + int(max(0, min(129, channel - 36)) / 129.0 * max(1, x2 - lo))


def _draw_rf_spectrum(draw: ImageDraw.ImageDraw, state: dict[str, Any], box, meta):
    x1, y1, x2, y2 = box
    px1, py1, px2, py2 = x1 + 30, y1 + 28, x2 - 8, y2 - 22
    draw.line((px1, py2, px2, py2), fill=_EDGE)
    draw.line((px1, py1, px1, py2), fill=_EDGE)

    # Useful, labelled scale. Minor ticks may be small; primary meaning is not.
    for db in (-30, -50, -70, -90):
        frac = max(0.0, min(1.0, (db + 100.0) / 70.0))
        y = py2 - int(frac * (py2 - py1))
        draw.line((px1 - 4, y, px1, y), fill=_EDGE)
        draw.text((x1 + 2, y - 5), str(db), fill=_MUTED, font=_font(9))
    split = px1 + int((px2 - px1) * 0.43)
    draw.line((split, py1, split, py2), fill=(48, 58, 60))
    draw.text((px1 + 34, py2 + 5), "2.4 GHz", fill=_MUTED, font=_font(9))
    draw.text((split + 46, py2 + 5), "5 GHz", fill=_MUTED, font=_font(9))

    for row in meta["aps"][:32]:
        ch = _int_or_none(row.get("channel"))
        rssi = _number(row.get("rssi"))
        if ch is None or rssi is None:
            continue
        x = _channel_x(ch, px1, px2)
        strength = max(0.0, min(1.0, (rssi + 100.0) / 70.0))
        y = py2 - int(strength * (py2 - py1))
        color = _TRACE_2 if bool(row.get("handshake")) else _TRACE
        draw.line((x, py2, x, y), fill=color, width=2)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline=color, fill=_BG)

    if meta["channel_reading"].known:
        ch = int(float(meta["channel_reading"].value))
        cx = _channel_x(ch, px1, px2)
        draw.line((cx, py1, cx, py2), fill=_WARN, width=1)
        draw.text((max(px1, cx - 16), py1), f"CH {ch}", fill=_WARN, font=_font(10))


def _draw_band_counts(draw: ImageDraw.ImageDraw, box, meta):
    x1, y1, x2, y2 = box
    buckets = (("2.4", 0), ("5 LOW", 0), ("5 HIGH", 0))
    vals = {label: 0 for label, _ in buckets}
    for row in meta["aps"]:
        ch = _int_or_none(row.get("channel"))
        if ch is None:
            continue
        if ch <= 14:
            vals["2.4"] += 1
        elif ch <= 64:
            vals["5 LOW"] += 1
        else:
            vals["5 HIGH"] += 1

    draw.line((x1, y1, x2, y1), fill=_EDGE)
    draw.text((x1 + 2, y1 + 7), "CURRENT BAND COUNT", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    maxv = max(1, max(vals.values()))
    for idx, label in enumerate(("2.4", "5 LOW", "5 HIGH")):
        bx = x1 + 112 + idx * 72
        val = vals[label]
        h = int((val / maxv) * 31)
        draw.rectangle((bx, y2 - h - 14, bx + 24, y2 - 14), fill=_TRACE if idx == 0 else _TRACE_2)
        draw.text((bx + 6, y2 - h - 28), str(val), fill=_INK, font=_font(SHELL_TYPE.caption))
        draw.text((bx - 5, y2 - 10), label, fill=_MUTED, font=_font(9))


def _observer(draw: ImageDraw.ImageDraw, state: dict[str, Any], shell: BeastShellModel):
    cx, cy = 411, 88
    mood = str(state.get("pwnagotchi.mood") or "unknown").lower()
    alert = shell.attention.level in {"critical", "warning"}
    eye_col = _attention_color(shell)

    draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(22, 27, 29), outline=_EDGE)
    draw.arc((cx - 40, cy - 40, cx + 40, cy + 40), 198, 344, fill=_TRACE, width=2)
    draw.arc((cx - 40, cy - 40, cx + 40, cy + 40), 18, 153, fill=_TRACE_2, width=1)
    shell_pts = [
        (cx, cy - 27), (cx + 19, cy - 21), (cx + 27, cy - 6),
        (cx + 25, cy + 14), (cx + 14, cy + 27), (cx, cy + 31),
        (cx - 14, cy + 27), (cx - 25, cy + 14), (cx - 27, cy - 6),
        (cx - 19, cy - 21),
    ]
    draw.polygon(shell_pts, fill=_PANEL_2, outline=eye_col)
    draw.line((cx - 16, cy - 5, cx - 6, cy - 7), fill=eye_col, width=2)
    draw.line((cx + 6, cy - 7, cx + 16, cy - 5), fill=eye_col, width=2)
    draw.ellipse((cx - 2, cy - 1, cx + 2, cy + 3), fill=_INK)
    if alert:
        draw.line((cx - 10, cy + 15, cx + 10, cy + 15), fill=eye_col, width=2)
    elif mood in {"happy", "excited", "awake"}:
        draw.arc((cx - 12, cy + 5, cx + 12, cy + 20), 18, 162, fill=_TRACE, width=2)
    else:
        draw.line((cx - 10, cy + 15, cx + 10, cy + 15), fill=_TRACE_2, width=2)


def _quality_label(meta) -> str:
    q = str(meta["observation_quality"] or "unknown").upper()
    if q == QUALITY_CAPTURED.upper() and meta["capture_date"]:
        return "CAPTURED"
    return q


def _draw_provenance(draw: ImageDraw.ImageDraw, state: dict[str, Any], meta, shell, rt=None):
    draw.line((350, 39, 350, 258), fill=_TRACE)
    _observer(draw, state, shell)
    _register(rt, SceneLayerSpec(
        "observatory.observer", "creature", (370, 44, 452, 132),
        signals=("pwnagotchi.mood", "beast.expression", "health.core.state",
                 "pwnagotchi.service.state", "bettercap.service.state"), update_class="live",
    ))

    draw.line((360, 137, 470, 137), fill=_EDGE)
    draw.text((360, 145), "PROVENANCE", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    source = str(meta["observation_source"] or "UNKNOWN").replace("_", " ").upper()[:17]
    draw.text((360, 166), source, fill=_INK, font=_font(SHELL_TYPE.caption))
    q = _quality_label(meta)
    qcol = _WARN if q in {"STALE", "UNKNOWN", "ERROR"} else _TRACE
    draw.text((360, 187), q, fill=qcol, font=_font(SHELL_TYPE.label))
    if meta["capture_date"]:
        draw.text((360, 211), meta["capture_date"][:16], fill=_MUTED, font=_font(SHELL_TYPE.caption))
    elif meta["observation_age_s"] is not None:
        draw.text((360, 211), f"AGE {meta['observation_age_s']:.0f}s", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    gps = "GPS FIX" if meta["gps_fix"] is True else "GPS NO FIX" if meta["gps_fix"] is False else "GPS —"
    draw.text((360, 234), gps, fill=_TRACE if meta["gps_fix"] else _MUTED, font=_font(SHELL_TYPE.caption))
    _register(rt, SceneLayerSpec(
        "observatory.provenance", "instrument", (350, 137, 474, 260),
        signals=("wifi.aps", "wifi.aps.quality", "wifi.aps.source", "wifi.aps.age_s", "gps.fix"),
        update_class="live",
    ))


def render_observatory_home(state: dict[str, Any], *, phase: float = 0.0,
                            scene_runtime: SceneRuntime | None = None) -> Image.Image:
    state = dict(state or {})
    meta = observatory_home_metadata(state)
    shell = _shell(state, "home")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:observatory:home", theme_id="experience.observatory")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_shell_status(d, shell, rt)

    d.text((12, 43), "RF OBSERVATION", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    _draw_rf_spectrum(d, state, (10, 38, 342, 198), meta)
    _register(rt, SceneLayerSpec(
        "observatory.spectrum", "graph", (10, 38, 342, 198),
        signals=("wifi.aps", "radio.primary.channel"), update_class="live",
    ))

    _draw_band_counts(d, (10, 202, 342, 258), meta)
    _register(rt, SceneLayerSpec(
        "observatory.distribution", "graph", (10, 202, 342, 258),
        signals=("wifi.aps",), update_class="live",
    ))

    _draw_provenance(d, state, meta, shell, rt)
    _draw_shell_nav(d, shell, rt)
    return im


def render_observatory_spectrum(state: dict[str, Any], *, phase: float = 0.0,
                                scene_runtime: SceneRuntime | None = None) -> Image.Image:
    state = dict(state or {})
    meta = observatory_home_metadata(state)
    shell = _shell(state, "spectrum")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="spectrum", scene_id="experience:observatory:spectrum",
                 theme_id="experience.observatory")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_shell_status(d, shell, rt)

    d.text((12, 43), "CHANNEL OCCUPANCY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    _draw_rf_spectrum(d, state, (10, 38, 390, 196), meta)
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.occupancy", "graph", (10, 38, 390, 196),
        signals=("wifi.aps", "radio.primary.channel"), update_class="live",
    ))

    # Measurement margin stays factual. Unknown is a dash, not zero.
    draw_x = 400
    d.line((draw_x, 40, draw_x, 258), fill=_TRACE)
    d.text((410, 46), "MEASURE", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    ap_text = "—" if meta["ap_count"] is None else str(meta["ap_count"])
    chs_text = "—" if not meta["aps_reading"].known else str(len(meta["channels"]))
    peak_text = "—" if meta["rssi_max"] is None else f"{meta['rssi_max']:.0f}"
    d.text((410, 70), f"APS {ap_text}", fill=_INK, font=_font(SHELL_TYPE.label))
    d.text((410, 96), f"CHS {chs_text}", fill=_INK, font=_font(SHELL_TYPE.label))
    d.text((410, 122), f"PEAK {peak_text}", fill=_INK, font=_font(SHELL_TYPE.caption))
    d.line((408, 145, 470, 145), fill=_EDGE)
    d.text((410, 155), "QUALITY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    q = _quality_label(meta)
    d.text((410, 178), q[:10], fill=_WARN if q == "STALE" else _TRACE,
           font=_font(SHELL_TYPE.label))
    tuned = format_reading(meta["channel_reading"])
    d.text((410, 215), f"CH {tuned}", fill=_WARN if meta["channel_reading"].known else _MUTED,
           font=_font(SHELL_TYPE.label))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.measure", "instrument", (400, 40, 474, 258),
        signals=("wifi.aps", "wifi.aps.quality", "radio.primary.channel"), update_class="live",
    ))

    d.line((10, 202, 390, 202), fill=_EDGE)
    d.text((12, 210), "CURRENT OBSERVATION", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    strongest = max(meta["aps"], key=lambda row: _number(row.get("rssi")) or -1000, default=None)
    if strongest is not None and _number(strongest.get("rssi")) is not None:
        sch = _int_or_none(strongest.get("channel"))
        srssi = _number(strongest.get("rssi"))
        text = f"STRONGEST  CH {sch if sch is not None else '—'}  {srssi:.0f} dBm"
    elif meta["aps_reading"].known:
        text = "NO OBSERVATIONS IN CURRENT SAMPLE"
    else:
        text = "OBSERVATION INPUT UNKNOWN"
    d.text((12, 235), text, fill=_INK, font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.summary", "instrument", (10, 202, 390, 258),
        signals=("wifi.aps",), update_class="live",
    ))

    # Static semantic marker replaces the old developer-facing truth disclaimer.
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.truth", "semantic", (0, 0, 1, 1),
        signals=(), update_class="static", decorative=True,
    ))

    _draw_shell_nav(d, shell, rt)
    return im
