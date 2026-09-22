from __future__ import annotations

import math
from .common import panel


def _vals(values):
    return [float(v) for v in values if isinstance(v,(int,float))]


def _bounds(box,pad=6):
    x1,y1,x2,y2=box
    return x1+pad,y1+pad,x2-pad,y2-pad


def _scale_points(values,box,pad=6):
    vals=_vals(values)
    if len(vals)<2:return [],vals
    xa,ya,xb,yb=_bounds(box,pad)
    lo=min(vals);hi=max(vals);span=max(1e-9,hi-lo)
    pts=[]
    for i,v in enumerate(vals):
        x=xa+int((xb-xa)*i/max(1,len(vals)-1))
        y=yb-int((yb-ya)*(v-lo)/span)
        pts.append((x,y))
    return pts,vals


def line_area(d, box, values, theme, accent=None, fill_area=True):
    panel(d, box, theme)
    pts,vals=_scale_points(values,box,6)
    if len(pts)<2:return
    x1,y1,x2,y2=box;col=accent or theme.c('accent')
    if fill_area:
        poly=pts+[(pts[-1][0],y2-6),(pts[0][0],y2-6)]
        d.polygon(poly, fill=theme.c('panel2'))
    d.line(pts,fill=col,width=2)


def multiline(d,box,series,theme,accents=None):
    panel(d,box,theme)
    rows=[_vals(v) for v in (series or [])]
    rows=[v for v in rows if len(v)>=2]
    if not rows:return
    allv=[x for r in rows for x in r];lo=min(allv);hi=max(allv);span=max(1e-9,hi-lo)
    xa,ya,xb,yb=_bounds(box,6)
    cols=accents or [theme.c('primary'),theme.c('accent'),theme.c('secondary'),theme.c('info')]
    for j,vals in enumerate(rows):
        pts=[]
        for i,v in enumerate(vals):
            x=xa+int((xb-xa)*i/max(1,len(vals)-1));y=yb-int((yb-ya)*(v-lo)/span);pts.append((x,y))
        d.line(pts,fill=cols[j%len(cols)],width=2 if j==0 else 1)


