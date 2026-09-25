from __future__ import annotations

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
    # Quiet geometric creature: large focal object, no panel behind it.
    cx,cy=240,142
    draw.ellipse((150,54,330,230),outline=_ACCENT,width=2)
    draw.polygon([(169,84),(194,43),(210,87)],fill=_BG,outline=_ACCENT)
    draw.polygon([(270,87),(288,43),(313,84)],fill=_BG,outline=_ACCENT)
    draw.ellipse((205,129,214,138),fill=_INK)
    draw.ellipse((266,129,275,138),fill=_INK)
    draw.arc((214,142,266,180),20,160,fill=_INK,width=2)
    draw.text((201,194),meta["stage"].upper(),fill=_MUTED,font=_font(9))
    draw.text((226,209),f"{meta['level']:02d}",fill=_INK,font=_font(13))


def render_monolith_home(state:dict[str,Any],*,scene_runtime:SceneRuntime|None=None)->Image.Image:
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
        action_id="inspect.current", update_class="interaction",
    ))
    return im
