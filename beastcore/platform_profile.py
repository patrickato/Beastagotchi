from __future__ import annotations

import os
from typing import Any, Callable


class PlatformProfile:
    """Derive portable Beast resource/display guidance from canonical state.

    This is intentionally capability-first. Board-name hints may refine defaults,
    but they never become hard allow/deny lists. The Resource Governor and
    measured runtime performance remain authoritative after boot.
    """

    schema = 1

    def __init__(self, state, *, cpu_count_fn: Callable[[], int | None] = os.cpu_count) -> None:
        self.state = state
        self.cpu_count_fn = cpu_count_fn

    @staticmethod
    def _display_class(width: int | None, height: int | None) -> str:
        if not width or not height:
            return "unknown"
        pixels = int(width) * int(height)
        if pixels <= 320 * 240:
            return "micro"
        if pixels <= 480 * 320:
            return "reference"
        if pixels <= 800 * 480:
            return "medium"
        if pixels <= 1280 * 800:
            return "large"
        return "desktop"

    def _primary_display(self) -> dict[str, Any]:
        rows = self.state.get("display.framebuffers", []) or []
        if isinstance(rows, list):
            valid = [x for x in rows if isinstance(x, dict) and x.get("width") and x.get("height")]
            if valid:
                # Prefer the reference-ish/local framebuffer over blindly choosing
                # the highest resolution external display.
                row = min(valid, key=lambda x: abs(int(x["width"]) * int(x["height"]) - 480 * 320))
                return {
                    "id": row.get("id"),
                    "device": row.get("device"),
                    "width": int(row.get("width") or 0),
                    "height": int(row.get("height") or 0),
                    "bpp": row.get("bpp"),
                }
        return {"id": None, "device": None, "width": None, "height": None, "bpp": None}

    def snapshot(self) -> dict[str, Any]:
        model = str(self.state.get("system.model") or "").strip()
        arch = str(self.state.get("system.architecture") or "").strip()
        try:
            ram_mb = int(float(self.state.get("system.ram_mb") or 0))
        except Exception:
            ram_mb = 0
        try:
            cores = int(self.cpu_count_fn() or 0)
        except Exception:
            cores = 0

        lower = model.lower()
        if "zero 2" in lower or (ram_mb and ram_mb <= 768):
            tier = "constrained"
        elif ram_mb and ram_mb <= 2048:
            tier = "compact"
        elif "raspberry pi 5" in lower or ram_mb >= 8192:
            tier = "enhanced"
        else:
            tier = "full"

        # Defaults are conservative starting points only. Runtime measurements may
        # raise/lower them and the owner can choose richer/lighter Experiences.
        budgets = {
            "constrained": {
                "ui_fps_hint": 5, "ambient_motion": "minimal", "scene_complexity": "light",
                "background_services": "economy", "local_ai": "off_by_default",
                "history_density": "reduced",
            },
            "compact": {
                "ui_fps_hint": 8, "ambient_motion": "moderate", "scene_complexity": "medium",
                "background_services": "balanced", "local_ai": "off_by_default",
                "history_density": "normal",
            },
            "full": {
                "ui_fps_hint": 12, "ambient_motion": "full", "scene_complexity": "full",
                "background_services": "full", "local_ai": "optional",
                "history_density": "normal",
            },
            "enhanced": {
                "ui_fps_hint": 15, "ambient_motion": "full", "scene_complexity": "expanded",
                "background_services": "expanded", "local_ai": "optional",
                "history_density": "expanded",
            },
        }[tier]

        display = self._primary_display()
        dclass = self._display_class(display.get("width"), display.get("height"))
        connected = int(self.state.get("display.connected_outputs", 0) or 0)
        return {
            "schema": self.schema,
            "compute_tier": tier,
            "model": model or None,
            "architecture": arch or None,
            "ram_mb": ram_mb or None,
            "cpu_cores": cores or None,
            "display_class": dclass,
            "primary_display": display,
            "external_display_count": connected,
            "multiple_displays": bool(connected),
            "budget_hints": budgets,
            "policy": {
                "capability_first": True,
                "board_name_is_hint_only": True,
                "runtime_measurement_can_override": True,
                "owner_can_choose_lighter_or_richer_experience": True,
                "unsupported_feature_hard_blocks": "technical_requirements_only",
            },
        }

    def state_patch(self) -> dict[str, Any]:
        row = self.snapshot()
        return {
            "platform.profile": row,
            "platform.compute_tier": row["compute_tier"],
            "platform.display_class": row["display_class"],
            "platform.budget_hints": row["budget_hints"],
        }
