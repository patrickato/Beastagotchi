import json
from pathlib import Path

import pytest

from beastui.experience_registry import (
    available_experience_pages,
    experience_renderer_catalog,
    experience_renderer_summary,
    get_experience_renderer,
    render_experience_page,
)
from beastui.scene_runtime import SceneRuntime


FIXTURE=Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_experience_renderer_registry_exposes_current_prototype_coverage():
    summary=experience_renderer_summary()
    assert summary["atlas"]==["home","recon"]
    assert summary["observatory"]==["home","spectrum"]
    assert summary["forge"]==["home"]
    assert summary["habitat"]==["beast","home"]
    assert summary["monolith"]==["home"]


def test_registry_resolves_and_renders_semantic_scene():
    rt=SceneRuntime()
    im=render_experience_page("atlas","recon",_state(),scene_runtime=rt)
    assert im.size==(480,320)
    assert rt.snapshot()["scene"]=="experience:atlas:recon"


def test_registry_missing_page_fails_explicitly_instead_of_silent_fallback():
    assert get_experience_renderer("forge","spectrum") is None
    with pytest.raises(KeyError):
        render_experience_page("forge","spectrum",_state())


def test_catalog_is_machine_readable_for_studio_and_compiler():
    rows=experience_renderer_catalog()
    assert all(row["status"]=="prototype" for row in rows)
    assert all(row["reference_size"]==[480,320] for row in rows)
    assert available_experience_pages("atlas")==("home","recon")
