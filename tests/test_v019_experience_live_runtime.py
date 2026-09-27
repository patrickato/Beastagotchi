import json
from pathlib import Path

from PIL import Image

from beastui.experience_live import ExperienceBeastUI, ExperienceSession
from beastui.experience_registry import available_experience_pages, render_experience_page
from beastui.scene_runtime import SceneRuntime


FIXTURE = Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_experience_page_order_is_authored_not_alphabetical():
    assert available_experience_pages("atlas") == ("home", "recon")
    assert available_experience_pages("forge") == ("home", "system")
    assert available_experience_pages("observatory") == ("home", "spectrum")
    assert available_experience_pages("habitat") == ("home", "beast")
    assert available_experience_pages("monolith") == ("home", "overview")


def test_registry_runtime_contract_renders_every_page_with_phase():
    state = _state()
    for experience_id in ("atlas", "forge", "observatory", "habitat", "monolith"):
        for page_id in available_experience_pages(experience_id):
            rt = SceneRuntime()
            image = render_experience_page(
                experience_id,
                page_id,
                state,
                phase=0.5,
                scene_runtime=rt,
            )
            assert image.size == (480, 320)
            snap = rt.snapshot()
            assert snap["page"] == page_id
            assert snap["scene"] == f"experience:{experience_id}:{page_id}"


def test_experience_session_navigation_is_bounded_and_invalid_page_falls_back():
    session = ExperienceSession.create("habitat", "not-a-page")
    assert session.pages == ("home", "beast")
    assert session.page_id == "home"
    assert session.index == 0

    assert session.move(+1) is True
    assert session.page_id == "beast"
    assert session.move(+1) is False
    assert session.page_id == "beast"

    assert session.move(-1) is True
    assert session.page_id == "home"
    assert session.move(-1) is False
    assert session.select("beast") is True
    assert session.select("missing") is False


def test_staged_experience_renders_through_inherited_beastui_output_and_touch(tmp_path):
    out = tmp_path / "live-monolith.png"
    ui = ExperienceBeastUI(
        "beastui",
        "/dev/this-must-not-be-opened",
        str(out),
        "classic",
        experience_id="monolith",
        experience_page="home",
        physical_size=(480, 320),
    )
    ui.state = _state()
    ui.phase_override = 0.0

    rendered = ui.render()
    assert rendered.size == (480, 320)
    assert out.is_file()
    with Image.open(out) as saved:
        assert saved.size == (480, 320)
        assert saved.convert("RGB").tobytes() == rendered.convert("RGB").tobytes()

    snap = ui.scene_runtime.snapshot()
    assert snap["scene"] == "experience:monolith:home"
    assert snap["page"] == "home"
    layers = {row["id"]: row for row in snap["layers"]}
    nav = layers["monolith.home.nav_next"]
    assert nav["touch"] == "experience_page:overview"

    x1, y1, x2, y2 = nav["bounds"]
    ui.on_input("tap", {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2})
    assert ui.experience.page_id == "overview"

    ui.render()
    snap = ui.scene_runtime.snapshot()
    assert snap["scene"] == "experience:monolith:overview"
    assert snap["page"] == "overview"

    runtime = ui.experience_runtime_snapshot()
    assert runtime == {
        "mode": "staging",
        "experience_id": "monolith",
        "page_id": "overview",
        "pages": ["home", "overview"],
        "legacy_page_index": ui.pages.IDS.index("overview"),
        "writes_preferences": False,
    }
    assert ui.pref_path is None
    assert ui.fb.total_frames == 2
    ui.fb.close()
