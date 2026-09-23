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
    def __init__(self,state,root: str='/var/lib/beastagotchi/missions',pack_root: str='/var/lib/beastagotchi/packs/installed') -> None:
        self.state=state;self.root=Path(root);self.pack_root=Path(pack_root)

    @staticmethod
    def _clean(obj: dict[str,Any])->dict[str,Any] | None:
        mid=str(obj.get('id') or '').strip().lower()
        label=str(obj.get('label') or '').strip()
        if not mid or not label:return None
        def sl(name,limit=32):
            raw=obj.get(name) or []
            return [str(x)[:96] for x in raw[:limit] if str(x).strip()] if isinstance(raw,list) else []
        face_profile=str(obj.get('face_profile') or '')[:96]
        animation_profile=str(obj.get('animation_profile') or '')[:96]
        board=str(obj.get('board') or '')[:96]
        layout=str(obj.get('layout') or '')[:96]
        theme=str(obj.get('theme') or '')[:64]
        experience=bool(theme or face_profile or animation_profile or board or layout)
        return {
            'id':mid[:64],'label':label[:64],'description':str(obj.get('description') or '')[:180],
            'deck':str(obj.get('deck') or '')[:32],'theme':theme,'face_profile':face_profile,
            'animation_profile':animation_profile,'board':board,'layout':layout,
            'apps':sl('apps'),'capabilities':sl('capabilities'),'checklist':sl('checklist'),
            'source':str(obj.get('source') or 'user')[:128],
            'readonly':bool(obj.get('readonly',False)),'experience':experience,
        }

    @staticmethod
    def _runtime_id(pack_id: str, mission_id: str)->str:
        def clean(v):
            return ''.join(c if c.isalnum() or c in '_-' else '_' for c in str(v).lower()).strip('_')
        return ('pack_'+clean(pack_id)+'_'+clean(mission_id))[:64]

    def _pack_missions(self)->list[dict[str,Any]]:
        out=[]
        try:packs=sorted(self.pack_root.iterdir())
        except OSError:return out
        for pack in packs:
            if not pack.is_dir():continue
            try:
                state=json.loads((pack/'state.json').read_text());manifest=json.loads((pack/'manifest.json').read_text())
                if not bool(state.get('enabled')):continue
                if str(manifest.get('pack_type') or manifest.get('type') or '').lower()!='mission':continue
                pack_id=str(manifest.get('id') or pack.name)
                for fp in sorted((pack/'missions').glob('*.json'))[:64]:
                    obj=json.loads(fp.read_text())
                    rows=obj.get('missions') if isinstance(obj,dict) and isinstance(obj.get('missions'),list) else [obj]
                    for raw in rows[:64]:
                        if not isinstance(raw,dict):continue
                        raw=dict(raw,source='pack:'+pack_id,readonly=True)
                        row=self._clean(raw)
                        if not row:continue
                        local_id=row['id'];row['local_id']=local_id;row['id']=self._runtime_id(pack_id,local_id)
                        row['source_pack']=pack_id;row['source_file']=str(fp)
                        out.append(row)
            except Exception:continue
        return out

    def catalog(self)->list[dict[str,Any]]:
        merged={x['id']:dict(x,source='builtin',readonly=True,experience=bool(x.get('theme'))) for x in BUILTINS}
        self.root.mkdir(parents=True,exist_ok=True)
        for fp in sorted(self.root.glob('*.json')):
            try:obj=json.loads(fp.read_text())
            except Exception:continue
            if not isinstance(obj,dict):continue
            obj=dict(obj,source='user');row=self._clean(obj)
            if row:merged[row['id']]=row
        for row in self._pack_missions():
            merged[row['id']]=row
        return list(merged.values())

    def tick(self)->dict[str,Any]:
        rows=self.catalog();caps=set(self.state.get('capabilities.present',[]) or [])
        pack_rows=[x for x in (self.state.get('packs.items',[]) or []) if isinstance(x,dict)]
        pack_by_id={str(x.get('id') or ''):x for x in pack_rows if x.get('origin')!='staged'}
        for r in rows:
            req=set(r.get('capabilities') or []);r['missing_capabilities']=sorted(req-caps)
            pack_ok=True
            if r.get('source_pack'):
                prow=pack_by_id.get(str(r['source_pack']))
                pack_ok=bool(prow and prow.get('requirements_met') and prow.get('enabled'))
            r['pack_requirements_met']=pack_ok
            r['requirements_met']=not r['missing_capabilities'] and pack_ok
            r['preview_only']=bool(r.get('experience'))
        return {
            'missions.count':len(rows),'missions.items':rows,
            'missions.available_count':sum(1 for r in rows if r.get('requirements_met')),
            'missions.experience_count':sum(1 for r in rows if r.get('experience')),
            'missions.pack_count':sum(1 for r in rows if r.get('source_pack')),
            'missions.root':str(self.root),'missions.pack_root':str(self.pack_root),
            'missions.experience_apply_enabled':False,
            'missions.experience_apply_reason':'v0.19 exposes validated composition profiles for preview/review; transactional preference application is the next gate',
        }
