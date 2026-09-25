from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class OwnerModeManager:
    """Persistent owner-control state for Beastagotchi.

    Expert Mode is an explicit owner preference, not an OS privilege grant.
    Mutations still travel through their normal brokers.  Successful policy
    overrides mark the installation customized so diagnostics/support records do
    not pretend it is still a fully managed configuration.
    """

    schema = 1

    def __init__(
        self,
        path: str = "/var/lib/beastagotchi/owner-mode.json",
        *,
        clock=time.time,
    ) -> None:
        self.path = Path(path)
        self.clock = clock

    def _default(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "expert_mode_enabled": False,
            "expert_mode_set_at": None,
            "expert_mode_set_by": None,
            "customized": False,
            "customized_at": None,
            "override_count": 0,
            "last_override_at": None,
            "last_override_action": None,
            "last_override_target": None,
            "last_override_actor": None,
            "last_policy_blockers": [],
        }

    def _read(self) -> dict[str, Any]:
        row = self._default()
        try:
            obj = json.loads(self.path.read_text())
            if isinstance(obj, dict):
                for key in row:
                    if key in obj:
                        row[key] = obj[key]
        except Exception:
            pass
        row["schema"] = self.schema
        row["expert_mode_enabled"] = bool(row.get("expert_mode_enabled", False))
        row["customized"] = bool(row.get("customized", False))
        try:
            row["override_count"] = max(0, int(row.get("override_count") or 0))
        except (TypeError, ValueError):
            row["override_count"] = 0
        blockers = row.get("last_policy_blockers")
        row["last_policy_blockers"] = [str(x)[:240] for x in blockers[:16]] if isinstance(blockers, list) else []
        return row

    def _write(self, row: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(row, indent=2, sort_keys=True, default=str) + "\n")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)

    def snapshot(self) -> dict[str, Any]:
        row = self._read()
        if row["customized"]:
            support_state = "customized"
        elif row["expert_mode_enabled"]:
            support_state = "expert"
        else:
            support_state = "managed"
        return {
            **row,
            "support_state": support_state,
            "managed_defaults_active": not row["expert_mode_enabled"],
        }

    def set_expert(self, enabled: bool, *, actor: str = "owner") -> dict[str, Any]:
        row = self._read()
        enabled = bool(enabled)
        if row["expert_mode_enabled"] == enabled:
            return self.snapshot()
        row["expert_mode_enabled"] = enabled
        row["expert_mode_set_at"] = float(self.clock())
        row["expert_mode_set_by"] = str(actor or "owner")[:160]
        self._write(row)
        return self.snapshot()

    def record_override(
        self,
        *,
        action: str,
        target: str = "",
        actor: str = "owner",
        policy_blockers: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        row = self._read()
        now = float(self.clock())
        if not row["customized"]:
            row["customized"] = True
            row["customized_at"] = now
        row["override_count"] = int(row.get("override_count") or 0) + 1
        row["last_override_at"] = now
        row["last_override_action"] = str(action or "")[:128]
        row["last_override_target"] = str(target or "")[:256]
        row["last_override_actor"] = str(actor or "owner")[:160]
        row["last_policy_blockers"] = [str(x)[:240] for x in list(policy_blockers or [])[:16]]
        self._write(row)
        return self.snapshot()

    def state_patch(self) -> dict[str, Any]:
        row = self.snapshot()
        return {
            "owner.expert_mode.enabled": row["expert_mode_enabled"],
            "owner.expert_mode.set_at": row["expert_mode_set_at"],
            "owner.expert_mode.set_by": row["expert_mode_set_by"],
            "owner.customized": row["customized"],
            "owner.customized_at": row["customized_at"],
            "owner.override_count": row["override_count"],
            "owner.last_override.at": row["last_override_at"],
            "owner.last_override.action": row["last_override_action"],
            "owner.last_override.target": row["last_override_target"],
            "owner.support_state": row["support_state"],
            "owner.managed_defaults_active": row["managed_defaults_active"],
        }
