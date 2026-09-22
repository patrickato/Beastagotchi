#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import select
import shutil
import statistics
import struct
import subprocess
import sys
import tarfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/opt/beast-ui')
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from PIL import Image, ImageDraw, ImageFont
    from beastui.framebuffer import FrameBuffer
    from beastui.input import classify_gesture
except Exception as exc:
    print(f'ERROR: Beast UI/Pillow runtime unavailable: {exc}', file=sys.stderr)
    raise

FMT = 'llHHi'
SIZE = struct.calcsize(FMT)
EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
SYN_REPORT = 0
BTN_TOUCH = 330
ABS_X, ABS_Y, ABS_PRESSURE = 0, 1, 24
ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID = 47, 53, 54, 57
W, H = 480, 320
DATA_ROOT = Path('/var/lib/beastagotchi/touchlab')
TOUCH_CONFIG = Path('/opt/beast-ui/config/touch.json')
FB = '/dev/fb1'

# Linux ioctl helpers
_IOC_NRBITS=8; _IOC_TYPEBITS=8; _IOC_SIZEBITS=14; _IOC_DIRBITS=2
_IOC_NRSHIFT=0; _IOC_TYPESHIFT=_IOC_NRSHIFT+_IOC_NRBITS
_IOC_SIZESHIFT=_IOC_TYPESHIFT+_IOC_TYPEBITS
_IOC_DIRSHIFT=_IOC_SIZESHIFT+_IOC_SIZEBITS
_IOC_READ=2

def _IOC(direction, typ, nr, size):
    return ((direction << _IOC_DIRSHIFT) | (ord(typ) << _IOC_TYPESHIFT) |
            (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT))

def EVIOCGABS(axis):
    return _IOC(_IOC_READ, 'E', 0x40 + axis, struct.calcsize('iiiiii'))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def discover_ads7846():
    text = Path('/proc/bus/input/devices').read_text(errors='ignore') if Path('/proc/bus/input/devices').exists() else ''
    for block in text.split('\n\n'):
        if 'ADS7846 Touchscreen' not in block:
            continue
        m = re.search(r'^H: Handlers=(.*)$', block, re.M)
        if m:
            for token in m.group(1).split():
                if token.startswith('event') and Path('/dev/input', token).exists():
                    return '/dev/input/' + token, block
    return None, ''


def parse_abs_mask(block):
    m = re.search(r'^B: ABS=([0-9a-fA-F]+)$', block, re.M)
    if not m:
        return 0
    return int(m.group(1), 16)


def abs_info(device, axis):
    try:
        with open(device, 'rb', buffering=0) as fd:
            buf = bytearray(struct.calcsize('iiiiii'))
            fcntl.ioctl(fd, EVIOCGABS(axis), buf, True)
            value, minimum, maximum, fuzz, flat, resolution = struct.unpack('iiiiii', buf)
            return {'value': value, 'min': minimum, 'max': maximum, 'fuzz': fuzz,
                    'flat': flat, 'resolution': resolution}
    except Exception:
        return None


def capabilities():
    dev, block = discover_ads7846()
    mask = parse_abs_mask(block)
    axes = [i for i in range(0, 64) if mask & (1 << i)]
    out = {
        'generated_at': utc_now(),
        'device': dev,
        'device_block': block,
        'abs_mask_hex': hex(mask),
        'axes': axes,
        'has_x': ABS_X in axes,
        'has_y': ABS_Y in axes,
        'has_pressure': ABS_PRESSURE in axes,
        'has_multitouch_axes': any(a in axes for a in (ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID)),
        'axis_info': {},
        'screen': {'width': W, 'height': H},
    }
    if dev:
        for axis in [ABS_X, ABS_Y, ABS_PRESSURE, ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID]:
            info = abs_info(dev, axis)
            if info:
                out['axis_info'][str(axis)] = info
    # For this controller, absence of MT axes is decisive: only one coordinate pair exists.
    out['contact_model'] = 'multi-touch' if out['has_multitouch_axes'] else 'single-contact'
    return out


