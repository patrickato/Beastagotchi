from beastcore.dependency_resolver import DependencyCapabilityResolver


class _S:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def test_native_capabilities_satisfy_requirements_without_new_pollers():
    state = _S({
        "gps.state": "connected_no_fix",
        "capabilities.present": ["display", "i2c"],
        "system.cpu.total": 12.0,
        "network.internet.state": "online",
        "pwnagotchi.service.state": "active",
    })
    resolver = DependencyCapabilityResolver(
        state,
        which=lambda name: "/usr/bin/systemctl" if name == "systemctl" else None,
        path_exists=lambda path: False,
    )

    for requirement in (
        "location.position",
        "display.primary",
        "i2c",
        "system.telemetry",
        "network.internet",
        "pwnagotchi.service",
    ):
        row = resolver.resolve_requirement(requirement)
        assert row.status == "satisfied", (requirement, row.as_dict())
        assert row.providers


def test_unknown_is_policy_blocker_while_missing_service_is_technical():
    state = _S({
        "platform.services": [
            {"unit": "gpsd.service", "load": "loaded", "active": "inactive", "sub": "dead"},
        ],
        "capabilities.present": [],
    })
    resolver = DependencyCapabilityResolver(
        state,
        which=lambda name: None,
        path_exists=lambda path: False,
    )
    out = resolver.resolve_components([
        {
            "id": "map",
            "enabled": True,
            "requires": ["gpsd.service", "mystery.capability"],
            "provides": [],
        }
    ])
    row = out["components"]["map"]
    assert "gpsd.service" in row["technical_blockers"]
    assert "mystery.capability" in row["policy_blockers"]
    assert row["owner_override_available"] is False
    assert row["requirements_status"] == "blocked"


def test_component_provider_graph_and_reverse_used_by_are_read_only():
    resolver = DependencyCapabilityResolver(
        _S({}),
        which=lambda name: None,
        path_exists=lambda path: False,
    )
    out = resolver.resolve_components([
        {
            "id": "gps-plugin",
            "enabled": True,
            "provides": ["location.position"],
            "requires": [],
        },
        {
            "id": "expedition-map",
            "enabled": True,
            "provides": [],
            "requires": ["location.position"],
        },
    ])

    row = out["components"]["expedition-map"]
    assert row["requirements_ready"] is True
    assert row["required_results"][0]["providers"] == ["component:gps-plugin"]
    assert out["used_by"]["component:gps-plugin"] == ["expedition-map"]
    assert out["execution_enabled"] is False
    assert out["provider_selection_enabled"] is False


def test_disabled_catalog_entries_do_not_make_active_health_look_broken():
    resolver = DependencyCapabilityResolver(
        _S({"capabilities.present": [], "platform.hardware": []}),
        which=lambda name: None,
        path_exists=lambda path: False,
    )
    out = resolver.resolve_components([
        {
            "id": "optional-ups",
            "enabled": False,
            "provides": ["power.battery.telemetry"],
            "requires": ["hardware.some_future_ups"],
        }
    ])
    assert out["summary"]["selected_component_count"] == 0
    assert out["summary"]["active_policy_blocker_count"] == 0
    assert out["summary"]["active_technical_blocker_count"] == 0
    assert out["summary"]["catalog_policy_blocker_count"] == 1


def test_prefixed_presence_probes_are_bounded_and_non_mutating():
    commands = []

    def runner(cmd, timeout=0):
        commands.append((list(cmd), timeout))
        if cmd[:2] == ["dpkg-query", "-W"] and cmd[-1] == "curl":
            return 0, "curl 8.0\n", ""
        return 1, "", "missing"

    modules = {"json": object()}

    resolver = DependencyCapabilityResolver(
        _S({}),
        command_runner=runner,
        which=lambda name: "/usr/bin/curl" if name == "curl" else None,
        path_exists=lambda path: path == "/dev/example",
        module_finder=lambda name: modules.get(name),
    )

    assert resolver.resolve_requirement("package:curl").status == "satisfied"
    assert resolver.resolve_requirement("package:not-there").status == "missing_installable"
    assert resolver.resolve_requirement("executable:curl").status == "satisfied"
    assert resolver.resolve_requirement("python:json").status == "satisfied"
    assert resolver.resolve_requirement("path:/dev/example").status == "satisfied"
    assert commands == [
        (["dpkg-query", "-W", "curl"], 2),
        (["dpkg-query", "-W", "not-there"], 2),
    ]


def test_credential_presence_is_never_the_credential_value():
    resolver = DependencyCapabilityResolver(
        _S({}),
        which=lambda name: None,
        path_exists=lambda path: False,
    )
    ready = resolver.resolve_components([
        {
            "id": "external-service",
            "enabled": True,
            "credential_required": True,
            "credential_present": True,
            "requires": [],
            "provides": [],
        }
    ])
    cred = ready["components"]["external-service"]["credential_results"][0]
    assert cred["status"] == "satisfied"
    assert cred["evidence"] == {"present": True}

    missing = resolver.resolve_components([
        {
            "id": "external-service",
            "enabled": True,
            "credential_required": True,
            "credential_present": False,
            "requires": [],
            "provides": [],
        }
    ])
    row = missing["components"]["external-service"]
    assert row["credential_results"][0]["status"] == "credential_missing"
    assert "credential:external-service" in row["technical_blockers"]
