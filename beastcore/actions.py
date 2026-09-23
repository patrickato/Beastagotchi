from __future__ import annotations

import time
import uuid
from typing import Any

from .plugin_broker import PluginBroker, PluginBrokerError
from .service_broker import ServiceBroker, ServiceBrokerError
from .backup import BackupManager, BackupError
from .container_broker import ContainerBroker, ContainerBrokerError
from .support_bundle import SupportBundleManager
from .operator_sessions import OperatorSessionManager
from .pack_intake import PackIntakeManager, PackIntakeError
from .pack_install import PackInstallManager, PackInstallError
from .update_downloads import VerifiedUpdateStager, UpdateStageError
from .presentation_transition import PresentationTransitionPlanner
from .update_orchestrator import PackUpdateOrchestrator, UpdateOrchestrationError


class ActionBroker:
    """Small allow-listed privileged action dispatcher.

    This is deliberately narrower than a shell/command API. Each action gets a
    typed handler, a plan, a durable audit row, and explicit success/failure.
    Network/API exposure is a separate security decision.
    """

    def __init__(self, state, store, events, *, plugin_broker: PluginBroker | None = None, service_broker: ServiceBroker | None = None, container_broker: ContainerBroker | None = None) -> None:
        self.state = state
        self.store = store
        self.events = events
        self.plugin_broker = plugin_broker or PluginBroker()
        self.service_broker = service_broker or ServiceBroker()
        self.container_broker = container_broker or ContainerBroker()
        self.backup_manager = BackupManager(str(store.path))
        self.support_manager = SupportBundleManager(state,store)
        self.operator_sessions = OperatorSessionManager()
        self.pack_intake = PackIntakeManager()
        self.pack_installer = PackInstallManager(state)
        self.update_stager = VerifiedUpdateStager(state)
        self.presentation_planner = PresentationTransitionPlanner(state)
        self.update_orchestrator = PackUpdateOrchestrator(state, stager=self.update_stager, intake=self.pack_intake, installer=self.pack_installer)

    def plan(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "plugin.toggle":
            return self.plugin_broker.plan_toggle(str(payload.get("name") or ""), bool(payload.get("enabled")))
        if action == "service.restart":
            return self.service_broker.plan_restart(str(payload.get("unit") or ""))
        if action == "backup.create":
            return self.backup_manager.plan()
        if action == "container.control":
            return self.container_broker.plan(str(payload.get("target") or ""),str(payload.get("operation") or ""))
        if action == "support.bundle":
            return self.support_manager.plan()
        if action == "operator.authorize":
            level=str(payload.get("level") or "").lower();duration=int(payload.get("duration_sec") or 900)
            allowed=level in {"operator","maintainer","administrator"}
            return {"allowed":allowed,"operation":"operator.authorize","level":level,"duration_sec":duration,"warnings":["Administrator sessions are time-limited and still use structured Beast actions."] if level=="administrator" else [],"blockers":[] if allowed else ["invalid privilege level"]}
        if action == "operator.revoke":
            return {"allowed":True,"operation":"operator.revoke","current":self.operator_sessions.current()}
        if action == "backup.stage":
            name=str(payload.get("name") or "");inspect=self.backup_manager.inspect(name)
            return {"allowed":bool(inspect.get("ready_to_stage")),"operation":"backup.stage","name":name,"inspection":inspect,"blockers":list(inspect.get("blockers") or [])}
        if action == "pack.inspect":
            check=self.pack_intake.inspect(str(payload.get("name") or ""))
            return {"allowed":True,"operation":"pack.inspect","inspection":check,"blockers":[]}
        if action == "pack.stage":
            return self.pack_intake.plan_stage(str(payload.get("name") or ""),replace=bool(payload.get("replace",False)))
        if action == "pack.install":
            return self.pack_installer.plan_install(str(payload.get("id") or ""))
        if action == "pack.rollback":
            return self.pack_installer.plan_rollback(str(payload.get("transaction_id") or ""))
        if action == "pack.history":
            return {"allowed":True,"operation":"pack.history","items":self.pack_installer.history(int(payload.get("limit") or 30)),"blockers":[]}
        if action == "update.stage":
            return self.update_stager.plan(str(payload.get("component") or ""),asset_name=str(payload.get("asset_name") or ""))
        if action == "presentation.plan":
            return self.presentation_planner.plan(str(payload.get("target") or ""))
        if action == "update.pack_apply":
            return self.update_orchestrator.plan(str(payload.get("component") or ""))
        if action == "update.auto_candidates":
            return {"allowed":True,"operation":"update.auto_candidates","items":self.update_orchestrator.auto_candidates(),"blockers":[]}
        raise ValueError("unsupported action")

    def perform(self, action: str, payload: dict[str, Any], *, actor: str = "local") -> dict[str, Any]:
        action_id = str(uuid.uuid4())
        started = time.time()
        requested = dict(payload or {})
        try:
            plan = self.plan(action, requested)
            if action == "operator.authorize":
                result=self.operator_sessions.authorize(str(requested.get("level") or ""),int(requested.get("duration_sec") or 900),actor=actor)
            elif action == "operator.revoke":
                result=self.operator_sessions.revoke()
            elif action == "backup.stage":
                result=self.backup_manager.stage(str(requested.get("name") or ""))
            elif action == "pack.inspect":
                result=self.pack_intake.inspect(str(requested.get("name") or ""))
            elif action == "pack.stage":
                result=self.pack_intake.stage(str(requested.get("name") or ""),replace=bool(requested.get("replace",False)))
            elif action == "pack.install":
                result=self.pack_installer.install(str(requested.get("id") or ""))
            elif action == "pack.rollback":
                result=self.pack_installer.rollback(str(requested.get("transaction_id") or ""))
            elif action == "update.stage":
                result=self.update_stager.stage(str(requested.get("component") or ""),asset_name=str(requested.get("asset_name") or ""))
            elif action == "update.pack_apply":
                result=self.update_orchestrator.apply(str(requested.get("component") or ""))
            elif action == "plugin.toggle":
                result = self.plugin_broker.toggle(str(requested.get("name") or ""), bool(requested.get("enabled")), restart=True)
            elif action == "service.restart":
                result = self.service_broker.restart(str(requested.get("unit") or ""))
            elif action == "container.control":
                result = self.container_broker.perform(str(requested.get("target") or ""),str(requested.get("operation") or ""))
            elif action == "support.bundle":
                job_id = f"support-{action_id}"
                self.store.upsert_job({"id":job_id,"kind":"support","label":"Sanitized Support Bundle","status":"running","created_at":started,"started_at":started,"progress":0.2,"detail":"Collecting privacy-conscious platform evidence"})
                result = self.support_manager.create()
                self.store.upsert_job({"id":job_id,"kind":"support","label":"Sanitized Support Bundle","status":"complete" if result.get("ok") else "failed","created_at":started,"started_at":started,"finished_at":time.time(),"progress":1.0 if result.get("ok") else None,"detail":str(result.get("path") or result.get("error") or "Support bundle finished"),"result":result})
            elif action == "backup.create":
                job_id = f"backup-{action_id}"
                self.store.upsert_job({"id":job_id,"kind":"backup","label":"Recovery Backup","status":"running","created_at":started,"started_at":started,"progress":0.15,"detail":"Creating verified recovery archive"})
                result = self.backup_manager.create()
                self.store.upsert_job({"id":job_id,"kind":"backup","label":"Recovery Backup","status":"complete" if result.get("ok") else "failed","created_at":started,"started_at":started,"finished_at":time.time(),"progress":1.0 if result.get("ok") else None,"detail":str(result.get("path") or result.get("error") or "Backup finished"),"result":result})
            else:
                raise ValueError("unsupported action")
            status = "success" if result.get("ok") else "rolled_back" if result.get("rolled_back") else "failed"
        except (PluginBrokerError, ServiceBrokerError, ContainerBrokerError, BackupError, PackIntakeError, PackInstallError, UpdateStageError, UpdateOrchestrationError, ValueError) as exc:
            plan = {}
            result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            status = "blocked" if isinstance(exc, PluginBrokerError) else "failed"
        finished = time.time()
        row = {
            "id": action_id,
            "ts": started,
            "finished_at": finished,
            "actor": str(actor),
            "action": action,
            "target": str(requested.get("name") or requested.get("unit") or requested.get("target") or ""),
            "status": status,
            "request": requested,
            "plan": plan,
            "result": result,
        }
        self.store.add_action(row)
        ev = self.events.publish("action.completed", "action_broker", {"id": action_id, "action": action, "target": row["target"], "status": status}, "warning" if status not in {"success"} else "info")
        self.store.add_event(ev)
        self.state.update_many("action_broker", {
            "actions.last.id": action_id,
            "actions.last.type": action,
            "actions.last.target": row["target"],
            "actions.last.status": status,
            "actions.last.finished_at": finished,
        }, priority=95)
        return row