class Mapper:
    def __init__(self, config=TOUCH_CONFIG):
        cfg = json.loads(Path(config).read_text())
        tr = cfg.get('transform') or {}
        self.cx = tr.get('x', [1,0,0]); self.cy = tr.get('y', [0,1,0])
        self.cfg = cfg
    def map(self, rx, ry):
        x = self.cx[0]*rx + self.cx[1]*ry + self.cx[2]
        y = self.cy[0]*rx + self.cy[1]*ry + self.cy[2]
        return max(0,min(W-1,int(round(x)))), max(0,min(H-1,int(round(y))))


class RawTouch:
    def __init__(self, device, mapper):
        self.device=device; self.mapper=mapper
        self.fd=open(device,'rb',buffering=0)
        self.rx=self.ry=None; self.pressure=0; self.touching=False
        self.pending_down=False; self.pending_up=False
        self.frame_x=self.frame_y=False
        self.fresh_x=self.fresh_y=False
        self.down_emitted=False
    def close(self):
        try:self.fd.close()
        except Exception:pass
    def poll(self, timeout=0.05):
        ready,_,_=select.select([self.fd],[],[],timeout)
        if not ready:return []
        events=[]
        while True:
            b=self.fd.read(SIZE)
            if len(b)!=SIZE:break
            sec,usec,typ,code,val=struct.unpack(FMT,b)
            if typ==EV_ABS:
                if code==ABS_X:self.rx=val;self.frame_x=True
                elif code==ABS_Y:self.ry=val;self.frame_y=True
                elif code==ABS_PRESSURE:self.pressure=val
            elif typ==EV_KEY and code==BTN_TOUCH:
                if val==1:self.pending_down=True
                elif val==0:self.pending_up=True
            elif typ==EV_SYN and code==SYN_REPORT:
                now=time.monotonic()
                if self.pending_down and not self.touching:
                    self.touching=True
                    self.fresh_x=self.frame_x; self.fresh_y=self.frame_y
                    self.down_emitted=False
                elif self.touching:
                    self.fresh_x=self.fresh_x or self.frame_x
                    self.fresh_y=self.fresh_y or self.frame_y

                # Require a fresh coordinate pair for every new contact, exactly
                # like the production Beast input path. This avoids stale lift-off
                # coordinates contaminating the precision study.
                if self.touching and self.fresh_x and self.fresh_y and (self.frame_x or self.frame_y or not self.down_emitted):
                    sample=self._sample(now)
                    if sample is not None:
                        events.append(('down' if not self.down_emitted else 'move', sample))
                        self.down_emitted=True

                if self.pending_up and self.touching:
                    if self.down_emitted:
                        sample=self._sample(now)
                        if sample is not None:events.append(('up',sample))
                    self.touching=False;self.fresh_x=self.fresh_y=False;self.down_emitted=False

                self.pending_down=self.pending_up=False
                self.frame_x=self.frame_y=False
                if events:break
            r,_,_=select.select([self.fd],[],[],0)
            if not r:break
        return events
    def _sample(self, now):
        if self.rx is None or self.ry is None:return None
        x,y=self.mapper.map(self.rx,self.ry)
        return {'t':now, 'raw_x':self.rx, 'raw_y':self.ry, 'pressure':self.pressure, 'x':x, 'y':y}


def fonts():
    candidates=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
    bold_candidates=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
    f=next((x for x in candidates if Path(x).exists()),None)
    b=next((x for x in bold_candidates if Path(x).exists()),f)
    def mk(path,size):
        try:return ImageFont.truetype(path,size) if path else ImageFont.load_default()
        except:return ImageFont.load_default()
    return {'tiny':mk(f,11),'small':mk(f,14),'medium':mk(b,18),'large':mk(b,25),'huge':mk(b,34)}


