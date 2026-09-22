from __future__ import annotations

import os
import time
from collections import Counter
from pathlib import Path
from typing import Any


CAPTURE_EXTENSIONS={'.pcap','.pcapng','.22000','.16800','.hccapx','.cap'}


class RecordsEngine:
    """Low-frequency persistent record enrichment.

    High-rate RF data remains in RAM/state. This engine deliberately writes only
    on a slow cadence: enrich known encounter records and index capture files.
    That gives BeastDex/Capture Vault durable truth without treating the SD card
    like a telemetry scratchpad.
    """

    def __init__(self,state,store,clock=time.time,handshake_dir: str='/etc/pwnagotchi/handshakes') -> None:
        self.state=state;self.store=store;self.clock=clock;self.handshake_dir=Path(handshake_dir)

    def _gps(self) -> dict[str,Any] | None:
        if not self.state.get('gps.fix'):return None
        lat=self.state.get('gps.latitude');lon=self.state.get('gps.longitude')
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)):return None
        return {'latitude':float(lat),'longitude':float(lon),'accuracy_m':self.state.get('gps.accuracy_m')}

    def _captures_path(self) -> Path:
        raw=self.state.get('captures.directory')
        return Path(str(raw)) if raw else self.handshake_dir

    def tick(self) -> dict[str,Any]:
        now=float(self.clock());aps=self.state.get('wifi.aps') or []
        try:self.store.update_wifi_observations(aps,now,self._gps())
        except Exception:pass
        try:
            cap=self.store.index_capture_directory(self._captures_path(),now)
        except Exception:
            cap={'count':0,'bytes':0,'formats':{},'recent':[]}
        try:enc=self.store.encounter_summary(6)
        except Exception:enc={'total':0,'vendor_count':0,'recent':[]}
        return {
            'records.encounters.total':int(enc.get('total') or 0),
            'records.encounters.vendor_count':int(enc.get('vendor_count') or 0),
            'records.encounters.recent':enc.get('recent') or [],
            'captures.indexed_files':int(cap.get('count') or 0),
            'captures.storage_bytes':int(cap.get('bytes') or 0),
            'captures.formats':cap.get('formats') or {},
            'captures.recent':cap.get('recent') or [],
            'records.last_indexed_at':now,
        }
