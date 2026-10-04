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
        self._cap_ready = False               # was the capture source readable last tick? (vs just mounted)
        self._mood: str | None = None         # currently expressed mood (for hysteresis)
        self._mood_since = now
        self._beast_id: Any = None            # active Beast, to reset the expression on a roster switch

    def _live(self, key: str) -> Any:
        # Per-key live-truth: return the value only while the registry considers the key live; a key
        # marked stale (its collector stopped refreshing) or unavailable reads as absent, so mood is
        # never driven by data that is no longer true (ADR-0008). Falls back to the plain value when
        # the state exposes no metadata (e.g. tests).
        meta = getattr(self.state, "meta", None)
        if callable(meta):
            m = meta(key)
            if m is not None and m.get("quality") in ("stale", "unavailable"):
                return None
        return self.state.get(key, None)

    def _num(self, key: str) -> float | None:
        try:
            return float(self._live(key))
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

        # Expression belongs to the active Beast: clear the hysteresis hold on a roster switch so a
        # newly activated Beast does not keep showing the previous one's mood through the dwell window.
        beast_id = self.state.get("progression.beast.id", None)
        if beast_id != self._beast_id:
            self._beast_id = beast_id
            self._mood = None
            self._mood_since = now
            # A new Beast does not inherit the previous one's pending reactions: re-baseline the
            # novelty/capture detectors so it does not celebrate or hunt the prior Beast's events.
            self._novel_t = now
            self._novel_seen = False
            self._sess_val = None
            self._life_val = None
            self._cap_t = None
            self._cap_val = None
            self._cap_ready = False

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

        # ``celebrating`` fires on a real new capture (handshake); the old ``semantic.capture.recent``
        # gate has no producer, so it never fired. captures.total reads 0 both for a genuinely empty
        # cache and for an absent/unmounted one, so the collector publishes captures.cache_present to
        # tell them apart: a capture counts only as an increase while the source was readable on the
        # previous tick. That celebrates a real first handshake (0 -> 1 on a readable cache) but not the
        # cache merely mounting with pre-existing captures (ADR-0008). When the signal is absent (older
        # data / tests) readability is inferred from a positive count, so a 0 -> N jump never celebrates.
        cap = self._num("captures.total")
        if cap is None:
            cap = self._num("pwnagotchi.handshakes")
        present = self._live("captures.cache_present")
        readable_now = bool(present) if present is not None else (cap is not None and cap > 0)
        if cap is not None and readable_now:
            if self._cap_ready and self._cap_val is not None and cap > self._cap_val:
                self._cap_t = now
            # captures.total is monotonic; keep the high-water mark so a transient partial-scan dip
            # (an .apcache file briefly unreadable) that then recovers is not read as a new capture.
            if self._cap_val is None or cap > self._cap_val:
                self._cap_val = cap
        else:
            self._cap_val = None  # source not readable -> re-baseline when it returns
        self._cap_ready = readable_now
        recent_capture = self._cap_t is not None and (now - self._cap_t) <= CAPTURE_CELEBRATE_SEC

        # --- observed conditions ----------------------------------------------------------------
        aps = int(self.state.get("wifi.ap_count", 0) or 0)
        # governor.mode is read per-key-live (_live): state.get returns retained values with no expiry, so
        # a stale "SURVIVAL" would otherwise drive overheated forever. The governor is an engine loop (not a
        # collector), so the health watchdog ages the "governor" source (core._age_engine_sources) -- a
        # stalled governor then falls through to "FULL", which is not overheated (ADR-0008).
        gov = str(self._live("governor.mode") or "FULL")
        # health.core.state is read raw on purpose: it is produced by the health/watchdog loop itself from
        # the current collector states, so it is fresh whenever that loop runs and cannot observe its own
        # staleness. A stalled health loop surfacing as fault is acceptable (the health monitor is down).
        health = str(self.state.get("health.core.state", "starting") or "starting")
        temp = float(self._live("system.temp.cpu_c") or 0)   # stale/unavailable temp -> 0 (not overheated)
        gps_state = str(self._live("gps.state") or "unknown")  # stale/absent -> "unknown"
        # pwnagotchi/bettercap service states are read raw on purpose: their absent/"unknown" default
        # itself triggers fault, so per-key-live gating would turn a merely stale read into an *asserted*
        # fault -- a mood-contract call deferred to #60, not this honesty pass (Bible §11 still notes
        # these inputs "aren't all quality-gated").
        pwn = str(self.state.get("pwnagotchi.service.state", "unknown") or "unknown")
        bc = str(self.state.get("bettercap.state", "unknown") or "unknown")
        phase = str(self.state.get("ambient.day_phase", "day") or "day")
        cpu = float(self.state.get("system.cpu.total", 0) or 0)
        lvl = int(self.state.get("progression.level", 1) or 1)
        # Motion is trustworthy only with an actual fix AND a live motion read: gps.state
        # "unavailable"/"connected_no_fix" are live values with no usable position, and the ContextEngine
        # (an engine loop) can stall while GPS still reads fixed. The health watchdog ages the "context"
        # source (core._age_engine_sources), so a stalled motion read goes stale and _live drops it: require
        # gps.state "fixed" and a per-key-live context.motion.state -- a stale "walking" reads "unknown" and
        # cannot drive hunting (ADR-0008).
        moving = gps_state == "fixed" and str(self._live("context.motion.state") or "unknown") in MOTION_ACTIVE
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
             (hunger is None and aps > 0 and self._novel_seen and quiet < NOVELTY_WARM_SEC):
            raw = "curious"
        elif (restless is not None and restless >= RESTLESS_MOOD) or \
             (lonely is not None and lonely >= RESTLESS_MOOD) or \
             (restless is None and lonely is None and quiet > QUIET_BORED_SEC):
            raw = "bored"
        elif gps_state == "connected_no_fix":
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
