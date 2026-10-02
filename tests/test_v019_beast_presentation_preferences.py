from __future__ import annotations

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.events import EventBus
from beastcore.roster import BeastRoster
from beastcore.state import StateRegistry


def setup(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    founder=roster.bootstrap_founder(name="Hex")
    other=roster.create_beast("Orbit")
    broker=ActionBroker(StateRegistry(),store,EventBus())
    return store,roster,broker,founder,other


def test_per_beast_presentation_preferences_are_independent(tmp_path):
    _,roster,broker,founder,other=setup(tmp_path)
    a={"theme":"classic","face_profile":"builtin","animation_profile":"none","experience_id":"field"}
    b={"theme":"matrix","face_profile":"orb","animation_profile":"float","experience_id":"night"}
    assert broker.perform("roster.presentation_set",{"id":founder["id"],"presentation":a})["status"]=="success"
    assert broker.perform("roster.presentation_set",{"id":other["id"],"presentation":b})["status"]=="success"
    assert roster.presentation_preferences(founder["id"])["theme"]=="classic"
    assert roster.presentation_preferences(other["id"])["theme"]=="matrix"
    assert roster.presentation_preferences(founder["id"])["experience_id"]=="field"
    assert roster.presentation_preferences(other["id"])["experience_id"]=="night"


def test_roster_switch_does_not_apply_presentation(tmp_path):
    _,roster,broker,_,other=setup(tmp_path)
    broker.perform("roster.presentation_set",{"id":other["id"],"presentation":{"theme":"matrix"}})
    row=broker.perform("roster.switch",{"id":other["id"]})
    assert row["status"]=="success"
    assert row["result"]["experience_changed"] is False
    assert roster.presentation_preferences(other["id"])["theme"]=="matrix"


def test_presentation_get_reports_saved_preference(tmp_path):
    _,_,broker,_,other=setup(tmp_path)
    broker.perform("roster.presentation_set",{"id":other["id"],"presentation":{"theme":"blackice","face_profile":"builtin"}})
    plan=broker.plan("roster.presentation_get",{"id":other["id"]})
    assert plan["has_preferred_presentation"] is True
    assert plan["presentation"]["theme"]=="blackice"


def test_clear_preferred_presentation_preserves_progression(tmp_path):
    _,roster,broker,founder,_=setup(tmp_path)
    roster.update_progress(founder["id"],xp=1234)
    broker.perform("roster.presentation_set",{"id":founder["id"],"presentation":{"theme":"classic"}})
    row=broker.perform("roster.presentation_clear",{"id":founder["id"]})
    assert row["status"]=="success"
    assert roster.presentation_preferences(founder["id"])=={}
    assert roster.get(founder["id"])["xp"]==1234


def test_preferred_presentation_rejects_oversized_payload(tmp_path):
    _,_,broker,founder,_=setup(tmp_path)
    huge={"dashboard_widgets":[{"blob":"x"*300000}]}
    row=broker.perform("roster.presentation_set",{"id":founder["id"],"presentation":huge})
    assert row["status"]=="failed"
