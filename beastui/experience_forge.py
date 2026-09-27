from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import BeastShellModel, SHELL_TYPE, build_shell_model, format_reading, reading
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


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _shell(state: dict[str, Any], page_id: str) -> BeastShellModel:
    shell = state.get("_beast_shell")
    if isinstance(shell, BeastShellModel) and shell.page_id == page_id:
        return shell
    return build_shell_model("forge", page_id, state, ("home", "system"))


def _attention_color(shell: BeastShellModel):
    if shell.attention.level in {"critical", "warning"}:
        return _WARN
    if shell.attention.level == "normal":
        return _OK
    return _EDGE


def forge_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state or {})
    attention = state.get("overview.attention")

    cpu = reading(state, "system.cpu.total", unit="%")
    temp = reading(state, "system.temp.cpu_c", unit="°C")
    memory = reading(state, "system.memory.used_pct", unit="%")
    channel = reading(state, "radio.primary.channel")
    ethernet = reading(state, "network.ethernet.carrier")
    power = reading(state, "power.telemetry.available")
    capabilities = reading(state, "capabilities.count")
    governor = reading(state, "governor.mode")
    monitor = reading(state, "radio.monitor.state")

    return {
        # Established public keys remain available for callers/tests.
        "core_state": str(state.get("health.core.state") or "unknown"),
        "cpu_pct": _number(cpu.value) if cpu.known else None,
        "temp_c": _number(temp.value) if temp.known else None,
        "memory_pct": _number(memory.value) if memory.known else None,
        "channel": _int_or_none(channel.value) if channel.known else None,
        "band": str(state.get("radio.primary.band") or "?") if "radio.primary.band" in state else "?",
        "ethernet": bool(ethernet.value) if ethernet.known else None,
        "power_available": bool(power.value) if power.known else None,
        "ups_state": str(state.get("power.ups.state") or "unknown"),
        "governor": str(governor.value) if governor.known else "unknown",
        "capabilities": _int_or_none(capabilities.value) if capabilities.known else None,
        "attention_count": len(attention) if isinstance(attention, list) else None,
        "attention_known": isinstance(attention, list),
        # Truth-bearing forms for rendering.
        "cpu_reading": cpu,
        "temp_reading": temp,
        "memory_reading": memory,
        "channel_reading": channel,
        "ethernet_reading": ethernet,
        "power_reading": power,
        "capabilities_reading": capabilities,
        "governor_reading": governor,
        "monitor_reading": monitor,
    }


