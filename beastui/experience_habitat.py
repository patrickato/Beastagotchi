from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

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


def habitat_home_metadata(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": str(state.get("progression.stage") or "Beast"),
        "level": _i(state, "progression.level"),
        "progress_pct": _f(state, "progression.level_progress_pct"),
        "mood": str(state.get("pwnagotchi.mood") or "awake"),
        "expression": str(state.get("beast.expression") or ""),
        "discoveries": _i(state, "wifi.encounters.session_unique", _i(state, "wifi.ap_count")),
        "lifetime": _i(state, "wifi.encounters.lifetime_unique"),
        "captures": _i(state, "captures.total"),
        "health": str(state.get("health.core.state") or "unknown"),
        "expedition_active": bool(state.get("expedition.active")),
    }


def _register(rt, spec):
    if rt is not None:
        rt.register(spec)


def _draw_habitat(draw, phase):
    # Organic backdrop. Decorative and intentionally not telemetry.
    for radius, tone in ((130, _SOIL), (105, (67, 72, 51)), (82, (58, 68, 50))):
        cx = 238 + int(math.sin(phase * 0.2 + radius) * 2)
        cy = 157
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=tone)
    for x, y, r in ((55,72,22),(414,73,25),(52,244,28),(425,239,20),(102,45,14),(374,270,16)):
        draw.ellipse((x-r, y-r, x+r, y+r), outline=_LEAF, width=2)


