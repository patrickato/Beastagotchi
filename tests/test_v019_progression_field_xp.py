"""Finding F3: XP comes from genuine discovery, not idle uptime.

The per-tick runtime drip now accrues only during *field* time (undocked) and is capped per day,
while ``lifetime_runtime_sec`` and the runtime achievements keep counting all uptime. A Beast parked
on its home dock no longer grinds XP; a Beast out in the field earns a small daily floor, and real
discovery (new APs/vendors/GPS/captures, via ``on_event``) stays uncapped and drives leveling.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from beastcore.db import Store
from beastcore.progression import ProgressionEngine
from beastcore.roster_progression import ActiveBeastProgressionStore
from beastcore.state import StateRegistry


def _runtime(tmp_path: Path):
    legacy_path = tmp_path / "profile.json"
    legacy_path.write_text(json.dumps({"xp": 0, "counters": {}}))
    store = Store(str(tmp_path / "beast.db"))
    pstore = ActiveBeastProgressionStore(store, legacy_profile_path=legacy_path, clock=lambda: 1000.0)
    state = StateRegistry()
    engine = ProgressionEngine(state, profile_store=pstore)
    return state, engine


def _tick_one_minute(engine):
    # tick() reads time.monotonic() directly and caps its delta at 60 s; rewinding _last_tick by 60 s
    # makes one tick count as a full field minute.
    engine._last_tick = time.monotonic() - 60.0
    engine.tick()


def test_docked_uptime_earns_no_xp_but_odometer_still_runs(tmp_path):
    state, engine = _runtime(tmp_path)
    state.update_many("dock", {"dock.docked": True}, priority=80)
    engine.profile["runtime_award_remainder_sec"] = 590.0        # one minute short of an award
    before_rt = engine.profile["lifetime_runtime_sec"]
    _tick_one_minute(engine)
    assert state.get("progression.xp") == 0                      # docked: no field XP across 600 s
    assert engine.profile["lifetime_runtime_sec"] > before_rt    # longevity odometer still advances
    assert engine.profile["runtime_award_remainder_sec"] == 590.0  # docked time is not banked


def test_field_uptime_earns_xp(tmp_path):
    state, engine = _runtime(tmp_path)                           # no dock.docked -> field by default
    engine.profile["runtime_award_remainder_sec"] = 541.0
    _tick_one_minute(engine)
    assert state.get("progression.xp") == 1                      # 541 + 60 crosses 600 -> 1 field XP
    assert state.get("progression.discovery.field_xp_today") == 1
    assert state.get("progression.discovery.field_xp_daily_cap") == engine.FIELD_XP_DAILY_CAP


def test_field_xp_is_capped_per_day(tmp_path):
    _, engine = _runtime(tmp_path)
    assert engine._grant_field_xp(100) == engine.FIELD_XP_DAILY_CAP   # a big burst is capped
    assert engine._grant_field_xp(100) == 0                           # nothing left that day
    assert engine.profile["counters"]["field_xp_day"] == engine.FIELD_XP_DAILY_CAP


def test_field_xp_cap_resets_on_a_new_day(tmp_path):
    _, engine = _runtime(tmp_path)
    assert engine._grant_field_xp(100) == engine.FIELD_XP_DAILY_CAP
    engine.profile["counters"]["field_xp_date"] = "2000-01-01"        # pretend the cap was set yesterday
    assert engine._grant_field_xp(5) == 5                             # new day -> grants again


def test_docked_time_does_not_bank_for_a_burst_on_undock(tmp_path):
    state, engine = _runtime(tmp_path)
    state.update_many("dock", {"dock.docked": True}, priority=80)
    for _ in range(20):                                          # 20 minutes parked on the dock
        _tick_one_minute(engine)
    assert state.get("progression.xp") == 0                      # earned nothing while docked
    state.update_many("dock", {"dock.docked": False}, priority=80)
    _tick_one_minute(engine)                                     # one minute of real field time
    assert state.get("progression.xp") == 0                      # no banked 20-minute dump on undock


def test_discovery_xp_is_uncapped_and_drives_leveling(tmp_path):
    # Contrast with the field-time floor: genuine device-first discoveries are not daily-capped, so a
    # busy field session out-levels idle presence many times over (the point of F3).
    import types
    _, engine = _runtime(tmp_path)
    ev = types.SimpleNamespace(type="wifi.ap_discovered", data={"device_new_count": 200, "aps": []})
    engine.on_event(ev)
    xp = int(engine.profile["xp"])
    assert xp >= 200                                             # >= 1 XP per device-first AP, uncapped
    assert xp > engine.FIELD_XP_DAILY_CAP * 5                    # dwarfs a whole day's idle field floor
