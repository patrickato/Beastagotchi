from __future__ import annotations

import colorsys
import math
from PIL import Image, ImageDraw


def _mix(a, b, p: float):
    p=max(0.0,min(1.0,float(p)))
    return tuple(int(a[i]*(1.0-p)+b[i]*p) for i in range(3))


def _hash32(v: int) -> int:
    v=(v ^ 61) ^ (v >> 16)
    v=(v + (v << 3)) & 0xffffffff
    v=v ^ (v >> 4)
    v=(v * 0x27d4eb2d) & 0xffffffff
    v=v ^ (v >> 15)
    return v & 0xffffffff


_MATRIX_GLYPH_SETS = {
    "mixed": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&*+-=<>?/[]{}:;|\\^~",
    "digits": "0123456789",
    "binary": "01",
    "hex": "0123456789ABCDEF",
    "symbols": "#$%&*+-=<>?/[]{}:;|\\^~",
}

_NAMED_MATRIX_COLORS = {
    "off": None,
    "green": (0,255,65),
    "lime": (137,255,57),
    "cyan": (0,229,255),
    "blue": (65,125,255),
    "violet": (190,80,255),
    "magenta": (255,66,220),
    "red": (255,44,74),
    "orange": (255,126,34),
    "amber": (255,174,35),
    "yellow": (255,226,65),
    "white": (255,255,255),
}


def _named_matrix_color(name, fallback=None):
    c=_NAMED_MATRIX_COLORS.get(str(name or '').lower())
    return fallback if c is None else c


def _hex_color(value, fallback):
    if isinstance(value,(tuple,list)) and len(value)>=3:
        return tuple(int(max(0,min(255,x))) for x in value[:3])
    try:
        s=str(value).strip().lstrip('#')
        if len(s)==6:return tuple(int(s[i:i+2],16) for i in (0,2,4))
    except Exception:pass
    return fallback


def _runtime_matrix_options(theme, runtime_options: dict | None = None) -> dict:
    o=dict(getattr(theme,'background_options',{}) or {})
    r=dict(runtime_options or {})
    density=str(r.get('density',o.get('density','dense')))
    speed_mode=str(r.get('speed_mode',o.get('speed_mode','fast')))
    spacing={'sparse':22,'light':17,'normal':13,'dense':10,'heavy':8,'storm':6,'deluge':5}.get(density,int(o.get('column_spacing',8)))
    speed_mult={'drift':0.38,'slow':0.62,'normal':0.92,'fast':1.28,'fury':1.72,'torrent':2.25}.get(speed_mode,1.0)
    o['column_spacing']=max(5,int(r.get('column_spacing',spacing)))
    o['speed']=float(r.get('speed',o.get('speed',88.0)))*speed_mult
    o['layer_mode']=str(r.get('layer_mode',o.get('layer_mode','mixed')))
    o['foreground_fraction']=max(0.0,min(0.65,float(r.get('foreground_fraction',o.get('foreground_fraction',0.14)))))
    o['palette_mode']=str(r.get('palette_mode',o.get('palette_mode','green')))
    o['primary_hex']=r.get('primary_hex',o.get('primary_hex'))
    o['secondary_hex']=r.get('secondary_hex',o.get('secondary_hex'))
    o['tertiary_hex']=r.get('tertiary_hex',o.get('tertiary_hex'))
    o['quaternary_hex']=r.get('quaternary_hex',o.get('quaternary_hex'))
    o['primary_color']=str(r.get('primary_color',o.get('primary_color','green')))
    o['secondary_color']=str(r.get('secondary_color',o.get('secondary_color','off')))
    o['tertiary_color']=str(r.get('tertiary_color',o.get('tertiary_color','off')))
    o['quaternary_color']=str(r.get('quaternary_color',o.get('quaternary_color','off')))
    o['accent_mix']=str(r.get('accent_mix',o.get('accent_mix','off')))
    o['glyph_set']=str(r.get('glyph_set',o.get('glyph_set','mixed')))
    o['trail_mode']=str(r.get('trail_mode',o.get('trail_mode','normal')))
    trail_ranges={'short':(4,9),'normal':(7,18),'long':(12,28),'extreme':(18,40)}
    if o['trail_mode'] in trail_ranges:
        o['min_trail'],o['max_trail']=trail_ranges[o['trail_mode']]
    return o


