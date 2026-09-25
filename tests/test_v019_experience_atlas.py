import json
from pathlib import Path

from beastui.experience_atlas import atlas_home_metadata, render_atlas_home
from beastui.scene_runtime import SceneRuntime


FIXTURE = Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_atlas_does_not_invent_route_without_gps_fix():
    state = _state()
    meta = atlas_home_metadata(state)
    assert state["expedition.active"] is True
    assert state["gps.fix"] is False
    assert state["expedition.route_points"] == 0
    assert meta["draw_route"] is False
    assert meta["gps_status"] == "GPS SEARCHING"


def test_atlas_route_requires_fix_and_real_route_points():
    state = _state()
    state["gps.fix"] = True
    state["expedition.route_points"] = 2
    meta = atlas_home_metadata(state)
    assert meta["draw_route"] is True
    assert meta["gps_status"] == "GPS FIX"


def test_atlas_home_renders_reference_size_and_semantic_scene():
    state = _state()
    rt = SceneRuntime()
    im = render_atlas_home(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["scene_id"] == "experience:atlas:home"
    ids = {row["id"] for row in snap["layers"]}
    assert {
        "atlas.header",
        "atlas.field",
        "atlas.beast",
        "atlas.radio",
        "atlas.discovery",
        "atlas.journey",
        "atlas.system",
        "atlas.expedition_strip",
    } <= ids


def test_atlas_field_canvas_is_live_truth_not_decorative_fake_map():
    state = _state()
    rt = SceneRuntime()
    render_atlas_home(state, phase=1.5, scene_runtime=rt)
    snap = rt.snapshot()
    field = next(row for row in snap["layers"] if row["id"] == "atlas.field")
    assert field["decorative"] is False
    assert "gps.fix" in field["signals"]
    assert "wifi.aps" in field["signals"]


def test_atlas_dirty_layers_respond_to_relevant_signal_only():
    state = _state()
    rt = SceneRuntime()
    render_atlas_home(state, scene_runtime=rt)
    # Establish baseline, then publish only a changed radio channel.
    rt.update_signals({"radio.primary.channel": 149})
    dirty = rt.dirty_layer_ids(include_ambient=False, include_interaction=False)
    assert "atlas.radio" in dirty
    assert "atlas.journey" not in dirty
    assert "atlas.system" not in dirty
