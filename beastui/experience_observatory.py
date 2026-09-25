from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

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


def observatory_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)]
    capture = state.get("_beast_capture") or {}
    channels = sorted({int(x.get("channel") or 0) for x in aps if x.get("channel") is not None})
    rssis = []
    for row in aps:
        try:
            rssis.append(float(row.get("rssi")))
        except Exception:
            pass
    return {
        "ap_count": len(aps),
        "channels": channels,
        "rssi_min": min(rssis) if rssis else None,
        "rssi_max": max(rssis) if rssis else None,
        "cpu_pct": _f(state, "system.cpu.total"),
        "temp_c": _f(state, "system.temp.cpu_c"),
        "memory_pct": _f(state, "system.memory.used_pct"),
        "capture_kind": str(capture.get("kind") or "live"),
        "capture_date": str(capture.get("captured_date") or ""),
        "gps_fix": bool(state.get("gps.fix")),
        "channel": _i(state, "radio.primary.channel"),
    }


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _plot_frame(draw, box, title):
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=_PANEL, outline=_EDGE, width=1)
    draw.text((x1+8, y1+5), title, fill=_MUTED, font=_font(8))
    # Sparse scientific axes, not decorative grid.
    draw.line((x1+24, y2-18, x2-8, y2-18), fill=_EDGE)
    draw.line((x1+24, y1+22, x1+24, y2-18), fill=_EDGE)


def _draw_rf_spectrum(draw, state, box):
    x1, y1, x2, y2 = box
    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)]
    px1, py1, px2, py2 = x1+24, y1+22, x2-8, y2-18
    span_x = max(1, px2-px1)
    span_y = max(1, py2-py1)

    for row in aps[:32]:
        try:
            channel = int(row.get("channel") or 0)
            rssi = float(row.get("rssi") or -100)
        except Exception:
            continue
        x = px1 + int(max(0, min(165, channel)) / 165.0 * span_x)
        strength = max(0.0, min(1.0, (rssi + 100.0) / 70.0))
        y = py2 - int(strength * span_y)
        color = _TRACE_2 if bool(row.get("handshake")) else _TRACE
        draw.line((x, py2, x, y), fill=color, width=2)
        draw.ellipse((x-3, y-3, x+3, y+3), outline=color, fill=_BG)

    # Real current tuned channel marker.
    ch = _i(state, "radio.primary.channel")
    cx = px1 + int(max(0, min(165, ch)) / 165.0 * span_x)
    draw.line((cx, py1, cx, py2), fill=_WARN, width=1)
    draw.text((max(px1, cx-12), py1), f"CH {ch}", fill=_WARN, font=_font(7))


def _draw_channel_distribution(draw, state, box):
    x1, y1, x2, y2 = box
    aps = [x for x in (state.get("wifi.aps") or []) if isinstance(x, dict)]
    buckets = {"2.4": 0, "5L": 0, "5H": 0}
    for row in aps:
        try:
            ch = int(row.get("channel") or 0)
        except Exception:
            continue
        if ch <= 14:
            buckets["2.4"] += 1
        elif ch <= 64:
            buckets["5L"] += 1
        else:
            buckets["5H"] += 1
    maxv = max(1, max(buckets.values()))
    sx = x1+42
    base = y2-16
    for idx, (lab, val) in enumerate(buckets.items()):
        bx = sx + idx*84
        h = int((val/maxv) * 46)
        draw.rectangle((bx, base-h, bx+28, base), fill=_TRACE_2 if idx else _TRACE)
        draw.text((bx+5, base+3), lab, fill=_MUTED, font=_font(7))
        draw.text((bx+8, base-h-11), str(val), fill=_INK, font=_font(8))


def _observer(draw, state):
    # Supporting observer identity, intentionally small compared with measurements.
    cx, cy = 410, 92
    draw.ellipse((cx-38, cy-38, cx+38, cy+38), outline=_EDGE, fill=_PANEL)
    draw.arc((cx-24, cy-18, cx+24, cy+22), 15, 165, fill=_TRACE, width=2)
    draw.ellipse((cx-16, cy-4, cx-12, cy), fill=_INK)
    draw.ellipse((cx+12, cy-4, cx+16, cy), fill=_INK)
    mood = str(state.get("pwnagotchi.mood") or "awake").upper()
    draw.text((cx-22, cy+48), mood, fill=_MUTED, font=_font(8))


