from __future__ import annotations

import time


class ReactionGovernor:
    """Select the most important recent visual reaction.

    Multiple events can land close together. Thermal/health faults must beat cosmetic
    celebrations; level-ups beat ordinary discoveries; ordinary discoveries beat idle.
    """

    PRIORITY = {
        'collector.error': 100,
        'system.health_changed': 95,
        'system.thermal_band': 90,
        'progression.stage_changed': 80,
        'progression.level_up': 75,
        'progression.achievement_unlocked': 68,
        'pwnagotchi.handshake': 70,
        'dock.changed': 55,
        'gps.lock_acquired': 45,
        'progression.vendor_discovered': 40,
        'wifi.ap_discovered': 25,
        'context.mode_changed': 20,
    }

    WINDOWS = {
        'collector.error': 6.0,
        'system.health_changed': 5.0,
        'system.thermal_band': 5.0,
        'progression.stage_changed': 7.0,
        'progression.level_up': 6.0,
        'progression.achievement_unlocked': 5.0,
        'pwnagotchi.handshake': 4.0,
        'dock.changed': 4.0,
        'gps.lock_acquired': 4.0,
        'progression.vendor_discovered': 4.0,
        'wifi.ap_discovered': 2.5,
        'context.mode_changed': 3.0,
    }

    def select(self, events: list[dict], now: float | None = None):
        now = float(now or time.time())
        candidates = []
        for ev in events or []:
            if not isinstance(ev, dict):
                continue
            typ = str(ev.get('type') or '')
            if typ not in self.PRIORITY:
                continue
            try: age = max(0.0, now - float(ev.get('ts') or 0.0))
            except Exception: continue
            window = self.WINDOWS.get(typ, 4.0)
            if age > window:
                continue
            data = ev.get('data') if isinstance(ev.get('data'), dict) else {}
            # A return to healthy/normal is informational, not an emergency.
            priority = self.PRIORITY[typ]
            if typ == 'system.health_changed' and data.get('to') == 'healthy': priority = 35
            if typ == 'system.thermal_band' and data.get('to') in {'normal','warm'}: priority = 30
            candidates.append((priority, -age, ev, window))
        if not candidates:
            return None
        candidates.sort(reverse=True, key=lambda row:(row[0],row[1]))
        priority, _, ev, window = candidates[0]
        age = max(0.0, now - float(ev.get('ts') or now))
        return {'event':ev, 'priority':priority, 'age':age, 'progress':max(0.0,1.0-age/window)}