def _matrix_x_for_col(col:int, spacing:int, x_offset:int)->int:
    """Return a stable but deliberately non-uniform X position.

    A perfectly regular X/Y lattice looked fine in off-screen renders but made
    diagonal/Moire bands on the physical 480x320 TFT.  Streams remain vertical;
    only the distance *between* columns varies slightly.
    """
    x=int(x_offset)
    for j in range(max(0,int(col))):
        seed=_hash32(j+0x71A7)
        # spacing-1 .. spacing+2, never less than 4 pixels
        x += max(4,int(spacing) + int(seed & 0x3) - 1)
    return x


def matrix_column_state(col: int, phase: float, options: dict | None = None):
    o=options or {}
    spacing=max(5,int(o.get('column_spacing',10)))
    base_speed=float(o.get('speed',78.0))
    base_step=max(8,int(o.get('glyph_step',10)))
    x_offset=int(o.get('x_offset',5))
    min_trail=max(4,int(o.get('min_trail',6)))
    max_trail=max(min_trail,int(o.get('max_trail',15)))
    top,bottom=34,278
    height=bottom-top
    seed=_hash32(col+0x5BEA57)
    x=_matrix_x_for_col(col,spacing,x_offset)
    # Per-stream vertical cadence breaks the regular character lattice which
    # caused the camera-visible diagonal bands while preserving vertical fall.
    glyph_step=max(8,base_step + int((seed>>13)&0x3) - 1)
    speed=base_speed*(0.61+(((seed>>8)&0xff)/255.0)*0.83)
    trail=min_trail + ((seed>>17) % (max_trail-min_trail+1))
    period=height + trail*glyph_step + 83 + ((seed>>24)&0x7f)
    offset=(seed % period)
    head=top + ((phase*speed + offset) % period) - trail*glyph_step
    resting=((seed>>5)&0x0f)==0 and ((int(phase*1.1)+(seed&7))%11)<2
    return {'x':x,'head':head,'speed':speed,'trail':trail,'glyph_step':glyph_step,'seed':seed,'resting':resting}


def _matrix_base_palette(theme, o: dict, col: int, phase: float):
    mode=str(o.get('palette_mode','green'))
    default_primary=theme.c('primary')
    default_head=theme.c('matrix_head',theme.c('text'))
    dim=theme.c('grid')
    if mode=='cyan':
        primary=(0,229,255); head=(225,254,255)
    elif mode=='red':
        primary=(255,44,74); head=(255,225,229)
    elif mode=='violet':
        primary=(190,80,255); head=(249,231,255)
    elif mode=='amber':
        primary=(255,174,35); head=(255,246,198)
    elif mode=='rainbow':
        h=((col*0.061)+(phase*0.015))%1.0
        primary=tuple(int(v*255) for v in colorsys.hsv_to_rgb(h,0.9,1.0))
        head=_mix(primary,(255,255,255),0.78)
    elif mode=='holiday':
        palette=[(255,54,62),(35,255,92),(255,222,65),(65,170,255)]
        primary=palette[col%len(palette)]; head=_mix(primary,(255,255,255),0.72)
    elif mode=='custom':
        primary=_hex_color(o.get('primary_hex'),_named_matrix_color(o.get('primary_color'),default_primary)); head=_mix(primary,(255,255,255),0.78)
    else:
        primary=default_primary; head=default_head
    return primary,head,dim


