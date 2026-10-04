"""Creature idea 1: needs persist across a restart and resume where they were (ADR-0010).

With a Store, NeedsEngine saves each need's current age plus the tiredness value; on restart it
re-anchors the timers so the Beast picks up its drives from the last save instead of starting blank.
A restored restlessness age survives the pre-GPS-fix startup window (held frozen until the first fix
realizes it). Corrupt / non-numeric persisted fields fall back to the fresh session, and a
clean-shutdown ``save()`` surfaces a real write failure. Without a Store the engine is session-live.

(Fading needs gently while powered off -- idea 1's refinement -- is a tracked follow-up, deferred
because it needs a trustworthy boot clock; it is intentionally out of this step.)
"""
from __future__ import annotations

import json

import pytest

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


def _engine(state, store, mono):
    return NeedsEngine(FakeState(state), clock=lambda: mono[0], store=store)


BASE = {"wifi.encounters.lifetime_unique": 10, "gps.state": "fixed",
        "context.motion.state": "stationary", "peerdex.last_seen_at": 5.0}


def test_needs_survive_a_restart_and_resume_where_they_were():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine(BASE, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    before = e1.tick()
    assert 40 <= before["needs.curiosity_hunger"] <= 60      # risen to ~half over 2h
    e1.save()
    # restart: fresh engine, monotonic clock resets to 0
    after = _engine(BASE, store, [0.0]).tick()
    for need in ("needs.curiosity_hunger", "needs.restlessness", "needs.loneliness"):
        assert abs(after[need] - before[need]) <= 2          # resumed where it was


def test_no_store_is_session_live():
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0)
    assert e.tick()["needs.source"] == "derived_live"
    e.save()  # no store -> no-op, must not raise


def test_corrupt_persisted_state_falls_back_to_fresh():
    store = FakeStore({"needs.persistence": {"novelty_age": "x", "tired": "xyz"}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # corrupt fields ignored -> fresh baseline


def test_a_corrupt_field_rejects_the_whole_blob_to_fresh():
    # Codex: a non-numeric baseline paired with a still-valid age must NOT half-restore into a plausible
    # live value. A present-but-corrupt field rejects the whole blob, so the session starts fresh (and
    # the tick never reaches the comparison that would TypeError).
    store = FakeStore({"needs.persistence": {
        "beast_id": None, "novelty_age": 3600.0, "novelty_val": "not-a-number",
        "move_age": 10.0, "peer_age": None, "peer_val": None, "tired": 0.0,
    }})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # fresh baseline, not a half-restored ~25


def test_an_inconsistent_null_age_pair_rejects_the_whole_blob():
    # Codex: an age present with no paired baseline (or vice-versa) is inconsistent and must not
    # half-restore -- the pair is validated together, so the whole blob falls back to a fresh session.
    store = FakeStore({"needs.persistence": {
        "beast_id": None, "novelty_age": 3600.0, "novelty_val": None,
        "move_age": None, "peer_age": None, "peer_val": None, "tired": 0.0,
    }})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # inconsistent pair -> fresh, not ~25


def test_save_surfaces_a_write_failure_but_periodic_persist_does_not():
    class BrokenStore(FakeStore):
        def set_meta_json(self, key, value):
            raise OSError("read-only filesystem")

    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=BrokenStore())
    e._persist(0.0)                                          # periodic path swallows
    with pytest.raises(OSError):
        e.save()                                             # clean-shutdown save surfaces it


def test_persisted_needs_do_not_cross_to_a_different_beast():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine({**BASE, "progression.beast.id": "A"}, store, mono)
    e1.tick()
    mono[0] = 3 * 3600.0
    e1.tick()
    e1.save()
    # restart with a different active Beast -> it must not inherit Beast A's accumulated needs
    after = _engine({**BASE, "progression.beast.id": "B"}, store, [0.0]).tick()
    assert after["needs.curiosity_hunger"] == 0


def test_restlessness_survives_the_pre_fix_gps_window():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine(BASE, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.restlessness"] >= 40               # ~50 after 2h stationary
    st = FakeState({**BASE, "gps.state": "unavailable", "context.motion.state": "unknown"})
    e2 = NeedsEngine(st, clock=lambda: 0.0, store=store)
    assert e2.tick()["needs.restlessness"] is None          # pre-fix: unavailable, age preserved
    st["gps.state"] = "fixed"
    st["context.motion.state"] = "stationary"
    assert e2.tick()["needs.restlessness"] >= 40            # first fix realizes the restored age


def test_restlessness_is_frozen_during_a_long_pre_fix_window():
    # The restored age must be held constant through the pre-fix window, not advanced by the unknown
    # interval: a 4h GPS-less boot must not turn a restored ~50 into 100 on the first fix.
    store = FakeStore()
    mono = [0.0]
    e1 = _engine(BASE, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.restlessness"] >= 40
    m2 = [0.0]
    st = FakeState({**BASE, "gps.state": "unavailable", "context.motion.state": "unknown"})
    e2 = NeedsEngine(st, clock=lambda: m2[0], store=store)
    e2.tick()
    m2[0] = 4 * 3600.0                                       # 4h of GPS-unavailable uptime
    assert e2.tick()["needs.restlessness"] is None
    st["gps.state"] = "fixed"
    st["context.motion.state"] = "stationary"
    realized = e2.tick()["needs.restlessness"]
    assert abs(realized - before["needs.restlessness"]) <= 5  # ~50, not the 100 a charged 4h gap gives
