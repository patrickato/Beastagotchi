from __future__ import annotations

from contextlib import nullcontext
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from .scene_compositor import alpha_panel, ambient_glow, paste_scene_asset, scene_particles


def _scene_layer(ui, layer_id, kind, bounds, **kwargs):
    runtime=getattr(ui,'scene_runtime',None)
    if runtime is None:return nullcontext()
    return runtime.layer(layer_id,kind,bounds,**kwargs)

def _mix(a, b, t: float):
    t=max(0.0,min(1.0,float(t)))
    return tuple(int(a[i]*(1.0-t)+b[i]*t) for i in range(3))


def _v(state, key, default='--'):
    value=state.get(key, default)
    return default if value is None else value


def _text_right(d, x, y, text, font, fill):
    text=str(text)
    try:w=d.textbbox((0,0),text,font=font)[2]
    except Exception:w=int(d.textlength(text,font=font))
    d.text((x-w,y),text,font=font,fill=fill)


def _glow_line(d, points, color, *, width=1, glow=None):
    if glow:
        d.line(points,fill=glow,width=max(width+2,3),joint='curve')
    d.line(points,fill=color,width=width,joint='curve')


def _asset_portrait(d, box, ui, asset_name: str, phase: float, *, border_role='primary') -> bool:
    path=getattr(ui,'root',None)
    if path is None:return False
    path=Path(path)/'assets'/'home'/asset_name
    if not path.is_file():return False
    try:
        with Image.open(path) as src:
            src=src.convert('RGB')
            x1,y1,x2,y2=box;size=(max(1,x2-x1),max(1,y2-y1))
            img=ImageOps.fit(src,size,method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
            # A very small live luminance pulse keeps concept-derived art from
            # behaving like a dead wallpaper tile while remaining inexpensive.
            pulse=0.98 + 0.035*(0.5+0.5*math.sin(float(phase)*1.8))
            img=ImageEnhance.Brightness(img).enhance(pulse)
            canvas=getattr(d,'_image',None)
            if canvas is None:return False
            canvas.paste(img,(x1,y1))
        t=ui.theme
        col=t.c(border_role)
        d.rectangle((x1,y1,x2-1,y2-1),outline=col,width=1)
        scan_y=y1+int((float(phase)*23.0) % max(1,(y2-y1)))
        d.line((x1+2,scan_y,x2-3,scan_y),fill=_mix(t.c('bg'),col,.45),width=1)
        return True
    except Exception:
        return False


def _portrait(d, box, t, state, phase: float, *, variant='classic'):
    """Procedural mascot portrait intended to read as a creature, not a UI glyph.

    This remains asset-free so the base install stays lightweight. Future Visual
    Asset Interop can replace this layer with Pack-provided art without changing
    the surrounding scene contract.
    """
    x1,y1,x2,y2=box;w=x2-x1;h=y2-y1;cx=(x1+x2)//2
    primary=t.c('primary');secondary=t.c('secondary');accent=t.c('accent')
    dim=t.c('dim');edge=t.c('edge');panel=t.c('panel');bg=t.c('bg')
    mood=str(_v(state,'pwnagotchi.mood','awake')).lower()
    expr=str(_v(state,'beast.expression',mood)).lower()
    alert=expr in {'hunting','focused','alert','warning','overheated'} or mood in {'angry','intense'}

    if variant in {'cyber','ice'}:
        for i in range(5):
            yy=y1+12+i*max(9,h//7)
            ln=13+(i*11)%31
            col=secondary if (i%2) else edge
            d.line((x1+2,yy,x1+2+ln,yy),fill=col,width=1)
            d.line((x2-ln-2,yy+5,x2-2,yy+5),fill=col,width=1)
    elif variant=='tactical':
        d.arc((x1+2,y1+3,x2-2,y2+8),195,345,fill=edge,width=1)
        d.line((cx,y1+4,cx,y1+17),fill=accent,width=1)

    ear_y=y1+int(h*.05); brow_y=y1+int(h*.31); chin_y=y1+int(h*.91)
    left=[(cx-int(w*.42),brow_y),(cx-int(w*.36),ear_y),(cx-int(w*.19),y1+int(h*.19)),(cx-int(w*.12),y1+int(h*.15))]
    right=[(2*cx-x, y) for x,y in reversed(left)]
    head=[left[0],left[1],left[2],(cx,y1+int(h*.10)),right[1],right[0],(cx+int(w*.39),y1+int(h*.57)),(cx+int(w*.27),chin_y),(cx, y2-int(h*.01)),(cx-int(w*.27),chin_y),(cx-int(w*.39),y1+int(h*.57))]
    shadow=_mix(bg,primary,.09 if variant!='cyber' else .13)
    d.polygon(head,fill=shadow)
    if variant=='cyber':
        d.line(head+[head[0]],fill=_mix(primary,secondary,.38),width=4,joint='curve')
        d.line(head+[head[0]],fill=primary,width=1,joint='curve')
    elif variant=='ice':
        d.line(head+[head[0]],fill=_mix(primary,(255,255,255),.35),width=2,joint='curve')
    else:
        d.line(head+[head[0]],fill=primary,width=2,joint='curve')

    d.polygon([left[1],left[2],(cx-int(w*.31),y1+int(h*.28))],fill=_mix(panel,secondary,.24),outline=secondary)
    d.polygon([right[1],right[2],(cx+int(w*.31),y1+int(h*.28))],fill=_mix(panel,secondary,.24),outline=secondary)
    cheek_col=_mix(panel,primary,.18)
    d.polygon([(cx-int(w*.37),y1+int(h*.54)),(cx-int(w*.17),y1+int(h*.62)),(cx-int(w*.25),y1+int(h*.80)),(cx-int(w*.34),y1+int(h*.69))],fill=cheek_col,outline=edge)
    d.polygon([(cx+int(w*.37),y1+int(h*.54)),(cx+int(w*.17),y1+int(h*.62)),(cx+int(w*.25),y1+int(h*.80)),(cx+int(w*.34),y1+int(h*.69))],fill=cheek_col,outline=edge)

    eye_y=y1+int(h*.43); eye_w=max(20,int(w*.19)); eye_h=max(10,int(h*.10)); gap=int(w*.07)
    for side in (-1,1):
        ex=cx + side*(gap+eye_w//2)
        if side<0:
            poly=[(ex-eye_w//2,eye_y),(ex+eye_w//2,eye_y+4),(ex+eye_w//3,eye_y+eye_h),(ex-eye_w//3,eye_y+eye_h-1)]
        else:
            poly=[(ex-eye_w//2,eye_y+4),(ex+eye_w//2,eye_y),(ex+eye_w//3,eye_y+eye_h-1),(ex-eye_w//3,eye_y+eye_h)]
        eye_fill=accent if alert else primary
        d.polygon(poly,fill=_mix(bg,eye_fill,.18),outline=eye_fill)
        px=ex + (2 if side<0 else -2);py=eye_y+eye_h//2
        d.ellipse((px-3,py-3,px+3,py+3),fill=_mix(eye_fill,(255,255,255),.45))
        brow=[(ex-eye_w//2-3,eye_y-8+(-2 if side<0 else 2)),(ex+eye_w//2+3,eye_y-3+(2 if side<0 else -2))]
        _glow_line(d,brow,secondary,width=2,glow=_mix(bg,secondary,.12) if variant=='cyber' else None)

    nose_y=y1+int(h*.64)
    d.polygon([(cx-7,nose_y),(cx+7,nose_y),(cx,nose_y+6)],fill=secondary)
    mouth_y=y1+int(h*.72)
    if mood in {'sad','bored'}:
        d.arc((cx-24,mouth_y,cx+24,mouth_y+20),200,340,fill=primary,width=2)
    elif alert:
        d.line((cx-25,mouth_y,cx-9,mouth_y+5,cx,mouth_y+2,cx+9,mouth_y+5,cx+25,mouth_y),fill=accent,width=2)
    else:
        d.line((cx-24,mouth_y,cx-9,mouth_y+6,cx+9,mouth_y+6,cx+24,mouth_y),fill=primary,width=2)

    tick=int(phase*2.0)
    if variant=='cyber':
        for i in range(5):
            sx=x1+8+i*17;sy=y2-18-(i%2)*7
            d.line((sx,sy,sx+8,sy,sx+12,sy-5),fill=secondary if (i+tick)%3 else accent,width=1)
        d.arc((x1+8,y1+8,x2-8,y2-5),205+(tick%18),334+(tick%18),fill=_mix(primary,secondary,.5),width=1)
    elif variant=='ice':
        for i in range(6):
            sx=x1+9+i*max(12,w//7);sy=y1+12+((i*19)%max(24,h-30))
            d.line((sx,sy,sx+7,sy+9,sx+2,sy+18),fill=edge,width=1)
    elif variant=='tactical':
        r=max(22,int(min(w,h)*.42));cy=y1+int(h*.54)
        d.arc((cx-r,cy-r,cx+r,cy+r),15+(tick%22),145+(tick%22),fill=edge,width=1)


def _instrument_rail(d, box, t, f, state, *, cyber=False):
    x1,y1,x2,y2=box
    gps='LOCK' if state.get('gps.fix') else '--'
    temp=_v(state,'system.temp.cpu_c','--'); temp=f'{temp:.0f}C' if isinstance(temp,(int,float)) else '--'
    cpu=_v(state,'system.cpu.total','--'); cpu=f'{cpu:.0f}%' if isinstance(cpu,(int,float)) else '--'
    batt=state.get('power.battery.percent_estimate'); batt=f'{batt:.0f}%' if isinstance(batt,(int,float)) else ('DOCK' if state.get('dock.docked') else '--')
    items=[('GPS',gps,t.c('accent') if state.get('gps.fix') else t.c('dim')),('CPU',cpu,t.c('info')),('TEMP',temp,t.c('warn')),('POWER',batt,t.c('secondary'))]
    h=max(1,(y2-y1)//len(items))
    for i,(lab,val,col) in enumerate(items):
        ya=y1+i*h;yb=y1+(i+1)*h-3
        if cyber:
            d.polygon([(x1+5,ya),(x2,ya),(x2,yb),(x1,yb),(x1,ya+7)],fill=_mix(t.c('panel'),col,.09),outline=_mix(t.c('edge'),col,.35))
        else:
            d.rounded_rectangle((x1,ya,x2,yb),radius=5,fill=t.c('panel'),outline=t.c('edge'))
        d.text((x1+8,ya+7),lab,font=f['micro'],fill=t.c('dim'))
        _text_right(d,x2-8,ya+15,val,f['small'],col)


def _hero_scene(d,state,ui, *, variant='classic'):
    """Layered Home scene: creature + atmosphere + live instruments.

    This intentionally avoids the previous three-box dashboard composition.
    Concept-derived art is allowed to own visual space; truthful live state is
    overlaid as a compact HUD rather than forcing the artwork into a tile.
    """
    t=ui.theme;f=ui.fonts
    canvas=getattr(d,'_image',None)
    if canvas is None:return False
    is_cyber=variant=='cyber';is_ice=variant=='ice';is_synth=variant=='synth';is_tactical=variant=='tactical'

    # Scene lighting is dynamic but decorative. It never encodes telemetry.
    glow_col=t.c('secondary') if (is_cyber or is_synth) else t.c('primary')
    with _scene_layer(ui,'home.environment','environment',(0,34,480,278),z=10,
                      update_class='ambient',resource_class='moderate',
                      reduced_motion='static_glow',decorative=True):
        ambient_glow(canvas,(156,148),150,glow_col,strength=.34 if is_cyber else .24)
        ambient_glow(canvas,(395,92),94,t.c('accent'),strength=.17)
        scene_particles(canvas,ui.phase,t.c('secondary'),count=18 if is_cyber else 10,alpha=62)
    d=ImageDraw.Draw(canvas)

    asset=None
    if ui.theme.id=='classic':asset='classic_portrait.png'
    elif ui.theme.id=='cyberpunk':asset='cyberpunk_portrait.png'
    elif ui.theme.id=='blackice':asset='blackice_portrait.png'
    asset_path=(Path(getattr(ui,'root','.'))/'assets'/'home'/asset) if asset else None

    # The Beast is now a scene anchor, not a framed thumbnail. Art may bleed
    # under HUD layers and fade into the information field.
    with _scene_layer(
        ui,'home.creature.art','creature',(6,38,278,269),z=20,
        signals=('pwnagotchi.mood','beast.expression'),
        update_class='ambient',cacheable=True,resource_class='moderate',
        reduced_motion='static_art',
    ):
        used=False
        if asset_path is not None:
            used=paste_scene_asset(
                canvas,asset_path,(6,38,278,269),phase=ui.phase,opacity=248,
                brightness_pulse=.035,tint=glow_col,tint_strength=.04,
                edge_fade=54,
            )
        d=ImageDraw.Draw(canvas)
        if not used:
            _portrait(d,(18,48,260,260),t,state,ui.phase,
                      variant='cyber' if is_cyber or is_synth else 'ice' if is_ice else 'tactical' if is_tactical else 'classic')

    name=str(_v(state,'progression.beast.name','BEAST')).strip() or 'BEAST'
    lvl=int(_v(state,'progression.level',1) or 1)
    stage=str(_v(state,'progression.stage','Hatchling')).upper()
    mode=str(_v(state,'context.mode.effective','pwn')).upper()
    mood=str(_v(state,'beast.expression',_v(state,'pwnagotchi.mood','awake'))).replace('_',' ').upper()
    status=str(_v(state,'pwnagotchi.status',_v(state,'beast.status_text','SCANNING THE FIELD'))).strip()
    if not status or status=='--':status='SCANNING THE FIELD'

    # Identity floats over the visual scene, avoiding a hard portrait border.
    d.text((18,205),name[:18],font=f['large'],fill=t.c('text'))
    d.text((19,230),f'LV {lvl:02d}  {stage[:14]}',font=f['small'],fill=t.c('secondary'))
    d.text((19,247),mood[:18],font=f['tiny'],fill=t.c('dim'))

    # Compact glass HUD on the right. This is one information plane, not a wall
    # of cards; large live values dominate and labels recede.
    alpha_panel(canvas,(282,47,470,216),fill=t.c('panel'),outline=t.c('edge'),alpha=176,radius=12)
    d=ImageDraw.Draw(canvas)
    d.text((298,60),'FIELD LINK',font=f['tiny'],fill=t.c('dim'))
    d.text((298,75),mode[:14],font=f['large'],fill=t.c('accent'))
    d.text((299,101),f"CHANNEL {_v(state,'radio.primary.channel','--')}",font=f['small'],fill=t.c('text'))
    d.line((298,122,454,122),fill=t.c('edge'))

    rows=[
        ('APS',_v(state,'wifi.ap_count',0),t.c('primary')),
        ('CLIENTS',_v(state,'wifi.client_count',0),t.c('info')),
        ('HANDSHAKES',_v(state,'pwnagotchi.handshakes',0),t.c('accent')),
        ('PMKIDS',_v(state,'pwnagotchi.pmkids',_v(state,'captures.pmkid_count',0)),t.c('secondary')),
    ]
    for i,(lab,val,col) in enumerate(rows):
        x=298+(i%2)*82;y=136+(i//2)*38
        d.text((x,y),lab,font=f['micro'],fill=t.c('dim'))
        d.text((x,y+11),str(val)[:8],font=f['medium'],fill=col)

    # Bottom conversational/status ribbon stays visually connected to the scene.
    alpha_panel(canvas,(10,272-39,470,269),fill=t.c('panel'),outline=t.c('edge'),alpha=150,radius=9)
    d=ImageDraw.Draw(canvas)
    d.text((20,239),status[:48],font=f['small'],fill=t.c('text'))
    session=_v(state,'wifi.encounters.session_unique',0)
    _text_right(d,458,254,f'{session} SIGNALS',f['tiny'],t.c('info'))

    # Small live system chips remain visible without becoming the composition.
    temp=_v(state,'system.temp.cpu_c','--');temp=f'{temp:.0f}C' if isinstance(temp,(int,float)) else '--'
    cpu=_v(state,'system.cpu.total','--');cpu=f'{cpu:.0f}%' if isinstance(cpu,(int,float)) else '--'
    gps='GPS' if state.get('gps.fix') else 'NO GPS'
    d.text((300,198),f'{gps}  ·  CPU {cpu}  ·  {temp}',font=f['micro'],fill=t.c('dim'))
    return True

def _wopr_scene(d,state,ui):
    t=ui.theme;f=ui.fonts
    d.rectangle((0,34,480,278),fill=t.c('bg'))
    for x in range(8,473,32):d.line((x,43,x,268),fill=t.c('grid'))
    for y in range(43,269,24):d.line((8,y,472,y),fill=t.c('grid'))
    d.rectangle((8,43,472,268),outline=t.c('primary'),width=1)
    d.line((13,69,467,69),fill=t.c('edge'))
    d.text((18,50),'GREETINGS, OPERATOR.',font=f['small'],fill=t.c('secondary'))
    d.text((18,76),'SYSTEM STATUS',font=f['tiny'],fill=t.c('dim'))
    health=str(_v(state,'health.core.state','STARTING')).upper()
    rows=[
        ('RECON STATUS',str(_v(state,'context.mode.effective','PWN')).upper(),t.c('accent')),
        ('NETWORKS',_v(state,'wifi.ap_count',0),t.c('text')),
        ('CLIENTS',_v(state,'wifi.client_count',0),t.c('text')),
        ('HANDSHAKES',_v(state,'pwnagotchi.handshakes',0),t.c('secondary')),
        ('CHANNEL',_v(state,'radio.primary.channel','--'),t.c('info')),
        ('CORE',health,t.c('accent') if health=='HEALTHY' else t.c('warn')),
    ]
    yy=94
    for lab,val,col in rows:
        d.text((20,yy),lab,font=f['tiny'],fill=t.c('primary'))
        d.text((132,yy),'►',font=f['tiny'],fill=t.c('secondary'))
        d.text((151,yy),str(val)[:16],font=f['small'],fill=col)
        yy+=23

    cx,cy=362,151;r=72
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=t.c('secondary'),width=2)
    for frac in (.36,.68):
        rr=int(r*frac);d.ellipse((cx-rr,cy-r,cx+rr,cy+r),outline=t.c('edge'))
    d.line((cx-r,cy,cx+r,cy),fill=t.c('edge'));d.line((cx,cy-r,cx,cy+r),fill=t.c('edge'))
    for dy in (-34,34):
        span=int(math.sqrt(max(0,r*r-dy*dy)));d.line((cx-span,cy+dy,cx+span,cy+dy),fill=t.c('edge'))
    sweep=(ui.phase*.52)%(math.pi*2);sx=cx+int(math.cos(sweep)*r);sy=cy+int(math.sin(sweep)*r)
    d.line((cx,cy,sx,sy),fill=t.c('accent'),width=1)
    for i,(dx,dy) in enumerate(((-34,-19),(24,-28),(40,17),(-18,37),(5,8))):
        col=t.c('danger') if i==0 and health!='HEALTHY' else t.c('secondary')
        d.rectangle((cx+dx-2,cy+dy-2,cx+dx+2,cy+dy+2),fill=col)
    d.text((294,229),'NORAD FIELD DISPLAY',font=f['micro'],fill=t.c('dim'))
    d.text((18,248),'AWAITING NEXT SIGNAL...',font=f['small'],fill=t.c('secondary'))
    return True


def _lcars_scene(d,state,ui):
    t=ui.theme;f=ui.fonts
    d.rounded_rectangle((8,43,86,267),radius=13,fill=t.c('secondary'))
    d.rectangle((52,76,86,235),fill=t.c('bg'))
    d.rounded_rectangle((94,43,314,267),radius=10,fill=_mix(t.c('panel'),t.c('primary'),.06),outline=t.c('primary'))
    _portrait(d,(108,60,300,211),t,state,ui.phase,variant='classic')
    name=str(_v(state,'progression.beast.name','BEAST')).upper();lvl=int(_v(state,'progression.level',1) or 1)
    d.text((112,220),name[:16],font=f['small'],fill=t.c('accent'))
    d.text((112,238),f'LEVEL {lvl:02d} · {_v(state,"progression.stage","HATCHLING")}',font=f['tiny'],fill=t.c('dim'))
    labels=[('MODE',str(_v(state,'context.mode.effective','PWN')).upper()),('APS',_v(state,'wifi.ap_count',0)),('CH',_v(state,'radio.primary.channel','--')),('CPU',f"{_v(state,'system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--'),('TEMP',f"{_v(state,'system.temp.cpu_c',0):.0f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--')]
    cols=[t.c('primary'),t.c('accent'),t.c('info'),t.c('secondary'),t.c('warn')]
    yy=50
    for i,(lab,val) in enumerate(labels):
        d.rounded_rectangle((323,yy,470,yy+37),radius=8,fill=_mix(t.c('panel'),cols[i],.07),outline=cols[i])
        d.text((334,yy+6),lab,font=f['micro'],fill=t.c('dim'))
        _text_right(d,459,yy+14,str(val),f['small'],cols[i]);yy+=43
    return True


def _terminal_scene(d,state,ui):
    t=ui.theme;f=ui.fonts
    d.rectangle((8,43,472,268),fill=_mix(t.c('bg'),t.c('primary'),.025),outline=t.c('primary'))
    d.text((18,50),'beast@field:~$ status --live',font=f['small'],fill=t.c('primary'))
    _portrait(d,(18,78,200,229),t,state,ui.phase,variant='classic')
    rows=[('mode',str(_v(state,'context.mode.effective','pwn')).lower()),('channel',_v(state,'radio.primary.channel','--')),('aps',_v(state,'wifi.ap_count',0)),('clients',_v(state,'wifi.client_count',0)),('handshakes',_v(state,'pwnagotchi.handshakes',0)),('cpu',f"{_v(state,'system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--'),('temp',f"{_v(state,'system.temp.cpu_c',0):.0f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--')]
    yy=82
    for lab,val in rows:
        d.text((220,yy),f'{lab:>10}:',font=f['tiny'],fill=t.c('dim'));d.text((302,yy),str(val),font=f['small'],fill=t.c('text'));yy+=23
    d.text((18,244),'> observing real state..._',font=f['small'],fill=t.c('accent'))
    return True


def render_home_scene(d, state, ui) -> bool:
    """Render a theme-selected structural Home scene.

    Theme.home_scene is deliberately semantic. Built-ins and future Theme Packs
    can select a composition family independently of palette/background. Unknown
    scene ids fail closed to the legacy page renderer.
    """
    scene=str(getattr(ui.theme,'home_scene',None) or '').strip().lower()
    if not scene:return False
    if scene=='hero':return _hero_scene(d,state,ui,variant='classic')
    if scene=='hero_cyber':return _hero_scene(d,state,ui,variant='cyber')
    if scene=='hero_ice':return _hero_scene(d,state,ui,variant='ice')
    if scene=='hero_synth':return _hero_scene(d,state,ui,variant='synth')
    if scene=='hero_tactical':return _hero_scene(d,state,ui,variant='tactical')
    if scene=='wopr':return _wopr_scene(d,state,ui)
    if scene=='lcars':return _lcars_scene(d,state,ui)
    if scene=='terminal':return _terminal_scene(d,state,ui)
    return False
