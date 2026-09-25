from beastcore.integration_catalog import IntegrationCatalog, INTEGRATIONS
from beastcore.dependency_resolver import DependencyCapabilityResolver
from beastcore.state import StateRegistry


def _runner(cmd, timeout=2):
    if cmd[:2] == ["dpkg-query", "-W"]:
        pkg = cmd[2]
        installed = {
            "python3-cairo": "1.27.0-2",
            "librsvg2-bin": "2.60.0",
            "python3-psutil": "7.0.0-2",
            "bubblewrap": "0.11.0",
        }
        if pkg in installed:
            return 0, f"{pkg} {installed[pkg]}", ""
        return 1, "", "not installed"
    return 1, "", "unsupported"


def _which(name):
    return {"bwrap": "/usr/bin/bwrap"}.get(name)


def test_integration_catalog_is_read_only_and_capability_oriented():
    state = StateRegistry()
    state.update_many("test", {"capabilities.present": ["display"]})
    resolver = DependencyCapabilityResolver(state, command_runner=_runner, which=_which)
    cat = IntegrationCatalog(state, resolver=resolver)
    snap = cat.snapshot()

    assert snap["mode"] == "read_only_catalog"
    assert snap["execution_enabled"] is False
    assert snap["automatic_install_enabled"] is False
    assert snap["count"] == len(INTEGRATIONS)
    assert "os_packages" in snap["lanes"]
    assert "external_process" in snap["lanes"]
    assert all(row["auto_install"] is False for row in snap["items"])
    assert all(row["base_dependency"] is False for row in snap["items"])
    assert all(row.get("provides") for row in snap["items"])


def test_integration_catalog_reuses_dependency_resolver_evidence():
    state = StateRegistry()
    resolver = DependencyCapabilityResolver(state, command_runner=_runner, which=_which)
    rows = {row["id"]: row for row in IntegrationCatalog(state, resolver=resolver).entries()}

    assert rows["vector-cairo-svg"]["requirements_status"] == "ready"
    assert rows["runtime-bubblewrap"]["requirements_status"] == "ready"
    assert rows["system-psutil"]["requirements_status"] == "ready"
    assert rows["bluetooth-bleak"]["requirements_status"] == "blocked"
    assert "package:python3-bleak" in rows["bluetooth-bleak"]["technical_blockers"]
