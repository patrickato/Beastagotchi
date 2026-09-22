from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DockEngine:
    """Derives Beast DOCKED from external power + trusted wired home network."""
    def __init__(self,state, profile='/etc/beastagotchi/home_dock.json'):
        self.state=state; self.profile=Path(profile)
    def _profile(self):
        try:
            obj=json.loads(self.profile.read_text())
            return obj if isinstance(obj,dict) else {}
        except Exception: return {}
    def tick(self)->dict[str,Any]:
        ext=bool(self.state.get('power.external_present',False))
        carrier=bool(self.state.get('network.ethernet.carrier',False))
        gw=str(self.state.get('network.default.gateway') or '')
        mac=str(self.state.get('network.default.gateway_mac') or '').lower()
        p=self._profile(); enrolled=bool(p)
        home=False
        if enrolled and carrier:
            pmac=str(p.get('gateway_mac') or '').lower(); pgw=str(p.get('gateway') or '')
            home=bool((pmac and mac and pmac==mac) or (not pmac and pgw and gw==pgw))
        docked=ext and carrier and home
        reason='docked' if docked else ('no_external_power' if not ext else 'no_ethernet' if not carrier else 'home_not_enrolled' if not enrolled else 'not_home_network')
        return {
            'dock.state':'docked' if docked else 'field',
            'dock.docked':docked,
            'dock.external_power':ext,
            'dock.ethernet':carrier,
            'dock.home_network':home,
            'dock.home_enrolled':enrolled,
            'dock.reason':reason,
        }
