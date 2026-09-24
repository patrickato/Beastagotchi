from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from . import __version__
from .api import LocalAPI
from .context import ContextEngine
from .events import EventBus
from .state import StateRegistry
from .db import Store
from .timeseries import TimeSeriesSampler
from .semantic import SemanticEngine
from .dock import DockEngine
from .progression import ProgressionEngine
from .roster_progression import ActiveBeastProgressionStore
from .global_achievements import GlobalAchievementEngine
from .rare import RareMomentEngine
from .ambient import AmbientContextEngine
from .governor import ResourceGovernor
from .expeditions import ExpeditionEngine
from .channel_history import ChannelActivityEngine
from .telemetry import TelemetryCatalog
from .plugin_integration import PluginIntegrationEngine
from .dependency_resolver import DependencyCapabilityResolver
from .template_tokens import TemplateTokenRegistry
from .records import RecordsEngine
from .overview import OverviewEngine
from .topology import ServiceTopologyEngine
from .field_library import FieldLibraryEngine
from .operator_policy import OperatorPolicy
from .operator_tools import OperatorToolRegistry
from .personality import PersonalityEngine
from .presentation import PresentationBroker
from .missions import MissionPackEngine
from .packs import PackRegistryEngine
from .updates import UpdatePolicyEngine
from .update_automation import UpdateAutomationEngine
from .search import UniversalSearch
from .incidents import IncidentEngine
from .peerdex import PeerDex
from .roster import BeastRoster
from .global_sync import GlobalProfileSync
from .memories import BeastMemoryEngine
from .actions import ActionBroker
from .owner_mode import OwnerModeManager
from .action_server import LocalActionServer
from .collectors import *

log = logging.getLogger("beastcore")

