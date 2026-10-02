from __future__ import annotations

from pathlib import Path

from beastcore.collectors.display import DisplayCollector
from beastcore.presentation_transition import PresentationTransitionPlanner


class FakeState:
    def __init__(self, data):
        self.data = dict(data)

    def get(self, key, default=None):
        return self.data.get(key, default)


def state(*, beast=False, theme_installed=True, theme_enabled=False, backup=False, managed=False):
    services = [
        {"unit":"pwnagotchi.service","active":"active"},
        {"unit":"beast-ui.service","active":"active" if beast else "inactive"},
    ]
    plugins = []
    if theme_installed:
        plugins.append({"name":"theme_manager","enabled":theme_enabled})
    return FakeState({
        "platform.services": services,
        "pwnagotchi.service.state": "active",
        "plugins.catalog": plugins,
        "display.handoff.backup_exists": backup,
        "presentation.theme_manager.managed_handoff_supported": managed,
        "presentation.active_owner": "beast" if beast else ("theme_manager" if theme_enabled else "native"),
    })


def test_beast_to_theme_manager_compatibility_plan_uses_clean_toggle():
    plan = PresentationTransitionPlanner(
        state(beast=True, theme_enabled=False, backup=True)
    ).plan("theme_manager")
    ids = [x["id"] for x in plan["steps"]]
    assert plan["allowed"] is True
    assert plan["strategy"] == "compatibility_toggle"
    assert ids == ["display.beast.release", "plugin.theme_manager.enable", "verify.theme_manager"]
    assert plan["executor_enabled"] is False
    assert any("WebUI" in x for x in plan["warnings"])


def test_theme_manager_to_beast_disables_plugin_before_claim():
    plan = PresentationTransitionPlanner(
        state(beast=False, theme_enabled=True, backup=False)
    ).plan("beast")
    ids = [x["id"] for x in plan["steps"]]
    assert ids[0] == "plugin.theme_manager.disable"
    assert "display.beast.claim" in ids


def test_beast_release_requires_visible_rollback_backup():
    plan = PresentationTransitionPlanner(
        state(beast=True, theme_enabled=False, backup=False)
    ).plan("native")
    assert plan["allowed"] is False
    assert any("rollback backup" in x for x in plan["blockers"])


def test_managed_theme_manager_contract_preserves_webui():
    plan = PresentationTransitionPlanner(
        state(beast=True, theme_enabled=True, backup=True, managed=True)
    ).plan("theme_manager")
    assert plan["strategy"] == "managed"
    assert any(x["id"] == "theme_manager.acquire" for x in plan["steps"])
    assert not any("WebUI is therefore unavailable" in x for x in plan["warnings"])


def test_display_collector_exposes_handoff_evidence(tmp_path: Path):
    graphics = tmp_path/"graphics"; drm=tmp_path/"drm"; handoff=tmp_path/"handoff"; runtime=tmp_path/"run"
    graphics.mkdir();drm.mkdir();handoff.mkdir();runtime.mkdir()
    (handoff/"config.toml.pre-beast").write_text("backup")
    (handoff/"confirmed").touch()
    (runtime/"ui-test-mode").touch()
    row=DisplayCollector(str(graphics),str(drm),str(handoff),str(runtime)).collect()
    assert row["display.handoff.backup_exists"] is True
    assert row["display.handoff.confirmed"] is True
    assert row["display.handoff.test_mode"] is True
