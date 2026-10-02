from __future__ import annotations

import json
from pathlib import Path

from beastcore.db import Store
from beastcore.progression import xp_threshold
from beastcore.roster import BeastRoster, BeastRosterError, MONSTER_GLOBAL_UNLOCK


def test_founder_migration_preserves_legacy_progress(tmp_path: Path):
    legacy=tmp_path/"profile.json"
    legacy.write_text(json.dumps({
        "created_at":123.0,"xp":xp_threshold(43),"max_level":100,
        "lifetime_runtime_sec":4567.0,"runtime_award_remainder_sec":12.0,
        "seen_vendors":["A","B"],"achievements":["first_signal","level_5"],
        "counters":{"lifetime_new_aps":99,"gps_locks":4},
    }))
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=legacy,clock=lambda:1000.0)
    founder=roster.bootstrap_founder(name="Hex")
    assert founder["id"]=="founder" and founder["active"] is True
    assert founder["level"]==43
    assert founder["seen_vendors"]==["A","B"]
    assert founder["counters"]["lifetime_new_aps"]==99
    assert set(founder["achievements"])=={"first_signal","level_5"}
    assert founder["identity"]["legacy_profile_migrated"] is True


def test_multiple_beasts_keep_independent_progress_and_switching(tmp_path: Path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"missing.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder(name="Hex")
    b=roster.create_beast("Orbit",lineage_id="starcore")
    roster.update_progress(a["id"],xp=xp_threshold(43))
    roster.update_progress(b["id"],xp=xp_threshold(73))
    assert roster.get(a["id"])["level"]==43
    assert roster.get(b["id"])["level"]==73
    roster.set_active(b["id"])
    assert roster.active()["id"]==b["id"]
    assert roster.get(a["id"])["level"]==43


def test_synthesis_requires_two_alpha_level_beasts(tmp_path: Path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder(name="Hex")
    b=roster.create_beast("Orbit")
    plan=roster.synthesis_plan(a["id"],b["id"])
    assert plan["allowed"] is False
    assert len(plan["blockers"])==2


def test_monster_synthesis_preserves_parents_and_unlocks_monstergotchi(tmp_path: Path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder(name="Hex")
    b=roster.create_beast("Orbit",lineage_id="starcore")
    roster.update_progress(a["id"],xp=xp_threshold(70))
    roster.update_progress(b["id"],xp=xp_threshold(85))
    out=roster.synthesize(a["id"],b["id"],name="Nova")
    monster=out["monster"]
    assert monster["kind"]=="monster"
    assert monster["level"]==1
    assert monster["generation"]==1
    assert set(monster["parents"])=={a["id"],b["id"]}
    assert roster.get(a["id"])["level"]==70
    assert roster.get(b["id"])["level"]==85
    assert out["parents_consumed"] is False and out["parents_reset"] is False
    assert MONSTER_GLOBAL_UNLOCK in {x["id"] for x in roster.global_unlocks()}


def test_same_pair_cannot_repeat_v1_synthesis(tmp_path: Path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder();b=roster.create_beast("B")
    roster.update_progress(a["id"],xp=xp_threshold(70));roster.update_progress(b["id"],xp=xp_threshold(70))
    roster.synthesize(a["id"],b["id"])
    assert roster.synthesis_plan(b["id"],a["id"])["allowed"] is False
    try:roster.synthesize(a["id"],b["id"])
    except BeastRosterError:pass
    else:raise AssertionError("same pair must not produce another v1 Monster")
