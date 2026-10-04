"""Creature idea 1 (scope C): only **tiredness** persists across a restart (ADR-0010).

Tiredness is a self-contained stored 0..100 value, so it persists and resumes on restart. curiosity-hunger,
loneliness and restlessness are deliberately session-live here: curiosity's baseline depends on which
discovery counter sourced it and on agreeing with the live count across a restart, so it joins loneliness
(peer wall-clock) and restlessness (GPS) in the clock-robust, source-stable cross-restart work deferred to
the follow-up (#56).

The persisted blob is validated before it is applied, so a corrupt / out-of-range / tampered one falls back
to a fresh session rather than half-restoring into plausible live telemetry (ADR-0008): a missing/null,
non-finite, float-overflowing, or out-of-range ``tired`` each reject the blob. A transient read error
preserves the checkpoint and reports tiredness unavailable for that session; the next restart resumes
cleanly from the preserved checkpoint (a checkpoint is applied only at construction, never injected
mid-session). A boot read-fault does not carry over to a Beast activated later in the same run.
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


def test_tiredness_persists_but_the_session_live_needs_do_not():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine(HOT, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.tiredness"] > 40                     # hot for 2h
    assert before["needs.curiosity_hunger"] >= 40             # ~50 over 2h (session-live)
    assert before["needs.restlessness"] >= 40                 # ~50 stationary
    assert before["needs.loneliness"] >= 40                   # ~50
    # restart: fresh engine, monotonic resets to 0
    after = _engine(HOT, store, [0.0]).tick()
    assert after["needs.tiredness"] >= before["needs.tiredness"] - 5   # tiredness resumed
    # everything else is session-live (not persisted) -> fresh after a restart
    assert after["needs.curiosity_hunger"] == 0
    assert after["needs.restlessness"] == 0
    assert after["needs.loneliness"] == 0


def test_no_store_is_session_live():
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0)
    assert e.tick()["needs.source"] == "derived_live"
    e.save()  # no store -> no-op, must not raise


def test_a_null_or_missing_tired_field_rejects_the_whole_blob():
    for blob in ({"beast_id": None, "tired": None}, {"beast_id": None}):   # null, then absent
        store = FakeStore({"needs.persistence": blob})
        e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0              # tired required -> blob rejected -> fresh


def test_a_corrupt_or_nonfinite_tired_rejects_the_whole_blob():
    for bad in ("x", float("nan"), float("inf")):
        store = FakeStore({"needs.persistence": {"beast_id": None, "tired": bad}})
        e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0              # non-finite/non-numeric -> rejected -> fresh


def test_a_float_overflowing_integer_tired_rejects_the_whole_blob():
    # A JSON-valid but corrupt checkpoint can hold an integer too large to convert to float
    # (float(10**400) raises OverflowError). It must reject the blob -> fresh session, not crash boot.
    store = FakeStore({"needs.persistence": {"beast_id": None, "tired": 10 ** 400}})
    e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
    assert e.tick()["needs.tiredness"] == 0                  # construction survived, blob rejected -> fresh


def test_an_out_of_range_tired_rejects_the_whole_blob():
    # tired is 0..100 by definition; a finite-but-impossible value must reject the blob, not clamp to 0/100.
    for bad in (1e308, -1.0, 250.0):
        store = FakeStore({"needs.persistence": {"beast_id": None, "tired": bad}})
        e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0


def test_a_checkpoint_without_a_valid_owner_is_rejected():
    # A checkpoint must prove it belongs to the active Beast: a missing beast_id (no provenance) or a
    # different Beast's id must take the fresh fallback, not bleed fatigue into the active Beast.
    for blob in ({"tired": 90.0}, {"beast_id": "A", "tired": 90.0}):
        store = FakeStore({"needs.persistence": blob})
        e = NeedsEngine(FakeState({**HOT, "progression.beast.id": "B"}), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0              # rejected -> Beast B starts fresh, not 90


def test_a_boolean_or_string_tired_is_rejected():
    # _persist emits a JSON number; a bool or numeric string is tampering. float() would coerce True->1.0
    # and "90"->90.0, so the type must be rejected before coercion (ADR-0008 fresh fallback).
    for bad in (True, "90"):
        store = FakeStore({"needs.persistence": {"beast_id": None, "tired": bad}})
        e = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store)
        assert e.tick()["needs.tiredness"] == 0              # type-confused tired -> rejected -> fresh


def test_save_surfaces_a_write_failure_but_periodic_persist_does_not():
    class BrokenWriteStore(FakeStore):
        def set_meta_json(self, key, value):
            raise OSError("read-only filesystem")

    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0, store=BrokenWriteStore())
    e._persist(0.0)                                          # periodic path swallows
    with pytest.raises(OSError):
        e.save()                                             # clean-shutdown save surfaces it


def test_a_read_error_preserves_the_checkpoint_and_resumes_on_restart():
    saved = {"beast_id": None, "tired": 40.0}

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
    assert out["needs.tiredness"] is None                    # persisted need unavailable while unreadable
    assert out["needs.curiosity_hunger"] is not None         # curiosity is session-live -> unaffected
    e._persist(0.0)                                          # must NOT overwrite the checkpoint while failed
    assert store._d["needs.persistence"] == saved
    store.fail = False                                       # storage recovers mid-session...
    assert e.tick()["needs.tiredness"] is None               # ...but a checkpoint is applied only at construction
    resumed = NeedsEngine(FakeState(HOT), clock=lambda: 0.0, store=store).tick()  # the next restart
    assert resumed["needs.tiredness"] is not None            # resumes cleanly from the preserved checkpoint


def test_a_beast_switch_clears_a_boot_read_fault():
    # A boot read failure makes the booted Beast's tiredness unavailable, but activating a DIFFERENT Beast
    # starts a fresh, persistable session -- the previous Beast's read fault must not carry over.
    class FailingReadStore(FakeStore):
        def __init__(self, data=None):
            super().__init__(data)
            self.fail = True

        def get_meta_json(self, key, default=None):
            if self.fail:
                raise OSError("boot read error")
            return super().get_meta_json(key, default)

    store = FailingReadStore()
    state = FakeState({**HOT, "progression.beast.id": "A"})
    e = NeedsEngine(state, clock=lambda: 0.0, store=store)
    assert e.tick()["needs.tiredness"] is None               # A's checkpoint unreadable -> unavailable
    state["progression.beast.id"] = "B"                      # operator activates a different Beast
    assert e.tick()["needs.tiredness"] is not None           # B is a fresh session, not poisoned by A's fault


def test_tiredness_does_not_cross_to_a_different_beast():
    store = FakeStore()
    mono = [0.0]
    e1 = _engine({**HOT, "progression.beast.id": "A"}, store, mono)
    e1.tick()
    mono[0] = 2 * 3600.0
    e1.tick()
    e1.save()                                                # A's fatigue (hot 2h) persisted
    after = _engine({**HOT, "progression.beast.id": "B"}, store, [0.0]).tick()
    assert after["needs.tiredness"] == 0                     # Beast B does not inherit Beast A's fatigue
