"""Creature finding F1: the Beast's mood is now varied and needs-driven, not stuck.

Before, the mood if-chain keyed on signals that were effectively constant -- ``quiet`` reset on any
AP-count churn, ``hunting``/``gps-searching`` gated on the always-true ``expedition.active``,
``celebrating`` on an unpublished signal, and ``gps-searching`` on a ``gps.state`` the collector
never emits -- so the Beast sat in one or two moods. These tests lock in the live derivation:
genuine-novelty ``quiet``, real-motion gating, real captures, the honest ``connected_no_fix``
state, the live ``needs.*`` drives folded into mood, and the expression-hold hysteresis.
"""
from __future__ import annotations

from beastcore.needs import NeedsEngine
from beastcore.personality import CAPTURE_CELEBRATE_SEC, PersonalityEngine


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class MetaState(dict):
    """FakeState that also exposes StateRegistry-style per-key quality metadata, so tests can mark a
    key stale/unavailable and check mood never treats a no-longer-live value as live."""
    def __init__(self, values=None, *, stale=(), unavailable=()):
        super().__init__(values or {})
        self._q = {**{k: "stale" for k in stale}, **{k: "unavailable" for k in unavailable}}

    def get(self, key, default=None):
        return dict.get(self, key, default)

    def meta(self, key):
        if key not in self:
            return None
        return {"quality": self._q.get(key, "live"), "value": self[key], "updated_at": 0.0}


HEALTHY = {
    "health.core.state": "healthy", "governor.mode": "FULL", "system.temp.cpu_c": 50.0,
    "pwnagotchi.service.state": "active", "bettercap.state": "active",
    "progression.level": 10, "ambient.day_phase": "day",
}


def _tick(**signals):
    """One tick of a fresh engine (so no hysteresis history) at clock 0."""
    return PersonalityEngine(FakeState({**HEALTHY, **signals}), clock=lambda: 0.0).tick()


def _after_new_network(**extra):
    """Result after the engine observes a *genuine* new network (an edge), past the mood dwell.

    Boot alone is not a discovery (finding on #50: ``_novel_t`` starts at "now"), so hunting needs an
    actual counter increase -- this ticks a baseline, bumps session_unique, then ticks again.
    """
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "wifi.ap_count": 20,
                   "wifi.encounters.session_unique": 10, **extra})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()                                    # baseline: a count is seen but has not risen
    s["wifi.encounters.session_unique"] = 11    # a genuinely new network appears
    clock[0] = 25.0                             # past the ~20s hysteresis dwell
    return e.tick()


# --- genuine novelty, not AP-count churn, drives "quiet" -------------------------------------

def test_ap_count_churn_alone_does_not_keep_the_beast_excited():
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "wifi.encounters.session_unique": 10, "wifi.ap_count": 20})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    out = {}
    for i in range(1, 40):                       # churn the AP count, but discover nothing new
        clock[0] = float(i * 10)
        s["wifi.ap_count"] = 20 + (i % 5)
        out = e.tick()
    assert out["beast.quiet_sec"] >= 120          # quiet grew: re-seeing the room is not novelty
    assert out["beast.mood"] not in {"curious", "hunting"}  # so the Beast is no longer stuck excited


def test_a_new_network_resets_quiet():
    clock = [0.0]
    s = FakeState({**HEALTHY, "wifi.encounters.session_unique": 10})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    clock[0] = 1000.0
    assert e.tick()["beast.quiet_sec"] >= 900
    s["wifi.encounters.session_unique"] = 11      # a genuinely new network
    clock[0] = 1001.0
    assert e.tick()["beast.quiet_sec"] <= 1.0


def test_recent_new_network_drives_curious_when_stationary():
    # curious (no-needs fallback) needs a genuine novelty edge, not just APs present at boot.
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "wifi.ap_count": 20, "wifi.encounters.session_unique": 10})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()                                       # baseline, no discovery edge yet
    s["wifi.encounters.session_unique"] = 11       # a genuinely new network
    clock[0] = 25.0                                # past the mood dwell
    assert e.tick()["beast.mood"] == "curious"


# --- real motion, real captures, real GPS state ---------------------------------------------

def test_hunting_requires_real_motion_not_the_always_true_expedition_flag():
    # expedition.active is always True and must not drive hunting; real motion + a real discovery does.
    assert _after_new_network(**{"expedition.active": True})["beast.mood"] != "hunting"          # not moving
    assert _after_new_network(**{"context.motion.state": "walking"})["beast.mood"] == "hunting"
    assert _after_new_network(**{"context.motion.state": "wardrive"})["beast.mood"] == "hunting"


