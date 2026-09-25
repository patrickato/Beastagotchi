from __future__ import annotations

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.events import EventBus
from beastcore.progression import MONSTER_STAGES, stage_for_level, xp_threshold
from beastcore.roster import BeastRoster
from beastcore.state import StateRegistry


def setup(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder(name="Hex")
    b=roster.create_beast("Orbit",lineage_id="starcore")
    roster.update_progress(a["id"],xp=xp_threshold(70))
    roster.update_progress(b["id"],xp=xp_threshold(85))
    broker=ActionBroker(StateRegistry(),store,EventBus())
    return store,roster,broker,a,b


def test_monster_has_distinct_fallback_stage_vocabulary():
    assert stage_for_level(1,"monster")=="Origin"
    assert stage_for_level(5,"monster")=="Awakened"
    assert stage_for_level(35,"monster")=="Chimera"
    assert stage_for_level(70,"monster")=="Prime"
    assert stage_for_level(85,"monster")=="Mythic"
    assert stage_for_level(100,"monster")=="Monstergotchi"
    assert stage_for_level(70,"beast")=="Alpha"


def test_synthesis_plan_is_non_mutating_and_reports_mutation_chance(tmp_path):
    _,roster,broker,a,b=setup(tmp_path)
    before=len(roster.list())
    plan=broker.plan("roster.synthesis_plan",{"parent_a":a["id"],"parent_b":b["id"],"name":"Nova"})
    assert plan["allowed"] is True
    assert plan["creates_immediately"] is False
    assert plan["parents_consumed"] is False
    assert plan["offspring_start_level"]==1
    assert 350<=plan["mutation_chance_basis_points"]<=1000
    assert len(roster.list())==before


def test_audited_synthesis_creates_level_one_monster_and_preserves_parents(tmp_path):
    _,roster,broker,a,b=setup(tmp_path)
    ax=roster.get(a["id"])["xp"];bx=roster.get(b["id"])["xp"]
    row=broker.perform("roster.synthesize",{"parent_a":a["id"],"parent_b":b["id"],"name":"Nova"},actor="test")
    assert row["status"]=="success"
    m=row["result"]["monster"]
    assert m["kind"]=="monster"
    assert m["name"]=="Nova"
    assert m["level"]==1
    assert m["stage"]=="Origin"
    assert set(m["parents"])=={a["id"],b["id"]}
    assert roster.get(a["id"])["xp"]==ax
    assert roster.get(b["id"])["xp"]==bx


def test_same_pair_second_synthesis_is_blocked(tmp_path):
    _,_,broker,a,b=setup(tmp_path)
    first=broker.perform("roster.synthesize",{"parent_a":a["id"],"parent_b":b["id"]})
    assert first["status"]=="success"
    second=broker.perform("roster.synthesize",{"parent_a":b["id"],"parent_b":a["id"]})
    assert second["status"]=="failed"
