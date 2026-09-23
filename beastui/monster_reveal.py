from __future__ import annotations

import math
import time
from PIL import Image, ImageDraw


def reveal_active(state: dict, now: float | None = None, dismissed_id: str | None = None) -> bool:
    now=float(time.time() if now is None else now)
    rid=str(state.get('roster.monster_reveal.id') or '')
    if not rid or (dismissed_id and rid==dismissed_id):return False
    try:return now < float(state.get('roster.monster_reveal.until') or 0)
    except Exception:return False


def render_monster_reveal(image: Image.Image, state: dict, phase: float, theme, fonts, *, now: float | None = None, dismissed_id: str | None = None):
    now=float(time.time() if now is None else now)
    if not reveal_active(state,now,dismissed_id):return image
    created=float(state.get('roster.monster_reveal.created_at') or now);until=float(state.get('roster.monster_reveal.until') or created+12)
    duration=max(1.0,until-created);p=max(0.0,min(1.0,(now-created)/duration))
    name=str(state.get('roster.monster_reveal.name') or 'MONSTER')[:28]
    generation=int(state.get('roster.monster_reveal.generation') or 1);stage=str(state.get('roster.monster_reveal.stage') or 'Origin')
    parents=[str(x)[:18] for x in (state.get('roster.monster_reveal.parents') or [])][:2]
    mutation=state.get('roster.monster_reveal.mutation') if isinstance(state.get('roster.monster_reveal.mutation'),dict) else None
    first=bool(state.get('roster.monster_reveal.first_unlock'))
    accent=theme.c('accent');secondary=theme.c('secondary',accent);text=theme.c('text')
    ov=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(ov);w,h=image.size;cx=w//2;cy=145
    d.rectangle((0,0,w,h),fill=(0,0,0,205 if p<.82 else int(205*(1-p)/.18)))
    # Two lineage streams converge, then expand into the new identity.
    for side,col in ((-1,accent),(1,secondary)):
        for i in range(7):
            y=64+i*26;start_x=30 if side<0 else w-30
            q=min(1.0,p*2.1);x=int(start_x+(cx-start_x)*q)
            wob=int(math.sin(phase*3+i*1.7)*8*(1-q))
            d.line((start_x,y,x,cy+wob),fill=tuple(col)+(70+i*18,),width=1+(i%2))
    pulse=.5+.5*math.sin(phase*5.0);r=int(26+58*min(1.0,max(0.0,(p-.12)/.42))+7*pulse)
    for j in range(5):
        rr=max(8,r-j*10);alpha=max(25,155-j*24)
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=tuple(accent)+(alpha,),width=1 if j<3 else 2)
    traits=state.get('roster.monster_reveal.traits') if isinstance(state.get('roster.monster_reveal.traits'),dict) else {}
    eyes=str(traits.get('eyes') or 'unknown');aura=str(traits.get('aura') or 'unknown');motion=str(traits.get('motion') or 'unknown')
    if p>.28:
        label='MONSTER SYNTHESIS' if not first else 'MONSTERGOTCHI AWAKENS'
        tw=d.textbbox((0,0),label,font=fonts['medium'])[2];d.text((cx-tw//2,38),label,font=fonts['medium'],fill=tuple(accent)+(240,))
    if p>.48:
        tw=d.textbbox((0,0),name.upper(),font=fonts['title'])[2];d.text((cx-tw//2,218),name.upper(),font=fonts['title'],fill=tuple(text)+(245,))
        sub=f'GEN {generation} · {stage.upper()}';sw=d.textbbox((0,0),sub,font=fonts['tiny'])[2];d.text((cx-sw//2,241),sub,font=fonts['tiny'],fill=tuple(secondary)+(230,))
    if p>.62:
        lineage=' × '.join(parents) if parents else 'LINEAGE RECORDED';lw=d.textbbox((0,0),lineage,font=fonts['tiny'])[2];d.text((cx-lw//2,260),lineage,font=fonts['tiny'],fill=tuple(text)+(205,))
        traitline=f'{eyes} eyes · {aura} aura · {motion} motion';tw=d.textbbox((0,0),traitline,font=fonts['micro'])[2];d.text((cx-tw//2,278),traitline,font=fonts['micro'],fill=tuple(text)+(175,))
    if mutation and p>.70:
        mut=('MUTATION · '+str(mutation.get('id') or 'UNKNOWN')+' · '+str(mutation.get('rarity') or '').upper())[:54]
        mw=d.textbbox((0,0),mut,font=fonts['tiny'])[2];d.rounded_rectangle((cx-mw//2-8,294,cx+mw//2+8,315),radius=5,fill=(0,0,0,210),outline=tuple(accent)+(220,));d.text((cx-mw//2,299),mut,font=fonts['tiny'],fill=tuple(accent)+(240,))
    elif p>.70:
        hint='TAP TO CONTINUE';hw=d.textbbox((0,0),hint,font=fonts['micro'])[2];d.text((cx-hw//2,301),hint,font=fonts['micro'],fill=tuple(text)+(130,))
    return Image.alpha_composite(image.convert('RGBA'),ov).convert('RGB')
