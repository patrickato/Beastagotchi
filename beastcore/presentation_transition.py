from __future__ import annotations

from typing import Any

from .presentation import PRESENTATION_OWNERS, normalize_owner


class PresentationTransitionPlanner:
    """Build explicit Native / Theme Manager / Beast handoff plans.

    This planner is descriptive only. It deliberately does not invoke systemctl,
    edit Pwnagotchi config, toggle plugins, or touch the framebuffer.
    """

    def __init__(self, state) -> None:
        self.state = state

    def _theme(self) -> tuple[bool, bool]:
        for row in self.state.get("plugins.catalog", []) or []:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").lower().replace("-", "_")
            if name == "theme_manager":
                return True, bool(row.get("enabled"))
        return False, False

    def _service_active(self, unit: str) -> bool:
        for row in self.state.get("platform.services", []) or []:
            if isinstance(row, dict) and str(row.get("unit") or "") == unit:
                return str(row.get("active") or "").lower() == "active"
        if unit == "beast-ui.service":
            return bool(self.state.get("presentation.beast.service_active", False))
        if unit == "pwnagotchi.service":
            return str(self.state.get("pwnagotchi.service.state") or "").lower() in {"active", "running"}
        return False

    def infer_owner(self) -> str:
        active = self.state.get("presentation.active_owner")
        try:
            if active:
                return normalize_owner(str(active))
        except ValueError:
            pass
        theme_installed, theme_enabled = self._theme()
        if self._service_active("beast-ui.service"):
            return "beast"
        if theme_installed and theme_enabled:
            return "theme_manager"
        return "native"

    @staticmethod
    def _step(step_id: str, label: str, *, mutates: bool = True, rollback: str = "") -> dict[str, Any]:
        return {
            "id": step_id,
            "label": label,
            "mutates": bool(mutates),
            "rollback": rollback,
        }

    def plan(self, target: str) -> dict[str, Any]:
        target = normalize_owner(target)
        current = self.infer_owner()
        theme_installed, theme_enabled = self._theme()
        managed = bool(self.state.get("presentation.theme_manager.managed_handoff_supported", False))
        backup = bool(self.state.get("display.handoff.backup_exists", False))
        pwn_active = self._service_active("pwnagotchi.service")
        beast_active = self._service_active("beast-ui.service")

        blockers: list[str] = []
        warnings: list[str] = []
        steps: list[dict[str, Any]] = []

        if target == "theme_manager" and not theme_installed:
            blockers.append("Korrie71 Theme Manager is not installed")
        if current == "beast" and target != "beast" and not backup:
            blockers.append("Beast owns the display but no active Pwnagotchi display rollback backup is visible")

        if not pwn_active and target in {"native", "theme_manager"}:
            warnings.append("Pwnagotchi is not currently active; transition must restore/start it before ownership can be verified")

        if current == target:
            steps.append(self._step("verify.current", f"Verify {target} remains healthy", mutates=False))
        elif target == "beast":
            if current == "theme_manager" or theme_enabled:
                if managed:
                    steps.append(self._step(
                        "theme_manager.release",
                        "Ask Theme Manager managed mode to release framebuffer/touch while retaining its WebUI",
                        rollback="Ask Theme Manager to reacquire presentation ownership",
                    ))
                else:
                    steps.append(self._step(
                        "plugin.theme_manager.disable",
                        "Disable Theme Manager so its on_unload cleanup releases render/touch hooks",
                        rollback="Re-enable Theme Manager and restart Pwnagotchi",
                    ))
            steps.extend([
                self._step(
                    "display.beast.claim",
                    "Use the validated Beast display-handoff path to snapshot Pwnagotchi display config, disable its display renderer, and start Beast UI",
                    rollback="Restore the saved Pwnagotchi display config and stop Beast UI",
                ),
                self._step("verify.beast", "Verify Pwnagotchi + Beast Core + Beast UI health and zero display-owner conflicts", mutates=False),
            ])
        elif target == "native":
            if current == "beast" or beast_active:
                steps.append(self._step(
                    "display.beast.release",
                    "Stop Beast UI and restore the saved Pwnagotchi display configuration",
                    rollback="Reclaim Beast display ownership from the restored config",
                ))
            if theme_enabled:
                steps.append(self._step(
                    "plugin.theme_manager.disable",
                    "Disable Theme Manager and let its on_unload path restore original Pwnagotchi rendering hooks",
                    rollback="Re-enable Theme Manager",
                ))
            steps.append(self._step("verify.native", "Verify native Pwnagotchi display ownership and touch/display health", mutates=False))
        else:
            # Theme Manager compatibility mode. Today the plugin's clean
            # on_unload makes enable/disable a viable ownership boundary.
            if current == "beast" or beast_active:
                steps.append(self._step(
                    "display.beast.release",
                    "Stop Beast UI and restore the saved Pwnagotchi display configuration",
                    rollback="Reclaim Beast display ownership",
                ))
            if managed:
                steps.append(self._step(
                    "theme_manager.acquire",
                    "Ask Theme Manager managed mode to acquire framebuffer/touch while keeping its WebUI active",
                    rollback="Return Theme Manager to web-only/standby presentation mode",
                ))
            else:
                steps.append(self._step(
                    "plugin.theme_manager.enable",
                    "Enable Theme Manager and restart/observe Pwnagotchi; plugin startup attaches its render and touch hooks",
                    rollback="Disable Theme Manager and restart/observe Pwnagotchi",
                ))
                warnings.append(
                    "Compatibility mode toggles the whole Theme Manager plugin. Its WebUI is therefore unavailable while the plugin is disabled."
                )
            steps.append(self._step("verify.theme_manager", "Verify Theme Manager owns Pwnagotchi rendering, Beast UI is inactive, and Pwnagotchi remains healthy", mutates=False))

        strategy = "managed" if managed else "compatibility_toggle"
        return {
            "allowed": not blockers,
            "operation": "presentation.switch",
            "current_owner": current,
            "target_owner": target,
            "noop": current == target,
            "strategy": strategy,
            "theme_manager_installed": theme_installed,
            "theme_manager_enabled": theme_enabled,
            "theme_manager_managed_handoff": managed,
            "display_rollback_backup": backup,
            "steps": steps,
            "blockers": blockers,
            "warnings": warnings,
            "executor_enabled": False,
            "executor_reason": (
                "transition plans are available now; physical execution remains locked "
                "until the compatibility sequence passes an off-screen gate and bounded TFT handoff test"
            ),
        }

    def all_plans(self) -> list[dict[str, Any]]:
        return [self.plan(owner) for owner in PRESENTATION_OWNERS]