def bars(d, box, values, theme, accent=None):
    panel(d,box,theme); vals=_vals(values)
    if not vals:return
    x1,y1,x2,y2=box; pad=6; hi=max(max(vals),1e-6); bw=max(2,(x2-x1-pad*2)//len(vals))
    col=accent or theme.c('primary')
    for i,v in enumerate(vals):
        h=max(1,int((y2-y1-pad*2)*max(0,v)/hi)); x=x1+pad+i*bw
        d.rectangle((x,y2-pad-h,x+bw-2,y2-pad),fill=col)


def stacked_bars(d,box,series,theme,accents=None):
    panel(d,box,theme)
    rows=[_vals(v) for v in (series or [])]
    rows=[r for r in rows if r]
    if not rows:return
    n=max(len(r) for r in rows); totals=[sum((r[i] if i<len(r) else 0) for r in rows) for i in range(n)]
    hi=max(max(totals),1e-9);x1,y1,x2,y2=box;pad=6;bw=max(3,(x2-x1-pad*2)//n)
    cols=accents or [theme.c('primary'),theme.c('accent'),theme.c('secondary'),theme.c('info')]
    for i in range(n):
        y=y2-pad
        for j,r in enumerate(rows):
            v=max(0,r[i] if i<len(r) else 0);h=int((y2-y1-pad*2)*v/hi)
            if h:d.rectangle((x1+pad+i*bw,y-h,x1+pad+i*bw+bw-2,y),fill=cols[j%len(cols)])
            y-=h


def histogram(d,box,values,theme,accent=None,bins=10):
    vals=_vals(values);panel(d,box,theme)
    if not vals:return
    lo=min(vals);hi=max(vals)
    if abs(hi-lo)<1e-9:
        counts=[len(vals)]
    else:
        bins=max(4,min(18,int(bins)));counts=[0]*bins
        for v in vals:
            idx=min(bins-1,int((v-lo)/(hi-lo)*bins));counts[idx]+=1
    x1,y1,x2,y2=box;pad=6;mx=max(counts) if counts else 1;bw=max(2,(x2-x1-pad*2)//max(1,len(counts)))
    col=accent or theme.c('primary')
    for i,v in enumerate(counts):
        h=max(1,int((y2-y1-pad*2)*v/max(1,mx)));x=x1+pad+i*bw
        d.rectangle((x,y2-pad-h,x+bw-2,y2-pad),fill=col)


def waveform(d,box,values,theme,accent=None):
    panel(d,box,theme); vals=_vals(values)
    if len(vals)<2:return
    x1,y1,x2,y2=box;xa,ya,xb,yb=_bounds(box,5);mid=(ya+yb)//2
    d.line((xa,mid,xb,mid),fill=theme.c('grid'))
    mean=sum(vals)/len(vals);amp=max(max(abs(v-mean) for v in vals),1e-9);pts=[]
    for i,v in enumerate(vals):
        x=xa+int((xb-xa)*i/max(1,len(vals)-1));y=mid-int((v-mean)/amp*(yb-ya)*0.46);pts.append((x,y))
    d.line(pts,fill=accent or theme.c('accent'),width=2)


def waterfall(d,box,values,theme,accent=None):
    panel(d,box,theme); vals=_vals(values)
    if not vals:return
    x1,y1,x2,y2=box;xa,ya,xb,yb=_bounds(box,5);n=min(32,len(vals));vals=vals[-n:]
    lo=min(vals);hi=max(vals);span=max(1e-9,hi-lo);rowh=max(2,(yb-ya)//n);base=theme.c('panel2');top=accent or theme.c('accent')
    for i,v in enumerate(vals):
        p=max(0,min(1,(v-lo)/span));col=tuple(int(base[k]+(top[k]-base[k])*p) for k in range(3));y=yb-(i+1)*rowh
        # deterministic horizontal texture makes this read as a history strip rather than a solid block
        split=0.35+0.55*((i*37)%17)/16.0;xx=xa+int((xb-xa)*split)
        d.rectangle((xa,y,xx,y+rowh-1),fill=col);d.rectangle((xx+1,y,xb,y+rowh-1),fill=tuple(int(c*.55) for c in col))


def radial(d, box, value, theme, accent=None, minimum=0.0, maximum=100.0, label=None, font=None):
    panel(d,box,theme)
    x1,y1,x2,y2=box; cx=(x1+x2)//2; cy=(y1+y2)//2; r=max(8,min(x2-x1,y2-y1)//2-7)
    col=accent or theme.c('accent')
    d.arc((cx-r,cy-r,cx+r,cy+r),135,405,fill=theme.c('edge'),width=4)
    try: p=max(0,min(1,(float(value)-minimum)/max(1e-9,maximum-minimum)))
    except Exception: p=0
    d.arc((cx-r,cy-r,cx+r,cy+r),135,135+270*p,fill=col,width=4)
    if font:
        txt=f"{float(value):.0f}" if isinstance(value,(int,float)) else '--'
        d.text((cx-r//2,cy-7),txt,font=font,fill=theme.c('text'))
        if label:d.text((x1+5,y2-13),str(label),font=font,fill=theme.c('dim'))


def donut(d,box,values,theme,accents=None,center_text=None,font=None):
    panel(d,box,theme);vals=[max(0,v) for v in _vals(values)]
    if not vals:return
    x1,y1,x2,y2=box;cx=(x1+x2)//2;cy=(y1+y2)//2;r=max(8,min(x2-x1,y2-y1)//2-7);inner=max(4,int(r*.58));tot=sum(vals) or 1
    cols=accents or [theme.c('primary'),theme.c('accent'),theme.c('secondary'),theme.c('info')]
    a=-90.0
    for i,v in enumerate(vals):
        span=360.0*v/tot;d.pieslice((cx-r,cy-r,cx+r,cy+r),a,a+span,fill=cols[i%len(cols)]);a+=span
    d.ellipse((cx-inner,cy-inner,cx+inner,cy+inner),fill=theme.c('panel'))
    if center_text is not None and font:
        txt=str(center_text);d.text((cx-len(txt)*3,cy-6),txt,font=font,fill=theme.c('text'))


def radar(d, box, values, labels, theme, accent=None):
    panel(d,box,theme); vals=_vals(values)
    if len(vals)<3:return
    x1,y1,x2,y2=box; cx=(x1+x2)//2; cy=(y1+y2)//2; r=max(12,min(x2-x1,y2-y1)//2-10); n=len(vals)
    col=accent or theme.c('accent')
    for frac in (.33,.66,1.0):
        pts=[]
        for i in range(n):
            a=-math.pi/2+2*math.pi*i/n; pts.append((cx+int(math.cos(a)*r*frac),cy+int(math.sin(a)*r*frac)))
        d.polygon(pts,outline=theme.c('edge'))
    m=max(max(vals),1.0); pts=[]
    for i,v in enumerate(vals):
        a=-math.pi/2+2*math.pi*i/n
        d.line((cx,cy,cx+int(math.cos(a)*r),cy+int(math.sin(a)*r)),fill=theme.c('grid'))
        rr=r*max(0,v)/m; pts.append((cx+int(math.cos(a)*rr),cy+int(math.sin(a)*rr)))
    d.polygon(pts,outline=col)


def polar(d,box,values,theme,accent=None):
    panel(d,box,theme);vals=_vals(values)
    if not vals:return
    x1,y1,x2,y2=box;cx=(x1+x2)//2;cy=(y1+y2)//2;r=max(10,min(x2-x1,y2-y1)//2-9);m=max(max(vals),1.0);col=accent or theme.c('accent')
    for frac in (.33,.66,1.0):d.ellipse((cx-r*frac,cy-r*frac,cx+r*frac,cy+r*frac),outline=theme.c('grid'))
    n=len(vals)
    for i,v in enumerate(vals):
        a=-math.pi/2+2*math.pi*i/n;rr=r*max(0,v)/m;x=cx+int(math.cos(a)*rr);y=cy+int(math.sin(a)*rr)
        d.line((cx,cy,x,y),fill=col,width=2);d.ellipse((x-2,y-2,x+2,y+2),fill=theme.c('text'))


def signal_meter(d,box,value,theme,accent=None,minimum=0,maximum=100):
    panel(d,box,theme);x1,y1,x2,y2=box;col=accent or theme.c('accent')
    try:p=max(0,min(1,(float(value)-minimum)/max(1e-9,maximum-minimum)))
    except Exception:p=0
    barsn=12;gap=2;usable=x2-x1-12;bw=max(2,(usable-(barsn-1)*gap)//barsn)
    for i in range(barsn):
        h=6+int((y2-y1-24)*(i+1)/barsn);x=x1+6+i*(bw+gap);y=y2-7-h
        fill=col if (i+1)/barsn<=p else theme.c('panel2');d.rectangle((x,y,x+bw,y2-7),fill=fill,outline=theme.c('grid'))


def heatmap(d, box, matrix, theme, accent=None):
    panel(d,box,theme)
    if not matrix or not isinstance(matrix,list):return
    rows=[r for r in matrix if isinstance(r,list)]
    if not rows:return
    cols=max((len(r) for r in rows),default=0)
    if cols<1:return
    vals=[float(v) for r in rows for v in r if isinstance(v,(int,float))]; hi=max(vals) if vals else 1.0; hi=max(hi,1e-9)
    x1,y1,x2,y2=box; pad=5; cw=max(1,(x2-x1-pad*2)//cols); ch=max(1,(y2-y1-pad*2)//len(rows))
    base=accent or theme.c('primary'); bg=theme.c('panel2')
    for rr,row in enumerate(rows):
        for cc in range(cols):
            v=float(row[cc]) if cc<len(row) and isinstance(row[cc],(int,float)) else 0.0
            p=max(0,min(1,v/hi));col=tuple(int(bg[i]+(base[i]-bg[i])*p) for i in range(3));xa=x1+pad+cc*cw; ya=y1+pad+rr*ch
            d.rectangle((xa,ya,xa+cw-1,ya+ch-1),fill=col)


def timeline(d,box,events,theme,accent=None):
    panel(d,box,theme);events=[e for e in (events or []) if isinstance(e,dict)]
    if not events:return
    x1,y1,x2,y2=box;xa,ya,xb,yb=_bounds(box,6);mid=(ya+yb)//2;d.line((xa,mid,xb,mid),fill=theme.c('edge'))
    col=accent or theme.c('accent');n=min(24,len(events));rows=events[-n:]
    for i,e in enumerate(rows):
        x=xa+int((xb-xa)*i/max(1,n-1));sev=str(e.get('severity') or 'info');c=theme.c('danger') if sev in {'critical','error'} else theme.c('warn') if sev=='warning' else col
        h=13 if sev in {'critical','error'} else 9 if sev=='warning' else 5;d.line((x,mid-h,x,mid+h),fill=c,width=2)


def microtrend(d,box,value,values,theme,accent=None,font=None,label=None):
    panel(d,box,theme);x1,y1,x2,y2=box;col=accent or theme.c('accent')
    if font:
        d.text((x1+6,y1+5),str(label or '').upper(),font=font,fill=theme.c('dim'));d.text((x1+6,y1+17),str(value),font=font,fill=col)
    pts,_=_scale_points(values,(x1+(x2-x1)//2,y1+5,x2-4,y2-5),3)
    if len(pts)>=2:d.line(pts,fill=col,width=2)
