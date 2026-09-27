from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .beast_shell import (
    BeastShellModel,
    SHELL_TYPE,
    build_shell_model,
    format_reading,
    reading,
)
from .scene_runtime import SceneLayerSpec, SceneRuntime


SIZE=(480,320)
_BG=(18,18,18)
_INK=(239,236,226)
_MUTED=(132,132,128)
_LINE=(62,62,60)
_ACCENT=(194,184,153)
_OK=(145,178,146)
_WARN=(205,151,91)
_CRITICAL=(207,103,84)


def _font(size=11):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _shell(state:dict[str,Any], page_id:str)->BeastShellModel:
    shell=state.get("_beast_shell")
    if isinstance(shell,BeastShellModel) and shell.page_id==page_id:
        return shell
    return build_shell_model("monolith",page_id,state,("home","overview"))


def _attention_color(shell:BeastShellModel):
    if shell.attention.level=="critical":return _CRITICAL
    if shell.attention.level=="warning":return _WARN
    if shell.attention.level=="normal":return _OK
    return _ACCENT


def monolith_home_metadata(state:dict[str,Any])->dict[str,Any]:
    level_row=reading(state,"progression.level")
    nearby_row=reading(state,"wifi.ap_count")
    channel_row=reading(state,"radio.primary.channel")
    level=int(float(level_row.value)) if level_row.known else None
    nearby=int(float(nearby_row.value)) if nearby_row.known else None
    channel=int(float(channel_row.value)) if channel_row.known else None
    return {
        "stage":str(state.get("progression.stage") or "Beast"),
        "level":level,
        "mood":str(state.get("pwnagotchi.mood") or "unknown"),
        # Preserve the established metadata contract for callers/tests while
        # exposing truth-safe Reading objects to the renderer.
        "nearby":nearby,
        "channel":channel,
        "nearby_reading":nearby_row,
        "channel_reading":channel_row,
        "health":str(state.get("health.core.state") or "unknown"),
        "field":str(state.get("dock.state") or "unknown"),
    }


def _register(rt,spec):
    if rt is not None:rt.register(spec)


