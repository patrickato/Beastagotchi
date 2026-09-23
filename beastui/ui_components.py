from __future__ import annotations


def clamp_pct(value) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except Exception:
        return 0.0


def progress_bar(d, box, value, theme, *, accent=None, show_marker=True):
    """Compact semantic progress indicator shared across themes."""
    x1,y1,x2,y2=map(int,box)
    pct=clamp_pct(value)
    bg=theme.c("edge")
    fg=accent or theme.c("accent")
    radius=max(1,min(4,(y2-y1)//2))
    d.rounded_rectangle((x1,y1,x2,y2),radius=radius,fill=bg)
    if pct>0:
        fill_x=x1+max(1,int((x2-x1)*pct/100.0))
        d.rounded_rectangle((x1,y1,fill_x,y2),radius=radius,fill=fg)
    if show_marker and 0<pct<100:
        mx=x1+int((x2-x1)*pct/100.0)
        d.line((mx,y1-1,mx,y2+1),fill=theme.c("text"),width=1)


def capsule(d, box, label, fonts, theme, *, accent=None, fill=None):
    x1,y1,x2,y2=map(int,box)
    col=accent or theme.c("accent")
    bg=fill or theme.c("panel2")
    d.rounded_rectangle((x1,y1,x2,y2),radius=max(3,(y2-y1)//2),fill=bg,outline=col,width=1)
    text=str(label).upper()
    # Monospace reference fonts are intentionally used for predictable bounds.
    approx=len(text)*6
    tx=max(x1+5, x1+((x2-x1)-approx)//2)
    d.text((tx,y1+4),text,font=fonts["tiny"],fill=col)


def stat_column(d, x, y, label, value, fonts, theme, *, accent=None):
    d.text((x,y),str(label).upper(),font=fonts["micro"],fill=theme.c("dim"))
    d.text((x,y+11),str(value),font=fonts["small"],fill=accent or theme.c("text"))


def status_dot(d, center, theme, state="ok"):
    x,y=center
    state=str(state or "").lower()
    if state in {"healthy","ok","ready","active","nominal"}:
        col=theme.c("accent")
    elif state in {"warning","attention","degraded","guarded"}:
        col=theme.c("warn")
    elif state in {"critical","error","failed","survival"}:
        col=theme.c("danger")
    else:
        col=theme.c("dim")
    d.ellipse((x-3,y-3,x+3,y+3),fill=col)
    return col
