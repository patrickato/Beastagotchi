from __future__ import annotations

from pathlib import Path

from beastcore.presentation_broker import PresentationBroker, PresentationBrokerError
from beastui.design_system import PAGE_GROUPS, PRIMARY_PAGES, TOKENS


class FakePresentation:
    def __init__(self, *, fail_acquire=False, fail_health=False):
        self.active = False
        self.fail_acquire = fail_acquire
        self.fail_health = fail_health

    def prepare_release(self):
        return {"ok": True}

    def release(self):
        self.active = False
        return {"ok": True}

    def acquire(self):
        if self.fail_acquire:
            return {"ok": False, "error": "simulated acquire failure"}
        self.active = True
        return {"ok": True}

    def health(self):
        return {"ok": self.active and not self.fail_health}


def test_v019_page_model_preserves_beast_and_operational_pages():
    assert PRIMARY_PAGES[0] == "home"
    assert "beast" in PRIMARY_PAGES
    assert "captures" in PRIMARY_PAGES
    assert "map" in PRIMARY_PAGES
    assert "system" in PRIMARY_PAGES
    assert PAGE_GROUPS["identity"] == ("home", "beast")
    assert TOKENS.touch_preferred >= TOKENS.touch_min >= 34


def test_presentation_broker_switch_persists(tmp_path: Path):
    state = tmp_path / "presentation.json"
    broker = PresentationBroker(str(state))
    beast = FakePresentation()
    korrie = FakePresentation()
    broker.register("beast-ui", beast)
    broker.register("korrie-theme-manager", korrie)
    beast.active = True

    result = broker.switch("korrie-theme-manager")
    assert result["ok"] is True
    assert result["changed"] is True
    assert broker.status()["lease"]["owner"] == "korrie-theme-manager"

    reloaded = PresentationBroker(str(state))
    assert reloaded.status()["lease"]["owner"] == "korrie-theme-manager"


def test_presentation_broker_rolls_back_failed_handoff(tmp_path: Path):
    broker = PresentationBroker(str(tmp_path / "presentation.json"))
    beast = FakePresentation()
    bad = FakePresentation(fail_acquire=True)
    broker.register("beast-ui", beast)
    broker.register("korrie-theme-manager", bad)
    beast.active = True

    result = broker.switch("korrie-theme-manager")
    assert result["ok"] is False
    assert result["owner"] == "beast-ui"
    assert result["rollback"]["ok"] is True
    assert beast.active is True
    assert broker.status()["lease"]["owner"] == "beast-ui"


def test_presentation_broker_refuses_unknown_owner(tmp_path: Path):
    broker = PresentationBroker(str(tmp_path / "presentation.json"))
    try:
        broker.plan_switch("mystery-ui")
    except PresentationBrokerError:
        pass
    else:
        raise AssertionError("unknown owner must be rejected")


def test_v019_home_visual_smoke_across_theme_families(tmp_path: Path):
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
        "pwnagotchi.mood": "awake",
        "context.mode.effective": "pwn",
        "wifi.ap_count": 18,
        "wifi.encounters.session_unique": 42,
        "wifi.encounters.lifetime_unique": 1337,
        "radio.primary.channel": 11,
        "system.temp.cpu_c": 58.0,
        "pwnagotchi.handshakes": 3,
        "gps.fix": True,
        "health.core.state": "healthy",
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
