from __future__ import annotations

import json
from pathlib import Path

from beastcore.collectors.bridge import BridgeCollector


def write_bridge(path: Path, *, instance_id=None, seq=0, updated_at=1.0, events=None):
    obj = {
        "updated_at": float(updated_at),
        "seq": int(seq),
        "state": {"pwnagotchi.mode": "ready"},
        "events": list(events or []),
    }
    if instance_id is not None:
        obj["instance_id"] = instance_id
    path.write_text(json.dumps(obj))


def test_bridge_accepts_sequence_reset_for_new_instance(tmp_path):
    path = tmp_path / "bridge.json"
    c = BridgeCollector(str(path))

    write_bridge(
        path,
        instance_id="first",
        seq=8,
        updated_at=10.0,
        events=[{"seq": 8, "type": "epoch", "ts": 10.0, "data": {"epoch": 8}}],
    )
    c.collect()
    assert [x["seq"] for x in c.drain_events()] == [8]

    write_bridge(
        path,
        instance_id="second",
        seq=1,
        updated_at=11.0,
        events=[{"seq": 1, "type": "loaded", "ts": 11.0, "data": {}}],
    )
    values = c.collect()
    assert values["pwnagotchi.bridge.instance_id"] == "second"
    assert [x["seq"] for x in c.drain_events()] == [1]


def test_bridge_does_not_duplicate_events_within_same_instance(tmp_path):
    path = tmp_path / "bridge.json"
    c = BridgeCollector(str(path))

    write_bridge(
        path,
        instance_id="same",
        seq=2,
        updated_at=20.0,
        events=[
            {"seq": 1, "type": "loaded", "ts": 19.0, "data": {}},
            {"seq": 2, "type": "ready", "ts": 20.0, "data": {}},
        ],
    )
    c.collect()
    assert [x["seq"] for x in c.drain_events()] == [1, 2]

    write_bridge(
        path,
        instance_id="same",
        seq=3,
        updated_at=21.0,
        events=[
            {"seq": 2, "type": "ready", "ts": 20.0, "data": {}},
            {"seq": 3, "type": "epoch", "ts": 21.0, "data": {}},
        ],
    )
    c.collect()
    assert [x["seq"] for x in c.drain_events()] == [3]


def test_legacy_bridge_uses_newer_timestamp_to_detect_restart(tmp_path):
    path = tmp_path / "bridge.json"
    c = BridgeCollector(str(path))

    write_bridge(
        path,
        seq=5,
        updated_at=30.0,
        events=[{"seq": 5, "type": "epoch", "ts": 30.0, "data": {}}],
    )
    c.collect()
    assert [x["seq"] for x in c.drain_events()] == [5]

    write_bridge(
        path,
        seq=1,
        updated_at=31.0,
        events=[{"seq": 1, "type": "loaded", "ts": 31.0, "data": {}}],
    )
    c.collect()
    assert [x["seq"] for x in c.drain_events()] == [1]
