"""Creature idea 1: needs persist across a restart and fade gently while powered off (ADR-0010).

With a Store, NeedsEngine saves each need's current age (capped at saturation) plus the tiredness
value and a wall-clock stamp; on restore it ages them by the powered-off duration with a half-life
decay, applied only once the boot wall clock is trustworthy. A quick reboot resumes the Beast where it
was; a long absence relaxes it toward neutral. Without a Store the engine is session-live.

Also covers the Codex review findings: the half-life halves a *saturated* need's value, a restored
restlessness age survives the pre-fix GPS window, a behind/unset boot clock defers decay instead of
baking in skew, non-numeric persisted baselines fall back without crashing, and a clean-shutdown
``save()`` surfaces a real write failure.
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


def _engine(state, store, mono, wall):
    return NeedsEngine(FakeState(state), clock=lambda: mono[0], wall_clock=lambda: wall[0], store=store)


def _settle(engine, n=3):
    # The powered-off fade is applied lazily once the wall clock is confirmed stable (two consistent
    # readings), so a few ticks are needed before the decayed values appear.
    out = {}
    for _ in range(n):
        out = engine.tick()
    return out


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
    after = _settle(_engine(BASE, store, mono2, wall2))
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
    after = _settle(_engine({**BASE, "system.temp.cpu_c": 84.0}, store, mono2, wall2))
    assert after["needs.curiosity_hunger"] < before["needs.curiosity_hunger"]
    assert after["needs.curiosity_hunger"] <= before["needs.curiosity_hunger"] // 2
    assert after["needs.tiredness"] < before["needs.tiredness"]   # a long rest while off


def test_a_saturated_need_still_halves_over_a_half_life():
    # Codex P1: fading an unbounded age leaves a saturated need pinned at 100; the cap-at-saturation
    # makes the half-life act on the need *value*, so one 6h half-life takes 100 -> ~50.
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 12 * 3600.0, 1000.0 + 12 * 3600.0     # curiosity saturated (100) long ago
    before = e1.tick()
    e1.save()
    assert before["needs.curiosity_hunger"] == 100
    mono2, wall2 = [0.0], [wall[0] + 6 * 3600.0]             # exactly one half-life off
    after = _settle(_engine(BASE, store, mono2, wall2))
    assert 40 <= after["needs.curiosity_hunger"] <= 60       # ~50, not still 100


def test_restlessness_survives_the_pre_fix_gps_window():
    # Codex P1: on a real restart the first ticks can run before GPS has a fix; the restored
    # restlessness age must survive that window and be realized by the first fix, not reset to ~0.
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 2 * 3600.0, 1000.0 + 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.restlessness"] >= 40               # ~50 after 2h stationary
    mono2, wall2 = [0.0], [wall[0] + 30.0]
    st = FakeState({**BASE, "gps.state": "unavailable", "context.motion.state": "unknown"})
    e2 = NeedsEngine(st, clock=lambda: mono2[0], wall_clock=lambda: wall2[0], store=store)
    assert e2.tick()["needs.restlessness"] is None          # pre-fix: unavailable, age preserved
    assert e2.tick()["needs.restlessness"] is None
    st["gps.state"] = "fixed"
    st["context.motion.state"] = "stationary"
    assert e2.tick()["needs.restlessness"] >= 40            # first fix realizes the restored age


def test_a_behind_boot_clock_defers_decay_until_it_syncs():
    # Codex P1: an unset RTC can read behind the save stamp at boot; treating that skew as a huge
    # outage would wrongly decay the needs. Preserve them until the clock syncs forward, then fade.
    store = FakeStore()
    mono, wall = [0.0], [10_000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 3 * 3600.0, 10_000.0 + 3 * 3600.0
    before = e1.tick()
    e1.save()
    saved_wall = wall[0]
    mono2, wall2 = [0.0], [500.0]                            # RTC unset: reads behind the save stamp
    e2 = _engine(BASE, store, mono2, wall2)
    e2.tick(); e2.tick()
    assert e2.tick()["needs.curiosity_hunger"] >= before["needs.curiosity_hunger"] - 2  # preserved, not decayed
    wall2[0] = saved_wall + 12 * 3600.0                      # clock syncs forward (12h after save)
    after = _settle(e2)
    assert after["needs.curiosity_hunger"] < before["needs.curiosity_hunger"] // 2      # now it fades


def test_no_store_is_session_live():
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}), clock=lambda: 0.0)
    assert e.tick()["needs.source"] == "derived_live"
    e.save()  # no store -> no-op, must not raise


def test_corrupt_persisted_state_falls_back_to_fresh():
    store = FakeStore({"needs.persistence": {"saved_at": "not-a-number", "tired": "xyz"}})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}),
                    clock=lambda: 0.0, wall_clock=lambda: 9999.0, store=store)
    assert e.tick()["needs.curiosity_hunger"] == 0           # ignored corrupt blob -> fresh baseline


def test_nonnumeric_persisted_baseline_does_not_crash_the_tick():
    # Codex P2: a blob with valid stamps but a non-numeric novelty_val previously passed restore and
    # then raised TypeError on the first live comparison, wedging the personality loop.
    store = FakeStore({"needs.persistence": {
        "saved_at": 1000.0, "beast_id": None,
        "novelty_age": 3600.0, "novelty_val": "not-a-number",
        "move_age": 10.0, "peer_age": None, "peer_val": None, "tired": 0.0,
    }})
    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}),
                    clock=lambda: 0.0, wall_clock=lambda: 1000.0, store=store)
    out = e.tick()                                           # must not raise
    assert out["needs.curiosity_hunger"] is not None


def test_save_surfaces_a_write_failure_but_periodic_persist_does_not():
    # Codex P2: the clean-shutdown save must report a real write error (so BeastCore.run can log it),
    # while a periodic in-tick persist swallows transient errors so the loop never dies.
    class BrokenStore(FakeStore):
        def set_meta_json(self, key, value):
            raise OSError("read-only filesystem")

    e = NeedsEngine(FakeState({"wifi.encounters.lifetime_unique": 10}),
                    clock=lambda: 0.0, wall_clock=lambda: 1000.0, store=BrokenStore())
    e._persist(0.0)                                          # periodic path swallows
    with pytest.raises(OSError):
        e.save()                                             # clean-shutdown save surfaces it


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
    after = _settle(_engine({**BASE, "progression.beast.id": "B"}, store, mono2, wall2))
    assert after["needs.curiosity_hunger"] == 0


def test_restlessness_is_frozen_during_a_long_pre_fix_window():
    # Codex round-2 P1: while waiting for the first boot fix, the restored restlessness age must be held
    # constant, not advanced by the unknown pre-fix interval -- a 4h GPS-less uptime must not turn a
    # restored ~50 into 100 on the first fix.
    store = FakeStore()
    mono, wall = [0.0], [1000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 2 * 3600.0, 1000.0 + 2 * 3600.0
    before = e1.tick()
    e1.save()
    assert before["needs.restlessness"] >= 40
    mono2, wall2 = [0.0], [wall[0] + 30.0]
    st = FakeState({**BASE, "gps.state": "unavailable", "context.motion.state": "unknown"})
    e2 = NeedsEngine(st, clock=lambda: mono2[0], wall_clock=lambda: wall2[0], store=store)
    e2.tick()
    mono2[0] = 4 * 3600.0                                     # 4h of GPS-unavailable uptime
    assert e2.tick()["needs.restlessness"] is None
    st["gps.state"] = "fixed"
    st["context.motion.state"] = "stationary"
    realized = e2.tick()["needs.restlessness"]
    assert abs(realized - before["needs.restlessness"]) <= 5  # ~50, not the 100 a charged 4h gap gives


def test_save_while_decay_pending_preserves_the_trusted_checkpoint():
    # Codex round-2 P1: a behind boot clock must not overwrite the trusted checkpoint, or a later clock
    # sync could no longer recover the real outage.
    store = FakeStore()
    mono, wall = [0.0], [10_000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 3 * 3600.0, 10_000.0 + 3 * 3600.0
    e1.tick()
    e1.save()
    trusted_stamp = store.get_meta_json(NeedsEngine.META_KEY)["saved_at"]
    mono2, wall2 = [0.0], [500.0]                             # RTC unset: behind the save stamp
    e2 = _engine(BASE, store, mono2, wall2)
    e2.tick()
    mono2[0] = 120.0                                          # enough that a periodic save would fire
    e2.tick()
    e2.save()                                                 # must not overwrite with the untrusted stamp
    assert store.get_meta_json(NeedsEngine.META_KEY)["saved_at"] == trusted_stamp


def test_a_live_discovery_during_deferral_is_not_overwritten_by_decay():
    # Codex round-2 P1: a lifetime-first discovery observed while decay is deferred eases hunger now;
    # applying the deferred fade later must not resurrect the stale pre-restart hunger.
    store = FakeStore()
    mono, wall = [0.0], [10_000.0]
    e1 = _engine(BASE, store, mono, wall)
    e1.tick()
    mono[0], wall[0] = 3 * 3600.0, 10_000.0 + 3 * 3600.0
    before = e1.tick()
    e1.save()
    saved_wall = wall[0]
    assert before["needs.curiosity_hunger"] >= 60
    mono2, wall2 = [0.0], [500.0]                             # behind clock -> decay deferred
    st = FakeState({**BASE})
    e2 = NeedsEngine(st, clock=lambda: mono2[0], wall_clock=lambda: wall2[0], store=store)
    e2.tick()
    st["wifi.encounters.lifetime_unique"] = 11               # a brand-new discovery during the deferral
    mono2[0] = 1.0
    assert e2.tick()["needs.curiosity_hunger"] <= 5          # eased to ~0 by the fresh discovery
    wall2[0] = saved_wall + 12 * 3600.0                      # clock finally syncs forward
    mono2[0] = 2.0
    assert e2.tick()["needs.curiosity_hunger"] <= 5          # decay must not resurrect the old hunger
