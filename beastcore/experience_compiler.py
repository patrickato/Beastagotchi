from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dependency_resolver import DependencyCapabilityResolver
from .experience_dna import (
    BUILTIN_EXPERIENCE_DNA,
    ExperienceDNA,
    compile_experience_variant,
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


def compile_experience(
    experience_id: str,
    platform_profile: dict[str, Any] | None,
    *,
    context: str | None = None,
    resolver: DependencyCapabilityResolver | None = None,
    renderer_pages: list[str] | tuple[str, ...] | None = None,
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
    variant = compile_experience_variant(dna, platform_profile or {}, context=context)

    implemented = tuple(dict.fromkeys(str(x).strip().lower() for x in (renderer_pages or ()) if str(x).strip()))
    preferred = tuple(policy.preferred_pages)
    missing_preferred = [page for page in preferred if page not in implemented]
    capability = _capability_resolution(eid, policy, resolver)

    optional_missing = [
        row.get("requirement")
        for row in capability.get("optional_results", [])
        if isinstance(row, dict) and not bool(row.get("satisfied"))
    ]

    return {
        "schema": 1,
        "experience_id": eid,
        "label": dna.label,
        "dna": dna.as_dict(),
        "variant": variant,
        "presentation_engine": policy.presentation_engine,
        "fallback_policy": policy.fallback_policy,
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
        "writes_preferences": False,
        "installs_dependencies": False,
        "selects_providers": False,
        "ready_for_preview": "home" in implemented,
        "ready_for_production_navigation": bool(implemented) and not missing_preferred,
    }


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
