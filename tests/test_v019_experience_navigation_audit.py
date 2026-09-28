import json
from pathlib import Path

from PIL import ImageChops

from beastui.apps import APPS
from beastui.experience_live_optimized import ExperienceBeastUI
from beastui.experience_registry import get_experience_renderer


FIXTURE = Path("tests/fixtures/v018_target_sanitized_state.json")


def _state():
    return json.loads(FIXTURE.read_text())


def _ui(tmp_path, *, experience="atlas", page="home", theme="classic"):
    ui = ExperienceBeastUI(
        "beastui", "/dev/this-must-not-be-opened", str(tmp_path / "frame.png"), theme,
        experience_id=experience, experience_page=page, physical_size=(480, 320),
    )
    ui.state = _state()
    ui.phase_override = 0.5
    return ui


def test_every_primary_page_app_is_reachable_from_an_experience(tmp_path):
    page_apps = [app for app in APPS if app.kind == "page"]
    seed = _ui(tmp_path)
    try:
        assert {app.target for app in page_apps} == set(seed.pages.IDS)
    finally:
        seed.fb.close()

    for app in page_apps:
        ui = _ui(tmp_path, experience="atlas")
        try:
            ui.app_launcher = True
            ui._open_app(app.id)
            assert ui.pages.IDS[ui.page] == app.target
            assert ui.experience.page_id == app.target
            assert ui.app_launcher is False
            image = ui._compose(ui.page)
            assert image.size == (480, 320)
            snap = ui.scene_runtime.snapshot()
            if get_experience_renderer("atlas", app.target):
                assert snap["scene"] == f"experience:atlas:{app.target}"
            else:
                assert snap["scene"] == f"page:{app.target}"
        finally:
            ui.fb.close()


def test_experience_navigation_uses_full_primary_carousel_and_shared_fallback(tmp_path):
    ui = _ui(tmp_path, experience="atlas", page="home")
    try:
        assert tuple(ui.experience.pages) == tuple(ui.pages.IDS)
        assert ui.experience.page_id == "home"
        ui.on_input("swipe", {"axis": "x", "dx": -100, "delta": 1})
        assert ui.experience.page_id == "overview"
        assert ui.pages.IDS[ui.page] == "overview"
        image = ui._compose(ui.page)
        assert image.size == (480, 320)
        assert ui.scene_runtime.snapshot()["scene"] == "page:overview"
    finally:
        ui.fb.close()


def test_authored_shell_navigation_points_into_full_carousel(tmp_path):
    ui = _ui(tmp_path, experience="atlas", page="home")
    try:
        ui._compose(ui.page)
        layers = {row["id"]: row for row in ui.scene_runtime.snapshot()["layers"]}
        nav = layers["atlas_v30.home.nav_next"]
        assert nav["touch"] == "experience_page:overview"
    finally:
        ui.fb.close()


def test_board_apps_route_to_shared_dashboard_inside_experience(tmp_path):
    ui = _ui(tmp_path)
    try:
        board = {"id": "fieldboard", "label": "Field Board", "widgets": []}
        ui.custom_boards = [board]
        ui.apps = ui._build_app_registry()
        ui._open_app("board:fieldboard")
        assert ui.pages.IDS[ui.page] == "dashboard"
        assert ui.experience.page_id == "dashboard"
        assert ui.active_board_id == "fieldboard"
        ui._compose(ui.page)
        assert ui.scene_runtime.snapshot()["scene"] == "page:dashboard"
    finally:
        ui.fb.close()


def test_theme_palette_bridge_visibly_changes_opted_in_experience_page(tmp_path):
    ui = _ui(tmp_path, experience="atlas", theme="classic")
    try:
        a = ui._compose(ui.page).copy()
        other = next(tid for tid in ui.THEMES if tid != ui.theme.id)
        from beastui.theme import load_theme
        ui.theme = load_theme(ui.theme_paths[other])
        b = ui._compose(ui.page).copy()
        assert ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox() is not None
    finally:
        ui.fb.close()


def test_capsule_long_press_has_predictable_back_behavior(tmp_path):
    ui = _ui(tmp_path)
    try:
        ui.capsule_share_overlay = True
        ui.app_launcher = False
        ui.on_input("long_press", {"x": 240, "y": 160})
        assert ui.capsule_share_overlay is False
        assert ui.app_launcher is True
    finally:
        ui.fb.close()


def test_every_experience_can_reach_every_primary_page_with_truthful_renderer_fallback(tmp_path):
    experiences = ("atlas", "forge", "observatory", "habitat", "monolith")
    for experience in experiences:
        ui = _ui(tmp_path, experience=experience)
        try:
            for page_id in ui.pages.IDS:
                ui._open_app(page_id)
                assert ui.pages.IDS[ui.page] == page_id
                assert ui.experience.page_id == page_id
                image = ui._compose(ui.page)
                assert image.size == (480, 320)
                scene = ui.scene_runtime.snapshot()["scene"]
                expected = (
                    f"experience:{experience}:{page_id}"
                    if get_experience_renderer(experience, page_id)
                    else f"page:{page_id}"
                )
                assert scene == expected
        finally:
            ui.fb.close()


def test_all_builtin_overlay_apps_open_and_render_from_experience(tmp_path):
    overlay_apps = [app for app in APPS if app.kind == "overlay"]
    ui = _ui(tmp_path, experience="atlas")
    try:
        for app in overlay_apps:
            ui.app_launcher = True
            ui.capsule_share_overlay = False
            ui.telemetry_overlay = False
            ui.correlation_overlay = False
            ui.plugins_overlay = False
            ui.beastdex_overlay = False
            ui.capture_vault_overlay = False
            ui.performance_overlay = False
            ui.platform_overlay = None
            ui.studio_overlay = False
            ui.theme_library = False
            ui.theme_detail = None
            ui.visualizer_overlay = False
            ui.achievements_overlay = False
            ui.help_overlay = False
            ui._open_app(app.id)
            image = ui._compose(ui.page)
            assert image.size == (480, 320), app.id
    finally:
        ui.fb.close()