def _matrix_stream_color(theme,o,col,k,trail,phase):
    primary,head,dim=_matrix_base_palette(theme,o,col,phase)
    mix=str(o.get('accent_mix','sparse'))
    seed=_hash32(col*991 + k*47)
    accents=[]
    slot_pairs=(('secondary_hex','secondary_color'),('tertiary_hex','tertiary_color'),('quaternary_hex','quaternary_color'))
    for hex_key,name_key in slot_pairs:
        if o.get(hex_key):
            accents.append(_hex_color(o.get(hex_key),primary))
        else:
            named=_NAMED_MATRIX_COLORS.get(str(o.get(name_key,'off')).lower())
            if named is not None: accents.append(named)
    if not accents and mix!='off' and str(o.get('palette_mode','green'))!='custom':
        # Preset palettes may use their theme-native accent colors only when the
        # user explicitly enables accents. Custom palettes never invent colors.
        accents=[theme.c('secondary'),theme.c('accent')]
    use_accent=False
    if accents:
        if mix=='balanced':use_accent=(seed%3)==0
        elif mix=='heavy':use_accent=(seed%5)==0
        elif mix=='medium':use_accent=(seed%9)==0
        elif mix=='sparse':use_accent=(seed%19)==0
    if use_accent:
        primary=accents[seed%len(accents)]; head=_mix(primary,(255,255,255),0.75)
    if k==0:return head
    if k<=2:return primary
    fade=(k-2)/max(1,trail-2)
    return _mix(primary,dim,min(0.94,fade*0.94))


def _is_foreground_stream(seed:int, fraction:float)->bool:
    return ((seed>>3)&0xffff) < int(65535*fraction)


def _draw_matrix(d,theme,phase,o:dict,foreground:bool=False,alpha_scale:float=1.0):
    spacing=max(5,int(o.get('column_spacing',8))); x_offset=int(o.get('x_offset',4))
    top,bottom=34,278
    layer_mode=str(o.get('layer_mode','mixed')); fraction=float(o.get('foreground_fraction',0.14))
    # Variable spacing means column count is discovered by X position rather
    # than calculated from a rigid grid.  Hard cap prevents bad configs.
    for col in range(128):
        st=matrix_column_state(col,phase,o); seed=st['seed']
        if st['x']>=480:break
        is_fg=_is_foreground_stream(seed,fraction)
        if layer_mode=='background' and foreground:continue
        if layer_mode=='foreground' and not foreground:continue
        if layer_mode=='mixed' and foreground!=is_fg:continue
        if layer_mode=='mixed' and (not foreground) and is_fg:continue
        x=st['x']; trail=st['trail']; head=st['head']; glyph_step=st['glyph_step']
        if x>=480 or st['resting']:continue
        mut=int(phase*5.2)
        for k in range(trail):
            y=int(head-k*glyph_step)
            if not (top<=y<bottom):continue
            # Small deterministic holes keep each stream from becoming a solid
            # ruler and further suppress physical-display diagonal patterning.
            hole_seed=_hash32(seed ^ (k*0x2C1B3C6D) ^ int(phase*0.7))
            if k>1 and (hole_seed % 17)==0:continue
            c=_matrix_stream_color(theme,o,col,k,trail,phase)
            if alpha_scale<1.0 and len(c)==3:
                # ImageDraw on an RGBA overlay accepts alpha in color tuple.
                c=tuple(c)+(int(255*alpha_scale),)
            gseed=_hash32(seed ^ (k*0x45D9F3B) ^ (mut*0x119DE1F3))
            glyphs=_MATRIX_GLYPH_SETS.get(str(o.get('glyph_set','mixed')),_MATRIX_GLYPH_SETS['mixed'])
            ch=glyphs[gseed % len(glyphs)]
            # A tiny fixed per-glyph vertical offset breaks the last rigid Y
            # cadence that can form diagonal Moire bands on the physical TFT.
            # X never changes, so the stream still reads as vertical rain.
            yj=((_hash32(seed ^ (k*0x9E3779B9))>>5)%5)-2
            d.text((x,y+yj),ch,fill=c)


