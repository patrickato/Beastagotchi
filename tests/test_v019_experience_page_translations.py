import json
from pathlib import Path

from beastui.experience_atlas import render_atlas_recon
from beastui.experience_observatory import render_observatory_spectrum
from beastui.experience_forge import render_forge_system
from beastui.experience_monolith import render_monolith_overview
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


def test_forge_system_is_machine_subsystem_view_not_generic_dashboard():
    state=_state()
    rt=SceneRuntime()
    im=render_forge_system(state,scene_runtime=rt)
    assert im.size==(480,320)
    snap=rt.snapshot()
    assert snap["page"]=="system"
    assert snap["scene"]=="experience:forge:system"
    rows={r["id"]:r for r in snap["layers"]}
    assert "system.cpu.total" in rows["forge_system.compute"]["signals"]
    assert "overview.attention" in rows["forge_system.doctor"]["signals"]
    assert rows["forge_system.bus"]["decorative"] is True


def test_monolith_overview_stays_sparse_and_drilldown_first():
    state=_state()
    rt=SceneRuntime()
    im=render_monolith_overview(state,scene_runtime=rt)
    assert im.size==(480,320)
    snap=rt.snapshot()
    assert snap["page"]=="overview"
    assert snap["scene"]=="experience:monolith:overview"
    rows={r["id"]:r for r in snap["layers"]}
    assert rows["monolith_overview.facts"]["signals"]==[
        "system.cpu.total","system.temp.cpu_c","wifi.ap_count"
    ]
    assert rows["monolith_overview.inspect_hint"]["update_class"]=="interaction"
    assert len(rows) <= 6


def test_all_five_first_experiences_now_have_cross_page_surface():
    from beastcore.experience_surfaces import experience_surface_coverage
    coverage=experience_surface_coverage()
    for eid in ("atlas","forge","observatory","habitat","monolith"):
        assert len(coverage[eid]) >= 2
