from __future__ import annotations

import hashlib
import hmac
import json
import os
import struct
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RareMomentEngine:
    """Deterministic scarce-event scheduler.

    A per-device secret is generated once. HMAC(secret, year) deterministically
    creates 1-4 event windows for that calendar year. The schedule therefore
    exists even while Beast is powered off: if the device is not running during
    a window, that opportunity is simply missed.

    The public state intentionally never exposes future timestamps. This keeps
    rare moments discoverable rather than predictable from the normal UI.
    """

    def __init__(self, state, root: str = '/var/lib/beastagotchi/secrets') -> None:
        self.state = state
        self.root = Path(root)
        self.secret_path = self.root / 'rare_seed.bin'
        self.history_path = self.root / 'rare_history.json'
        self.ack_path = Path('/var/lib/beastagotchi/ui/rare_ack.json')
        self.secret = self._load_or_create_secret()
        self.history = self._load_history()
        self._last_second = None
        self._active_id = None
        self._omen_id = None
        self._publish_idle()

    def _load_or_create_secret(self) -> bytes:
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            data = self.secret_path.read_bytes()
            if len(data) >= 32:
                return data[:32]
        except Exception:
            pass
        data = os.urandom(32)
        fd, tmp = tempfile.mkstemp(prefix='.rare_seed.', dir=str(self.root))
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.secret_path)
        finally:
            try:
                if os.path.exists(tmp): os.unlink(tmp)
            except Exception:
                pass
        return data

    def _load_history(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.history_path.read_text())
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        return {'schema': 1, 'origin_at': time.time(), 'seen': [], 'missed': [], 'acknowledged': []}

    def _save_history(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix='.rare_history.', suffix='.json', dir=str(self.history_path.parent))
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(self.history, f, indent=2, sort_keys=True)
                f.write('\n')
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.history_path)
        finally:
            try:
                if os.path.exists(tmp): os.unlink(tmp)
            except Exception:
                pass

    @staticmethod
    def _year_bounds(year: int) -> tuple[int, int]:
        start = int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp())
        end = int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp())
        return start, end

    def schedule_for_year(self, year: int) -> list[dict[str, Any]]:
        digest = hmac.new(self.secret, f'beast-rare:{year}'.encode(), hashlib.sha256).digest()
        count = 1 + digest[0] % 4
        start, end = self._year_bounds(year)
        span = max(1, end - start)
        rows: list[dict[str, Any]] = []
        for idx in range(count):
            block = hmac.new(self.secret, f'beast-rare:{year}:{idx}'.encode(), hashlib.sha256).digest()
            raw = struct.unpack('>Q', block[:8])[0]
            # Keep events away from exact year boundaries and spread them over
            # nearly the full calendar year.
            margin = 3 * 24 * 3600
            usable = max(1, span - margin * 2)
            ts = start + margin + (raw % usable)
            rarity_roll = block[10]
            rarity = 'mythic' if rarity_roll >= 248 else 'legendary' if rarity_roll >= 220 else 'epic' if rarity_roll >= 170 else 'rare'
            # Duration grows with rarity.  Common scarce events are brief flashes;
            # mythic ones are allowed to become genuine 30-60 second cinematics.
            duration_ranges={'rare':(6,11),'epic':(10,19),'legendary':(18,31),'mythic':(30,61)}
            lo,hi=duration_ranges[rarity]
            duration = lo + (block[8] % max(1,hi-lo))
            omen_ranges={'rare':(12,28),'epic':(18,38),'legendary':(25,50),'mythic':(35,75)}
            olo,ohi=omen_ranges[rarity]
            omen_lead = olo + (block[9] % max(1,ohi-olo))
            sigil = ['veil','eye','spiral','gate','constellation','cipher'][block[11] % 6]
            presentations={
                'rare':['fade','drift','cross'],
                'epic':['drift','orbit','ghost','cross'],
                'legendary':['ghost','orbit','storm','apparition'],
                'mythic':['apparition','storm','cinematic'],
            }[rarity]
            presentation=presentations[block[13] % len(presentations)]
            rows.append({
                'id': f'{year}-{idx+1}-{block[12:16].hex()}',
                'start': int(ts), 'duration': int(duration), 'omen_lead': int(omen_lead),
                'rarity': rarity, 'sigil': sigil, 'presentation': presentation,
            })
        rows.sort(key=lambda r: r['start'])
        return rows

    def _publish_idle(self) -> None:
        self.state.update_many('rare', {
            'rare.engine.ready': True,
            'rare.omen.active': False,
            'rare.moment.active': False,
            'rare.moment.id': None,
            'rare.moment.rarity': None,
            'rare.moment.sigil': None,
            'rare.moment.presentation': None,
            'rare.moment.remaining_sec': 0,
            'rare.seen_count': len(self.history.get('seen') or []),
            'rare.acknowledged_count': len(self.history.get('acknowledged') or []),
            'rare.missed_count': len(self.history.get('missed') or []),
        }, priority=89)

    def _acknowledgement(self, event_id: str) -> bool:
        try:
            obj = json.loads(self.ack_path.read_text())
            if str(obj.get('event_id') or '') != event_id:
                return False
            # Acknowledge only fresh taps written by the UI.
            ts = float(obj.get('ts') or 0)
            return abs(time.time() - ts) <= 90
        except Exception:
            return False

    def tick(self, now: float | None = None) -> list[tuple[str, str, dict[str, Any], str]]:
        now = float(now if now is not None else time.time())
        sec = int(now)
        if self._last_second == sec:
            return []
        self._last_second = sec
        year = datetime.fromtimestamp(now, tz=timezone.utc).year
        rows = self.schedule_for_year(year)
        out: list[tuple[str, str, dict[str, Any], str]] = []
        # If Beast was powered off through an eligible slot, it is recorded as
        # missed on the next boot. Slots before this installation's rare-engine
        # origin are ignored rather than retroactively counted as misses.
        origin=float(self.history.get('origin_at') or now)
        origin_year=datetime.fromtimestamp(origin,tz=timezone.utc).year
        seen=set(self.history.get('seen') or []); missed=set(self.history.get('missed') or [])
        changed_history=False
        for yy in range(origin_year, year+1):
            for row in self.schedule_for_year(yy):
                eid=row['id']; end=float(row['start'])+float(row['duration'])
                if float(row['start']) >= origin and end < now and eid not in seen and eid not in missed:
                    self.history.setdefault('missed', []).append(eid); missed.add(eid); changed_history=True
        if changed_history:self._save_history()
        active = None
        omen = None
        for row in rows:
            start = float(row['start']); end = start + float(row['duration'])
            if start <= now < end:
                active = row; break
            if start - float(row['omen_lead']) <= now < start:
                omen = row; break

        if active:
            eid = active['id']
            if eid not in set(self.history.get('seen') or []):
                self.history.setdefault('seen', []).append(eid); self._save_history()
                out.append(('rare.moment.started','rare',{'id':eid,'rarity':active['rarity'],'sigil':active['sigil'],'presentation':active['presentation'],'duration':active['duration']},'info'))
            if self._acknowledgement(eid) and eid not in set(self.history.get('acknowledged') or []):
                self.history.setdefault('acknowledged', []).append(eid); self._save_history()
                out.append(('rare.moment.acknowledged','rare',{'id':eid,'rarity':active['rarity'],'sigil':active['sigil'],'presentation':active['presentation']},'info'))
            self._active_id = eid; self._omen_id = None
            self.state.update_many('rare', {
                'rare.omen.active': False,
                'rare.moment.active': True,
                'rare.moment.id': eid,
                'rare.moment.rarity': active['rarity'],
                'rare.moment.sigil': active['sigil'],
                'rare.moment.presentation': active['presentation'],
                'rare.moment.remaining_sec': max(0, int(active['start'] + active['duration'] - now)),
                'rare.seen_count': len(self.history.get('seen') or []),
                'rare.acknowledged_count': len(self.history.get('acknowledged') or []),
                'rare.missed_count': len(self.history.get('missed') or []),
            }, priority=89)
        elif omen:
            eid = omen['id']
            if self._omen_id != eid:
                out.append(('rare.omen.started','rare',{'id':eid,'rarity':omen['rarity'],'sigil':omen['sigil'],'presentation':omen['presentation']},'info'))
            self._omen_id=eid; self._active_id=None
            self.state.update_many('rare', {
                'rare.omen.active': True,
                'rare.moment.active': False,
                'rare.moment.id': eid,
                'rare.moment.rarity': omen['rarity'],
                'rare.moment.sigil': omen['sigil'],
                'rare.moment.presentation': omen['presentation'],
                'rare.moment.remaining_sec': max(0, int(omen['start'] - now)),
                'rare.seen_count': len(self.history.get('seen') or []),
                'rare.acknowledged_count': len(self.history.get('acknowledged') or []),
                'rare.missed_count': len(self.history.get('missed') or []),
            }, priority=89)
        else:
            if self._active_id:
                out.append(('rare.moment.ended','rare',{'id':self._active_id},'info'))
            self._active_id=None; self._omen_id=None
            self._publish_idle()

        return out
