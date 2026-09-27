import json
from pathlib import Path

from beastui.experience_forge import forge_home_metadata, render_forge_home
from beastui.experience_observatory import observatory_home_metadata, render_observatory_home
from beastui.scene_runtime import SceneRuntime


FIXTURE = Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_forge_uses_real_machine_state_and_no_fake_power_sensor():
    state = _state()
    meta = forge_home_metadata(state)
    assert meta["power_available"] is False
    assert meta["ups_state"] == "not_detected"
    assert meta["ethernet"] is True
    assert meta["channel"] == 52


def test_forge_scene_is_machine_cluster_not_atlas_layout():
    state = _state()
    rt = SceneRuntime()
    im = render_forge_home(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["scene"] == "experience:forge:home"
    ids = {row["id"] for row in snap["layers"]}
    assert {"forge.compute", "forge.radio", "forge.power", "forge.io", "forge.doctor"} <= ids
    assert not any(x.startswith("atlas.") for x in ids)


def test_observatory_metadata_is_derived_from_real_observations():
    state = _state()
    meta = observatory_home_metadata(state)
    assert meta["ap_count"] == len(state["wifi.aps"])
    assert meta["channels"] == sorted({row["channel"] for row in state["wifi.aps"]})
    assert meta["rssi_max"] == max(row["rssi"] for row in state["wifi.aps"])
    assert meta["capture_kind"] == "sanitized_real_target_capture"
    assert meta["aps_reading"].known is True


def test_observatory_scene_prioritizes_measurement_provenance_and_shell_truth():
    state = _state()
    rt = SceneRuntime()
    im = render_observatory_home(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["scene"] == "experience:observatory:home"
    rows = {row["id"]: row for row in snap["layers"]}
    assert rows["observatory.spectrum"]["signals"] == ["wifi.aps", "radio.primary.channel"]
    assert rows["observatory.distribution"]["signals"] == ["wifi.aps"]
    assert "observatory.provenance" in rows
    assert "observatory.home.shell_status" in rows
    assert rows["observatory.home.nav_position"]["update_class"] == "static"
    assert "observatory.home.nav_previous" not in rows
    assert rows["observatory.home.nav_next"]["touch"] == "experience_page:spectrum"


def test_observatory_missing_observation_input_is_unknown_not_zero():
    state = _state()
    state.pop("wifi.aps", None)
    state.pop("wifi.ap_count", None)
    state.pop("radio.primary.channel", None)
    meta = observatory_home_metadata(state)
    assert meta["ap_count"] is None
    assert meta["channel"] is None
    assert meta["aps_reading"].known is False
    assert meta["channel_reading"].known is False


def test_forge_and_observatory_are_visually_distinct():
    state = _state()
    assert render_forge_home(state).tobytes() != render_observatory_home(state).tobytes()
