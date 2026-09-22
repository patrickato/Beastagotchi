from __future__ import annotations

import shutil
from typing import Any

from .base import Collector
from ..util import run


class BluetoothCollector(Collector):
    """Read-only onboard/external Bluetooth adapter state.

    Discovery/scanning is deliberately not started here.  Beast first exposes
    the Pi's existing Bluetooth capability and adapter health; an Observer app
    can later opt into active discovery as a separate foreground operation.
    """
    name='bluetooth'
    interval=15.0
    priority=45

    @staticmethod
    def _parse_show(text: str) -> dict[str,Any]:
        out: dict[str,Any]={}
        first=''
        for raw in str(text or '').splitlines():
            line=raw.strip()
            if not line:continue
            if line.startswith('Controller '):
                parts=line.split()
                if len(parts)>=2:first=parts[1]
                continue
            if ':' not in line:continue
            k,v=line.split(':',1);key=k.strip().lower().replace(' ','_');val=v.strip()
            if val.lower() in {'yes','no'}:out[key]=val.lower()=='yes'
            else:out[key]=val
        if first:out['address']=first
        return out

    def collect(self) -> dict[str,Any]:
        path=shutil.which('bluetoothctl')
        if not path:
            return {
                'bluetooth.available':False,
                'bluetooth.adapter.present':False,
                'bluetooth.adapter.state':'tool_unavailable',
            }
        rc,out,err=run([path,'show'],timeout=4)
        info=self._parse_show(out) if rc==0 else {}
        present=bool(info.get('address'))
        return {
            'bluetooth.available':True,
            'bluetooth.adapter.present':present,
            'bluetooth.adapter.state':'ready' if present else 'no_controller',
            'bluetooth.adapter.address':info.get('address'),
            'bluetooth.adapter.name':info.get('name') or info.get('alias'),
            'bluetooth.adapter.powered':info.get('powered'),
            'bluetooth.adapter.discoverable':info.get('discoverable'),
            'bluetooth.adapter.pairable':info.get('pairable'),
            'bluetooth.adapter.discovering':info.get('discovering'),
            'bluetooth.adapter.error':(err or '')[-300:] if rc!=0 else None,
        }
