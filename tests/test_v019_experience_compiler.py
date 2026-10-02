from beastcore.dependency_resolver import DependencyCapabilityResolver
from beastcore.experience_compiler import (
    ExperienceCompileError,
    compile_builtin_catalog,
    compile_experience,
    compile_pack_experience,
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


def test_pack_experience_compiles_through_common_resolver_without_mutation():
    row = compile_pack_experience(
        "pack_field-experience_field",
        {
            "visual_family": "expedition",
            "layout_family": "map_first",
            "density": "balanced",
            "motion_profile": "calm_ambient",
            "creature_presence": "supporting",
            "utility_bias": "instrument",
            "playfulness": "low",
            "alert_style": "field",
            "doctor_visibility": "contextual",
            "mystery_level": "discoverable",
        },
        {"compute_tier": "full", "display_class": "reference"},
        label="Field Companion",
        requires=["display.primary"],
        optional_requirements=["location.position"],
        preferred_pages=["home", "recon", "map"],
        resolver=_resolver(),
        renderer_pages=["home", "recon"],
        source_pack="field-experience",
        source_file="/packs/field/missions/field.json",
    )
    assert row["experience_id"] == "pack_field-experience_field"
    assert row["source"]["kind"] == "pack"
    assert row["source"]["pack_id"] == "field-experience"
    assert row["variant"]["visual_family"] == "expedition"
    assert row["page_coverage"]["missing_preferred"] == ["map"]
    assert row["capabilities"]["resolution"]["requirements_ready"] is True
    assert row["writes_preferences"] is False
    assert row["installs_dependencies"] is False
    assert row["selects_providers"] is False


def test_pack_experience_rejects_invalid_dna_explicitly():
    try:
        compile_pack_experience(
            "pack_bad",
            {"visual_family": "not_namespaced", "layout_family": "also_bad"},
            {},
        )
    except ValueError as exc:
        assert "visual_family" in str(exc)
    else:
        raise AssertionError("invalid Pack DNA should fail")


def test_reference_target_can_be_native_but_medium_requires_explicit_scene_variant():
    reference = compile_experience(
        "monolith",
        {
            "compute_tier": "full",
            "display_class": "reference",
            "primary_display": {"width": 480, "height": 320},
        },
        resolver=_resolver(),
        renderer_pages=("home", "overview"),
        renderer_native_targets=("reference",),
    )
    assert reference["render_target"]["native_supported"] is True
    assert reference["render_target"]["render_mode"] == "native_reference"
    assert reference["render_target"]["requested_size"] == [480, 320]
    assert reference["ready_for_native_target"] is True
    assert reference["ready_for_production_navigation"] is True

    medium = compile_experience(
        "monolith",
        {
            "compute_tier": "full",
            "display_class": "medium",
            "primary_display": {"width": 800, "height": 480},
        },
        resolver=_resolver(),
        renderer_pages=("home", "overview"),
        renderer_native_targets=("reference",),
    )
    assert medium["ready_for_preview"] is True
    assert medium["render_target"]["native_supported"] is False
    assert medium["render_target"]["render_mode"] == "native_variant_required"
    assert medium["render_target"]["reflow_required"] is True
    assert medium["render_target"]["compatibility_scaling_is_native"] is False
    assert medium["render_target"]["scale_hint"] == 1.5
    assert medium["ready_for_native_target"] is False
    assert medium["ready_for_production_navigation"] is False
