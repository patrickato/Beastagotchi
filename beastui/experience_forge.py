from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)
_BG = (24, 23, 21)
_METAL = (46, 45, 40)
_METAL_2 = (60, 57, 49)
_EDGE = (108, 98, 72)
_INK = (232, 224, 196)
_MUTED = (157, 150, 127)
_AMBER = (221, 153, 56)
_OK = (129, 175, 115)
_WARN = (208, 109, 68)


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


def forge_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    attention = state.get("overview.attention") or []
    return {
        "core_state": str(state.get("health.core.state") or "unknown"),
        "cpu_pct": _f(state, "system.cpu.total"),
        "temp_c": _f(state, "system.temp.cpu_c"),
        "memory_pct": _f(state, "system.memory.used_pct"),
        "channel": _i(state, "radio.primary.channel"),
        "band": str(state.get("radio.primary.band") or "?"),
        "ethernet": bool(state.get("network.ethernet.carrier")),
        "power_available": bool(state.get("power.telemetry.available")),
        "ups_state": str(state.get("power.ups.state") or "unknown"),
        "governor": str(state.get("governor.mode") or "unknown"),
        "capabilities": _i(state, "capabilities.count"),
        "attention_count": len(attention) if isinstance(attention, list) else 0,
    }


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _module(draw, box, title, primary, secondary, *, status="normal"):
    x1, y1, x2, y2 = box
    edge = _WARN if status == "warn" else _OK if status == "ok" else _EDGE
    draw.rounded_rectangle(box, radius=7, fill=_METAL, outline=edge, width=2)
    draw.rectangle((x1+5, y1+5, x1+10, y1+10), fill=edge)
    draw.text((x1+16, y1+5), title, fill=_MUTED, font=_font(8))
    draw.text((x1+10, y1+24), primary, fill=_INK, font=_font(14))
    draw.text((x1+10, y1+44), secondary, fill=_AMBER, font=_font(8))