def _draw_header(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    col = _attention_color(shell)
    draw.rectangle((0, 0, 479, 33), fill=(31, 30, 27))
    draw.line((0, 32, 479, 32), fill=_EDGE, width=2)
    draw.text((10, 6), "FORGE", fill=_AMBER, font=_font(SHELL_TYPE.label))
    draw.text((67, 9), "MACHINE BAY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    draw.ellipse((292, 11, 302, 21), fill=col)
    box = draw.textbbox((0, 0), shell.status_sentence, font=_font(SHELL_TYPE.caption))
    draw.text((468 - (box[2] - box[0]), 8), shell.status_sentence,
              fill=_INK if shell.attention.level != "notice" else _MUTED,
              font=_font(SHELL_TYPE.caption))
    _register(rt, SceneLayerSpec(
        f"forge.{shell.page_id}.shell_status", "text", (0, 0, 480, 34),
        signals=("health.core.state", "system.temp.cpu_c", "pwnagotchi.service.state",
                 "bettercap.service.state", "radio.monitor.state"), update_class="live",
    ))
    if shell.page_id == "home":
        _register(rt, SceneLayerSpec(
            "forge.header", "text", (0, 0, 480, 34),
            signals=("health.core.state",), update_class="live",
        ))
    else:
        _register(rt, SceneLayerSpec(
            "forge_system.header", "text", (0, 0, 480, 34),
            signals=("health.core.state",), update_class="live",
        ))


def _draw_nav(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=(31, 30, 27))
    draw.line((0, y, 479, y), fill=_EDGE, width=2)
    draw.line((160, y + 8, 160, 312), fill=_METAL_2)
    draw.line((320, y + 8, 320, 312), fill=_METAL_2)

    if nav.previous_enabled:
        text = f"‹ {nav.previous_page.upper()}"
        draw.text((18, y + 18), text, fill=_AMBER, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"forge.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))

    center = nav.position_text
    box = draw.textbbox((0, 0), center, font=_font(SHELL_TYPE.body))
    draw.text((240 - (box[2] - box[0]) // 2, y + 18), center,
              fill=_MUTED, font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        f"forge.{nav.page_id}.nav_position", "text", nav.center_box,
        update_class="static",
    ))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        box = draw.textbbox((0, 0), text, font=_font(SHELL_TYPE.caption))
        draw.text((462 - (box[2] - box[0]), y + 18), text,
                  fill=_AMBER, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"forge.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))


def _chassis(draw: ImageDraw.ImageDraw):
    outer = [(8, 46), (18, 38), (461, 38), (471, 48), (471, 252), (461, 260), (18, 260), (8, 252)]
    inner = [(13, 58), (21, 52), (458, 52), (466, 59), (466, 246), (458, 253), (21, 253), (13, 246)]
    draw.polygon(outer, fill=(35, 34, 30), outline=_EDGE)
    draw.polygon(inner, fill=(27, 27, 24), outline=_METAL_2)
    for x in (160, 320):
        draw.line((x, 55, x, 246), fill=_METAL_2, width=3)
        for y in (66, 139, 207, 241):
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=_EDGE, outline=_BG)
    for x, y in ((23, 61), (456, 61), (23, 244), (456, 244)):
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=_EDGE, outline=_BG)


def _bay_label(draw, x1, x2, label, state_text="", state_color=_MUTED):
    draw.line((x1, 58, x2, 58), fill=_EDGE)
    draw.text((x1 + 6, 42), label, fill=_MUTED, font=_font(SHELL_TYPE.caption))
    if state_text:
        box = draw.textbbox((0, 0), state_text, font=_font(10))
        draw.text((x2 - 6 - (box[2] - box[0]), 43), state_text,
                  fill=state_color, font=_font(10))


def _dial(draw, center, radius, reading_row, *, warn=False):
    cx, cy = center
    edge = _WARN if warn else _OK
    draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), 205, 335, fill=_EDGE, width=3)
    value = _number(reading_row.value) if reading_row.known else None
    if value is not None:
        bounded = max(0.0, min(100.0, value))
        draw.arc((cx - radius, cy - radius, cx + radius, cy + radius),
                 205, 205 + int(130 * bounded / 100.0), fill=edge, width=4)
        angle = math.radians(205 + 130 * bounded / 100.0)
        nx = cx + int((radius - 7) * math.cos(angle))
        ny = cy + int((radius - 7) * math.sin(angle))
        draw.line((cx, cy, nx, ny), fill=_INK, width=2)
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=_AMBER)
    text = format_reading(reading_row)
    font = _font(SHELL_TYPE.title)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, cy - 10), text,
              fill=_INK if reading_row.known else _MUTED, font=font)


def _port(draw, x, y, state: bool | None):
    col = _OK if state is True else _EDGE
    draw.rectangle((x, y, x + 24, y + 15), outline=col, width=2)
    draw.line((x + 5, y + 5, x + 19, y + 5), fill=col)
    draw.line((x + 5, y + 10, x + 19, y + 10), fill=col)


def _beast_core(draw, shell: BeastShellModel, phase: float):
    cx, cy = 240, 157
    col = _attention_color(shell) if shell.attention.level in {"critical", "warning"} else _AMBER
    draw.rectangle((24, 153, 455, 161), fill=_METAL_2)
    draw.line((24, 157, 455, 157), fill=_AMBER, width=2)
    for x in (54, 127, 201, 279, 353, 426):
        draw.ellipse((x - 4, 153, x + 4, 161), fill=_AMBER, outline=_BG)
    draw.polygon([(cx, cy - 27), (cx + 24, cy - 14), (cx + 24, cy + 14),
                  (cx, cy + 27), (cx - 24, cy + 14), (cx - 24, cy - 14)],
                 fill=_BG, outline=col, width=2)
    draw.polygon([(cx, cy - 13), (cx + 12, cy), (cx, cy + 13), (cx - 12, cy)], outline=_INK)
    draw.text((cx - 18, cy - 6), "BEAST", fill=_INK, font=_font(8))

    pulse = 0.5 + 0.5 * math.sin(float(phase) * 2.2)
    r = 29 + int(round(pulse * 2))
    draw.arc((cx - r, cy - r, cx + r, cy + r), 205, 335, fill=_EDGE, width=1)