def draw_background(d, theme, phase: float, runtime_options: dict | None = None):
    bg=theme.c('bg'); d.rectangle((0,0,480,320),fill=bg)
    kind=getattr(theme,'background','grid');opts=dict(runtime_options or {})
    if kind=='none':
        if str(opts.get('ambient','off'))=='soft':
            for i in range(26):
                x=(i*79+17)%480;y=38+((i*43+11)%232)
                c=theme.c('grid') if i%3 else theme.c('edge');d.point((x,y),fill=c)
        return
    if kind=='grid':
        dens=str(opts.get('grid_density','normal'));step={'off':0,'light':36,'normal':24,'dense':16}.get(dens,24)
        if step:
            pulse=str(opts.get('pulse_level','subtle'));base=theme.c('grid')
            if pulse!='off':
                amount=(0.10 if pulse=='subtle' else 0.24)*(0.5+0.5*math.sin(phase*1.4))
                base=_mix(base,theme.c('primary'),amount)
            for x in range(0,480,step): d.line((x,34,x,278),fill=base)
            for y in range(38,278,max(14,int(step*.83))): d.line((0,y,480,y),fill=base)
    elif kind=='matrix':
        o=_runtime_matrix_options(theme,runtime_options);_draw_matrix(d,theme,phase,o,foreground=False)
    elif kind=='starfield':
        dens=str(opts.get('star_density','normal'));count={'sparse':28,'normal':54,'dense':88,'nebula':120}.get(dens,54)
        tw=str(opts.get('twinkle','normal'));tw_rate={'off':0.0,'low':0.8,'normal':1.8,'high':3.5}.get(tw,1.8)
        for i in range(count):
            x=(i*83+17)%480;y=38+((i*47+11)%232)
            bright=(i+int(phase*tw_rate))%7==0 if tw_rate else False;r=2 if bright else 1
            col=theme.c('info') if bright else theme.c('dim');d.ellipse((x-r,y-r,x+r,y+r),fill=col)
        if dens=='nebula':
            for i in range(5):
                x=40+i*97;y=90+int(math.sin(phase*.35+i)*28);d.arc((x-55,y-35,x+55,y+35),190,340,fill=theme.c('grid'),width=2)
        if str(opts.get('orbit','on'))!='off':d.arc((300,60,510,270),160,285,fill=theme.c('edge'),width=1)
    elif kind=='ice':
        dens=str(opts.get('frost_density','normal'));count={'light':7,'normal':12,'heavy':18,'whiteout':28}.get(dens,12)
        drift=str(opts.get('drift','slow'));spd={'still':0,'slow':1.5,'normal':3.0,'fast':6.0}.get(drift,1.5)
        for i in range(count):
            x=(i*43+int(phase*spd))%540-30;d.line((x,34,x-55,278),fill=theme.c('grid'))
        cross=max(3,count//2)
        for i in range(cross):
            y=50+i*max(12,210//max(1,cross));d.line((0,y,130,y-20,260,y+8,480,y-16),fill=theme.c('grid'))
    elif kind=='hunter':
        dens=str(opts.get('grid_density','normal'));step={'off':0,'light':34,'normal':24,'dense':16}.get(dens,24)
        if step:
            for y in range(40,278,step):d.line((0,y,480,y),fill=theme.c('grid'))
            for x in range(0,480,step*2):d.line((x,34,x,278),fill=theme.c('grid'))
        if str(opts.get('reticle','on'))!='off':
            cx,cy=240,154;r=70+int(math.sin(phase*2)*5)
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=theme.c('grid'))
            for a in (0,90,180,270):
                rad=math.radians(a);x=cx+int(math.cos(rad)*r);y=cy+int(math.sin(rad)*r);dx=int(math.cos(rad)*14);dy=int(math.sin(rad)*14);d.line((x,y,x-dx,y-dy),fill=theme.c('edge'),width=2)
    elif kind=='synthwave':
        horizon=154
        stars=str(opts.get('stars','normal'));count={'off':0,'sparse':14,'normal':28,'dense':48}.get(stars,28)
        for i in range(count):
            x=(i*101+37)%480;y=38+((i*53+7)%(horizon-48));bright=((i+int(phase*.8))%9)==0
            d.point((x,y),fill=theme.c('info') if bright else theme.c('dim'))
        sun=str(opts.get('sun','half'))
        if sun!='off':
            r=42 if sun=='full' else 35;cy=horizon-8 if sun=='half' else horizon-28
            d.ellipse((240-r,cy-r,240+r,cy+r),fill=theme.c('secondary'),outline=theme.c('accent'))
            # Dark horizon slices create the recognizable striped synth sun.
            for sy in range(cy+4,cy+r,8):d.rectangle((240-r,sy,240+r,sy+3),fill=theme.c('bg'))
        glow=str(opts.get('horizon_glow','soft'))
        if glow!='off':
            d.line((0,horizon,479,horizon),fill=theme.c('accent'),width=3 if glow=='hot' else 1)
            if glow=='hot':d.line((0,horizon+4,479,horizon+4),fill=theme.c('secondary'))
        dens=str(opts.get('grid_density','normal'));n={'off':0,'light':6,'normal':10,'dense':16}.get(dens,10)
        if n:
            # Perspective rays converge at the horizon; horizontal spacing grows toward the viewer.
            for i in range(n+1):
                xb=int(i*480/max(1,n));d.line((240,horizon,xb,278),fill=theme.c('grid'))
            for i in range(1,10):
                frac=(i/10.0)**1.7;y=int(horizon+(278-horizon)*frac);d.line((0,y,479,y),fill=theme.c('grid'))
    elif kind=='tactical':
        dens=str(opts.get('grid_density','normal'));step={'off':0,'light':48,'normal':32,'dense':20}.get(dens,32)
        if step:
            for x in range(0,480,step):d.line((x,34,x,278),fill=theme.c('grid'))
            for y in range(38,278,step):d.line((0,y,479,y),fill=theme.c('grid'))
        cx,cy=240,155
        if str(opts.get('scope','on'))!='off':
            for r in (34,68,103):d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=theme.c('edge'))
            d.line((cx-124,cy,cx+124,cy),fill=theme.c('primary'));d.line((cx,cy-112,cx,cy+112),fill=theme.c('primary'))
        sweep=str(opts.get('sweep','slow'));spd={'off':0.0,'slow':0.35,'normal':0.75,'fast':1.35}.get(sweep,0.35)
        if spd:
            a=(phase*spd)%(math.pi*2);r=103;x=cx+int(math.cos(a)*r);y=cy+int(math.sin(a)*r);d.line((cx,cy,x,y),fill=theme.c('accent'),width=2)
        if str(opts.get('brackets','on'))!='off':
            c=theme.c('secondary');d.line((10,50,10,78,34,78),fill=c,width=2);d.line((470,50,470,78,446,78),fill=c,width=2);d.line((10,258,10,230,34,230),fill=c,width=2);d.line((470,258,470,230,446,230),fill=c,width=2)
    elif kind=='ghost':
        if str(opts.get('ambient','soft'))=='soft':
            for i in range(18):
                x=(i*127+31)%480;y=42+((i*61+19)%224);c=theme.c('grid') if i%3 else theme.c('edge');d.point((x,y),fill=c)
        if str(opts.get('edge_trace','on'))!='off':
            c=theme.c('edge');d.line((6,58,6,38,28,38),fill=c);d.line((474,58,474,38,452,38),fill=c);d.line((6,254,6,274,28,274),fill=c);d.line((474,254,474,274,452,274),fill=c)
    elif kind=='cyberpunk':
        # Pure visual chrome: no line, building, or rain element represents
        # measured telemetry.  Live data remains inside labeled widgets.
        lanes=str(opts.get('lanes','normal'));lane_n={'off':0,'light':3,'normal':5,'dense':8}.get(lanes,5)
        horizon=214
        if str(opts.get('city','on'))!='off':
            # Stable skyline silhouette with neon edge caps.
            x=0
            for i in range(22):
                w=14+((_hash32(i+0xC17) >> 3) % 23)
                h=22+((_hash32(i+0x51A7) >> 7) % 74)
                x2=min(479,x+w)
                d.rectangle((x,horizon-h,x2,horizon),fill=_mix(theme.c('bg'),theme.c('panel'),0.55))
                if i%3==0:d.line((x,horizon-h,x2,horizon-h),fill=theme.c('secondary'))
                if i%4==1:d.line((x2,horizon-h,x2,horizon),fill=theme.c('edge'))
                x=x2+5
                if x>=480:break
        if lane_n:
            # Perspective street/light lanes converge below the live content.
            van_x,van_y=240,horizon
            for i in range(lane_n+1):
                xb=int(i*480/max(1,lane_n))
                col=theme.c('primary') if i%2==0 else theme.c('secondary')
                d.line((van_x,van_y,xb,278),fill=_mix(theme.c('bg'),col,0.55))
            for i in range(1,7):
                frac=(i/7.0)**1.65;y=int(van_y+(278-van_y)*frac)
                d.line((0,y,479,y),fill=theme.c('grid'))
        rain=str(opts.get('rain','sparse'));count={'off':0,'sparse':10,'normal':20,'dense':34}.get(rain,10)
        for i in range(count):
            x=(i*61+23)%480
            y=40+((i*47+int(phase*(11+i%4)))%158)
            ln=4+(i%4)*3
            d.line((x,y,x,y+ln),fill=theme.c('grid'))
        glitch=str(opts.get('glitch','low'));gcount={'off':0,'low':2,'normal':4,'high':7}.get(glitch,2)
        # Deterministic short edge accents only; deliberately outside data panels.
        for i in range(gcount):
            seed=_hash32(i+int(phase*2.0)*37)
            y=38+(seed%232);ln=10+((seed>>8)%34)
            x=0 if i%2==0 else 480-ln
            d.line((x,y,x+ln,y),fill=theme.c('accent'))
    elif kind=='wopr':
        # WOPR/NORAD is a command-room aesthetic. Range rings and grid are
        # decorative framing, never implied contacts or target positions.
        dens=str(opts.get('grid_density','normal'));step={'off':0,'light':48,'normal':32,'dense':20}.get(dens,32)
        if step:
            for x in range(0,480,step):d.line((x,34,x,278),fill=theme.c('grid'))
            for y in range(38,278,step):d.line((0,y,479,y),fill=theme.c('grid'))
        if str(opts.get('rings','on'))!='off':
            cx,cy=240,156
            for r in (38,74,110):d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=theme.c('edge'))
            d.line((cx-124,cy,cx+124,cy),fill=theme.c('grid'))
            d.line((cx,cy-116,cx,cy+116),fill=theme.c('grid'))
        nodes=str(opts.get('blips','normal'));count={'off':0,'sparse':4,'normal':8,'dense':14}.get(nodes,8)
        for i in range(count):
            # Ambient UI nodes are intentionally pinned near frame edges so
            # they cannot be confused with live RF contacts in Recon.
            seed=_hash32(i+0xA11CE);x=10+(seed%52) if i%2==0 else 418+(seed%52)
            y=46+((seed>>9)%214);r=1 if i%3 else 2
            d.rectangle((x-r,y-r,x+r,y+r),fill=theme.c('dim'))
        sweep=str(opts.get('sweep','slow'));spd={'off':0.0,'slow':0.25,'normal':0.55,'fast':1.0}.get(sweep,0.25)
        if spd and str(opts.get('rings','on'))!='off':
            cx,cy=240,156;a=(phase*spd)%(math.pi*2);r=110
            d.line((cx,cy,cx+int(math.cos(a)*r),cy+int(math.sin(a)*r)),fill=theme.c('secondary'))
    elif kind=='lcars':
        stars=str(opts.get('stars','normal'));count={'off':0,'sparse':12,'normal':24,'dense':42}.get(stars,24)
        for i in range(count):
            x=(i*137+31)%480;y=38+((i*71+17)%222)
            d.point((x,y),fill=theme.c('dim') if i%5 else theme.c('info'))
        bands=str(opts.get('bands','full'))
        if bands!='off':
            # LCARS-style asymmetrical framing stays behind real widgets.
            thick=9 if bands=='full' else 5
            d.rounded_rectangle((5,42,80,42+thick),radius=thick//2,fill=theme.c('secondary'))
            d.rounded_rectangle((85,42,184,42+thick),radius=thick//2,fill=theme.c('accent'))
            d.rounded_rectangle((190,42,305,42+thick),radius=thick//2,fill=theme.c('primary'))
            d.rounded_rectangle((310,42,472,42+thick),radius=thick//2,fill=theme.c('info'))
            d.rounded_rectangle((5,263,115,272),radius=4,fill=theme.c('accent'))
            d.rounded_rectangle((120,263,260,272),radius=4,fill=theme.c('secondary'))
            d.rounded_rectangle((265,263,472,272),radius=4,fill=theme.c('primary'))
        pulse=str(opts.get('pulse','soft'));amount={'off':0.0,'soft':0.12,'normal':0.24,'bright':0.42}.get(pulse,0.12)
        if amount:
            col=_mix(theme.c('grid'),theme.c('primary'),amount*(0.5+0.5*math.sin(phase*1.25)))
            d.arc((150,72,330,252),205,335,fill=col,width=2)
    elif kind=='crt':
        grid=str(opts.get('grid','soft'));step={'off':0,'soft':32,'normal':24,'dense':16}.get(grid,32)
        phosphor=str(opts.get('phosphor','green'))
        pcol={'green':(72,255,126),'amber':(255,183,66),'white':(220,245,225)}.get(phosphor,theme.c('primary'))
        if step:
            gc=_mix(theme.c('bg'),pcol,0.12 if grid=='soft' else 0.20)
            for x in range(0,480,step):d.line((x,34,x,278),fill=gc)
            for y in range(38,278,step):d.line((0,y,479,y),fill=gc)
        noise=str(opts.get('noise','low'));count={'off':0,'low':18,'normal':36,'high':70}.get(noise,18)
        tick=int(phase*3.0)
        for i in range(count):
            seed=_hash32(i*97+tick*131);x=seed%480;y=36+((seed>>10)%240)
            d.point((x,y),fill=_mix(theme.c('bg'),pcol,0.18))
        bloom=str(opts.get('bloom','soft'))
        if bloom!='off':
            c=_mix(theme.c('bg'),pcol,0.18 if bloom=='soft' else 0.30)
            d.rectangle((2,36,477,276),outline=c,width=2 if bloom=='strong' else 1)


def draw_foreground_effects(image:Image.Image, theme, phase:float, runtime_options:dict|None=None)->Image.Image:
    kind=getattr(theme,'background','');opts=dict(runtime_options or {})
    if kind=='matrix':
        o=_runtime_matrix_options(theme,runtime_options)
        if str(o.get('layer_mode','mixed'))=='background':return image
        overlay=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(overlay);_draw_matrix(d,theme,phase,o,foreground=True,alpha_scale=0.58)
        return Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')
    if kind=='hunter' and str(opts.get('embers','sparse'))!='off':
        count={'sparse':10,'normal':22,'heavy':40}.get(str(opts.get('embers')),10);overlay=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(overlay)
        col=theme.c('accent')+(125,)
        for i in range(count):
            x=(i*97+int(phase*(23+(i%5)*4)))%500-10;y=274-((i*41+int(phase*(31+(i%7)*3)))%230);r=1 if i%4 else 2;d.ellipse((x-r,y-r,x+r,y+r),fill=col)
        return Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')
    if kind=='ice' and str(opts.get('crystal_overlay','subtle'))!='off':
        mode=str(opts.get('crystal_overlay'));count=8 if mode=='subtle' else 18;overlay=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(overlay);col=theme.c('secondary')+(52 if mode=='subtle' else 78,)
        for i in range(count):
            x=(i*67+23)%480;y=40+((i*103+17)%220);r=4+(i%4)*2
            d.line((x-r,y,x+r,y),fill=col);d.line((x,y-r,x,y+r),fill=col);d.line((x-r//2,y-r//2,x+r//2,y+r//2),fill=col);d.line((x-r//2,y+r//2,x+r//2,y-r//2),fill=col)
        return Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')
    if kind=='ghost' and str(opts.get('ghosts','sparse'))!='off':
        mode=str(opts.get('ghosts'));count=5 if mode=='sparse' else 11;overlay=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(overlay);col=theme.c('primary')+(28 if mode=='sparse' else 42,)
        for i in range(count):
            x=(i*113+int(phase*(3+i%3)))%500-10;y=48+((i*73+int(phase*(2+i%2)))%208);r=8+(i%3)*4
            d.arc((x-r,y-r,x+r,y+r),185,350,fill=col,width=1)
        return Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')
    return image
