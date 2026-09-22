from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import tarfile
from .base import Collector

class BackupCollector(Collector):
    name='backups';interval=30.0;priority=40
    def __init__(self,root: str='/var/lib/beastagotchi/backups')->None:self.root=Path(root)
    def collect(self)->dict[str,Any]:
        rows=[]
        if self.root.is_dir():
            for p in sorted(self.root.glob('beastagotchi-backup-*.tar.gz'),key=lambda x:x.stat().st_mtime,reverse=True)[:20]:
                try:
                    st=p.stat();valid=False;created_at=None
                    try:
                        with tarfile.open(p,'r:gz') as tf:
                            members=tf.getmembers()
                            safe=all(m.name=='beastagotchi-backup' or m.name.startswith('beastagotchi-backup/') for m in members)
                            mf=tf.extractfile('beastagotchi-backup/manifest.json') if safe else None
                            if mf:
                                manifest=json.load(mf);created_at=manifest.get('created_at');valid=bool(manifest.get('format')==1)
                    except Exception:
                        valid=False
                    rows.append({'name':p.name,'path':str(p),'size_bytes':int(st.st_size),'mtime':float(st.st_mtime),'created_at':created_at,'valid':valid})
                except OSError:pass
        return {'backups.count':len(rows),'backups.items':rows,'backups.last':rows[0] if rows else None}