def render_observatory_home(state: dict[str, Any], *, scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Observatory Home as one continuous measurement station, not boxed widgets."""
    state = dict(state or {})
    meta = observatory_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:observatory:home", theme_id="experience.observatory")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    # Quiet lab header.
    d.rectangle((0, 0, 479, 30), fill=(23, 28, 30))
    d.text((10, 7), "OBSERVATORY", fill=_TRACE, font=_font(14))
    d.text((112, 9), "MEASUREMENT STATION // LIVE OBSERVATION", fill=_MUTED, font=_font(7))
    d.text((432, 9), f"{meta['ap_count']} AP", fill=_INK, font=_font(8))
    _register(rt, SceneLayerSpec(
        "observatory.header", "text", (0, 0, 480, 31),
        signals=("wifi.ap_count",), update_class="live",
    ))

    # Main instrument occupies a continuous lab surface. Sparse axes provide
    # measurement structure without a card/panel container.
    primary = (10, 40, 342, 205)
    d.text((12, 42), "RF OBSERVATION // CHANNEL / RSSI", fill=_MUTED, font=_font(8))
    d.line((34, 64, 34, 190), fill=_EDGE)
    d.line((34, 190, 336, 190), fill=_EDGE)
    # Tick marks are functional axis cues, not decorative grid.
    for x in range(34, 337, 50):
        d.line((x, 187, x, 193), fill=_EDGE)
    for y in range(70, 191, 30):
        d.line((31, y, 37, y), fill=_EDGE)
    _draw_rf_spectrum(d, state, (10, 42, 342, 208))
    _register(rt, SceneLayerSpec(
        "observatory.spectrum", "graph", primary,
        signals=("wifi.aps", "radio.primary.channel"), update_class="live",
    ))

    # Secondary distribution is an integrated comparison strip under the main
    # phenomenon rather than another framed plot card.
    secondary = (10, 214, 342, 284)
    d.line((10, 214, 342, 214), fill=_EDGE)
    d.text((12, 220), "OBSERVED BAND DISTRIBUTION", fill=_MUTED, font=_font(7))
    d.line((34, 271, 336, 271), fill=_EDGE)
    _draw_channel_distribution(d, state, (10, 218, 342, 287))
    _register(rt, SceneLayerSpec(
        "observatory.distribution", "graph", secondary,
        signals=("wifi.aps",), update_class="live",
    ))

    # A ruled observation margin holds identity + provenance. It is visually
    # part of the laboratory page, not a separate dashboard card.
    d.line((350, 38, 350, 286), fill=_TRACE, width=1)
    _observer(d, state)
    _register(rt, SceneLayerSpec(
        "observatory.observer", "creature", (366, 46, 454, 158),
        signals=("pwnagotchi.mood", "beast.expression"), update_class="live",
    ))

    d.line((358, 166, 470, 166), fill=_EDGE)
    d.text((360, 173), "PROVENANCE", fill=_MUTED, font=_font(7))
    kind = meta["capture_kind"].replace("_", " ").upper()
    d.text((360, 190), kind[:18], fill=_INK, font=_font(8))
    if meta["capture_date"]:
        d.text((360, 204), meta["capture_date"], fill=_MUTED, font=_font(7))
    d.line((358, 221, 470, 221), fill=_EDGE)
    gps = "FIX" if meta["gps_fix"] else "NO FIX"
    d.text((360, 228), f"GPS {gps}", fill=_WARN if not meta["gps_fix"] else _TRACE, font=_font(8))
    d.text((360, 244), f"CPU {meta['cpu_pct']:.0f}%  //  {meta['temp_c']:.0f} C", fill=_INK, font=_font(7))
    d.text((360, 260), f"MEM {meta['memory_pct']:.1f}%", fill=_INK, font=_font(7))
    d.text((360, 274), f"TUNED CH {meta['channel']}", fill=_WARN, font=_font(7))
    _register(rt, SceneLayerSpec(
        "observatory.provenance", "instrument", (350, 166, 470, 286),
        signals=("gps.fix", "system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct", "radio.primary.channel"),
        update_class="live",
    ))

    # Footer labels data truth explicitly.
    d.line((10, 298, 470, 298), fill=_EDGE)
    d.text((12, 304), "LIVE/CAPTURED OBSERVATIONS // NO SYNTHETIC HISTORY", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "observatory.truth_footer", "text", (10, 294, 470, 318),
        signals=(), update_class="static",
    ))
    return im



def render_observatory_spectrum(
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Observatory translation of Spectrum: measured occupancy + source quality."""
    state = dict(state or {})
    meta = observatory_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="spectrum", scene_id="experience:observatory:spectrum",
                 theme_id="experience.observatory")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    d.rectangle((0,0,479,30), fill=(23,28,30))
    d.text((10,7),"OBSERVATORY",fill=_TRACE,font=_font(14))
    d.text((112,9),"SPECTRUM LAB",fill=_MUTED,font=_font(8))
    d.text((408,9),f"CH {meta['channel']}",fill=_WARN,font=_font(9))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.header","text",(0,0,480,31),
        signals=("radio.primary.channel",),update_class="live",
    ))

    aps=[x for x in (state.get("wifi.aps") or []) if isinstance(x,dict)]
    by_channel={}
    for row in aps:
        try:
            ch=int(row.get("channel") or 0)
            rssi=float(row.get("rssi") or -100)
        except Exception:
            continue
        bucket=by_channel.setdefault(ch,{"count":0,"peak":-100.0,"handshakes":0})
        bucket["count"]+=1
        bucket["peak"]=max(bucket["peak"],rssi)
        if bool(row.get("handshake")): bucket["handshakes"]+=1

    # Main occupancy spectrum.
    box=(10,42,390,222)
    d.rectangle(box,fill=_PANEL,outline=_EDGE)
    d.text((20,51),"OBSERVED CHANNEL OCCUPANCY",fill=_MUTED,font=_font(8))
    x1,y1,x2,y2=34,72,378,201
    d.line((x1,y2,x2,y2),fill=_EDGE)
    d.line((x1,y1,x1,y2),fill=_EDGE)
    channels=sorted(by_channel)
    if channels:
        max_count=max(1,max(by_channel[ch]["count"] for ch in channels))
        for ch in channels:
            x=x1+int(max(0,min(165,ch))/165.0*(x2-x1))
            row=by_channel[ch]
            h=max(3,int(row["count"]/max_count*(y2-y1-18)))
            color=_TRACE_2 if row["handshakes"] else _TRACE
            d.rectangle((x-4,y2-h,x+4,y2),fill=color)
            d.text((x-5,y2+4),str(ch),fill=_MUTED,font=_font(6))
            if row["peak"] > -50:
                d.ellipse((x-3,y2-h-9,x+3,y2-h-3),outline=_WARN)
    tuned=meta["channel"]
    tx=x1+int(max(0,min(165,tuned))/165.0*(x2-x1))
    d.line((tx,y1,tx,y2),fill=_WARN,width=1)
    d.text((max(x1,tx-13),y1-12),f"TUNE {tuned}",fill=_WARN,font=_font(7))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.occupancy","graph",box,
        signals=("wifi.aps","radio.primary.channel"),update_class="live",
    ))

    # Measurement table column.
    side=(400,42,470,222)
    d.rectangle(side,fill=_PANEL_2,outline=_EDGE)
    d.text((409,51),"MEASURE",fill=_MUTED,font=_font(7))
    d.text((409,70),f"APS {meta['ap_count']}",fill=_INK,font=_font(9))
    d.text((409,88),f"CHS {len(channels)}",fill=_INK,font=_font(9))
    if meta["rssi_max"] is None:
        peak="?"
    else:
        peak=f"{meta['rssi_max']:.0f}"
    d.text((409,106),f"PEAK {peak}",fill=_INK,font=_font(8))
    d.text((409,132),"QUALITY",fill=_MUTED,font=_font(7))
    d.text((409,148),"CAPTURED",fill=_TRACE,font=_font(8))
    gps="GPS FIX" if meta["gps_fix"] else "GPS NO"
    d.text((409,166),gps,fill=_TRACE if meta["gps_fix"] else _WARN,font=_font(7))
    d.text((409,190),str(meta["capture_date"] or "")[:10],fill=_MUTED,font=_font(7))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.measure","instrument",side,
        signals=("wifi.aps","gps.fix"),update_class="live",
    ))

    # Lower correlation/readout area only shows derived facts from current observations.
    lower=(10,234,470,286)
    d.rectangle(lower,fill=_PANEL,outline=_EDGE)
    d.text((20,242),"CURRENT OBSERVATION SUMMARY",fill=_MUTED,font=_font(8))
    strongest = max(
        aps,
        key=lambda row: float(row.get("rssi") or -100),
        default=None,
    )
    if strongest:
        d.text((20,259),f"STRONGEST  CH {int(strongest.get('channel') or 0)}  {float(strongest.get('rssi') or -100):.0f} dBm",
               fill=_INK,font=_font(9))
    d.text((244,259),f"HANDSHAKE APS  {_i(state,'wifi.handshake_ap_count')}",
           fill=_INK,font=_font(9))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.summary","instrument",lower,
        signals=("wifi.aps","wifi.handshake_ap_count"),update_class="live",
    ))

    d.text((12,302),"LIVE/CAPTURED SPECTRUM · NO INVENTED TIME SERIES",fill=_MUTED,font=_font(8))
    _register(rt, SceneLayerSpec(
        "observatory_spectrum.truth","text",(10,294,470,318),
        signals=(),update_class="static",
    ))
    return im
