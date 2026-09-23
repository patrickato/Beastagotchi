from pathlib import Path

from beastcore.presentation import PresentationBroker, normalize_owner
from beastui.design import TOKENS, PRIMARY_PAGES, PAGE_GROUPS


class _S:
    def __init__(self, d=None):
        self.d = dict(d or {})

    def get(self, key, default=None):
        return self.d.get(key, default)


def test_v019_design_tokens_preserve_validated_reference_geometry():
    assert (TOKENS.canvas_w, TOKENS.canvas_h) == (480, 320)
    assert TOKENS.header_h == 34 and TOKENS.footer_y == 278
    assert TOKENS.touch_min >= 48 and TOKENS.touch_primary >= TOKENS.touch_normal
    assert TOKENS.motion_page_s > TOKENS.motion_fast_s > 0


def test_v019_page_model_preserves_beast_and_operational_pages():
    assert PRIMARY_PAGES[0] == "home"
    assert "beast" in PRIMARY_PAGES
    assert "captures" in PRIMARY_PAGES
    assert "map" in PRIMARY_PAGES
    assert "system" in PRIMARY_PAGES
    assert PAGE_GROUPS["identity"] == ("home", "beast")


def test_presentation_owner_aliases_are_explicit():
    assert normalize_owner("pwn-native") == "native"
    assert normalize_owner("theme-manager") == "theme_manager"
    assert normalize_owner("beast-ui") == "beast"


def test_presentation_broker_persists_requested_owner_without_executing_handoff(tmp_path):
    p = tmp_path / "presentation.json"
    s = _S({"pwnagotchi.service.state": "active", "platform.services": [], "plugins.catalog": []})
    b = PresentationBroker(s, path=str(p), clock=lambda: 100.0)
    first = b.tick()
    assert first["presentation.desired_owner"] == "native"
    assert first["presentation.executor_enabled"] is False

    row = b.request("beast-ui", requested_by="test")
    assert row["desired_owner"] == "beast"
    assert row["status"] == "requested"

    reloaded = PresentationBroker(s, path=str(p), clock=lambda: 101.0).tick()
    assert reloaded["presentation.desired_owner"] == "beast"
    assert reloaded["presentation.executor_enabled"] is False


def test_presentation_broker_surfaces_legacy_theme_manager_conflict(tmp_path):
    s = _S({
        "pwnagotchi.service.state": "active",
        "platform.services": [{"unit": "beast-ui.service", "active": "active"}],
        "plugins.catalog": [{"name": "theme_manager", "enabled": True}],
    })
    b = PresentationBroker(s, path=str(tmp_path / "p.json"), clock=lambda: 1.0)
    b.mark_active("beast")
    row = b.tick()
    assert row["presentation.theme_manager.installed"] is True
    assert row["presentation.theme_manager.enabled"] is True
    assert row["presentation.conflict_count"] == 1
    assert row["presentation.executor_enabled"] is False


def test_presentation_state_file_is_private(tmp_path):
    p = tmp_path / "p.json"
    b = PresentationBroker(_S(), path=str(p), clock=lambda: 1.0)
    b.request("native")
    assert p.exists()
    assert (p.stat().st_mode & 0o777) == 0o600


def test_v019_home_visual_smoke_across_theme_families(tmp_path):
    from PIL import Image
    from beastui.engine import BeastUI

    root = Path(__file__).resolve().parents[1] / "beastui"
    state = {
        "progression.level": 27,
        "progression.max_level": 100,
        "progression.stage": "Stalker",
        "progression.aura": "spark",
        "progression.level_progress_pct": 63.0,
        "progression.xp_current_level": 420,
        "progression.xp_next_level": 245,
        "beast.expression": "curious",
        "pwnagotchi.mood": "awake",
        "context.mode.effective": "pwn",
        "wifi.ap_count": 18,
        "wifi.client_count": 4,
        "wifi.encounters.session_unique": 42,
        "wifi.encounters.lifetime_unique": 1337,
        "radio.primary.channel": 11,
        "system.cpu.total": 21.0,
        "system.temp.cpu_c": 58.0,
        "pwnagotchi.handshakes": 3,
        "gps.fix": True,
        "health.core.state": "healthy",
        "dock.state": "field",
        "governor.mode": "FULL",
    }

    for theme in ("classic", "blackice", "hunter", "synthwave", "lcars"):
        out = tmp_path / f"home-{theme}.png"
        ui = BeastUI(root=root, output=str(out), theme_id=theme)
        ui.state = dict(state)
        ui.page = ui.pages.IDS.index("home")
        ui.render()
        assert out.is_file(), theme
        with Image.open(out) as im:
            assert im.size == (480, 320)
            assert im.getbbox() == (0, 0, 480, 320)
