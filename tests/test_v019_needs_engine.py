"""Creature idea 1+2: the NeedsEngine derives live, honest needs from real signals.

Needs rise over hours and are eased by a real satisfying signal; heritage temperament shifts the
rates; a need whose driving signal is absent is reported unavailable (None here), never faked
(ADR-0008 / ADR-0010).
"""
from __future__ import annotations

from beastcore.needs import NeedsEngine


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class MetaState(dict):
    """FakeState that also exposes StateRegistry-style per-key quality metadata, so tests can mark a
    key stale/unavailable (its collector stopped refreshing) and check the engine treats it as absent."""
    def __init__(self, values=None, *, stale=(), unavailable=()):
        super().__init__(values or {})
        self._q = {**{k: "stale" for k in stale}, **{k: "unavailable" for k in unavailable}}

    def get(self, key, default=None):
        return dict.get(self, key, default)

    def meta(self, key):
        if key not in self:
            return None
        return {"quality": self._q.get(key, "live"), "value": self[key], "updated_at": 0.0}


def _engine(state, clock_box):
    return NeedsEngine(FakeState(state), clock=lambda: clock_box[0])


def test_absent_signals_are_unavailable_not_faked():
    # An empty state has no novelty / GPS / peer / thermal signal -> every need is unavailable.
    out = NeedsEngine(FakeState({}), clock=lambda: 0.0).tick()
    for need in ("needs.curiosity_hunger", "needs.restlessness", "needs.loneliness", "needs.tiredness"):
        assert out[need] is None
    assert out["needs.source"] == "derived_live"


def test_time_based_needs_rise_toward_full_over_hours():
    clock = [0.0]
    e = _engine({"wifi.encounters.lifetime_unique": 10, "gps.state": "fixed",
                 "context.motion.state": "stationary", "peerdex.last_seen_at": 1.0}, clock)
    assert e.tick()["needs.curiosity_hunger"] == 0
    clock[0] = 2 * 3600.0  # half of the ~4h neutral rise
    out = e.tick()
    assert 40 <= out["needs.curiosity_hunger"] <= 60
    assert 40 <= out["needs.restlessness"] <= 60
    assert 40 <= out["needs.loneliness"] <= 60


def test_novelty_eases_curiosity_hunger():
    clock = [0.0]
    e = _engine({"wifi.encounters.lifetime_unique": 10}, clock)
    e.tick()
    clock[0] = 3 * 3600.0
    assert e.tick()["needs.curiosity_hunger"] > 0
    e.state["wifi.encounters.lifetime_unique"] = 11  # a genuinely new network
    clock[0] = 3 * 3600.0 + 1.0
    assert e.tick()["needs.curiosity_hunger"] == 0


def test_restlessness_unavailable_without_gps():
    clock = [0.0]
    e = _engine({"wifi.encounters.lifetime_unique": 1, "gps.state": "unavailable"}, clock)
    clock[0] = 3600.0
    assert e.tick()["needs.restlessness"] is None  # can't know movement without GPS (ADR-0008)


def test_restlessness_unavailable_when_gps_is_stale():
    # A stalled GPS collector keeps its last values but the registry marks them stale; frozen motion
    # must not read as live -> restlessness is unavailable, same as no GPS at all (ADR-0008).
    clock = [0.0]
    s = MetaState({"gps.state": "fixed", "context.motion.state": "walking"}, stale=["gps.state"])
    e = NeedsEngine(s, clock=lambda: clock[0])
    clock[0] = 3600.0
    assert e.tick()["needs.restlessness"] is None


def test_movement_eases_restlessness():
    clock = [0.0]
    e = _engine({"gps.state": "fixed", "context.motion.state": "stationary"}, clock)
    e.tick()
    clock[0] = 3 * 3600.0
    assert e.tick()["needs.restlessness"] > 0        # staying put -> restlessness rose
    e.state["context.motion.state"] = "walking"      # went for a walk
    clock[0] = 3 * 3600.0 + 1.0
    assert e.tick()["needs.restlessness"] == 0        # real movement eases it


def test_tiredness_integrates_heat_and_recovers():
    clock = [0.0]
    e = _engine({"system.temp.cpu_c": 55.0}, clock)
    assert e.tick()["needs.tiredness"] == 0
    e.state["system.temp.cpu_c"] = 84.0          # hot
    clock[0] = 1800.0                             # 30 min of heat
    hot = e.tick()["needs.tiredness"]
    assert hot > 0
    e.state["system.temp.cpu_c"] = 50.0          # cooled down
    clock[0] = 1800.0 + 2 * 3600.0               # a couple hours cool
    assert e.tick()["needs.tiredness"] < hot     # recovers


def test_normal_throttle_string_does_not_accrue_fatigue():
    # system.throttle.flags is "0x0" (NOT throttled) -- a truthy string. Fatigue must key on the
    # parsed governor.throttle_current bit, not the raw string, or a cool Beast tires forever.
    clock = [0.0]
    e = _engine({"system.temp.cpu_c": 50.0, "system.throttle.flags": "0x0",
                 "governor.throttle_current": False}, clock)
    e.tick()
    clock[0] = 3600.0
    assert e.tick()["needs.tiredness"] == 0          # cool + not throttled -> no fatigue
    clock2 = [0.0]
    throttled = _engine({"system.temp.cpu_c": 50.0, "system.throttle.flags": "0x4",
                         "governor.throttle_current": True}, clock2)
    throttled.tick()
    clock2[0] = 3600.0
    assert throttled.tick()["needs.tiredness"] > 0   # a real throttle bit does accrue fatigue