def _draw_shell_nav(draw, shell:BeastShellModel, rt=None):
    nav=shell.navigation
    y=nav.footer_y
    draw.line((0,y,480,y),fill=_LINE,width=1)
    draw.rectangle((0,y+1,479,319),fill=(15,15,15))
    draw.line((160,y+8,160,312),fill=_LINE)
    draw.line((320,y+8,320,312),fill=_LINE)

    if nav.previous_enabled:
        prev=f"‹ {nav.previous_page.upper()}"
        draw.text((18,y+18),prev,fill=_MUTED,font=_font(SHELL_TYPE.caption))
        _register(rt,SceneLayerSpec(
            f"monolith.{nav.page_id}.nav_previous","interaction",nav.previous_box,
            touch=f"experience_page:{nav.previous_page}",update_class="interaction",
        ))

    center=nav.position_text
    cb=draw.textbbox((0,0),center,font=_font(SHELL_TYPE.body));cw=cb[2]-cb[0]
    draw.text((240-cw//2,y+18),center,fill=_ACCENT,font=_font(SHELL_TYPE.body))
    _register(rt,SceneLayerSpec(
        f"monolith.{nav.page_id}.nav_position","text",nav.center_box,
        update_class="static",
    ))

    if nav.next_enabled:
        nxt=f"{nav.next_page.upper()} ›"
        nb=draw.textbbox((0,0),nxt,font=_font(SHELL_TYPE.caption));nw=nb[2]-nb[0]
        draw.text((462-nw,y+18),nxt,fill=_MUTED,font=_font(SHELL_TYPE.caption))
        _register(rt,SceneLayerSpec(
            f"monolith.{nav.page_id}.nav_next","interaction",nav.next_box,
            touch=f"experience_page:{nav.next_page}",update_class="interaction",
        ))


def _draw_shell_status(draw, shell:BeastShellModel, rt=None):
    col=_attention_color(shell)
    draw.ellipse((18,17,27,26),fill=col)
    draw.text((38,14),shell.status_sentence,fill=_INK,font=_font(SHELL_TYPE.caption))
    _register(rt,SceneLayerSpec(
        f"monolith.{shell.page_id}.shell_status","text",(12,8,466,34),
        signals=("health.core.state","system.temp.cpu_c","pwnagotchi.service.state",
                 "bettercap.service.state","radio.monitor.state"),
        update_class="live",
    ))


def _draw_focal(draw,meta,shell:BeastShellModel):
    """Premium sculptural Beast bust: dimensional, restrained, never logo-like."""
    cx = 240
    shadow = (22, 22, 21)
    shadow_2 = (26, 26, 24)
    facet = (31, 31, 29)
    facet_2 = (38, 37, 34)
    facet_hi = (45, 43, 38)
    health_col = _attention_color(shell)

    draw.arc((146, 47, 334, 230), 212, 326, fill=_LINE, width=1)
    draw.arc((154, 55, 326, 222), 30, 148, fill=(43,43,41), width=1)
    draw.arc((167, 68, 313, 212), 188, 246, fill=(34,34,33), width=1)
    draw.arc((167, 68, 313, 212), 294, 352, fill=(34,34,33), width=1)

    draw.polygon([(215,198),(265,198),(281,224),(267,236),(213,236),(199,224)],
                 fill=shadow, outline=(54,53,49))
    draw.polygon([(220,199),(260,199),(269,219),(258,227),(222,227),(211,219)],
                 fill=shadow_2, outline=_LINE)

    head = [
        (168, 107), (174, 78), (188, 84), (201, 47), (219, 79),
        (239, 70), (262, 77), (279, 48), (292, 84), (305, 76),
        (311, 106), (314, 144), (305, 174), (286, 201),
        (259, 219), (239, 225), (217, 218), (194, 203),
        (176, 177), (166, 147),
    ]
    draw.polygon(head, fill=shadow, outline=_ACCENT)
    draw.line(head + [head[0]], fill=_ACCENT, width=2, joint="curve")

    draw.polygon([(178,82),(201,52),(214,84),(198,101)], fill=(27,27,25), outline=_LINE)
    draw.polygon([(266,84),(279,53),(301,84),(283,101)], fill=(27,27,25), outline=_LINE)
    draw.line((185,80,199,62,207,84), fill=(72,69,59))
    draw.line((273,84,280,63,294,82), fill=(72,69,59))

    draw.polygon([(206,88),(239,73),(274,87),(260,122),(241,138),(222,122)],
                 fill=facet_hi, outline=(55,54,50))
    draw.polygon([(176,108),(206,88),(222,122),(208,164),(182,180),(169,146)],
                 fill=facet, outline=_LINE)
    draw.polygon([(305,106),(274,87),(260,122),(274,163),(299,177),(313,144)],
                 fill=facet, outline=_LINE)
    draw.polygon([(208,164),(241,138),(274,163),(262,198),(240,212),(218,198)],
                 fill=facet_2, outline=(56,55,51))
    draw.polygon([(181,180),(208,164),(218,198),(204,210),(188,198)],
                 fill=(28,28,26), outline=(48,48,45))
    draw.polygon([(299,177),(274,163),(262,198),(277,209),(291,197)],
                 fill=(28,28,26), outline=(48,48,45))

    draw.line((190,126,219,122), fill=_INK, width=2)
    draw.line((261,122,289,127), fill=_INK, width=2)
    draw.polygon([(194,128),(219,125),(213,136),(198,136)], fill=(17,17,17))
    draw.polygon([(261,125),(286,128),(281,136),(266,136)], fill=(17,17,17))
    draw.ellipse((205,128,210,133), fill=health_col)
    draw.ellipse((270,128,275,133), fill=health_col)
    draw.point((207,128), fill=_INK)
    draw.point((272,128), fill=_INK)

    draw.polygon([(230,152),(250,152),(246,162),(240,167),(234,162)], fill=_ACCENT)
    draw.line((240,167,240,176), fill=(88,85,74), width=1)
    draw.arc((217,162,241,188), 20, 108, fill=(172,168,149), width=1)
    draw.arc((239,162,264,188), 72, 160, fill=(172,168,149), width=1)

    mood = meta["mood"].lower()
    fault=shell.attention.level in {"critical","warning"}
    if fault:
        draw.line((223,186,257,186), fill=health_col, width=2)
    elif mood in {"awake","happy","excited"}:
        draw.arc((220,170,260,191), 18, 162, fill=_INK, width=2)
    elif mood in {"sad","bored"}:
        draw.arc((220,177,260,197), 200, 340, fill=_INK, width=2)
    else:
        draw.line((223,186,257,186), fill=_INK, width=2)

    draw.line((202,101,214,90,229,82), fill=(85,81,69), width=1)
    draw.line((277,94,289,107,299,136), fill=(74,71,61), width=1)
    draw.line((197,199,217,214,239,220), fill=(66,64,57), width=1)

    level_text="—" if meta["level"] is None else f"{meta['level']:02d}"
    identity = f"{meta['stage'].upper()[:3]} / {level_text}"
    iw = draw.textbbox((0,0), identity, font=_font(SHELL_TYPE.caption))[2]
    draw.line((cx-36, 219, cx+36, 219), fill=(59,58,53), width=1)
    draw.text((cx-iw//2, 226), identity, fill=_MUTED, font=_font(SHELL_TYPE.caption))


def render_monolith_home(state:dict[str,Any],*,phase:float=0.0,scene_runtime:SceneRuntime|None=None)->Image.Image:
    state=dict(state or {})
    meta=monolith_home_metadata(state)
    shell=_shell(state,"home")
    rt=scene_runtime
    if rt is not None:
        rt.begin(page_id="home",scene_id="experience:monolith:home",theme_id="experience.monolith")
        rt.update_signals(state)

    im=Image.new("RGB",SIZE,_BG)
    d=ImageDraw.Draw(im)

    _draw_shell_status(d,shell,rt)

    _draw_focal(d,meta,shell)
    _register(rt,SceneLayerSpec(
        "monolith.focal","creature",(146,36,334,238),
        signals=("progression.stage","progression.level","pwnagotchi.mood","beast.expression",
                 "health.core.state","pwnagotchi.service.state","bettercap.service.state"),
        update_class="live",
    ))

    pulse=0.5+0.5*math.sin(float(phase)*1.25)
    halo=(
        int(_LINE[0]+(_ACCENT[0]-_LINE[0])*pulse),
        int(_LINE[1]+(_ACCENT[1]-_LINE[1])*pulse),
        int(_LINE[2]+(_ACCENT[2]-_LINE[2])*pulse),
    )
    d.arc((142,40,338,236),205,335,fill=halo,width=1)
    d.arc((156,54,324,222),25,155,fill=halo,width=1)
    _register(rt,SceneLayerSpec(
        "monolith.ambient_halo","ambient",(138,36,342,240),
        update_class="ambient",reduced_motion="static",decorative=True,
    ))

    nearby_text=format_reading(meta["nearby_reading"])
    channel_text=format_reading(meta["channel_reading"])
    d.text((118,240),f"{nearby_text} NEARBY",fill=_INK,font=_font(SHELL_TYPE.label))
    d.line((248,240,248,258),fill=_LINE)
    d.text((266,240),f"CH {channel_text}",fill=_INK,font=_font(SHELL_TYPE.label))
    _register(rt,SceneLayerSpec(
        "monolith.primary_fact","instrument",(108,234,370,263),
        signals=("wifi.ap_count","radio.primary.channel"),update_class="live",
    ))

    _draw_shell_nav(d,shell,rt)
    return im



def render_monolith_overview(
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
) -> Image.Image:
    """Monolith translation of Overview: sparse body over the shared Beast shell."""
    state = dict(state or {})
    meta = monolith_home_metadata(state)
    shell=_shell(state,"overview")
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="overview", scene_id="experience:monolith:overview",
                 theme_id="experience.monolith")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, _BG)
    d = ImageDraw.Draw(im)

    _draw_shell_status(d,shell,rt)

    primary=shell.attention.summary
    pb=d.textbbox((0,0),primary,font=_font(SHELL_TYPE.hero));pw=pb[2]-pb[0]
    d.text((240-pw//2,70),primary,fill=_INK,font=_font(SHELL_TYPE.hero))
    d.line((120,110,360,110),fill=_LINE)
    _register(rt, SceneLayerSpec(
        "monolith_overview.primary", "text", (112,62,368,118),
        signals=("health.core.state","system.temp.cpu_c","pwnagotchi.service.state",
                 "bettercap.service.state","radio.monitor.state"), update_class="live",
    ))
    _register(rt, SceneLayerSpec(
        "monolith_overview.inspect_hint", "interaction", (112,62,368,124),
        touch="hold_for_detail", update_class="interaction",
    ))

    cpu=reading(state,"system.cpu.total",unit="%")
    temp=reading(state,"system.temp.cpu_c",unit="°")
    nearby=meta["nearby_reading"]
    facts=(
        (146,"COMPUTE",format_reading(cpu)),
        (240,"THERMAL",format_reading(temp)),
        (334,"NEARBY",format_reading(nearby)),
    )
    for idx,(cx,label,value) in enumerate(facts):
        vb=d.textbbox((0,0),value,font=_font(SHELL_TYPE.hero));vw=vb[2]-vb[0]
        d.text((cx-vw//2,138),value,fill=_INK,font=_font(SHELL_TYPE.hero))
        lb=d.textbbox((0,0),label,font=_font(SHELL_TYPE.caption));lw=lb[2]-lb[0]
        d.text((cx-lw//2,173),label,fill=_MUTED,font=_font(SHELL_TYPE.caption))
        if idx<2:d.line((cx+47,136,cx+47,194),fill=_LINE)
    _register(rt, SceneLayerSpec(
        "monolith_overview.facts", "instrument", (88,130,392,198),
        signals=("system.cpu.total", "system.temp.cpu_c", "wifi.ap_count"),
        update_class="live",
    ))

    expedition = "EXPEDITION" if bool(state.get("expedition.active")) else meta["field"].upper()
    governor = str(state.get("governor.mode") or "UNKNOWN").upper()
    context=f"{expedition} · {governor}"
    cb=d.textbbox((0,0),context,font=_font(SHELL_TYPE.body));cw=cb[2]-cb[0]
    d.text((240-cw//2,220),context,fill=_ACCENT,font=_font(SHELL_TYPE.body))
    _register(rt, SceneLayerSpec(
        "monolith_overview.context", "text", (120,212,360,244),
        signals=("expedition.active", "dock.state", "governor.mode"),
        update_class="live",
    ))

    _draw_shell_nav(d,shell,rt)
    return im
