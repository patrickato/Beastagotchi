from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from .pack_intake import PackIntakeManager
from .pack_install import PackInstallManager
from .update_downloads import VerifiedUpdateStager


class UpdateOrchestrationError(RuntimeError):
    pass


class UpdateProbationEvaluator:
    """Read-only post-update health gate shared by component adapters."""

    def __init__(self, state) -> None:
        self.state = state

    def snapshot(self) -> dict[str, Any]:
        health = str(self.state.get("health.core.state") or "unknown").lower()
        pwn = str(self.state.get("pwnagotchi.service.state") or "unknown").lower()
        better = str(self.state.get("bettercap.state") or "unknown").lower()
        readonly = bool(self.state.get("storage.root.readonly", False))
        conflicts = list(self.state.get("presentation.conflicts", []) or [])
        blockers = []
        if health == "critical":
            blockers.append("core health is critical")
        if pwn not in {"active", "running", "unknown"}:
            blockers.append(f"pwnagotchi state is {pwn}")
        if better not in {"active", "running", "ready", "unknown"}:
            blockers.append(f"bettercap state is {better}")
        if readonly:
            blockers.append("root filesystem is read-only")
        if conflicts:
            blockers.append("presentation ownership conflict is active")
        return {
            "ok": not blockers,
            "health_core": health,
            "pwnagotchi": pwn,
            "bettercap": better,
            "root_readonly": readonly,
            "presentation_conflicts": conflicts,
            "blockers": blockers,
        }


class PackUpdateOrchestrator:
    """Verified end-to-end update path for inert Beast Packs only."""

    def __init__(
        self,
        state,
        *,
        stager: VerifiedUpdateStager | None = None,
        intake: PackIntakeManager | None = None,
        installer: PackInstallManager | None = None,
        inbox_root: str | Path = "/var/lib/beastagotchi/packs/inbox",
        history_root: str | Path = "/var/lib/beastagotchi/updates/history",
        clock=time.time,
    ) -> None:
        self.state = state
        self.stager = stager or VerifiedUpdateStager(state)
        self.intake = intake or PackIntakeManager()
        self.installer = installer or PackInstallManager(state)
        self.inbox_root = Path(inbox_root)
        self.history_root = Path(history_root)
        self.clock = clock
        self.probation = UpdateProbationEvaluator(state)

    def _component(self, component_id: str) -> dict[str, Any]:
        for row in self.state.get("updates.components", []) or []:
            if isinstance(row, dict) and str(row.get("id") or "") == str(component_id):
                return row
        raise UpdateOrchestrationError("update component not present in canonical state")

    def plan(self, component_id: str) -> dict[str, Any]:
        component = self._component(component_id)
        blockers = []
        cid = str(component.get("id") or "")
        if not cid.startswith("pack:"):
            blockers.append("end-to-end automatic application is currently limited to Beast Packs")
        pack_id = cid.split(":", 1)[1] if cid.startswith("pack:") else ""
        if component.get("update_available") is not True:
            blockers.append("component does not report an available update")
        if not component.get("source_trusted"):
            blockers.append("update source is not trusted")
        if component.get("compatibility") == "blocked":
            blockers.extend(component.get("blockers") or ["component compatibility is blocked"])
        stage_plan = None
        if not blockers:
            stage_plan = self.stager.plan(cid)
            if not stage_plan.get("allowed"):
                blockers.extend(stage_plan.get("blockers") or ["verified download staging is blocked"])
        return {
            "allowed": not blockers,
            "operation": "update.pack_apply",
            "component": cid,
            "pack_id": pack_id,
            "policy": component.get("policy"),
            "installed_version": component.get("installed_version"),
            "available_version": component.get("available_version"),
            "verified_stage_plan": stage_plan,
            "activation_included": False,
            "service_restart_included": False,
            "automatic_rollback_available": True,
            "blockers": blockers,
            "warnings": [
                "This transaction updates only the inert Beast Pack registry.",
                "The updated pack remains disabled/inactive until a separate activation transaction exists.",
            ],
        }

    def _history_write(self, key: str, row: dict[str, Any]) -> Path:
        self.history_root.mkdir(parents=True, exist_ok=True)
        fp = self.history_root / f"{key}.json"
        tmp = fp.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, indent=2, sort_keys=True, default=str) + "\n")
        tmp.replace(fp)
        return fp

    def apply(self, component_id: str) -> dict[str, Any]:
        plan = self.plan(component_id)
        if not plan["allowed"]:
            raise UpdateOrchestrationError("; ".join(plan["blockers"]))
        started = float(self.clock())
        staged_update = self.stager.stage(component_id)
        artifact = Path(str(staged_update.get("artifact") or ""))
        if not artifact.is_file():
            raise UpdateOrchestrationError("verified update artifact is missing after staging")

        self.inbox_root.mkdir(parents=True, exist_ok=True)
        inbox_name = artifact.name
        inbox_file = self.inbox_root / inbox_name
        shutil.copy2(artifact, inbox_file)

        try:
            inspection = self.intake.inspect(inbox_name)
            manifest = inspection.get("manifest") or {}
            if str(manifest.get("id") or "") != plan["pack_id"]:
                raise UpdateOrchestrationError("release Beast Pack id does not match update component id")
            self.intake.stage(inbox_name, replace=True)
            install = self.installer.install(plan["pack_id"])
            probation = self.probation.snapshot()
            if not probation["ok"]:
                tx = str(install.get("transaction_id") or "")
                rollback = self.installer.rollback(tx) if tx else {"ok": False}
                raise UpdateOrchestrationError(
                    "post-update probation failed and rollback was attempted: "
                    + "; ".join(probation["blockers"])
                    + f"; rollback_ok={bool(rollback.get('ok'))}"
                )
            result = {
                "ok": True,
                "component": component_id,
                "pack_id": plan["pack_id"],
                "from_version": plan.get("installed_version"),
                "to_version": manifest.get("version"),
                "verified_download": staged_update,
                "pack_inspection": inspection,
                "install": install,
                "probation": probation,
                "enabled": False,
                "activation_performed": False,
                "service_restart_performed": False,
                "completed_at": float(self.clock()),
            }
            self._history_write(str(install.get("transaction_id") or f"pack-update-{int(started)}"), result)
            return result
        finally:
            try:
                inbox_file.unlink()
            except OSError:
                pass

    def auto_candidates(self) -> list[dict[str, Any]]:
        """Describe automatic work allowed by current policy; perform nothing."""
        ready = bool(self.state.get("updates.auto_trigger_ready", False))
        rows = []
        for component in self.state.get("updates.components", []) or []:
            if not isinstance(component, dict):
                continue
            policy = str(component.get("policy") or "manual")
            cid = str(component.get("id") or "")
            action = "none"
            reason = ""
            if not ready:
                reason = "waiting for dock/internet trigger"
            elif component.get("update_available") is not True:
                reason = "no update available"
            elif policy == "auto_stage" and component.get("auto_stage_eligible"):
                action = "stage"
            elif policy == "auto_install" and cid.startswith("pack:") and component.get("auto_stage_eligible"):
                action = "apply_inert_pack_update"
            elif policy == "auto_install":
                action = "stage"
                reason = "component-specific install adapter not yet enabled"
            else:
                reason = f"policy is {policy}"
            rows.append({"component": cid, "policy": policy, "action": action, "reason": reason})
        return rows
