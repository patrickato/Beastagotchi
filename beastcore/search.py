from __future__ import annotations

from typing import Any


class UniversalSearch:
    """Search durable Beast records and current canonical state without web access."""

    def __init__(self,state,store) -> None:
        self.state=state;self.store=store

    def search(self,query: str,limit: int=12) -> dict[str,Any]:
        q=str(query or '').strip();limit=max(1,min(int(limit),50))
        if not q:return {'query':'','count':0,'groups':{}}
        groups: dict[str,list[dict[str,Any]]]={}
        groups['library']=[{'type':'document','title':r.get('title') or r.get('filename'),'subtitle':r.get('path'),'data':r} for r in self.store.search_library(q,limit)]
        groups['networks']=[{'type':'network','title':r.get('ssid') or '<hidden>','subtitle':r.get('bssid'),'data':r} for r in self.store.search_encounters(q,limit,0)]
        groups['captures']=[{'type':'capture','title':r.get('filename'),'subtitle':r.get('network_hint') or r.get('path'),'data':r} for r in self.store.search_captures(q,limit)]
        groups['events']=[{'type':'event','title':r.get('type'),'subtitle':r.get('source'),'data':r} for r in self.store.search_events(q,limit)]
        ql=q.lower();tele=[]
        for key,value in self.state.snapshot(False).items():
            if ql in str(key).lower():tele.append({'type':'telemetry','title':str(key),'subtitle':str(value)[:120],'data':{'key':key,'value':value}})
            if len(tele)>=limit:break
        groups['telemetry']=tele
        groups={k:v for k,v in groups.items() if v}
        return {'query':q,'count':sum(len(v) for v in groups.values()),'groups':groups}
