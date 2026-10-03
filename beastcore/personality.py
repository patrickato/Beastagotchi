from __future__ import annotations

import time
from typing import Any

# --- Mood thresholds (seconds unless noted) -------------------------------------------------
TIRED_MOOD = 65               # needs.tiredness at/above this -> the Beast looks sleepy
HUNGRY_MOOD = 60              # needs.curiosity_hunger at/above this -> curious
RESTLESS_MOOD = 60           # needs.restlessness / needs.loneliness at/above this -> bored
NOVELTY_RECENT_SEC = 60.0    # "just found a genuinely new network" -> hunting (while on the move)
NOVELTY_WARM_SEC = 120.0     # recently found something new -> curious (fallback when no needs)
QUIET_SLEEPY_SEC = 600.0     # fallback: quiet this long at night -> sleepy (tiredness unavailable)
QUIET_BORED_SEC = 900.0      # fallback: quiet this long -> bored (needs unavailable)
CAPTURE_CELEBRATE_SEC = 60.0  # celebrate for this long after a genuinely new capture
CAPTURE_MAX_DELTA = 10        # a live capture adds a few handshakes per tick; a larger jump is the
                              # capture source mounting/recovering, not a capture happening now
DWELL_MIN_SEC = 10.0         # a non-urgent mood is held at least this long (hysteresis) ...
DWELL_FOCUS_SEC = 20.0       # ... plus up to this much more at maximum focus temperament (-> ~30 s)

MOTION_ACTIVE = frozenset({"walking", "moving", "wardrive"})      # real movement the collector emits
URGENT_MOODS = frozenset({"fault", "overheated", "celebrating"})  # always preempt the hysteresis hold

# Base expressed scalars per mood: (energy, focus, curiosity). idle's energy is CPU-derived below.
_MOOD_SCALARS = {
    "fault":         (20, 95, 10),
    "overheated":    (25, 80, 10),
    "celebrating":   (95, 70, 80),
    "hunting":       (80, 85, 90),
    "gps-searching": (65, 85, 70),
    "curious":       (70, 65, 90),
    "sleepy":        (25, 30, 25),
    "bored":         (40, 35, 45),
    "idle":          (70, 50, 55),
}


