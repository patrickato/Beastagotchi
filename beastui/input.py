from __future__ import annotations

import json
import logging
import os
import re
import select
import statistics
import struct
import threading
import time
from collections import deque
from pathlib import Path

log = logging.getLogger("beastui.touch")

FMT = "llHHi"
SIZE = struct.calcsize(FMT)
EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
SYN_REPORT = 0
BTN_TOUCH = 330
ABS_X, ABS_Y = 0, 1
ABS_MT_POSITION_X, ABS_MT_POSITION_Y = 53, 54
TRACE_PATH = Path("/run/beastagotchi/touch-gestures.jsonl")


def _discover_ads7846() -> str | None:
    """Resolve the ADS7846 event node if event numbering changed after reboot."""
    try:
        text = open("/proc/bus/input/devices").read()
    except Exception:
        return None
    for block in text.split("\n\n"):
        if "ADS7846 Touchscreen" not in block:
            continue
        m = re.search(r"^H: Handlers=(.*)$", block, re.M)
        if not m:
            continue
        for tok in m.group(1).split():
            if tok.startswith("event"):
                path = "/dev/input/" + tok
                if os.path.exists(path):
                    return path
    return None


def _median_point(points, n=5, from_end=False):
    if not points:
        return (0, 0)
    pts = list(points[-n:] if from_end else points[:n])
    return (int(statistics.median([p[0] for p in pts])), int(statistics.median([p[1] for p in pts])))


def _dedupe(points, min_dist=2):
    out=[]
    for p in points:
        if not out or abs(p[0]-out[-1][0]) + abs(p[1]-out[-1][1]) >= min_dist:
            out.append(p)
    return out or list(points[:1])


def _trend_delta(vals):
    """Least-squares trend expressed as full-gesture displacement.

    This resists one or two bad lift-off samples much better than relying on the
    final coordinate alone.
    """
    n=len(vals)
    if n < 2:
        return 0.0
    mx=(n-1)/2.0
    my=sum(vals)/n
    den=sum((i-mx)**2 for i in range(n))
    if not den:
        return 0.0
    slope=sum((i-mx)*(v-my) for i,v in enumerate(vals))/den
    return slope*(n-1)


