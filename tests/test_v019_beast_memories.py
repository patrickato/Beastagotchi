from __future__ import annotations

from types import SimpleNamespace

from beastcore.db import Store
from beastcore.memories import BeastMemoryEngine
from beastcore.roster import BeastRoster
from beastcore.state import StateRegistry


class Clock:
    def __init__(self):self.wall=1000.0;self.mono=10.0
    def time(self):return self.wall
    def monotonic(self):return self.mono


def setup(tmp_path):
    c=Clock();store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=c.time)
    founder=roster.bootstrap_founder(name="Hex")
    state=StateRegistry();mem=BeastMemoryEngine(state,store,roster,clock=c.time,mono=c.monotonic)
    return c,store,roster,founder,state,mem


def ev(eid,etype,data=None,ts=1000.0):
    return SimpleNamespace(id=eid,type=etype,data=data or {},ts=ts)


def test_meaningful_progression_event_becomes_beast_memory(tmp_path):
    _,_,_,founder,_,mem=setup(tmp_path)
    assert mem.record_event(ev("e1","progression.level_up",{"from":9,"to":10,"stage":"Scout","xp":200})) is True
    rows=mem.recent(founder["id"])
    assert len(rows)==1
    assert rows[0]["kind"]=="level"
    assert "level 10" in rows[0]["summary"]


def test_raw_unlisted_event_is_not_duplicated_into_memory(tmp_path):
    _,_,_,founder,_,mem=setup(tmp_path)
    assert mem.record_event(ev("e1","wifi.ap_discovered",{"aps":[{"bssid":"secret"}]})) is False
    assert mem.summary(founder["id"])["memory_count"]==0


def test_rare_memory_keeps_only_sanitized_fields(tmp_path):
    _,_,_,founder,_,mem=setup(tmp_path)
    mem.record_event(ev("r1","rare.moment.acknowledged",{
        "id":"rare-1","rarity":"legendary","sigil":"eye","presentation":"ghost",
        "latitude":42.0,"ssid":"private",
    }))
    row=mem.recent(founder["id"])[0]
    assert row["rarity"]=="legendary"
    assert "latitude" not in row["data"] and "ssid" not in row["data"]


def test_expedition_membership_is_throttled_and_per_beast(tmp_path):
    c,store,roster,founder,_,mem=setup(tmp_path)
    patch={"expedition.active":True,"expedition.id":"exp-1"}
    mem.observe_expedition(patch)
    c.wall+=10;mem.observe_expedition(patch)
    assert mem.summary(founder["id"])["expedition_count"]==1
    other=roster.create_beast("Orbit",activate=True)
    c.wall+=1;mem.observe_expedition(patch)
    assert mem.summary(other["id"])["expedition_count"]==1


def test_personality_transition_requires_stability_before_memory(tmp_path):
    c,_,_,founder,_,mem=setup(tmp_path)
    patch={"beast.mood":"curious","beast.energy":70,"beast.curiosity":90,"beast.focus":60,"beast.confidence":50,"beast.stress":10}
    mem.observe_personality(patch)
    assert mem.summary(founder["id"])["memory_count"]==0
    c.mono+=11;c.wall+=11;mem.observe_personality(patch)
    assert mem.summary(founder["id"])["personality_transition_count"]==1
    mem.observe_personality(patch)
    assert mem.summary(founder["id"])["personality_transition_count"]==1


def test_custom_lineage_memory_is_idempotent(tmp_path):
    _,_,_,founder,_,mem=setup(tmp_path)
    mem.record_custom(founder["id"],"lineage","Descendant created",{"child_id":"m1"},memory_id="synth:x:parent")
    mem.record_custom(founder["id"],"lineage","Descendant created",{"child_id":"m1"},memory_id="synth:x:parent")
    assert mem.summary(founder["id"])["memory_count"]==1
