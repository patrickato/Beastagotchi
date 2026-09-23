from __future__ import annotations

from beastcore.db import Store
from beastcore.global_sync import GlobalProfileSync, clean_policy
from beastcore.roster import BeastRoster
from beastcore.progression import xp_threshold


class State: pass


def setup(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"missing.json",clock=lambda:100.0)
    founder=roster.bootstrap_founder(name="Hex")
    return store,roster,founder


def test_global_sync_is_off_and_has_no_identity_by_default(tmp_path):
    store,roster,_=setup(tmp_path)
    g=GlobalProfileSync(State(),store,roster,clock=lambda:100.0)
    out=g.tick()
    assert out["global.enabled"] is False
    assert out["global.public_id"] is None
    assert out["global.queue.pending"]==0


def test_opt_in_auto_sync_queues_only_sanitized_public_fields(tmp_path):
    store,roster,founder=setup(tmp_path)
    roster.update_progress(founder["id"],xp=xp_threshold(70))
    g=GlobalProfileSync(State(),store,roster,clock=lambda:100.0)
    g.set_policy({
        "enabled":True,"auto_sync":True,"roster_scope":"all",
        "publish_names":True,"publish_level_stage":True,
        "publish_synthesis_eligibility":True,"publish_lineage":True,
    })
    out=g.tick();pending=g.pending()
    assert out["global.queue.pending"]==1
    p=pending[0]["payload"]
    assert p["creatures"][0]["name"]=="Hex"
    assert p["creatures"][0]["level"]==70
    assert p["creatures"][0]["synthesis_eligible"] is True
    raw=str(p).lower()
    assert "bssid" not in raw and "ssid" not in raw and "gps" not in raw and "handshake" not in raw
    assert p["creatures"][0]["id"]!="founder"


def test_unchanged_public_state_does_not_queue_duplicate_revision(tmp_path):
    store,roster,_=setup(tmp_path)
    g=GlobalProfileSync(State(),store,roster,clock=lambda:100.0)
    g.set_policy({"enabled":True,"auto_sync":True})
    g.tick();g.tick()
    assert len(g.pending())==1


def test_private_change_does_not_change_public_snapshot_when_field_disabled(tmp_path):
    store,roster,founder=setup(tmp_path)
    g=GlobalProfileSync(State(),store,roster,clock=lambda:100.0)
    policy=g.set_policy({"enabled":True,"auto_sync":True,"publish_level_stage":False,
                         "publish_synthesis_eligibility":False,"publish_roster_totals":False})
    first=g.content_hash(g.build_snapshot(policy))
    roster.update_progress(founder["id"],xp=xp_threshold(73))
    second=g.content_hash(g.build_snapshot(policy))
    assert first==second


def test_selected_achievement_mode_only_publishes_allowlist(tmp_path):
    store,roster,founder=setup(tmp_path)
    with store.conn:
        store.conn.execute("INSERT INTO beast_achievements(beast_id,achievement_id,unlocked_at,context_json) VALUES(?,?,?,?)",(founder["id"],"public_one",1.0,"{}"))
        store.conn.execute("INSERT INTO beast_achievements(beast_id,achievement_id,unlocked_at,context_json) VALUES(?,?,?,?)",(founder["id"],"private_two",2.0,"{}"))
    g=GlobalProfileSync(State(),store,roster)
    p=clean_policy({"enabled":True,"publish_achievements":"selected","selected_achievement_ids":["public_one"]})
    snap=g.build_snapshot(p)
    assert snap["creatures"][0]["achievements"]==["public_one"]


def test_disabling_global_forces_auto_sync_off():
    p=clean_policy({"enabled":False,"auto_sync":True})
    assert p["auto_sync"] is False
