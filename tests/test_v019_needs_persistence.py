"""Creature idea 1 (scope B): the clock-independent needs persist across a restart (ADR-0010).

Only **curiosity-hunger** (its baseline is a monotonic discovery count) and **tiredness** (a stored
value) persist and resume on restart. **loneliness** (a peer wall-clock timestamp) and **restlessness**
(GPS) are deliberately session-live here; their cross-restart resume, and fading while powered off, are
deferred to the follow-up (#56) with a clock-robust design.

The whole persisted blob is validated before any of it is applied, so a partial / corrupt / tampered
blob falls back to a fresh session rather than half-restoring into plausible live telemetry (ADR-0008):
a non-finite field, a missing required field (tired), or an inconsistent novelty (baseline, age) pair
each reject the blob. A pathologically large restored age cannot overflow the need math. A transient
read error preserves the checkpoint and reports the persisted needs unavailable for that session; the next
restart resumes cleanly from the preserved checkpoint (a checkpoint is applied only at construction, never
injected mid-session).
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
HOT = {**BASE, "system.temp.cpu_c": 84.0}


def test_novelty_and_tiredness_persist_but_clock_needs_do_not():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine(HOT, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert 40 <= before["needs.curiosity_hunger"] <= 60      # ~50 over 2h
    assert before["needs.tiredness"] > 40                    # hot for 2h
    assert before["needs.restlessness"] >= 40                # ~50 stationary
    assert before["needs.loneliness"] >= 40                  # ~50
    # restart: fresh engine, monotonic resets to 0
    after = _engine(HOT, store, [0.0]).tick()
    assert abs(after["needs.curiosity_hunger"] - before["needs.curiosity_hunger"]) <= 2   # resumed
    assert after["needs.tiredness"] >= before["needs.tiredness"] - 5                      # resumed
    # loneliness & restlessness are session-live (not persisted) -> fresh after a restart
    assert after["needs.restlessness"] == 0
    assert after["needs.loneliness"] == 0


def test_no_store_is_session_live():
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0)
    assert e.tick()["needs.source"] == "derived_live"
    e.save()  # no store -> no-op, must not raise


def test_a_corrupt_field_rejects_the_whole_blob_to_fresh():
    store = FakeStore({"needs.persistence": {"novelty_age": "x", "novelty_val": 5.0, "tired": 0.0}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # non-finite field -> fresh baseline


def test_an_inconsistent_novelty_pair_rejects_the_whole_blob():
    store = FakeStore({"needs.persistence": {"novelty_age": 3600.0, "novelty_val": None, "tired": 0.0}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # age without a baseline -> fresh


def test_a_null_required_tired_field_rejects_the_whole_blob():
    store = FakeStore({"needs.persistence": {"novelty_age": 3600.0, "novelty_val": 10.0, "tired": None}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # tired is required -> whole blob rejected


def test_a_huge_restored_age_does_not_overflow():
    # A JSON-finite but absurd age must not overflow _rise() into inf/OverflowError.
    store = FakeStore({"needs.persistence": {"novelty_age": 1e308, "novelty_val": 999.0, "tired": 0.0}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 100         # saturates cleanly, no crash


def test_a_float_overflowing_integer_field_rejects_the_whole_blob():
    # A JSON-valid but corrupt checkpoint can hold an integer too large to convert to float
    # (float(10**400) raises OverflowError). It must reject the blob -> fresh session, not crash boot.
    store = FakeStore({"needs.persistence": {"novelty_age": 3600.0, "novelty_val": 10.0, "tired": 10 ** 400}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # construction survived, blob rejected -> fresh


def test_an_out_of_range_tired_rejects_the_whole_blob():
    # tired is 0..100 by definition; a finite-but-impossible value must reject the blob, not clamp to 0/100.
    # Detected via curiosity: an accepted blob would restore novelty_age=3600 (curiosity > 0); a rejected
    # one starts novelty fresh (curiosity 0).
    for bad in (1e308, -1.0, 250.0):
        store = FakeStore({"needs.persistence": {"novelty_age": 3600.0, "novelty_val": 10.0, "tired": bad}})
        e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.curiosity_hunger"] == 0


def test_a_negative_novelty_field_rejects_the_whole_blob():
    # novelty count and age are non-negative by construction; a negative value is corruption -> reject the
    # whole blob, not clamp it. Detected via tiredness: a rejected blob starts fresh at 0 rather than 40.
    for bad in ({"novelty_age": -5.0, "novelty_val": 10.0}, {"novelty_age": 3600.0, "novelty_val": -1.0}):
        store = FakeStore({"needs.persistence": {**bad, "tired": 40.0}})
        e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0


def test_save_surfaces_a_write_failure_but_periodic_persist_does_not():
    class BrokenWriteStore(FakeStore):
        def set_meta_json(self, key, value):
            raise OSError("read-only filesystem")

    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=BrokenWriteStore())
    e._persist(0.0)                                          # periodic path swallows
    with pytest.raises(OSError):
        e.save()                                             # clean-shutdown save surfaces it


def test_a_read_error_preserves_the_checkpoint_and_resumes_on_restart():
    saved = {"beast_id": None, "novelty_age": 3600.0, "novelty_val": 5.0, "tired": 40.0}

    class FlakyReadStore(FakeStore):
        def __init__(self, data=None):
            super().__init__(data)
            self.fail = True

        def get_meta_json(self, key, default=None):
            if self.fail:
                raise OSError("temporary read error")
            return super().get_meta_json(key, default)

    store = FlakyReadStore({"needs.persistence": dict(saved)})
    e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
    out = e.tick()
    assert out["needs.curiosity_hunger"] is None             # persisted needs unavailable while unreadable
    assert out["needs.tiredness"] is None
    e._persist(0.0)                                          # must NOT overwrite the checkpoint while failed
    assert store._d["needs.persistence"] == saved
    store.fail = False                                       # storage recovers mid-session...
    out2 = e.tick()
    assert out2["needs.curiosity_hunger"] is None            # ...but a checkpoint is applied only at
    assert out2["needs.tiredness"] is None                   # construction, never injected mid-session
    resumed = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store).tick()  # the next restart
    assert resumed["needs.curiosity_hunger"] is not None     # resumes cleanly from the preserved checkpoint
    assert resumed["needs.tiredness"] is not None


def test_persisted_needs_do_not_cross_to_a_different_beast():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine({**BASE, "progression.beast.id": "A"}, store, mono)
    e1.tick()
    mono[0] = 3 * 3600.0
    e1.tick()
    e1.save()
    after = _engine({**BASE, "progression.beast.id": "B"}, store, [0.0]).tick()
    assert after["needs.curiosity_hunger"] == 0              # Beast B does not inherit Beast A's needs
