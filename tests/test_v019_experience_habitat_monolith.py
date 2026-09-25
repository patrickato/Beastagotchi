import json
from pathlib import Path

from beastui.experience_habitat import habitat_home_metadata, render_habitat_home, render_habitat_beast
from beastui.experience_monolith import monolith_home_metadata, render_monolith_home
from beastui.scene_runtime import SceneRuntime


FIXTURE = Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def test_habitat_is_creature_first_and_uses_real_progression():
    state = _state()
    meta = habitat_home_metadata(state)
    assert meta["stage"] == state["progression.stage"]
    assert meta["level"] == state["progression.level"]
    assert meta["progress_pct"] == state["progression.level_progress_pct"]

    rt = SceneRuntime()
    im = render_habitat_home(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["scene"] == "experience:habitat:home"
    rows = {row["id"]: row for row in snap["layers"]}
    assert rows["monolith.ambient_halo"]["decorative"] is True
    assert rows["habitat.beast"]["bounds"] == [130, 40, 350, 260]
    assert rows["habitat.environment"]["decorative"] is True


def test_habitat_truth_strip_does_not_replace_creature_hierarchy():
    state = _state()
    rt = SceneRuntime()
    render_habitat_home(state, scene_runtime=rt)
    rows = {row["id"]: row for row in rt.snapshot()["layers"]}
    beast = rows["habitat.beast"]["bounds"]
    truth = rows["habitat.truth"]["bounds"]
    beast_area = (beast[2]-beast[0]) * (beast[3]-beast[1])
    truth_area = (truth[2]-truth[0]) * (truth[3]-truth[1])
    assert beast_area > truth_area * 5


def test_monolith_keeps_primary_information_intentionally_sparse():
    state = _state()
    meta = monolith_home_metadata(state)
    assert meta["nearby"] == state["wifi.ap_count"]
    assert meta["channel"] == state["radio.primary.channel"]

    rt = SceneRuntime()
    im = render_monolith_home(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["scene"] == "experience:monolith:home"
    assert snap["layer_count"] == 5


def test_habitat_and_monolith_are_visually_distinct():
    state = _state()
    assert render_habitat_home(state).tobytes() != render_monolith_home(state).tobytes()


def test_habitat_beast_page_preserves_creature_first_growth_memory_language():
    state = _state()
    rt = SceneRuntime()
    im = render_habitat_beast(state, scene_runtime=rt)
    assert im.size == (480, 320)
    snap = rt.snapshot()
    assert snap["page"] == "beast"
    assert snap["scene"] == "experience:habitat:beast"
    rows = {row["id"]: row for row in snap["layers"]}
    assert "habitat_beast.creature" in rows
    assert "habitat_beast.growth" in rows
    assert "habitat_beast.memories" in rows
    assert rows["habitat_beast.environment"]["decorative"] is True