class PersonalityEngine:
    """Derive canonical Beast personality state from real platform conditions.

    This engine never changes Pwnagotchi behaviour. It turns observed state into a consistent
    experiential vocabulary that themes/face packs may render.

    Mood derivation (finding F1): the mood used to be an if-chain over a few instantaneous signals
    whose gates were effectively stuck, so the Beast sat in one or two moods forever --

    * ``quiet`` reset on *any* ``wifi.ap_count`` drift, so it was almost always ~0;
    * ``hunting`` / ``gps-searching`` were gated on ``expedition.active``, which ``ExpeditionEngine``
      holds permanently ``True``;
    * ``celebrating`` keyed on ``semantic.capture.recent``, which nothing publishes (dead); and
    * ``gps-searching`` tested a ``gps.state`` the collector never emits (``'searching'``).

    This version derives mood from real, live signals and the Beast's live needs:

    * ``quiet`` is time since a genuinely *new* network (``wifi.encounters.session_unique`` rising,
      falling back to lifetime-unique), not raw AP-count churn;
    * ``hunting`` requires real movement (``context.motion.state``) and ``gps-searching`` the real
      ``connected_no_fix`` state;
    * ``celebrating`` fires on a genuinely new capture (``captures.total`` rising);
    * the live ``needs.*`` drives fold into mood and the expressed scalars, so the Beast visibly
      *wants* things and two Beasts diverge over time (a need reported unavailable is ignored); and
    * each non-urgent mood is held a short, focus-scaled minimum (hysteresis) so expressions do not
      flicker, while fault / overheated / celebrating always preempt.

    Values stay live/derived (ADR-0008); the ``beast.*`` vocabulary is unchanged.
    """

    def __init__(self, state, clock=time.monotonic) -> None:
        self.state = state
        self.clock = clock
        now = clock()
        self._sess_val: float | None = None   # last-seen session-unique AP count (bounded; see tick)
        self._life_val: float | None = None   # last-seen lifetime-unique AP count (DB-backed, unbounded)
        self._novel_t = now                   # when either last rose -> ``quiet`` is measured from here
        self._novel_seen = False              # has a counter actually risen? (boot is not a discovery)
        self._cap_val: float | None = None    # last-seen capture total
        self._cap_t: float | None = None      # when a capture was last added
        self._mood: str | None = None         # currently expressed mood (for hysteresis)
        self._mood_since = now

    def _num(self, key: str) -> float | None:
        v = self.state.get(key, None)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _temp(self, axis: str) -> int:
        # Neutral (50) only when the axis is absent / None / invalid. A real 0 is a valid heritage
        # minimum (0..100) and must be kept, so no truthiness ``or 50`` here (findings F5 / P2).
        v = self.state.get("beast.temperament." + axis, 50)
        if v is None:
            return 50
        try:
            return max(0, min(100, int(v)))
        except (TypeError, ValueError):
            return 50

    def _need(self, name: str) -> int | None:
        # A live need is 0..100; absent / unavailable is None -> callers ignore that need (ADR-0008).
        v = self.state.get("needs." + name, None)
        if v is None:
            return None
        try:
            return max(0, min(100, int(v)))
        except (TypeError, ValueError):
            return None

    def tick(self) -> dict[str, Any]:
        now = self.clock()

        # --- edge detectors: time since the last genuinely new network / capture ----------------
        # ``quiet`` keys on genuine novelty, not raw AP-count churn, so simply re-seeing the same
        # room cannot keep the Beast excited. Track BOTH the session-unique counter and the lifetime
        # counter and reset on either: SemanticEngine caps session_unique (~50k BSSIDs) and evicts
        # on a very long wardrive, after which it is flat while the DB-backed lifetime counter keeps
        # climbing -- keying on session alone would then stop registering new discoveries.
        sess = self._num("wifi.encounters.session_unique")
        life = self._num("wifi.encounters.lifetime_unique")
        if sess is not None:
            if self._sess_val is None:
                self._sess_val = sess
            elif sess > self._sess_val:
                self._sess_val = sess
                self._novel_t = now
                self._novel_seen = True
        if life is not None:
            if self._life_val is None:
                self._life_val = life
            elif life > self._life_val:
                self._life_val = life
                self._novel_t = now
                self._novel_seen = True
        quiet = max(0.0, now - self._novel_t)

        # ``celebrating`` fires on a real new capture (handshake); ``semantic.capture.recent`` --
        # the old gate -- has no producer, so it never fired. ``captures.total`` is the live count.
        # Only a modest live increment counts as "a capture just happened": captures.total reads 0
        # both for a genuinely empty cache and for an absent/unmounted one, so a later 0 -> N jump is
        # the source recovering, not a capture now -- update the baseline but do not celebrate it.
        cap = self._num("captures.total")
        if cap is None:
            cap = self._num("pwnagotchi.handshakes")
        if cap is not None:
            if self._cap_val is None:
                self._cap_val = cap
            elif cap > self._cap_val:
                delta = cap - self._cap_val
                self._cap_val = cap
                if delta <= CAPTURE_MAX_DELTA:
                    self._cap_t = now
        recent_capture = self._cap_t is not None and (now - self._cap_t) <= CAPTURE_CELEBRATE_SEC

        # --- observed conditions ----------------------------------------------------------------
        aps = int(self.state.get("wifi.ap_count", 0) or 0)
        health = str(self.state.get("health.core.state", "starting") or "starting")
        gov = str(self.state.get("governor.mode", "FULL") or "FULL")
        temp = float(self.state.get("system.temp.cpu_c", 0) or 0)
        gps_state = str(self.state.get("gps.state", "unknown") or "unknown")
        pwn = str(self.state.get("pwnagotchi.service.state", "unknown") or "unknown")
        bc = str(self.state.get("bettercap.state", "unknown") or "unknown")
        phase = str(self.state.get("ambient.day_phase", "day") or "day")
        cpu = float(self.state.get("system.cpu.total", 0) or 0)
        lvl = int(self.state.get("progression.level", 1) or 1)
        # GPS can stall: the collector stops, its last gps.* values are retained but marked stale,
        # and ContextEngine still republishes context.motion.state from them as if live. Trusting it
        # would let a stationary Beast keep entering hunting / gps-searching (ADR-0008: never treat
        # stale data as live). The health loop publishes a fresh staleness flag, so gate on it.
        gps_fresh = str(self.state.get("health.collector.gps.state", "ok") or "ok") != "stale"
        moving = gps_fresh and str(self.state.get("context.motion.state", "unknown") or "unknown") in MOTION_ACTIVE
        night = phase in {"night", "late_night"}

        cur_t = self._temp("curiosity")
        foc_t = self._temp("focus")
        bold_t = self._temp("boldness")
        noct_t = self._temp("nocturnal")

        tiredness = self._need("tiredness")
        hunger = self._need("curiosity_hunger")
        restless = self._need("restlessness")
        lonely = self._need("loneliness")

        # --- raw mood: physical urgencies, then real activity, then the Beast's live needs ------
        # Each needs-driven branch falls back to a time/condition heuristic when that need is
        # unavailable, so a Beast with no heritage/needs still behaves (just without the drives).
        if health in {"critical", "failed"} or pwn not in {"active", "running"} or bc not in {"active", "running"}:
            raw = "fault"
        elif temp >= 80 or gov == "SURVIVAL":
            raw = "overheated"
        elif recent_capture:
            raw = "celebrating"
        elif moving and self._novel_seen and quiet < NOVELTY_RECENT_SEC:
            raw = "hunting"
        elif (tiredness is not None and tiredness >= TIRED_MOOD) or \
             (tiredness is None and night and quiet > QUIET_SLEEPY_SEC):
            raw = "sleepy"
        elif (hunger is not None and hunger >= HUNGRY_MOOD) or \
             (hunger is None and aps > 0 and quiet < NOVELTY_WARM_SEC):
            raw = "curious"
        elif (restless is not None and restless >= RESTLESS_MOOD) or \
             (lonely is not None and lonely >= RESTLESS_MOOD) or \
             (restless is None and lonely is None and quiet > QUIET_BORED_SEC):
            raw = "bored"
        elif gps_fresh and gps_state == "connected_no_fix":
            raw = "gps-searching"
        else:
            raw = "idle"

        # --- hysteresis: hold a non-urgent mood a short, focus-scaled minimum -------------------
        # Urgent moods (fault / overheated / celebrating) preempt instantly, and leaving one is
        # instant too; only non-urgent <-> non-urgent transitions wait out the dwell.
        if self._mood is None:
            self._mood, self._mood_since = raw, now
        elif raw in URGENT_MOODS or self._mood in URGENT_MOODS:
            if raw != self._mood:
                self._mood, self._mood_since = raw, now
        else:
            min_dwell = DWELL_MIN_SEC + DWELL_FOCUS_SEC * foc_t / 100.0
            if raw != self._mood and (now - self._mood_since) >= min_dwell:
                self._mood, self._mood_since = raw, now
        mood = self._mood

        # --- expressed scalars from the chosen mood --------------------------------------------
        energy, focus, curiosity = _MOOD_SCALARS[mood]
        if mood == "idle":
            energy = max(35, min(75, int(70 - cpu * 0.25)))

        # Live needs nudge the scalars: exhaustion saps energy, novelty-hunger sharpens curiosity.
        if tiredness is not None:
            energy -= round(tiredness * 0.30)
        if hunger is not None:
            curiosity += round(hunger * 0.20)

        confidence = max(10, min(100, 35 + lvl // 2 + (20 if health == "healthy" else 0) + (10 if gps_state == "fixed" else 0)))
        energy = max(0, min(100, energy))
        stress = max(0, min(100, (100 - energy) // 2 + (35 if gov in {"REDUCED", "SURVIVAL"} else 0) + (45 if health not in {"healthy", "starting"} else 0)))

        # Heritage temperament biases the expressed numbers so two Beasts differ (finding F5).
        # Core publishes beast.temperament.* for the active Beast; absent axes default to 50
        # (neutral), leaving behaviour unchanged. Values stay live/derived (ADR-0008).
        curiosity = max(0, min(100, curiosity + round((cur_t - 50) * 0.5)))
        focus = max(0, min(100, focus + round((foc_t - 50) * 0.4)))
        energy = max(0, min(100, energy + round((bold_t - 50) * 0.3) + round((noct_t - 50) * (0.3 if night else -0.15))))
        stress = max(0, min(100, stress - round((bold_t - 50) * 0.2)))
        return {
            "beast.mood": mood,
            "beast.energy": int(energy),
            "beast.curiosity": int(curiosity),
            "beast.focus": int(focus),
            "beast.confidence": int(confidence),
            "beast.stress": int(stress),
            "beast.quiet_sec": round(quiet, 1),
            "beast.expression": mood,
            "beast.personality.source": "derived_live",
        }
