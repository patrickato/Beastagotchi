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
    """Layered organic habitat with slow decorative motion and less flat geometry."""
    cx = 238 + int(math.sin(phase * 0.23) * 2)
    cy = 158 + int(math.cos(phase * 0.17) * 1)

    # Broad earth/canopy masses. The off-centre inner pools prevent the background
    # reading as a target made from three perfect circles.
    draw.ellipse((cx-134, cy-134, cx+134, cy+134), fill=(66, 58, 45))
    draw.ellipse((cx-111, cy-118, cx+105, cy+114), fill=(62, 68, 49))
    draw.ellipse((cx-88, cy-96, cx+91, cy+99), fill=(53, 63, 47))

    # Broken canopy rings and root arcs create depth without pretending to be data.
    for radius, start_ang, end_ang, tone, width in (
        (126, 196, 342, _LEAF, 3),
        (113, 22, 150, _LEAF_2, 2),
        (96, 206, 326, (86, 105, 72), 2),
        (78, 32, 142, (104, 125, 82), 2),
    ):
        draw.arc((cx-radius, cy-radius, cx+radius, cy+radius),
                 start_ang, end_ang, fill=tone, width=width)

    # Vines/roots on the outside keep the scene organic while leaving the Beast clear.
    draw.line((23, 231, 34, 208, 45, 195, 58, 188), fill=_LEAF, width=3)
    draw.line((421, 94, 433, 110, 441, 133, 446, 156), fill=(91, 118, 78), width=2)
    draw.arc((17, 177, 82, 269), 122, 286, fill=(111, 137, 88), width=2)
    draw.arc((397, 48, 463, 129), 206, 356, fill=(102, 128, 83), width=2)

    # Leaf/seed nodes are intentionally irregular rather than a symmetric ring.
    nodes = (
        (55,72,22),(414,73,25),(52,244,28),(425,239,20),
        (102,45,14),(374,270,16),(150,102,9),(329,119,8),
        (143,168,7),(335,177,11),(166,61,6),(313,70,7),
    )
    for idx,(x,y,r) in enumerate(nodes):
        wobble = int(math.sin(phase * 0.31 + idx) * 1.5)
        draw.ellipse((x-r+wobble, y-r, x+r+wobble, y+r),
                     outline=_LEAF_2 if idx % 3 == 0 else _LEAF,
                     width=2)

    # Tiny warm spores add depth and an inhabited feeling without becoming UI chrome.
    for idx,(x,y) in enumerate(((132,82),(347,91),(120,217),(357,222),(86,163),(394,165))):
        pulse = 1 if math.sin(phase * 0.5 + idx) > 0.35 else 0
        r = 2 + pulse
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(154,132,76))


