from beastcore.plugin_integration import PluginIntegrationEngine


class _S:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def test_stock_plugin_catalog_has_capability_and_requirement_metadata():
    state = _S({
        "platform.plugins": [
            {"name": "gps", "enabled": True, "configured": True},
            {"name": "pisugarx", "enabled": True, "configured": True},
            {"name": "wigle", "enabled": True, "configured": True},
            {"name": "gpio_buttons", "enabled": True, "configured": True},
        ]
    })
    out = PluginIntegrationEngine(state).tick()
    rows = {row["name"]: row for row in out["plugins.catalog"]}

    assert "location.position" in rows["gps"]["provides"]
    assert rows["gps"]["provider_group"] == "location"
    assert rows["pisugarx"]["provider_group"] == "power"
    assert rows["pisugarx"]["hardware_specific"] is True
    assert rows["wigle"]["credential_required"] is True
    assert rows["wigle"]["data_egress"] == "location_and_network_metadata"
    assert "gpio.available" in rows["gpio_buttons"]["requires"]

    assert out["plugins.requirements_model"] == "dependency_capability_resolver_v0.1_catalog_only"
    assert out["plugins.requirements_executor_enabled"] is False


def test_stock_known_external_entries_do_not_claim_implemented_adapters():
    for name in ("gps_listener", "pwndroid", "ups_hat_c", "wittypi", "pisugarx"):
        row = PluginIntegrationEngine._binding(name)
        assert row["integration"] == "config_only"
        assert row["provides"]

    assert PluginIntegrationEngine._binding("pwndroid")["provider_group"] == "location"
    assert PluginIntegrationEngine._binding("ups_hat_c")["provider_group"] == "power"


def test_overlapping_provider_plugins_are_cataloged_not_double_counted_as_truth():
    state = _S({
        "platform.plugins": [
            {"name": "gps", "enabled": True, "configured": True},
            {"name": "pwndroid", "enabled": True, "configured": True},
            {"name": "ups_lite", "enabled": True, "configured": True},
            {"name": "pisugarx", "enabled": True, "configured": True},
        ]
    })
    out = PluginIntegrationEngine(state).tick()
    rows = {row["name"]: row for row in out["plugins.catalog"]}

    assert rows["gps"]["provider_group"] == rows["pwndroid"]["provider_group"] == "location"
    assert rows["ups_lite"]["provider_group"] == rows["pisugarx"]["provider_group"] == "power"
    # This milestone only catalogs provider overlap. It deliberately does not
    # select or activate providers, install dependencies or mutate configuration.
    assert all(row["requirements_resolution"] == "catalog_only" for row in rows.values())
    assert out["plugins.requirements_executor_enabled"] is False
