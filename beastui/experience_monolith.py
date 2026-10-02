from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE=(480,320)
_BG=(18,18,18)
_INK=(239,236,226)
_MUTED=(132,132,128)
_LINE=(62,62,60)
_ACCENT=(194,184,153)
_OK=(145,178,146)


def _font(size=11):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _i(state:dict[str,Any],key:str,default=0)->int:
    try:return int(float(state.get(key,default) or default))
    except Exception:return int(default)


def monolith_home_metadata(state:dict[str,Any])->dict[str,Any]:
    return {
        "stage":str(state.get("progression.stage") or "Beast"),
        "level":_i(state,"progression.level"),
        "mood":str(state.get("pwnagotchi.mood") or "awake"),
        "nearby":_i(state,"wifi.ap_count"),
        "channel":_i(state,"radio.primary.channel"),
        "health":str(state.get("health.core.state") or "unknown"),
        "field":str(state.get("dock.state") or "field"),
    }


def _register(rt,spec):
    if rt is not None:rt.register(spec)


def _draw_focal(draw,meta):
    """Premium sculptural Beast bust: dimensional, restrained, never logo-like."""
    cx = 240
    shadow = (22, 22, 21)
    shadow_2 = (26, 26, 24)
    facet = (31, 31, 29)
    facet_2 = (38, 37, 34)
    facet_hi = (45, 43, 38)
    health_col = _OK if meta["health"].lower()=="healthy" else _ACCENT

    # Quiet halo establishes depth behind the sculpture. Broken arcs avoid a badge/ring read.
    draw.arc((146, 47, 334, 238), 212, 326, fill=_LINE, width=1)
    draw.arc((154, 55, 326, 230), 30, 148, fill=(43,43,41), width=1)
    draw.arc((167, 68, 313, 218), 188, 246, fill=(34,34,33), width=1)
    draw.arc((167, 68, 313, 218), 294, 352, fill=(34,34,33), width=1)

    # Neck / plinth anchors the Beast as a sculptural bust rather than a floating mask.
    draw.polygon([(215,204),(265,204),(281,230),(267,242),(213,242),(199,230)],
                 fill=shadow, outline=(54,53,49))
    draw.polygon([(220,205),(260,205),(269,225),(258,233),(222,233),(211,225)],
                 fill=shadow_2, outline=_LINE)

    # Slightly asymmetric head silhouette with ears integrated into the skull.
    head = [
        (168, 111), (174, 82), (188, 88), (201, 51), (219, 83),
        (239, 74), (262, 81), (279, 52), (292, 88), (305, 80),
        (311, 110), (314, 148), (305, 178), (286, 205),
        (259, 223), (239, 229), (217, 222), (194, 207),
        (176, 181), (166, 151),
    ]
    draw.polygon(head, fill=shadow, outline=_ACCENT)
    draw.line(head + [head[0]], fill=_ACCENT, width=2, joint="curve")

    # Ear recesses and temple shelves create actual volume.
    draw.polygon([(178,86),(201,56),(214,88),(198,105)], fill=(27,27,25), outline=_LINE)
    draw.polygon([(266,88),(279,57),(301,88),(283,105)], fill=(27,27,25), outline=_LINE)
    draw.line((185,84,199,66,207,88), fill=(72,69,59))
    draw.line((273,88,280,67,294,86), fill=(72,69,59))

    # Major facial planes. The center plane is narrow/high; cheeks fall away to darker values.
    draw.polygon([(206,92),(239,77),(274,91),(260,126),(241,142),(222,126)],
                 fill=facet_hi, outline=(55,54,50))
    draw.polygon([(176,112),(206,92),(222,126),(208,168),(182,184),(169,150)],
                 fill=facet, outline=_LINE)
    draw.polygon([(305,110),(274,91),(260,126),(274,167),(299,181),(313,148)],
                 fill=facet, outline=_LINE)
    draw.polygon([(208,168),(241,142),(274,167),(262,202),(240,216),(218,202)],
                 fill=facet_2, outline=(56,55,51))

    # Lower cheek planes add mass while leaving the central muzzle clean.
    draw.polygon([(181,184),(208,168),(218,202),(204,214),(188,202)],
                 fill=(28,28,26), outline=(48,48,45))
    draw.polygon([(299,181),(274,167),(262,202),(277,213),(291,201)],
                 fill=(28,28,26), outline=(48,48,45))

    # Brow shelves / recessed eyes. Eyes remain tiny; health is a subtle glint, not an LED face.
    draw.line((190,130,219,126), fill=_INK, width=2)
    draw.line((261,126,289,131), fill=_INK, width=2)
    draw.polygon([(194,132),(219,129),(213,140),(198,140)], fill=(17,17,17))
    draw.polygon([(261,129),(286,132),(281,140),(266,140)], fill=(17,17,17))
    draw.ellipse((205,132,210,137), fill=health_col)
    draw.ellipse((270,132,275,137), fill=health_col)
    draw.point((207,132), fill=_INK)
    draw.point((272,132), fill=_INK)

    # Nose/muzzle bridge breaks the old symmetric-mask silhouette.
    draw.polygon([(230,156),(250,156),(246,166),(240,171),(234,166)],
                 fill=_ACCENT)
    draw.line((240,171,240,180), fill=(88,85,74), width=1)
    draw.arc((217,166,241,192), 20, 108, fill=(172,168,149), width=1)
    draw.arc((239,166,264,192), 72, 160, fill=(172,168,149), width=1)

    mood = meta["mood"].lower()
    if mood in {"awake","happy","excited"}:
        draw.arc((220,174,260,195), 18, 162, fill=_INK, width=2)
    elif mood in {"sad","bored"}:
        draw.arc((220,181,260,201), 200, 340, fill=_INK, width=2)
    else:
        draw.line((223,190,257,190), fill=_INK, width=2)

    # Sparse highlight edges sell the sculptural planes without adding ornament.
    draw.line((202,105,214,94,229,86), fill=(85,81,69), width=1)
    draw.line((277,98,289,111,299,140), fill=(74,71,61), width=1)
    draw.line((197,203,217,218,239,224), fill=(66,64,57), width=1)

    # Engraved identity on the plinth: quiet and deliberately separate from the face.
    identity = f"{meta['stage'].upper()[:3]} / {meta['level']:02d}"
    iw = draw.textbbox((0,0), identity, font=_font(7))[2]
    draw.line((cx-30, 225, cx+30, 225), fill=(59,58,53), width=1)
    draw.text((cx-iw//2, 231), identity, fill=_MUTED, font=_font(7))


def render_monolith_home(state:dict[str,Any],*,phase:float=0.0,scene_runtime:SceneRuntime|None=None)->Image.Image:
    state=dict(state or {})
    meta=monolith_home_metadata(state)
    rt=scene_runtime
    if rt is not None:
        rt.begin(page_id="home",scene_id="experience:monolith:home",theme_id="experience.monolith")
        rt.update_signals(state)

    im=Image.new("RGB",SIZE,_BG)
    d=ImageDraw.Draw(im)

    d.text((18,16),"BEAST",fill=_MUTED,font=_font(8))
    health=meta["health"].upper()
    d.ellipse((449,17,456,24),fill=_OK if health=="HEALTHY" else _ACCENT)
    _register(rt,SceneLayerSpec(
        "monolith.status","text",(12,10,466,30),
        signals=("health.core.state",),update_class="live",
    ))

    _draw_focal(d,meta)
    _register(rt,SceneLayerSpec(
        "monolith.focal","creature",(146,40,334,232),
        signals=("progression.stage","progression.level","pwnagotchi.mood","beast.expression"),
        update_class="live",
    ))

    # Quiet decorative breath around the focal sculpture only.
    pulse=0.5+0.5*math.sin(float(phase)*1.25)
    halo=(
        int(_LINE[0]+(_ACCENT[0]-_LINE[0])*pulse),
        int(_LINE[1]+(_ACCENT[1]-_LINE[1])*pulse),
        int(_LINE[2]+(_ACCENT[2]-_LINE[2])*pulse),
    )
    d.arc((142,44,338,240),205,335,fill=halo,width=1)
    d.arc((156,58,324,226),25,155,fill=halo,width=1)
    _register(rt,SceneLayerSpec(
        "monolith.ambient_halo","ambient",(138,40,342,244),
        update_class="ambient",reduced_motion="static",decorative=True,
    ))

    # Exactly one primary fact row.
    d.text((164,250),f"{meta['nearby']} NEARBY",fill=_INK,font=_font(15))
    d.line((248,251,248,267),fill=_LINE)
    d.text((266,250),f"CH {meta['channel']}",fill=_INK,font=_font(15))
    _register(rt,SceneLayerSpec(
        "monolith.primary_fact","instrument",(150,244,332,272),
        signals=("wifi.ap_count","radio.primary.channel"),update_class="live",
    ))

    # Minimal contextual footer; large negative space remains intentional.
    d.line((170,291,310,291),fill=_LINE)
    d.text((182,299),meta["field"].upper(),fill=_MUTED,font=_font(8))
    d.text((236,299),meta["mood"].upper(),fill=_MUTED,font=_font(8))
    d.text((286,299),health,fill=_MUTED,font=_font(8))
    _register(rt,SceneLayerSpec(
        "monolith.context","text",(170,286,310,316),
        signals=("dock.state","pwnagotchi.mood","health.core.state"),update_class="live",
    ))
    return im



def render_monolith_overview(
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Monolith translation of Overview: deliberately sparse, high-value status only."""
    state = dict(state or {})
    meta = monolith_home_metadata(state)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="overview", scene_id="experience:monolith:overview",
                 theme_id="experience.monolith")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    # Tiny identity/header; negative space is part of the Experience contract.
    d.text((18, 16), "OVERVIEW", fill=_MUTED, font=_font(8))
    health = meta["health"].upper()
    d.ellipse((449,17,456,24), fill=_OK if health == "HEALTHY" else _ACCENT)
    _register(rt, SceneLayerSpec(
        "monolith_overview.status", "text", (12,10,466,30),
        signals=("health.core.state",), update_class="live",
    ))

    # One focal status statement rather than a module grid.
    primary = "SYSTEM READY" if health == "HEALTHY" else health
    d.text((145, 82), primary, fill=_INK, font=_font(24))
    d.line((145, 116, 335, 116), fill=_LINE)
    _register(rt, SceneLayerSpec(
        "monolith_overview.primary", "text", (138,72,342,122),
        signals=("health.core.state",), update_class="live",
    ))

    # Only three compact facts: compute, field context, nearby environment.
    cpu = _i(state, "system.cpu.total")
    temp = _i(state, "system.temp.cpu_c")
    nearby = meta["nearby"]
    d.text((154, 148), f"{cpu:02d}%", fill=_INK, font=_font(20))
    d.text((154, 174), "COMPUTE", fill=_MUTED, font=_font(8))
    d.line((224,146,224,190), fill=_LINE)

    d.text((246, 148), f"{temp:02d}°", fill=_INK, font=_font(20))
    d.text((246, 174), "THERMAL", fill=_MUTED, font=_font(8))
    d.line((314,146,314,190), fill=_LINE)

    d.text((336, 148), f"{nearby:02d}", fill=_INK, font=_font(20))
    d.text((336, 174), "NEARBY", fill=_MUTED, font=_font(8))
    _register(rt, SceneLayerSpec(
        "monolith_overview.facts", "instrument", (145,140,390,192),
        signals=("system.cpu.total", "system.temp.cpu_c", "wifi.ap_count"),
        update_class="live",
    ))

    # Context line stays quiet and readable.
    expedition = "EXPEDITION" if bool(state.get("expedition.active")) else meta["field"].upper()
    governor = str(state.get("governor.mode") or "unknown").upper()
    d.text((170, 232), expedition, fill=_ACCENT, font=_font(9))
    d.text((246, 232), "·", fill=_LINE, font=_font(9))
    d.text((260, 232), governor, fill=_MUTED, font=_font(9))
    _register(rt, SceneLayerSpec(
        "monolith_overview.context", "text", (166,224,330,248),
        signals=("expedition.active", "dock.state", "governor.mode"),
        update_class="live",
    ))

    # Universal depth hint: detail is intentionally drill-in rather than always visible.
    d.line((188, 283, 292, 283), fill=_LINE)
    d.text((200, 291), "HOLD FOR DETAIL", fill=_MUTED, font=_font(7))
    _register(rt, SceneLayerSpec(
        "monolith_overview.inspect_hint", "interaction", (184,276,296,312),
        touch="hold_for_detail", update_class="interaction",
    ))
    return im
