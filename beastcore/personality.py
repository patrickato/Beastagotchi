from __future__ import annotations

import time
from typing import Any


class PersonalityEngine:
    """Derive canonical Beast personality state from real platform conditions.

    This engine never changes Pwnagotchi behavior.  It turns observed state into
    a consistent experiential vocabulary that themes/face packs may render.
    """

    def __init__(self,state,clock=time.monotonic) -> None:
        self.state=state;self.clock=clock;self._last_ap=None;self._last_ap_change=clock()

    def tick(self)->dict[str,Any]:
        now=self.clock()
        aps=int(self.state.get('wifi.ap_count',0) or 0)
        if self._last_ap is None:self._last_ap=aps
        if aps!=self._last_ap:self._last_ap=aps;self._last_ap_change=now
        quiet=max(0.0,now-self._last_ap_change)
        health=str(self.state.get('health.core.state','starting') or 'starting')
        gov=str(self.state.get('governor.mode','FULL') or 'FULL')
        temp=float(self.state.get('system.temp.cpu_c',0) or 0)
        gps_state=str(self.state.get('gps.state','unknown') or 'unknown')
        pwn=str(self.state.get('pwnagotchi.service.state','unknown') or 'unknown')
        bc=str(self.state.get('bettercap.state','unknown') or 'unknown')
        exp=bool(self.state.get('expedition.active',False))
        recent_capture=bool(self.state.get('semantic.capture.recent',False))
        phase=str(self.state.get('ambient.day_phase','day') or 'day')
        cpu=float(self.state.get('system.cpu.total',0) or 0)
        lvl=int(self.state.get('progression.level',1) or 1)

        if health in {'critical','failed'} or pwn not in {'active','running'} or bc not in {'active','running'}:
            mood='fault';energy=20;focus=95;curiosity=10
        elif temp>=80 or gov=='SURVIVAL':
            mood='overheated';energy=25;focus=80;curiosity=10
        elif recent_capture:
            mood='celebrating';energy=95;focus=70;curiosity=80
        elif gps_state in {'searching','connected_no_fix'} and exp:
            mood='gps-searching';energy=65;focus=85;curiosity=70
        elif exp and quiet<45:
            mood='hunting';energy=80;focus=85;curiosity=90
        elif aps>0 and quiet<120:
            mood='curious';energy=70;focus=65;curiosity=90
        elif phase in {'night','late_night'} and quiet>600:
            mood='sleepy';energy=25;focus=30;curiosity=25
        elif quiet>900:
            mood='bored';energy=40;focus=35;curiosity=45
        else:
            mood='idle';energy=max(35,min(75,int(70-cpu*.25)));focus=50;curiosity=55

        confidence=max(10,min(100,35 + lvl//2 + (20 if health=='healthy' else 0) + (10 if gps_state=='locked' else 0)))
        stress=max(0,min(100,(100-energy)//2 + (35 if gov in {'REDUCED','SURVIVAL'} else 0) + (45 if health not in {'healthy','starting'} else 0)))
        return {
            'beast.mood':mood,
            'beast.energy':int(energy),
            'beast.curiosity':int(curiosity),
            'beast.focus':int(focus),
            'beast.confidence':int(confidence),
            'beast.stress':int(stress),
            'beast.quiet_sec':round(quiet,1),
            'beast.expression':mood,
            'beast.personality.source':'derived_live',
        }