def classify_gesture(points, duration):
    """Classify a small resistive-panel gesture.

    v0.5.2 uses synchronized touch samples plus a full-path trend estimate. The
    direction therefore comes from the gesture as a whole, not one noisy first
    or last coordinate.
    """
    if not points:
        return None, None

    pts=_dedupe(list(points))
    n=len(pts)
    edge_n=max(2, min(5, max(2, n//4)))
    edge_n=min(edge_n,n)
    s=_median_point(pts,edge_n,False)
    e=_median_point(pts,edge_n,True)
    dx,dy=e[0]-s[0],e[1]-s[1]
    adx,ady=abs(dx),abs(dy)

    xs=sorted(p[0] for p in pts)
    ys=sorted(p[1] for p in pts)
    trim=1 if len(pts)>=8 else 0
    sx=xs[-1-trim]-xs[trim] if len(xs)>2*trim else 0
    sy=ys[-1-trim]-ys[trim] if len(ys)>2*trim else 0

    trend_x=_trend_delta([p[0] for p in pts])
    trend_y=_trend_delta([p[1] for p in pts])
    motion_x=max(adx,abs(trend_x))
    motion_y=max(ady,abs(trend_y))

    base={
        "x":e[0],"y":e[1],
        "start_x":s[0],"start_y":s[1],
        "duration":duration,"dx":dx,"dy":dy,
        "trend_dx":round(trend_x,1),"trend_dy":round(trend_y,1),
        "spread_x":sx,"spread_y":sy,
        "samples":len(pts),
    }

    # Long press remains forgiving of the wobble typical of a 3.5-inch ADS7846.
    if duration>=0.70 and max(sx,sy)<46 and max(motion_x,motion_y)<36:
        return "long_press",base

    # Horizontal swipes get a slightly easier threshold than vertical gestures.
    # The finger has less physical travel available across the tiny panel once
    # the enclosure/bezel is taken into account.
    if duration<=2.2:
        if motion_x>=38 and motion_x>=motion_y*1.08:
            signed=trend_x if abs(trend_x)>=24 else dx
            return "swipe",dict(base,axis="x",delta=1 if signed<0 else -1,
                                direction="left" if signed<0 else "right")
        if motion_y>=44 and motion_y>=motion_x*1.08:
            signed=trend_y if abs(trend_y)>=24 else dy
            return "swipe",dict(base,axis="y",delta=1 if signed<0 else -1,
                                direction="up" if signed<0 else "down")

    return "tap",base


class TouchInput(threading.Thread):
    def __init__(self,config_path:str,callback)->None:
        super().__init__(daemon=True,name="beast-ui-touch")
        cfg=json.loads(open(config_path).read())
        configured=cfg.get("device","/dev/input/event0")
        discovered=_discover_ads7846()
        self.device=discovered or configured
        tr=cfg.get("transform") or {}
        self.cx=tr.get("x",[1.0,0.0,0.0])
        self.cy=tr.get("y",[0.0,1.0,0.0])
        self.width=int(cfg.get("screen_width",480))
        self.height=int(cfg.get("screen_height",320))
        self.callback=callback
        self.stop_event=threading.Event()
        log.info("touch configured=%s resolved=%s",configured,self.device)

    def stop(self):
        self.stop_event.set()

    def map(self,rx,ry):
        x=self.cx[0]*rx+self.cx[1]*ry+self.cx[2]
        y=self.cy[0]*rx+self.cy[1]*ry+self.cy[2]
        return max(0,min(self.width-1,int(x))),max(0,min(self.height-1,int(y)))

    def _trace(self,kind,payload,path):
        """Keep a tiny volatile gesture trace for physical tuning.

        /run is RAM-backed/ephemeral on the target. The file is bounded and
        contains only mapped screen coordinates/timing, never network data.
        """
        try:
            TRACE_PATH.parent.mkdir(parents=True,exist_ok=True)
            if TRACE_PATH.exists() and TRACE_PATH.stat().st_size>512_000:
                TRACE_PATH.unlink()
            pts=list(path)
            if len(pts)>64:
                step=max(1,len(pts)//64)
                pts=pts[::step][:64]
            rec={"ts":time.time(),"kind":kind,"payload":payload,"path":pts}
            with TRACE_PATH.open("a") as f:
                f.write(json.dumps(rec,separators=(",",":"))+"\n")
        except Exception:
            log.debug("touch trace write failed",exc_info=True)

    def run(self):
        if not os.path.exists(self.device):
            log.error("touch device missing: %s",self.device)
            return

        rx=ry=None
        touching=False
        path=deque(maxlen=256)
        started=0.0
        down_reported=False
        last_drag_report=0.0

        # Linux input events arrive in frames terminated by SYN_REPORT. v0.5.1
        # appended a point after each ABS_X/ABS_Y event, which could mix a fresh
        # axis with the previous touch's other axis. That is particularly bad for
        # swipe direction. v0.5.2 samples only complete SYN frames.
        frame_x=False
        frame_y=False
        pending_down=False
        pending_up=False
        fresh_x=False
        fresh_y=False

        def append_sample(now):
            nonlocal down_reported,last_drag_report
            if rx is None or ry is None:
                return
            p=self.map(rx,ry)
            if not path or p!=path[-1]:
                path.append(p)
            if not down_reported:
                self.callback("touch_down",{"x":p[0],"y":p[1],"duration":0.0})
                down_reported=True
                last_drag_report=now
            elif now-last_drag_report>=0.040:
                self.callback("drag",{"x":p[0],"y":p[1],"duration":now-started})
                last_drag_report=now

        try:
            with open(self.device,"rb",buffering=0) as fd:
                log.info("touch reader active: %s",self.device)
                while not self.stop_event.is_set():
                    ready,_,_=select.select([fd],[],[],0.05)
                    if not ready:
                        continue
                    b=fd.read(SIZE)
                    if len(b)!=SIZE:
                        continue
                    _,_,typ,code,val=struct.unpack(FMT,b)

                    if typ==EV_ABS:
                        if code in (ABS_X,ABS_MT_POSITION_X):
                            rx=val;frame_x=True
                        elif code in (ABS_Y,ABS_MT_POSITION_Y):
                            ry=val;frame_y=True
                        continue

                    if typ==EV_KEY and code==BTN_TOUCH:
                        if val==1:
                            pending_down=True
                        elif val==0:
                            pending_up=True
                        continue

                    if typ!=EV_SYN or code!=SYN_REPORT:
                        continue

                    now=time.monotonic()

                    if pending_down and not touching:
                        touching=True
                        path.clear()
                        started=now
                        down_reported=False
                        last_drag_report=0.0
                        fresh_x=frame_x
                        fresh_y=frame_y
                    elif touching:
                        fresh_x=fresh_x or frame_x
                        fresh_y=fresh_y or frame_y

                    # Do not emit the first point until this touch has supplied a
                    # complete coordinate pair. This prevents stale coordinates
                    # from the previous contact becoming the new gesture start.
                    if touching and fresh_x and fresh_y and (frame_x or frame_y or not down_reported):
                        append_sample(now)

                    if pending_up and touching:
                        touching=False
                        duration=now-started
                        if path:
                            kind,payload=classify_gesture(path,duration)
                            self._trace(kind,payload,list(path))
                            if kind:
                                self.callback(kind,payload)
                            self.callback("touch_up",{
                                "x":payload.get("x",0) if payload else 0,
                                "y":payload.get("y",0) if payload else 0,
                                "duration":duration,
                            })
                        path.clear()
                        down_reported=False
                        fresh_x=fresh_y=False

                    pending_down=False
                    pending_up=False
                    frame_x=False
                    frame_y=False
        except OSError as exc:
            log.exception("touch reader failed: %s",exc)