def test_celebrating_fires_on_a_new_capture_not_the_phantom_signal():
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 5, "semantic.capture.recent": True})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    assert e.tick()["beast.mood"] != "celebrating"          # the old phantom gate does nothing
    s["captures.total"] = 6
    clock[0] = 5.0
    assert e.tick()["beast.mood"] == "celebrating"          # a genuinely new capture
    clock[0] = 5.0 + CAPTURE_CELEBRATE_SEC + 1.0
    assert e.tick()["beast.mood"] != "celebrating"          # and it is a brief window, not sticky


def test_gps_searching_uses_the_real_connected_no_fix_state():
    base = {"wifi.ap_count": 0}
    assert _tick(**{**base, "gps.state": "connected_no_fix"})["beast.mood"] == "gps-searching"
    assert _tick(**{**base, "gps.state": "unavailable"})["beast.mood"] == "idle"
    assert _tick(**{**base, "gps.state": "searching"})["beast.mood"] == "idle"   # phantom state -> never fires


# --- the live needs fold into mood and the expressed scalars ---------------------------------

def test_high_tiredness_makes_sleepy_and_saps_energy():
    base = {"gps.state": "fixed", "wifi.ap_count": 0}
    assert _tick(**{**base, "needs.tiredness": 80})["beast.mood"] == "sleepy"
    assert _tick(**{**base, "needs.tiredness": 100})["beast.energy"] < _tick(**{**base, "needs.tiredness": 65})["beast.energy"]


def test_high_curiosity_hunger_drives_curious_and_sharpens_curiosity():
    base = {"gps.state": "fixed", "wifi.ap_count": 0}
    assert _tick(**{**base, "needs.curiosity_hunger": 90})["beast.mood"] == "curious"
    # even below the mood threshold, hunger sharpens the expressed curiosity scalar
    assert _tick(**{**base, "needs.curiosity_hunger": 50})["beast.curiosity"] > _tick(**{**base, "needs.curiosity_hunger": 0})["beast.curiosity"]


def test_restlessness_or_loneliness_makes_bored():
    base = {"gps.state": "fixed", "wifi.ap_count": 0}
    assert _tick(**{**base, "needs.restlessness": 80})["beast.mood"] == "bored"
    assert _tick(**{**base, "needs.loneliness": 80})["beast.mood"] == "bored"


def test_unavailable_needs_fall_back_without_error():
    # No needs.* in state at all -> every need is unavailable -> the engine uses its heuristics.
    out = _tick(**{"gps.state": "fixed", "wifi.ap_count": 5, "wifi.encounters.session_unique": 10})
    assert out["beast.mood"] in {"curious", "idle", "hunting", "gps-searching", "bored", "sleepy"}


def test_tick_returns_the_stable_beast_contract_keys():
    # The beast.* vocabulary is unchanged by the F1 rewrite (no new keys, none dropped).
    assert set(_tick(**{"gps.state": "fixed"})) == {
        "beast.mood", "beast.energy", "beast.curiosity", "beast.focus", "beast.confidence",
        "beast.stress", "beast.quiet_sec", "beast.expression", "beast.personality.source",
    }


# --- hysteresis: steady expressions, but urgencies still preempt -----------------------------

def test_hysteresis_holds_a_nonurgent_mood_but_urgent_preempts():
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "wifi.ap_count": 0, "wifi.encounters.session_unique": 10})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    assert e.tick()["beast.mood"] == "idle"                     # establish idle at t0 (aps 0, no edge)
    s["wifi.ap_count"] = 5
    s["wifi.encounters.session_unique"] = 11                    # a genuine new network (novelty edge)
    clock[0] = 5.0
    assert e.tick()["beast.mood"] == "idle"                     # curious conditions, but within the dwell
    clock[0] = 30.0
    assert e.tick()["beast.mood"] == "curious"                  # past the dwell -> it switches
    s["system.temp.cpu_c"] = 85.0
    clock[0] = 31.0
    assert e.tick()["beast.mood"] == "overheated"              # urgent preempts instantly, ignoring the dwell


def test_mood_hysteresis_resets_on_active_beast_change():
    # A roster switch must not keep showing the previous Beast's expression through the dwell window.
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "wifi.ap_count": 0, "progression.beast.id": "A"})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    assert e.tick()["beast.mood"] == "idle"                   # Beast A settles to idle
    s["needs.tiredness"] = 90                                 # raw mood for the next Beast is sleepy
    s["progression.beast.id"] = "B"                           # roster.switch, within the dwell window
    clock[0] = 2.0
    assert e.tick()["beast.mood"] == "sleepy"                 # Beast B shows its own mood at once


