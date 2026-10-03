from __future__ import annotations

import time
from typing import Any


class NeedsEngine:
    """Derive the Beast's live needs (0-100) from real platform signals (creature ideas 1 + 2).

    Four needs rise over hours and are eased by a real satisfying signal; heritage temperament
    shifts the rates (idea 2). A need whose driving signal is not present is reported *unavailable*
    (``None`` here, published with ``quality="unavailable"`` by Core) rather than a fabricated
    number (ADR-0008). Needs are session-live for now -- they start easing from boot; cross-restart
    persistence is a planned follow-up. This engine never changes Pwnagotchi behaviour; it only
    interprets observed state.

    Published under the ``needs.*`` namespace (each an int 0-100, or unavailable):

    - ``needs.curiosity_hunger`` -- time since a lifetime-first discovery (novelty); eased only by
      genuinely new networks/vendors, so re-seeing the same ones cannot fake it.
    - ``needs.restlessness`` -- time since real GPS movement ("walkies"); unavailable without GPS.
    - ``needs.loneliness`` -- time since the last peer encounter (PeerDex).
    - ``needs.tiredness`` -- accumulates under heat / throttling / low battery (and, at night, for
      non-nocturnal Beasts), and recovers when cool. Neglect should make a Beast sleepy, never
      damaged.
    """

    RISE_SEC = 4 * 3600.0        # neutral time for a time-based need to climb 0 -> 100
    TIRED_RISE_SEC = 2 * 3600.0  # full-swing of the tiredness integrator under sustained stress
    TIRED_FALL_SEC = 1 * 3600.0  # recovery time when conditions are good

    def __init__(self, state, clock=time.monotonic) -> None:
        self.state = state
        self.clock = clock
        now = clock()
        self._novelty_val: float | None = None
        self._novelty_t = now
        self._move_val: float | None = None
        self._move_t = now
        self._peer_val: float | None = None
        self._peer_t = now
        self._tired = 0.0
        self._last_tick = now

    def _num(self, key: str) -> float | None:
        v = self.state.get(key, None)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _temp(self, axis: str) -> float:
        # Heritage temperament (0..100); absent/unavailable -> neutral 50 for the internal rate math.
        v = self.state.get('beast.temperament.' + axis, None)
        try:
            return max(0.0, min(100.0, float(v)))
        except (TypeError, ValueError):
            return 50.0

    @staticmethod
    def _rise(elapsed: float, rise_sec: float, rate: float) -> int:
        return int(max(0, min(100, round(100.0 * max(0.0, elapsed) * rate / rise_sec))))

    def tick(self) -> dict[str, Any]:
        now = self.clock()
        dt = max(0.0, now - self._last_tick)
        self._last_tick = now
        out: dict[str, Any] = {}

        # curiosity_hunger -- rises since the last lifetime-first discovery; eased by novelty.
        novelty = self._num('wifi.encounters.lifetime_unique')
        if novelty is None:
            novelty = self._num('progression.vendors.count')
        if novelty is None:
            out['needs.curiosity_hunger'] = None
        else:
            if self._novelty_val is None:
                self._novelty_val = novelty
            if novelty > self._novelty_val:
                self._novelty_val = novelty
                self._novelty_t = now
            rate = 0.5 + self._temp('curiosity') / 100.0  # curious Beasts hunger for novelty faster
            out['needs.curiosity_hunger'] = self._rise(now - self._novelty_t, self.RISE_SEC, rate)

        # restlessness -- rises since real movement; unknown (unavailable) without a GPS fix.
        gps_state = str(self.state.get('gps.state', 'unavailable') or 'unavailable')
        dist = self._num('gps.session_distance_m')
        if dist is None:
            dist = self._num('gps.trip_distance_m')
        if gps_state == 'unavailable' or dist is None:
            out['needs.restlessness'] = None
        else:
            if self._move_val is None:
                self._move_val = dist
            if dist > self._move_val + 1.0:  # >1 m of fresh travel counts as a walk
                self._move_val = dist
                self._move_t = now
            out['needs.restlessness'] = self._rise(now - self._move_t, self.RISE_SEC, 1.0)

        # loneliness -- rises since the last peer encounter; social Beasts feel it faster.
        peer = self._num('peerdex.last_seen_at')
        if peer is None:
            out['needs.loneliness'] = None
        else:
            if self._peer_val is None:
                self._peer_val = peer
            if peer > self._peer_val:
                self._peer_val = peer
                self._peer_t = now
            rate = 0.5 + self._temp('social') / 100.0
            out['needs.loneliness'] = self._rise(now - self._peer_t, self.RISE_SEC, rate)

        # tiredness -- integrates heat / throttle / low battery / night, recovers when good.
        temp_c = self._num('system.temp.cpu_c')
        batt = self._num('power.battery.percent_estimate')
        if temp_c is None and batt is None:
            out['needs.tiredness'] = None
        else:
            gov = str(self.state.get('governor.mode', 'FULL') or 'FULL')
            throttle = self.state.get('system.throttle.flags', None)
            phase = str(self.state.get('ambient.day_phase', 'day') or 'day')
            stress = 0.0
            if temp_c is not None:
                heat = max(0.0, (temp_c - 65.0) / 20.0)                 # 0 at 65C, 1 at 85C
                stress += heat * (1.5 - self._temp('boldness') / 100.0)  # bold Beasts tire less from heat
            if gov in {'REDUCED', 'SURVIVAL'}:
                stress += 0.5
            if throttle:
                stress += 0.3
            if batt is not None and batt < 25:
                stress += (25.0 - batt) / 25.0
            if phase in {'night', 'late_night'}:
                stress += (100.0 - self._temp('nocturnal')) / 100.0 * 0.5  # nocturnal Beasts resist night sleepiness
            if stress > 0:
                self._tired = min(100.0, self._tired + stress * 100.0 * dt / self.TIRED_RISE_SEC)
            else:
                self._tired = max(0.0, self._tired - 100.0 * dt / self.TIRED_FALL_SEC)
            out['needs.tiredness'] = int(round(self._tired))

        out['needs.source'] = 'derived_live'
        return out
