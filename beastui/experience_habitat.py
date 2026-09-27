from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import BeastShellModel, SHELL_TYPE, build_shell_model, format_reading, reading
from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE = (480, 320)
_BG = (40, 37, 31)
_SOIL = (75, 65, 49)
_LEAF = (95, 124, 82)
_LEAF_2 = (125, 150, 98)
_WARM = (219, 186, 116)
_INK = (242, 232, 201)
_MUTED = (169, 159, 128)
_HEALTH = (133, 179, 119)
_WARN = (206, 119, 85)


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
    return build_shell_model("habitat", page_id, state, ("home", "beast"))


def _attention_color(shell: BeastShellModel):
    if shell.attention.level in {"critical", "warning"}:
        return _WARN
    if shell.attention.level == "normal":
        return _HEALTH
    return _MUTED


def habitat_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    """Creature-facing truth. Missing counters/progression remain unknown."""
    state = dict(state or {})
    level = reading(state, "progression.level")
    progress = reading(state, "progression.level_progress_pct", unit="%")
    session = reading(state, "wifi.encounters.session_unique")
    nearby = reading(state, "wifi.ap_count")
    lifetime = reading(state, "wifi.encounters.lifetime_unique")
    captures = reading(state, "captures.total")
    expedition = reading(state, "expedition.active")
    mood = reading(state, "pwnagotchi.mood")
    expression = reading(state, "beast.expression")

    if session.known:
        discoveries = _int_or_none(session.value)
    elif nearby.known:
        discoveries = _int_or_none(nearby.value)
    else:
        discoveries = None

    return {
        "stage": str(state.get("progression.stage") or "Beast"),
        "level": _int_or_none(level.value) if level.known else None,
        "progress_pct": _number(progress.value) if progress.known else None,
        "mood": str(mood.value) if mood.known else "unknown",
        "expression": str(expression.value) if expression.known else "",
        "discoveries": discoveries,
        "lifetime": _int_or_none(lifetime.value) if lifetime.known else None,
        "captures": _int_or_none(captures.value) if captures.known else None,
        "health": str(state.get("health.core.state") or "unknown"),
        "expedition_active": bool(expedition.value) if expedition.known else None,
        "level_reading": level,
        "progress_reading": progress,
        "session_reading": session,
        "nearby_reading": nearby,
        "lifetime_reading": lifetime,
        "captures_reading": captures,
        "expedition_reading": expedition,
        "mood_reading": mood,
        "expression_reading": expression,
    }


def _draw_header(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None, *, page_label="HOME"):
    col = _attention_color(shell)
    draw.rectangle((0, 0, 479, 33), fill=(35, 34, 29))
    draw.line((0, 32, 479, 32), fill=_SOIL)
    draw.text((12, 6), "HABITAT", fill=_LEAF_2, font=_font(SHELL_TYPE.label))
    draw.text((89, 9), page_label, fill=_MUTED, font=_font(SHELL_TYPE.caption))
    draw.ellipse((292, 11, 302, 21), fill=col)
    box = draw.textbbox((0, 0), shell.status_sentence, font=_font(SHELL_TYPE.caption))
    draw.text((468 - (box[2] - box[0]), 8), shell.status_sentence,
              fill=_INK if shell.attention.level != "notice" else _MUTED,
              font=_font(SHELL_TYPE.caption))
    _register(rt, SceneLayerSpec(
        f"habitat.{shell.page_id}.shell_status", "text", (0, 0, 480, 34),
        signals=("health.core.state", "system.temp.cpu_c", "pwnagotchi.service.state",
                 "bettercap.service.state", "radio.monitor.state"), update_class="live",
    ))
    if shell.page_id == "home":
        _register(rt, SceneLayerSpec(
            "habitat.health", "text", (286, 5, 474, 29),
            signals=("health.core.state",), update_class="live",
        ))


