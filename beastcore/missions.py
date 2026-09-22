from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUILTINS=(
    {'id':'field-survey','label':'Field Survey','description':'Portable RF/GPS observation session','deck':'field','theme':'classic','apps':['overview','recon','spectrum','map','expedition','capture_vault'],'capabilities':['display'],'checklist':['Confirm storage health','Confirm GPS state','Start or resume Expedition','Review captures before ending session']},
    {'id':'road-trip','label':'Road Trip','description':'Navigation, Expedition and low-distraction status','deck':'field','theme':'ghost_minimal','apps':['overview','map','expedition','system'],'capabilities':['gps'],'checklist':['Confirm GPS receiver','Check available storage','Use low-distraction layout']},
    {'id':'lab-diagnostics','label':'Lab Diagnostics','description':'System, topology and troubleshooting workspace','deck':'system','theme':'amber_tactical','apps':['operations','topology','diagnostics','incidents','performance','tasks'],'capabilities':['display'],'checklist':['Review Overview attention','Inspect Topology failures','Review Black Box incidents','Create Support Bundle if needed']},
    {'id':'home-base','label':'Home Base','description':'Docked maintenance, backup and library workflow','deck':'system','theme':'minimal','apps':['overview','backups','field_library','plugins','storage','connectivity'],'capabilities':['display'],'checklist':['Create recovery backup','Index Field Library','Review storage','Review plugin health']},
)

class MissionPackEngine:
    def __init__(self,state,root: str='/var/lib/beastagotchi/missions') -> None:
        self.state=state;self.root=Path(root)

    @staticmethod
    def _clean(obj: dict[str,Any])->dict[str,Any] | None:
        mid=str(obj.get('id') or '').strip().lower()
        label=str(obj.get('label') or '').strip()
        if not mid or not label:return None
        def sl(name,limit=32):
            raw=obj.get(name) or []
            return [str(x)[:96] for x in raw[:limit] if str(x).strip()] if isinstance(raw,list) else []
        return {'id':mid[:48],'label':label[:64],'description':str(obj.get('description') or '')[:180],'deck':str(obj.get('deck') or '')[:32],'theme':str(obj.get('theme') or '')[:32],'apps':sl('apps'),'capabilities':sl('capabilities'),'checklist':sl('checklist'),'source':str(obj.get('source') or 'user')}

    def catalog(self)->list[dict[str,Any]]:
        merged={x['id']:dict(x,source='builtin') for x in BUILTINS}
        self.root.mkdir(parents=True,exist_ok=True)
        for fp in sorted(self.root.glob('*.json')):
            try:obj=json.loads(fp.read_text())
            except Exception:continue
            if not isinstance(obj,dict):continue
            obj=dict(obj,source='user');row=self._clean(obj)
            if row:merged[row['id']]=row
        return list(merged.values())

    def tick(self)->dict[str,Any]:
        rows=self.catalog();caps=set(self.state.get('capabilities.present',[]) or [])
        for r in rows:
            req=set(r.get('capabilities') or []);r['requirements_met']=req.issubset(caps);r['missing_capabilities']=sorted(req-caps)
        return {'missions.count':len(rows),'missions.items':rows,'missions.available_count':sum(1 for r in rows if r.get('requirements_met')),'missions.root':str(self.root)}