def test_battery_fatigue_requires_available_telemetry():
    # A dropped UPS leaves a stale percent with power.telemetry.available False -> no battery fatigue.
    clock = [0.0]
    stale = _engine({"power.battery.percent_estimate": 5.0, "power.telemetry.available": False}, clock)
    stale.tick()
    clock[0] = 3600.0
    assert stale.tick()["needs.tiredness"] is None   # the only battery driver is not live
    clock2 = [0.0]
    live = _engine({"power.battery.percent_estimate": 5.0, "power.telemetry.available": True}, clock2)
    live.tick()
    clock2[0] = 3600.0
    assert live.tick()["needs.tiredness"] > 0        # a live low battery does tire the Beast


def test_stale_thermal_driver_is_not_treated_as_live():
    # A stalled system collector retains a hot CPU temp (registry marks it stale); fatigue must not
    # integrate from stale data, and with no other live driver tiredness is unavailable (ADR-0008).
    clock = [0.0]
    s = MetaState({"system.temp.cpu_c": 84.0}, stale=["system.temp.cpu_c"])
    e = NeedsEngine(s, clock=lambda: clock[0])
    e.tick()
    clock[0] = 3600.0
    assert e.tick()["needs.tiredness"] is None


def test_need_state_resets_when_the_active_beast_changes():
    # Switching Beasts must not let the new one inherit the previous Beast's accumulated need history.
    clock = [0.0]
    e = _engine({"progression.beast.id": "A", "wifi.encounters.lifetime_unique": 10,
                 "gps.state": "fixed", "context.motion.state": "stationary",
                 "peerdex.last_seen_at": 0.0, "system.temp.cpu_c": 84.0}, clock)
    e.tick()
    clock[0] = 2 * 3600.0
    before = e.tick()
    assert before["needs.curiosity_hunger"] > 0 and before["needs.tiredness"] > 0
    e.state["progression.beast.id"] = "B"            # roster.switch to a different Beast
    out = e.tick()
    assert out["needs.curiosity_hunger"] == 0 and out["needs.tiredness"] == 0  # fresh history


def test_governor_stress_requires_fresh_system_telemetry():
    # governor.mode / throttle derive from system telemetry (system.throttle.flags); if that key is
    # stale (but power is live, so tiredness is still published) their stress must not accrue (ADR-0008).
    clock = [0.0]
    s = MetaState({"power.battery.percent_estimate": 80.0, "power.telemetry.available": True,
                   "governor.mode": "SURVIVAL", "governor.throttle_current": True,
                   "system.throttle.flags": "0x4"}, stale=["system.throttle.flags"])
    stale_sys = NeedsEngine(s, clock=lambda: clock[0])
    stale_sys.tick()
    clock[0] = 3600.0
    assert stale_sys.tick()["needs.tiredness"] == 0
    clock2 = [0.0]
    fresh_sys = _engine({"power.battery.percent_estimate": 80.0, "power.telemetry.available": True,
                         "governor.mode": "SURVIVAL", "governor.throttle_current": True,
                         "system.throttle.flags": "0x4"}, clock2)
    fresh_sys.tick()
    clock2[0] = 3600.0
    assert fresh_sys.tick()["needs.tiredness"] > 0


def test_restlessness_does_not_charge_a_gps_outage_on_recovery():
    # During an outage (motion unknown) restlessness is unavailable; on recovery it must start fresh,
    # not instantly read 100 by charging the whole unobserved gap.
    clock = [0.0]
    e = _engine({"gps.state": "fixed", "context.motion.state": "unknown"}, clock)
    e.tick()
    clock[0] = 4 * 3600.0                             # a 4h gap with movement unknowable
    assert e.tick()["needs.restlessness"] is None
    e.state["context.motion.state"] = "stationary"    # GPS recovers; sitting still
    clock[0] = 4 * 3600.0 + 1.0
    assert e.tick()["needs.restlessness"] <= 5        # resumes from the recovery, not the outage


def test_loneliness_unavailable_until_a_real_peer():
    # peerdex.last_seen_at == 0 is the "no peer ever" sentinel, not an encounter at the epoch.
    clock = [0.0]
    e = _engine({"peerdex.last_seen_at": 0.0}, clock)
    clock[0] = 3 * 3600.0
    assert e.tick()["needs.loneliness"] is None
    e.state["peerdex.last_seen_at"] = 1000.0          # first real peer observed
    clock[0] = 3 * 3600.0 + 1.0
    assert e.tick()["needs.loneliness"] == 0          # just saw a peer -> not lonely
    clock[0] = 3 * 3600.0 + 1.0 + 2 * 3600.0
    assert e.tick()["needs.loneliness"] > 0           # and it grows again afterwards


def test_temperament_modulates_rates():
    clock = [0.0]
    curious = _engine({"wifi.encounters.lifetime_unique": 1, "beast.temperament.curiosity": 95}, clock)
    incurious = _engine({"wifi.encounters.lifetime_unique": 1, "beast.temperament.curiosity": 5}, clock)
    curious.tick(); incurious.tick()
    clock[0] = 3600.0
    assert curious.tick()["needs.curiosity_hunger"] > incurious.tick()["needs.curiosity_hunger"]


def test_unavailable_temperament_defaults_to_neutral_rate():
    # beast.temperament.* may be unavailable (no active Beast). The engine must still run, using a
    # neutral rate, not crash.
    clock = [0.0]
    e = _engine({"wifi.encounters.lifetime_unique": 1, "beast.temperament.curiosity": None}, clock)
    e.tick()
    clock[0] = 2 * 3600.0
    assert 40 <= e.tick()["needs.curiosity_hunger"] <= 60