def _dial(draw, center, radius, value, *, label, unit="", warn=False):
    cx, cy = center
    edge = _WARN if warn else _OK
    draw.arc((cx-radius, cy-radius, cx+radius, cy+radius), 205, 335, fill=_EDGE, width=3)
    draw.arc((cx-radius, cy-radius, cx+radius, cy+radius), 205, 205 + int(130 * max(0.0, min(100.0, value)) / 100.0), fill=edge, width=4)
    angle = 205 + 130 * max(0.0, min(100.0, value)) / 100.0
    import math
    rad = math.radians(angle)
    nx = cx + int((radius-8) * math.cos(rad))
    ny = cy + int((radius-8) * math.sin(rad))
    draw.line((cx, cy, nx, ny), fill=_INK, width=2)
    draw.ellipse((cx-3, cy-3, cx+3, cy+3), fill=_AMBER)
    draw.text((cx-radius+3, cy+radius-12), label, fill=_MUTED, font=_font(7))
    value_text = f"{value:.0f}{unit}"
    tw = draw.textbbox((0,0), value_text, font=_font(12))[2]
    draw.text((cx-tw//2, cy-7), value_text, fill=_INK, font=_font(12))


def _bay_title(draw, x1, x2, label, state_text, *, state_color=_MUTED):
    draw.line((x1, 49, x2, 49), fill=_EDGE, width=1)
    draw.text((x1+6, 37), label, fill=_MUTED, font=_font(8))
    bbox = draw.textbbox((0,0), state_text, font=_font(7))
    draw.text((x2-6-(bbox[2]-bbox[0]), 38), state_text, fill=state_color, font=_font(7))


def _port(draw, x, y, *, active=False):
    col = _OK if active else _EDGE
    draw.rectangle((x, y, x+18, y+12), outline=col, width=1)
    draw.line((x+4, y+4, x+14, y+4), fill=col)
    draw.line((x+4, y+8, x+14, y+8), fill=col)


def _bus(draw):
    draw.line((46, 150, 434, 150), fill=_EDGE, width=3)
    for x in (82, 232, 386):
        draw.ellipse((x-5, 145, x+5, 155), fill=_AMBER, outline=_BG)
    draw.text((194, 139), "SYSTEM BUS", fill=_MUTED, font=_font(8))


def _core_emblem(draw, state):
    cx, cy = 236, 151
    draw.ellipse((cx-28, cy-28, cx+28, cy+28), fill=_BG, outline=_AMBER, width=2)
    draw.polygon([(cx, cy-17), (cx+15, cy), (cx, cy+17), (cx-15, cy)], outline=_INK)
    draw.text((cx-17, cy-5), "BEAST", fill=_INK, font=_font(8))


def render_forge_home(state: dict[str, Any], *, scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Forge Home as one continuous machine-bay scene, not a card dashboard."""
    state = dict(state or {})
    meta = forge_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:forge:home", theme_id="experience.forge")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    health = meta["core_state"].upper()
    health_col = _OK if health == "HEALTHY" else _WARN

    # Header: stamped machine identity, deliberately flat/no card chrome.
    d.rectangle((0, 0, 479, 29), fill=(31, 30, 27))
    d.rectangle((0, 28, 479, 30), fill=_EDGE)
    d.text((10, 6), "FORGE", fill=_AMBER, font=_font(15))
    d.text((70, 9), "MACHINE BAY // ACTIVE CHASSIS", fill=_MUTED, font=_font(8))
    d.ellipse((445, 9, 455, 19), fill=health_col)
    d.text((386, 9), health, fill=health_col, font=_font(8))
    _register(rt, SceneLayerSpec(
        "forge.header", "text", (0, 0, 480, 31),
        signals=("health.core.state",), update_class="live",
    ))

    # One chassis occupies the screen. Subsystems are separated by frame rails,
    # not rounded independent cards.
    d.rectangle((8, 36, 471, 275), fill=(35, 34, 30), outline=_EDGE, width=2)
    d.rectangle((12, 53, 467, 264), fill=(27, 27, 24), outline=_METAL_2)
    for x in (160, 320):
        d.rectangle((x-2, 52, x+2, 264), fill=_METAL_2)
        for y in (62, 132, 205, 252):
            d.ellipse((x-4, y-2, x+4, y+6), fill=_EDGE, outline=_BG)

    # COMPUTE bay: one physical gauge plus memory rail.
    _bay_title(d, 14, 158, "COMPUTE CORE", f"{meta['temp_c']:.0f}C", state_color=_OK if meta["temp_c"] < 75 else _WARN)
    _dial(d, (75, 102), 39, meta["cpu_pct"], label="CPU LOAD", unit="%", warn=meta["temp_c"] >= 75)
    mem = max(0.0, min(100.0, meta["memory_pct"]))
    d.text((118, 73), "MEM", fill=_MUTED, font=_font(7))
    d.rectangle((120, 87, 132, 132), outline=_EDGE)
    fill_h = int(43 * mem / 100.0)
    d.rectangle((122, 130-fill_h, 130, 130), fill=_AMBER)
    d.text((109, 137), f"{mem:.0f}%", fill=_INK, font=_font(9))
    _register(rt, SceneLayerSpec(
        "forge.compute", "instrument", (14, 34, 158, 148),
        signals=("system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct"), update_class="live",
    ))

    # RADIO bay: frequency ruler and channel are embedded in the chassis.
    _bay_title(d, 164, 318, "RADIO DECK", meta["band"], state_color=_OK)
    d.text((181, 66), "CHANNEL", fill=_MUTED, font=_font(7))
    d.text((181, 78), f"{meta['channel']:02d}", fill=_INK, font=_font(30))
    ap_count = _i(state, "wifi.ap_count")
    d.text((257, 81), f"{ap_count} AP", fill=_AMBER, font=_font(10))
    d.line((176, 121, 306, 121), fill=_EDGE, width=2)
    for idx, x in enumerate(range(178, 307, 16)):
        h = 9 if idx % 2 == 0 else 5
        d.line((x, 121-h, x, 121+h), fill=_MUTED)
    pos = 178 + int(126 * max(0, min(165, meta["channel"])) / 165.0)
    d.polygon([(pos,108),(pos-5,116),(pos+5,116)], fill=_AMBER)
    d.text((176, 134), "RF FABRIC ONLINE", fill=_OK, font=_font(7))
    _register(rt, SceneLayerSpec(
        "forge.radio", "instrument", (164, 34, 318, 148),
        signals=("radio.primary.channel", "radio.primary.band", "wifi.ap_count"), update_class="live",
    ))

    # POWER bay is truthful about absent telemetry; still looks like hardware.
    power_col = _OK if meta["power_available"] else _EDGE
    power_state = "SENSOR ONLINE" if meta["power_available"] else "NO SENSOR"
    _bay_title(d, 324, 465, "POWER TRAIN", power_state, state_color=power_col)
    d.line((341, 82, 341, 132), fill=power_col, width=3)
    for y in (84, 100, 116, 132):
        d.line((335, y, 347, y), fill=power_col, width=2)
    d.text((359, 78), "TELEMETRY", fill=_MUTED, font=_font(7))
    d.text((359, 94), "KNOWN" if meta["power_available"] else "UNAVAILABLE", fill=power_col, font=_font(10))
    d.text((359, 115), meta["ups_state"].replace("_"," ").upper()[:16], fill=_AMBER, font=_font(7))
    _register(rt, SceneLayerSpec(
        "forge.power", "instrument", (324, 34, 466, 148),
        signals=("power.telemetry.available", "power.ups.state"), update_class="live",
    ))

    # Shared bus physically binds every subsystem. Beast is the machine core.
    d.rectangle((24, 155, 455, 163), fill=_METAL_2)
    d.line((24, 159, 455, 159), fill=_AMBER, width=2)
    for x in (53, 127, 201, 279, 353, 427):
        d.ellipse((x-4, 155, x+4, 163), fill=_AMBER, outline=_BG)
    cx, cy = 240, 159
    d.polygon([(cx,cy-28),(cx+24,cy-14),(cx+24,cy+14),(cx,cy+28),(cx-24,cy+14),(cx-24,cy-14)],
              fill=_BG, outline=_AMBER)
    d.polygon([(cx,cy-14),(cx+12,cy),(cx,cy+14),(cx-12,cy)], outline=_INK)
    d.text((cx-15,cy-4),"BEAST",fill=_INK,font=_font(7))
    _register(rt, SceneLayerSpec(
        "forge.machine_bus", "shape", (20, 130, 460, 190),
        signals=("health.core.state",), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.beast_core", "creature", (214, 130, 266, 188),
        signals=("progression.level", "pwnagotchi.mood", "beast.expression"), update_class="live",
    ))

    # Lower machine bay: ports/capabilities on the left, fault/governor stack on right.
    d.line((14, 194, 465, 194), fill=_EDGE)
    d.text((18, 181), "I/O FABRIC", fill=_MUTED, font=_font(8))
    ethernet = bool(meta["ethernet"])
    _port(d, 20, 207, active=ethernet)
    _port(d, 45, 207, active=meta["channel"] > 0)
    _port(d, 70, 207, active=meta["capabilities"] > 0)
    d.text((20, 226), f"{meta['capabilities']} CAPABILITIES", fill=_INK, font=_font(11))
    d.text((20, 244), "ETH LINK UP" if ethernet else "ETH NO LINK", fill=_OK if ethernet else _MUTED, font=_font(8))
    d.text((120, 244), f"RADIO CH {meta['channel']}", fill=_AMBER, font=_font(8))
    for x in range(20, 284, 18):
        d.line((x, 256, x+10, 256), fill=_METAL_2)
    _register(rt, SceneLayerSpec(
        "forge.io", "instrument", (14, 178, 294, 263),
        signals=("capabilities.count", "network.ethernet.carrier", "radio.primary.channel"), update_class="live",
    ))

    d.rectangle((302, 200, 458, 258), outline=_EDGE, width=1)
    d.text((312, 207), "DOCTOR / GOVERNOR", fill=_MUTED, font=_font(8))
    attention = meta["attention_count"]
    doctor_text = "READY" if attention == 0 and health == "HEALTHY" else f"{attention} ATTENTION"
    d.ellipse((312, 226, 326, 240), fill=_OK if doctor_text == "READY" else _WARN)
    d.text((335, 224), doctor_text, fill=_INK, font=_font(11))
    d.text((335, 242), f"GOV {meta['governor'].upper()}", fill=_AMBER, font=_font(8))
    _register(rt, SceneLayerSpec(
        "forge.doctor", "instrument", (302, 198, 460, 262),
        signals=("overview.attention", "health.core.state", "governor.mode"), update_class="live",
    ))

    # Bottom machine rail: concise context, no app/nav chrome.
    d.rectangle((8, 282, 471, 311), fill=_METAL)
    d.rectangle((8, 282, 471, 284), fill=_EDGE)
    d.text((18, 292), "MACHINE", fill=_MUTED, font=_font(7))
    d.text((63, 290), health, fill=health_col, font=_font(9))
    d.text((162, 292), "DOCK", fill=_MUTED, font=_font(7))
    d.text((195, 290), str(state.get("dock.state") or "?").upper()[:10], fill=_INK, font=_font(9))
    d.text((302, 292), "GOV", fill=_MUTED, font=_font(7))
    d.text((330, 290), meta["governor"].upper()[:12], fill=_AMBER, font=_font(9))
    _register(rt, SceneLayerSpec(
        "forge.state_rail", "text", (8, 282, 472, 312),
        signals=("health.core.state", "dock.state", "governor.mode"), update_class="live",
    ))

    return im



def render_forge_system(
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Forge translation of System: machine subsystems + Doctor/governor context."""
    state = dict(state or {})
    meta = forge_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="system", scene_id="experience:forge:system", theme_id="experience.forge")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 479, 30), fill=(35, 33, 29))
    d.text((10, 7), "FORGE", fill=_AMBER, font=_font(15))
    d.text((68, 9), "SYSTEM BAY", fill=_MUTED, font=_font(9))
    health = meta["core_state"].upper()
    d.text((394, 9), health, fill=_OK if health == "HEALTHY" else _WARN, font=_font(9))
    _register(rt, SceneLayerSpec(
        "forge_system.header", "text", (0, 0, 480, 31),
        signals=("health.core.state",), update_class="live",
    ))

    # Left powertrain: compute and memory are shown as one physical subsystem.
    _module(
        d, (12, 42, 224, 126), "COMPUTE CORE",
        f"CPU {meta['cpu_pct']:.0f}% · {meta['temp_c']:.0f} C",
        f"MEMORY {meta['memory_pct']:.1f}%",
        status="ok" if meta["temp_c"] < 75 else "warn",
    )
    _register(rt, SceneLayerSpec(
        "forge_system.compute", "instrument", (12, 42, 224, 126),
        signals=("system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct"),
        update_class="live",
    ))

    # Right I/O module: connectivity/capabilities without pretending at detailed topology.
    ethernet = "LINK UP" if meta["ethernet"] else "NO LINK"
    _module(
        d, (244, 42, 468, 126), "I/O FABRIC",
        ethernet,
        f"{meta['capabilities']} CAPABILITIES · RADIO CH {meta['channel']}",
        status="ok" if meta["ethernet"] else "normal",
    )
    _register(rt, SceneLayerSpec(
        "forge_system.io", "instrument", (244, 42, 468, 126),
        signals=("network.ethernet.carrier", "capabilities.count", "radio.primary.channel"),
        update_class="live",
    ))

    # Central machine bus visually joins the subsystems.
    d.line((44, 151, 436, 151), fill=_EDGE, width=4)
    for x in (82, 238, 394):
        d.ellipse((x-6,145,x+6,157), fill=_AMBER, outline=_BG)
    d.text((197, 137), "MACHINE BUS", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "forge_system.bus", "shape", (40, 134, 440, 160),
        signals=(), update_class="static", decorative=True,
    ))

    # Power/telemetry is explicit about absence.
    power_primary = "TELEMETRY ONLINE" if meta["power_available"] else "NO POWER SENSOR"
    _module(
        d, (12, 174, 224, 258), "POWER TRAIN",
        power_primary,
        meta["ups_state"].replace("_", " ").upper(),
        status="ok" if meta["power_available"] else "normal",
    )
    _register(rt, SceneLayerSpec(
        "forge_system.power", "instrument", (12, 174, 224, 258),
        signals=("power.telemetry.available", "power.ups.state"),
        update_class="live",
    ))

    attention = meta["attention_count"]
    doctor_primary = "NO ACTIVE FAULTS" if attention == 0 and health == "HEALTHY" else f"{attention} ATTENTION"
    _module(
        d, (244, 174, 468, 258), "DOCTOR / GOVERNOR",
        doctor_primary,
        f"GOVERNOR {meta['governor'].upper()}",
        status="ok" if doctor_primary == "NO ACTIVE FAULTS" else "warn",
    )
    _register(rt, SceneLayerSpec(
        "forge_system.doctor", "instrument", (244, 174, 468, 258),
        signals=("overview.attention", "health.core.state", "governor.mode"),
        update_class="live",
    ))

    # Bottom rail is machine context, not page navigation.
    d.rectangle((12, 278, 468, 309), fill=_METAL_2)
    d.text((22, 288), f"CORE {health}", fill=_OK if health == "HEALTHY" else _WARN, font=_font(8))
    d.text((154, 288), f"GOV {meta['governor'].upper()}", fill=_AMBER, font=_font(8))
    d.text((286, 288), f"POWER {'KNOWN' if meta['power_available'] else 'UNKNOWN'}", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "forge_system.rail", "text", (12, 278, 468, 310),
        signals=("health.core.state", "governor.mode", "power.telemetry.available"),
        update_class="live",
    ))
    return im