def _monitor_text(meta) -> tuple[str, tuple[int, int, int]]:
    row = meta["monitor_reading"]
    if not row.known:
        return "MONITOR —", _MUTED
    word = str(row.value).strip().lower()
    if word in {"up", "active", "ready", "monitor", "running"}:
        return "MONITOR UP", _OK
    if word in {"offline", "down", "failed", "failure"}:
        return "MONITOR DOWN", _WARN
    return f"MONITOR {str(row.value).upper()[:8]}", _MUTED


def render_forge_home(state: dict[str, Any], *, phase: float = 0.0,
                      scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Forge Home: one readable machine chassis, not a pile of mini dashboards."""
    state = dict(state or {})
    meta = forge_home_metadata(state)
    shell = _shell(state, "home")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:forge:home", theme_id="experience.forge")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_header(d, shell, rt)
    _chassis(d)

    # Compute bay: one gauge, temperature and memory. No tiny duplicate telemetry.
    temp_text = format_reading(meta["temp_reading"])
    temp_num = meta["temp_c"]
    _bay_label(d, 14, 158, "COMPUTE", temp_text,
               _WARN if temp_num is not None and temp_num >= 75 else _OK if temp_num is not None else _MUTED)
    _dial(d, (77, 103), 37, meta["cpu_reading"], warn=temp_num is not None and temp_num >= 75)
    d.text((56, 132), "CPU", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    mem_text = format_reading(meta["memory_reading"])
    d.text((112, 84), "MEM", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    d.text((112, 104), mem_text, fill=_INK if meta["memory_reading"].known else _MUTED,
           font=_font(SHELL_TYPE.label))
    _register(rt, SceneLayerSpec(
        "forge.compute", "instrument", (14, 38, 158, 148),
        signals=("system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct"), update_class="live",
    ))

    # Radio bay: channel/band/observed AP count without a fake linear channel ruler.
    band = meta["band"].upper() if meta["band"] != "?" else "BAND —"
    _bay_label(d, 164, 318, "RADIO", band, _OK if meta["band"] != "?" else _MUTED)
    d.text((178, 69), "CHANNEL", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    ch_text = format_reading(meta["channel_reading"])
    d.text((178, 86), ch_text, fill=_INK if meta["channel_reading"].known else _MUTED,
           font=_font(30))
    aps = reading(state, "wifi.ap_count")
    ap_text = f"{format_reading(aps)} AP" if aps.known else "AP —"
    d.text((254, 94), ap_text, fill=_AMBER if aps.known else _MUTED,
           font=_font(SHELL_TYPE.body))
    d.line((176, 126, 306, 126), fill=_EDGE, width=2)
    for x in range(178, 307, 21):
        d.line((x, 121, x, 131), fill=_MUTED)
    monitor_text, monitor_col = _monitor_text(meta)
    d.text((176, 135), monitor_text, fill=monitor_col, font=_font(10))
    _register(rt, SceneLayerSpec(
        "forge.radio", "instrument", (164, 38, 318, 148),
        signals=("radio.primary.channel", "radio.primary.band", "wifi.ap_count", "radio.monitor.state"),
        update_class="live",
    ))

    # Power bay: absence is an explicit fact, not fabricated telemetry.
    if meta["power_available"] is True:
        power_state, power_col = "SENSOR", _OK
        power_primary = "KNOWN"
    elif meta["power_available"] is False:
        power_state, power_col = "NO SENSOR", _EDGE
        power_primary = "UNAVAILABLE"
    else:
        power_state, power_col = "STATUS —", _MUTED
        power_primary = "UNKNOWN"
    _bay_label(d, 324, 465, "POWER", power_state, power_col)
    d.line((343, 82, 343, 132), fill=power_col, width=3)
    for y in (84, 100, 116, 132):
        d.line((336, y, 350, y), fill=power_col, width=2)
    d.text((360, 78), "TELEMETRY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    d.text((360, 98), power_primary, fill=power_col, font=_font(SHELL_TYPE.body))
    ups = meta["ups_state"].replace("_", " ").upper()
    d.text((360, 124), ups[:15], fill=_AMBER if ups != "UNKNOWN" else _MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "forge.power", "instrument", (324, 38, 466, 148),
        signals=("power.telemetry.available", "power.ups.state"), update_class="live",
    ))

    _beast_core(d, shell, phase)
    _register(rt, SceneLayerSpec(
        "forge.machine_bus", "shape", (20, 130, 460, 184),
        signals=("health.core.state",), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.beast_core", "creature", (214, 130, 266, 184),
        signals=("progression.level", "pwnagotchi.mood", "beast.expression"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "forge.ambient_chassis", "ambient", (20, 128, 460, 186),
        update_class="ambient", reduced_motion="static", decorative=True,
    ))

    # Service floor: two readable zones rather than a row of tiny labels.
    d.line((18, 188, 286, 188), fill=_EDGE)
    d.text((20, 194), "I/O FABRIC", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    _port(d, 20, 216, meta["ethernet"])
    _port(d, 54, 216, True if meta["channel"] is not None else None)
    _port(d, 88, 216, True if meta["capabilities"] is not None and meta["capabilities"] > 0 else None)
    eth_text = "ETH UP" if meta["ethernet"] is True else "ETH DOWN" if meta["ethernet"] is False else "ETH —"
    caps_text = "CAP —" if meta["capabilities"] is None else f"CAP {meta['capabilities']}"
    d.text((128, 211), eth_text, fill=_OK if meta["ethernet"] is True else _MUTED,
           font=_font(SHELL_TYPE.body))
    d.text((128, 232), caps_text, fill=_INK if meta["capabilities"] is not None else _MUTED,
           font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        "forge.io", "instrument", (14, 188, 294, 254),
        signals=("capabilities.count", "network.ethernet.carrier", "radio.primary.channel"), update_class="live",
    ))

    d.line((300, 188, 459, 188), fill=_EDGE)
    d.text((310, 194), "DOCTOR / GOVERNOR", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    if meta["attention_known"] and meta["attention_count"] == 0 and shell.attention.level == "normal":
        doctor_text, doctor_col = "READY", _OK
    elif meta["attention_known"] and meta["attention_count"] is not None:
        doctor_text, doctor_col = f"{meta['attention_count']} ATTENTION", _WARN
    else:
        doctor_text, doctor_col = "STATUS —", _MUTED
    d.ellipse((310, 222, 326, 238), fill=doctor_col)
    d.text((338, 217), doctor_text, fill=_INK, font=_font(SHELL_TYPE.body))
    gov = format_reading(meta["governor_reading"])
    d.text((338, 239), f"GOV {gov}", fill=_AMBER if meta["governor_reading"].known else _MUTED,
           font=_font(10))
    _register(rt, SceneLayerSpec(
        "forge.doctor", "instrument", (302, 188, 460, 254),
        signals=("overview.attention", "health.core.state", "governor.mode"), update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im


def render_forge_system(state: dict[str, Any], *, scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Forge System: service access to the same chassis with truthful subsystem facts."""
    state = dict(state or {})
    meta = forge_home_metadata(state)
    shell = _shell(state, "system")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="system", scene_id="experience:forge:system", theme_id="experience.forge")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_header(d, shell, rt)

    d.rectangle((8, 39, 471, 258), fill=(35, 34, 30), outline=_EDGE, width=2)
    d.rectangle((13, 55, 466, 252), fill=(27, 27, 24), outline=_METAL_2)
    d.rectangle((238, 55, 242, 252), fill=_METAL_2)

    # Compute service bay.
    d.text((20, 44), "COMPUTE SERVICE", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    _dial(d, (78, 112), 41, meta["cpu_reading"],
          warn=meta["temp_c"] is not None and meta["temp_c"] >= 75)
    d.text((58, 145), "CPU", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    temp = format_reading(meta["temp_reading"])
    mem = format_reading(meta["memory_reading"])
    d.text((137, 83), "THERMAL", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    d.text((137, 102), temp, fill=_WARN if meta["temp_c"] is not None and meta["temp_c"] >= 75 else _INK,
           font=_font(SHELL_TYPE.label))
    d.text((137, 132), "MEMORY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    d.text((137, 151), mem, fill=_INK if meta["memory_reading"].known else _MUTED,
           font=_font(SHELL_TYPE.label))
    _register(rt, SceneLayerSpec(
        "forge_system.compute", "instrument", (14, 39, 236, 176),
        signals=("system.cpu.total", "system.temp.cpu_c", "system.memory.used_pct"), update_class="live",
    ))

    # I/O service bay.
    d.text((252, 44), "I/O SERVICE", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    _port(d, 258, 82, meta["ethernet"])
    _port(d, 296, 82, True if meta["channel"] is not None else None)
    _port(d, 334, 82, True if meta["capabilities"] is not None and meta["capabilities"] > 0 else None)
    _port(d, 372, 82, meta["power_available"])
    caps = "—" if meta["capabilities"] is None else str(meta["capabilities"])
    channel = format_reading(meta["channel_reading"])
    d.text((258, 117), f"CAPABILITIES {caps}", fill=_INK if meta["capabilities"] is not None else _MUTED,
           font=_font(SHELL_TYPE.body))
    d.text((258, 143), f"RADIO CH {channel}", fill=_AMBER if meta["channel_reading"].known else _MUTED,
           font=_font(SHELL_TYPE.body))
    eth = "LINK UP" if meta["ethernet"] is True else "NO LINK" if meta["ethernet"] is False else "LINK —"
    d.text((258, 166), eth, fill=_OK if meta["ethernet"] is True else _MUTED,
           font=_font(SHELL_TYPE.caption))
    _register(rt, SceneLayerSpec(
        "forge_system.io", "instrument", (244, 39, 466, 176),
        signals=("network.ethernet.carrier", "capabilities.count", "radio.primary.channel"), update_class="live",
    ))

    # Decorative shared service bus.
    d.rectangle((24, 181, 456, 189), fill=_METAL_2)
    d.line((24, 185, 456, 185), fill=_AMBER, width=2)
    for x in (58, 130, 202, 278, 350, 422):
        d.ellipse((x - 4, 181, x + 4, 189), fill=_AMBER, outline=_BG)
    _register(rt, SceneLayerSpec(
        "forge_system.bus", "shape", (22, 178, 458, 192),
        signals=(), update_class="static", decorative=True,
    ))

    # Lower power train.
    power_col = _OK if meta["power_available"] is True else _EDGE if meta["power_available"] is False else _MUTED
    d.text((20, 198), "POWER TRAIN", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    d.line((24, 218, 24, 246), fill=power_col, width=3)
    for y in (220, 232, 244):
        d.line((17, y, 31, y), fill=power_col, width=2)
    power_word = "ONLINE" if meta["power_available"] is True else "NO SENSOR" if meta["power_available"] is False else "UNKNOWN"
    d.text((45, 216), power_word, fill=power_col, font=_font(SHELL_TYPE.body))
    d.text((45, 239), meta["ups_state"].replace("_", " ").upper()[:20],
           fill=_AMBER if meta["ups_state"] != "unknown" else _MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "forge_system.power", "instrument", (14, 194, 226, 252),
        signals=("power.telemetry.available", "power.ups.state"), update_class="live",
    ))

    # Doctor/governor service stack.
    d.line((242, 196, 242, 252), fill=_METAL_2, width=2)
    d.text((258, 198), "DOCTOR / GOVERNOR", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    if meta["attention_known"] and meta["attention_count"] == 0 and shell.attention.level == "normal":
        doctor, doctor_col = "NO ACTIVE FAULTS", _OK
    elif meta["attention_known"] and meta["attention_count"] is not None:
        doctor, doctor_col = f"{meta['attention_count']} ATTENTION", _WARN
    else:
        doctor, doctor_col = "FAULT STATE —", _MUTED
    d.ellipse((258, 222, 274, 238), fill=doctor_col)
    d.text((286, 216), doctor, fill=_INK, font=_font(SHELL_TYPE.body))
    gov = format_reading(meta["governor_reading"])
    d.text((286, 239), f"GOV {gov}", fill=_AMBER if meta["governor_reading"].known else _MUTED,
           font=_font(10))
    _register(rt, SceneLayerSpec(
        "forge_system.doctor", "instrument", (244, 194, 466, 252),
        signals=("overview.attention", "health.core.state", "governor.mode"), update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im