class TouchLab:
    def __init__(self, mode):
        self.mode=mode
        self.cap=capabilities()
        if not self.cap.get('device'):
            raise RuntimeError('ADS7846 touchscreen not found')
        self.mapper=Mapper()
        self.touch=RawTouch(self.cap['device'], self.mapper)
        self.fb=FrameBuffer(FB,W,H)
        self.font=fonts()
        stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
        self.dir=DATA_ROOT/f'{stamp}_{mode}'
        self.dir.mkdir(parents=True,exist_ok=True)
        self.data={'schema':1,'mode':mode,'started_at':utc_now(),'capabilities':self.cap,
                   'touch_config':self.mapper.cfg,'contacts':[],'targets':[],'traces':[],
                   'pressure_prompts':[],'gestures':[]}
        self.active_contact=None
        self.last_frame=0
        self.status=''
    def save(self):
        self.data['ended_at']=utc_now()
        (self.dir/'session.json').write_text(json.dumps(self.data,indent=2))
        summary=self.analyze()
        (self.dir/'summary.json').write_text(json.dumps(summary,indent=2))
        (self.dir/'SUMMARY.md').write_text(self.summary_md(summary))
        # Keep a copy of current calibration for exact comparison.
        shutil.copy2(TOUCH_CONFIG,self.dir/'touch.json')
        Path(self.dir/'input_devices.txt').write_text(Path('/proc/bus/input/devices').read_text(errors='ignore'))
        return summary
    def handle_events(self, events):
        completed=[]
        for kind,s in events:
            if s is None:continue
            if kind=='down':
                self.active_contact={'started_at':utc_now(),'samples':[s]}
            elif kind=='move':
                if self.active_contact:self.active_contact['samples'].append(s)
            elif kind=='up':
                if self.active_contact:
                    self.active_contact['samples'].append(s)
                    self.active_contact['ended_at']=utc_now()
                    self.data['contacts'].append(self.active_contact)
                    completed.append(self.active_contact)
                    self.active_contact=None
        return completed
    def draw_base(self,title,subtitle='',step=''):
        im=Image.new('RGB',(W,H),(2,8,13));d=ImageDraw.Draw(im)
        d.rectangle((0,0,W-1,H-1),outline=(0,190,220),width=2)
        d.text((12,8),'BEAST TOUCH LAB',font=self.font['medium'],fill=(75,235,255))
        if step:d.text((W-12,10),step,font=self.font['small'],fill=(120,210,220),anchor='ra')
        d.text((12,40),title,font=self.font['large'],fill=(245,250,250))
        if subtitle:d.text((12,72),subtitle,font=self.font['small'],fill=(155,195,205))
        return im,d
    def write(self,im):
        self.fb.write(im)
    def wait_contact(self, draw_fn, min_samples=1):
        while True:
            im=draw_fn();self.write(im)
            ev=self.touch.poll(.05);done=self.handle_events(ev)
            if done:
                c=done[-1]
                if len(c['samples'])>=min_samples:return c
    def run(self):
        try:
            if self.mode=='stylus':self.run_stylus()
            elif self.mode=='finger':self.run_finger()
            else:raise ValueError(self.mode)
            summary=self.save()
            self.done_screen(summary)
        finally:
            self.touch.close();self.fb.close()
    def intro(self):
        cap=self.cap
        lines=[f"Device: {Path(cap['device']).name}  Contact: {cap['contact_model']}",
               f"Pressure axis: {'YES' if cap['has_pressure'] else 'NO'}   Multi-touch axes: {'YES' if cap['has_multitouch_axes'] else 'NO'}"]
        def dr():
            im,d=self.draw_base('STYLUS PASS' if self.mode=='stylus' else 'FINGER PASS',
                                'Guided measurements. Follow the prompts; every touch is logged.')
            y=112
            for line in lines:d.text((18,y),line,font=self.font['small'],fill=(160,230,185));y+=28
            d.rounded_rectangle((80,224,400,292),radius=12,outline=(0,210,235),width=3)
            d.text((240,245),'TAP TO BEGIN',font=self.font['medium'],fill=(230,250,255),anchor='ma')
            return im
        self.wait_contact(dr)
    def run_stylus(self):
        self.intro()
        xs=[20,130,240,350,459]; ys=[18,89,160,231,301]
        targets=[(x,y) for y in ys for x in xs]
        # serpentine to reduce hand travel
        targets=[]
        for row,y in enumerate(ys):
            rowx=xs if row%2==0 else list(reversed(xs))
            targets.extend((x,y) for x in rowx)
        for idx,(tx,ty) in enumerate(targets,1):
            attempts=0
            while True:
                def dr(tx=tx,ty=ty,idx=idx):
                    im,d=self.draw_base('PRECISION TARGETS','Tap the exact center with the stylus.',f'{idx}/{len(targets)}')
                    r=11
                    d.ellipse((tx-r,ty-r,tx+r,ty+r),outline=(255,230,60),width=2)
                    d.line((tx-16,ty,tx+16,ty),fill=(255,255,255),width=1);d.line((tx,ty-16,tx,ty+16),fill=(255,255,255),width=1)
                    return im
                c=self.wait_contact(dr)
                attempts+=1
                s=median_sample(c['samples'])
                err=math.hypot(s['x']-tx,s['y']-ty)
                self.data['targets'].append({'kind':'stylus','target':[tx,ty],'size':22,'attempt':attempts,
                                             'hit':err<=55,'sample':s,'error_px':round(err,2)})
                if err<=55 or attempts>=3:break
        guides=[
            ('HORIZONTAL',(45,105),(435,105),'Draw left to right along the guide.'),
            ('VERTICAL',(240,70),(240,280),'Draw top to bottom along the guide.'),
            ('DIAGONAL DOWN',(55,65),(425,270),'Trace the diagonal line.'),
            ('DIAGONAL UP',(55,270),(425,65),'Trace the diagonal line.'),
        ]
        for i,(name,a,b,msg) in enumerate(guides,1):
            def dr(name=name,a=a,b=b,msg=msg,i=i):
                im,d=self.draw_base(name,msg,f'{i}/{len(guides)+1}')
                d.line((*a,*b),fill=(75,235,255),width=3)
                d.ellipse((a[0]-7,a[1]-7,a[0]+7,a[1]+7),outline=(255,230,60),width=2)
                d.ellipse((b[0]-7,b[1]-7,b[0]+7,b[1]+7),outline=(255,230,60),width=2)
                return im
            c=self.wait_contact(dr,min_samples=4)
            self.data['traces'].append({'name':name,'contact':c})
        def circle_draw():
            im,d=self.draw_base('CIRCLE TRACE','Trace one full circle with the stylus.',f'{len(guides)+1}/{len(guides)+1}')
            d.ellipse((140,60,340,260),outline=(75,235,255),width=3)
            d.ellipse((232,52,248,68),outline=(255,230,60),width=2)
            return im
        c=self.wait_contact(circle_draw,min_samples=8);self.data['traces'].append({'name':'CIRCLE','contact':c})
        for label in ['LIGHT','NORMAL','FIRM']:
            for n in range(1,4):
                def dr(label=label,n=n):
                    im,d=self.draw_base('PRESSURE SAMPLE',f'{label} stylus tap — use a comfortable {label.lower()} touch.',f'{label} {n}/3')
                    d.ellipse((210,130,270,190),outline=(255,230,60),width=3)
                    d.text((240,210),label,font=self.font['large'],fill=(220,250,255),anchor='ma')
                    return im
                c=self.wait_contact(dr)
                vals=[s['pressure'] for s in c['samples']]
                self.data['pressure_prompts'].append({'label':label,'contact':c,'pressure':stat(vals)})
        self.gesture_prompts(stylus=True)
    def run_finger(self):
        self.intro()
        # Deterministic spatial/size mix, including edge-adjacent targets.
        targets=[
            (54,70,64),(240,70,52),(426,70,44),(92,145,36),(240,145,64),(388,145,52),
            (45,230,44),(160,230,36),(320,230,52),(435,230,64),
            (28,292,52),(120,292,44),(240,292,36),(360,292,44),(452,292,52),
            (24,25,44),(120,25,52),(240,25,36),(360,25,52),(456,25,44),
        ]
        for idx,(tx,ty,size) in enumerate(targets,1):
            attempts=0
            while True:
                def dr(tx=tx,ty=ty,size=size,idx=idx):
                    im,d=self.draw_base('FINGER TARGETS',f'Tap the target naturally. Size {size}px.',f'{idx}/{len(targets)}')
                    r=size//2
                    d.ellipse((tx-r,ty-r,tx+r,ty+r),fill=(13,42,50),outline=(75,235,255),width=3)
                    d.ellipse((tx-4,ty-4,tx+4,ty+4),fill=(255,230,60))
                    return im
                c=self.wait_contact(dr)
                attempts+=1;s=median_sample(c['samples'])
                err=math.hypot(s['x']-tx,s['y']-ty);hit=err<=size/2
                self.data['targets'].append({'kind':'finger','target':[tx,ty],'size':size,'attempt':attempts,'hit':hit,
                                             'sample':s,'error_px':round(err,2)})
                if hit or attempts>=4:break
        # Footer hit zones mirror the real UI's large invisible controls.
        zones=[('PREV',(0,268,150,319)),('HOME',(151,268,329,319)),('NEXT',(330,268,479,319))]
        for name,rect in zones:
            for n in range(1,6):
                def dr(name=name,rect=rect,n=n):
                    im,d=self.draw_base('NAVIGATION HITBOXES',f'Tap {name} naturally with your finger.',f'{name} {n}/5')
                    d.rounded_rectangle(rect,radius=10,outline=(75,235,255),fill=(8,28,34),width=3)
                    x=(rect[0]+rect[2])//2;y=(rect[1]+rect[3])//2
                    d.text((x,y-8),name,font=self.font['medium'],fill=(235,250,255),anchor='ma')
                    return im
                c=self.wait_contact(dr);s=median_sample(c['samples'])
                hit=rect[0]<=s['x']<=rect[2] and rect[1]<=s['y']<=rect[3]
                self.data['targets'].append({'kind':'nav','target_rect':rect,'name':name,'attempt':n,'hit':hit,'sample':s})
        self.gesture_prompts(stylus=False)
        for n in range(1,4):
            def dr(n=n):
                im,d=self.draw_base('LONG PRESS',f'Press and hold the center target until it completes.',f'{n}/3')
                d.ellipse((205,125,275,195),outline=(255,230,60),width=3)
                d.text((240,214),'HOLD',font=self.font['medium'],fill=(230,250,255),anchor='ma')
                return im
            c=self.wait_contact(dr); self.data['gestures'].append(gesture_record('LONG_PRESS',c))
    def gesture_prompts(self,stylus=False):
        seq=['LEFT','RIGHT','LEFT','RIGHT','UP','DOWN','UP','DOWN']
        for idx,name in enumerate(seq,1):
            def dr(name=name,idx=idx):
                im,d=self.draw_base('GESTURE PATHS',f"{'Stylus' if stylus else 'Finger'}: swipe {name.lower()} naturally.",f'{idx}/{len(seq)}')
                if name=='LEFT':a,b=(410,160),(70,160)
                elif name=='RIGHT':a,b=(70,160),(410,160)
                elif name=='UP':a,b=(240,270),(240,70)
                else:a,b=(240,70),(240,270)
                d.line((*a,*b),fill=(75,235,255),width=4)
                d.polygon(arrow_head(a,b),fill=(255,230,60))
                return im
            c=self.wait_contact(dr,min_samples=3)
            self.data['gestures'].append(gesture_record(name,c))
    def analyze(self):
        contacts=self.data['contacts']
        pressures=[s['pressure'] for c in contacts for s in c['samples'] if s.get('pressure') is not None]
        target_errors=[t['error_px'] for t in self.data['targets'] if 'error_px' in t]
        jitter=[]
        for c in contacts:
            pts=[(s['x'],s['y']) for s in c['samples']]
            if pts:
                mx=statistics.median([p[0] for p in pts]);my=statistics.median([p[1] for p in pts])
                jitter.append(max(math.hypot(p[0]-mx,p[1]-my) for p in pts))
        out={'mode':self.mode,'contacts':len(contacts),'pressure':stat(pressures),'mapped_target_error_px':stat(target_errors),
             'contact_jitter_radius_px':stat(jitter),'capabilities':self.cap}
        if self.mode=='stylus':
            samples=[]
            for t in self.data['targets']:
                if t.get('kind')=='stylus' and t.get('attempt')==1:
                    s=t['sample'];samples.append((s['raw_x'],s['raw_y'],t['target'][0],t['target'][1]))
            if len(samples)>=6:
                out['calibration_candidates']=calibration_candidates(samples)
        if self.mode=='finger':
            sizes=defaultdict(lambda:{'attempts':0,'first_hits':0,'eventual_hits':0,'targets':0})
            grouped=defaultdict(list)
            for t in self.data['targets']:
                if t.get('kind')!='finger':continue
                grouped[tuple(t['target'])].append(t)
            for tg,arr in grouped.items():
                size=arr[0]['size'];r=sizes[size];r['targets']+=1;r['attempts']+=len(arr)
                if arr[0]['hit']:r['first_hits']+=1
                if any(a['hit'] for a in arr):r['eventual_hits']+=1
            out['finger_target_sizes']={str(k):v for k,v in sorted(sizes.items())}
        return out
    def summary_md(self,s):
        lines=['# Beastagotchi Touch Lab Session','',f"Mode: **{s['mode']}**",f"Contacts recorded: **{s['contacts']}**",'',
               f"Contact model: **{s['capabilities']['contact_model']}**",
               f"Pressure axis: **{s['capabilities']['has_pressure']}**",
               f"Multi-touch axes: **{s['capabilities']['has_multitouch_axes']}**",'',
               '## Metrics','',f"Mapped target error: `{s['mapped_target_error_px']}`",
               f"Contact jitter radius: `{s['contact_jitter_radius_px']}`",f"Pressure: `{s['pressure']}`"]
        if 'finger_target_sizes' in s:
            lines += ['','## Finger target sizes','', '```json',json.dumps(s['finger_target_sizes'],indent=2),'```']
        if 'calibration_candidates' in s:
            lines += ['','## Calibration candidates','', '```json',json.dumps(s['calibration_candidates'],indent=2),'```',
                      '', '> Candidates are diagnostic only. Touch Lab never changes the active calibration automatically.']
        return '\n'.join(lines)+'\n'
    def done_screen(self,summary):
        start=time.monotonic()
        while time.monotonic()-start<8:
            im,d=self.draw_base('PASS COMPLETE','Results saved. Beast UI will return automatically.')
            d.text((20,125),f"Contacts: {summary['contacts']}",font=self.font['medium'],fill=(175,235,195))
            e=summary['mapped_target_error_px']
            if e.get('median') is not None:d.text((20,160),f"Median target error: {e['median']:.1f}px",font=self.font['medium'],fill=(175,235,195))
            p=summary['pressure']
            if p.get('median') is not None:d.text((20,195),f"Median pressure value: {p['median']:.0f}",font=self.font['medium'],fill=(175,235,195))
            d.text((20,250),str(self.dir),font=self.font['tiny'],fill=(130,180,190))
            self.write(im);time.sleep(.15)


