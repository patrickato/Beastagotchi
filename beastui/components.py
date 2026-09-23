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
