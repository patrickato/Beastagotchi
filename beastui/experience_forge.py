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
    state = dict(state or {})
    meta = forge_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:forge:home", theme_id="experience.forge")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 479, 30), fill=(35, 33, 29))
    d.text((10, 7), "FORGE", fill=_AMBER, font=_font(15))
    d.text((68, 9), "MACHINE BAY", fill=_MUTED, font=_font(9))
    health = meta["core_state"].upper()
    d.text((394, 9), health, fill=_OK if health == "HEALTHY" else _WARN, font=_font(9))
    _register(rt, SceneLayerSpec(
        "forge.header", "text", (0, 0, 480, 31),
        signals=("health.core.state",), update_class="live",
    ))

    # Upper machine modules.
    _module(
        d, (12, 42, 148, 128), "COMPUTE",
        f"CPU {meta['cpu_pct']:.0f}%",
        f"{meta['temp_c']:.0f} C · MEM {meta['memory_pct']:.0f}%",
        status="ok" if meta["temp_c"] < 75 else "warn",
    )
    _module(
        d, (172, 42, 308, 128), "RADIO",
        f"CH {meta['channel']}",
        f"{meta['band']} · { _i(state, 'wifi.ap_count') } AP",
        status="ok",
    )
    power_primary = "TELEM OK" if meta["power_available"] else "NO SENSOR"
    _module(
        d, (332, 42, 468, 128), "POWER",
        power_primary,
        meta["ups_state"].replace("_", " ").upper(),
        status="ok" if meta["power_available"] else "normal",
    )
    _register(rt, SceneLayerSpec(
        "forge.compute", "instrument", (12, 42, 148, 128),
        signals=("system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.radio", "instrument", (172, 42, 308, 128),
        signals=("radio.primary.channel", "radio.primary.band", "wifi.ap_count"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.power", "instrument", (332, 42, 468, 128),
        signals=("power.telemetry.available", "power.ups.state"), update_class="live",
    ))

    _bus(d)
    _core_emblem(d, state)
    _register(rt, SceneLayerSpec(
        "forge.machine_bus", "shape", (42, 133, 438, 178),
        signals=("health.core.state",), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.beast_core", "creature", (208, 123, 264, 179),
        signals=("progression.level", "pwnagotchi.mood", "beast.expression"), update_class="live",
    ))

    # Lower modules are wider and operational, deliberately unlike Atlas's edge instruments.
    ethernet = "LINK UP" if meta["ethernet"] else "NO LINK"
    _module(
        d, (12, 184, 226, 270), "I/O + CAPABILITIES",
        f"{meta['capabilities']} CAPABILITIES",
        f"ETH {ethernet}",
        status="ok" if meta["ethernet"] else "normal",
    )
    doctor_primary = "READY" if meta["attention_count"] == 0 and health == "HEALTHY" else f"{meta['attention_count']} ATTENTION"
    _module(
        d, (242, 184, 468, 270), "DOCTOR / GOVERNOR",
        doctor_primary,
        meta["governor"].upper(),
        status="ok" if doctor_primary == "READY" else "warn",
    )
    _register(rt, SceneLayerSpec(
        "forge.io", "instrument", (12, 184, 226, 270),
        signals=("capabilities.count", "network.ethernet.carrier"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.doctor", "instrument", (242, 184, 468, 270),
        signals=("overview.attention", "health.core.state", "governor.mode"), update_class="live",
    ))

    # Footer is a machine-state rail, not app navigation.
    d.rectangle((12, 284, 468, 310), fill=_METAL_2)
    d.text((22, 292), "MACHINE", fill=_MUTED, font=_font(8))
    d.text((83, 292), health, fill=_OK if health == "HEALTHY" else _WARN, font=_font(9))
    d.text((180, 292), "DOCK", fill=_MUTED, font=_font(8))
    d.text((220, 292), str(state.get("dock.state") or "?").upper(), fill=_INK, font=_font(9))
    d.text((310, 292), "GOV", fill=_MUTED, font=_font(8))
    d.text((346, 292), meta["governor"].upper(), fill=_AMBER, font=_font(9))
    _register(rt, SceneLayerSpec(
        "forge.state_rail", "text", (12, 284, 468, 310),
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
