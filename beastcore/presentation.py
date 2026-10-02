from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable


PRESENTATION_OWNERS = ("native", "theme_manager", "beast")
OWNER_ALIASES = {
    "pwn-native": "native",
    "pwnagotchi": "native",
    "stock": "native",
    "korrie-theme-manager": "theme_manager",
    "theme-manager": "theme_manager",
    "theme_manager": "theme_manager",
    "beast-ui": "beast",
    "beastagotchi": "beast",
    "beast": "beast",
}


def normalize_owner(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace(" ", "_")
    raw = OWNER_ALIASES.get(raw, raw)
    if raw not in PRESENTATION_OWNERS:
        raise ValueError(f"unknown presentation owner: {value!r}")
    return raw


class PresentationBroker:
    """Persistent presentation-ownership truth for v0.19.

    This is deliberately a *state and policy* foundation, not yet the physical
    handoff executor. v0.18's proven display-handoff scripts remain authoritative
    until owner-specific release/acquire adapters are implemented and physically
    validated. Keeping those stages separate prevents a development broker from
    silently stealing or stranding the TFT.
    """

    def __init__(
        self,
        state,
        *,
        path: str = "/var/lib/beastagotchi/presentation.json",
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.state = state
        self.path = Path(path)
        self.clock = clock

    def _default(self) -> dict[str, Any]:
        # "native" is a fail-safe desired preference for a fresh state file.
        # It does NOT execute a transition or change current display ownership.
        return {
            "schema": 1,
            "desired_owner": "native",
            "active_owner": None,
            "status": "uninitialized",
            "generation": 0,
            "updated_at": self.clock(),
            "requested_by": "bootstrap",
            "last_error": None,
        }

    def load(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.path.read_text())
            if not isinstance(obj, dict):
                raise ValueError("presentation state must be an object")
            obj = {**self._default(), **obj}
            obj["desired_owner"] = normalize_owner(obj.get("desired_owner"))
            active = obj.get("active_owner")
            obj["active_owner"] = normalize_owner(active) if active else None
            obj["generation"] = max(0, int(obj.get("generation") or 0))
            return obj
        except FileNotFoundError:
            return self._default()
        except Exception as exc:
            row = self._default()
            row["status"] = "state_error"
            row["last_error"] = f"{type(exc).__name__}: {exc}"
            return row

    def _write(self, obj: dict[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)
        return obj

    def request(self, owner: str, *, requested_by: str = "user") -> dict[str, Any]:
        target = normalize_owner(owner)
        row = self.load()
        row.update({
            "desired_owner": target,
            "status": "requested" if row.get("active_owner") != target else "stable",
            "generation": int(row.get("generation") or 0) + 1,
            "updated_at": self.clock(),
            "requested_by": str(requested_by or "user")[:64],
            "last_error": None,
        })
        return self._write(row)

    def mark_active(self, owner: str) -> dict[str, Any]:
        target = normalize_owner(owner)
        row = self.load()
        row.update({
            "desired_owner": target,
            "active_owner": target,
            "status": "stable",
            "updated_at": self.clock(),
            "last_error": None,
        })
        return self._write(row)

    def mark_released(self, owner: str) -> dict[str, Any]:
        target = normalize_owner(owner)
        row = self.load()
        if row.get("active_owner") == target:
            row["active_owner"] = None
            row["status"] = "released"
            row["updated_at"] = self.clock()
        return self._write(row)

    def mark_error(self, message: str) -> dict[str, Any]:
        row = self.load()
        row["status"] = "error"
        row["last_error"] = str(message or "presentation transition failed")[:512]
        row["updated_at"] = self.clock()
        return self._write(row)

    def _service_active(self, unit: str) -> bool:
        for item in self.state.get("platform.services", []) or []:
            if isinstance(item, dict) and item.get("unit") == unit:
                return str(item.get("active") or "").lower() == "active"
        return False

    def _theme_manager(self) -> dict[str, Any] | None:
        for row in self.state.get("plugins.catalog", []) or []:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").lower().replace("-", "_")
            if name == "theme_manager":
                return row
        return None

    def tick(self) -> dict[str, Any]:
        row = self.load()
        theme = self._theme_manager()
        theme_installed = bool(theme)
        theme_enabled = bool(theme and theme.get("enabled"))
        theme_interop = theme.get("interop") if isinstance(theme, dict) and isinstance(theme.get("interop"), dict) else {}
        theme_version = theme_interop.get("version") or self.state.get("plugins.theme_manager.version")
        theme_capabilities = list(theme_interop.get("capabilities") or self.state.get("plugins.theme_manager.capabilities", []) or [])
        theme_managed = bool(theme_interop.get("managed_handoff_supported") or self.state.get("plugins.theme_manager.managed_handoff_supported", False))
        theme_compat = bool(theme_interop.get("compatibility_handoff_evidence") or self.state.get("plugins.theme_manager.compatibility_handoff_evidence", False))
        beast_active = self._service_active("beast-ui.service")
        pwn_active = str(self.state.get("pwnagotchi.service.state") or "").lower() == "active"

        active = row.get("active_owner")
        conflicts: list[str] = []
        # Until Theme Manager exposes a managed/web-only ownership contract,
        # enabling it while Beast UI is physically active remains a real risk.
        if beast_active and theme_enabled and active in {None, "beast"}:
            conflicts.append("theme_manager_and_beast_ui_may_compete_for_display")

        available = ["native", "beast"]
        if theme_installed:
            available.insert(1, "theme_manager")

        return {
            "presentation.schema": 1,
            "presentation.desired_owner": row.get("desired_owner"),
            "presentation.active_owner": active,
            "presentation.status": row.get("status"),
            "presentation.generation": row.get("generation"),
            "presentation.updated_at": row.get("updated_at"),
            "presentation.requested_by": row.get("requested_by"),
            "presentation.last_error": row.get("last_error"),
            "presentation.owners": list(PRESENTATION_OWNERS),
            "presentation.available_owners": available,
            "presentation.native.available": pwn_active,
            "presentation.beast.available": True,
            "presentation.beast.service_active": beast_active,
            "presentation.theme_manager.installed": theme_installed,
            "presentation.theme_manager.enabled": theme_enabled,
            "presentation.theme_manager.version": theme_version,
            "presentation.theme_manager.capabilities": theme_capabilities,
            "presentation.theme_manager.managed_handoff_supported": theme_managed,
            "presentation.theme_manager.compatibility_handoff_evidence": theme_compat,
            "presentation.conflicts": conflicts,
            "presentation.conflict_count": len(conflicts),
            "presentation.executor_enabled": False,
            "presentation.executor_reason": (
                "v0.19 groundwork: physical handoff remains on validated v0.18 "
                "scripts until owner adapters pass off-screen and physical validation"
            ),
        }
