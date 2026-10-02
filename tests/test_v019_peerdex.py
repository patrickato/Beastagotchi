from __future__ import annotations

from beastcore.db import Store
from beastcore.peerdex import PeerDex


def payload(identity="abc",name="PWNBOB",rssi=-61,encounters=1):
    return {"identity":identity,"name":name,"version":"2.9.5.9","face":"(◕‿‿◕)",
            "rssi":rssi,"channel":6,"encounters":encounters,"session_id":"s1",
            "pwnd_run":2,"pwnd_total":22,"uptime":123,"epoch":4}


def test_peerdex_first_and_repeat_encounter(tmp_path):
    store=Store(str(tmp_path/"beast.db"));dex=PeerDex(store,clock=lambda:100.0)
    a=dex.observe(payload(),ts=100.0)
    b=dex.observe(payload(rssi=-40,encounters=5),ts=200.0)
    assert a["first_local_encounter"] is True
    assert b["first_local_encounter"] is False
    row=dex.recent(1)[0]
    assert row["fingerprint"]=="abc"
    assert row["seen_events"]==2
    assert row["advertised_encounters"]==5
    assert row["best_rssi"]==-40
    assert dex.summary()["peerdex.total_peers"]==1


def test_peerdex_rejects_unknown_identity(tmp_path):
    store=Store(str(tmp_path/"beast.db"));dex=PeerDex(store)
    assert dex.observe(payload(identity="???"))["accepted"] is False
    assert dex.summary()["peerdex.total_peers"]==0


def test_peer_lost_updates_last_seen_without_increment(tmp_path):
    store=Store(str(tmp_path/"beast.db"));dex=PeerDex(store)
    dex.observe(payload(),ts=100.0)
    out=dex.mark_lost({"identity":"abc"},ts=150.0)
    assert out["accepted"] is True
    row=dex.recent(1)[0]
    assert row["last_seen"]==150.0
    assert row["seen_events"]==1