class BeastCore:
    def __init__(self, db_path: str = "/var/lib/beastagotchi/beast.db", host: str = "127.0.0.1", port: int = 8090) -> None:
        self.state = StateRegistry()
        self.events = EventBus()
        self.store = Store(db_path)
        self.channel_history = ChannelActivityEngine(self.state)
        self.telemetry = TelemetryCatalog(self.state)
        self.dependencies = DependencyCapabilityResolver(self.state)
        self.plugin_integration = PluginIntegrationEngine(self.state, resolver=self.dependencies)
        self.template_tokens = TemplateTokenRegistry(self.state)
        self.api = LocalAPI(self.state, self.events, self.store, host, port,
                            channel_history=self.channel_history, telemetry=self.telemetry)
        self.api.template_tokens = self.template_tokens
        self.collectors = [
            SystemCollector(), RadioCollector(), GPSCollector(), BettercapCollector(),
            PwnagotchiCollector(), BridgeCollector(), ServicesCollector(), StorageCollector(), HardwareCollector(),
            NetworkCollector(), CapabilityCollector(), PowerCollector(), DisplayCollector(), BluetoothCollector(), ContainerCollector(), BackupCollector(), AICapabilityCollector(), DesktopCapabilityCollector(), PerformanceCollector()
        ]
        self.stop_event = asyncio.Event()
        self.started_mono = time.monotonic()
        self.health: dict[str, dict[str, Any]] = {}
        self.context = ContextEngine(self.state)
        self.sampler = TimeSeriesSampler(self.state, self.store)
        self.dock = DockEngine(self.state)
        self.progression_store = ActiveBeastProgressionStore(self.store)
        self.roster = self.progression_store.roster
        self.progression = ProgressionEngine(self.state, profile_store=self.progression_store)
        self.semantic = SemanticEngine(self.state, self.store, active_beast_id=self.progression_store.current_id)
        self.global_achievements = GlobalAchievementEngine(self.state,self.store,self.roster)
        self.rare = RareMomentEngine(self.state)
        self.ambient = AmbientContextEngine(self.state)
        self.governor = ResourceGovernor(self.state)
        self.expedition = ExpeditionEngine(self.state, self.store)
        self.records = RecordsEngine(self.state, self.store)
        self.overview = OverviewEngine(self.state)
        self.topology = ServiceTopologyEngine(self.state)
        self.field_library = FieldLibraryEngine(self.state, self.store)
        self.operator_policy = OperatorPolicy()
        self.personality = PersonalityEngine(self.state)
        self.presentation = PresentationBroker(self.state)
        self.missions = MissionPackEngine(self.state)
        self.packs = PackRegistryEngine(self.state, resolver=self.dependencies)
        self.updates = UpdatePolicyEngine(self.state)
        self.search = UniversalSearch(self.state, self.store)
        self.incidents = IncidentEngine(self.state, self.store, self.events)
        self.peerdex = PeerDex(self.store)
        self.global_sync = GlobalProfileSync(self.state,self.store,self.roster)
        self.memories = BeastMemoryEngine(self.state,self.store,self.roster)
        self.owner_mode = OwnerModeManager()
        self.state.update_many("owner_mode", self.owner_mode.state_patch(), priority=99)
        self.api.search_engine = self.search
        self.api.operator_policy = self.operator_policy
        self.actions = ActionBroker(self.state, self.store, self.events, owner_mode=self.owner_mode)
        self.update_automation = UpdateAutomationEngine(self.state, self.actions)
        self.operator_tools = OperatorToolRegistry(self.state,self.store,self.search,self.actions)
        self.api.backup_manager = self.actions.backup_manager
        self.api.operator_tools = self.operator_tools
        self.action_server = LocalActionServer(self.actions)
        self.state.update_many("beastcore", {"system.beast_version": __version__}, priority=100)
        self.state.update_many("peerdex", self.peerdex.summary(), priority=83)

    def _health_patch(self, c, state: str, duration_ms: float, error: str | None = None) -> dict[str, Any]:
        now = time.time()
        h = self.health.setdefault(c.name, {"consecutive_errors": 0, "last_ok": None, "last_run": None})
        h["last_run"] = now
        if state == "ok":
            h["consecutive_errors"] = 0
            h["last_ok"] = now
            h["last_error"] = None
        else:
            h["consecutive_errors"] = int(h.get("consecutive_errors", 0)) + 1
            h["last_error"] = error
        h["state"] = state
        h["duration_ms"] = round(duration_ms, 2)
        prefix = f"health.collector.{c.name}."
        return {
            prefix+"state": h["state"],
            prefix+"duration_ms": h["duration_ms"],
            prefix+"consecutive_errors": h["consecutive_errors"],
            prefix+"last_run": h["last_run"],
            prefix+"last_ok": h.get("last_ok"),
            prefix+"last_error": h.get("last_error"),
        }

    def _publish_progression_followups(self, ev) -> None:
        # Progression events are cosmetic/identity events. Do not recursively feed
        # progression events back into the progression engine.
        if str(getattr(ev, "type", "")).startswith("progression."):
            return
        try:
            rows = self.progression.on_event(ev)
        except Exception:
            log.exception("progression event handler failed")
            return
        for etype, source, data, severity in rows:
            pdata=dict(data or {});pdata.setdefault('beast_id',str(self.state.get('progression.beast.id') or self.roster.active()['id']))
            pev = self.events.publish(etype, source, pdata, severity)
            self.store.add_event(pev)
            self.memories.record_event(pev)

    def _publish_durable(self, event_type: str, source: str, data=None, severity: str = "info"):
        ev = self.events.publish(event_type, source, data or {}, severity)
        self.store.add_event(ev)
        self.memories.record_event(ev)
        self._publish_progression_followups(ev)
        return ev

    def _publish_bridge_events(self, c) -> None:
        try: pending = c.drain_events()
        except Exception: pending = []
        for raw in pending:
            et = str(raw.get("type") or "event")
            data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
            if raw.get("seq") is not None: data = dict(data, bridge_seq=raw.get("seq"))
            if et == "peer_detected":
                peer = self.peerdex.observe(data, ts=raw.get("ts"))
                if peer.get("accepted"):
                    data = dict(data, peerdex=peer)
                    self.state.update_many("peerdex", self.peerdex.summary(), priority=83)
            elif et == "peer_lost":
                peer = self.peerdex.mark_lost(data, ts=raw.get("ts"))
                if peer.get("accepted"):
                    data = dict(data, peerdex=peer)
                    self.state.update_many("peerdex", self.peerdex.summary(), priority=83)
            ev = self.events.publish(f"pwnagotchi.{et}", "bridge", data)
            # Preserve plugin callback timestamp when supplied.
            try:
                if raw.get("ts") is not None: ev.ts = float(raw["ts"])
            except Exception: pass
            self.store.add_event(ev)
            self._publish_progression_followups(ev)

    async def _collector_loop(self, c) -> None:
        await asyncio.sleep(0.05)
        while not self.stop_event.is_set():
            started = time.monotonic()
            try:
                values = await asyncio.to_thread(c.collect)
                changed = self.state.update_many(c.name, values, priority=getattr(c, "priority", 50))
                duration_ms = (time.monotonic() - started) * 1000.0
                self.state.update_many("health", self._health_patch(c, "ok", duration_ms), priority=100)
                self._publish_bridge_events(c)
                # Plugin catalog depends on Pwnagotchi's parsed plugin inventory.
                # Refresh immediately when that collector runs instead of leaving
                # a 0-item catalog visible until the independent 5s integration
                # loop happens to run again.
                if c.name == "pwnagotchi" and any(k == "platform.plugins" for k, *_ in changed):
                    self.state.update_many("plugin_integration", self.plugin_integration.tick(), priority=82)
                if changed:
                    keys = [x[0] for x in changed]
                    # State patches are streamed live but not persisted; otherwise the
                    # durable event timeline is buried under high-frequency telemetry.
                    self.events.publish("state.changed", c.name, {"keys": keys})
            except Exception as exc:
                duration_ms = (time.monotonic() - started) * 1000.0
                log.exception("collector %s failed", c.name)
                self.state.update_many("health", self._health_patch(c, "error", duration_ms, repr(exc)), priority=100)
                ev = self.events.publish("collector.error", c.name, {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            delay = max(0.05, c.interval - (time.monotonic() - started))
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
            except asyncio.TimeoutError: pass

    def _health_summary(self, now: float, uptime: float) -> dict[str, Any]:
        """Compute truthful Core readiness/health without treating boot as failure.

        Collectors start concurrently.  During the first seconds of a normal boot
        some have not completed their first sample yet; that is STARTING, not
        DEGRADED.  After the startup grace expires, a collector that has never
        produced a good sample is legitimately degraded.
        """
        degraded: list[str] = []
        starting: list[str] = []
        for c in self.collectors:
            h = self.health.get(c.name) or {}
            last_ok = h.get("last_ok")
            age = (now - last_ok) if isinstance(last_ok, (int, float)) else None
            if last_ok is None:
                starting.append(c.name)
                self.state.update_many("health", {
                    f"health.collector.{c.name}.state": "starting",
                    f"health.collector.{c.name}.age_sec": None,
                }, priority=100)
                continue
            if age is not None and age > c.effective_stale_after:
                self.state.mark_source_stale(c.name, c.effective_stale_after)
                degraded.append(c.name)
                self.state.update_many("health", {
                    f"health.collector.{c.name}.state": "stale",
                    f"health.collector.{c.name}.age_sec": round(age, 2),
                }, priority=100)
            else:
                self.state.update_many("health", {
                    f"health.collector.{c.name}.state": "ok",
                    f"health.collector.{c.name}.age_sec": round(age, 2) if age is not None else None,
                }, priority=100)

        critical_failures: list[str] = []
        startup_grace = 20.0
        if uptime >= startup_grace:
            # Anything that never produced a successful first sample after the
            # grace period is no longer merely "starting".
            degraded.extend(x for x in starting if x not in degraded)
            starting = []
            pwn = str(self.state.get("pwnagotchi.service.state") or "unknown").lower()
            better = str(self.state.get("bettercap.state") or "unknown").lower()
            if pwn not in {"active", "running"}:
                critical_failures.append(f"pwnagotchi:{pwn}")
            if better not in {"active", "running", "ready"}:
                critical_failures.append(f"bettercap:{better}")
            if bool(self.state.get("storage.root.readonly")):
                critical_failures.append("storage:readonly")

        if critical_failures:
            core_state = "critical"
        elif starting and uptime < startup_grace:
            core_state = "starting"
        elif degraded:
            core_state = "degraded"
        else:
            core_state = "healthy"

        return {
            "health.core.state": core_state,
            "health.core.ok": core_state == "healthy",
            "health.core.ready": not starting,
            "health.core.uptime_sec": round(uptime, 2),
            "health.core.collector_count": len(self.collectors),
            "health.core.starting_collectors": starting,
            "health.core.degraded_collectors": degraded,
            "health.core.critical_failures": critical_failures,
            "health.core.critical_count": len(critical_failures),
        }

    async def _health_loop(self) -> None:
        while not self.stop_event.is_set():
            now = time.time()
            uptime = time.monotonic() - self.started_mono
            self.state.update_many("health", self._health_summary(now, uptime), priority=100)
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

    async def _context_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                changed = self.state.update_many("context", self.context.tick(), priority=90)
                if changed:
                    self.events.publish("context.changed", "context", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("context engine failed")
                ev = self.events.publish("context.error", "context", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError: pass


    async def _semantic_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                for etype, source, data, severity in self.semantic.tick():
                    self._publish_durable(etype, source, data, severity)
            except Exception as exc:
                log.exception("semantic engine failed")
                ev = self.events.publish("semantic.error", "semantic", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError: pass

    async def _dock_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                changed = self.state.update_many("dock", self.dock.tick(), priority=92)
                if changed:
                    self.events.publish("dock.changed", "dock", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("dock engine failed")
                ev = self.events.publish("dock.error", "dock", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError: pass

    async def _global_achievement_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                for etype,source,data,severity in self.global_achievements.tick():
                    ev=self.events.publish(etype,source,data,severity)
                    self.store.add_event(ev)
            except Exception as exc:
                log.exception("global achievement engine failed")
                ev=self.events.publish("global.achievement_error","global_achievements",{"error":repr(exc)},"warning")
                self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=5.0)
            except asyncio.TimeoutError:pass

    async def _progression_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                for etype, source, data, severity in self.progression.tick():
                    # These are already progression-originated; persist/publish but
                    # do not feed them back into ProgressionEngine.
                    ev = self.events.publish(etype, source, data, severity)
                    self.store.add_event(ev)
            except Exception as exc:
                log.exception("progression engine failed")
                ev = self.events.publish("progression.error", "progression", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=5.0)
            except asyncio.TimeoutError: pass


    async def _personality_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                personality_patch=self.personality.tick()
                self.state.update_many("personality", personality_patch, priority=87)
                self.memories.observe_personality(personality_patch)
                self.state.update_many("operator_session", {"operator.session":self.actions.operator_sessions.current(),"operator.policy.level":self.actions.operator_sessions.current().get("level","observer")}, priority=96)
            except Exception as exc:
                log.exception("personality engine failed")
                ev=self.events.publish("personality.error","personality",{"error":repr(exc)},"warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError: pass

    async def _mission_loop(self) -> None:
        while not self.stop_event.is_set():
            try:self.state.update_many("missions",self.missions.tick(),priority=65)
            except Exception as exc:
                log.exception("mission pack engine failed")
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=30.0)
            except asyncio.TimeoutError: pass

    async def _rare_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                for etype, source, data, severity in self.rare.tick():
                    self._publish_durable(etype, source, data, severity)
            except Exception as exc:
                log.exception("rare moment engine failed")
                ev = self.events.publish("rare.error", "rare", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=0.5)
            except asyncio.TimeoutError: pass

    async def _ambient_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                self.state.update_many("ambient", self.ambient.tick(), priority=55)
            except Exception as exc:
                log.exception("ambient engine failed")
                ev = self.events.publish("ambient.error", "ambient", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=60.0)
            except asyncio.TimeoutError: pass

    async def _governor_loop(self) -> None:
        previous = None
        while not self.stop_event.is_set():
            try:
                patch = self.governor.tick()
                mode = patch.get("governor.mode")
                changed = self.state.update_many("governor", patch, priority=96)
                if previous is not None and mode != previous:
                    self._publish_durable("governor.mode_changed", "governor", {
                        "from": previous, "to": mode, "reason": patch.get("governor.reason"),
                        "budget_pct": patch.get("governor.budget_pct"),
                    }, "warning" if mode in {"REDUCED","SURVIVAL"} else "info")
                previous = mode
                if changed:
                    self.events.publish("governor.changed", "governor", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("resource governor failed")
                ev = self.events.publish("governor.error", "governor", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError: pass

    async def _expedition_loop(self) -> None:
        # Give collectors/progression one first sample so expedition baselines are
        # meaningful without slowing Beast Core startup.
        try: await asyncio.wait_for(self.stop_event.wait(), timeout=0.35)
        except asyncio.TimeoutError: pass
        while not self.stop_event.is_set():
            try:
                patch, rows = self.expedition.tick()
                changed = self.state.update_many("expedition", patch, priority=87)
                self.memories.observe_expedition(patch)
                for etype, source, data, severity in rows:
                    self._publish_durable(etype, source, data, severity)
                if changed:
                    self.events.publish("expedition.changed", "expedition", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("expedition engine failed")
                ev = self.events.publish("expedition.error", "expedition", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError: pass


    async def _channel_history_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                patch = self.channel_history.tick()
                changed = self.state.update_many("channel_activity", patch, priority=84)
                if changed:
                    self.events.publish("channel_activity.changed", "channel_activity", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("channel activity engine failed")
                ev = self.events.publish("channel_activity.error", "channel_activity", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError: pass

    async def _presentation_loop(self) -> None:
        # v0.19 continuously exposes presentation ownership truth but does not
        # yet execute physical handoffs. v0.18 display scripts remain the
        # validated path until owner adapters pass off-screen + physical gates.
        while not self.stop_event.is_set():
            try:
                changed = self.state.update_many("presentation", self.presentation.tick(), priority=93)
                if changed:
                    self.events.publish("presentation.changed", "presentation", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("presentation broker failed")
                ev = self.events.publish("presentation.error", "presentation", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError: pass

    async def _packs_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                changed = self.state.update_many("packs", self.packs.tick(), priority=73)
                if changed:
                    self.events.publish("packs.changed", "packs", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("pack registry failed")
                ev = self.events.publish("packs.error", "packs", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=10.0)
            except asyncio.TimeoutError: pass

    async def _updates_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                patch = await asyncio.to_thread(self.updates.tick)
                changed = self.state.update_many("updates", patch, priority=74)
                if changed:
                    self.events.publish("updates.changed", "updates", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("update policy engine failed")
                ev = self.events.publish("updates.error", "updates", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=10.0)
            except asyncio.TimeoutError: pass

    async def _update_automation_loop(self) -> None:
        # Policy-selected staging is intentionally much slower than telemetry.
        while not self.stop_event.is_set():
            try:
                patch = await asyncio.to_thread(self.update_automation.tick)
                changed = self.state.update_many("update_automation", patch, priority=75)
                if changed:
                    self.events.publish(
                        "update_automation.changed",
                        "update_automation",
                        {"keys": [x[0] for x in changed]},
                    )
            except Exception as exc:
                log.exception("update automation failed")
                ev = self.events.publish(
                    "update_automation.error",
                    "update_automation",
                    {"error": repr(exc)},
                    "warning",
                )
                self.store.add_event(ev)
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=60.0)
            except asyncio.TimeoutError:
                pass

    async def _plugin_integration_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                changed = self.state.update_many("plugin_integration", self.plugin_integration.tick(), priority=82)
                if changed:
                    self.events.publish("plugins.changed", "plugin_integration", {"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("plugin integration engine failed")
                ev = self.events.publish("plugins.error", "plugin_integration", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=5.0)
            except asyncio.TimeoutError: pass

    async def _global_sync_loop(self) -> None:
        # Privacy-first local publisher. This only creates sanitized revisions in
        # the local queue; a separate future connector performs network I/O.
        while not self.stop_event.is_set():
            try:
                changed=self.state.update_many("global_sync",self.global_sync.tick(),priority=62)
                if changed:self.events.publish("global.changed","global_sync",{"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("global profile sync failed")
                ev=self.events.publish("global.error","global_sync",{"error":repr(exc)},"warning");self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=15.0)
            except asyncio.TimeoutError:pass

    async def _sample_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                count = self.sampler.sample()
                self.state.update_many("timeseries", {"history.last_sample_count":count, "history.last_sample_at":time.time()}, priority=50)
            except Exception as exc:
                log.exception("time-series sampler failed")
                ev = self.events.publish("history.error", "timeseries", {"error":repr(exc)}, "warning")
                self.store.add_event(ev)
            scale = self.state.get("governor.history.interval_scale", 1.0)
            try:
                scale = max(1.0, min(4.0, float(scale)))
            except (TypeError, ValueError):
                scale = 1.0
            try: await asyncio.wait_for(self.stop_event.wait(), timeout=self.sampler.interval * scale)
            except asyncio.TimeoutError: pass

    async def _records_loop(self) -> None:
        # Durable indexing is intentionally low-frequency: rich records without
        # high-rate SD-card churn.
        while not self.stop_event.is_set():
            try:
                changed=self.state.update_many("records",self.records.tick(),priority=72)
                if changed:self.events.publish("records.changed","records",{"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("records engine failed")
                ev=self.events.publish("records.error","records",{"error":repr(exc)},"warning");self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=20.0)
            except asyncio.TimeoutError:pass

    async def _overview_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                changed=self.state.update_many("overview",self.overview.tick(),priority=88)
                changed+=self.state.update_many("topology",self.topology.tick(),priority=88)
                changed+=self.state.update_many("operator_policy",self.operator_policy.snapshot("observer"),priority=40)
                if changed:self.events.publish("overview.changed","overview",{"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("overview/topology engine failed")
                ev=self.events.publish("overview.error","overview",{"error":repr(exc)},"warning");self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=1.0)
            except asyncio.TimeoutError:pass

    async def _incident_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                patch,rows=self.incidents.tick()
                changed=self.state.update_many("incidents",patch,priority=94)
                for etype,source,data,severity in rows:self._publish_durable(etype,source,data,severity)
                if changed:self.events.publish("incidents.changed","incidents",{"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("incident engine failed")
                ev=self.events.publish("incidents.error","incidents",{"error":repr(exc)},"warning");self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=2.0)
            except asyncio.TimeoutError:pass

    async def _field_library_loop(self) -> None:
        # Offline knowledge is indexed slowly to avoid turning the SD card into a search scratchpad.
        while not self.stop_event.is_set():
            try:
                changed=self.state.update_many("field_library",self.field_library.tick(),priority=60)
                self.state.update_many("task_center",{"tasks.recent":self.store.recent_jobs(12)},priority=55)
                if changed:self.events.publish("library.changed","field_library",{"keys":[x[0] for x in changed]})
            except Exception as exc:
                log.exception("field library engine failed")
                ev=self.events.publish("library.error","field_library",{"error":repr(exc)},"warning");self.store.add_event(ev)
            try:await asyncio.wait_for(self.stop_event.wait(),timeout=60.0)
            except asyncio.TimeoutError:pass

    async def run(self) -> None:
        await self.api.start()
        await self.action_server.start()
        ev = self.events.publish("core.started", "beastcore", {"version":__version__})
        self.store.add_event(ev)
        tasks = [asyncio.create_task(self._collector_loop(c), name=f"collector:{c.name}") for c in self.collectors]
        tasks += [
            asyncio.create_task(self._health_loop(), name="health"),
            asyncio.create_task(self._context_loop(), name="context"),
            asyncio.create_task(self._sample_loop(), name="timeseries"),
            asyncio.create_task(self._semantic_loop(), name="semantic"),
            asyncio.create_task(self._dock_loop(), name="dock"),
            asyncio.create_task(self._progression_loop(), name="progression"),
            asyncio.create_task(self._global_achievement_loop(), name="global-achievements"),
            asyncio.create_task(self._personality_loop(), name="personality"),
            asyncio.create_task(self._mission_loop(), name="missions"),
            asyncio.create_task(self._rare_loop(), name="rare"),
            asyncio.create_task(self._ambient_loop(), name="ambient"),
            asyncio.create_task(self._governor_loop(), name="governor"),
            asyncio.create_task(self._expedition_loop(), name="expedition"),
            asyncio.create_task(self._channel_history_loop(), name="channel-history"),
            asyncio.create_task(self._plugin_integration_loop(), name="plugin-integration"),
            asyncio.create_task(self._packs_loop(), name="packs"),
            asyncio.create_task(self._updates_loop(), name="updates"),
            asyncio.create_task(self._update_automation_loop(), name="update-automation"),
            asyncio.create_task(self._presentation_loop(), name="presentation"),
            asyncio.create_task(self._records_loop(), name="records"),
            asyncio.create_task(self._overview_loop(), name="overview"),
            asyncio.create_task(self._field_library_loop(), name="field-library"),
            asyncio.create_task(self._global_sync_loop(), name="global-sync"),
            asyncio.create_task(self._incident_loop(), name="incidents"),
        ]
        await self.stop_event.wait()
        ev = self.events.publish("core.stopping", "beastcore")
        self.store.add_event(ev)
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        try:
            checkpoint = self.expedition.checkpoint()
            if checkpoint:
                eid, summary = checkpoint
                self._publish_durable("expedition.checkpointed", "expedition", {
                    "id": eid, "distance_m": summary.get("distance_m",0),
                    "ap_unique": summary.get("ap_unique",0),
                    "captures_delta": summary.get("captures_delta",0),
                    "xp_delta": summary.get("xp_delta",0),
                    "reason": "core_stop",
                })
        except Exception:
            log.exception("could not checkpoint expedition")
        await self.action_server.stop()
        await self.api.stop()
        self.store.close()

    def stop(self) -> None:
        self.stop_event.set()
