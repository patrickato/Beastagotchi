from __future__ import annotations

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.events import EventBus
from beastcore.progression import xp_threshold
from beastcore.roster import BeastRoster
from beastcore.state import StateRegistry


def runtime(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"missing.json",clock=lambda:1000.0)
    founder=roster.bootstrap_founder(name="Hex")
    orbit=roster.create_beast("Orbit",lineage_id="starcore")
    roster.update_progress(founder["id"],xp=xp_threshold(43))
    roster.update_progress(orbit["id"],xp=xp_threshold(73))
    broker=ActionBroker(StateRegistry(),store,EventBus())
    return store,roster,broker,founder,orbit


def test_roster_snapshot_reports_independent_creatures_and_eligibility(tmp_path):
    _,_,broker,founder,orbit=runtime(tmp_path)
    snap=broker.plan("roster.snapshot",{})
    assert snap["count"]==2
    rows={x["id"]:x for x in snap["items"]}
    assert rows[founder["id"]]["level"]==43
    assert rows[founder["id"]]["synthesis_eligible"] is False
    assert rows[orbit["id"]]["level"]==73
    assert rows[orbit["id"]]["synthesis_eligible"] is True


def test_roster_switch_is_audited_and_does_not_claim_experience_change(tmp_path):
    _,roster,broker,founder,orbit=runtime(tmp_path)
    plan=broker.plan("roster.switch",{"id":orbit["id"]})
    assert plan["allowed"] is True
    row=broker.perform("roster.switch",{"id":orbit["id"]},actor="test")
    assert row["status"]=="success"
    assert row["target"]==orbit["id"]
    assert row["result"]["experience_changed"] is False
    assert roster.active()["id"]==orbit["id"]
    assert roster.get(founder["id"])["level"]==43


def test_roster_switch_rejects_unknown_id(tmp_path):
    _,_,broker,_,_=runtime(tmp_path)
    row=broker.perform("roster.switch",{"id":"does-not-exist"},actor="test")
    assert row["status"]=="failed"
    assert row["result"]["ok"] is False
