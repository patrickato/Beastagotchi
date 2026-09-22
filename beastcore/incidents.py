from __future__ import annotations

import time
import uuid
from typing import Any


class IncidentEngine:
    """Durable Black Box incident detection from canonical Beast state."""

    def __init__(self,state,store,events,clock=time.time) -> None:
        self.state=state;self.store=store;self.events=events;self.clock=clock;self._active:set[str]=set()

    def _conditions(self) -> dict[str,dict[str,Any]]:
        out={}
        pwn=str(self.state.get('pwnagotchi.service.state') or 'unknown').lower()
        better=str(self.state.get('bettercap.state') or 'unknown').lower()
        uptime=float(self.state.get('health.core.uptime_sec') or 0)
        if uptime>=20 and pwn not in {'active','running'}:
            out['service.pwnagotchi']={'severity':'critical','summary':'Pwnagotchi service unavailable','detail':f'state={pwn} sub={self.state.get("pwnagotchi.service.substate") or "--"}'}
        if uptime>=20 and better not in {'active','running','ready'}:
            out['service.bettercap']={'severity':'critical','summary':'Bettercap service unavailable','detail':f'state={better}'}
        if bool(self.state.get('storage.root.readonly')):
            out['storage.root_readonly']={'severity':'critical','summary':'Root filesystem became read-only','detail':'Persistent writes may fail; inspect storage immediately.'}
        used=self.state.get('storage.root.used_pct')
        if isinstance(used,(int,float)) and float(used)>=95:
            out['storage.root_full']={'severity':'warning','summary':'Root filesystem critically full','detail':f'{float(used):.1f}% used'}
        temp=self.state.get('system.temp.cpu_c')
        if isinstance(temp,(int,float)) and float(temp)>=82:
            out['thermal.cpu_hot']={'severity':'warning','summary':'CPU temperature critical','detail':f'{float(temp):.1f} C'}
        conflicts=list(self.state.get('plugins.display_conflicts_enabled') or [])
        if conflicts:
            out['plugins.display_conflict']={'severity':'warning','summary':'Competing display plugin enabled','detail':', '.join(map(str,conflicts))}
        return out

    def _snapshot(self,kind: str, summary: str='') -> dict[str,Any]:
        keys=[
            'health.core.state','health.core.critical_failures','pwnagotchi.service.state','pwnagotchi.service.substate','bettercap.state',
            'radio.primary.name','radio.primary.channel','gps.state','gps.fix','system.cpu.total','system.memory.used_pct','system.temp.cpu_c',
            'storage.root.used_pct','storage.root.readonly','governor.mode','plugins.display_conflicts_enabled','expedition.id',
        ]
        terms=[]
        for raw in (kind.replace('.',' '),summary):
            for word in str(raw).split():
                clean=''.join(ch for ch in word.lower() if ch.isalnum() or ch in {'_','-'})
                if len(clean)>=3 and clean not in terms:terms.append(clean)
        related=[]
        for term in terms[:6]:
            try:
                for row in self.store.search_library(term,4,0):
                    if row.get('id') not in {x.get('id') for x in related}:related.append(row)
            except Exception:
                continue
            if len(related)>=6:break
        return {'kind':kind,'state':{k:self.state.get(k) for k in keys},'events':self.events.recent(16,include_transient=False),'related_documents':related[:6]}

    def tick(self) -> tuple[dict[str,Any],list[tuple[str,str,dict[str,Any],str]]]:
        now=float(self.clock());conditions=self._conditions();rows=[]
        current=set(conditions)
        for kind,info in conditions.items():
            is_new=kind not in self._active
            iid=str(uuid.uuid4()) if is_new else ''
            opened=self.store.open_incident({'id':iid,'kind':kind,'severity':info['severity'],'opened_at':now,'last_seen':now,'summary':info['summary'],'detail':info['detail'],'snapshot':self._snapshot(kind,info['summary']) if is_new else {}})
            if is_new:rows.append(('incident.opened','incidents',{'id':opened['id'],'kind':kind,'summary':info['summary']},info['severity']))
        for kind in self._active-current:
            if self.store.resolve_incident(kind,now):rows.append(('incident.resolved','incidents',{'kind':kind},'info'))
        self._active=current
        recent=self.store.recent_incidents(20);open_rows=[x for x in recent if x.get('status')=='open']
        patch={'incidents.open_count':len(open_rows),'incidents.open':open_rows,'incidents.recent':recent,'incidents.last_checked_at':now}
        return patch,rows
