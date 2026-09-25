from __future__ import annotations

import math
from .design import PRIMARY_PAGES
from .customization import dashboard_widget_box
from .components import card, label_value, progress_bar, divider, status_badge, section_title, empty_state, summary_strip
from .home_scenes import render_home_scene
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
        rows=[x for x in (state.get('overview.cards') or []) if isinstance(x,dict)]
        attention=[x for x in (state.get('overview.attention') or []) if isinstance(x,dict)]
        overall=str(state.get('overview.state') or 'starting').upper()
        col=t.c('danger') if overall=='CRITICAL' else t.c('warn') if overall=='ATTENTION' else t.c('accent')

        # v0.19 Overview prioritizes "what needs my attention?" over a wall of
        # equal diagnostic tiles. Source data remains the same overview model.
        card(d,(8,43,304,157),t,accent=col,width=2)
        section_title(d,(18,52),'WHOLE DEVICE',f,t)
        status_badge(d,(190,49),overall,f,t,color=col,min_width=92)

        primary=rows[:3]
        for i,row in enumerate(primary):
            y=76+i*25
            status=str(row.get('status') or 'ok').lower()
            rcol=t.c('danger') if status in {'critical','error'} else t.c('warn') if status in {'warning','degraded','attention'} else t.c('info') if status=='info' else t.c('text')
            d.text((18,y),str(row.get('title') or '--').upper()[:15],font=f['tiny'],fill=t.c('dim'))
            value=str(row.get('value') or '--')[:20]
            tw=d.textbbox((0,0),value,font=f['small'])[2]
            d.text((290-tw,y-1),value,font=f['small'],fill=rcol)
            if i<2:divider(d,18,y+18,294,t)

        card(d,(312,43,472,157),t)
        section_title(d,(322,52),'MORE STATUS',f,t)
        secondary=rows[3:6]
        if secondary:
            for i,row in enumerate(secondary):
                y=73+i*27
                status=str(row.get('status') or 'ok').lower()
                rcol=t.c('danger') if status in {'critical','error'} else t.c('warn') if status in {'warning','degraded','attention'} else t.c('accent')
                d.text((322,y),str(row.get('title') or '--').upper()[:12],font=f['micro'],fill=t.c('dim'))
                d.text((322,y+10),str(row.get('value') or '--')[:18],font=f['small'],fill=rcol if status!='ok' else t.c('text'))
        else:
            d.text((322,82),'COLLECTING',font=f['small'],fill=t.c('dim'))

        card(d,(8,165,472,268),t,accent=col if attention else t.c('edge'))
        if attention:
            first=attention[0]
            section_title(d,(18,175),f'ATTENTION · {len(attention)}',f,t,color=col)
            d.text((18,195),str(first.get('title') or 'Attention')[:50],font=f['medium'],fill=t.c('text'))
            detail=str(first.get('detail') or '')
            d.text((18,218),detail[:66],font=f['tiny'],fill=t.c('dim'))
            if len(attention)>1:
                d.text((18,245),f'+ {len(attention)-1} MORE ITEM(S) · OPEN OPERATIONS FOR DETAIL',font=f['tiny'],fill=col)
        else:
            section_title(d,(18,176),'STATUS',f,t,color=t.c('accent'))
            d.text((18,197),'NO ACTIVE ATTENTION ITEMS',font=f['medium'],fill=t.c('accent'))
            d.text((18,222),'Core services and available capabilities report nominal.',font=f['tiny'],fill=t.c('dim'))
            d.text((18,244),'Swipe for detail · Operations keeps the full diagnostic view.',font=f['tiny'],fill=t.c('dim'))

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
        # v0.19 structural scene layer: themes may now change composition, not
        # merely recolor the same card dashboard.  Legacy/special fallbacks stay
        # below for themes that do not yet opt into a scene.
        if render_home_scene(d,state,ui):
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
        beast_name=str(self._v(state,'progression.beast.name','BEAST')).strip() or 'BEAST'
        lineage=str(self._v(state,'progression.beast.lineage','standard')).replace('_',' ').upper()
        generation=int(self._v(state,'progression.beast.generation',0) or 0)
        section_title(d,(18,168),beast_name[:20],f,t,color=t.c('accent'))
        d.text((18,181),expression[:18],font=f['micro'],fill=t.c('dim'))
        d.text((18,192),f'LV {lvl:02d}',font=f['medium'],fill=t.c('primary'))
        d.text((72,195),stage[:16],font=f['tiny'],fill=t.c('text'))
        d.text((18,207),f'{lineage[:12]} · G{generation}',font=f['micro'],fill=t.c('dim'))
        progress_bar(d,(116,207,216,213),growth,t,color=t.c('accent'))

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
        t=ui.theme;f=ui.fonts
        aps=[a for a in (state.get('wifi.aps') or []) if isinstance(a,dict)]
        mode=ui.renderer_for('recon')
        rows=sorted(aps,key=lambda a:a.get('rssi',-999),reverse=True)
        strongest=rows[0] if rows else {}
        strongest_rssi=strongest.get('rssi','--')
        channels=len(self._channel_counts(rows))
        summary_strip(
            d,(8,43,472,91),
            [
                ('OBSERVED',len(rows),t.c('primary')),
                ('CHANNELS',channels,t.c('info')),
                ('STRONGEST',f"{strongest_rssi} dBm" if isinstance(strongest_rssi,(int,float)) else '--',t.c('accent')),
                ('VIEW',str(mode).upper(),t.c('secondary')),
            ],
            f,t,
        )

        left=(8,99,286,268)
        right=(294,99,472,268)
        strengths=[]
        for ap in rows[:18]:
            try:strengths.append(max(0,min(100,100+float(ap.get('rssi',-100)))))
            except Exception:strengths.append(0)

        if not rows:
            empty_state(
                d,left,'NO OBSERVATIONS','Waiting for live Bettercap AP state.',f,t,
                hint='RECON STAYS EMPTY UNTIL REAL DATA ARRIVES',
            )
        elif mode=='radar':
            card(d,left,t);cx,cy=147,184
            for r in (28,54,76):d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=t.c('edge'))
            d.line((cx-80,cy,cx+80,cy),fill=t.c('edge'));d.line((cx,cy-80,cx,cy+80),fill=t.c('edge'))
            sweep=(ui.phase*55)%360;ex=cx+int(math.cos(math.radians(sweep))*76);ey=cy+int(math.sin(math.radians(sweep))*76)
            d.line((cx,cy,ex,ey),fill=t.c('grid'),width=1)
            for i,ap in enumerate(rows[:18]):
                try:rssi=float(ap.get('rssi',-100))
                except Exception:rssi=-100
                a=self._channel_angle(ap.get('channel'))
                if a is None:continue
                strength=max(0.0,min(1.0,(rssi+100.0)/70.0));rr=max(9,int(76*(1.0-strength)))
                x=cx+int(math.cos(math.radians(a))*rr);y=cy+int(math.sin(math.radians(a))*rr)
                d.ellipse((x-3,y-3,x+3,y+3),fill=t.c('accent') if i==0 else t.c('primary'))
            section_title(d,(18,108),'LIVE FIELD',f,t)
            d.text((18,249),'RADIUS = RSSI · ANGLE = CHANNEL',font=f['micro'],fill=t.c('dim'))
        elif mode=='polar':polar(d,left,strengths[:12],t,t.c('accent'))
        elif mode=='bars':bars(d,left,strengths[:16],t,t.c('primary'))
        elif mode=='signal':signal_meter(d,left,max(strengths or [0]),t,t.c('accent'))
        else:radar(d,left,strengths[:8] or [0,0,0],list(range(8)),t,t.c('accent'))

        card(d,right,t)
        section_title(d,(304,108),'STRONGEST / RECENT',f,t)
        if rows:
            for i,ap in enumerate(rows[:5]):
                y=128+i*27
                ssid=str(ap.get('hostname') or ap.get('ssid') or '<hidden>').strip() or '<hidden>'
                ch=ap.get('channel','--');rssi=ap.get('rssi','--')
                d.text((304,y),ssid[:18],font=f['small'],fill=t.c('text'))
                d.text((304,y+12),f'CH {ch}',font=f['micro'],fill=t.c('dim'))
                val=f'{rssi} dBm' if isinstance(rssi,(int,float)) else '--'
                vb=d.textbbox((0,0),val,font=f['tiny']);vw=vb[2]-vb[0]
                d.text((462-vw,y+10),val,font=f['tiny'],fill=t.c('accent') if i==0 else t.c('info'))
                if i<4:divider(d,304,y+24,462,t)
        else:
            d.text((304,143),'NO LIVE AP ROWS',font=f['small'],fill=t.c('dim'))
        d.text((304,249),'Detail/search keeps the full catalog.',font=f['micro'],fill=t.c('dim'))

    def networks(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        aps=[a for a in (state.get('wifi.aps') or []) if isinstance(a,dict)]
        rows=sorted(aps,key=lambda a:a.get('rssi',-999),reverse=True)
        hidden=sum(1 for a in rows if not str(a.get('hostname') or a.get('ssid') or '').strip())
        secure=sum(1 for a in rows if str(a.get('encryption') or '').upper() not in {'','OPEN','NONE'})
        strongest=rows[0].get('rssi') if rows else None
        strongest_txt=f'{strongest} dBm' if isinstance(strongest,(int,float)) else '--'

        # Same summary grammar as Recon/Spectrum/Expedition: one glance tells
        # the user what changed before they read individual rows.
        summary_strip(
            d,(8,43,472,91),
            [
                ('OBSERVED',len(rows),t.c('primary')),
                ('SECURE',secure,t.c('secondary')),
                ('HIDDEN',hidden,t.c('info')),
                ('STRONGEST',strongest_txt,t.c('accent')),
            ],
            f,t,
        )

        list_box=(8,99,472,268)
        if not rows:
            empty_state(
                d,list_box,'NO NETWORK OBSERVATIONS','Waiting for live Bettercap network state.',f,t,
                hint='NO DEMO NETWORKS ARE INSERTED',
            )
            return

        # Five taller rows fit the 3.5-inch TFT with a proper hierarchy:
        # identity first, then channel/security/RSSI, then a real-RSSI rail.
        y=99
        visible=rows[:5]
        for i,ap in enumerate(visible):
            rssi=ap.get('rssi')
            try:
                strength=max(0.0,min(1.0,(float(rssi)+100.0)/70.0))
            except Exception:
                strength=0.0
            name=str(ap.get('hostname') or ap.get('ssid') or '<hidden>').strip() or '<hidden>'
            ch=ap.get('channel','--')
            sec=str(ap.get('encryption') or 'OPEN').upper()
            accent=t.c('accent') if i==0 else t.c('primary')
            card(d,(8,y,472,y+30),t,accent=accent if i==0 else t.c('edge'),width=2 if i==0 else 1)
            d.text((17,y+5),name[:29],font=f['small'],fill=t.c('text'))
            meta=f'CH {ch} · {sec[:12]}'
            d.text((17,y+17),meta,font=f['micro'],fill=t.c('dim'))
            val=f'{rssi} dBm' if isinstance(rssi,(int,float)) else '--'
            vb=d.textbbox((0,0),val,font=f['tiny']);vw=max(0,vb[2]-vb[0])
            d.text((460-vw,y+6),val,font=f['tiny'],fill=accent)
            d.rectangle((298,y+22,460,y+24),fill=t.c('edge'))
            if strength>0:
                d.rectangle((298,y+22,298+int(162*strength),y+24),fill=accent)
            y+=33

        if len(rows)>5:
            d.text((12,265),f'+ {len(rows)-5} MORE · OPEN DETAIL/SEARCH FOR FULL CATALOG',font=f['micro'],fill=t.c('dim'))


    def spectrum(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        aps=[a for a in (state.get('wifi.aps') or []) if isinstance(a,dict)]
        mode=ui.renderer_for('spectrum')
        counts=self._channel_counts(aps);channels=sorted(counts);vals=[counts[ch] for ch in channels]
        current=self._v(state,'radio.primary.channel')
        band=self._v(state,'radio.primary.band')
        busiest=max(counts,key=counts.get) if counts else '--'
        summary_strip(
            d,(8,43,472,91),
            [
                ('CURRENT',current,t.c('accent')),
                ('BAND',band,t.c('info')),
                ('BUSIEST',busiest,t.c('secondary')),
                ('APS',len(aps),t.c('primary')),
            ],
            f,t,
        )

        box=(8,99,472,211)
        channel_hist=ui.aux.get('channel_history') if isinstance(getattr(ui,'aux',None),dict) else []
        hist_channels,matrix=self._channel_history_matrix(channel_hist,'ap_count')
        if not aps and not matrix:
            empty_state(
                d,box,'COLLECTING CHANNEL HISTORY','No real channel observations are available yet.',f,t,
                hint='THIS VIEW DOES NOT SYNTHESIZE RF POWER',
            )
        elif mode=='bars':channel_bars(d,box,aps,t)
        elif mode=='line':line_area(d,box,vals,t,t.c('accent'),fill_area=False)
        elif mode=='area':line_area(d,box,vals,t,t.c('accent'),fill_area=True)
        elif mode in {'heatmap','waterfall'}:
            if matrix:
                shown=matrix[-18:] if mode=='heatmap' else matrix[-28:]
                heatmap(d,box,shown,t,t.c('accent') if mode=='waterfall' else t.c('primary'))
                if hist_channels:
                    d.text((14,195),f'CH {hist_channels[0]}',font=f['tiny'],fill=t.c('dim'))
                    d.text((423,195),f'{hist_channels[-1]}',font=f['tiny'],fill=t.c('dim'))
            else:
                empty_state(d,box,'HISTORY NOT READY','Waiting for successive real channel samples.',f,t)
        elif mode=='radar':
            top=sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))[:8]
            radar(d,box,[v for _,v in top],[str(ch) for ch,_ in top],t,t.c('accent'))
        elif mode=='polar':polar(d,box,vals,t,t.c('accent'))
        elif mode=='histogram':histogram(d,box,vals,t,t.c('primary'),bins=10)
        elif mode=='donut':donut(d,box,vals,t,[t.c('primary'),t.c('accent'),t.c('secondary'),t.c('info')],center_text=sum(vals),font=f['small'])
        elif mode=='waveform':waveform(d,box,vals,t,t.c('accent'))
        else:channel_bars(d,box,aps,t)

        hist=ui.histories.get('wifi.ap_count') or []
        card(d,(8,219,472,268),t)
        section_title(d,(18,227),f'OBSERVED ACTIVITY · {str(mode).upper()}',f,t)
        d.text((18,241),'Wi-Fi occupancy derived from observed AP/channel data.',font=f['tiny'],fill=t.c('text'))
        d.text((18,254),'NOT RAW RF POWER',font=f['micro'],fill=t.c('warn'))
        if hist:
            d.text((338,241),f'{len(hist)} AP samples',font=f['tiny'],fill=t.c('dim'))

    def captures(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        mode=ui.renderer_for('captures')
        total=self._v(state,'captures.total',self._v(state,'pwnagotchi.cache.handshake_ap_count',0))
        session=self._v(state,'pwnagotchi.handshakes',0)
        better=self._v(state,'wifi.handshake_ap_count',0)
        vals=[]
        for value in (total,session,better):
            try:vals.append(float(value or 0))
            except Exception:vals.append(0.0)

        card(d,(8,43,214,111),t,accent=t.c('primary'),width=2)
        section_title(d,(18,52),'CAPTURE VAULT',f,t)
        d.text((18,67),str(total),font=f['large'],fill=t.c('primary'))
        d.text((18,91),'STORED CAPTURE RECORDS',font=f['tiny'],fill=t.c('dim'))
        summary_strip(
            d,(222,43,472,111),
            [
                ('SESSION HS',session,t.c('accent')),
                ('LIVE APS',better,t.c('info')),
            ],
            f,t,
        )

        box=(8,119,472,268)
        if max(vals or [0])<=0:
            empty_state(
                d,box,'VAULT EMPTY','No stored or live capture records are currently reported.',f,t,
                hint='DETAILS APPEAR ONLY FROM REAL CAPTURE STATE',
            )
        else:
            card(d,box,t)
            section_title(d,(18,128),f'CAPTURE ANALYTICS · {str(mode).upper()}',f,t)
            graph=(18,148,462,254)
            if mode=='bars':bars(d,graph,vals,t,t.c('accent'))
            elif mode=='donut':donut(d,graph,vals,t,[t.c('primary'),t.c('accent'),t.c('secondary')],center_text=total,font=f['small'])
            elif mode=='radial':
                w=(462-18)//3
                for i,(v,lab,col) in enumerate(zip(vals,['STORED','SESSION','LIVE'],[t.c('primary'),t.c('accent'),t.c('secondary')])):
                    radial(d,(20+i*w,150,16+(i+1)*w-4,250),v,t,col,minimum=0,maximum=max(1,max(vals)),label=lab,font=f['tiny'])
            elif mode=='timeline':timeline(d,graph,ui.events,t,t.c('accent'))
            else:bars(d,graph,vals,t,t.c('accent'))

    def map(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        expedition=ui.aux.get('expedition') if isinstance(getattr(ui,'aux',None),dict) else None
        pts=self._route_points(expedition)
        gps_locked=bool(state.get('gps.fix'))
        dist=state.get('expedition.distance_m')
        dist_txt=f'{float(dist)/1609.344:.2f} mi' if isinstance(dist,(int,float)) else '--'
        summary_strip(
            d,(8,43,472,91),
            [
                ('GPS','LOCK' if gps_locked else 'NO FIX',t.c('accent') if gps_locked else t.c('warn')),
                ('SAT',f"{self._v(state,'gps.satellites_used',0)}/{self._v(state,'gps.satellites_visible',0)}",t.c('info')),
                ('DIST',dist_txt,t.c('secondary')),
                ('ROUTE PTS',self._v(state,'expedition.route_points',0),t.c('primary')),
            ],
            f,t,
        )

        mapbox=(8,99,344,268)
        if pts:
            card(d,mapbox,t)
            section_title(d,(18,108),'RECORDED ROUTE',f,t)
            lats=[p[0] for p in pts];lons=[p[1] for p in pts]
            lat0,lat1=min(lats),max(lats);lon0,lon1=min(lons),max(lons)
            lat_span=max(1e-7,lat1-lat0);lon_span=max(1e-7,lon1-lon0);xa,ya,xb,yb=20,128,332,247
            for x in range(xa,xb+1,52):d.line((x,ya,x,yb),fill=t.c('grid'))
            for y in range(ya,yb+1,30):d.line((xa,y,xb,y),fill=t.c('grid'))
            xy=[]
            for lat,lon,_row in pts:
                x=xa+int((lon-lon0)/lon_span*(xb-xa));y=yb-int((lat-lat0)/lat_span*(yb-ya));xy.append((x,y))
            if len(xy)>=2:d.line(xy,fill=t.c('primary'),width=2)
            x,y=xy[-1];d.ellipse((x-5,y-5,x+5,y+5),outline=t.c('accent'),fill=t.c('panel2'),width=2)
            d.text((18,251),'REAL RECORDED FIXES · AUTO-FIT TRACE · NOT A BASEMAP',font=f['micro'],fill=t.c('dim'))
        else:
            empty_state(
                d,mapbox,'NO RECORDED ROUTE','Field trace appears after real GPS fixes are recorded.',f,t,
                accent=t.c('accent') if gps_locked else t.c('edge'),
                hint='NO FAKE MAP OR POSITION IS DRAWN',
            )

        card(d,(352,99,472,268),t)
        section_title(d,(362,108),'FIELD',f,t)
        sp=state.get('context.motion.speed_mph')
        label_value(d,(362,126),'SPEED',f'{sp:.1f} mph' if isinstance(sp,(int,float)) else '--',f,t,color=t.c('info'),max_chars=12)
        label_value(d,(362,166),'MODE',str(self._v(state,'context.mode.effective','pwn')).upper(),f,t,color=t.c('primary'),max_chars=12)
        label_value(d,(362,206),'UNIQUE AP',self._v(state,'expedition.ap_unique',0),f,t,color=t.c('accent'),max_chars=12)
        d.text((362,247),'EXPEDITION DATA',font=f['micro'],fill=t.c('dim'))

    def expedition(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        active=bool(state.get('expedition.active'))
        eid=str(self._v(state,'expedition.id','--'))
        dur=state.get('expedition.duration_sec');mins=int(float(dur or 0)//60);hrs=mins//60;mins%=60
        dist=state.get('expedition.distance_m');dist_m=float(dist or 0) if isinstance(dist,(int,float)) else 0.0
        state_col=t.c('accent') if active else t.c('dim')

        card(d,(8,43,472,99),t,accent=state_col,width=2 if active else 1)
        section_title(d,(18,52),'FIELD SESSION',f,t)
        status_badge(d,(18,68),'ACTIVE' if active else 'IDLE',f,t,color=state_col,min_width=68)
        d.text((104,72),eid[-22:],font=f['tiny'],fill=t.c('text'))
        tm=f'{hrs:02d}:{mins:02d}'
        tw=d.textbbox((0,0),tm,font=f['medium'])[2]
        d.text((458-tw,69),tm,font=f['medium'],fill=t.c('info'))

        summary_strip(
            d,(8,107,472,163),
            [
                ('DISTANCE',f'{dist_m/1609.344:.2f} mi',t.c('primary')),
                ('ROUTE',self._v(state,'expedition.route_points',0),t.c('info')),
                ('UNIQUE AP',self._v(state,'expedition.ap_unique',0),t.c('accent')),
                ('CAPTURES',self._v(state,'expedition.captures_delta',0),t.c('secondary')),
            ],
            f,t,
        )

        card(d,(8,171,472,268),t)
        section_title(d,(18,180),'SESSION RECORD',f,t)
        d.text((18,197),f"XP +{self._v(state,'expedition.xp_delta',0)}",font=f['medium'],fill=t.c('accent'))
        mt=state.get('expedition.max_temp_c');mc=state.get('expedition.max_cpu_pct');mb=state.get('expedition.min_battery_pct')
        d.text((112,199),f"MAX T {mt:.1f}C" if isinstance(mt,(int,float)) else 'MAX T --',font=f['small'],fill=t.c('warn'))
        d.text((235,199),f"CPU {mc:.0f}%" if isinstance(mc,(int,float)) else 'CPU --',font=f['small'],fill=t.c('text'))
        d.text((335,199),f"MIN BAT {mb:.0f}%" if isinstance(mb,(int,float)) else 'MIN BAT --',font=f['small'],fill=t.c('info'))
        divider(d,18,222,462,t)
        status='RECOVERED AFTER RESTART' if state.get('expedition.recovered') else ('LIVE CHECKPOINTING · RECOVERY ARMED' if active else 'READY FOR NEXT FIELD SESSION')
        d.text((18,232),status,font=f['tiny'],fill=t.c('secondary') if active else t.c('dim'))
        d.text((18,250),'Archive/replay depth belongs in Expedition history, not this glance page.',font=f['micro'],fill=t.c('dim'))

    def beast(self,d,state,ui):
        t=ui.theme;f=ui.fonts
        # v0.19 roster-aware Beast page: creature identity is now first-class
        # cockpit information rather than something visible only in Studio.
        # Everything shown here comes from canonical progression/roster state.
        name=str(self._v(state,'progression.beast.name','BEAST')).strip() or 'BEAST'
        kind=str(self._v(state,'progression.beast.kind','beast')).replace('_',' ').upper()
        lineage=str(self._v(state,'progression.beast.lineage','standard')).replace('_',' ').upper()
        generation=int(self._v(state,'progression.beast.generation',0) or 0)
        roster=state.get('progression.roster.summary') if isinstance(state.get('progression.roster.summary'),dict) else {}
        roster_total=int(roster.get('total') or 1)
        roster_monsters=int(roster.get('monsters') or 0)
        level=int(self._v(state,'progression.level',1));max_level=int(self._v(state,'progression.max_level',100))
        stage=str(self._v(state,'progression.stage','Hatchling')).upper()
        xp=int(self._v(state,'progression.xp',0));next_xp=int(self._v(state,'progression.xp_next_level',0))
        pct=self._pct(state,'progression.level_progress_pct')
        aura=str(self._v(state,'progression.aura','none')).upper()
        mood=str(self._v(state,'pwnagotchi.mood','awake')).upper()
        mode=str(self._v(state,'context.mode.effective','pwn')).upper()
        beast_aps=int(self._v(state,'progression.discovery.beast_unique_aps',0) or 0)
        device_first=int(self._v(state,'progression.discovery.device_first_witnessed',0) or 0)
        ach=int(self._v(state,'progression.achievements.count',0) or 0)

        # Left side is deliberately creature-led. The compact identity card
        # beneath the face is what makes switching Beasts visibly meaningful.
        self.face.draw(d,(8,43,210,206),t,state,ui.phase)
        card(d,(8,214,210,268),t,accent=t.c('primary'))
        section_title(d,(18,222),name[:22],f,t,color=t.c('accent'))
        d.text((18,236),f'{kind[:8]} · G{generation} · {lineage[:14]}',font=f['tiny'],fill=t.c('text'))
        d.text((18,251),f'ROSTER {roster_total} · MONSTERS {roster_monsters}',font=f['micro'],fill=t.c('dim'))

        # Right side is one readable progression instrument, not a wall of
        # mini-cards. Progress, personality and discovery each get one layer.
        card(d,(218,43,472,268),t,accent=t.c('edge'))
        section_title(d,(230,52),'PROGRESSION',f,t)
        d.text((230,65),f'LEVEL {level:02d}',font=f['large'],fill=t.c('primary'))
        sb=d.textbbox((0,0),stage,font=f['small']);sw=max(0,sb[2]-sb[0])
        d.text((460-sw,70),stage,font=f['small'],fill=t.c('text'))
        d.text((230,91),f'XP {xp:,}',font=f['small'],fill=t.c('text'))
        need='MAX LEVEL' if level>=max_level else f'{next_xp:,} TO NEXT'
        nb=d.textbbox((0,0),need,font=f['tiny']);nw=max(0,nb[2]-nb[0])
        d.text((460-nw,93),need,font=f['tiny'],fill=t.c('dim'))
        progress_bar(d,(230,108,460,117),pct,t,color=t.c('accent'))
        d.text((230,120),f'{pct:0.1f}% LEVEL PROGRESS',font=f['micro'],fill=t.c('dim'))

        divider(d,230,136,460,t)
        section_title(d,(230,145),'PERSONALITY / CONTEXT',f,t)
        label_value(d,(230,158),'MOOD',mood,f,t,color=t.c('accent'),value_font='small',max_chars=11)
        label_value(d,(310,158),'AURA',aura,f,t,color=t.c('secondary'),value_font='small',max_chars=11)
        label_value(d,(390,158),'MODE',mode,f,t,color=t.c('info'),value_font='small',max_chars=10)

        divider(d,230,194,460,t)
        section_title(d,(230,203),'THIS BEAST',f,t)
        label_value(d,(230,216),'DISCOVERED',beast_aps,f,t,color=t.c('primary'),value_font='small',max_chars=8)
        label_value(d,(315,216),'FIRST',device_first,f,t,color=t.c('info'),value_font='small',max_chars=8)
        label_value(d,(390,216),'ACH',ach,f,t,color=t.c('accent'),value_font='small',max_chars=8)
        d.text((230,253),'Creature progress persists when another Beast wakes.',font=f['micro'],fill=t.c('dim'))


    def system(self,d,state,ui):
        t=ui.theme;f=ui.fonts;mode=ui.renderer_for('system')
        health=str(self._v(state,'health.core.state','--')).upper()
        temp=f"{state.get('system.temp.cpu_c',0):.1f}C" if isinstance(state.get('system.temp.cpu_c'),(int,float)) else '--'
        cpu=f"{state.get('system.cpu.total',0):.0f}%" if isinstance(state.get('system.cpu.total'),(int,float)) else '--'
        ram=f"{state.get('system.memory.used_pct',0):.0f}%" if isinstance(state.get('system.memory.used_pct'),(int,float)) else '--'
        hcol=t.c('accent') if health=='HEALTHY' else t.c('warn')

        # Compact status spine instead of four identical metric boxes.
        card(d,(8,43,294,105),t,accent=hcol)
        section_title(d,(18,52),'DEVICE HEALTH',f,t)
        status_badge(d,(18,69),health,f,t,color=hcol,min_width=84)
        label_value(d,(119,57),'TEMP',temp,f,t,color=t.c('warn'),max_chars=8)
        label_value(d,(180,57),'CPU',cpu,f,t,color=t.c('primary'),max_chars=8)
        label_value(d,(238,57),'RAM',ram,f,t,color=t.c('info'),max_chars=8)

        gov=str(self._v(state,'governor.mode','FULL')).upper()
        budget=self._v(state,'governor.budget_pct',100)
        gcol=t.c('danger') if gov=='SURVIVAL' else t.c('warn') if gov=='REDUCED' else t.c('accent') if gov=='GUARDED' else t.c('text')
        card(d,(302,43,472,105),t)
        section_title(d,(312,52),'RESOURCE MODE',f,t)
        d.text((312,68),gov[:12],font=f['medium'],fill=gcol)
        d.text((312,88),f'BUDGET {budget}%',font=f['tiny'],fill=t.c('dim'))

        card(d,(8,113,294,268),t)
        section_title(d,(18,122),'HARDWARE / POWER / LINKS',f,t)
        power_available=bool(state.get('power.telemetry.available'))
        power='UPS '+str(self._v(state,'power.ups.state','--')).upper()
        d.text((18,143),power,font=f['small'],fill=t.c('accent') if power_available else t.c('dim'))
        if power_available:
            bat=self._v(state,'power.battery.percent_estimate',0)
            volt=self._v(state,'power.battery.voltage_v',0)
            watts=self._v(state,'power.power_w',0)
            d.text((18,163),f'BAT {bat:.0f}%  {volt:.2f}V  {watts:.2f}W',font=f['small'],fill=t.c('text'))
        else:
            d.text((18,163),'No managed battery telemetry',font=f['tiny'],fill=t.c('dim'))
        divider(d,18,184,284,t)
        label_value(d,(18,194),'DOCK',str(self._v(state,'dock.state','field')).upper(),f,t,color=t.c('secondary'),max_chars=12)
        label_value(d,(110,194),'ETH','LINK' if state.get('network.ethernet.carrier') else 'DOWN',f,t,color=t.c('accent') if state.get('network.ethernet.carrier') else t.c('dim'),max_chars=8)
        label_value(d,(182,194),'CAPS',self._v(state,'capabilities.count',0),f,t,color=t.c('info'),max_chars=8)
        d.text((18,239),f"LIFETIME DISCOVERIES {self._v(state,'wifi.encounters.lifetime_unique',0)}",font=f['tiny'],fill=t.c('dim'))
        d.text((18,252),'Detailed services, storage and diagnostics live in Operations.',font=f['micro'],fill=t.c('dim'))

        cpu_hist=ui.histories.get('system.cpu.total') or []
        temp_hist=ui.histories.get('system.temp.cpu_c') or []
        section_title(d,(308,116),f'CPU % · {mode}',f,t,color=t.c('primary'))
        section_title(d,(308,190),'TEMP C',f,t,color=t.c('warn'))
        top=(302,130,472,184);bottom=(302,204,472,268)
        if mode=='area':
            line_area(d,top,cpu_hist,t,t.c('primary'),fill_area=True);line_area(d,bottom,temp_hist,t,t.c('warn'),fill_area=True)
        elif mode=='waveform':
            waveform(d,top,cpu_hist,t,t.c('primary'));waveform(d,bottom,temp_hist,t,t.c('warn'))
        elif mode=='histogram':
            histogram(d,top,cpu_hist,t,t.c('primary'));histogram(d,bottom,temp_hist,t,t.c('warn'))
        elif mode=='waterfall':
            waterfall(d,top,cpu_hist,t,t.c('primary'));waterfall(d,bottom,temp_hist,t,t.c('warn'))
        else:
            line_area(d,top,cpu_hist,t,t.c('primary'),fill_area=False);line_area(d,bottom,temp_hist,t,t.c('warn'),fill_area=False)
