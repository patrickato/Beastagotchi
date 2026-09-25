from __future__ import annotations

import json
from pathlib import Path

from beastcore.db import Store
from beastcore.progression import ProgressionEngine, xp_threshold
from beastcore.roster_progression import ActiveBeastProgressionStore
from beastcore.state import StateRegistry


def make_runtime(tmp_path: Path, legacy: dict | None = None):
    legacy_path = tmp_path / "profile.json"
    if legacy is not None:
        legacy_path.write_text(json.dumps(legacy))
    store = Store(str(tmp_path / "beast.db"))
    pstore = ActiveBeastProgressionStore(
        store,
        legacy_profile_path=legacy_path,
        clock=lambda: 1000.0,
    )
    state = StateRegistry()
    engine = ProgressionEngine(state, profile_store=pstore)
    return store, pstore, state, engine, legacy_path


def test_founder_migration_becomes_live_progression_truth(tmp_path: Path):
    _, pstore, state, _, _ = make_runtime(
        tmp_path,
        {
            "created_at": 123.0,
            "xp": xp_threshold(43),
            "max_level": 100,
            "lifetime_runtime_sec": 4567.0,
            "runtime_award_remainder_sec": 12.0,
            "seen_vendors": ["Acme"],
            "achievements": ["first_signal"],
            "last_achievement": "First Signal",
            "counters": {"lifetime_new_aps": 99},
        },
    )
    assert state.get("progression.storage") == "roster"
    assert state.get("progression.beast.id") == "founder"
    assert state.get("progression.level") == 43
    assert pstore.load_profile("founder")["last_achievement"] == "First Signal"


def test_switching_active_creature_redirects_xp_without_overwriting_founder(tmp_path: Path):
    _, pstore, state, engine, _ = make_runtime(tmp_path, {"xp": 0, "counters": {}})
    founder_id = pstore.current_id()
    orbit = pstore.roster.create_beast("Orbit", lineage_id="starcore")
    engine._award(20, "founder-test")
    founder_xp = pstore.roster.get(founder_id)["xp"]
    pstore.roster.set_active(orbit["id"])
    engine._award(40, "orbit-test")
    assert state.get("progression.beast.id") == orbit["id"]
    assert pstore.roster.get(founder_id)["xp"] == founder_xp
    assert pstore.roster.get(orbit["id"])["xp"] == 40


def test_restart_reloads_current_active_creature(tmp_path: Path):
    store, pstore, _, engine, legacy_path = make_runtime(tmp_path)
    orbit = pstore.roster.create_beast("Orbit", activate=True)
    engine._award(123, "restart-test")
    state2 = StateRegistry()
    pstore2 = ActiveBeastProgressionStore(
        store,
        legacy_profile_path=legacy_path,
        clock=lambda: 1001.0,
    )
    ProgressionEngine(state2, profile_store=pstore2)
    assert state2.get("progression.beast.id") == orbit["id"]
    assert state2.get("progression.xp") == 123


def test_founder_progress_keeps_legacy_rollback_mirror_current(tmp_path: Path):
    _, pstore, _, engine, legacy_path = make_runtime(tmp_path, {"xp": 0, "counters": {}})
    engine._award(33, "founder-mirror")
    mirrored = json.loads(legacy_path.read_text())
    assert mirrored["xp"] == 33
    assert pstore.roster.get("founder")["xp"] == 33


def test_non_founder_never_replaces_founder_legacy_mirror(tmp_path: Path):
    _, pstore, _, engine, legacy_path = make_runtime(tmp_path, {"xp": 7, "counters": {}})
    original = json.loads(legacy_path.read_text())["xp"]
    other = pstore.roster.create_beast("Other", activate=True)
    engine._award(77, "other-beast")
    assert json.loads(legacy_path.read_text())["xp"] == original
    assert pstore.roster.get(other["id"])["xp"] == 77


def test_roster_summary_published_without_changing_existing_progression_keys(tmp_path: Path):
    _, pstore, state, engine, _ = make_runtime(tmp_path)
    pstore.roster.create_beast("B")
    pstore.roster.create_beast("C")
    engine._publish_state()
    summary = state.get("progression.roster.summary")
    assert summary["total"] == 3
    assert summary["beasts"] == 3
    assert isinstance(state.get("progression.level"), int)


def test_roster_summary_counts_hall_inductees_by_legend_marker(tmp_path: Path):
    _, pstore, _, _, _ = make_runtime(tmp_path)
    founder = pstore.roster.get("founder")
    pstore.roster.update_progress(founder["id"], xp=xp_threshold(100))
    pstore.roster.set_legend(founder["id"], True)
    summary = pstore.roster_summary()
    assert summary["legends"] == 1
