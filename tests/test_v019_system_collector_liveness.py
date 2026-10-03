"""Collector-boundary live-truth: SystemCollector must not leave a stale reading looking live.

A failed sensor read must publish the key as unavailable (None) / clear a cached value, not omit it
(which retains the last value in StateRegistry as if live) -- the source side of the ADR-0008 fixes the
downstream needs/mood tests assert against fake state. Reviewed on PR #50.
"""
from __future__ import annotations

import beastcore.collectors.system as sysmod
from beastcore.collectors.system import SystemCollector


def test_failed_thermal_read_publishes_temperature_unavailable(monkeypatch):
    c = SystemCollector()
    monkeypatch.setattr(sysmod, "run", lambda *a, **k: (1, "", ""))  # vcgencmd unavailable
    # a readable, hot thermal zone first
    monkeypatch.setattr(sysmod, "read_text", lambda p="", *a, **k: "84000" if "thermal" in str(p) else "")
    hot = c.collect()
    assert hot["system.temp.cpu_c"] == 84.0
    # now the thermal file is unreadable -> the key must be published as None, not retain 84.0
    monkeypatch.setattr(sysmod, "read_text", lambda *a, **k: "")
    cold = c.collect()
    assert "system.temp.cpu_c" in cold and cold["system.temp.cpu_c"] is None


def test_failed_throttle_refresh_clears_the_flag(monkeypatch):
    c = SystemCollector()
    monkeypatch.setattr(sysmod, "read_text", lambda *a, **k: "")
    # first refresh succeeds with an active throttle bit
    monkeypatch.setattr(sysmod, "run", lambda *a, **k: (0, "throttled=0x5", ""))
    assert c.collect()["system.throttle.flags"] == "0x5"
    # force the refresh window and make the next vcgencmd fail -> the flag clears, not retains 0x5
    c._throttle_at = 0.0
    monkeypatch.setattr(sysmod, "run", lambda *a, **k: (1, "", ""))
    assert c.collect()["system.throttle.flags"] is None


def test_persistent_throttle_failure_honours_the_cadence(monkeypatch):
    # A failed read clears the flag, but must not re-shell vcgencmd every 1s tick (clearing to None
    # must not trip an "is None -> re-read" path); the 5s cadence still applies.
    c = SystemCollector()
    monkeypatch.setattr(sysmod, "read_text", lambda *a, **k: "")
    calls = {"n": 0}

    def fake_run(cmd, *a, **k):
        if "get_throttled" in cmd:
            calls["n"] += 1
        return (1, "", "")  # always fails

    monkeypatch.setattr(sysmod, "run", fake_run)
    c.collect()   # startup read (1 attempt), value None
    c.collect()   # immediately after, within the 5s window -> must NOT re-shell
    c.collect()
    assert calls["n"] == 1
    assert c.collect()["system.throttle.flags"] is None
