from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class UpdateAutomationEngine:
    """Policy-driven verified staging with durable de-duplication/backoff.

    This engine may invoke only the audited Action Broker update.stage action.
    It never applies an update or invokes a component installer directly.
    """

    def __init__(
        self,
        state,
        action_broker,
        *,
        path: str | Path = "/var/lib/beastagotchi/updates/automation.json",
        clock=time.time,
        retry_sec: float = 3600.0,
    ) -> None:
        self.state = state
        self.action_broker = action_broker
        self.path = Path(path)
        self.clock = clock
        self.retry_sec = max(300.0, float(retry_sec))

    def _load(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.path.read_text())
            if isinstance(obj, dict) and isinstance(obj.get("components"), dict):
                return obj
        except Exception:
            pass
        return {"schema": 1, "components": {}}

    def _save(self, obj: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)

    def tick(self) -> dict[str, Any]:
        now = float(self.clock())
        ledger = self._load()
        records = ledger["components"]
        components = [
            x for x in (self.state.get("updates.components", []) or [])
            if isinstance(x, dict)
        ]
        trigger_ready = bool(self.state.get("updates.auto_trigger_ready", False))
        candidates = []
        blocked = []
        pending_install = 0

        for row in components:
            cid = str(row.get("id") or "").strip()
            policy = str(row.get("policy") or "notify")
            if (
                not cid
                or policy not in {"auto_stage", "auto_install"}
                or row.get("update_available") is not True
            ):
                continue

            version = str(row.get("available_version") or "").strip()
            if policy == "auto_install":
                pending_install += 1

            if not row.get("auto_stage_eligible"):
                blocked.append({
                    "id": cid,
                    "version": version,
                    "policy": policy,
                    "reason": "update is not eligible for verified automatic staging",
                })
                continue

            previous = records.get(cid) if isinstance(records.get(cid), dict) else {}
            if str(previous.get("version") or "") == version:
                if previous.get("status") == "staged":
                    continue
                if (
                    previous.get("status") == "failed"
                    and now - float(previous.get("attempted_at") or 0) < self.retry_sec
                ):
                    continue
            candidates.append((row, version))

        result: dict[str, Any] | None = None
        if trigger_ready and candidates:
            # One remote artifact per pass keeps bandwidth, heat and SD writes
            # predictable even if several components become eligible together.
            row, version = candidates[0]
            cid = str(row.get("id"))
            action = self.action_broker.perform(
                "update.stage",
                {"component": cid},
                actor="automation:update",
            )
            ok = action.get("status") == "success"
            action_result = action.get("result") if isinstance(action.get("result"), dict) else {}
            result = {
                "id": cid,
                "version": version,
                "policy": str(row.get("policy")),
                "attempted_at": now,
                "status": "staged" if ok else "failed",
                "action_id": action.get("id"),
                "path": action_result.get("path") if ok else None,
                "sha256": action_result.get("sha256") if ok else None,
                "error": None if ok else action_result.get("error"),
                "install_pending": bool(ok and row.get("policy") == "auto_install"),
            }
            records[cid] = result
            ledger["updated_at"] = now
            self._save(ledger)

        if not trigger_ready:
            status = "waiting_for_dock_and_internet"
        elif result:
            status = result["status"]
        elif candidates:
            status = "ready"
        elif blocked:
            status = "blocked"
        else:
            status = "idle"

        recent = sorted(
            [x for x in records.values() if isinstance(x, dict)],
            key=lambda x: float(x.get("attempted_at") or 0),
            reverse=True,
        )[:20]

        return {
            "update_automation.enabled": True,
            "update_automation.status": status,
            "update_automation.auto_trigger_ready": trigger_ready,
            "update_automation.candidate_count": len(candidates),
            "update_automation.blocked_count": len(blocked),
            "update_automation.blocked": blocked[:20],
            "update_automation.pending_install_count": pending_install,
            "update_automation.last": result or (recent[0] if recent else None),
            "update_automation.history": recent,
            "update_automation.auto_stage_executor_enabled": True,
            "update_automation.auto_install_executor_enabled": False,
            "update_automation.auto_install_reason": (
                "verified artifacts may be staged automatically, but applying an update "
                "requires a component-specific backup/probation/rollback adapter"
            ),
        }
