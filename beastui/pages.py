from __future__ import annotations

import math
from .design import PRIMARY_PAGES
from .customization import dashboard_widget_box
from .components import card, label_value, progress_bar, divider, status_badge, section_title
from .widgets import (
    panel, metric, channel_bars, line_area, multiline, bars, stacked_bars, histogram,
    waveform, waterfall, radial, donut, radar, polar, signal_meter, heatmap, timeline, microtrend,
)


class Pages:
    IDS=list(PRIMARY_PAGES)
    TITLES={'home':'BEAST CORE','overview':'OVERVIEW','dashboard':'DASHBOARD','recon':'RECON','networks':'NETWORKS','spectrum':'SPECTRUM','captures':'CAPTURE VAULT','map':'FIELD MAP','expedition':'EXPEDITION','beast':'BEAST','system':'SYSTEM'}
    def __init__(self,face):self.face=face
    @staticmethod
    def _v(state,key,default='--'):
        v=state.get(key,default);return default if v is None else v
    @staticmethod
    def _pct(state,key):
        v=state.get(key);return float(v) if isinstance(v,(int,float)) else 0.0

    @staticmethod
    def _channel_counts(aps):
        counts={}
        for ap in aps or []:
            if not isinstance(ap,dict):continue
            ch=ap.get('channel')
            if isinstance(ch,(int,float)):
                ch=int(ch);counts[ch]=counts.get(ch,0)+1
        return counts

    @staticmethod
    def _channel_angle(channel):
        """Map the real Wi-Fi channel to a categorical polar angle.

        This is *not* direction finding. 2.4 GHz occupies the lower arc and
        5 GHz the upper arc so angular position always means channel/band.
        """
        try: ch=int(channel)
        except Exception:return None
        if 1 <= ch <= 14:
            return 205.0 + (ch-1) * (130.0/13.0)
        if 32 <= ch <= 177:
            return 25.0 + (ch-32) * (145.0/145.0)
        return float((ch * 2) % 360)

    @staticmethod
    def _channel_history_matrix(history, metric='ap_count'):
        rows=[x for x in (history or []) if isinstance(x,dict) and isinstance(x.get('channels'),list)]
        if not rows:return [],[]
        channels=sorted({int(c.get('channel')) for r in rows for c in r.get('channels',[]) if isinstance(c,dict) and isinstance(c.get('channel'),(int,float))})
        if not channels:return [],[]
        matrix=[]
        for r in rows:
            by={int(c.get('channel')):c for c in r.get('channels',[]) if isinstance(c,dict) and isinstance(c.get('channel'),(int,float))}
            vals=[]
            for ch in channels:
                v=by.get(ch,{}).get(metric,0)
                try:vals.append(float(v or 0))
                except Exception:vals.append(0.0)
            matrix.append(vals)
        return channels,matrix

    @staticmethod
    def _route_points(expedition):
        out=[]
        if not isinstance(expedition,dict):return out
        for row in expedition.get('points') or []:
            if not isinstance(row,dict):continue
            try:lat=float(row.get('latitude'));lon=float(row.get('longitude'))
            except Exception:continue
            if math.isfinite(lat) and math.isfinite(lon):out.append((lat,lon,row))
        return out

    def overview(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        cards=[x for x in (state.get('overview.cards') or []) if isinstance(x,dict)]
        attention=[x for x in (state.get('overview.attention') or []) if isinstance(x,dict)]
        overall=str(state.get('overview.state') or 'starting').upper()
        col=t.c('danger') if overall=='CRITICAL' else t.c('warn') if overall=='ATTENTION' else t.c('accent')
        d.text((14,42),'WHOLE-DEVICE OVERVIEW',font=f['medium'],fill=col)
        d.text((352,45),overall,font=f['small'],fill=col)
        boxes=[(8,64,160,121),(164,64,316,121),(320,64,472,121),(8,127,160,184),(164,127,316,184),(320,127,472,184)]
        for row,box in zip(cards[:6],boxes):
            status=str(row.get('status') or 'ok').lower();edge=t.c('danger') if status in {'critical','error'} else t.c('warn') if status in {'warning','degraded','attention'} else t.c('info') if status=='info' else t.c('edge')
            panel(d,box,t,accent=edge,width=2 if status in {'critical','error','warning'} else 1)
            x1,y1,x2,y2=box;d.text((x1+8,y1+6),str(row.get('title') or '--')[:16],font=f['tiny'],fill=t.c('dim'))
            d.text((x1+8,y1+22),str(row.get('value') or '--')[:17],font=f['medium'],fill=edge if status!='ok' else t.c('text'))
            d.text((x1+8,y1+41),str(row.get('detail') or '')[:24],font=f['micro'],fill=t.c('dim'))
        panel(d,(8,191,472,267),t,accent=col)
        if attention:
            first=attention[0];d.text((18,201),f"ATTENTION {len(attention)}",font=f['small'],fill=col)
            d.text((18,222),str(first.get('title') or 'Attention')[:42],font=f['small'],fill=t.c('text'))
            d.text((18,242),str(first.get('detail') or '')[:64],font=f['tiny'],fill=t.c('dim'))
        else:
            d.text((18,204),'NO ACTIVE ATTENTION ITEMS',font=f['small'],fill=t.c('accent'))
            d.text((18,229),'PWNAGOTCHI / BETTERCAP / STORAGE / CORE NOMINAL',font=f['tiny'],fill=t.c('dim'))

    def home(self,d,state,ui):
        t=ui.theme;f=ui.fonts;tid=t.id
        if tid in {'pwn_dark','pwn_light','pwn_chroma'}:
            # Preserve the iconic Pwnagotchi visual grammar on the Home page:
            # sparse monochrome/Chroma surface, giant stock text face, small
            # status fields, and a simple conversational status line. Beast
            # navigation remains available in the footer so the classic look
            # is a first-class theme rather than a separate compatibility app.
            bg=t.c('bg'); text=t.c('text'); dim=t.c('dim'); accent=t.c('accent')
            d.rectangle((0,34,480,278),fill=bg)
            d.text((12,45),f"CH {self._v(state,'radio.primary.channel','--')}",font=f['body'],fill=text)
            d.text((88,45),f"APS {self._v(state,'wifi.ap_count',0)}",font=f['body'],fill=text)
            d.text((180,45),f"STA {self._v(state,'wifi.client_count',0)}",font=f['body'],fill=text)
            d.text((280,45),f"HS {self._v(state,'pwnagotchi.handshakes',0)}",font=f['body'],fill=text)
            temp=state.get('system.temp.cpu_c')
            d.text((382,45),f"{temp:.0f}C" if isinstance(temp,(int,float)) else 'TEMP --',font=f['body'],fill=text)
            self.face.draw(d,(92,72,388,172),t,state,ui.phase)
            mood=str(self._v(state,'pwnagotchi.mood','awake')).upper()
            mode=str(self._v(state,'context.mode.effective','pwn')).upper()
            status=f'{mood} // {mode}'
            d.text((18,186),status,font=f['medium'],fill=accent if tid=='pwn_chroma' else text)
            d.line((18,207,462,207),fill=t.c('edge'))
            gps='GPS LOCK' if state.get('gps.fix') else 'GPS --'
            health=str(self._v(state,'health.core.state','starting')).upper()
            level=int(self._v(state,'progression.level',1))
            stage=str(self._v(state,'progression.stage','Hatchling')).upper()
            d.text((18,218),f'{gps}   CORE {health}',font=f['small'],fill=text)
            d.text((18,239),f'LVL {level:02d} {stage[:14]}',font=f['small'],fill=text)
            d.text((282,239),f"LIFE AP {self._v(state,'wifi.encounters.lifetime_unique',0)}",font=f['small'],fill=dim)
            return
        if tid=='minimal':
            self.face.draw(d,(18,52,228,248),t,state,ui.phase)
            radial(d,(250,48,352,145),self._pct(state,'system.cpu.total'),t,t.c('primary'),font=f['small'])
            radial(d,(362,48,464,145),self._pct(state,'system.memory.used_pct'),t,t.c('secondary'),font=f['small'])
            d.text((271,129),'CPU',font=f['tiny'],fill=t.c('dim'));d.text((387,129),'RAM',font=f['tiny'],fill=t.c('dim'))
            panel(d,(250,156,464,248),t);mode=str(self._v(state,'context.mode.effective','pwn')).upper();d.text((264,168),mode,font=f['large'],fill=t.c('accent'))
            d.text((264,195),f"AP {self._v(state,'wifi.ap_count',0)}   CH {self._v(state,'radio.primary.channel')}",font=f['small'],fill=t.c('text'))
            if state.get('power.telemetry.available'):
                d.text((264,216),f"BAT {self._v(state,'power.battery.percent_estimate',0):.0f}%",font=f['small'],fill=t.c('info'))
            return
        if tid=='starcore':
            # Starship-console composition: vertical status rail + center creature + right instruments.
            panel(d,(8,43,72,268),t,accent=t.c('secondary'));labels=[('AP',self._v(state,'wifi.ap_count',0)),('CH',self._v(state,'radio.primary.channel')),('GPS','Y' if state.get('gps.fix') else 'N'),('DOCK','Y' if state.get('dock.docked') else 'N')]
            for i,(k,v) in enumerate(labels):d.text((18,58+i*47),k,font=f['tiny'],fill=t.c('ink'));d.text((18,72+i*47),str(v),font=f['medium'],fill=t.c('ink'))
            self.face.draw(d,(82,48,286,230),t,state,ui.phase)
            metric(d,(300,48,466,96),'MODE',str(self._v(state,'context.mode.effective','pwn')).upper(),f,t,t.c('primary'))
            radial(d,(300,104,380,184),self._pct(state,'system.cpu.total'),t,t.c('info'),font=f['tiny']);radial(d,(386,104,466,184),self._pct(state,'system.memory.used_pct'),t,t.c('secondary'),font=f['tiny'])
            panel(d,(300,192,466,262),t);d.text((312,204),'SYSTEMS NOMINAL' if state.get('health.core.state')=='healthy' else 'CHECK SYSTEM',font=f['small'],fill=t.c('accent'))
            d.text((312,225),f"{self._v(state,'system.temp.cpu_c',0):.0f}C   {self._v(state,'pwnagotchi.handshakes',0)} HS",font=f['small'],fill=t.c('text'))
            return
        if tid=='matrix':
            panel(d,(8,43,214,267),t);self.face.draw(d,(18,54,204,201),t,state,ui.phase)
            d.text((20,211),'> MODE '+str(self._v(state,'context.mode.effective','pwn')).upper(),font=f['small'],fill=t.c('primary'));d.text((20,229),'> APS '+str(self._v(state,'wifi.ap_count',0)),font=f['small'],fill=t.c('primary'));d.text((20,247),f"> LVL {self._v(state,'progression.level',1):02d} {str(self._v(state,'progression.stage','Hatchling')).upper()}",font=f['tiny'],fill=t.c('dim'))
            panel(d,(224,43,472,267),t)
            rows=[('CHANNEL',self._v(state,'radio.primary.channel')),('CLIENTS',self._v(state,'wifi.client_count',0)),('TEMP',f"{self._v(state,'system.temp.cpu_c',0):.0f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--'),('CPU',f"{self._v(state,'system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--'),('RAM',f"{self._v(state,'system.memory.used_pct',0):.0f}%" if isinstance(state.get('system.memory.used_pct'),(int,float)) else '--'),('HANDSHAKES',self._v(state,'pwnagotchi.handshakes',0)),('DOCK',str(self._v(state,'dock.state','field')).upper())]
            for i,(k,v) in enumerate(rows):d.text((238,55+i*28),k,font=f['tiny'],fill=t.c('dim'));d.text((358,55+i*28),str(v),font=f['small'],fill=t.c('accent'))
            return
        # v0.19 reference Home: the Beast is the primary object; operational
        # telemetry is summarized around it rather than competing with it.
        health=str(self._v(state,'health.core.state','starting')).upper()
        mood=str(self._v(state,'pwnagotchi.mood','awake')).upper()
        dock=str(self._v(state,'dock.state','field')).upper()
        lvl=int(self._v(state,'progression.level',1))
        stage=str(self._v(state,'progression.stage','Hatchling')).upper()
        aura=str(self._v(state,'progression.aura','none')).upper()
        try:growth=max(0.0,min(100.0,float(self._v(state,'progression.level_progress_pct',0))))
        except Exception:growth=0.0
        expression=str(self._v(state,'beast.expression',mood)).replace('_',' ').upper()
        mode=str(self._v(state,'context.mode.effective','pwn')).upper()

        # Identity card: creature, expression and progression are the visual
        # anchor. This is deliberately not another telemetry dashboard.
        card(d,(8,43,228,216),t,accent=t.c('primary'),width=2)
        self.face.draw(d,(20,52,216,163),t,state,ui.phase)
        section_title(d,(18,168),expression[:20],f,t,color=t.c('accent'))
        d.text((18,183),f'LV {lvl:02d}',font=f['medium'],fill=t.c('primary'))
        d.text((72,186),stage[:16],font=f['tiny'],fill=t.c('text'))
        d.text((18,201),f'GROWTH {growth:3.0f}%',font=f['micro'],fill=t.c('dim'))
        progress_bar(d,(88,203,216,209),growth,t,color=t.c('accent'))

        # Operational card: one strong mode/status area, then compact supporting
        # facts. This avoids the old equal-weight "box wall" treatment.
        card(d,(238,43,472,216),t,accent=t.c('edge'))
        section_title(d,(250,53),'MODE',f,t)
        d.text((250,64),mode[:18],font=f['large'],fill=t.c('secondary'))
        status_col=t.c('accent') if health=='HEALTHY' else t.c('warn')
        badge=status_badge(d,(250,86),f'CORE {health}',f,t,color=status_col)
        if dock!='FIELD':
            status_badge(d,(258+badge,86),dock,f,t,color=t.c('info'))
        divider(d,250,111,460,t)

        stats=[
            ('APS',self._v(state,'wifi.ap_count',0),t.c('primary')),
            ('CH',self._v(state,'radio.primary.channel'),t.c('info')),
            ('HS',self._v(state,'pwnagotchi.handshakes',0),t.c('accent')),
            ('CPU',f"{self._v(state,'system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--',t.c('text')),
            ('TEMP',f"{self._v(state,'system.temp.cpu_c',0):.0f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--',t.c('text')),
            ('GPS','LOCK' if state.get('gps.fix') else '--',t.c('accent') if state.get('gps.fix') else t.c('dim')),
        ]
        for i,(label,value,col) in enumerate(stats):
            cx=250+(i%3)*70;cy=121+(i//3)*42
            label_value(d,(cx,cy),label,value,f,t,color=col,max_chars=8)
        d.text((250,198),f'AURA {aura[:10]}',font=f['tiny'],fill=t.c('dim'))

        # Calm exploration/context strip. It carries persistent meaning without
        # pushing the Beast off the page or recreating a dense dashboard.
        card(d,(8,224,472,268),t)
        session=self._v(state,'wifi.encounters.session_unique',0)
        life=self._v(state,'wifi.encounters.lifetime_unique',0)
        label_value(d,(18,232),'SESSION',f'{session} SIGNALS',f,t,color=t.c('text'),value_font='small',max_chars=18)
        label_value(d,(205,232),'LIFETIME',f'{life} DISCOVERIES',f,t,color=t.c('info'),value_font='small',max_chars=18)
        if state.get('power.telemetry.available'):
            pct=state.get('power.battery.percent_estimate')
            power=f'BAT {pct:.0f}%' if isinstance(pct,(int,float)) else 'BAT --'
        else:
            power='DOCKED' if state.get('dock.docked') else 'FIELD'
        label_value(d,(397,232),'STATE',power,f,t,color=t.c('accent'),value_font='tiny',max_chars=10)

    @staticmethod
    def _dashboard_value(key,value):
        if value is None:return '--'
        try:
            if key=='expedition.distance_m':return f"{float(value)/1609.344:.2f} mi"
            if key.endswith('_bytes') or key.endswith('.bytes'):
                v=float(value)
                for unit in ('B','KB','MB','GB','TB'):
                    if abs(v)<1024 or unit=='TB':return f"{v:.1f}{unit}" if unit!='B' else f"{v:.0f}B"
                    v/=1024.0
            if key.endswith('_sec') or key.endswith('.uptime_sec'):
                sec=max(0,int(float(value)));h=sec//3600;m=(sec%3600)//60
                return f"{h}h {m}m" if h else f"{m}m"
            if key.endswith('_pct') or 'percent' in key:return f"{float(value):.0f}%"
            if key.endswith('_c') or '.temp.' in key:return f"{float(value):.1f}C"
            if key.endswith('_w'):return f"{float(value):.1f}W"
            if key.endswith('_mph'):return f"{float(value):.1f} mph"
            if isinstance(value,float):return f"{value:.1f}"
        except Exception:pass
        return str(value)[:16]

    def dashboard(self,d,state,ui):
        """User-composed live instruments configured by Beast Studio.

        Geometry is stored on a 12x8 logical grid so the web composer and the
        physical 480x320 compositor share exactly the same layout model. Every
        value remains canonical Beast state; unavailable sources remain '--'.
        """
        t=ui.theme;f=ui.fonts
        widgets=[w for w in ui._active_dashboard_widgets() if isinstance(w,dict) and bool(w.get('visible',True))]
        widgets.sort(key=lambda w:(int(w.get('z',0)), str(w.get('id') or '')))
        for idx,row in enumerate(widgets):
            if not isinstance(row,dict):continue
            box=dashboard_widget_box(row);x1,y1,x2,y2=box
            key=str(row.get('key') or '');label=str(row.get('label') or key.split('.')[-1] or 'DATA').upper()[:18]
            style=str(row.get('style') or 'metric');value=state.get(key) if key else None;hist=ui.histories.get(key) or []
            accent=[t.c('primary'),t.c('info'),t.c('accent'),t.c('secondary'),t.c('warn'),t.c('primary')][idx%6]
            try:lo=float(row.get('min',0));hi=float(row.get('max',100))
            except Exception:lo,hi=0.0,100.0
            # Tiny custom tiles degrade to a metric rather than crushing a
            # complex renderer into unreadable geometry. Data is unchanged.
            bw,bh=x2-x1,y2-y1
            use_style=style if bw>=92 and bh>=52 else 'metric'
            if use_style=='radial' and isinstance(value,(int,float)):
                radial(d,box,value,t,accent,minimum=lo,maximum=hi,label=label,font=f['tiny'])
            elif use_style=='bar' and isinstance(value,(int,float)):
                panel(d,box,t);d.text((x1+7,y1+6),label,font=f['tiny'],fill=t.c('dim'));txt=self._dashboard_value(key,value);d.text((x1+7,y1+22),txt,font=f['medium'] if bh>=56 else f['small'],fill=accent);p=max(0,min(1,(float(value)-lo)/max(1e-9,hi-lo)));bar_y=max(y1+34,y2-13);d.rectangle((x1+7,bar_y,x2-7,min(y2-7,bar_y+6)),fill=t.c('edge'));d.rectangle((x1+7,bar_y,x1+7+int(max(1,x2-x1-14)*p),min(y2-7,bar_y+6)),fill=accent)
            elif use_style=='microtrend':
                microtrend(d,box,self._dashboard_value(key,value),hist,t,accent,font=f['tiny'],label=label)
            else:
                panel(d,box,t);d.text((x1+7,y1+6),label,font=f['tiny'],fill=t.c('dim'));d.text((x1+7,y1+22),self._dashboard_value(key,value),font=f['medium'] if bh>=52 else f['small'],fill=accent)
                if bh>=64 and bw>=112:d.text((x1+7,y2-13),key[:max(8,min(28,(bw-14)//5))],font=f['micro'],fill=t.c('dim'))
        board_label='DASHBOARD'
        if getattr(ui,'active_board_id',''):
            board_label=next((str(b.get('label') or b.get('id')) for b in getattr(ui,'custom_boards',[]) if str(b.get('id'))==ui.active_board_id),ui.active_board_id)
        d.text((12,269),f'{board_label.upper()[:18]} // LIVE CANONICAL TELEMETRY // long-press tile for source',font=f['micro'],fill=t.c('dim'))

    def recon(self,d,state,ui):
        t=ui.theme;f=ui.fonts;aps=state.get('wifi.aps') or [];mode=ui.renderer_for('recon')
        d.text((12,44),f'RECON // {mode.upper()} // LIVE BETTERCAP OBSERVATIONS',font=f['tiny'],fill=t.c('dim'))
        left=(8,58,252,268)
        rows=sorted([a for a in aps if isinstance(a,dict)],key=lambda a:a.get('rssi',-999),reverse=True)
        strengths=[]
        for ap in rows[:16]:
            try:strengths.append(max(0,min(100,100+float(ap.get('rssi',-100)))))
            except Exception:strengths.append(0)
        if mode=='radar':
            panel(d,left,t);cx,cy=130,164
            for r in (32,64,94):d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=t.c('edge'))
            d.line((cx-98,cy,cx+98,cy),fill=t.c('edge'));d.line((cx,cy-98,cx,cy+98),fill=t.c('edge'))
            # Sweep is decorative UI chrome only; plotted geometry is truthful:
            # radius = RSSI, angle = observed Wi-Fi channel (not bearing).
            sweep=(ui.phase*55)%360;ex=cx+int(math.cos(math.radians(sweep))*94);ey=cy+int(math.sin(math.radians(sweep))*94)
            d.line((cx,cy,ex,ey),fill=t.c('grid'),width=1)
            for i,ap in enumerate(rows[:18]):
                try:rssi=float(ap.get('rssi',-100))
                except Exception:rssi=-100
                a=self._channel_angle(ap.get('channel'))
                if a is None:continue
                strength=max(0.0,min(1.0,(rssi+100.0)/70.0));rr=max(10,int(94*(1.0-strength)))
                x=cx+int(math.cos(math.radians(a))*rr);y=cy+int(math.sin(math.radians(a))*rr)
                d.ellipse((x-3,y-3,x+3,y+3),fill=t.c('accent') if i==0 else t.c('primary'))
            d.text((18,247),'R=RSSI  ANGLE=CHANNEL',font=f['tiny'],fill=t.c('dim'))
        elif mode=='polar':polar(d,left,strengths[:12],t,t.c('accent'))
        elif mode=='bars':bars(d,left,strengths[:16],t,t.c('primary'))
        elif mode=='signal':signal_meter(d,left,max(strengths or [0]),t,t.c('accent'))
        else:radar(d,left,strengths[:8] or [0,0,0],list(range(8)),t,t.c('accent'))
        panel(d,(260,58,472,268),t);d.text((270,66),'STRONGEST / RECENT',font=f['tiny'],fill=t.c('dim'))
        for i,ap in enumerate(rows[:7]):
            y=84+i*25;ssid=str(ap.get('hostname') or ap.get('ssid') or '<hidden>')[:17];ch=ap.get('channel','--');rssi=ap.get('rssi','--')
            d.text((270,y),ssid,font=f['small'],fill=t.c('text'));d.text((400,y),f'{ch}/{rssi}',font=f['tiny'],fill=t.c('accent'))

    def networks(self,d,state,ui):
        t=ui.theme;f=ui.fonts;aps=state.get('wifi.aps') or [];panel(d,(8,42,472,268),t);headers=[('SSID',16),('CH',280),('RSSI',323),('SEC',375)]
        for lab,x in headers:d.text((x,49),lab,font=f['tiny'],fill=t.c('dim'))
        rows=sorted([a for a in aps if isinstance(a,dict)],key=lambda a:a.get('rssi',-999),reverse=True)[:9]
        for i,ap in enumerate(rows):
            y=66+i*21
            if i%2==0:d.rectangle((12,y-2,468,y+17),fill=t.c('panel2'))
            d.text((16,y),str(ap.get('hostname') or '<hidden>')[:29],font=f['small'],fill=t.c('text'));d.text((282,y),str(ap.get('channel','--')),font=f['small'],fill=t.c('info'));d.text((325,y),str(ap.get('rssi','--')),font=f['small'],fill=t.c('accent'));d.text((375,y),str(ap.get('encryption') or 'OPEN')[:12],font=f['tiny'],fill=t.c('primary'))

    def spectrum(self,d,state,ui):
        t=ui.theme;f=ui.fonts;aps=state.get('wifi.aps') or [];mode=ui.renderer_for('spectrum');counts=self._channel_counts(aps);channels=sorted(counts);vals=[counts[ch] for ch in channels]
        d.text((12,44),f'OBSERVED WI-FI CHANNEL ACTIVITY // {mode.upper()}',font=f['tiny'],fill=t.c('dim'))
        box=(8,60,472,185)
        channel_hist=ui.aux.get('channel_history') if isinstance(getattr(ui,'aux',None),dict) else []
        hist_channels,matrix=self._channel_history_matrix(channel_hist,'ap_count')
        if mode=='bars':channel_bars(d,box,aps,t)
        elif mode=='line':line_area(d,box,vals,t,t.c('accent'),fill_area=False)
        elif mode=='area':line_area(d,box,vals,t,t.c('accent'),fill_area=True)
        elif mode in {'heatmap','waterfall'}:
            if matrix:
                # Every cell is a real successive per-channel Bettercap sample.
                shown=matrix[-18:] if mode=='heatmap' else matrix[-28:]
                heatmap(d,box,shown,t,t.c('accent') if mode=='waterfall' else t.c('primary'))
                if hist_channels:
                    d.text((14,171),f'CH {hist_channels[0]}',font=f['tiny'],fill=t.c('dim'))
                    d.text((423,171),f'{hist_channels[-1]}',font=f['tiny'],fill=t.c('dim'))
            else:
                panel(d,box,t);d.text((120,115),'COLLECTING REAL CHANNEL HISTORY...',font=f['small'],fill=t.c('dim'))
        elif mode=='radar':
            top=sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))[:8];radar(d,box,[v for _,v in top],[str(ch) for ch,_ in top],t,t.c('accent'))
        elif mode=='polar':polar(d,box,vals,t,t.c('accent'))
        elif mode=='histogram':histogram(d,box,vals,t,t.c('primary'),bins=10)
        elif mode=='donut':donut(d,box,vals,t,[t.c('primary'),t.c('accent'),t.c('secondary'),t.c('info')],center_text=sum(vals),font=f['small'])
        elif mode=='waveform':waveform(d,box,vals,t,t.c('accent'))
        else:channel_bars(d,box,aps,t)
        hist=ui.histories.get('wifi.ap_count') or []
        microtrend(d,(8,194,238,264),self._v(state,'wifi.ap_count',0),hist,t,t.c('accent'),font=f['small'],label='TOTAL OBSERVED AP TREND')
        metric(d,(246,194,356,264),'Current',self._v(state,'radio.primary.channel'),f,t,t.c('accent'));metric(d,(364,194,472,264),'Band',self._v(state,'radio.primary.band'),f,t)
        d.text((270,254),'NOT RAW RF POWER',font=f['tiny'],fill=t.c('dim'))

    def captures(self,d,state,ui):
        t=ui.theme;f=ui.fonts;mode=ui.renderer_for('captures');total=self._v(state,'captures.total',self._v(state,'pwnagotchi.cache.handshake_ap_count',0));session=self._v(state,'pwnagotchi.handshakes',0);better=self._v(state,'wifi.handshake_ap_count',0)
        metric(d,(8,42,148,98),'Stored',total,f,t,t.c('primary'));metric(d,(156,42,306,98),'Session HS',session,f,t,t.c('accent'));metric(d,(314,42,472,98),'Bettercap',better,f,t)
        d.text((12,108),f'CAPTURE ANALYTICS // {mode.upper()} // TAP GRAPH TO CHANGE',font=f['tiny'],fill=t.c('dim'));box=(8,124,472,266);vals=[total,session,better]
        if mode=='bars':bars(d,box,vals,t,t.c('accent'))
        elif mode=='donut':donut(d,box,vals,t,[t.c('primary'),t.c('accent'),t.c('secondary')],center_text=total,font=f['small'])
        elif mode=='radial':
            panel(d,box,t);w=(472-8)//3
            for i,(v,lab,col) in enumerate(zip(vals,['STORED','SESSION','LIVE'],[t.c('primary'),t.c('accent'),t.c('secondary')])):
                radial(d,(12+i*w,132,8+(i+1)*w-4,258),v,t,col,minimum=0,maximum=max(1,max(vals)),label=lab,font=f['tiny'])
        elif mode=='timeline':timeline(d,box,ui.events,t,t.c('accent'))
        else:bars(d,box,vals,t,t.c('accent'))

    def map(self,d,state,ui):
        t=ui.theme;f=ui.fonts;mapbox=(8,42,342,268);panel(d,mapbox,t)
        for x in range(20,342,32):d.line((x,50,x,260),fill=t.c('grid'))
        for y in range(50,268,28):d.line((12,y,338,y),fill=t.c('grid'))
        expedition=ui.aux.get('expedition') if isinstance(getattr(ui,'aux',None),dict) else None
        pts=self._route_points(expedition)
        if pts:
            lats=[p[0] for p in pts];lons=[p[1] for p in pts];lat0,lat1=min(lats),max(lats);lon0,lon1=min(lons),max(lons)
            lat_span=max(1e-7,lat1-lat0);lon_span=max(1e-7,lon1-lon0);xa,ya,xb,yb=22,60,328,248
            xy=[]
            for lat,lon,_row in pts:
                x=xa+int((lon-lon0)/lon_span*(xb-xa));y=yb-int((lat-lat0)/lat_span*(yb-ya));xy.append((x,y))
            if len(xy)>=2:d.line(xy,fill=t.c('primary'),width=2)
            # Latest actual GPS point.
            x,y=xy[-1];d.ellipse((x-5,y-5,x+5,y+5),outline=t.c('accent'),fill=t.c('panel2'),width=2)
            d.text((16,247),'REAL EXPEDITION ROUTE // AUTO FIT',font=f['tiny'],fill=t.c('dim'))
        else:
            d.text((92,142),'NO GPS ROUTE DATA YET',font=f['small'],fill=t.c('dim'))
            d.text((74,160),'Route appears only from recorded fixes.',font=f['tiny'],fill=t.c('dim'))
        panel(d,(350,42,472,268),t);d.text((360,52),'GPS',font=f['tiny'],fill=t.c('dim'));d.text((360,67),'LOCK' if state.get('gps.fix') else 'NO FIX',font=f['medium'],fill=t.c('accent') if state.get('gps.fix') else t.c('warn'))
        d.text((360,100),f"SAT {self._v(state,'gps.satellites_used',0)}/{self._v(state,'gps.satellites_visible',0)}",font=f['small'],fill=t.c('text'));sp=state.get('context.motion.speed_mph');d.text((360,124),f'SPD {sp:.1f} mph' if isinstance(sp,(int,float)) else 'SPD --',font=f['small'],fill=t.c('text'));d.text((360,148),str(self._v(state,'context.mode.effective','pwn')).upper(),font=f['medium'],fill=t.c('primary'))
        dist=state.get('expedition.distance_m');dist_txt=f'{float(dist)/1609.344:.2f} mi' if isinstance(dist,(int,float)) else '--';d.text((360,182),'EXPEDITION',font=f['tiny'],fill=t.c('dim'));d.text((360,195),dist_txt,font=f['small'],fill=t.c('secondary'));d.text((360,216),f"AP {self._v(state,'expedition.ap_unique',0)}  PT {self._v(state,'expedition.route_points',0)}",font=f['tiny'],fill=t.c('text'))

    def expedition(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        active=bool(state.get('expedition.active'));eid=str(self._v(state,'expedition.id','--'))
        d.text((12,44),'FIELD SESSION RECORDER',font=f['tiny'],fill=t.c('dim'))
        panel(d,(8,58,472,111),t,accent=t.c('accent') if active else t.c('edge'))
        d.text((18,68),'ACTIVE' if active else 'IDLE',font=f['medium'],fill=t.c('accent') if active else t.c('dim'))
        d.text((102,69),eid[-20:],font=f['small'],fill=t.c('text'))
        dur=state.get('expedition.duration_sec');mins=int(float(dur or 0)//60);hrs=mins//60;mins%=60
        d.text((360,69),f'{hrs:02d}:{mins:02d}',font=f['medium'],fill=t.c('info'))
        dist=state.get('expedition.distance_m');dist_m=float(dist or 0) if isinstance(dist,(int,float)) else 0.0
        metric(d,(8,120,120,181),'Distance',f'{dist_m/1609.344:.2f}mi',f,t,t.c('primary'))
        metric(d,(126,120,238,181),'Route pts',self._v(state,'expedition.route_points',0),f,t,t.c('info'))
        metric(d,(244,120,356,181),'Unique AP',self._v(state,'expedition.ap_unique',0),f,t,t.c('accent'))
        metric(d,(362,120,472,181),'Captures',self._v(state,'expedition.captures_delta',0),f,t,t.c('secondary'))
        panel(d,(8,190,472,268),t)
        d.text((18,201),f"XP +{self._v(state,'expedition.xp_delta',0)}",font=f['small'],fill=t.c('accent'))
        mt=state.get('expedition.max_temp_c');mc=state.get('expedition.max_cpu_pct');mb=state.get('expedition.min_battery_pct')
        d.text((118,201),f"MAX T {mt:.1f}C" if isinstance(mt,(int,float)) else 'MAX T --',font=f['small'],fill=t.c('warn'))
        d.text((248,201),f"MAX CPU {mc:.0f}%" if isinstance(mc,(int,float)) else 'MAX CPU --',font=f['small'],fill=t.c('text'))
        d.text((382,201),f"MIN B {mb:.0f}%" if isinstance(mb,(int,float)) else 'MIN B --',font=f['small'],fill=t.c('info'))
        status='RECOVERED AFTER RESTART' if state.get('expedition.recovered') else 'LIVE CHECKPOINTING / CRASH RECOVERY ARMED'
        d.text((18,232),status,font=f['tiny'],fill=t.c('secondary'))
        d.text((18,249),'Route + AP details available through local expedition API.',font=f['tiny'],fill=t.c('dim'))

    def beast(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        # The physical 3.5-inch panel proved that v0.8 packed too much tiny
        # text into this page. Keep the Beast large, but give progression a
        # proper readable instrument panel with no text drawn inside bars.
        self.face.draw(d,(8,42,210,268),t,state,ui.phase);panel(d,(218,42,472,268),t)
        level=int(self._v(state,'progression.level',1));max_level=int(self._v(state,'progression.max_level',100));stage=str(self._v(state,'progression.stage','Hatchling')).upper();xp=int(self._v(state,'progression.xp',0));next_xp=int(self._v(state,'progression.xp_next_level',0));pct=self._pct(state,'progression.level_progress_pct');aura=str(self._v(state,'progression.aura','none')).upper()
        d.text((230,50),'BEAST DNA',font=f['small'],fill=t.c('dim'))
        d.text((230,65),f'LEVEL {level:02d} / {max_level}',font=f['large'],fill=t.c('primary'))
        d.text((230,88),'STAGE',font=f['tiny'],fill=t.c('dim'));d.text((270,85),stage,font=f['medium'] if len(stage)<=11 else f['small'],fill=t.c('text'))
        d.text((230,108),f'XP  {xp:,} / {next_xp:,}',font=f['body'],fill=t.c('text'))
        d.rectangle((230,124,460,137),outline=t.c('edge'),fill=t.c('panel2'));fill=230+int(230*max(0,min(100,pct))/100.0);d.rectangle((230,124,fill,137),fill=t.c('accent'))
        d.text((230,140),f'{pct:0.1f}% TO NEXT LEVEL',font=f['tiny'],fill=t.c('dim'))

        # Three large two-column status rows. Values use 11/13px fonts rather
        # than 6/7px micro text so every structural theme remains legible.
        rows=[
            ('MOOD',str(self._v(state,'pwnagotchi.mood','awake')).upper(),'MODE',str(self._v(state,'context.mode.effective','pwn')).upper()),
            ('AURA',aura,'VENDORS',str(self._v(state,'progression.vendors.count',0))),
            ('ACH',str(self._v(state,'progression.achievements.count',0)),'LIFE AP',str(self._v(state,'wifi.encounters.lifetime_unique',0))),
        ]
        y0=160
        for i,(la,va,lb,vb) in enumerate(rows):
            y=y0+i*32
            d.text((230,y),la,font=f['tiny'],fill=t.c('dim'));d.text((230,y+10),va[:14],font=f['body'],fill=t.c('accent') if i==0 else t.c('text'))
            d.text((350,y),lb,font=f['tiny'],fill=t.c('dim'));d.text((350,y+10),vb[:14],font=f['body'],fill=t.c('info') if i==0 else t.c('text'))


    def system(self,d,state,ui):
        t=ui.theme;f=ui.fonts;mode=ui.renderer_for('system')
        metric(d,(8,42,120,94),'Core',str(self._v(state,'health.core.state','--')).upper(),f,t,t.c('accent'));metric(d,(126,42,238,94),'Temp',f"{state.get('system.temp.cpu_c',0):.1f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--',f,t);metric(d,(244,42,356,94),'CPU',f"{state.get('system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--',f,t);metric(d,(362,42,472,94),'RAM',f"{state.get('system.memory.used_pct',0):.1f}%" if isinstance(state.get('system.memory.used_pct'),(int,float)) else '--',f,t)
        panel(d,(8,102,292,268),t);d.text((16,110),'HARDWARE / POWER',font=f['tiny'],fill=t.c('dim'));power='UPS '+str(self._v(state,'power.ups.state','--')).upper();d.text((16,130),power,font=f['small'],fill=t.c('accent') if state.get('power.telemetry.available') else t.c('dim'))
        if state.get('power.telemetry.available'):
            d.text((16,150),f"BAT {self._v(state,'power.battery.percent_estimate',0):.0f}%  {self._v(state,'power.battery.voltage_v',0):.2f}V",font=f['small'],fill=t.c('text'));d.text((16,169),f"{self._v(state,'power.power_w',0):.2f}W  {self._v(state,'power.current_ma',0):.0f}mA",font=f['small'],fill=t.c('text'))
        d.text((16,194),'DOCK '+str(self._v(state,'dock.state','field')).upper(),font=f['small'],fill=t.c('secondary'));d.text((16,213),'ETH '+('LINK' if state.get('network.ethernet.carrier') else 'DOWN'),font=f['small'],fill=t.c('text'))
        gov=str(self._v(state,'governor.mode','FULL')).upper();budget=self._v(state,'governor.budget_pct',100);gcol=t.c('danger') if gov=='SURVIVAL' else t.c('warn') if gov=='REDUCED' else t.c('accent') if gov=='GUARDED' else t.c('text');d.text((16,232),f'GOV {gov} {budget}%',font=f['small'],fill=gcol);d.text((170,232),f"CAPS {self._v(state,'capabilities.count',0)}  LIFE AP {self._v(state,'wifi.encounters.lifetime_unique',0)}",font=f['small'],fill=t.c('text'))
        cpu=ui.histories.get('system.cpu.total') or [];temp=ui.histories.get('system.temp.cpu_c') or []
        # CPU (%) and temperature (C) are intentionally independent scales.
        # They are never overlaid on one unlabeled axis.
        d.text((304,103),f'CPU % // {mode.upper()}',font=f['tiny'],fill=t.c('primary'));d.text((304,184),'TEMP C',font=f['tiny'],fill=t.c('warn'))
        top=(300,114,472,181);bottom=(300,195,472,268)
        if mode=='area':
            line_area(d,top,cpu,t,t.c('primary'),fill_area=True);line_area(d,bottom,temp,t,t.c('warn'),fill_area=True)
        elif mode=='waveform':
            waveform(d,top,cpu,t,t.c('primary'));waveform(d,bottom,temp,t,t.c('warn'))
        elif mode=='histogram':
            histogram(d,top,cpu,t,t.c('primary'));histogram(d,bottom,temp,t,t.c('warn'))
        elif mode=='waterfall':
            waterfall(d,top,cpu,t,t.c('primary'));waterfall(d,bottom,temp,t,t.c('warn'))
        else:
            line_area(d,top,cpu,t,t.c('primary'),fill_area=False);line_area(d,bottom,temp,t,t.c('warn'),fill_area=False)

