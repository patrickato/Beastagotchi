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
from .experience_try_on import ExperienceTryOnPlanner
from .update_orchestrator import PackUpdateOrchestrator, UpdateOrchestrationError
from .pack_activation import PackActivationManager, PackActivationError
from .roster import BeastRoster, BeastRosterError
from .global_sync import GlobalProfileSync, GlobalPublishPolicyError, clean_policy
from .memories import BeastMemoryEngine
from .owner_mode import OwnerModeManager
from .provider_preferences import ProviderPreferenceManager


class ActionBroker:
    """Small allow-listed privileged action dispatcher.

    This is deliberately narrower than a shell/command API. Each action gets a
    typed handler, a plan, a durable audit row, and explicit success/failure.
    Network/API exposure is a separate security decision.
    """

    def __init__(self, state, store, events, *, plugin_broker: PluginBroker | None = None, service_broker: ServiceBroker | None = None, container_broker: ContainerBroker | None = None, owner_mode: OwnerModeManager | None = None, provider_preferences: ProviderPreferenceManager | None = None) -> None:
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
        self.experience_try_on = ExperienceTryOnPlanner(state)
        self.update_orchestrator = PackUpdateOrchestrator(state, stager=self.update_stager, intake=self.pack_intake, installer=self.pack_installer)
        self.pack_activation = PackActivationManager(state)
        self.roster = BeastRoster(store)
        self.global_sync = GlobalProfileSync(state,store,self.roster)
        self.memories = BeastMemoryEngine(state,store,self.roster)
        self.owner_mode = owner_mode or OwnerModeManager()
        self.provider_preferences = provider_preferences or ProviderPreferenceManager()

    def _plugin_plan(self, name: str, enabled: bool, *, owner_override: bool, expert_mode: bool) -> dict[str, Any]:
        try:
            return self.plugin_broker.plan_toggle(
                name,
                enabled,
                owner_override=owner_override,
                expert_mode=expert_mode,
            )
        except TypeError as exc:
            # Preserve the older PluginBroker/test-double call contract for normal
            # managed operations.  An override must never silently fall back to a
            # broker that does not understand override semantics.
            if "unexpected keyword argument" not in str(exc):
                raise
            if owner_override:
                raise PluginBrokerError("active plugin broker does not support owner override") from exc
            return self.plugin_broker.plan_toggle(name, enabled)

    def _plugin_toggle(self, name: str, enabled: bool, *, owner_override: bool, expert_mode: bool) -> dict[str, Any]:
        try:
            return self.plugin_broker.toggle(
                name,
                enabled,
                restart=True,
                owner_override=owner_override,
                expert_mode=expert_mode,
            )
        except TypeError as exc:
            if "unexpected keyword argument" not in str(exc):
                raise
            if owner_override:
                raise PluginBrokerError("active plugin broker does not support owner override") from exc
            return self.plugin_broker.toggle(name, enabled, restart=True)

    def plan(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "plugin.toggle":
            expert = bool(self.owner_mode.snapshot().get("expert_mode_enabled"))
            return self._plugin_plan(
                str(payload.get("name") or ""),
                bool(payload.get("enabled")),
                owner_override=bool(payload.get("owner_override", False)),
                expert_mode=expert,
            )
        if action == "owner.expert_mode_get":
            return {"allowed": True, "operation": "owner.expert_mode_get", "state": self.owner_mode.snapshot(), "blockers": []}
        if action == "owner.expert_mode_set":
            requested = bool(payload.get("enabled", False))
            session = self.operator_sessions.current()
            allowed = bool(session.get("active")) and str(session.get("level") or "") == "administrator"
            return {
                "allowed": allowed,
                "operation": "owner.expert_mode_set",
                "current": self.owner_mode.snapshot(),
                "requested_enabled": requested,
                "requires_level": "administrator",
                "warnings": [
                    "Expert Mode allows explicit owner overrides of Beast managed-policy blockers. Technical blockers still apply.",
                    "Unsupported changes may reduce compatibility or rollback guarantees and will be marked as customized when an override is used.",
                ],
                "blockers": [] if allowed else ["active administrator session required"],
            }
        if action in {"provider.preference_set", "provider.preference_clear"}:
            capability = str(payload.get("capability") or "").strip()
            provider = str(payload.get("provider") or "").strip()
            session = self.operator_sessions.current()
            level = str(session.get("level") or "observer")
            authorized = bool(session.get("active")) and level in {"operator", "maintainer", "administrator"}
            blockers = []
            if not capability:
                blockers.append("missing capability")
            if action == "provider.preference_set" and not provider:
                blockers.append("missing provider")
            try:
                if capability:
                    ProviderPreferenceManager._clean_token(capability, "capability")
                if action == "provider.preference_set" and provider:
                    ProviderPreferenceManager._clean_token(provider, "provider")
            except ValueError as exc:
                blockers.append(str(exc))
            if not authorized:
                blockers.append("active operator session required")
            decisions = self.state.get("plugins.provider_decisions", {}) or {}
            decision = decisions.get(capability.lower().replace(" ", "_")) if isinstance(decisions, dict) else None
            candidates = [
                str(row.get("provider"))
                for row in (decision.get("candidates") or [])
                if isinstance(row, dict) and row.get("provider")
            ] if isinstance(decision, dict) else []
            warnings = []
            if action == "provider.preference_set" and provider and provider not in candidates:
                warnings.append("provider is not currently a ready/known candidate; preference will remain dormant until it becomes available")
            if action == "provider.preference_set":
                warnings.append("This changes provider policy only; it does not enable a plugin, start a service, switch hardware ownership, or perform failover.")
            else:
                warnings.append("Clearing returns the capability to automatic provider policy; it does not immediately mutate hardware or services.")
            return {
                "allowed": not blockers,
                "operation": action,
                "capability": capability,
                "provider": provider if action == "provider.preference_set" else None,
                "current": self.provider_preferences.snapshot(),
                "current_decision": decision,
                "known_candidates": candidates,
                "requires_level": "operator",
                "selection_mutation_enabled": False,
                "automatic_failover_enabled": False,
                "warnings": warnings,
                "blockers": blockers,
            }
        if action == "doctor.known_good_save":
            doctor = getattr(self, "doctor", None)
            return {
                "allowed": doctor is not None,
                "operation": "doctor.known_good_save",
                "label": str(payload.get("label") or "owner")[:80],
                "warnings": [
                    "This saves a privacy-light Doctor baseline in Beast's local database only.",
                    "It does not change the running platform, UI, providers, services or Pwnagotchi configuration.",
                ],
                "blockers": [] if doctor is not None else ["Beast Doctor unavailable"],
            }
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
        if action == "experience.try_on_tft_plan":
            return self.experience_try_on.plan(
                str(payload.get("id") or ""),
                page_id=str(payload.get("page") or "home"),
                duration_sec=int(payload.get("duration_sec") or 90),
            )
        if action == "update.pack_apply":
            return self.update_orchestrator.plan(str(payload.get("component") or ""))
        if action == "update.auto_candidates":
            return {"allowed":True,"operation":"update.auto_candidates","items":self.update_orchestrator.auto_candidates(),"blockers":[]}
        if action == "pack.activate":
            return self.pack_activation.plan(str(payload.get("id") or ""),True)
        if action == "pack.deactivate":
            return self.pack_activation.plan(str(payload.get("id") or ""),False)
        if action == "roster.snapshot":
            items=[]
            for b in self.roster.list():
                items.append({
                    "id":b["id"],"name":b["name"],"kind":b["kind"],"lineage_id":b["lineage_id"],
                    "status":b["status"],"active":bool(b["active"]),"generation":int(b.get("generation") or 0),
                    "level":int(b.get("level") or 1),"stage":b.get("stage"),
                    "achievement_count":len(b.get("achievements") or []),
                    "parent_ids":list(b.get("parents") or []),
                    "synthesis_eligible":bool(b.get("kind")=="beast" and int(b.get("level") or 1)>=70),
                    "has_preferred_presentation":bool(self.roster.presentation_preferences(b["id"])),
                    "preferred_presentation":self.roster.presentation_preferences(b["id"]),
                    "memory_summary":self.memories.summary(b["id"]),
                    "legend":bool(b.get("legend")),"legend_at":b.get("legend_at"),
                })
            active=next((x for x in items if x.get("active")),None)
            return {
                "allowed":True,"operation":"roster.snapshot","active_id":active.get("id") if active else None,
                "items":items,"count":len(items),"blockers":[]
            }
        if action == "roster.hall":
            hall=self.roster.hall_of_legends()
            def clean(b):
                return {
                    "id":b["id"],"name":b["name"],"kind":b["kind"],"lineage_id":b["lineage_id"],
                    "level":b["level"],"stage":b["stage"],"generation":b["generation"],
                    "active":b["active"],"legend":b.get("legend"),"legend_at":b.get("legend_at"),
                    "achievement_count":len(b.get("achievements") or []),"memory_summary":self.memories.summary(b["id"]),
                    "parents":list(b.get("parents") or []),
                    "children":[e["child_id"] for e in hall["graph"]["edges"] if e["parent_id"]==b["id"]],
                    "mutation":((b.get("appearance") or {}).get("mutation")),
                }
            return {"allowed":True,"operation":"roster.hall","inductees":[clean(b) for b in hall["inductees"]],
                    "candidates":[clean(b) for b in hall["candidates"]],"level_100_count":hall["level_100_count"],
                    "graph":hall["graph"],"blockers":[]}
        if action == "roster.legend_set":
            beast=self.roster.get(str(payload.get("id") or ""));enabled=bool(payload.get("enabled",True))
            blockers=[]
            if enabled and int(beast.get("level") or 1)<100:blockers.append("Hall of Legends induction requires level 100")
            return {"allowed":not blockers,"operation":"roster.legend_set","id":beast["id"],"name":beast["name"],
                    "enabled":enabled,"current":bool(beast.get("legend")),
                    "warnings":["Hall membership is separate from active/resting state and never changes XP or progression."],
                    "blockers":blockers}
        if action == "roster.synthesis_plan":
            parent_a=str(payload.get("parent_a") or "")
            parent_b=str(payload.get("parent_b") or "")
            plan=self.roster.synthesis_plan(parent_a,parent_b)
            if plan.get("parent_a") and plan.get("parent_b"):
                from .heritage import mutation_chance_basis_points
                plan["mutation_chance_basis_points"]=mutation_chance_basis_points(plan["parent_a"],plan["parent_b"])
            plan["child_name"]=str(payload.get("name") or "Monster")[:64]
            plan["creates_immediately"]=False
            return plan
        if action == "roster.synthesize":
            parent_a=str(payload.get("parent_a") or "")
            parent_b=str(payload.get("parent_b") or "")
            plan=self.roster.synthesis_plan(parent_a,parent_b)
            if plan.get("parent_a") and plan.get("parent_b"):
                from .heritage import mutation_chance_basis_points
                plan["mutation_chance_basis_points"]=mutation_chance_basis_points(plan["parent_a"],plan["parent_b"])
            plan["operation"]="roster.synthesize"
            plan["child_name"]=str(payload.get("name") or "Monster")[:64]
            return plan
        if action == "roster.presentation_get":
            beast=self.roster.get(str(payload.get("id") or self.roster.active()["id"]))
            pref=self.roster.presentation_preferences(beast["id"])
            return {
                "allowed":True,"operation":"roster.presentation_get","id":beast["id"],
                "name":beast["name"],"presentation":pref,"has_preferred_presentation":bool(pref),
                "blockers":[]
            }
        if action == "roster.presentation_set":
            beast=self.roster.get(str(payload.get("id") or self.roster.active()["id"]))
            presentation=payload.get("presentation") if isinstance(payload.get("presentation"),dict) else {}
            clean={k:presentation[k] for k in self.roster.PRESENTATION_KEYS if k in presentation}
            raw=__import__("json").dumps(clean,separators=(",",":"))
            blockers=[] if len(raw.encode("utf-8"))<=262144 else ["preferred presentation exceeds 256 KiB"]
            return {
                "allowed":not blockers,"operation":"roster.presentation_set","id":beast["id"],
                "name":beast["name"],"presentation":clean,
                "warnings":["This stores a preferred presentation for the creature; it does not change the currently running UI."],
                "blockers":blockers
            }
        if action == "roster.presentation_clear":
            beast=self.roster.get(str(payload.get("id") or self.roster.active()["id"]))
            return {"allowed":True,"operation":"roster.presentation_clear","id":beast["id"],"name":beast["name"],"blockers":[]}
        if action == "roster.switch":
            target=str(payload.get("id") or "")
            if not target:
                return {"allowed":False,"operation":"roster.switch","blockers":["missing Beast/Monster id"]}
            current=self.roster.active()
            candidate=self.roster.get(target)
            return {
                "allowed":True,"operation":"roster.switch","from_id":current["id"],"to_id":candidate["id"],
                "already_active":bool(candidate.get("active")),
                "warnings":["Switching changes the active progression identity only. The current UI Experience is not changed automatically in this milestone."],
                "blockers":[]
            }
        if action == "global.preview":
            policy=self.global_sync.policy()
            snapshot=self.global_sync.build_snapshot(policy)
            return {
                "allowed":True,"operation":"global.preview","policy":policy,"snapshot":snapshot,
                "pending":self.global_sync.pending(20),
                "local_roster":[{"id":b["id"],"name":b["name"],"kind":b["kind"],"level":b["level"],"active":b["active"]} for b in self.global_sync.roster.list()],
                "network_io_enabled":False,"blockers":[]
            }
        if action == "global.policy_set":
            requested=clean_policy(payload.get("policy") if isinstance(payload.get("policy"),dict) else {})
            return {
                "allowed":True,"operation":"global.policy_set","current":self.global_sync.policy(),
                "requested":requested,"network_io_enabled":False,
                "warnings":["Global connector is not configured; this changes only the local privacy/publish policy and local revision queue."],
                "blockers":[]
            }
        raise ValueError("unsupported action")

    def perform(self, action: str, payload: dict[str, Any], *, actor: str = "local") -> dict[str, Any]:
        action_id = str(uuid.uuid4())
        started = time.time()
        requested = dict(payload or {})
        try:
            plan = self.plan(action, requested)
            if action == "owner.expert_mode_set":
                if not plan.get("allowed"):
                    raise ValueError("; ".join(plan.get("blockers") or ["Expert Mode change blocked"]))
                result = {"ok": True, "state": self.owner_mode.set_expert(bool(requested.get("enabled", False)), actor=actor)}
                self.state.update_many("owner_mode", self.owner_mode.state_patch(), priority=99)
            elif action == "owner.expert_mode_get":
                result = {"ok": True, "state": self.owner_mode.snapshot()}
            elif action == "provider.preference_set":
                if not plan.get("allowed"):
                    raise ValueError("; ".join(plan.get("blockers") or ["provider preference change blocked"]))
                result = {
                    "ok": True,
                    "preferences": self.provider_preferences.set(
                        str(requested.get("capability") or ""),
                        str(requested.get("provider") or ""),
                        actor=actor,
                    ),
                    "provider_switched": False,
                }
                self.state.update_many("provider_preferences", self.provider_preferences.state_patch(), priority=98)
            elif action == "provider.preference_clear":
                if not plan.get("allowed"):
                    raise ValueError("; ".join(plan.get("blockers") or ["provider preference clear blocked"]))
                result = {
                    "ok": True,
                    "preferences": self.provider_preferences.clear(
                        str(requested.get("capability") or ""),
                        actor=actor,
                    ),
                    "provider_switched": False,
                }
                self.state.update_many("provider_preferences", self.provider_preferences.state_patch(), priority=98)
            elif action == "operator.authorize":
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
            elif action == "pack.activate":
                result=self.pack_activation.set_enabled(str(requested.get("id") or ""),True)
            elif action == "pack.deactivate":
                result=self.pack_activation.set_enabled(str(requested.get("id") or ""),False)
            elif action == "roster.legend_set":
                before=self.roster.get(str(requested.get("id") or ""))
                after=self.roster.set_legend(before["id"],bool(requested.get("enabled",True)))
                enabled=bool(after.get("legend"))
                if enabled and not before.get("legend"):
                    self.memories.record_custom(after["id"],"legend","Inducted into the Hall of Legends",
                        {"level":after["level"],"stage":after["stage"]},rarity="mythic",memory_id=f"legend:{after['id']}")
                result={"ok":True,"id":after["id"],"legend":enabled,"legend_at":after.get("legend_at"),
                        "active":after["active"],"level":after["level"]}
            elif action == "roster.synthesize":
                result=self.roster.synthesize(
                    str(requested.get("parent_a") or ""),
                    str(requested.get("parent_b") or ""),
                    name=str(requested.get("name") or "Monster")[:64],
                )
                monster=result.get("monster") or {}
                reveal_now=time.time();mutation=((monster.get("appearance") or {}).get("mutation"))
                self.state.update_many("roster",{
                    "roster.last_monster.id":monster.get("id"),
                    "roster.last_monster.name":monster.get("name"),
                    "roster.last_monster.generation":monster.get("generation"),
                    "roster.count":len(self.roster.list()),
                    "roster.monster_reveal.id":monster.get("id"),
                    "roster.monster_reveal.name":monster.get("name"),
                    "roster.monster_reveal.generation":monster.get("generation"),
                    "roster.monster_reveal.stage":monster.get("stage"),
                    "roster.monster_reveal.parents":[p.get("name") for p in result.get("parents") or []],
                    "roster.monster_reveal.traits":((monster.get("identity") or {}).get("traits") or {}),
                    "roster.monster_reveal.mutation":mutation,
                    "roster.monster_reveal.first_unlock":bool(result.get("first_monstergotchi_unlock")),
                    "roster.monster_reveal.created_at":reveal_now,
                    "roster.monster_reveal.until":reveal_now+12.0,
                },priority=89)
                mev=self.events.publish("roster.monster_created","roster",{
                    "id":monster.get("id"),"name":monster.get("name"),
                    "generation":monster.get("generation"),
                    "parents":list(monster.get("parents") or []),
                    "mutation":((monster.get("appearance") or {}).get("mutation")),
                },"info")
                self.store.add_event(mev)
                child_id=str(monster.get("id") or "")
                if child_id:
                    self.memories.record_custom(
                        child_id,"origin",
                        f"Created from {result['parents'][0]['name']} × {result['parents'][1]['name']}",
                        {"synthesis_id":result.get("synthesis_id"),"parents":list(monster.get("parents") or []),
                         "generation":monster.get("generation"),"mutation":((monster.get("appearance") or {}).get("mutation"))},
                        rarity=str((((monster.get("appearance") or {}).get("mutation") or {}).get("rarity") or "")) or None,
                        memory_id=f"synthesis:{result.get('synthesis_id')}:child",
                    )
                    for parent_row in result.get("parents") or []:
                        self.memories.record_custom(
                            str(parent_row.get("id")),"lineage",
                            f"Descendant created · {monster.get('name') or child_id}",
                            {"synthesis_id":result.get("synthesis_id"),"child_id":child_id,"generation":monster.get("generation")},
                            memory_id=f"synthesis:{result.get('synthesis_id')}:parent:{parent_row.get('id')}",
                        )
            elif action == "roster.presentation_set":
                beast=self.roster.set_presentation_preferences(
                    str(requested.get("id") or self.roster.active()["id"]),
                    requested.get("presentation") if isinstance(requested.get("presentation"),dict) else {},
                )
                result={"ok":True,"id":beast["id"],"presentation":self.roster.presentation_preferences(beast["id"]),"ui_changed":False}
            elif action == "roster.presentation_clear":
                beast=self.roster.clear_presentation_preferences(str(requested.get("id") or self.roster.active()["id"]))
                result={"ok":True,"id":beast["id"],"presentation":{},"ui_changed":False}
            elif action == "roster.switch":
                before=self.roster.active()
                after=self.roster.set_active(str(requested.get("id") or ""))
                self.state.update_many("roster",{
                    "roster.active.id":after["id"],"roster.active.name":after["name"],
                    "roster.active.kind":after["kind"],"roster.active.level":after["level"],
                    "roster.active.stage":after["stage"],"roster.count":len(self.roster.list()),
                },priority=89)
                result={"ok":True,"from_id":before["id"],"active":after,"experience_changed":False}
            elif action == "global.policy_set":
                policy=self.global_sync.set_policy(requested.get("policy") if isinstance(requested.get("policy"),dict) else {})
                patch=self.global_sync.tick()
                self.state.update_many("global_sync",patch,priority=62)
                result={"ok":True,"policy":policy,"snapshot":self.global_sync.build_snapshot(policy),"state":patch,"network_io_performed":False}
            elif action == "plugin.toggle":
                expert = bool(self.owner_mode.snapshot().get("expert_mode_enabled"))
                result = self._plugin_toggle(
                    str(requested.get("name") or ""),
                    bool(requested.get("enabled")),
                    owner_override=bool(requested.get("owner_override", False)),
                    expert_mode=expert,
                )
                p = result.get("plan") if isinstance(result.get("plan"), dict) else plan
                if result.get("ok") and p.get("owner_override_executed"):
                    mode = self.owner_mode.record_override(
                        action="plugin.toggle",
                        target=str(requested.get("name") or ""),
                        actor=actor,
                        policy_blockers=list(p.get("policy_blockers") or []),
                    )
                    self.state.update_many("owner_mode", self.owner_mode.state_patch(), priority=99)
                    result["owner_mode"] = mode
            elif action == "doctor.known_good_save":
                doctor = getattr(self, "doctor", None)
                if doctor is None:
                    raise ValueError("Beast Doctor unavailable")
                saved = doctor.save_known_good(str(requested.get("label") or "owner")[:80])
                result = {"ok": True, **saved}
                self.state.update_many("doctor", doctor.state_patch(), priority=76)
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
        except (PluginBrokerError, ServiceBrokerError, ContainerBrokerError, BackupError, PackIntakeError, PackInstallError, UpdateStageError, UpdateOrchestrationError, PackActivationError, GlobalPublishPolicyError, BeastRosterError, ValueError) as exc:
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
            "target": (
                "doctor.patient"
                if action == "doctor.known_good_save"
                else str(requested.get("name") or requested.get("unit") or requested.get("target")
                         or requested.get("id") or requested.get("capability") or "")
            ),
            "status": status,
            "request": requested,
            "plan": plan,
            "result": result,
        }
        self.store.add_action(row)
        ev = self.events.publish("action.completed", "action_broker", {"id": action_id, "action": action, "target": row["target"], "status": status}, "warning" if status not in {"success"} else "info")
        if status == "success" and action == "owner.expert_mode_set":
            mode = self.owner_mode.snapshot()
            mev = self.events.publish("owner.expert_mode.changed", "owner_mode", {"enabled": bool(mode.get("expert_mode_enabled")), "support_state": mode.get("support_state")}, "warning" if mode.get("expert_mode_enabled") else "info")
            self.store.add_event(mev)
        elif status == "success" and action in {"provider.preference_set", "provider.preference_clear"}:
            pref = self.provider_preferences.snapshot()
            mev = self.events.publish(
                "provider.preference.changed",
                "provider_preferences",
                {
                    "capability": str(requested.get("capability") or ""),
                    "provider": pref.get("values", {}).get(str(requested.get("capability") or "")),
                    "operation": action,
                    "provider_switched": False,
                },
                "info",
            )
            self.store.add_event(mev)
        elif status == "success" and action == "plugin.toggle" and bool((result.get("plan") or {}).get("owner_override_executed")):
            mev = self.events.publish("owner.override.used", "owner_mode", {"action": action, "target": row["target"], "policy_blockers": list((result.get("plan") or {}).get("policy_blockers") or [])}, "warning")
            self.store.add_event(mev)
        self.store.add_event(ev)
        self.state.update_many("action_broker", {
            "actions.last.id": action_id,
            "actions.last.type": action,
            "actions.last.target": row["target"],
            "actions.last.status": status,
            "actions.last.finished_at": finished,
        }, priority=95)
        return row
