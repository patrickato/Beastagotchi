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
                 "gps.session_distance_m": 0.0, "peerdex.last_seen_at": 0.0}, clock)
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
    # A stalled GPS collector keeps its last values (quality marked stale); frozen distance must not
    # read as "not moving" -> restlessness is unavailable, same as no GPS at all (ADR-0008).
    clock = [0.0]
    e = _engine({"gps.state": "fixed", "gps.session_distance_m": 100.0,
                 "health.collector.gps.state": "stale"}, clock)
    clock[0] = 3600.0
    assert e.tick()["needs.restlessness"] is None


def test_movement_eases_restlessness():
    clock = [0.0]
    e = _engine({"gps.state": "fixed", "gps.session_distance_m": 0.0}, clock)
    e.tick()
    clock[0] = 3 * 3600.0
    assert e.tick()["needs.restlessness"] > 0
    e.state["gps.session_distance_m"] = 500.0  # went for a walk
    clock[0] = 3 * 3600.0 + 1.0
    assert e.tick()["needs.restlessness"] == 0


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