# --- freshness + counter-saturation robustness (Codex review on #50) -------------------------

def test_stale_gps_motion_is_not_trusted_for_hunting_or_searching():
    # GPS stalled: gps.* values are retained but the registry marks them stale, and ContextEngine still
    # republishes context.motion.state as live. Mood must not treat that as live -> neither hunting nor
    # gps-searching may fire (ADR-0008), even though motion.state itself still reads "walking".
    clock = [0.0]
    s = MetaState({**HEALTHY, "gps.state": "fixed", "context.motion.state": "walking", "wifi.ap_count": 20,
                   "wifi.encounters.session_unique": 10}, stale=["gps.state"])
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["wifi.encounters.session_unique"] = 11
    clock[0] = 25.0
    assert e.tick()["beast.mood"] != "hunting"
    s2 = MetaState({**HEALTHY, "gps.state": "connected_no_fix", "wifi.ap_count": 0}, stale=["gps.state"])
    assert PersonalityEngine(s2, clock=lambda: 0.0).tick()["beast.mood"] != "gps-searching"
    # the same signals while the gps.* keys are live DO drive those moods
    assert _after_new_network(**{"context.motion.state": "walking"})["beast.mood"] == "hunting"
    assert _tick(**{"gps.state": "connected_no_fix", "wifi.ap_count": 0})["beast.mood"] == "gps-searching"


def test_stale_temperature_is_not_read_as_overheated():
    # A stale hot CPU temp (collector stopped refreshing it) must not drive the overheated mood.
    s = MetaState({**HEALTHY, "system.temp.cpu_c": 90.0, "gps.state": "fixed"}, stale=["system.temp.cpu_c"])
    assert PersonalityEngine(s, clock=lambda: 0.0).tick()["beast.mood"] != "overheated"


def test_stale_motion_is_not_trusted_for_hunting_though_gps_is_fixed():
    # The ContextEngine (motion) and GPS collector are separate producers. If the context engine stalls
    # while GPS still reads a live "fixed", a retained "walking" must not drive hunting -- motion is read
    # per-key-live, so a stale motion reads as "unknown" and hunting cannot fire (ADR-0008).
    clock = [0.0]
    s = MetaState({**HEALTHY, "gps.state": "fixed", "context.motion.state": "walking", "wifi.ap_count": 20,
                   "wifi.encounters.session_unique": 10}, stale=["context.motion.state"])
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["wifi.encounters.session_unique"] = 11      # a genuinely new network while "moving"
    clock[0] = 25.0
    assert e.tick()["beast.mood"] != "hunting"
    # the same signals with a live motion read DO drive hunting
    assert _after_new_network(**{"context.motion.state": "walking"})["beast.mood"] == "hunting"


def test_stale_survival_governor_is_not_read_as_overheated():
    # A stale governor "SURVIVAL" (the governor producer stopped refreshing) must not keep driving the
    # overheated mood indefinitely; it falls through to the live signals (ADR-0008).
    s = MetaState({**HEALTHY, "governor.mode": "SURVIVAL", "gps.state": "fixed", "wifi.ap_count": 0},
                  stale=["governor.mode"])
    assert PersonalityEngine(s, clock=lambda: 0.0).tick()["beast.mood"] != "overheated"
    # a live SURVIVAL still drives overheated
    assert _tick(**{"governor.mode": "SURVIVAL", "gps.state": "fixed", "wifi.ap_count": 0})["beast.mood"] == "overheated"


def test_stale_critical_health_is_not_read_as_fault():
    # A stale health "critical"/"failed" (the health producer stopped refreshing) must not keep driving
    # the fault mood indefinitely; it falls through to the live signals (ADR-0008).
    s = MetaState({**HEALTHY, "health.core.state": "critical", "gps.state": "fixed", "wifi.ap_count": 0},
                  stale=["health.core.state"])
    assert PersonalityEngine(s, clock=lambda: 0.0).tick()["beast.mood"] != "fault"
    # a live critical health still drives fault
    assert _tick(**{"health.core.state": "critical", "gps.state": "fixed", "wifi.ap_count": 0})["beast.mood"] == "fault"


