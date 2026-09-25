from beastcore.dependency_resolver import DependencyCapabilityResolver
from beastcore.experience_compiler import (
    ExperienceCompileError,
    compile_builtin_catalog,
    compile_experience,
)


def _resolver_state():
    return {
        "radio.primary.state": "available",
        "system.cpu.total": 22.0,
        "system.temp.cpu_c": 48.0,
        "display.physical.width": 480,
        "display.physical.height": 320,
        "capabilities.present": ["display"],
        "gps.state": "not_detected",
        "power.telemetry.available": False,
    }


def _resolver():
    return DependencyCapabilityResolver(
        _resolver_state(),
        which=lambda name: None,
        path_exists=lambda path: False,
        module_finder=lambda name: None,
        command_runner=lambda *a, **k: (1, "", ""),
    )


def test_compiler_keeps_atlas_identity_and_reports_real_page_coverage():
    row = compile_experience(
        "atlas",
        {"compute_tier": "full", "display_class": "reference"},
        resolver=_resolver(),
        renderer_pages=("home", "recon"),
    )
    assert row["experience_id"] == "atlas"
    assert row["variant"]["visual_family"] == "expedition"
    assert row["ready_for_preview"] is True
    assert row["ready_for_production_navigation"] is False
    assert row["page_coverage"]["implemented"] == ["home", "recon"]
    assert row["page_coverage"]["missing_preferred"] == ["map", "expedition"]
    assert "location.position" in row["capabilities"]["optional_missing"]
    assert row["writes_preferences"] is False
    assert row["installs_dependencies"] is False


def test_compiler_uses_common_dependency_resolver_for_experience_capabilities():
    row = compile_experience(
        "forge",
        {"compute_tier": "full", "display_class": "reference"},
        resolver=_resolver(),
        renderer_pages=("home",),
    )
    optional = {
        x["requirement"]: x
        for x in row["capabilities"]["resolution"]["optional_results"]
    }
    assert optional["system.telemetry"]["satisfied"] is True
    assert optional["radio.wifi.monitor"]["satisfied"] is True
    assert optional["display.primary"]["satisfied"] is True
    assert optional["power.battery.telemetry"]["satisfied"] is False


def test_compiler_preserves_identity_on_constrained_platform_and_incident_context():
    row = compile_experience(
        "habitat",
        {"compute_tier": "constrained", "display_class": "reference"},
        context="incident",
        resolver=_resolver(),
        renderer_pages=("home", "beast"),
    )
    assert row["variant"]["visual_family"] == "companion"
    assert row["variant"]["quality_variant"] == "constrained"
    assert row["doctor_visibility"] == "operations_first"
    assert row["variant"]["identity_preserved"] is True


def test_catalog_compiles_all_builtins_without_inventing_missing_pages():
    coverage = {
        "atlas": ["home", "recon"],
        "forge": ["home"],
        "observatory": ["home", "spectrum"],
        "habitat": ["home", "beast"],
        "monolith": ["home"],
    }
    rows = compile_builtin_catalog(
        {"compute_tier": "full", "display_class": "reference"},
        resolver=_resolver(),
        renderer_coverage=coverage,
    )
    by_id = {row["experience_id"]: row for row in rows}
    assert by_id["observatory"]["page_coverage"]["implemented"] == ["home", "spectrum"]
    assert by_id["dossier"]["page_coverage"]["implemented"] == []
    assert by_id["dossier"]["ready_for_preview"] is False


def test_unknown_experience_fails_explicitly():
    try:
        compile_experience("does-not-exist", {})
    except ExperienceCompileError as exc:
        assert "unknown built-in Experience" in str(exc)
    else:
        raise AssertionError("unknown Experience should fail")
