from __future__ import annotations

from .design import TOKENS


def card(d, box, theme, *, accent=None, fill=None, width=1, radius=None):
    """Shared v0.19 card primitive with theme-driven color and common spacing."""
    x1,y1,x2,y2=box
    radius=TOKENS.radius_m if radius is None else int(radius)
    d.rounded_rectangle(
        (x1,y1,x2,y2),
        radius=radius,
        fill=fill if fill is not None else theme.c('panel'),
        outline=accent if accent is not None else theme.c('edge'),
        width=max(1,int(width)),
    )


def label_value(d, xy, label, value, fonts, theme, *, color=None, value_font='medium', max_chars=12):
    x,y=xy
    d.text((x,y),str(label).upper(),font=fonts['micro'],fill=theme.c('dim'))
    d.text((x,y+11),str(value)[:max_chars],font=fonts[value_font],fill=color or theme.c('text'))


def status_badge(d, xy, text, fonts, theme, *, color=None, min_width=0):
    x,y=xy
    text=str(text).upper()
    color=color or theme.c('accent')
    bbox=d.textbbox((0,0),text,font=fonts['tiny'])
    tw=max(0,bbox[2]-bbox[0])
    w=max(int(min_width),tw+16)
    d.rounded_rectangle((x,y,x+w,y+20),radius=TOKENS.radius_s,fill=theme.c('panel2'),outline=color)
    d.text((x+8,y+6),text,font=fonts['tiny'],fill=color)
    return w


def progress_bar(d, box, value, theme, *, color=None):
    x1,y1,x2,y2=box
    try:p=max(0.0,min(1.0,float(value)/100.0))
    except Exception:p=0.0
    color=color or theme.c('accent')
    d.rounded_rectangle((x1,y1,x2,y2),radius=2,fill=theme.c('edge'))
    if p>0:
        fill_x=x1+max(1,int((x2-x1)*p))
        d.rounded_rectangle((x1,y1,fill_x,y2),radius=2,fill=color)


def divider(d, x1, y, x2, theme):
    d.line((x1,y,x2,y),fill=theme.c('edge'))


def section_title(d, xy, title, fonts, theme, *, color=None):
    x,y=xy
    d.text((x,y),str(title).upper(),font=fonts['tiny'],fill=color or theme.c('dim'))


def empty_state(d, box, title, detail, fonts, theme, *, accent=None, hint=None):
    """Readable honest empty/unavailable state for the 480x320 cockpit."""
    x1,y1,x2,y2=box
    accent=accent or theme.c('dim')
    card(d,box,theme,accent=accent)
    title=str(title).upper()
    detail=str(detail)
    tb=d.textbbox((0,0),title,font=fonts['medium'])
    tw=max(0,tb[2]-tb[0])
    d.text((x1+max(10,((x2-x1)-tw)//2),y1+22),title,font=fonts['medium'],fill=theme.c('text'))
    db=d.textbbox((0,0),detail,font=fonts['tiny'])
    dw=max(0,db[2]-db[0])
    d.text((x1+max(10,((x2-x1)-dw)//2),y1+48),detail,font=fonts['tiny'],fill=theme.c('dim'))
    if hint:
        hint=str(hint)
        hb=d.textbbox((0,0),hint,font=fonts['micro'])
        hw=max(0,hb[2]-hb[0])
        d.text((x1+max(10,((x2-x1)-hw)//2),y2-20),hint,font=fonts['micro'],fill=accent)


def summary_strip(d, box, items, fonts, theme, *, accent=None):
    """One calm summary card with evenly divided label/value cells."""
    rows=list(items or [])
    if not rows:
        return
    x1,y1,x2,y2=box
    card(d,box,theme,accent=accent or theme.c('edge'))
    width=max(1,x2-x1)
    cell=max(1,width//len(rows))
    for i,row in enumerate(rows):
        label=row[0] if len(row)>0 else ''
        value=row[1] if len(row)>1 else '--'
        color=row[2] if len(row)>2 else theme.c('text')
        cx=x1+10+i*cell
        label_value(d,(cx,y1+8),label,value,fonts,theme,color=color,value_font='small',max_chars=max(6,(cell-16)//6))
        if i<len(rows)-1:
            x=x1+(i+1)*cell
            d.line((x,y1+7,x,y2-7),fill=theme.c('edge'))
