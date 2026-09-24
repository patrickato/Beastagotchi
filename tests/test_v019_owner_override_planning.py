from beastcore.plugin_broker import PluginBroker


def _broker(tmp_path, text: str):
    cfg = tmp_path / "config.toml"
    cfg.write_text(text)
    confd = tmp_path / "conf.d"
    confd.mkdir()
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    return PluginBroker(
        config_path=str(cfg),
        conf_d=str(confd),
        custom_plugins=str(plugins),
        snapshot_root=str(tmp_path / "snapshots"),
        service_active=lambda unit: unit == "beast-ui.service",
    )


def test_owner_override_metadata_distinguishes_policy_from_technical_blockers(tmp_path):
    broker = _broker(
        tmp_path,
        """
[main.plugins.beast_bridge]
enabled = true

[main.plugins.theme_manager]
enabled = false
""",
    )

    bridge = broker.plan_toggle("beast_bridge", False, beast_ui_active=True)
    assert bridge["managed_allowed"] is False
    assert bridge["technical_blockers"] == []
    assert bridge["policy_blockers"]
    assert bridge["owner_override_available"] is True
    assert bridge["owner_override_executed"] is False

    theme = broker.plan_toggle("theme_manager", True, beast_ui_active=True)
    assert theme["technical_blockers"] == []
    assert theme["policy_blockers"]
    assert theme["owner_override_available"] is True
    assert theme["allowed"] is False


def test_missing_plugin_is_a_technical_blocker_not_fake_override(tmp_path):
    broker = _broker(tmp_path, "[main.plugins]\n")
    plan = broker.plan_toggle("not_installed", True, beast_ui_active=False)

    assert plan["technical_blockers"] == ["plugin is not installed/configured"]
    assert plan["policy_blockers"] == []
    assert plan["owner_override_available"] is False
    assert plan["managed_allowed"] is False
