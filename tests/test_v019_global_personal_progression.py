from __future__ import annotations

from types import SimpleNamespace

from beastcore.db import Store
from beastcore.global_achievements import GlobalAchievementEngine
from beastcore.progression import ProgressionEngine
from beastcore.roster_progression import ActiveBeastProgressionStore
from beastcore.semantic import SemanticEngine
from beastcore.state import StateRegistry


def setup_runtime(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    pstore=ActiveBeastProgressionStore(store,legacy_profile_path=tmp_path/"missing.json",clock=lambda:1000.0)
    state=StateRegistry()
    progression=ProgressionEngine(state,profile_store=pstore)
    semantic=SemanticEngine(state,store,active_beast_id=pstore.current_id)
    return store,pstore,state,progression,semantic


def ap(mac,vendor="Acme"):
    return {"mac":mac,"hostname":"net-"+mac[-2:],"vendor":vendor,"channel":6,"rssi":-50,"encryption":"WPA2"}


def event(data):
    return SimpleNamespace(type="wifi.ap_discovered",data=data)


def test_device_first_and_beast_first_are_persisted_separately(tmp_path):
    store,pstore,state,progression,semantic=setup_runtime(tmp_path)
    batch=[ap(f"00:00:00:00:00:{i:02x}") for i in range(1,7)]
    state.update_many("test",{"wifi.aps":batch},priority=100)
    rows=semantic.tick()
    discovery=next(x for x in rows if x[0]=="wifi.ap_discovered")
    data=discovery[2]
    assert data["device_new_count"]==6
    assert data["beast_new_count"]==6
    assert data["beast_familiar_new_count"]==0
    assert store.count_wifi_encounters()==6
    assert store.count_beast_wifi_encounters("founder")==6

    other=pstore.roster.create_beast("Orbit",activate=True)
    rows=semantic.tick()
    discovery=next(x for x in rows if x[0]=="wifi.ap_discovered")
    data=discovery[2]
    assert data["device_new_count"]==0
    assert data["beast_new_count"]==6
    assert data["beast_familiar_new_count"]==6
    assert store.count_beast_wifi_encounters(other["id"])==6


def test_new_beast_gets_small_capped_familiar_world_xp(tmp_path):
    _,pstore,_,progression,_=setup_runtime(tmp_path)
    other=pstore.roster.create_beast("Orbit",activate=True)
    rows=progression.on_event(event({"beast_new_count":60,"device_new_count":0,"aps":[]}))
    first_xp=pstore.roster.get(other["id"])["xp"]
    # Base familiar-world XP is capped at 20/day. One-time personal achievement
    # bonuses may make total XP larger, which is intentional.
    assert progression.profile["counters"]["familiar_discovery_xp_day"]==20
    assert first_xp>=20
    progression.on_event(event({"beast_new_count":60,"device_new_count":0,"aps":[]}))
    assert progression.profile["counters"]["familiar_discovery_xp_day"]==20
    assert pstore.roster.get(other["id"])["xp"]==first_xp


def test_device_first_still_gets_full_one_per_ap_without_using_familiar_cap(tmp_path):
    _,pstore,_,progression,_=setup_runtime(tmp_path)
    rows=progression.on_event(event({"beast_new_count":12,"device_new_count":12,"aps":[]}))
    assert pstore.roster.get("founder")["xp"]>=12
    assert any(r[0]=="progression.xp_awarded" and r[2]["amount"]>=12 for r in rows)


def test_signal_achievements_follow_personal_unique_count(tmp_path):
    _,pstore,state,progression,_=setup_runtime(tmp_path)
    other=pstore.roster.create_beast("Orbit",activate=True)
    progression.on_event(event({"beast_new_count":10,"device_new_count":0,"aps":[]}))
    b=pstore.roster.get(other["id"])
    assert "signals_10" in b["achievements"]
    assert state.get("progression.discovery.beast_unique_aps")==10


def test_founder_migration_seeds_existing_device_world_as_already_known(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    store.record_wifi_encounters([ap("00:00:00:00:00:01"),ap("00:00:00:00:00:02")],ts=100.0)
    pstore=ActiveBeastProgressionStore(store,legacy_profile_path=tmp_path/"missing.json",clock=lambda:1000.0)
    assert store.count_beast_wifi_encounters("founder")==2
    assert pstore.load_profile("founder")["counters"]["beast_unique_aps"]>=2


def test_global_achievements_are_device_wide_and_do_not_award_active_beast_xp(tmp_path):
    store,pstore,state,progression,_=setup_runtime(tmp_path)
    store.record_wifi_encounters([ap("00:00:00:00:00:01")],ts=100.0)
    before=pstore.roster.get("founder")["xp"]
    engine=GlobalAchievementEngine(state,store,pstore.roster,clock=lambda:2000.0)
    rows=engine.tick()
    assert any(x[2]["id"]=="world_first_signal" for x in rows)
    assert pstore.roster.get("founder")["xp"]==before
    assert "world_first_signal" in state.get("global.achievements.unlocked_ids")


def test_global_roster_achievement_can_unlock_while_specific_beasts_keep_own_records(tmp_path):
    store,pstore,state,_,_=setup_runtime(tmp_path)
    pstore.roster.create_beast("Orbit")
    engine=GlobalAchievementEngine(state,store,pstore.roster,clock=lambda:2000.0)
    rows=engine.tick()
    assert any(x[2]["id"]=="roster_two" for x in rows)
    assert state.get("global.collection.roster_total")==2