def arrow_head(a,b):
    ax,ay=a;bx,by=b;ang=math.atan2(by-ay,bx-ax);r=14
    return [(bx,by),(bx+r*math.cos(ang+2.55),by+r*math.sin(ang+2.55)),(bx+r*math.cos(ang-2.55),by+r*math.sin(ang-2.55))]


def median_sample(samples):
    if not samples:return {'x':0,'y':0,'raw_x':0,'raw_y':0,'pressure':0}
    keys=['x','y','raw_x','raw_y','pressure'];out={}
    for k in keys:
        vals=[s[k] for s in samples if s.get(k) is not None]
        out[k]=int(round(statistics.median(vals))) if vals else 0
    return out


def stat(vals):
    vals=[float(v) for v in vals if v is not None]
    if not vals:return {'count':0,'min':None,'median':None,'mean':None,'p95':None,'max':None}
    vals=sorted(vals);n=len(vals)
    def pct(q):return vals[min(n-1,max(0,int(math.ceil(q*n))-1))]
    return {'count':n,'min':vals[0],'median':statistics.median(vals),'mean':statistics.mean(vals),'p95':pct(.95),'max':vals[-1]}


def gesture_record(expected,c):
    pts=[(s['x'],s['y']) for s in c['samples']]
    dur=max(0.001,c['samples'][-1]['t']-c['samples'][0]['t']) if len(c['samples'])>1 else 0.001
    kind,payload=classify_gesture(pts,dur)
    return {'expected':expected,'classified':kind,'payload':payload,'duration':dur,'samples':len(pts),'contact':c}


