from __future__ import annotations

import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any


STAGES = [
    (1, 'Hatchling'),
    (5, 'Cub'),
    (10, 'Scout'),
    (20, 'Tracker'),
    (35, 'Hunter'),
    (50, 'Beast'),
    (70, 'Alpha'),
    (85, 'Apex'),
    (100, 'Monstergotchi'),
]

AURAS = [
    (0, 'none'),
    (10, 'static'),
    (25, 'spark'),
    (50, 'electric'),
    (100, 'inferno'),
    (200, 'apex'),
]


ACHIEVEMENT_DEFS = {
    # id: (label, bonus_xp, rarity)
    'first_signal': ('First Signal', 10, 'common'),
    'signals_10': ('Ten Signals', 10, 'common'),
    'signal_scout': ('Signal Scout', 25, 'common'),
    'signals_50': ('Signal Gatherer', 35, 'uncommon'),
    'signal_tracker': ('Signal Tracker', 75, 'uncommon'),
    'signals_250': ('Quarter Thousand', 120, 'rare'),
    'signal_hunter': ('Signal Hunter', 200, 'rare'),
    'signals_1000': ('Four Digits', 350, 'epic'),
    'signals_2500': ('Signal Cartographer', 500, 'epic'),
    'signals_5000': ('RF Naturalist', 750, 'legendary'),
    'signals_10000': ('Ten Thousand Voices', 1500, 'mythic'),
    'first_vendor': ('Species Discovered', 10, 'common'),
    'vendors_10': ('Vendor Sampler', 25, 'common'),
    'vendor_collector': ('Vendor Collector', 50, 'uncommon'),
    'vendors_50': ('Silicon Menagerie', 100, 'rare'),
    'vendors_100': ('BeastDex Scholar', 250, 'epic'),
    'vendors_250': ('World of Makers', 500, 'legendary'),
    'first_gps_lock': ('Found My Place', 10, 'common'),
    'gps_10': ('Ten Locks', 25, 'uncommon'),
    'gps_100': ('Always Knows the Way', 125, 'rare'),
    'first_capture': ('First Capture', 15, 'common'),
    'captures_10': ('Capture Apprentice', 35, 'uncommon'),
    'captures_50': ('Capture Archivist', 100, 'rare'),
    'captures_250': ('Vault Keeper', 350, 'epic'),
    'runtime_hour': ('One Hour Awake', 20, 'common'),
    'runtime_10h': ('Long Day', 50, 'uncommon'),
    'runtime_100h': ('Always Watching', 200, 'rare'),
    'runtime_500h': ('Old Soul', 500, 'epic'),
    'runtime_1000h': ('Ancient Process', 1000, 'legendary'),
    'level_5': ('Cub', 15, 'common'),
    'level_10': ('Scout', 25, 'common'),
    'level_20': ('Tracker', 50, 'uncommon'),
    'level_35': ('Hunter', 100, 'rare'),
    'level_50': ('Beast', 200, 'epic'),
    'level_70': ('Alpha', 350, 'epic'),
    'level_85': ('Apex', 600, 'legendary'),
    'level_100': ('Monstergotchi', 1500, 'mythic'),
    'rare_witness': ('I Saw It', 250, 'legendary'),
}

RARITY_ORDER = ['common','uncommon','rare','epic','legendary','mythic']


