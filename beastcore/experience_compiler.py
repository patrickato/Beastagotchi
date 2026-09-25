from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dependency_resolver import DependencyCapabilityResolver
from .experience_dna import (
    BUILTIN_EXPERIENCE_DNA,
    ExperienceDNA,
    compile_experience_variant,
    experience_dna_from_dict,
    get_experience_dna,
)


@dataclass(frozen=True)
class ExperienceComponentPolicy:
    requires: tuple[str, ...] = ()
    optional_requirements: tuple[str, ...] = ()
    preferred_pages: tuple[str, ...] = ("home",)
    presentation_engine: str = "beast_scene"
    fallback_policy: str = "identity_preserving"


BUILTIN_EXPERIENCE_POLICIES: dict[str, ExperienceComponentPolicy] = {
    "atlas": ExperienceComponentPolicy(
        optional_requirements=("location.position", "radio.wifi.monitor"),
        preferred_pages=("home", "recon", "map", "expedition"),
    ),
    "forge": ExperienceComponentPolicy(
        optional_requirements=(
            "system.telemetry", "radio.wifi.monitor", "power.battery.telemetry",
            "display.primary",
        ),
        preferred_pages=("home", "system", "overview"),
    ),
    "observatory": ExperienceComponentPolicy(
        optional_requirements=("radio.wifi.monitor", "system.telemetry", "location.position"),
        preferred_pages=("home", "spectrum", "recon"),
    ),
    "habitat": ExperienceComponentPolicy(
        optional_requirements=("location.position",),
        preferred_pages=("home", "beast", "expedition"),
    ),
    "monolith": ExperienceComponentPolicy(
        optional_requirements=("display.primary",),
        preferred_pages=("home", "overview"),
    ),
    "dossier": ExperienceComponentPolicy(
        optional_requirements=("storage.writable",),
        preferred_pages=("home", "overview", "system"),
    ),
    "stillwater": ExperienceComponentPolicy(
        optional_requirements=("power.battery.telemetry",),
        preferred_pages=("home", "beast"),
    ),
    "bench": ExperienceComponentPolicy(
        optional_requirements=("system.telemetry", "display.primary"),
        preferred_pages=("home", "system", "overview"),
    ),
}


class ExperienceCompileError(ValueError):
    pass


def _capability_resolution(
    experience_id: str,
    policy: ExperienceComponentPolicy,
    resolver: DependencyCapabilityResolver | None,
) -> dict[str, Any]:
    if resolver is None:
        return {
            "requirements_resolution": "unavailable",
            "requirements_ready": None,
            "requirements_status": "unknown",
            "required_results": [],
            "optional_results": [],
            "technical_blockers": [],
            "policy_blockers": [],
            "execution_enabled": False,
        }

    graph = resolver.resolve_components([{
        "id": f"experience:{experience_id}",
        "enabled": True,
        "selected": True,
        "requires": list(policy.requires),
        "optional_requirements": list(policy.optional_requirements),
        "provides": [],
    }])
    row = dict((graph.get("components") or {}).get(f"experience:{experience_id}") or {})
    row["execution_enabled"] = False
    row["provider_selection_enabled"] = bool(graph.get("provider_selection_enabled", False))
    return row