def solve_linear(A,b):
    n=len(b);M=[list(map(float,A[i]))+[float(b[i])] for i in range(n)]
    for col in range(n):
        pivot=max(range(col,n),key=lambda r:abs(M[r][col]))
        if abs(M[pivot][col])<1e-12:raise ValueError('singular matrix')
        M[col],M[pivot]=M[pivot],M[col]
        p=M[col][col];M[col]=[x/p for x in M[col]]
        for r in range(n):
            if r==col:continue
            f=M[r][col]
            if f:M[r]=[M[r][c]-f*M[col][c] for c in range(n+1)]
    return [M[i][-1] for i in range(n)]


def least_squares(features, targets):
    m=len(features[0]);ata=[[0.0]*m for _ in range(m)];atb=[0.0]*m
    for row,y in zip(features,targets):
        for i in range(m):
            atb[i]+=row[i]*y
            for j in range(m):ata[i][j]+=row[i]*row[j]
    return solve_linear(ata,atb)


def calibration_candidates(samples):
    rx=[s[0] for s in samples];ry=[s[1] for s in samples];sx=[s[2] for s in samples];sy=[s[3] for s in samples]
    fa=[[x,y,1.0] for x,y in zip(rx,ry)]
    fq=[[x,y,x*y,x*x,y*y,1.0] for x,y in zip(rx,ry)]
    ax=least_squares(fa,sx);ay=least_squares(fa,sy)
    qx=least_squares(fq,sx);qy=least_squares(fq,sy)
    def metrics(cx,cy,features):
        errs=[]
        for row,tx,ty in zip(features,sx,sy):
            px=sum(c*v for c,v in zip(cx,row));py=sum(c*v for c,v in zip(cy,row));errs.append(math.hypot(px-tx,py-ty))
        return stat(errs)
    return {
        'affine':{'x':ax,'y':ay,'residual_px':metrics(ax,ay,fa)},
        'quadratic':{'x':qx,'y':qy,'basis':['raw_x','raw_y','raw_x*raw_y','raw_x^2','raw_y^2','1'],
                     'residual_px':metrics(qx,qy,fq)},
    }


