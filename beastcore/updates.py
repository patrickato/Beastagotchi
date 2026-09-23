from __future__ import annotations

import json
from pathlib import Path
from typing import Any


POLICIES = ("manual", "notify", "auto_stage", "auto_install")


class UpdatePolicyEngine:
    """Expose update intent without performing network or install actions."""

    def __init__(self, state, path: str = "/var/lib/beastagotchi/ui/update_policies.json") -> None:
        self.state = state
        self.path = Path(path)

    def _policies(self) -> dict[str, str]:
        try:
            obj = json.loads(self.path.read_text())
            raw = obj.get("policies") if isinstance(obj, dict) else {}
            if not isinstance(raw, dict):
                return {}
            return {
                str(k): str(v)
                for k, v in raw.items()
                if str(v) in POLICIES and str(k).strip()
            }
        except Exception:
            return {}

    def _theme_manager(self) -> dict[str, Any] | None:
        for row in self.state.get("plugins.catalog", []) or []:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").lower().replace("-", "_")
            if name == "theme_manager":
                return row
        return None

    def tick(self) -> dict[str, Any]:
        policies = self._policies()
        components: list[dict[str, Any]] = []

        def add(cid: str, label: str, version: Any, kind: str, *, source_type: str, source: str = "",
                default_policy: str = "notify", compatible: bool = True, blockers: list[str] | None = None) -> None:
            selected = policies.get(cid, default_policy)
            components.append({
                "id": cid,
                "label": label,
                "kind": kind,
                "installed_version": str(version or "unknown"),
                "available_version": None,
                "update_available": None,
                "policy": selected if selected in POLICIES else default_policy,
                "source_type": source_type,
                "source": source,
                "compatibility": "compatible" if compatible else "blocked",
                "blockers": list(blockers or []),
                "last_checked_at": None,
                "last_result": "not_checked",
                # The user may express auto-install intent now, but execution is
                # intentionally impossible until source verification + rollback
                # are implemented.
                "auto_install_eligible": False,
            })

        add(
            "beastagotchi", "Beastagotchi", self.state.get("system.beast_version"),
            "core", source_type="github_release", source="patrickato/Beastagotchi",
        )
        add(
            "pwnagotchi", "Pwnagotchi", self.state.get("pwnagotchi.version"),
            "platform", source_type="project_release", source="jayofelony/pwnagotchi",
        )

        theme = self._theme_manager()
        if theme:
            add(
                "theme_manager", "Korrie71 Theme Manager", theme.get("version"),
                "integration", source_type="github_release",
                source="Korrie71/pwnagotchi-theme-manager",
            )

        for pack in self.state.get("packs.items", []) or []:
            if not isinstance(pack, dict) or pack.get("origin") == "staged":
                continue
            pid = str(pack.get("id") or "").strip()
            if not pid:
                continue
            source = pack.get("source") if isinstance(pack.get("source"), dict) else {}
            blockers = list(pack.get("blockers") or [])
            add(
                f"pack:{pid}", str(pack.get("label") or pid), pack.get("version"),
                "pack", source_type=str(source.get("type") or "local"),
                source=str(source.get("url") or ""),
                compatible=bool(pack.get("requirements_met", True)),
                blockers=blockers,
            )

        docked = bool(self.state.get("dock.docked", False))
        internet = str(self.state.get("network.internet.state") or "unknown").lower()
        counts = {p: sum(1 for c in components if c.get("policy") == p) for p in POLICIES}
        return {
            "updates.components": components,
            "updates.component_count": len(components),
            "updates.policy_counts": counts,
            "updates.allowed_policies": list(POLICIES),
            "updates.policy_path": str(self.path),
            "updates.dock_ready": docked,
            "updates.internet_state": internet,
            "updates.auto_trigger_ready": bool(docked and internet in {"online", "reachable", "up"}),
            "updates.check_state": "metadata_fetch_not_enabled",
            "updates.executor_enabled": False,
            "updates.executor_reason": (
                "v0.19 policy/catalog foundation only; no background downloads or installs "
                "until source verification, staging, backup, probation and rollback are implemented"
            ),
        }
