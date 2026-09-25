import json
from pathlib import Path

from beastui.experience_atlas import render_atlas_recon
from beastui.experience_observatory import render_observatory_spectrum
from beastui.scene_runtime import SceneRuntime


FIXTURE=Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_atlas_recon_is_field_survey_not_fake_geographic_map():
    state=_state()
    rt=SceneRuntime()
    im=render_atlas_recon(state,scene_runtime=rt)
    assert im.size==(480,320)
    snap=rt.snapshot()
    assert snap["page"]=="recon"
    assert snap["scene"]=="experience:atlas:recon"
    rows={r["id"]:r for r in snap["layers"]}
    assert rows["atlas_recon.survey"]["decorative"] is False
    assert "wifi.aps" in rows["atlas_recon.survey"]["signals"]
    assert "gps.fix" in rows["atlas_recon.position"]["signals"]


def test_observatory_spectrum_uses_current_observation_truth_only():
    state=_state()
    rt=SceneRuntime()
    im=render_observatory_spectrum(state,scene_runtime=rt)
    assert im.size==(480,320)
    snap=rt.snapshot()
    assert snap["page"]=="spectrum"
    assert snap["scene"]=="experience:observatory:spectrum"
    rows={r["id"]:r for r in snap["layers"]}
    assert rows["observatory_spectrum.occupancy"]["signals"]==["wifi.aps","radio.primary.channel"]
    assert rows["observatory_spectrum.truth"]["update_class"]=="static"


def test_cross_page_experience_translations_remain_visually_distinct():
    state=_state()
    assert render_atlas_recon(state).tobytes()!=render_observatory_spectrum(state).tobytes()