def _draw_creature(draw, meta):
    """Organic companion portrait with layered facial structure, not a circle mascot."""
    cx = 240
    coat = (46, 48, 39)
    coat_2 = (54, 58, 45)
    shadow = (37, 40, 34)

    # Body/shoulders sit behind the head so the Beast feels present in a habitat,
    # not pasted as a floating icon.
    draw.ellipse((166, 190, 314, 292), fill=shadow, outline=_SOIL, width=2)
    draw.arc((150, 184, 330, 300), 198, 342, fill=_LEAF, width=2)

    # Asymmetric leafy halo is decorative habitat language.
    for x, y, r in ((151,105,10),(326,118,8),(142,168,7),(334,176,11),(167,61,6),(312,70,7)):
        draw.ellipse((x-r,y-r,x+r,y+r), outline=_LEAF, width=2)

    # Head silhouette: broad cheek structure, tapered chin, tall ears.
    head = [
        (158, 115), (166, 82), (182, 88), (191, 54), (213, 84),
        (240, 75),
        (267, 84), (289, 54), (298, 90), (314, 83), (322, 116),
        (326, 161), (312, 205), (284, 235), (240, 252),
        (196, 235), (168, 205), (154, 161),
    ]
    draw.polygon(head, fill=coat, outline=_WARM)
    draw.line(head + [head[0]], fill=_WARM, width=3, joint="curve")

    # Inner ears and cheek planes.
    draw.polygon([(174,91),(191,61),(207,91),(192,108)], fill=coat_2, outline=_LEAF)
    draw.polygon([(273,91),(289,61),(306,93),(289,108)], fill=coat_2, outline=_LEAF)
    draw.polygon([(166,151),(193,138),(208,177),(190,211),(167,190)], fill=coat_2, outline=_SOIL)
    draw.polygon([(314,151),(287,138),(272,177),(290,211),(313,190)], fill=coat_2, outline=_SOIL)

    # Brow/eye shapes convey mood more expressively than dot eyes.
    eye_y = 141
    alert = meta["mood"].lower() in {"angry","intense","focused","hunting"}
    left_eye = [(188,eye_y),(222,eye_y+3),(214,eye_y+17),(194,eye_y+16)]
    right_eye = [(258,eye_y+3),(292,eye_y),(286,eye_y+16),(266,eye_y+17)]
    eye_col = _WARM if alert else _INK
    draw.polygon(left_eye, fill=(34,37,31), outline=eye_col)
    draw.polygon(right_eye, fill=(34,37,31), outline=eye_col)
    draw.ellipse((202,147,208,153), fill=_LEAF_2)
    draw.ellipse((272,147,278,153), fill=_LEAF_2)
    draw.line((184,132,220,128), fill=_LEAF if not alert else _WARM, width=2)
    draw.line((260,128,296,132), fill=_LEAF if not alert else _WARM, width=2)

    # Muzzle/nose and mood-driven mouth.
    draw.polygon([(232,171),(248,171),(240,180)], fill=_WARM)
    draw.line((240,180,240,187), fill=_MUTED)
    mood = meta["mood"].lower()
    if mood in {"awake","happy","excited"}:
        draw.arc((207,176,241,205), 5, 100, fill=_LEAF_2, width=2)
        draw.arc((239,176,273,205), 80, 175, fill=_LEAF_2, width=2)
    elif mood in {"sad","bored"}:
        draw.arc((214,188,266,214), 200, 340, fill=_LEAF_2, width=2)
    else:
        draw.line((216,197,264,197), fill=_LEAF_2, width=2)

    # Identity is a small collar/tag beneath the face rather than text across it.
    draw.line((207,224,240,239,273,224), fill=_LEAF, width=2)
    draw.ellipse((229,232,251,254), fill=_SOIL, outline=_WARM)
    level = str(meta["level"])
    bbox = draw.textbbox((0,0), level, font=_font(9))
    draw.text((240-(bbox[2]-bbox[0])//2,237), level, fill=_INK, font=_font(9))
    label = meta["stage"].upper()
    tw = draw.textbbox((0,0), label, font=_font(9))[2]
    draw.text((240-tw//2, 258), label, fill=_INK, font=_font(9))


def render_habitat_home(state: dict[str, Any], *, phase: float = 0.0,
                        scene_runtime: SceneRuntime | None = None) -> Image.Image:
    state = dict(state or {})
    meta = habitat_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:habitat:home", theme_id="experience.habitat")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_habitat(d, phase)
    _register(rt, SceneLayerSpec(
        "habitat.environment", "environment", (0, 0, 480, 320),
        update_class="ambient", decorative=True,
    ))

    d.text((12, 10), "HABITAT", fill=_LEAF_2, font=_font(14))
    health = meta["health"].upper()
    d.text((405, 11), health, fill=_HEALTH if health=="HEALTHY" else _WARM, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.health", "text", (390, 5, 472, 28),
        signals=("health.core.state",), update_class="live",
    ))

    _draw_creature(d, meta)
    _register(rt, SceneLayerSpec(
        "habitat.beast", "creature", (130, 40, 350, 260),
        signals=("progression.stage","progression.level","pwnagotchi.mood","beast.expression"),
        update_class="live",
    ))

    # Context is distributed as habitat objects, not dashboard panels.
    d.ellipse((18, 48, 112, 142), fill=(50,49,40), outline=_LEAF)
    d.text((38, 69), "TODAY", fill=_MUTED, font=_font(8))
    d.text((39, 87), str(meta["discoveries"]), fill=_INK, font=_font(22))
    d.text((30, 116), "DISCOVERIES", fill=_LEAF_2, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.discovery", "instrument", (18,48,112,142),
        signals=("wifi.encounters.session_unique","wifi.ap_count"), update_class="live",
    ))

    d.ellipse((370, 55, 462, 147), fill=(50,49,40), outline=_LEAF)
    d.text((391, 74), "MEMORY", fill=_MUTED, font=_font(8))
    d.text((393, 91), str(meta["lifetime"]), fill=_INK, font=_font(20))
    d.text((387, 120), "ENCOUNTERS", fill=_LEAF_2, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.memory", "instrument", (370,55,462,147),
        signals=("wifi.encounters.lifetime_unique",), update_class="live",
    ))

    # Growth vine is backed by genuine level progress.
    x1,y1,x2,y2 = 28, 188, 104, 272
    d.arc((x1,y1,x2,y2), 90, 270, fill=_LEAF, width=4)
    pct=max(0.0,min(100.0,meta["progress_pct"]))
    end_y=int(y2 - (y2-y1)*(pct/100.0))
    d.ellipse((43,end_y-6,55,end_y+6), fill=_WARM)
    d.text((24, 278), f"GROWTH {pct:.0f}%", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat.growth", "instrument", (18,180,112,296),
        signals=("progression.level_progress_pct",), update_class="live",
    ))

    # Expedition is a small environmental cue, not a mode banner.
    if meta["expedition_active"]:
        d.ellipse((394, 202, 449, 257), outline=_WARM, width=2)
        d.text((407, 219), "OUT", fill=_WARM, font=_font(10))
        d.text((400, 235), "ROAMING", fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "habitat.expedition", "ambient", (388,196,456,264),
        signals=("expedition.active",), update_class="live",
    ))

    # Truth strip remains deliberately small.
    d.rounded_rectangle((142, 277, 338, 310), radius=12, fill=(48,47,39), outline=_SOIL)
    d.text((158, 287), meta["mood"].upper(), fill=_INK, font=_font(9))
    d.text((230, 287), f"CAP {meta['captures']}", fill=_INK, font=_font(9))
    d.text((288, 287), meta["expression"].replace("-"," ").upper()[:10], fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "habitat.truth", "text", (142,277,338,310),
        signals=("pwnagotchi.mood","captures.total","beast.expression"), update_class="live",
    ))
    return im



