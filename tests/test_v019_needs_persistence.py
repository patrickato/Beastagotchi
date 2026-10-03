"""Creature idea 1: needs persist across a restart and fade gently while powered off (ADR-0010).

With a Store, NeedsEngine saves each need's current age (plus the tiredness integrator) and a wall-clock
stamp; on restore it ages them by the powered-off duration with a half-life decay. A quick reboot
resumes the Beast where it was; a long absence relaxes it toward neutral rather than freezing or
resetting it. Without a Store the engine is session-live.
"""
from __future__ import annotations

import json

from beastcore.needs import NeedsEngine


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class FakeStore:
    """Dict-backed stand-in for the Store meta KV, with a JSON round-trip like the real one."""
    def __init__(self, data=None):
        self._d = dict(data or {})

    def get_meta_json(self, key, default=None):
        return self._d.get(key, default)

    def set_meta_json(self, key, value):
        self._d[key] = json.loads(json.dumps(value, default=str))
        return True


def _engine(state, store, mono, wall):
    return NeedsEngine(FakeState(state), clock=lambda: mono[0], wall_clock=lambda: wall[0], store=store)


BASE = {"wifi.encounters.lifetime_unique": 10, "gps.state": "fixed",
        "context.motion.state": "stationary", "peerdex.last_seen_at": 5.0}


def test_needs_survive_a_quick_restart():
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 2 * 3600.0, 1000.0 + 2 * 3600.0
    before = e1.tick()
    assert 40 <= before["needs.curiosity_hunger"] <= 60      # risen to ~half over 2h
    e1.save()                                                # clean shutdown flush
    # restart: fresh engine (monotonic clock resets to 0), only ~30s powered off
    mono2, wall2 = [0.0], [wall[0] + 30.0]
    after = _engine(BASE, store, mono2, wall2).tick()
    for need in ("needs.curiosity_hunger", "needs.restlessness", "needs.loneliness"):
        assert abs(after[need] - before[need]) <= 2          # essentially intact across the quick reboot


def test_needs_fade_toward_relaxed_while_powered_off():
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine({**BASE, "system.temp.cpu_c": 84.0}, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 3 * 3600.0, 1000.0 + 3 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.curiosity_hunger"] >= 60            # ~75 after 3h
    assert before["needs.tiredness"] > 50                    # hot for 3h
    # restart after 12h off = two 6h half-lives -> needs ~1/4
    mono2, wall2 = [0.0], [wall[0] + 12 * 3600.0]
    after = _engine({**BASE, "system.temp.cpu_c": 84.0}, store, mono2, wall2).tick()
    assert after["needs.curiosity_hunger"] < before["needs.curiosity_hunger"]
    assert after["needs.curiosity_hunger"] <= before["needs.curiosity_hunger"] // 2
    assert after["needs.tiredness"] < before["needs.tiredness"]   # a long rest while off


def test_no_store_is_session_live():
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0)
    assert e.tick()["needs.source"] == "derived_live"
    e.save()  # no store -> no-op, must not raise


def test_corrupt_persisted_state_falls_back_to_fresh():
    store = FakeStore({"needs.persistence": {"saved_at": "not-a-number", "tired": "xyz"}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}),
                    clock=lambda: 0.0, wall_clock=lambda: 9999.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # ignored corrupt blob -> fresh baseline


def test_persisted_needs_do_not_cross_to_a_different_beast():
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine({**BASE, "progression.beast.id": "A"}, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 3 * 3600.0, 1000.0 + 3 * 3600.0
    e1.tick()
    e1.save()
    # restart with a different active Beast -> it must not inherit Beast A's accumulated needs
    mono2, wall2 = [0.0], [wall[0] + 30.0]
    after = _engine({**BASE, "progression.beast.id": "B"}, store, mono2, wall2).tick()
    assert after["needs.curiosity_hunger"] == 0
