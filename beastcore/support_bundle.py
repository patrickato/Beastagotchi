from __future__ import annotations

import hashlib
import json
import os
import platform
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any


_SAFE_PREFIXES=(
    'system.','health.','storage.','display.','governor.','performance.',
    'capabilities.','bluetooth.','containers.','desktop.','ai.',
    'pwnagotchi.service.','bettercap.state','bettercap.service.',
    'gps.service.','plugins.catalog_count','plugins.enabled_count',
    'plugins.integrated_count','plugins.display_conflict_count',
    'network.route.available','network.internet.state','library.',
    'incidents.open_count','backups.count','system.beast_version',
)


class SupportBundleManager:
    """Create a bounded, privacy-conscious support archive.

    The default bundle is designed to be shareable for troubleshooting: it
    intentionally omits exact AP/client lists, BSSID/SSID details, GPS
    coordinates, IP/MAC addresses, credentials and raw Pwnagotchi logs.
    """

    def __init__(self,state,store,root='/var/lib/beastagotchi/support',keep=3,clock=time.time) -> None:
        self.state=state;self.store=store;self.root=Path(root);self.keep=max(1,int(keep));self.clock=clock

    def plan(self) -> dict[str,Any]:
        return {
            'allowed':True,'operation':'support.bundle','destination':str(self.root),'retention':self.keep,
            'privacy':'sanitized','includes':['platform health/state summary','service/capability inventory','incident summaries','action/job summaries'],
            'excludes':['credentials','raw Pwnagotchi config','raw logs','SSIDs/BSSIDs/client IDs','GPS coordinates','IP/MAC addresses'],
            'warnings':['Review a support archive before sharing if you add custom documents to it later.'],
        }

    @staticmethod
    def _safe_state(snapshot: dict[str,Any]) -> dict[str,Any]:
        out={}
        for k,v in snapshot.items():
            key=str(k)
            if any(key==p or key.startswith(p) for p in _SAFE_PREFIXES):
                # Network interface objects can contain addresses/MACs; only the
                # explicit route/internet booleans above are selected.
                if key.startswith('capabilities.usb_devices'):
                    # USB descriptions/VID:PIDs are hardware identity, not user
                    # network identity, and are useful for support.
                    out[key]=v
                elif key.startswith('platform.'):
                    continue
                else:
                    out[key]=v
        return out

    @staticmethod
    def _incident_summary(rows: list[dict[str,Any]]) -> list[dict[str,Any]]:
        keys=('id','kind','severity','status','opened_at','last_seen','resolved_at','summary','detail')
        return [{k:r.get(k) for k in keys} for r in rows]

    @staticmethod
    def _action_summary(rows: list[dict[str,Any]]) -> list[dict[str,Any]]:
        keys=('id','ts','finished_at','actor','action','target','status')
        return [{k:r.get(k) for k in keys} for r in rows]

    @staticmethod
    def _job_summary(rows: list[dict[str,Any]]) -> list[dict[str,Any]]:
        keys=('id','kind','label','status','created_at','started_at','finished_at','progress','detail')
        return [{k:r.get(k) for k in keys} for r in rows]

    def create(self) -> dict[str,Any]:
        self.root.mkdir(parents=True,exist_ok=True)
        try:os.chmod(self.root,0o700)
        except Exception:pass
        now=float(self.clock());stamp=time.strftime('%Y%m%d-%H%M%S',time.localtime(now))
        dest=self.root/f'beast-support-{stamp}.tar.gz'
        snapshot=self.state.snapshot(False)
        with tempfile.TemporaryDirectory(prefix='beast-support-') as td:
            base=Path(td)/'beast-support';base.mkdir()
            manifest={
                'format':1,'created_at':now,'privacy':'sanitized','beast_version':snapshot.get('system.beast_version'),
                'hostname_omitted':True,'raw_logs_included':False,'network_identifiers_included':False,'gps_coordinates_included':False,
            }
            (base/'manifest.json').write_text(json.dumps(manifest,indent=2,default=str)+'\n')
            (base/'state.json').write_text(json.dumps(self._safe_state(snapshot),indent=2,default=str)+'\n')
            (base/'incidents.json').write_text(json.dumps(self._incident_summary(self.store.recent_incidents(50)),indent=2,default=str)+'\n')
            (base/'actions.json').write_text(json.dumps(self._action_summary(self.store.recent_actions(50)),indent=2,default=str)+'\n')
            (base/'jobs.json').write_text(json.dumps(self._job_summary(self.store.recent_jobs(50)),indent=2,default=str)+'\n')
            with tarfile.open(dest,'w:gz') as tf:tf.add(base,arcname='beast-support')
        os.chmod(dest,0o600)
        digest=hashlib.sha256(dest.read_bytes()).hexdigest()
        rows=sorted(self.root.glob('beast-support-*.tar.gz'),key=lambda p:p.stat().st_mtime,reverse=True)
        for old in rows[self.keep:]:
            try:old.unlink()
            except Exception:pass
        return {'ok':True,'path':str(dest),'name':dest.name,'size_bytes':dest.stat().st_size,'sha256':digest,'privacy':'sanitized','retention':self.keep}
