from __future__ import annotations

import math
import time
from typing import Any

_MOVING = frozenset({"walking", "moving", "wardrive"})  # real movement ContextEngine emits


class NeedsEngine:
    """Derive the Beast's live needs (0-100) from real platform signals (creature ideas 1 + 2).

    Four needs rise over hours and are eased by a real satisfying signal; heritage temperament
    shifts the rates (idea 2). A need whose driving signal is not present -- or whose driver has gone
    stale or unavailable -- is reported *unavailable* (``None`` here, published with
    ``quality="unavailable"`` by Core) rather than a fabricated number (ADR-0008). Needs reset when
    the active Beast changes. Given a Store, **tiredness persists across restarts and resumes where it was**
    (see ``_restore``) -- it is a self-contained 0..100 value. curiosity-hunger, loneliness and restlessness
    stay session-live: their cross-restart resume (and fading gently while powered off) needs a clock-robust,
    source-stable design and is deferred to #56. This engine never changes Pwnagotchi behaviour; it only
    interprets observed state.

    Published under the ``needs.*`` namespace (each an int 0-100, or unavailable):

    - ``needs.curiosity_hunger`` -- time since a lifetime-first discovery (novelty); eased only by
      genuinely new networks/vendors, so re-seeing the same ones cannot fake it.
    - ``needs.restlessness`` -- time since real movement (``context.motion.state``); unavailable
      without a usable GPS fix or when the GPS collector is stale.
    - ``needs.loneliness`` -- time since the last peer encounter (PeerDex).
    - ``needs.tiredness`` -- accumulates under heat / throttling / low battery / night and recovers
      when good; each driver counts only while its collector is live (ADR-0008). Neglect should make
      a Beast sleepy, never damaged.
    """

    RISE_SEC = 4 * 3600.0        # neutral time for a time-based need to climb 0 -> 100
    TIRED_RISE_SEC = 2 * 3600.0  # full-swing of the tiredness integrator under sustained stress
    TIRED_FALL_SEC = 1 * 3600.0  # recovery time when conditions are good
    SAVE_INTERVAL_SEC = 60.0     # throttle for persisting need state to the Store
    META_KEY = "needs.persistence"

    def __init__(self, state, clock=time.monotonic, store=None) -> None:
        self.state = state
        self.clock = clock              # monotonic: in-session rise/integration durations
        self.store = store              # optional Store (meta KV); None -> session-live, no persistence
        now = clock()
        # Seed the active-Beast id up front so a boot read-failure (which leaves _restore early) does not look
        # like an identity change on the first tick -- that would wrongly clear the read-fault flag and treat
        # the booted Beast as fresh instead of reporting its persisted need unavailable.
        self._beast_id: Any = self.state.get('progression.beast.id', None)
        self._last_tick = now
        self._last_save = now
        self._restore_failed = False     # a transient read error at boot -> suppress saves (preserve checkpoint)
        self._reset_session(now)
        if self.store is not None:
            self._restore(now)

    def _reset_session(self, now: float) -> None:
        # Session baselines/integrator. Reset on construction and whenever the active Beast changes,
        # so a newly activated Beast never inherits the previous one's elapsed time or fatigue.
        self._novelty_val: float | None = None
        self._novelty_t = now
        self._move_t = now
        self._peer_val: float | None = None
        self._peer_t = now
        self._tired = 0.0

    @staticmethod
    def _finite(x: Any) -> float | None:
        # A real, finite JSON number, or None for anything corrupt -- so a bad blob takes the fresh-session
        # fallback instead of reaching the tick-time float math. _persist only ever writes a JSON number, so:
        #   - reject a bool (float(True) == 1.0) and a non-number like a numeric string (float("90") == 90.0)
        #     by type before coercion -- bool is an int subclass, so exclude it explicitly and first;
        #   - NaN / inf are not finite -> None;
        #   - a huge int (e.g. a 400-digit JSON number) overflows float() -> OverflowError -> None.
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            return None
        try:
            v = float(x)
        except (TypeError, ValueError, OverflowError):
            return None
        return v if math.isfinite(v) else None

    def _restore(self, now: float) -> None:
        # Resume the *persisted* need where it was. Scope C persists only **tiredness** -- a self-contained
        # stored 0..100 value. curiosity-hunger, loneliness and restlessness stay session-live: curiosity's
        # baseline depends on which discovery counter sourced it and on agreeing with the live count across a
        # restart, so it joins loneliness (peer wall-clock) and restlessness (GPS) in the clock-robust,
        # source-stable cross-restart work deferred to #56. The blob is validated before any of it is applied,
        # so a corrupt / out-of-range / tampered one falls back to the fresh session rather than half-restoring
        # a fabricated value (ADR-0008).
        try:
            blob = self.store.get_meta_json(self.META_KEY, None)
        except Exception:
            # A transient read error (SQLite/FS hiccup) is NOT "no checkpoint". Flag it so the engine reports
            # the persisted need (tiredness) *unavailable* for this session and _persist does not overwrite the
            # real checkpoint with reset state. A checkpoint is applied only at construction, before any live
            # derivation; recovery waits for the next restart, which resumes cleanly from the preserved
            # checkpoint.
            self._restore_failed = True
            return
        self._restore_failed = False
        if not isinstance(blob, dict):
            return
        if "beast_id" not in blob or blob.get("beast_id") != self._beast_id:
            # The checkpoint must prove it belongs to the active Beast. A missing owner (no provenance) or a
            # different Beast's id takes the fresh-session fallback rather than bleeding another Beast's (or an
            # unattributable) fatigue into this one (ADR-0008). _beast_id was seeded from the active Beast.
            return
        tired = self._finite(blob.get("tired"))
        if tired is None:
            return  # tired is required and must be a finite JSON number -> reject the whole blob
        if not 0.0 <= tired <= 100.0:
            # tired is a 0..100 need level by definition (all _persist ever writes); a finite but out-of-range
            # value is corruption -> reject the whole blob rather than clamp it into a plausible 0/100, which
            # would fabricate a confident need from a bad record (ADR-0008).
            return
        self._tired = tired                               # validated to 0..100 above; owner matches above

    def _persist(self, now: float, *, strict: bool = False) -> None:
        if self.store is None:
            return
        if self._restore_failed:
            # We could not read the checkpoint at boot: do not overwrite it with this run's reset state
            # (a transient read error must not become permanent loss on the next 60s save).
            return
        try:
            self.store.set_meta_json(self.META_KEY, {
                "beast_id": self._beast_id,
                "tired": self._tired,
            })
        except Exception:
            # A periodic in-tick save swallows transient write errors so the loop never dies; the
            # explicit clean-shutdown save (strict) propagates so BeastCore.run() can log a real
            # failure instead of silently leaving a stale checkpoint.
            if strict:
                raise

    def save(self) -> None:
        """Flush need state to the Store now (e.g. on a clean shutdown); raises on a real write error."""
        self._persist(self.clock(), strict=True)

    def _live(self, key: str) -> Any:
        # Per-key live-truth: return the value only while the registry considers the key live. A key
        # marked stale (its collector stopped refreshing) or unavailable (a producer published it so)
        # reads as absent, so a derived need is never driven by data that is no longer true (ADR-0008).
        # Falls back to the plain value when the state exposes no metadata (e.g. tests).
        meta = getattr(self.state, 'meta', None)
        if callable(meta):
            m = meta(key)
            if m is not None and m.get('quality') in ('stale', 'unavailable'):
                return None
        return self.state.get(key, None)

    def _num(self, key: str) -> float | None:
        try:
            return float(self._live(key))
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
        # Cap elapsed at the saturation point (where the need already reads 100) before the multiply, so a
        # pathologically large age cannot overflow the product to inf and make round() raise OverflowError
        # (which would wedge the whole personality loop). Lossless: any age past saturation is already 100.
        rate = max(rate, 1e-9)
        elapsed = min(max(0.0, elapsed), rise_sec / rate)
        return int(max(0, min(100, round(100.0 * elapsed * rate / rise_sec))))

    def tick(self) -> dict[str, Any]:
        now = self.clock()
        dt = max(0.0, now - self._last_tick)
        self._last_tick = now
        out: dict[str, Any] = {}

        # Needs belong to the active Beast: reset the session baselines on an identity change so a
        # newly activated Beast does not inherit the previous Beast's novelty/peer timers or fatigue.
        beast_id = self.state.get('progression.beast.id', None)
        if beast_id != self._beast_id:
            self._beast_id = beast_id
            self._reset_session(now)
            # A boot read-fault belonged to the previously-active Beast; a newly activated Beast starts a
            # fresh, persistable session, so clear the flag rather than carrying the old fault into it.
            self._restore_failed = False

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

        # restlessness -- rises while the Beast stays put, eased by real movement. Driven by the
        # produced context.motion.state (there is no gps.*_distance producer). Unavailable without a
        # usable GPS fix (motion "unknown") or when the GPS collector is stale, so frozen motion from
        # a stalled collector cannot masquerade as "not moving" (ADR-0008).
        motion = str(self.state.get('context.motion.state', 'unknown') or 'unknown')
        # Only an actual fix is usable motion evidence: "unavailable"/"connected_no_fix" are live values
        # with no position, and a stale gps.state reads as "unknown" (per-key quality) -- neither is a fix.
        if motion == 'unknown' or str(self._live('gps.state') or 'unknown') != 'fixed':
            # Movement is unknowable now; re-baseline so a later recovery does not charge the whole
            # outage (e.g. a 4h GPS gap must not resume as an instant restlessness=100). restlessness is
            # session-live (not persisted), so there is no restored age to preserve here.
            self._move_t = now
            out['needs.restlessness'] = None
        else:
            if motion in _MOVING:
                self._move_t = now  # moving now -> restlessness eases to 0
            out['needs.restlessness'] = self._rise(now - self._move_t, self.RISE_SEC, 1.0)

        # loneliness -- rises since the last peer encounter; social Beasts feel it faster.
        # peerdex.last_seen_at is 0 on a fresh profile (sentinel for "no peer ever"), so <= 0 is
        # unavailable, not a real encounter at the epoch; re-baseline so the first real peer reads ~0.
        peer = self._num('peerdex.last_seen_at')
        if peer is None or peer <= 0:
            self._peer_t = now
            out['needs.loneliness'] = None
        else:
            if self._peer_val is None:
                self._peer_val = peer
            if peer > self._peer_val:
                self._peer_val = peer
                self._peer_t = now
            rate = 0.5 + self._temp('social') / 100.0
            out['needs.loneliness'] = self._rise(now - self._peer_t, self.RISE_SEC, rate)

        # tiredness -- integrates heat / throttle / low battery / night, recovers when good. Each
        # input counts only while its collector is live and telemetry is available, so a stale CPU
        # temperature, a retained battery % from a dropped UPS, or the normal "0x0" throttle string
        # cannot drive apparently-live fatigue (ADR-0008).
        temp_c = self._num('system.temp.cpu_c')        # _num already drops a stale/unavailable reading
        batt = self._num('power.battery.percent_estimate')
        # system.throttle.flags goes stale with the system collector; use it as the liveness proxy for
        # the governor-derived stress below (the governor itself re-publishes those keys as live).
        sys_live = self._live('system.throttle.flags') is not None
        use_temp = temp_c is not None
        batt_available = bool(self.state.get('power.telemetry.available', True))
        use_batt = batt is not None and batt_available
        if not use_temp and not use_batt:
            out['needs.tiredness'] = None
        else:
            gov = str(self.state.get('governor.mode', 'FULL') or 'FULL')
            # governor.throttle_current is the parsed throttle bit; the raw system.throttle.flags is
            # a string ("0x0" when NOT throttled) that would be truthy and accrue fatigue forever.
            throttled = bool(self.state.get('governor.throttle_current', False))
            phase = str(self.state.get('ambient.day_phase', 'day') or 'day')
            stress = 0.0
            if use_temp:
                heat = max(0.0, (temp_c - 65.0) / 20.0)                  # 0 at 65C, 1 at 85C
                stress += heat * (1.5 - self._temp('boldness') / 100.0)  # bold Beasts tire less from heat
            # governor mode / throttle both derive from system telemetry; the governor refreshes them
            # every second so they never look stale themselves -- gate on the system collector instead,
            # or a throttle that has ended keeps tiring the Beast off stale data (ADR-0008).
            if sys_live and gov in {'REDUCED', 'SURVIVAL'}:
                stress += 0.5
            if sys_live and throttled:
                stress += 0.3
            if use_batt and batt < 25:
                stress += (25.0 - batt) / 25.0
            if phase in {'night', 'late_night'}:
                stress += (100.0 - self._temp('nocturnal')) / 100.0 * 0.5  # nocturnal Beasts resist night sleepiness
            if stress > 0:
                self._tired = min(100.0, self._tired + stress * 100.0 * dt / self.TIRED_RISE_SEC)
            else:
                self._tired = max(0.0, self._tired - 100.0 * dt / self.TIRED_FALL_SEC)
            out['needs.tiredness'] = int(round(self._tired))

        if self._restore_failed:
            # The tiredness checkpoint was unreadable at boot: its value is unknown for this session, so report
            # tiredness unavailable rather than a confident fresh value (ADR-0008); the next restart resumes
            # from the preserved checkpoint. The session-live needs (curiosity-hunger, restlessness,
            # loneliness) are derived fresh and unaffected.
            out['needs.tiredness'] = None
        out['needs.source'] = 'derived_live'
        if self.store is not None and (now - self._last_save) >= self.SAVE_INTERVAL_SEC:
            self._persist(now)
            self._last_save = now
        return out
