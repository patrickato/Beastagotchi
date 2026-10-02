from beastcore.experience_dna import (
    BUILTIN_EXPERIENCE_DNA,
    LEGACY_REFERENCE_IDENTITIES,
    VISUAL_FAMILIES,
    compile_experience_variant,
    experience_dna_from_dict,
    get_experience_dna,
    validate_builtin_experiences,
)


def test_builtin_experience_dna_is_valid_and_broad():
    assert validate_builtin_experiences() == {}
    assert len(VISUAL_FAMILIES) >= 16
    assert len(BUILTIN_EXPERIENCE_DNA) >= 8
    # The new architecture must not collapse back to the old handful of named themes.
    assert {"atlas", "forge", "observatory", "habitat", "monolith"} <= set(BUILTIN_EXPERIENCE_DNA)
    assert not (set(BUILTIN_EXPERIENCE_DNA) & LEGACY_REFERENCE_IDENTITIES)


def test_first_prototype_families_are_deliberately_different():
    assert get_experience_dna("atlas").visual_family == "expedition"
    assert get_experience_dna("forge").visual_family == "industrial"
    assert get_experience_dna("observatory").visual_family == "scientific"
    assert get_experience_dna("habitat").visual_family == "companion"
    assert get_experience_dna("monolith").visual_family == "premium"
    assert len({
        get_experience_dna("atlas").layout_family,
        get_experience_dna("forge").layout_family,
        get_experience_dna("observatory").layout_family,
        get_experience_dna("habitat").layout_family,
        get_experience_dna("monolith").layout_family,
    }) == 5


def test_constrained_variant_preserves_identity_but_reduces_cost():
    dna = get_experience_dna("observatory")
    full = compile_experience_variant(dna, {
        "compute_tier": "full", "display_class": "reference",
    })
    constrained = compile_experience_variant(dna, {
        "compute_tier": "constrained", "display_class": "reference",
    })
    assert full["experience_id"] == constrained["experience_id"] == "observatory"
    assert full["visual_family"] == constrained["visual_family"] == "scientific"
    assert constrained["identity_preserved"] is True
    assert constrained["quality_variant"] == "constrained"
    assert constrained["density"] in {"glance", "balanced", "dense"}
    assert constrained["motion_profile"] in {"still", "subtle"}


def test_large_enhanced_variant_can_add_density_without_changing_identity():
    dna = get_experience_dna("atlas")
    reference = compile_experience_variant(dna, {
        "compute_tier": "full", "display_class": "reference",
    })
    enhanced = compile_experience_variant(dna, {
        "compute_tier": "enhanced", "display_class": "large",
    })
    assert enhanced["experience_id"] == "atlas"
    assert enhanced["layout_family"] == "map_first"
    assert enhanced["visual_family"] == "expedition"
    assert enhanced["density"] != "glance"
    assert reference["identity_preserved"] and enhanced["identity_preserved"]


def test_context_can_promote_doctor_without_turning_experience_into_doctor_theme():
    dna = get_experience_dna("habitat")
    normal = compile_experience_variant(dna, {
        "compute_tier": "full", "display_class": "reference",
    })
    incident = compile_experience_variant(dna, {
        "compute_tier": "full", "display_class": "reference",
    }, context="incident")
    assert normal["doctor_visibility"] == "background"
    assert incident["doctor_visibility"] == "operations_first"
    assert incident["visual_family"] == "companion"
    assert incident["creature_presence"] == "dominant"


def test_night_context_reduces_motion_without_changing_family():
    dna = get_experience_dna("forge")
    night = compile_experience_variant(dna, {
        "compute_tier": "full", "display_class": "reference",
    }, context="night")
    assert night["motion_profile"] == "subtle"
    assert night["visual_family"] == "industrial"
    assert night["layout_family"] == "cockpit_cluster"


def test_namespaced_pack_families_can_extend_presentation_without_core_patch():
    from beastcore.experience_dna import ExperienceDNA

    custom = ExperienceDNA(
        id="example_biomech",
        label="Example Biomech",
        visual_family="example.biomech",
        layout_family="example.organism",
        motion_profile="example.pulse",
        alert_style="example.alert",
    )
    assert custom.validate() == ()

    bad = ExperienceDNA(
        id="bad_custom",
        label="Bad Custom",
        visual_family="biomech",
        layout_family="organism",
    )
    errors = bad.validate()
    assert any("visual_family" in x for x in errors)
    assert any("layout_family" in x for x in errors)


def test_pack_dna_parser_validates_core_and_namespaced_axes():
    row = experience_dna_from_dict({
        "visual_family": "example.biomech",
        "layout_family": "example.organism",
        "density": "dense",
        "motion_profile": "example.pulse",
        "creature_presence": "supporting",
        "utility_bias": "instrument",
        "playfulness": "low",
        "alert_style": "example.alert",
        "input_model": "touch_first",
        "doctor_visibility": "contextual",
        "mystery_level": "discoverable",
        "hardware_fit": ["reference", "large"],
        "mission_bias": ["field", "signals"],
        "tags": ["pack", "biomech"],
    }, experience_id="pack_example_biomech", label="Pack Biomech")
    assert row.id == "pack_example_biomech"
    assert row.visual_family == "example.biomech"
    assert row.layout_family == "example.organism"
    assert row.hardware_fit == ("reference", "large")
    assert row.validate() == ()

    try:
        experience_dna_from_dict({
            "visual_family": "biomech",
            "layout_family": "organism",
        }, experience_id="bad_pack", label="Bad")
    except ValueError as exc:
        assert "visual_family" in str(exc)
        assert "layout_family" in str(exc)
    else:
        raise AssertionError("unnamespaced Pack vocab should fail")
