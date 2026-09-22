from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont
from .customization import DASHBOARD_GRID_COLS,DASHBOARD_GRID_ROWS


def _font(size:int):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try:return ImageFont.truetype(p,size)
        except Exception:pass
    return ImageFont.load_default()


def _fmt(key,value):
    if value is None:return '--'
    try:
        if key.endswith('_pct') or 'percent' in key:return f'{float(value):.0f}%'
        if key.endswith('_c') or '.temp.' in key:return f'{float(value):.1f}C'
        if key.endswith('_w'):return f'{float(value):.1f}W'
        if isinstance(value,float):return f'{value:.1f}'
    except Exception:pass
    return str(value)[:24]


def render_responsive_board(size,theme,state,widgets,label='DASHBOARD'):
    """Native-size responsive renderer for user Boards.

    This intentionally covers Boards first. Other legacy pages continue through
    the 480x320 compatibility compositor until migrated individually.
    """
    w,h=map(int,size);im=Image.new('RGB',(w,h),theme.c('bg'));d=ImageDraw.Draw(im)
    scale=max(.8,min(2.2,min(w/480,h/320)));pad=max(8,round(12*scale));header=max(42,round(48*scale));footer=max(34,round(38*scale));gap=max(4,round(5*scale))
    d.rectangle((0,0,w,header),fill=theme.c('panel'));d.line((0,header-1,w,header-1),fill=theme.c('primary'),width=max(1,round(scale)))
    d.text((pad,round(10*scale)),str(label).upper()[:28],font=_font(max(15,round(18*scale))),fill=theme.c('primary'))
    d.text((w-round(160*scale),round(14*scale)),'RESPONSIVE BOARD',font=_font(max(8,round(9*scale))),fill=theme.c('dim'))
    x1,y1,x2,y2=pad,header+gap,w-pad,h-footer-gap
    width=x2-x1;height=y2-y1
    rows=[r for r in widgets if isinstance(r,dict) and bool(r.get('visible',True))];rows.sort(key=lambda r:(int(r.get('z',0)),str(r.get('id') or '')))
    for idx,r in enumerate(rows):
        gx=max(0,min(DASHBOARD_GRID_COLS-1,int(r.get('x',0))));gy=max(0,min(DASHBOARD_GRID_ROWS-1,int(r.get('y',0))))
        gw=max(1,min(DASHBOARD_GRID_COLS-gx,int(r.get('w',4))));gh=max(1,min(DASHBOARD_GRID_ROWS-gy,int(r.get('h',3))))
        a=x1+round(width*gx/DASHBOARD_GRID_COLS);b=y1+round(height*gy/DASHBOARD_GRID_ROWS);c=x1+round(width*(gx+gw)/DASHBOARD_GRID_COLS)-gap;e=y1+round(height*(gy+gh)/DASHBOARD_GRID_ROWS)-gap
        d.rounded_rectangle((a,b,max(a+40,c),max(b+34,e)),radius=max(4,round(6*scale)),fill=theme.c('panel2'),outline=theme.c('edge'),width=max(1,round(scale)))
        key=str(r.get('key') or '');lab=str(r.get('label') or key.split('.')[-1] or 'DATA').upper()[:22]
        val=state.get(key) if key else None;accent=[theme.c('primary'),theme.c('accent'),theme.c('info'),theme.c('secondary')][idx%4]
        d.text((a+round(8*scale),b+round(7*scale)),lab,font=_font(max(8,round(9*scale))),fill=theme.c('dim'))
        d.text((a+round(8*scale),b+round(25*scale)),_fmt(key,val),font=_font(max(13,round(18*scale))),fill=accent)
        if e-b>70*scale:d.text((a+round(8*scale),e-round(18*scale)),key[:34],font=_font(max(7,round(8*scale))),fill=theme.c('dim'))
    d.rectangle((0,h-footer,w,h),fill=theme.c('panel'));d.text((pad,h-footer+round(9*scale)),'LIVE CANONICAL TELEMETRY  //  NATIVE RESPONSIVE BOARD',font=_font(max(8,round(9*scale))),fill=theme.c('dim'))
    return im
