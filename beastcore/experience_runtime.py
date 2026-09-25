from __future__ import annotations

from typing import Any

from .experience_compiler import compile_builtin_catalog, compile_pack_experience
from .experience_surfaces import experience_native_target_coverage, experience_surface_coverage


class ExperiencePlanPublisher:
    """Publish read-only Experience Compiler plans from Beast Core.

    This is deliberately a planning surface. It shares the live
    DependencyCapabilityResolver and PlatformProfile owned by Beast Core, but it
    cannot select providers, install dependencies, write preferences, or claim
    TFT ownership.
    """

    schema = 1

    def __init__(self, state, *, resolver, platform_profile) -> None:
        self.state = state
        self.resolver = resolver
        self.platform_profile = platform_profile

    def _context(self) -> str:
        value = str(self.state.get("context.mode.effective") or "").strip().lower()
        return value or "default"

    def _pack_plans(
        self,
        profile: dict[str, Any],
        context: str,
        coverage: dict[str, list[str]],
        target_coverage: dict[str, list[str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        rows: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        for mission in self.state.get("missions.items", []) or []:
            if not isinstance(mission, dict):
                continue
            if not mission.get("source_pack") or not mission.get("experience"):
                continue
            if not mission.get("experience_dna_valid"):
                if mission.get("experience_dna_error"):
                    errors.append({
                        "experience_id": str(mission.get("id") or ""),
                        "source_pack": str(mission.get("source_pack") or ""),
                        "error": str(mission.get("experience_dna_error") or "")[:320],
                    })
                continue
            dna = mission.get("experience_dna")
            if not isinstance(dna, dict):
                continue
            policy = mission.get("experience_policy") if isinstance(mission.get("experience_policy"), dict) else {}
            renderer_ref = str(mission.get("experience_renderer") or "").strip().lower()
            try:
                row = compile_pack_experience(
                    str(mission.get("id") or ""),
                    dna,
                    profile,
                    label=str(mission.get("label") or mission.get("id") or "Pack Experience"),
                    requires=list(policy.get("requires") or []),
                    optional_requirements=list(policy.get("optional_requirements") or []),
                    preferred_pages=list(policy.get("preferred_pages") or ["home"]),
                    presentation_engine=str(policy.get("presentation_engine") or "beast_scene"),
                    fallback_policy=str(policy.get("fallback_policy") or "identity_preserving"),
                    context=context,
                    resolver=self.resolver,
                    renderer_pages=coverage.get(renderer_ref, []),
                    renderer_native_targets=target_coverage.get(renderer_ref, ["reference"]),
                    source_pack=str(mission.get("source_pack") or ""),
                    source_file=str(mission.get("source_file") or ""),
                )
                row["renderer_experience_id"] = renderer_ref or None
                row["mission_requirements_met"] = bool(mission.get("requirements_met"))
                row["component_refs"] = {
                    key: mission.get(key) or None
                    for key in ("theme", "face_profile", "animation_profile", "board", "layout", "deck")
                }
                if not row["mission_requirements_met"]:
                    row["ready_for_preview"] = False
                    row["ready_for_production_navigation"] = False
                rows.append(row)
            except Exception as exc:
                errors.append({
                    "experience_id": str(mission.get("id") or ""),
                    "source_pack": str(mission.get("source_pack") or ""),
                    "error": f"{type(exc).__name__}: {exc}"[:320],
                })
        return rows, errors

    def snapshot(self) -> dict[str, Any]:
        profile = dict(self.platform_profile.snapshot() or {})
        context = self._context()
        coverage = experience_surface_coverage()
        target_coverage = experience_native_target_coverage()
        rows = compile_builtin_catalog(
            profile,
            context=context,
            resolver=self.resolver,
            renderer_coverage=coverage,
            native_target_coverage=target_coverage,
        )
        pack_rows, pack_errors = self._pack_plans(profile, context, coverage, target_coverage)
        rows.extend(pack_rows)
        preview_ready = sum(1 for row in rows if row.get("ready_for_preview") is True)
        production_ready = sum(
            1 for row in rows if row.get("ready_for_production_navigation") is True
        )
        return {
            "schema": self.schema,
            "mode": "read_only",
            "context": context,
            "platform": {
                "compute_tier": profile.get("compute_tier"),
                "display_class": profile.get("display_class"),
            },
            "count": len(rows),
            "builtin_count": sum(1 for row in rows if (row.get("source") or {}).get("kind") == "builtin"),
            "pack_count": len(pack_rows),
            "pack_errors": pack_errors,
            "preview_ready_count": preview_ready,
            "production_navigation_ready_count": production_ready,
            "renderer_coverage": coverage,
            "native_target_coverage": target_coverage,
            "items": rows,
            "writes_preferences": False,
            "installs_dependencies": False,
            "selects_providers": False,
            "tft_activation_enabled": False,
        }

    def state_patch(self) -> dict[str, Any]:
        row = self.snapshot()
        return {
            "experience.compiler.plan": row,
            "experience.compiler.mode": row["mode"],
            "experience.compiler.count": row["count"],
            "experience.compiler.preview_ready_count": row["preview_ready_count"],
            "experience.compiler.production_navigation_ready_count": row[
                "production_navigation_ready_count"
            ],
            "experience.compiler.tft_activation_enabled": False,
        }