ACHIEVEMENT_META = {
    # key: category, metric, target, description, hidden-until-unlocked
    'first_signal': ('signals','lifetime_new_aps',1,'Discover a lifetime-first access point.',False),
    'signals_10': ('signals','lifetime_new_aps',10,'Discover 10 lifetime-first access points.',False),
    'signal_scout': ('signals','lifetime_new_aps',25,'Discover 25 lifetime-first access points.',False),
    'signals_50': ('signals','lifetime_new_aps',50,'Discover 50 lifetime-first access points.',False),
    'signal_tracker': ('signals','lifetime_new_aps',100,'Discover 100 lifetime-first access points.',False),
    'signals_250': ('signals','lifetime_new_aps',250,'Discover 250 lifetime-first access points.',False),
    'signal_hunter': ('signals','lifetime_new_aps',500,'Discover 500 lifetime-first access points.',False),
    'signals_1000': ('signals','lifetime_new_aps',1000,'Discover 1,000 lifetime-first access points.',False),
    'signals_2500': ('signals','lifetime_new_aps',2500,'Discover 2,500 lifetime-first access points.',False),
    'signals_5000': ('signals','lifetime_new_aps',5000,'Discover 5,000 lifetime-first access points.',False),
    'signals_10000': ('signals','lifetime_new_aps',10000,'Discover 10,000 lifetime-first access points.',False),
    'first_vendor': ('vendors','vendors',1,'Identify your first hardware vendor.',False),
    'vendors_10': ('vendors','vendors',10,'Identify 10 unique hardware vendors.',False),
    'vendor_collector': ('vendors','vendors',25,'Identify 25 unique hardware vendors.',False),
    'vendors_50': ('vendors','vendors',50,'Identify 50 unique hardware vendors.',False),
    'vendors_100': ('vendors','vendors',100,'Identify 100 unique hardware vendors.',False),
    'vendors_250': ('vendors','vendors',250,'Identify 250 unique hardware vendors.',False),
    'first_gps_lock': ('navigation','gps_locks',1,'Acquire your first GPS lock.',False),
    'gps_10': ('navigation','gps_locks',10,'Acquire 10 GPS locks.',False),
    'gps_100': ('navigation','gps_locks',100,'Acquire 100 GPS locks.',False),
    'first_capture': ('captures','handshakes',1,'Catalog your first capture.',False),
    'captures_10': ('captures','handshakes',10,'Catalog 10 captures.',False),
    'captures_50': ('captures','handshakes',50,'Catalog 50 captures.',False),
    'captures_250': ('captures','handshakes',250,'Catalog 250 captures.',False),
    'runtime_hour': ('runtime','runtime_sec',3600,'Remain awake for one lifetime hour.',False),
    'runtime_10h': ('runtime','runtime_sec',36000,'Accumulate 10 hours of runtime.',False),
    'runtime_100h': ('runtime','runtime_sec',360000,'Accumulate 100 hours of runtime.',False),
    'runtime_500h': ('runtime','runtime_sec',1800000,'Accumulate 500 hours of runtime.',False),
    'runtime_1000h': ('runtime','runtime_sec',3600000,'Accumulate 1,000 hours of runtime.',False),
    'level_5': ('evolution','level',5,'Reach evolution level 5.',False),
    'level_10': ('evolution','level',10,'Reach evolution level 10.',False),
    'level_20': ('evolution','level',20,'Reach evolution level 20.',False),
    'level_35': ('evolution','level',35,'Reach evolution level 35.',False),
    'level_50': ('evolution','level',50,'Reach evolution level 50.',False),
    'level_70': ('evolution','level',70,'Reach evolution level 70.',False),
    'level_85': ('evolution','level',85,'Reach evolution level 85.',False),
    'level_100': ('evolution','level',100,'Reach the Monstergotchi cap.',False),
    'rare_witness': ('secrets','rare_witness',1,'Witness and acknowledge a scarce Rare Moment.',True),
}




def xp_threshold(level: int) -> int:
    """Cumulative XP required to reach a level.

    Level 100 is deliberately finite (~70k XP) so the end-goal is long-term but
    obtainable. Cosmetics/collections/records continue after the cap.
    """
    level = max(1, min(100, int(level)))
    if level <= 1:
        return 0
    return int(round(45.0 * ((level - 1) ** 1.60)))


def level_for_xp(xp: int) -> int:
    xp = max(0, int(xp))
    lo, hi = 1, 100
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if xp_threshold(mid) <= xp:
            lo = mid
        else:
            hi = mid - 1
    return lo


def stage_for_level(level: int) -> str:
    stage = STAGES[0][1]
    for threshold, name in STAGES:
        if level >= threshold:
            stage = name
    return stage


def aura_for_session_unique(count: int) -> str:
    aura = AURAS[0][1]
    for threshold, name in AURAS:
        if count >= threshold:
            aura = name
    return aura


