from PIL import ImageChops

from beastui.experience_atlas import atlas_home_metadata
from beastui.experience_registry import (
    available_experience_pages,
    get_experience_renderer,
    render_experience_page,
)
from beastui.scene_runtime import SceneRuntime


def _state(*, live: bool) -> dict:
    state = {
        "health.core.state": "healthy",
        "governor.mode": "FULL",
        "system.temp.cpu_c": 58.0,
        "progression.stage": "Stalker",
        "progression.level": 27,
        "beast.expression": "curious",
        "pwnagotchi.mood": "awake",
        "wifi.ap_count": 0,
        "wifi.aps": [],
        "radio.primary.channel": 1,
        "radio.primary.band": "2.4GHz",
        "gps.fix": False,
        "gps.satellites_used": 0,
        "expedition.active": False,
        "expedition.route_points": 0,
        "expedition.ap_unique": 0,
        "expedition.captures_delta": 0,
        "expedition.xp_delta": 0,
        "wifi.handshake_ap_count": 0,
        "wifi.hidden_count": 0,
    }
    if live:
        state.update({
            "wifi.ap_count": 3,
            "wifi.aps": [
                {"ssid": "field-one", "channel": 1, "rssi": -42},
                {"ssid": "field-two", "channel": 6, "rssi": -58},
                {"ssid": "field-three", "channel": 149, "rssi": -67, "handshake": True},
            ],
            "radio.primary.channel": 6,
            "gps.fix": True,
            "gps.satellites_used": 7,
            "expedition.active": True,
            "expedition.route_points": 4,
            "expedition.ap_unique": 17,
            "expedition.distance_m": 1420.0,
            "expedition.duration_sec": 754,
            "expedition.captures_delta": 2,
            "expedition.xp_delta": 14,
            "wifi.handshake_ap_count": 3,
            "wifi.hidden_count": 1,
        })
    return state


def test_atlas_registry_uses_fieldbook_v21_without_changing_page_order():
    assert available_experience_pages("atlas") == ("home", "recon")
    home = get_experience_renderer("atlas", "home")
    recon = get_experience_renderer("atlas", "recon")
    assert home is not None and recon is not None
    assert home.renderer.__module__ == "beastui.experience_atlas_fieldbook_v21"
    assert recon.renderer.__module__ == "beastui.experience_atlas_fieldbook_v21"


def test_atlas_fieldbook_renders_empty_and_live_truth_states():
    empty = _state(live=False)
    live = _state(live=True)

    for page in ("home", "recon"):
        empty_image = render_experience_page("atlas", page, empty, phase=0.25)
        live_image = render_experience_page("atlas", page, live, phase=0.25)
        assert empty_image.size == (480, 320)
        assert live_image.size == (480, 320)
        assert empty_image.getbbox() == (0, 0, 480, 320)
        assert live_image.getbbox() == (0, 0, 480, 320)
        assert ImageChops.difference(empty_image, live_image).getbbox() is not None


def test_atlas_fieldbook_keeps_route_truth_gate_from_validated_atlas_model():
    empty = atlas_home_metadata(_state(live=False))
    live = atlas_home_metadata(_state(live=True))
    assert empty["gps_fix"] is False
    assert empty["draw_route"] is False
    assert live["gps_fix"] is True
    assert live["route_points"] == 4
    assert live["draw_route"] is True


def test_atlas_fieldbook_v21_keeps_stable_runtime_scene_ids():
    state = _state(live=True)
    for page in ("home", "recon"):
        runtime = SceneRuntime()
        render_experience_page("atlas", page, state, phase=0.5, scene_runtime=runtime)
        snapshot = runtime.snapshot()
        assert snapshot["page"] == page
        assert snapshot["scene"] == f"experience:atlas:{page}"


def test_atlas_recon_phase_has_visible_sweep_motion_without_changing_state():
    state = _state(live=True)
    a = render_experience_page("atlas", "recon", state, phase=0.0)
    b = render_experience_page("atlas", "recon", state, phase=3.0)
    assert ImageChops.difference(a, b).getbbox() is not None