def test_first_capture_on_a_readable_cache_celebrates():
    # With the capture-source signal, a genuine first handshake (0 -> 1 on an already-readable cache)
    # celebrates -- while a cache that only just became present does not.
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 0, "captures.cache_present": True})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["captures.total"] = 1
    clock[0] = 2.0
    assert e.tick()["beast.mood"] == "celebrating"
    clock2 = [0.0]
    s2 = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 0, "captures.cache_present": False})
    e2 = PersonalityEngine(s2, clock=lambda: clock2[0])
    e2.tick()
    s2["captures.cache_present"] = True       # cache just mounted with pre-existing captures
    s2["captures.total"] = 50
    clock2[0] = 2.0
    assert e2.tick()["beast.mood"] != "celebrating"


def test_unavailable_gps_state_is_not_live_motion():
    # gps.state="unavailable" (and "connected_no_fix") are live values with no fix; ContextEngine may
    # preserve "walking" during a brief fix drop, but only an actual "fixed" is usable motion evidence.
    assert _after_new_network(**{"gps.state": "unavailable", "context.motion.state": "walking"})["beast.mood"] != "hunting"


def test_capture_count_dip_then_recovery_does_not_celebrate():
    # captures.total is monotonic; a transient partial-scan dip that recovers to the prior total is not a
    # new capture (high-water mark), so it must not celebrate.
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 10, "captures.cache_present": True})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["captures.total"] = 8                               # a file briefly unreadable -> count dips
    clock[0] = 2.0
    assert e.tick()["beast.mood"] != "celebrating"
    s["captures.total"] = 10                              # scan recovers to the prior total
    clock[0] = 4.0
    assert e.tick()["beast.mood"] != "celebrating"


def test_capped_session_counter_still_registers_novelty_via_lifetime():
    # SemanticEngine bounds session_unique (~50k BSSIDs) and evicts, so on a long wardrive it sits
    # flat while the DB-backed lifetime counter keeps climbing. A genuinely new AP then shows up only
    # in lifetime_unique; quiet must still reset so discovery-driven moods keep firing.
    clock = [0.0]
    s = FakeState({**HEALTHY, "context.motion.state": "wardrive", "gps.state": "fixed",
                   "wifi.encounters.session_unique": 50000, "wifi.encounters.lifetime_unique": 90000})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    clock[0] = 1000.0
    assert e.tick()["beast.quiet_sec"] >= 900           # nothing new -> quiet grows
    s["wifi.encounters.lifetime_unique"] = 90001        # a new AP: session capped/flat, lifetime ticks
    clock[0] = 1001.0
    assert e.tick()["beast.quiet_sec"] <= 1.0           # quiet resets off the lifetime counter


def test_fresh_start_motion_does_not_hunt_without_a_real_discovery():
    # At boot `quiet` is 0 only because the engine just started, not because a network appeared.
    # GPS motion alone must not read as hunting until a counter has actually risen (ADR-0008).
    assert _tick(**{"gps.state": "fixed", "context.motion.state": "walking",
                    "wifi.ap_count": 0})["beast.mood"] != "hunting"
    # once a genuinely new network is observed while moving, hunting is correct
    assert _after_new_network(**{"context.motion.state": "walking"})["beast.mood"] == "hunting"


def test_celebrating_ignores_capture_source_recovery():
    # captures.total reads 0 for an absent/unmounted cache too, so a later 0 -> N jump is the source
    # recovering with pre-existing captures, not a capture happening now -> do not celebrate it.
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 0})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["captures.total"] = 50                             # cache mounts with pre-existing captures
    clock[0] = 5.0
    assert e.tick()["beast.mood"] != "celebrating"
    s["captures.total"] = 51                             # a real new capture (+1) on a now-positive base
    clock[0] = 10.0
    assert e.tick()["beast.mood"] == "celebrating"
    # a *small* recovery (0 -> 5) is also a source becoming readable, not a live capture
    clock2 = [0.0]
    s2 = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 0})
    e2 = PersonalityEngine(s2, clock=lambda: clock2[0])
    e2.tick()
    s2["captures.total"] = 5
    clock2[0] = 5.0
    assert e2.tick()["beast.mood"] != "celebrating"


def test_switching_beasts_clears_pending_reactions():
    # Celebrate/hunt are the active Beast's presentation; a roster switch must not inherit the previous
    # Beast's pending reaction (e.g. a capture observed seconds before the switch).
    clock = [0.0]
    s = FakeState({**HEALTHY, "gps.state": "fixed", "captures.total": 5, "progression.beast.id": "A"})
    e = PersonalityEngine(s, clock=lambda: clock[0])
    e.tick()
    s["captures.total"] = 6
    clock[0] = 2.0
    assert e.tick()["beast.mood"] == "celebrating"       # Beast A celebrates its own capture
    s["progression.beast.id"] = "B"
    clock[0] = 5.0
    assert e.tick()["beast.mood"] != "celebrating"       # Beast B does not inherit A's celebration