def ensure_root():
    if os.geteuid()!=0:
        raise SystemExit('Run physical Touch Lab passes with sudo.')


def run_pass(mode):
    ensure_root()
    # Never steal the LCD from Pwnagotchi. Touch Lab only operates inside an active/confirmed Beast display handoff.
    check=subprocess.run(['/opt/beast-ui/bin/display_config.py','--config','/etc/pwnagotchi/config.toml','require-disabled'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if check.returncode!=0:
        raise SystemExit('Pwnagotchi display is enabled. Start a Beast physical handoff first: sudo /opt/beast-ui/bin/claim_display_test.sh 45')
    was_active=subprocess.run(['systemctl','is-active','--quiet','beast-ui.service']).returncode==0
    if was_active:subprocess.run(['systemctl','stop','beast-ui.service'],check=True)
    try:
        TouchLab(mode).run()
    finally:
        if was_active:subprocess.run(['systemctl','start','beast-ui.service'])


def latest_dirs():
    if not DATA_ROOT.exists():return []
    return sorted([p for p in DATA_ROOT.iterdir() if p.is_dir()],key=lambda p:p.stat().st_mtime)


def bundle():
    ensure_root();DATA_ROOT.mkdir(parents=True,exist_ok=True)
    out=Path('/home/pi/beast-touchlab-validation.tar.gz')
    cap=capabilities();(DATA_ROOT/'capabilities-latest.json').write_text(json.dumps(cap,indent=2))
    with tarfile.open(out,'w:gz') as tf:
        tf.add(DATA_ROOT,arcname='touchlab')
        if TOUCH_CONFIG.exists():tf.add(TOUCH_CONFIG,arcname='system/touch.json')
        if Path('/proc/bus/input/devices').exists():
            tmp=DATA_ROOT/'input_devices-latest.txt';tmp.write_text(Path('/proc/bus/input/devices').read_text(errors='ignore'));tf.add(tmp,arcname='system/input_devices.txt')
        log=Path('/run/beastagotchi/touch-gestures.jsonl')
        if log.exists():tf.add(log,arcname='system/beast-ui-touch-gestures.jsonl')
    shutil.chown(out,user='pi',group='pi');os.chmod(out,0o644)
    print(out)


def show_caps():
    print(json.dumps(capabilities(),indent=2))


def main():
    ap=argparse.ArgumentParser(description='Beastagotchi physical touchscreen characterization lab')
    ap.add_argument('command',choices=['capabilities','stylus','finger','bundle'])
    a=ap.parse_args()
    if a.command=='capabilities':show_caps()
    elif a.command in ('stylus','finger'):run_pass(a.command)
    else:bundle()

if __name__=='__main__':main()