def render_habitat_beast(
    state: dict[str, Any],
    *,
    phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Habitat translation of the Beast page: growth/memory as a living space."""
    state = dict(state or {})
    meta = habitat_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="beast", scene_id="experience:habitat:beast", theme_id="experience.habitat")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)
    _draw_habitat(d, phase)
    _register(rt, SceneLayerSpec(
        "habitat_beast.environment", "environment", (0,0,480,320),
        update_class="ambient", decorative=True,
    ))

    d.text((12,10),"HABITAT",fill=_LEAF_2,font=_font(14))
    d.text((79,12),"GROWTH + MEMORY",fill=_MUTED,font=_font(8))

    # Creature remains primary but shifts left to make room for its history.
    cx, cy = 152, 150
    d.ellipse((65,62,239,238),fill=(46,48,39),outline=_WARM,width=3)
    d.polygon([(82,91),(104,47),(123,94)],fill=(46,48,39),outline=_WARM)
    d.polygon([(180,94),(200,47),(222,91)],fill=(46,48,39),outline=_WARM)
    d.ellipse((118,130,131,143),fill=_INK)
    d.ellipse((174,130,187,143),fill=_INK)
    d.arc((130,144,178,180),18,162,fill=_LEAF_2,width=3)
    d.text((111,194),meta["stage"].upper(),fill=_INK,font=_font(13))
    d.text((133,213),f"LV {meta['level']}",fill=_WARM,font=_font(10))
    _register(rt, SceneLayerSpec(
        "habitat_beast.creature","creature",(62,44,242,242),
        signals=("progression.stage","progression.level","pwnagotchi.mood","beast.expression"),
        update_class="live",
    ))

    # Growth path is a single organic vertical journey rather than a progress card.
    pct=max(0.0,min(100.0,meta["progress_pct"]))
    path_x=278
    d.line((path_x,62,path_x,250),fill=_LEAF,width=5)
    for idx,level in enumerate((0,25,50,75,100)):
        y=250-int((level/100.0)*188)
        r=7 if pct>=level else 4
        col=_WARM if pct>=level else _SOIL
        d.ellipse((path_x-r,y-r,path_x+r,y+r),fill=col,outline=_LEAF_2)
        d.text((294,y-5),f"{level}%",fill=_MUTED,font=_font(7))
    marker_y=250-int((pct/100.0)*188)
    d.ellipse((path_x-11,marker_y-11,path_x+11,marker_y+11),outline=_INK,width=2)
    d.text((254,264),f"CURRENT {pct:.0f}%",fill=_INK,font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat_beast.growth","instrument",(250,52,326,286),
        signals=("progression.level_progress_pct",),update_class="live",
    ))

    # Memory stones contain only real counters currently available.
    memories=[
        ("ENCOUNTERS",meta["lifetime"]),
        ("CAPTURES",meta["captures"]),
        ("EXP AP",_i(state,"expedition.ap_unique")),
    ]
    y=68
    for title,value in memories:
        d.ellipse((342,y,458,y+58),fill=(51,50,41),outline=_LEAF)
        d.text((365,y+10),title,fill=_MUTED,font=_font(7))
        d.text((385,y+27),str(value),fill=_INK,font=_font(15))
        y+=68
    _register(rt, SceneLayerSpec(
        "habitat_beast.memories","instrument",(340,66,460,262),
        signals=("wifi.encounters.lifetime_unique","captures.total","expedition.ap_unique"),
        update_class="live",
    ))

    d.rounded_rectangle((88,277,392,309),radius=12,fill=(48,47,39),outline=_SOIL)
    roaming="ROAMING" if meta["expedition_active"] else "HOME"
    d.text((106,287),meta["mood"].upper(),fill=_INK,font=_font(8))
    d.text((190,287),roaming,fill=_WARM,font=_font(8))
    d.text((280,287),meta["health"].upper(),fill=_HEALTH,font=_font(8))
    _register(rt, SceneLayerSpec(
        "habitat_beast.context","text",(88,277,392,309),
        signals=("pwnagotchi.mood","expedition.active","health.core.state"),update_class="live",
    ))
    return im