class ProgressionEngine:
    """Persistent, cosmetic progression derived from safe Beast activity.

    The engine never changes RF behavior. It only tracks identity/progression and
    publishes state/events used by the UI. It intentionally rewards exploration,
    longevity, first-time vendor discoveries, GPS locks and cataloged captures far
    more than any active behavior.
    """

    def __init__(self, state, path: str = '/var/lib/beastagotchi/profile.json') -> None:
        self.state = state
        self.path = Path(path)
        self._last_tick = time.monotonic()
        self._runtime_dirty = 0.0
        self.profile = self._load()
        self._publish_state()

    @staticmethod
    def _default_profile() -> dict[str, Any]:
        now = time.time()
        return {
            'schema': 1,
            'created_at': now,
            'updated_at': now,
            'xp': 0,
            'max_level': 100,
            'lifetime_runtime_sec': 0.0,
            'runtime_award_remainder_sec': 0.0,
            'seen_vendors': [],
            'achievements': [],
            'last_achievement': None,
            'counters': {
                'lifetime_new_aps': 0,
                'vendors': 0,
                'gps_locks': 0,
                'handshakes': 0,
                'runtime_awards': 0,
            },
        }

    def _load(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.path.read_text())
            if not isinstance(obj, dict):
                raise ValueError('profile is not an object')
        except Exception:
            obj = self._default_profile()
        base = self._default_profile()
        base.update(obj)
        if not isinstance(base.get('counters'), dict):
            base['counters'] = self._default_profile()['counters']
        else:
            c = self._default_profile()['counters']
            c.update(base['counters'])
            base['counters'] = c
        base['seen_vendors'] = list(dict.fromkeys(str(v) for v in (base.get('seen_vendors') or []) if str(v).strip()))
        base['achievements'] = list(dict.fromkeys(str(v) for v in (base.get('achievements') or []) if str(v).strip()))
        return base

    def _save(self) -> None:
        self.profile['updated_at'] = time.time()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix='.profile.', suffix='.json', dir=str(self.path.parent))
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(self.profile, f, indent=2, sort_keys=True)
                f.write('\n')
            os.replace(tmp, self.path)
        finally:
            try:
                if os.path.exists(tmp): os.unlink(tmp)
            except Exception:
                pass

    def _metric_value(self, metric: str, level: int) -> float:
        c = self.profile.get('counters') or {}
        if metric == 'vendors': return float(len(self.profile.get('seen_vendors') or []))
        if metric == 'runtime_sec': return float(self.profile.get('lifetime_runtime_sec') or 0.0)
        if metric == 'level': return float(level)
        if metric == 'rare_witness': return 1.0 if 'rare_witness' in set(self.profile.get('achievements') or []) else 0.0
        return float(c.get(metric) or 0.0)

    def _achievement_catalog(self, level: int) -> list[dict[str, Any]]:
        unlocked=set(self.profile.get('achievements') or [])
        rows=[]
        for key,(label,bonus,rarity) in ACHIEVEMENT_DEFS.items():
            category,metric,target,description,hidden=ACHIEVEMENT_META.get(key,('misc','',1,'',False))
            current=self._metric_value(metric,level)
            pct=100.0 if target<=0 else max(0.0,min(100.0,current*100.0/float(target)))
            is_unlocked=key in unlocked
            rows.append({
                'id':key,
                'label':label if (is_unlocked or not hidden) else '???',
                'real_label':label,
                'rarity':rarity,
                'category':category,
                'metric':metric,
                'current':round(current,1),
                'target':target,
                'progress_pct':round(pct,1),
                'unlocked':is_unlocked,
                'hidden':bool(hidden),
                'bonus_xp':bonus,
                'description':description if (is_unlocked or not hidden) else 'A hidden condition has not yet been witnessed.',
            })
        return rows

    def _award_catalog(self, level: int, session_unique: int) -> list[dict[str, Any]]:
        rows=[]
        for threshold,name in STAGES:
            rows.append({
                'id':f'stage_{threshold}', 'kind':'evolution', 'label':name,
                'current':level, 'target':threshold, 'unlocked':level>=threshold,
                'progress_pct':round(max(0.0,min(100.0,level*100.0/max(1,threshold))),1),
                'description':f'Evolution title earned at level {threshold}.',
            })
        for threshold,name in AURAS[1:]:
            rows.append({
                'id':f'aura_{threshold}', 'kind':'session_aura', 'label':name.title()+' Aura',
                'current':session_unique, 'target':threshold, 'unlocked':session_unique>=threshold,
                'progress_pct':round(max(0.0,min(100.0,session_unique*100.0/max(1,threshold))),1),
                'description':f'Session aura reached at {threshold} unique discoveries in one Beast session.',
            })
        return rows

    def _state_values(self) -> dict[str, Any]:
        xp = max(0, int(self.profile.get('xp') or 0))
        level = level_for_xp(xp)
        current = xp_threshold(level)
        nxt = xp_threshold(min(100, level + 1))
        if level >= 100:
            pct = 100.0
            next_needed = 0
        else:
            span = max(1, nxt - current)
            pct = max(0.0, min(100.0, (xp - current) * 100.0 / span))
            next_needed = max(0, nxt - xp)
        session_unique = self.state.get('wifi.encounters.session_unique', 0)
        try: session_unique_i = int(session_unique or 0)
        except Exception: session_unique_i = 0
        aura = aura_for_session_unique(session_unique_i)
        return {
            'progression.level': level,
            'progression.max_level': 100,
            'progression.xp': xp,
            'progression.xp_current_level': max(0, xp - current),
            'progression.xp_next_level': next_needed,
            'progression.level_progress_pct': round(pct, 2),
            'progression.stage': stage_for_level(level),
            'progression.aura': aura,
            'progression.session_unique': session_unique_i,
            'progression.achievements.count': len(self.profile.get('achievements') or []),
            'progression.achievements.catalog_count': len(ACHIEVEMENT_DEFS),
            'progression.achievements.unlocked_ids': list(self.profile.get('achievements') or []),
            'progression.achievements.unlocked': [
                {'id':k,'label':ACHIEVEMENT_DEFS[k][0],'rarity':ACHIEVEMENT_DEFS[k][2]}
                for k in (self.profile.get('achievements') or []) if k in ACHIEVEMENT_DEFS
            ][-24:],
            'progression.achievements.catalog': self._achievement_catalog(level),
            'progression.achievements.rarity_counts': {
                r: sum(1 for k in (self.profile.get('achievements') or []) if k in ACHIEVEMENT_DEFS and ACHIEVEMENT_DEFS[k][2] == r)
                for r in RARITY_ORDER
            },
            'progression.awards.catalog': self._award_catalog(level, session_unique_i),
            'progression.awards.count': sum(1 for row in self._award_catalog(level, session_unique_i) if row.get('unlocked')),
            'progression.achievement.last': self.profile.get('last_achievement'),
            'progression.vendors.count': len(self.profile.get('seen_vendors') or []),
            'progression.lifetime_runtime_sec': round(float(self.profile.get('lifetime_runtime_sec') or 0.0), 1),
            'progression.profile_path': str(self.path),
        }

    def _publish_state(self) -> None:
        self.state.update_many('progression', self._state_values(), priority=88)

    def _award(self, amount: int, reason: str) -> list[tuple[str, str, dict[str, Any], str]]:
        amount = max(0, int(amount))
        if amount <= 0:
            return []
        before_level = level_for_xp(int(self.profile.get('xp') or 0))
        before_stage = stage_for_level(before_level)
        self.profile['xp'] = int(self.profile.get('xp') or 0) + amount
        after_level = level_for_xp(int(self.profile['xp']))
        after_stage = stage_for_level(after_level)
        self._save(); self._publish_state()
        out: list[tuple[str, str, dict[str, Any], str]] = [
            ('progression.xp_awarded', 'progression', {'amount': amount, 'reason': reason, 'xp': self.profile['xp']}, 'info')
        ]
        if after_level > before_level:
            out.append(('progression.level_up', 'progression', {
                'from': before_level, 'to': after_level, 'stage': after_stage, 'xp': self.profile['xp']
            }, 'info'))
        if after_stage != before_stage:
            out.append(('progression.stage_changed', 'progression', {
                'from': before_stage, 'to': after_stage, 'level': after_level
            }, 'info'))
        return out

    def _unlock_achievement(self, key: str) -> list[tuple[str, str, dict[str, Any], str]]:
        if key in set(self.profile.get('achievements') or []):
            return []
        label, bonus, rarity = ACHIEVEMENT_DEFS[key]
        self.profile.setdefault('achievements', []).append(key)
        self.profile['achievements'] = list(dict.fromkeys(self.profile['achievements']))
        self.profile['last_achievement'] = label
        self._save(); self._publish_state()
        out: list[tuple[str, str, dict[str, Any], str]] = [
            ('progression.achievement_unlocked', 'progression', {
                'id': key, 'label': label, 'bonus_xp': bonus, 'rarity': rarity,
                'count': len(self.profile.get('achievements') or []),
            }, 'info')
        ]
        if bonus:
            out.extend(self._award(bonus, f'achievement: {label}'))
        return out

    def _check_achievements(self) -> list[tuple[str, str, dict[str, Any], str]]:
        c = self.profile.get('counters') or {}
        level = level_for_xp(int(self.profile.get('xp') or 0))
        apn = int(c.get('lifetime_new_aps') or 0)
        vendors = len(self.profile.get('seen_vendors') or [])
        gps = int(c.get('gps_locks') or 0)
        caps = int(c.get('handshakes') or 0)
        runtime = float(self.profile.get('lifetime_runtime_sec') or 0.0)
        checks = [
            ('first_signal', apn >= 1), ('signals_10', apn >= 10), ('signal_scout', apn >= 25),
            ('signals_50', apn >= 50), ('signal_tracker', apn >= 100), ('signals_250', apn >= 250),
            ('signal_hunter', apn >= 500), ('signals_1000', apn >= 1000), ('signals_2500', apn >= 2500),
            ('signals_5000', apn >= 5000), ('signals_10000', apn >= 10000),
            ('first_vendor', vendors >= 1), ('vendors_10', vendors >= 10), ('vendor_collector', vendors >= 25),
            ('vendors_50', vendors >= 50), ('vendors_100', vendors >= 100), ('vendors_250', vendors >= 250),
            ('first_gps_lock', gps >= 1), ('gps_10', gps >= 10), ('gps_100', gps >= 100),
            ('first_capture', caps >= 1), ('captures_10', caps >= 10), ('captures_50', caps >= 50), ('captures_250', caps >= 250),
            ('runtime_hour', runtime >= 3600), ('runtime_10h', runtime >= 36000), ('runtime_100h', runtime >= 360000),
            ('runtime_500h', runtime >= 1800000), ('runtime_1000h', runtime >= 3600000),
            ('level_5', level >= 5), ('level_10', level >= 10), ('level_20', level >= 20), ('level_35', level >= 35),
            ('level_50', level >= 50), ('level_70', level >= 70), ('level_85', level >= 85), ('level_100', level >= 100),
        ]
        out: list[tuple[str, str, dict[str, Any], str]] = []
        for key, ok in checks:
            if ok:
                out.extend(self._unlock_achievement(key))
        return out

    def on_event(self, ev) -> list[tuple[str, str, dict[str, Any], str]]:
        et = str(getattr(ev, 'type', '') or '')
        data = getattr(ev, 'data', {}) or {}
        out: list[tuple[str, str, dict[str, Any], str]] = []
        amount = 0; reason = ''

        if et == 'wifi.ap_discovered':
            # Only lifetime-first APs count for persistent XP; session repeats do not.
            try: new_lifetime = int(data.get('lifetime_new_count') or 0)
            except Exception: new_lifetime = 0
            if new_lifetime:
                self.profile['counters']['lifetime_new_aps'] = int(self.profile['counters'].get('lifetime_new_aps') or 0) + new_lifetime
                amount += new_lifetime
                reason = 'new APs'
            seen = set(self.profile.get('seen_vendors') or [])
            new_vendors = []
            for ap in data.get('aps') or []:
                if not isinstance(ap, dict): continue
                vendor = str(ap.get('vendor') or '').strip()
                if vendor and vendor not in seen:
                    seen.add(vendor); new_vendors.append(vendor)
            if new_vendors:
                self.profile['seen_vendors'] = sorted(seen)
                self.profile['counters']['vendors'] = len(seen)
                amount += len(new_vendors) * 8
                reason = 'new APs + vendor discoveries' if reason else 'vendor discoveries'
                out.append(('progression.vendor_discovered', 'progression', {'vendors': new_vendors[:12], 'count': len(new_vendors)}, 'info'))
        elif et == 'gps.lock_acquired':
            self.profile['counters']['gps_locks'] = int(self.profile['counters'].get('gps_locks') or 0) + 1
            amount, reason = 3, 'GPS lock'
        elif et == 'pwnagotchi.handshake':
            self.profile['counters']['handshakes'] = int(self.profile['counters'].get('handshakes') or 0) + 1
            amount, reason = 5, 'capture cataloged'
        elif et == 'rare.moment.acknowledged':
            out.extend(self._unlock_achievement('rare_witness'))

        if amount:
            # _award performs the durable save for all counter changes above.
            out.extend(self._award(amount, reason))
        elif out:
            self._save(); self._publish_state()
        out.extend(self._check_achievements())
        return out

    def tick(self) -> list[tuple[str, str, dict[str, Any], str]]:
        now = time.monotonic()
        delta = max(0.0, min(60.0, now - self._last_tick))
        self._last_tick = now
        self.profile['lifetime_runtime_sec'] = float(self.profile.get('lifetime_runtime_sec') or 0.0) + delta
        remainder = float(self.profile.get('runtime_award_remainder_sec') or 0.0) + delta
        awards = int(remainder // 600.0)
        self.profile['runtime_award_remainder_sec'] = remainder - awards * 600.0
        out: list[tuple[str, str, dict[str, Any], str]] = []
        if awards:
            self.profile['counters']['runtime_awards'] = int(self.profile['counters'].get('runtime_awards') or 0) + awards
            out.extend(self._award(awards, 'runtime milestone'))
        else:
            self._runtime_dirty += delta
            if self._runtime_dirty >= 60.0:
                self._runtime_dirty = 0.0
                self._save()
            self._publish_state()
        out.extend(self._check_achievements())
        return out