def _draw_creature(draw, meta):
    """Sculpted companion portrait with layered planes, gaze and body depth."""
    coat = (43, 46, 38)
    coat_mid = (51, 55, 43)
    coat_high = (61, 66, 49)
    shadow = (31, 34, 29)
    muzzle = (58, 61, 47)
    eye_socket = (24, 28, 24)

    # Torso and shoulders. Multiple overlapping masses make the portrait occupy space
    # instead of reading as a head pasted on a circular badge.
    draw.ellipse((157, 188, 323, 296), fill=shadow)
    draw.ellipse((176, 196, 304, 289), fill=coat)
    draw.arc((145, 181, 335, 302), 197, 343, fill=_LEAF, width=2)
    draw.arc((165, 198, 315, 292), 205, 334, fill=(105, 124, 82), width=2)
    draw.polygon([(182,224),(208,205),(240,216),(272,205),(298,224),(282,274),(198,274)],
                 fill=(48,51,41))

    # Head silhouette: broad cheeks, tapered chin and ears integrated into the skull.
    head = [
        (157, 117), (164, 84), (178, 90), (191, 53), (214, 83),
        (240, 74),
        (266, 83), (289, 53), (302, 91), (316, 84), (323, 117),
        (327, 158), (316, 196), (291, 226), (262, 244), (240, 252),
        (218, 244), (189, 226), (164, 196), (153, 158),
    ]
    draw.polygon(head, fill=coat, outline=_WARM)
    draw.line(head + [head[0]], fill=_WARM, width=3, joint="curve")

    # Ear cavities use three depths rather than a single outlined triangle.
    draw.polygon([(172,91),(191,59),(209,91),(194,111)], fill=shadow, outline=_LEAF)
    draw.polygon([(180,88),(191,68),(201,91),(193,101)], fill=(73,72,52))
    draw.polygon([(271,91),(289,59),(308,93),(289,111)], fill=shadow, outline=_LEAF)
    draw.polygon([(279,89),(289,68),(299,92),(289,101)], fill=(73,72,52))

    # Forehead bridge and temple planes give the face a dimensional centre.
    draw.polygon([(240,79),(216,91),(204,126),(219,148),(240,157),
                  (261,148),(276,126),(264,91)],
                 fill=coat_mid, outline=(72,76,57))
    draw.line((240,84,240,153), fill=(85,88,64), width=1)
    draw.polygon([(165,145),(193,135),(212,171),(195,211),(169,194)],
                 fill=coat_mid, outline=_SOIL)
    draw.polygon([(315,145),(287,135),(268,171),(285,211),(311,194)],
                 fill=coat_mid, outline=_SOIL)
    draw.polygon([(196,178),(216,158),(240,166),(264,158),(284,178),
                  (270,216),(240,231),(210,216)],
                 fill=muzzle, outline=(74,78,58))

    # Brow and recessed eye sockets. Pupils have direction/highlight so the Beast
    # reads as a living focal subject instead of a symbol.
    mood = meta["mood"].lower()
    alert = mood in {"angry","intense","focused","hunting"}
    eye_col = _WARM if alert else _INK
    brow_col = _WARM if alert else _LEAF_2
    draw.line((181,130,219,124), fill=brow_col, width=3)
    draw.line((261,124,299,130), fill=brow_col, width=3)
    left_eye = [(187,139),(221,141),(214,160),(194,158)]
    right_eye = [(259,141),(293,139),(286,158),(266,160)]
    draw.polygon(left_eye, fill=eye_socket, outline=eye_col)
    draw.polygon(right_eye, fill=eye_socket, outline=eye_col)
    draw.ellipse((199,144,211,157), fill=(105,137,86), outline=_LEAF_2)
    draw.ellipse((269,144,281,157), fill=(105,137,86), outline=_LEAF_2)
    draw.ellipse((203,146,208,157), fill=(18,22,18))
    draw.ellipse((273,146,278,157), fill=(18,22,18))
    draw.ellipse((204,146,206,148), fill=_INK)
    draw.ellipse((274,146,276,148), fill=_INK)

    # Nose, muzzle split, mouth and short whisker marks.
    draw.polygon([(231,174),(249,174),(240,184)], fill=_WARM)
    draw.line((240,184,240,191), fill=_MUTED, width=2)
    draw.arc((209,177,240,207), 8, 102, fill=_LEAF_2, width=2)
    draw.arc((240,177,271,207), 78, 172, fill=_LEAF_2, width=2)
    if mood in {"sad","bored"}:
        draw.arc((216,192,264,216), 200, 340, fill=_LEAF_2, width=2)
    elif alert:
        draw.line((218,202,262,202), fill=_LEAF_2, width=2)
    draw.line((203,184,181,180), fill=(112,111,84))
    draw.line((204,191,178,193), fill=(112,111,84))
    draw.line((277,184,299,180), fill=(112,111,84))
    draw.line((276,191,302,193), fill=(112,111,84))

    # Chin and cheek edge highlights keep the lower face from collapsing into a flat fill.
    draw.line((191,212,216,233,240,241,264,233,289,212),
              fill=(91,108,73), width=2)
    draw.line((176,173,184,205,204,226), fill=(72,82,61), width=2)
    draw.line((304,173,296,205,276,226), fill=(72,82,61), width=2)

    # Collar/tag: identity detail belongs beneath the portrait, not across the face.
    draw.line((205,229,240,243,275,229), fill=_LEAF, width=2)
    draw.ellipse((228,235,252,259), fill=_SOIL, outline=_WARM, width=2)
    level = str(meta["level"])
    bbox = draw.textbbox((0,0), level, font=_font(9))
    draw.text((240-(bbox[2]-bbox[0])//2,241), level, fill=_INK, font=_font(9))
    label = meta["stage"].upper()
    tw = draw.textbbox((0,0), label, font=_font(9))[2]
    draw.text((240-tw//2, 263), label, fill=_INK, font=_font(9))


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

    # Creature remains primary but uses the same layered organic language as Home.
    cx = 152
    coat=(46,48,39);coat_2=(54,58,45);shadow=(37,40,34)
    d.ellipse((92,174,216,258),fill=shadow,outline=_SOIL,width=2)
    head=[
        (82,109),(88,83),(100,88),(109,55),(126,82),
        (152,73),(178,82),(195,55),(204,90),(216,84),(222,110),
        (224,149),(214,181),(191,211),(152,226),(113,211),(90,181),(80,149),
    ]
    d.polygon(head,fill=coat,outline=_WARM)
    d.line(head+[head[0]],fill=_WARM,width=3,joint="curve")
    d.polygon([(94,91),(109,62),(123,91),(110,106)],fill=coat_2,outline=_LEAF)
    d.polygon([(181,91),(195,62),(210,92),(195,106)],fill=coat_2,outline=_LEAF)
    d.polygon([(88,146),(111,135),(124,169),(108,199),(88,181)],fill=coat_2,outline=_SOIL)
    d.polygon([(216,146),(193,135),(180,169),(196,199),(216,181)],fill=coat_2,outline=_SOIL)
    alert=meta["mood"].lower() in {"angry","intense","focused","hunting"}
    eye_col=_WARM if alert else _INK
    d.polygon([(104,132),(132,135),(125,148),(110,147)],fill=(34,37,31),outline=eye_col)
    d.polygon([(172,135),(200,132),(194,147),(179,148)],fill=(34,37,31),outline=eye_col)
    d.ellipse((116,137,121,142),fill=_LEAF_2)
    d.ellipse((183,137,188,142),fill=_LEAF_2)
    d.polygon([(145,158),(159,158),(152,166)],fill=_WARM)
    mood=meta["mood"].lower()
    if mood in {"awake","happy","excited"}:
        d.arc((126,166,153,191),5,100,fill=_LEAF_2,width=2)
        d.arc((151,166,178,191),80,175,fill=_LEAF_2,width=2)
    elif mood in {"sad","bored"}:
        d.arc((128,176,176,199),200,340,fill=_LEAF_2,width=2)
    else:
        d.line((130,187,174,187),fill=_LEAF_2,width=2)
    d.line((126,202,152,214,178,202),fill=_LEAF,width=2)
    d.ellipse((143,207,161,225),fill=_SOIL,outline=_WARM)
    label=f"{meta['stage'].upper()[:3]} {meta['level']:02d}"
    tw=d.textbbox((0,0),label,font=_font(7))[2]
    d.text((cx-tw//2,230),label,fill=_MUTED,font=_font(7))
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
