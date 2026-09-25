from __future__ import annotations

from typing import Any

from .experience_compiler import compile_builtin_catalog
from .experience_surfaces import experience_surface_coverage


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

    def snapshot(self) -> dict[str, Any]:
        profile = dict(self.platform_profile.snapshot() or {})
        context = self._context()
        coverage = experience_surface_coverage()
        rows = compile_builtin_catalog(
            profile,
            context=context,
            resolver=self.resolver,
            renderer_coverage=coverage,
        )
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
            "preview_ready_count": preview_ready,
            "production_navigation_ready_count": production_ready,
            "renderer_coverage": coverage,
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
