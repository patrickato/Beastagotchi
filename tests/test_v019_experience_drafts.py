from __future__ import annotations

from beaststudio.experiences import compose_experience_draft, ExperienceDraftError


def base():
    return {
        "theme":"classic","face_profile":"builtin","animation_profile":"none","page":"home",
        "dashboard_widgets":[{"id":"old","key":"wifi.ap_count"}],
        "context_decks":[{"id":"field","label":"FIELD","apps":["map"]},{"id":"system","label":"SYSTEM","apps":["system"]}],
        "active_context_deck":"system",
    }


def schema():
    return {
        "themes":[{"id":"orchard","label":"Orchard"}],
        "face_profiles":[{"id":"pack_visuals_orb","local_id":"orb","label":"Orb","source_pack":"visuals"}],
        "animation_profiles":[{"id":"pack_visuals_float","local_id":"float","label":"Float","source_pack":"visuals"}],
        "pack_boards":[{"id":"pack_visuals_field","local_id":"field","label":"Field","source_pack":"visuals","widgets":[{"id":"cpu","key":"system.cpu.total"}]}],
        "pack_layouts":[{"id":"pack_visuals_triad","local_id":"triad","label":"Triad","source_pack":"visuals","widgets":[{"id":"temp","key":"system.temp.cpu_c"}]}],
        "default_context_decks":[],
    }


def test_experience_composes_visual_identity_and_board_without_writing():
    mission={
        "id":"pack_visuals_full","label":"Full","experience":True,"requirements_met":True,"source_pack":"visuals",
        "theme":"orchard","face_profile":"orb","animation_profile":"float","board":"field","deck":"field",
    }
    out=compose_experience_draft(base(),mission,schema())
    assert out["writes_preferences"] is False and out["requires_explicit_apply"] is True
    assert out["draft"]["theme"]=="orchard"
    assert out["draft"]["face_profile"]=="pack_visuals_orb"
    assert out["draft"]["animation_profile"]=="pack_visuals_float"
    assert out["draft"]["dashboard_widgets"][0]["id"]=="cpu"
    assert out["draft"]["active_context_deck"]=="field"
    assert out["draft"]["page"]=="dashboard"


def test_layout_experience_copies_template_widgets():
    mission={"id":"layout","label":"Layout","experience":True,"requirements_met":True,"source_pack":"visuals","layout":"triad"}
    out=compose_experience_draft(base(),mission,schema())
    assert out["draft"]["dashboard_widgets"][0]["id"]=="temp"
    out["draft"]["dashboard_widgets"][0]["id"]="changed"
    assert schema()["pack_layouts"][0]["widgets"][0]["id"]=="temp"


def test_missing_optional_piece_becomes_warning_not_silent_substitution():
    mission={"id":"x","label":"X","experience":True,"requirements_met":True,"theme":"missing","face_profile":"missing"}
    out=compose_experience_draft(base(),mission,schema())
    assert out["draft"]["theme"]=="classic"
    assert len(out["warnings"])==2


def test_unmet_experience_requirements_are_blocked():
    mission={"id":"x","label":"X","experience":True,"requirements_met":False,"missing_capabilities":["gps"]}
    try:compose_experience_draft(base(),mission,schema())
    except ExperienceDraftError as exc:assert "gps" in str(exc)
    else:raise AssertionError("unmet Experience must be blocked")