# --- end to end: NeedsEngine + PersonalityEngine over a simulated day ------------------------

def _world(t: float) -> dict:
    """Real signals for a day stitched together: home -> walk -> wardrive -> hot -> night."""
    H = 3600.0
    base = {"health.core.state": "healthy", "governor.mode": "FULL", "pwnagotchi.service.state": "active",
            "bettercap.state": "active", "progression.level": 7, "system.cpu.total": 18.0}
    if t < 3 * H:                                   # home: GPS no fix, a few early new nets then nothing
        new = 100 + min(3, int(t // 400))
        base.update({"gps.state": "connected_no_fix", "gps.fix": False, "context.motion.state": "unknown",
                     "wifi.ap_count": 24, "wifi.encounters.session_unique": new,
                     "wifi.encounters.lifetime_unique": 1000 + new,
                     "peerdex.last_seen_at": (60.0 if t >= 60 else None), "system.temp.cpu_c": 52.0,
                     "power.battery.percent_estimate": 80.0, "ambient.day_phase": "day"})
    elif t < 4 * H:                                 # walk: fixed + moving, steady new networks
        u = t - 3 * H
        new = 200 + int(u // 120)
        base.update({"gps.state": "fixed", "gps.fix": True, "context.motion.state": "walking",
                     "gps.session_distance_m": 1.4 * u, "wifi.ap_count": 30,
                     "wifi.encounters.session_unique": new, "wifi.encounters.lifetime_unique": 2000 + new,
                     "system.temp.cpu_c": 58.0, "power.battery.percent_estimate": 70.0, "ambient.day_phase": "day"})
    elif t < 5 * H:                                 # wardrive: flood of new networks and a few captures
        u = t - 4 * H
        new = 300 + int(u // 20)
        base.update({"gps.state": "fixed", "gps.fix": True, "context.motion.state": "wardrive",
                     "gps.session_distance_m": 13.0 * u, "captures.total": int(u // 900),
                     "wifi.ap_count": 45, "wifi.encounters.session_unique": new,
                     "wifi.encounters.lifetime_unique": 3000 + new, "system.temp.cpu_c": 64.0,
                     "power.battery.percent_estimate": 60.0, "ambient.day_phase": "day"})
    else:                                           # hot spell then a long night, nothing new
        u = t - 5 * H
        hot = u < 1.5 * H
        base.update({"governor.mode": "REDUCED" if hot else "FULL", "gps.state": "unavailable",
                     "gps.fix": False, "context.motion.state": "unknown", "wifi.ap_count": 12,
                     "wifi.encounters.session_unique": 400, "wifi.encounters.lifetime_unique": 4000,
                     "system.temp.cpu_c": 86.0 if hot else 55.0,
                     "power.battery.percent_estimate": max(8.0, 60.0 - u / H * 12.0),
                     "ambient.day_phase": "day" if hot else "night"})
    return base


def _simulate_day(temperament: dict | None = None) -> dict[str, int]:
    clock = [0.0]
    state = FakeState({})
    if temperament:
        state.update({f"beast.temperament.{k}": v for k, v in temperament.items()})
    needs = NeedsEngine(state, clock=lambda: clock[0])
    pers = PersonalityEngine(state, clock=lambda: clock[0])
    counts: dict[str, int] = {}
    for sec in range(0, 8 * 3600, 10):
        clock[0] = float(sec)
        state.update(_world(sec))
        for key, value in needs.tick().items():
            state[key] = value
        mood = pers.tick()["beast.mood"]
        counts[mood] = counts.get(mood, 0) + 1
    return counts


def test_mood_is_varied_across_a_simulated_day():
    counts = _simulate_day()
    total = sum(counts.values())
    assert len(counts) >= 5                                      # F1: no longer stuck in one or two moods
    assert max(counts.values()) / total < 0.5                   # and nothing dominates the day
    # the moods that were effectively impossible before all occur now
    assert {"hunting", "celebrating", "overheated", "sleepy"} <= set(counts)


def test_two_heritages_diverge_over_the_same_day():
    neutral = _simulate_day()
    curious_nocturnal = _simulate_day({"curiosity": 95, "nocturnal": 95, "social": 80})
    assert neutral != curious_nocturnal