def _draw_nav(draw: ImageDraw.ImageDraw, shell: BeastShellModel, rt=None):
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=(35, 34, 29))
    draw.line((0, y, 479, y), fill=_SOIL, width=2)
    draw.line((160, y + 8, 160, 312), fill=(60, 57, 45))
    draw.line((320, y + 8, 320, 312), fill=(60, 57, 45))

    if nav.previous_enabled:
        text = f"‹ {nav.previous_page.upper()}"
        draw.text((18, y + 18), text, fill=_LEAF_2, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"habitat.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))

    center = nav.position_text
    box = draw.textbbox((0, 0), center, font=_font(SHELL_TYPE.body))
    draw.text((240 - (box[2] - box[0]) // 2, y + 18), center,
              fill=_MUTED, font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        f"habitat.{nav.page_id}.nav_position", "text", nav.center_box, update_class="static",
    ))

    if nav.next_enabled:
        text = f"{nav.next_page.upper()} ›"
        box = draw.textbbox((0, 0), text, font=_font(SHELL_TYPE.caption))
        draw.text((462 - (box[2] - box[0]), y + 18), text,
                  fill=_LEAF_2, font=_font(SHELL_TYPE.caption))
        _register(rt, SceneLayerSpec(
            f"habitat.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))


def _draw_habitat(draw, phase, *, bottom=263):
    """Organic ambient environment; decorative motion never masquerades as telemetry."""
    cx = 238 + int(math.sin(phase * 0.23) * 2)
    cy = 151 + int(math.cos(phase * 0.17))
    draw.ellipse((cx-128, cy-118, cx+128, min(bottom, cy+118)), fill=(66, 58, 45))
    draw.ellipse((cx-105, cy-105, cx+101, min(bottom, cy+103)), fill=(62, 68, 49))
    draw.ellipse((cx-84, cy-86, cx+87, min(bottom, cy+88)), fill=(53, 63, 47))
    for radius, start_ang, end_ang, tone, width in (
        (120, 196, 342, _LEAF, 3),
        (107, 22, 150, _LEAF_2, 2),
        (92, 206, 326, (86, 105, 72), 2),
        (74, 32, 142, (104, 125, 82), 2),
    ):
        draw.arc((cx-radius, cy-radius, cx+radius, cy+radius), start_ang, end_ang, fill=tone, width=width)
    for idx, (x, y, r) in enumerate(((55,72,22),(414,73,25),(53,226,24),(425,226,18),
                                      (102,45,14),(374,245,14),(145,157,7),(335,164,10))):
        wobble = int(math.sin(phase * 0.31 + idx) * 1.5)
        draw.ellipse((x-r+wobble, y-r, x+r+wobble, y+r),
                     outline=_LEAF_2 if idx % 3 == 0 else _LEAF, width=2)


def _draw_creature(draw, meta):
    """Large living focal subject; all instrumentation stays subordinate."""
    coat = (43, 46, 38)
    coat_mid = (51, 55, 43)
    shadow = (31, 34, 29)
    muzzle = (58, 61, 47)
    eye_socket = (24, 28, 24)

    # Torso is clipped above the shell rail so the creature never fights navigation.
    draw.ellipse((166, 177, 314, 261), fill=shadow)
    draw.ellipse((181, 188, 299, 258), fill=coat)
    draw.arc((154, 171, 326, 268), 197, 343, fill=_LEAF, width=2)

    head = [
        (157, 111), (164, 80), (178, 87), (191, 49), (214, 79), (240, 70),
        (266, 79), (289, 49), (302, 88), (316, 80), (323, 111),
        (327, 151), (316, 186), (291, 214), (262, 231), (240, 239),
        (218, 231), (189, 214), (164, 186), (153, 151),
    ]
    draw.polygon(head, fill=coat, outline=_WARM)
    draw.line(head + [head[0]], fill=_WARM, width=3, joint="curve")
    draw.polygon([(172,87),(191,55),(209,87),(194,107)], fill=shadow, outline=_LEAF)
    draw.polygon([(271,87),(289,55),(308,89),(289,107)], fill=shadow, outline=_LEAF)
    draw.polygon([(240,75),(216,87),(204,120),(219,142),(240,151),(261,142),(276,120),(264,87)],
                 fill=coat_mid, outline=(72,76,57))
    draw.polygon([(196,169),(216,151),(240,159),(264,151),(284,169),(270,204),(240,218),(210,204)],
                 fill=muzzle, outline=(74,78,58))

    mood = meta["mood"].lower()
    alert = mood in {"angry", "intense", "focused", "hunting"}
    eye_col = _WARM if alert else _INK
    brow_col = _WARM if alert else _LEAF_2
    draw.line((181,124,219,118), fill=brow_col, width=3)
    draw.line((261,118,299,124), fill=brow_col, width=3)
    draw.polygon([(187,133),(221,135),(214,154),(194,152)], fill=eye_socket, outline=eye_col)
    draw.polygon([(259,135),(293,133),(286,152),(266,154)], fill=eye_socket, outline=eye_col)
    draw.ellipse((199,138,211,151), fill=(105,137,86), outline=_LEAF_2)
    draw.ellipse((269,138,281,151), fill=(105,137,86), outline=_LEAF_2)
    draw.ellipse((203,140,208,151), fill=(18,22,18))
    draw.ellipse((273,140,278,151), fill=(18,22,18))
    draw.polygon([(231,165),(249,165),(240,175)], fill=_WARM)
    draw.line((240,175,240,182), fill=_MUTED, width=2)
    if mood in {"sad", "bored"}:
        draw.arc((216,183,264,207), 200, 340, fill=_LEAF_2, width=2)
    elif alert:
        draw.line((218,194,262,194), fill=_LEAF_2, width=2)
    else:
        draw.arc((216,177,264,203), 12, 168, fill=_LEAF_2, width=2)

    # Identity tag is truthful even before progression has loaded.
    draw.line((207,218,240,231,273,218), fill=_LEAF, width=2)
    draw.ellipse((229,224,251,246), fill=_SOIL, outline=_WARM, width=2)
    level = "—" if meta["level"] is None else str(meta["level"])
    box = draw.textbbox((0, 0), level, font=_font(9))
    draw.text((240 - (box[2] - box[0]) // 2, 229), level, fill=_INK, font=_font(9))
    label = meta["stage"].upper()
    box = draw.textbbox((0, 0), label, font=_font(9))
    draw.text((240 - (box[2] - box[0]) // 2, 249), label, fill=_INK, font=_font(9))


def _counter_or_dash(value: int | None) -> str:
    return "—" if value is None else str(value)


def render_habitat_home(state: dict[str, Any], *, phase: float = 0.0,
                        scene_runtime: SceneRuntime | None = None) -> Image.Image:
    state = dict(state or {})
    meta = habitat_home_metadata(state)
    shell = _shell(state, "home")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:habitat:home", theme_id="experience.habitat")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_habitat(d, phase)
    _register(rt, SceneLayerSpec(
        "habitat.environment", "environment", (0, 34, 480, 264),
        update_class="ambient", decorative=True,
    ))
    _draw_header(d, shell, rt, page_label="HOME")

    _draw_creature(d, meta)
    _register(rt, SceneLayerSpec(
        "habitat.beast", "creature", (130, 40, 350, 260),
        signals=("progression.stage", "progression.level", "pwnagotchi.mood", "beast.expression"),
        update_class="live",
    ))

    # Two habitat objects hold secondary truth without surrounding the companion in cards.
    d.ellipse((18, 55, 112, 149), fill=(50,49,40), outline=_LEAF, width=2)
    d.text((37, 72), "TODAY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    discoveries = _counter_or_dash(meta["discoveries"])
    d.text((39, 91), discoveries, fill=_INK if meta["discoveries"] is not None else _MUTED,
           font=_font(SHELL_TYPE.hero))
    d.text((27, 121), "DISCOVERIES", fill=_LEAF_2, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat.discovery", "instrument", (18,55,112,149),
        signals=("wifi.encounters.session_unique", "wifi.ap_count"), update_class="live",
    ))

    d.ellipse((368, 55, 462, 149), fill=(50,49,40), outline=_LEAF, width=2)
    d.text((389, 72), "MEMORY", fill=_MUTED, font=_font(SHELL_TYPE.caption))
    lifetime = _counter_or_dash(meta["lifetime"])
    d.text((391, 91), lifetime, fill=_INK if meta["lifetime"] is not None else _MUTED,
           font=_font(SHELL_TYPE.hero))
    d.text((383, 121), "ENCOUNTERS", fill=_LEAF_2, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat.memory", "instrument", (368,55,462,149),
        signals=("wifi.encounters.lifetime_unique",), update_class="live",
    ))

    # Growth remains organic. Unknown progression means an unfilled vine, not 0%.
    x1, y1, x2, y2 = 28, 177, 104, 251
    d.arc((x1,y1,x2,y2), 90, 270, fill=_LEAF, width=4)
    pct = meta["progress_pct"]
    if pct is not None:
        bounded = max(0.0, min(100.0, pct))
        end_y = int(y2 - (y2-y1)*(bounded/100.0))
        d.ellipse((43,end_y-6,55,end_y+6), fill=_WARM)
        growth_text = f"GROWTH {bounded:.0f}%"
    else:
        growth_text = "GROWTH —"
    d.text((24, 244), growth_text, fill=_MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat.growth", "instrument", (18,170,112,263),
        signals=("progression.level_progress_pct",), update_class="live",
    ))

    # Expedition cue appears only when the fact is actually true.
    if meta["expedition_active"] is True:
        d.ellipse((392, 188, 454, 250), outline=_WARM, width=2)
        d.text((407, 207), "OUT", fill=_WARM, font=_font(SHELL_TYPE.body))
        d.text((401, 229), "ROAMING", fill=_MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat.expedition", "ambient", (388,184,458,254),
        signals=("expedition.active",), update_class="live",
    ))

    # Small truth stone: context, never the primary hierarchy.
    d.rounded_rectangle((139, 231, 341, 261), radius=12, fill=(48,47,39), outline=_SOIL)
    mood = format_reading(meta["mood_reading"])
    caps = format_reading(meta["captures_reading"])
    expression = format_reading(meta["expression_reading"])
    d.text((151, 240), mood.upper()[:10], fill=_INK if meta["mood_reading"].known else _MUTED, font=_font(10))
    d.text((222, 240), f"CAP {caps}", fill=_INK if meta["captures_reading"].known else _MUTED, font=_font(10))
    d.text((286, 240), expression.replace("-", " ").upper()[:8], fill=_MUTED, font=_font(9))
    _register(rt, SceneLayerSpec(
        "habitat.truth", "text", (139,231,341,261),
        signals=("pwnagotchi.mood", "captures.total", "beast.expression"), update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im


def render_habitat_beast(state: dict[str, Any], *, phase: float = 0.0,
                         scene_runtime: SceneRuntime | None = None) -> Image.Image:
    """Habitat Beast page: growth and memory remain a living space, not a dashboard."""
    state = dict(state or {})
    meta = habitat_home_metadata(state)
    shell = _shell(state, "beast")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="beast", scene_id="experience:habitat:beast", theme_id="experience.habitat")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_habitat(d, phase)
    _register(rt, SceneLayerSpec(
        "habitat_beast.environment", "environment", (0,34,480,264),
        update_class="ambient", decorative=True,
    ))
    _draw_header(d, shell, rt, page_label="GROWTH + MEMORY")

    # A smaller side portrait preserves creature primacy while opening room for growth history.
    cx = 145
    coat = (46,48,39)
    coat_2 = (54,58,45)
    shadow = (37,40,34)
    d.ellipse((86,169,204,251), fill=shadow, outline=_SOIL, width=2)
    head = [
        (77,106),(83,80),(96,86),(105,52),(122,79),(145,70),(168,79),(185,52),
        (198,87),(210,81),(216,107),(218,143),(208,174),(186,202),(145,217),
        (104,202),(82,174),(75,143),
    ]
    d.polygon(head, fill=coat, outline=_WARM)
    d.line(head + [head[0]], fill=_WARM, width=3, joint="curve")
    d.polygon([(90,88),(105,59),(119,88),(106,103)], fill=coat_2, outline=_LEAF)
    d.polygon([(171,88),(185,59),(201,89),(185,103)], fill=coat_2, outline=_LEAF)
    alert = meta["mood"].lower() in {"angry","intense","focused","hunting"}
    eye_col = _WARM if alert else _INK
    d.polygon([(100,129),(128,132),(121,146),(106,145)], fill=(34,37,31), outline=eye_col)
    d.polygon([(162,132),(190,129),(184,145),(169,146)], fill=(34,37,31), outline=eye_col)
    d.polygon([(138,155),(152,155),(145,164)], fill=_WARM)
    if alert:
        d.line((123,184,167,184), fill=_LEAF_2, width=2)
    else:
        d.arc((121,169,169,194), 12, 168, fill=_LEAF_2, width=2)
    level = "—" if meta["level"] is None else str(meta["level"])
    label = f"{meta['stage'].upper()[:5]} / {level}"
    box = d.textbbox((0,0), label, font=_font(10))
    d.text((cx-(box[2]-box[0])//2, 225), label, fill=_MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat_beast.creature", "creature", (58,42,232,254),
        signals=("progression.stage", "progression.level", "pwnagotchi.mood", "beast.expression"),
        update_class="live",
    ))

    # Growth vine.
    pct = meta["progress_pct"]
    path_x = 274
    d.line((path_x,62,path_x,247), fill=_LEAF, width=5)
    for level_mark in (0,25,50,75,100):
        y = 247 - int((level_mark/100.0)*185)
        reached = pct is not None and pct >= level_mark
        r = 7 if reached else 4
        d.ellipse((path_x-r,y-r,path_x+r,y+r), fill=_WARM if reached else _SOIL, outline=_LEAF_2)
        d.text((291,y-6),f"{level_mark}%",fill=_MUTED,font=_font(9))
    if pct is not None:
        bounded = max(0.0,min(100.0,pct))
        marker_y = 247 - int((bounded/100.0)*185)
        d.ellipse((path_x-11,marker_y-11,path_x+11,marker_y+11),outline=_INK,width=2)
        growth_label = f"CURRENT {bounded:.0f}%"
    else:
        growth_label = "CURRENT —"
    d.text((247, 250), growth_label, fill=_INK if pct is not None else _MUTED, font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat_beast.growth", "instrument", (244,52,330,263),
        signals=("progression.level_progress_pct",), update_class="live",
    ))

    # Memory stones show only actual counters.
    memories = [
        ("ENCOUNTERS", meta["lifetime"]),
        ("CAPTURES", meta["captures"]),
        ("EXP AP", _int_or_none(state.get("expedition.ap_unique"))),
    ]
    y = 68
    for title, value in memories:
        d.ellipse((342,y,458,y+52), fill=(51,50,41), outline=_LEAF)
        d.text((362,y+8),title,fill=_MUTED,font=_font(9))
        text = _counter_or_dash(value)
        d.text((384,y+25),text,fill=_INK if value is not None else _MUTED,font=_font(SHELL_TYPE.label))
        y += 61
    _register(rt, SceneLayerSpec(
        "habitat_beast.memories", "instrument", (340,66,460,252),
        signals=("wifi.encounters.lifetime_unique", "captures.total", "expedition.ap_unique"),
        update_class="live",
    ))

    # Context is deliberately tiny relative to the creature/growth scene.
    roaming = "ROAMING" if meta["expedition_active"] is True else "HOME" if meta["expedition_active"] is False else "LOCATION —"
    d.text((345, 249), roaming, fill=_WARM if meta["expedition_active"] is True else _MUTED, font=_font(9))
    _register(rt, SceneLayerSpec(
        "habitat_beast.context", "text", (338,244,466,263),
        signals=("pwnagotchi.mood", "expedition.active", "health.core.state"), update_class="live",
    ))

    _draw_nav(d, shell, rt)
    return im
