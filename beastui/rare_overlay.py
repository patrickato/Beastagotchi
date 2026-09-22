from __future__ import annotations

import math
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


def _sigil(draw,x,y,r,kind,color,width=2):
    if kind=='eye':
        draw.arc((x-r,y-r//2,x+r,y+r//2),190,350,fill=color,width=width)
        draw.arc((x-r,y-r//2,x+r,y+r//2),10,170,fill=color,width=width)
        draw.ellipse((x-r//5,y-r//5,x+r//5,y+r//5),outline=color,width=width)
    elif kind=='spiral':
        pts=[]
        for i in range(56):
            a=i*0.42; rr=r*i/56.0; pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
        draw.line(pts,fill=color,width=width)
    elif kind=='gate':
        draw.rectangle((x-r,y-r,x+r,y+r),outline=color,width=width)
        draw.rectangle((x-r//2,y-r//2,x+r//2,y+r//2),outline=color,width=width)
        draw.line((x,y-r,x,y+r),fill=color,width=width)
    elif kind=='constellation':
        pts=[(x-r,y+r//3),(x-r//2,y-r//2),(x,y),(x+r//3,y-r),(x+r,y+r//2)]
        draw.line(pts,fill=color,width=width)
        for px,py in pts:draw.ellipse((px-2,py-2,px+2,py+2),fill=color)
    elif kind=='cipher':
        draw.ellipse((x-r,y-r,x+r,y+r),outline=color,width=width)
        for a in range(0,360,45):
            rad=math.radians(a);x1=x+math.cos(rad)*r*.55;y1=y+math.sin(rad)*r*.55;x2=x+math.cos(rad)*r;y2=y+math.sin(rad)*r
            draw.line((x1,y1,x2,y2),fill=color,width=width)
        draw.rectangle((x-r//4,y-r//4,x+r//4,y+r//4),outline=color,width=width)
    else: # veil
        draw.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],outline=color)
        draw.ellipse((x-r//2,y-r//2,x+r//2,y+r//2),outline=color,width=width)
        draw.line((x-r,y,x+r,y),fill=color,width=width)


def _omen_positions(presentation:str,phase:float):
    base=[(86,92,25),(382,118,19),(247,220,28)]
    p=str(presentation or 'fade')
    if p=='drift':
        return [(x+int(math.sin(phase*.35+i*1.4)*34), y+int(math.cos(phase*.27+i)*11), r) for i,(x,y,r) in enumerate(base)]
    if p=='cross':
        return [(-55+int((phase*(19+i*4)+i*177)%590),y,r) for i,(_x,y,r) in enumerate(base)]
    if p=='orbit':
        out=[]
        for i,(_x,_y,r) in enumerate(base):
            a=phase*(.20+.03*i)+i*2.09; rr=72+22*i
            out.append((240+int(math.cos(a)*rr),155+int(math.sin(a)*rr*.58),r))
        return out
    if p in {'ghost','apparition'}:
        return [(100+int(math.sin(phase*.17)*22),102,34),(363+int(math.cos(phase*.14)*18),177,27),(240,210+int(math.sin(phase*.21)*16),31)]
    return base


def _render_omen(overlay,state,phase,theme):
    kind=str(state.get('rare.moment.sigil') or 'veil')
    presentation=str(state.get('rare.moment.presentation') or 'fade')
    base=theme.c('accent')
    sig=Image.new('RGBA',overlay.size,(0,0,0,0));d=ImageDraw.Draw(sig)
    breath=0.5+0.5*math.sin(phase*1.15)
    if presentation=='ghost':alpha=int(18+48*breath)
    elif presentation=='cross':alpha=int(28+75*breath)
    else:alpha=int(32+70*breath)
    col=tuple(base)+(alpha,)
    for i,(x,y,r) in enumerate(_omen_positions(presentation,phase)):
        scale=1.0+0.10*math.sin(phase*.8+i*1.7)
        _sigil(d,x,y,int(r*scale),kind,col,1)
    if presentation in {'ghost','apparition'}:
        sig=sig.filter(ImageFilter.GaussianBlur(1.2 if presentation=='ghost' else 2.0))
    return Image.alpha_composite(overlay,sig)


def _cinematic_layer(size,kind,presentation,base,phase,rarity):
    layer=Image.new('RGBA',size,(0,0,0,0));d=ImageDraw.Draw(layer);w,h=size;cx,cy=w//2,151
    pulse=0.5+0.5*math.sin(phase*4.0)

    if presentation=='drift':
        for i in range(7):
            x=-70+int((phase*(28+i*4)+i*91)%620);y=54+((i*41)%188);r=18+(i%3)*8
            _sigil(d,x,y,r,kind,tuple(base)+(55+18*(i%4),),1+(i%2))
    elif presentation=='cross':
        for i in range(5):
            x=-90+int((phase*(38+i*5)+i*127)%700);y=70+i*38
            _sigil(d,x,y,26+i*3,kind,tuple(base)+(75,),2)
    elif presentation=='orbit':
        for i in range(8):
            a=phase*(.55+i*.025)+i*(math.tau/8);rr=44+i*10
            x=cx+int(math.cos(a)*rr*1.4);y=cy+int(math.sin(a)*rr*.72)
            _sigil(d,x,y,10+(i%3)*3,kind,tuple(base)+(72+i*12,),1)
        _sigil(d,cx,cy,int(42+7*pulse),kind,tuple(base)+(220,),3)
    elif presentation=='ghost':
        ghost=Image.new('RGBA',size,(0,0,0,0));gd=ImageDraw.Draw(ghost)
        _sigil(gd,cx+int(math.sin(phase*.22)*46),cy+int(math.cos(phase*.18)*16),72,kind,tuple(base)+(135,),3)
        ghost=ghost.filter(ImageFilter.GaussianBlur(2.5));layer=Image.alpha_composite(layer,ghost);d=ImageDraw.Draw(layer)
        for i in range(3):
            _sigil(d,110+i*130,80+(i%2)*130,22,kind,tuple(base)+(45,),1)
    elif presentation=='storm':
        for i in range(18):
            seed=i*1103515245+int(phase*6)*12345
            x=(seed>>3)%w;y=42+((seed>>11)%220);r=8+((seed>>19)%22)
            _sigil(d,x,y,r,kind,tuple(base)+(28+((seed>>7)%86),),1)
        for i in range(6):
            r=int(34+i*24+10*math.sin(phase*2+i));d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=tuple(base)+(35+i*20,),width=1)
    elif presentation=='apparition':
        # Large spectral mark materializes from a blurred under-image into crisp geometry.
        ghost=Image.new('RGBA',size,(0,0,0,0));gd=ImageDraw.Draw(ghost)
        rr=int(88+12*math.sin(phase*.8));_sigil(gd,cx,cy,rr,kind,tuple(base)+(105,),4)
        ghost=ghost.filter(ImageFilter.GaussianBlur(5.0-2.5*pulse));layer=Image.alpha_composite(layer,ghost);d=ImageDraw.Draw(layer)
        _sigil(d,cx,cy,int(58+8*pulse),kind,tuple(base)+(215,),2)
    elif presentation=='cinematic':
        # Highest-budget procedural fallback. Pre-rendered clips can supersede this
        # later without changing the scheduler or witness semantics.
        for i in range(10):
            r=int(22+i*18+12*math.sin(phase*(1.1+i*.04)+i));alpha=min(210,24+i*17)
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=tuple(base)+(alpha,),width=1 if i<7 else 2)
        for a in range(0,360,30):
            rad=math.radians(a+phase*11);r1=72;r2=138+18*math.sin(phase*.6+a)
            d.line((cx+math.cos(rad)*r1,cy+math.sin(rad)*r1*.72,cx+math.cos(rad)*r2,cy+math.sin(rad)*r2*.72),fill=tuple(base)+(80,),width=1)
        _sigil(d,cx,cy,int(62+10*pulse),kind,tuple(base)+(235,),3)
        # Iris bars give a cinematic opening/closing rhythm without video assets.
        bar=int(18+12*(0.5+0.5*math.sin(phase*.55)))
        d.rectangle((0,0,w,bar),fill=(0,0,0,150));d.rectangle((0,h-bar,w,h),fill=(0,0,0,150))
    else: # fade/default
        for i in range(7):
            r=int(30+i*20+8*math.sin(phase*2+i));d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=tuple(base)+(40+i*18,),width=1 if i<5 else 2)
        _sigil(d,cx,cy,int(55+8*pulse),kind,tuple(base)+(220,),3)

    return layer


def render_rare_overlay(image:Image.Image,state:dict,phase:float,theme,fonts):
    omen=bool(state.get('rare.omen.active'));active=bool(state.get('rare.moment.active'))
    if not (omen or active):return image
    base=theme.c('accent');kind=str(state.get('rare.moment.sigil') or 'veil');rarity=str(state.get('rare.moment.rarity') or 'rare').upper();presentation=str(state.get('rare.moment.presentation') or 'fade')
    # The scheduler/witness semantics remain authoritative, but costly procedural
    # presentations yield to the Resource Governor.  We deliberately do not
    # alter the persisted Rare Moment metadata; this is only a render fallback.
    if not bool(state.get('governor.rare.cinematic_allowed', True)) and presentation in {'cinematic','storm','apparition'}:
        presentation='fade'
    overlay=Image.new('RGBA',image.size,(0,0,0,0))
    if omen:overlay=_render_omen(overlay,state,phase,theme)
    if active:
        # Full-screen dimming deliberately lifts the Rare Moment out of the normal
        # UI. The rarity/presentation metadata selects one of several animation
        # families; future H.264 assets can replace the procedural layer.
        dim=Image.new('RGBA',image.size,(0,0,0,145 if rarity in {'RARE','EPIC'} else 165))
        overlay=Image.alpha_composite(overlay,dim)
        overlay=Image.alpha_composite(overlay,_cinematic_layer(image.size,kind,presentation,base,phase,rarity))
        d=ImageDraw.Draw(overlay);col=tuple(base)+(225,)
        d.rounded_rectangle((106,244,374,272),radius=6,fill=(0,0,0,198),outline=col,width=1)
        d.text((124,251),f'{rarity} // {presentation.upper()} // TOUCH TO WITNESS',font=fonts['tiny'],fill=col)
    return Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB')


def acknowledge_rare_event(state:dict,path:str='/var/lib/beastagotchi/ui/rare_ack.json')->bool:
    eid=str(state.get('rare.moment.id') or '')
    if not eid or not state.get('rare.moment.active'):return False
    try:
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
        import json
        p.write_text(json.dumps({'event_id':eid,'ts':time.time()},separators=(',',':'))+'\n')
        return True
    except Exception:
        return False
