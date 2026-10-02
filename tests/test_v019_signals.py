from beastcore.signals import SignalCatalog
from beastcore.state import StateRegistry


def test_signal_catalog_wraps_canonical_state_without_new_truth():
    state = StateRegistry()
    state.update_many("system", {
        "system.cpu.total": 27.5,
        "gps.latitude": 42.0,
        "progression.level": 9,
    })
    cat = SignalCatalog(state)

    cpu = cat.describe("system.cpu.total")
    assert cpu["value"] == 27.5
    assert cpu["value_type"] == "float"
    assert cpu["structure"] == "scalar"
    assert cpu["history_supported"] is True
    assert cpu["source"] == "system"
    assert cpu["privacy"] == "local_system"

    gps = cat.describe("gps.latitude")
    assert gps["privacy"] == "sensitive_location"
    assert gps["publication"] == "never"


def test_signal_catalog_truthfully_reports_unavailable_unknown_signal():
    state = StateRegistry()
    row = SignalCatalog(state).describe("future.optional.signal")
    assert row["available"] is False
    assert row["quality"] == "unavailable"
    assert row["value"] is None
    assert row["value_type"] == "unknown"


def test_signal_snapshot_is_bounded_and_deduplicated():
    state = StateRegistry()
    state.update_many("test", {"system.cpu.total": 10, "system.temp.cpu_c": 50})
    snap = SignalCatalog(state).snapshot(["system.cpu.total", "system.cpu.total", "system.temp.cpu_c"])
    assert snap["count"] == 2
    assert snap["available_count"] == 2
    assert snap["history_capable_count"] == 2