def compile_scene_target(
    platform_profile: dict[str, Any] | None,
    *,
    native_target_classes: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Describe target geometry/support without pretending scaling is native reflow."""
    profile = dict(platform_profile or {})
    display_class = str(profile.get("display_class") or "unknown").strip().lower()
    primary = profile.get("primary_display") if isinstance(profile.get("primary_display"), dict) else {}
    try:
        width = int(primary.get("width")) if primary.get("width") else None
        height = int(primary.get("height")) if primary.get("height") else None
    except (TypeError, ValueError):
        width, height = None, None
    if width and height:
        orientation = "landscape" if width >= height else "portrait"
    else:
        orientation = "unknown"

    native = tuple(dict.fromkeys(
        str(x).strip().lower()
        for x in (native_target_classes or ("reference",))
        if str(x).strip()
    ))
    exact_reference = (width, height) == (480, 320)
    class_only_reference = display_class == "reference" and not (width and height)
    native_supported = display_class in native and (
        display_class != "reference" or exact_reference or class_only_reference
    )
    if native_supported:
        mode = "native_reference" if display_class == "reference" else "native_variant"
    elif display_class == "unknown":
        mode = "target_unknown"
    else:
        mode = "native_variant_required"

    scale = None
    if width and height:
        scale = min(width / 480.0, height / 320.0)

    return {
        "schema": 1,
        "display_class": display_class,
        "requested_size": [width, height],
        "orientation": orientation,
        "reference_size": [480, 320],
        "native_target_classes": list(native),
        "native_supported": bool(native_supported),
        "render_mode": mode,
        "reflow_required": not bool(native_supported),
        "compatibility_scaling_is_native": False,
        "scale_hint": None if scale is None else round(float(scale), 3),
        "evidence": (
            "exact_dimensions" if width and height
            else "display_class_only" if display_class != "unknown"
            else "unknown"
        ),
    }



def compile_experience_definition(
    dna: ExperienceDNA,
    platform_profile: dict[str, Any] | None,
    *,
    context: str | None = None,
    resolver: DependencyCapabilityResolver | None = None,
    renderer_pages: list[str] | tuple[str, ...] | None = None,
    policy: ExperienceComponentPolicy | None = None,
    source: dict[str, Any] | None = None,
    native_target_classes: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Compile any validated Experience DNA definition without mutation."""
    errors = dna.validate()
    if errors:
        raise ExperienceCompileError("; ".join(errors))
    policy = policy or ExperienceComponentPolicy()
    variant = compile_experience_variant(dna, platform_profile or {}, context=context)
    implemented = tuple(dict.fromkeys(
        str(x).strip().lower()
        for x in (renderer_pages or ())
        if str(x).strip()
    ))
    preferred = tuple(policy.preferred_pages)
    missing_preferred = [page for page in preferred if page not in implemented]
    capability = _capability_resolution(dna.id, policy, resolver)
    target = compile_scene_target(
        platform_profile,
        native_target_classes=native_target_classes,
    )
    optional_missing = [
        row.get("requirement")
        for row in capability.get("optional_results", [])
        if isinstance(row, dict) and not bool(row.get("satisfied"))
    ]
    return {
        "schema": 1,
        "experience_id": dna.id,
        "label": dna.label,
        "dna": dna.as_dict(),
        "variant": variant,
        "presentation_engine": policy.presentation_engine,
        "fallback_policy": policy.fallback_policy,
        "source": dict(source or {"kind": "builtin"}),
        "page_coverage": {
            "implemented": list(implemented),
            "preferred": list(preferred),
            "missing_preferred": missing_preferred,
            "complete_for_preferred": not missing_preferred,
        },
        "capabilities": {
            "requires": list(policy.requires),
            "optional": list(policy.optional_requirements),
            "resolution": capability,
            "optional_missing": [x for x in optional_missing if x],
        },
        "doctor_visibility": variant["doctor_visibility"],
        "render_target": target,
        "ready_for_native_target": bool(implemented) and bool(target["native_supported"]),
        "writes_preferences": False,
        "installs_dependencies": False,
        "selects_providers": False,
        "ready_for_preview": "home" in implemented,
        "ready_for_production_navigation": (
            bool(implemented) and not missing_preferred and bool(target["native_supported"])
        ),
    }


def compile_pack_experience(
    runtime_id: str,
    raw_dna: dict[str, Any],
    platform_profile: dict[str, Any] | None,
    *,
    label: str | None = None,
    requires: list[str] | tuple[str, ...] | None = None,
    optional_requirements: list[str] | tuple[str, ...] | None = None,
    preferred_pages: list[str] | tuple[str, ...] | None = None,
    presentation_engine: str = "beast_scene",
    fallback_policy: str = "identity_preserving",
    context: str | None = None,
    resolver: DependencyCapabilityResolver | None = None,
    renderer_pages: list[str] | tuple[str, ...] | None = None,
    renderer_native_targets: list[str] | tuple[str, ...] | None = None,
    source_pack: str | None = None,
    source_file: str | None = None,
) -> dict[str, Any]:
    dna = experience_dna_from_dict(raw_dna, experience_id=runtime_id, label=label)
    policy = ExperienceComponentPolicy(
        requires=tuple(str(x) for x in (requires or ()) if str(x)),
        optional_requirements=tuple(str(x) for x in (optional_requirements or ()) if str(x)),
        preferred_pages=tuple(str(x).strip().lower() for x in (preferred_pages or ("home",)) if str(x).strip()),
        presentation_engine=str(presentation_engine or "beast_scene"),
        fallback_policy=str(fallback_policy or "identity_preserving"),
    )
    return compile_experience_definition(
        dna,
        platform_profile,
        context=context,
        resolver=resolver,
        renderer_pages=renderer_pages,
        policy=policy,
        source={
            "kind": "pack",
            "pack_id": str(source_pack or ""),
            "source_file": str(source_file or ""),
        },
        native_target_classes=renderer_native_targets,
    )



def compile_experience(
    experience_id: str,
    platform_profile: dict[str, Any] | None,
    *,
    context: str | None = None,
    resolver: DependencyCapabilityResolver | None = None,
    renderer_pages: list[str] | tuple[str, ...] | None = None,
    renderer_native_targets: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Compile Experience intent into a bounded, non-mutating runtime plan.

    This v1 compiler resolves identity, platform/display quality guidance,
    capability evidence and currently implemented page coverage. It does not
    install dependencies, select providers, write preferences or claim that an
    unimplemented page exists.
    """
    eid = str(experience_id or "").strip().lower()
    dna = get_experience_dna(eid)
    if dna is None:
        raise ExperienceCompileError(f"unknown built-in Experience: {eid or '?'}")
    errors = dna.validate()
    if errors:
        raise ExperienceCompileError("; ".join(errors))

    policy = BUILTIN_EXPERIENCE_POLICIES.get(eid, ExperienceComponentPolicy())
    return compile_experience_definition(
        dna,
        platform_profile,
        context=context,
        resolver=resolver,
        renderer_pages=renderer_pages,
        policy=policy,
        source={"kind": "builtin"},
        native_target_classes=renderer_native_targets,
    )


def compile_builtin_catalog(
    platform_profile: dict[str, Any] | None,
    *,
    context: str | None = None,
    resolver: DependencyCapabilityResolver | None = None,
    renderer_coverage: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    coverage = renderer_coverage or {}
    return [
        compile_experience(
            experience_id,
            platform_profile,
            context=context,
            resolver=resolver,
            renderer_pages=coverage.get(experience_id, []),
        )
        for experience_id in BUILTIN_EXPERIENCE_DNA
    ]
