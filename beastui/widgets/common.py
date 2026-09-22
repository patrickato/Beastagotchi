from __future__ import annotations

import math


def panel(d, box, theme, accent=None, fill=None, width=1):
    col = accent or theme.c("edge"); bg = fill or theme.c("panel")
    x1,y1,x2,y2=box
    g=getattr(theme,"geometry","classic")
    if g in {"cut","angular"}:
        cut=7 if g=="angular" else 5
        d.polygon([(x1+cut,y1),(x2-cut,y1),(x2,y1+cut),(x2,y2-cut),(x2-cut,y2),(x1+cut,y2),(x1,y2-cut),(x1,y1+cut)], fill=bg, outline=col)
    elif g=="lcars":
        d.rounded_rectangle(box,radius=10,fill=bg,outline=col,width=width)
        d.rectangle((x1,y1,x1+10,y2),fill=accent or theme.c("secondary"))
    elif g=="terminal":
        d.rectangle(box,fill=bg,outline=col,width=width)
        d.line((x1+3,y1+3,x1+15,y1+3),fill=theme.c("accent"))
    elif g=="minimal":
        d.rounded_rectangle(box,radius=8,fill=bg,outline=theme.c("edge"),width=1)
    else:
        d.rounded_rectangle(box, radius=5, fill=bg, outline=col, width=width)


def metric(d, box, label, value, fonts, theme, accent=None):
    panel(d, box, theme, accent=accent)
    x1,y1,x2,y2=box
    d.text((x1+6,y1+5), str(label).upper(), font=fonts["tiny"], fill=theme.c("dim"))
    text=str(value)
    d.text((x1+6,y1+17), text, font=fonts["medium"], fill=accent or theme.c("text"))


def sparkline(d, box, values, theme, accent=None):
    panel(d, box, theme)
    vals=[float(v) for v in values if isinstance(v,(int,float))]
    if len(vals)<2:return
    x1,y1,x2,y2=box; pad=5; lo=min(vals); hi=max(vals); span=max(.0001,hi-lo)
    pts=[]
    for i,v in enumerate(vals):
        x=x1+pad+int((x2-x1-pad*2)*i/(len(vals)-1)); y=y2-pad-int((y2-y1-pad*2)*(v-lo)/span); pts.append((x,y))
    d.line(pts, fill=accent or theme.c("accent"), width=2)


def channel_bars(d, box, aps, theme):
    panel(d, box, theme)
    x1,y1,x2,y2=box; counts={}
    for ap in aps or []:
        if isinstance(ap,dict) and isinstance(ap.get("channel"),(int,float)):
            ch=int(ap["channel"]); counts[ch]=counts.get(ch,0)+1
    channels=sorted(counts)
    if not channels:return
    maxv=max(counts.values())
    bw=max(2,(x2-x1-12)//max(1,len(channels)))
    for i,ch in enumerate(channels):
        h=int((y2-y1-22)*counts[ch]/maxv); x=x1+6+i*bw
        d.rectangle((x,y2-7-h,x+bw-2,y2-7), fill=theme.c("primary"))
