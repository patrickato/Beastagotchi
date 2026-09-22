from __future__ import annotations

import json
import shutil
from typing import Any

from .base import Collector
from ..util import run


class ContainerCollector(Collector):
    """Read-only Docker/Podman inventory.

    Container support is optional. The collector is intentionally inert when no
    runtime exists so the base Pwnagotchi image gains no dependency or daemon.
    """
    name='containers'
    interval=15.0
    priority=45

    def _runtime(self) -> tuple[str,str] | None:
        for name in ('podman','docker'):
            path=shutil.which(name)
            if path:return name,path
        return None

    @staticmethod
    def _parse_labels(raw) -> dict[str,str]:
        if isinstance(raw,dict):return {str(k):str(v) for k,v in raw.items()}
        out={}
        for part in str(raw or '').split(','):
            if '=' in part:
                k,v=part.split('=',1);out[k.strip()]=v.strip()
        return out

    @staticmethod
    def _is_beast_managed(labels: dict[str,str]) -> bool:
        low={str(k).lower():str(v).lower() for k,v in labels.items()}
        return low.get('io.beastagotchi.managed')=='true' or low.get('beastagotchi.managed')=='true'

    def collect(self) -> dict[str,Any]:
        rt=self._runtime()
        if not rt:
            return {'containers.runtime.available':False,'containers.runtime':None,'containers.count':0,'containers.running_count':0,'containers.items':[]}
        name,path=rt
        rc,out,err=run([path,'ps','-a','--format','{{json .}}'],timeout=5)
        items=[]
        if rc==0:
            for line in out.splitlines():
                try:row=json.loads(line)
                except Exception:continue
                if not isinstance(row,dict):continue
                # Docker and Podman field names differ slightly. Preserve raw
                # fields but normalize the common Beast-facing subset.
                names=row.get('Names') or row.get('Names') or row.get('Name') or row.get('names') or ''
                status=row.get('Status') or row.get('State') or row.get('status') or ''
                image=row.get('Image') or row.get('image') or ''
                cid=row.get('ID') or row.get('Id') or row.get('id') or ''
                running=str(status).lower().startswith('up') or str(status).lower()=='running'
                labels=self._parse_labels(row.get('Labels') or row.get('labels') or {})
                items.append({'id':str(cid),'name':str(names),'image':str(image),'status':str(status),'running':running,'labels':labels,'beast_managed':self._is_beast_managed(labels),'raw':row})
        return {
            'containers.runtime.available':True,
            'containers.runtime':name,
            'containers.runtime.path':path,
            'containers.runtime.state':'ready' if rc==0 else 'unavailable',
            'containers.runtime.error':(err or '')[-300:] if rc!=0 else None,
            'containers.count':len(items),
            'containers.running_count':sum(1 for x in items if x.get('running')),
            'containers.managed_count':sum(1 for x in items if x.get('beast_managed')),
            'containers.items':items,
        }
