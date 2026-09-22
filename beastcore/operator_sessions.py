from __future__ import annotations

import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

LEVELS=("observer","operator","maintainer","administrator")


class OperatorSessionManager:
    """Owner-controlled, expiring Beast Operator privilege session.

    The session file is local runtime state only.  It does not itself grant OS
    privileges; it tells structured Beast tools which policy tier the owner has
    temporarily authorized.  All mutations still traverse ActionBroker.
    """

    def __init__(self,path: str='/run/beastagotchi/operator-session.json',clock=time.time) -> None:
        self.path=Path(path);self.clock=clock

    def _read(self)->dict[str,Any]:
        try:
            obj=json.loads(self.path.read_text())
            return obj if isinstance(obj,dict) else {}
        except Exception:
            return {}

    def current(self)->dict[str,Any]:
        now=float(self.clock());obj=self._read()
        level=str(obj.get('level') or 'observer')
        if level not in LEVELS:level='observer'
        expires=float(obj.get('expires_at') or 0)
        active=bool(obj) and expires>now and level!='observer'
        if not active:
            return {'active':False,'level':'observer','expires_at':None,'remaining_sec':0,'session_id':None,'actor':None}
        return {
            'active':True,'level':level,'expires_at':expires,'remaining_sec':max(0,int(expires-now)),
            'session_id':obj.get('session_id'),'actor':obj.get('actor'),'started_at':obj.get('started_at'),
        }

    def authorize(self,level: str,duration_sec: int=900,*,actor: str='owner')->dict[str,Any]:
        level=str(level or '').strip().lower()
        if level not in LEVELS or level=='observer':raise ValueError('elevated level required')
        duration=max(60,min(int(duration_sec),3600 if level=='administrator' else 14400))
        now=float(self.clock());obj={
            'session_id':secrets.token_urlsafe(12),'level':level,'actor':str(actor or 'owner'),
            'started_at':now,'expires_at':now+duration,
        }
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,separators=(',',':'))+'\n')
        os.chmod(tmp,0o600);os.replace(tmp,self.path)
        return self.current()

    def revoke(self)->dict[str,Any]:
        try:self.path.unlink()
        except FileNotFoundError:pass
        return self.current()
