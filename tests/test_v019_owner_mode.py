import json
import tarfile

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.events import EventBus
from beastcore.owner_mode import OwnerModeManager
from beastcore.state import StateRegistry


class _FakePluginBroker:
    def plan_toggle(self, name, enabled, *, beast_ui_active=None, owner_override=False, expert_mode=False):
        policy = ["test policy blocker"]
        executed = bool(owner_override and expert_mode)
        return {
            "plugin": name,
            "requested_enabled": bool(enabled),
            "technical_blockers": [],
            "policy_blockers": policy,
            "overridden_policy_blockers": list(policy) if executed else [],
            "owner_override_available": True,
            "owner_override_requested": bool(owner_override),
            "owner_override_executed": executed,
            "managed_allowed": False,
            "blockers": [] if executed else list(policy),
            "warnings": [],
            "allowed": executed,
            "no_change": False,
        }

    def toggle(self, name, enabled, *, restart=True, observe_seconds=2.0, owner_override=False, expert_mode=False):
        plan = self.plan_toggle(
            name,
            enabled,
            owner_override=owner_override,
            expert_mode=expert_mode,
        )
        if not plan["allowed"]:
            from beastcore.plugin_broker import PluginBrokerError
            raise PluginBrokerError("; ".join(plan["blockers"]))
        return {
            "ok": True,
            "changed": True,
            "rolled_back": False,
            "final_enabled": bool(enabled),
            "plan": plan,
        }


def _broker(tmp_path):
    state = StateRegistry()
    store = Store(str(tmp_path / "beast.db"))
    events = EventBus()
    owner = OwnerModeManager(str(tmp_path / "owner-mode.json"), clock=lambda: 1000.0)
    broker = ActionBroker(
        state,
        store,
        events,
        plugin_broker=_FakePluginBroker(),
        owner_mode=owner,
    )
    broker.operator_sessions.path = tmp_path / "operator-session.json"
    return state, store, events, owner, broker


def test_owner_mode_persists_expert_state_and_customization(tmp_path):
    path = tmp_path / "owner-mode.json"
    manager = OwnerModeManager(str(path), clock=lambda: 10.0)

    assert manager.snapshot()["support_state"] == "managed"
    row = manager.set_expert(True, actor="owner")
    assert row["expert_mode_enabled"] is True
    assert row["support_state"] == "expert"
    assert path.exists()
    assert (path.stat().st_mode & 0o777) == 0o600

    again = OwnerModeManager(str(path), clock=lambda: 20.0)
    assert again.snapshot()["expert_mode_enabled"] is True

    row = again.record_override(
        action="plugin.toggle",
        target="theme_manager",
        actor="owner",
        policy_blockers=["display conflict"],
    )
    assert row["customized"] is True
    assert row["support_state"] == "customized"
    assert row["override_count"] == 1
    assert row["last_override_target"] == "theme_manager"

    row = again.set_expert(False, actor="owner")
    assert row["expert_mode_enabled"] is False
    assert row["support_state"] == "customized"


def test_expert_mode_change_requires_active_administrator_session(tmp_path):
    state, store, events, owner, broker = _broker(tmp_path)
    try:
        blocked = broker.plan("owner.expert_mode_set", {"enabled": True})
        assert blocked["allowed"] is False
        assert blocked["blockers"] == ["active administrator session required"]

        broker.operator_sessions.authorize("administrator", 300, actor="owner")
        plan = broker.plan("owner.expert_mode_set", {"enabled": True})
        assert plan["allowed"] is True

        row = broker.perform("owner.expert_mode_set", {"enabled": True}, actor="owner")
        assert row["status"] == "success"
        assert owner.snapshot()["expert_mode_enabled"] is True
        assert state.get("owner.expert_mode.enabled") is True
        assert state.get("owner.support_state") == "expert"
    finally:
        store.close()


def test_successful_owner_override_marks_installation_customized_and_audited(tmp_path):
    state, store, events, owner, broker = _broker(tmp_path)
    try:
        broker.operator_sessions.authorize("administrator", 300, actor="owner")
        enabled = broker.perform("owner.expert_mode_set", {"enabled": True}, actor="owner")
        assert enabled["status"] == "success"

        plan = broker.plan(
            "plugin.toggle",
            {"name": "theme_manager", "enabled": True, "owner_override": True},
        )
        assert plan["owner_override_executed"] is True
        assert plan["allowed"] is True

        row = broker.perform(
            "plugin.toggle",
            {"name": "theme_manager", "enabled": True, "owner_override": True},
            actor="owner",
        )
        assert row["status"] == "success"
        assert row["result"]["plan"]["owner_override_executed"] is True

        mode = owner.snapshot()
        assert mode["customized"] is True
        assert mode["override_count"] == 1
        assert mode["last_override_action"] == "plugin.toggle"
        assert mode["last_override_target"] == "theme_manager"
        assert state.get("owner.support_state") == "customized"

        recent = store.recent_actions(10)
        assert any(x["action"] == "plugin.toggle" and x["status"] == "success" for x in recent)
        events_seen = store.search_events("owner.override.used", 10)
        assert events_seen
    finally:
        store.close()


def test_owner_override_without_expert_mode_remains_blocked(tmp_path):
    state, store, events, owner, broker = _broker(tmp_path)
    try:
        plan = broker.plan(
            "plugin.toggle",
            {"name": "theme_manager", "enabled": True, "owner_override": True},
        )
        assert plan["owner_override_available"] is True
        assert plan["owner_override_executed"] is False
        assert plan["allowed"] is False

        row = broker.perform(
            "plugin.toggle",
            {"name": "theme_manager", "enabled": True, "owner_override": True},
            actor="owner",
        )
        assert row["status"] == "blocked"
        assert owner.snapshot()["customized"] is False
    finally:
        store.close()

def test_support_bundle_reports_expert_and_customized_state_without_secrets(tmp_path):
    from beastcore.support_bundle import SupportBundleManager

    state = StateRegistry()
    state.update_many(
        "owner_mode",
        {
            "owner.expert_mode.enabled": True,
            "owner.customized": True,
            "owner.override_count": 3,
            "owner.support_state": "customized",
            "owner.last_override.action": "plugin.toggle",
            "owner.last_override.target": "theme_manager",
        },
        priority=99,
    )
    store = Store(str(tmp_path / "support.db"))
    try:
        mgr = SupportBundleManager(state, store, root=str(tmp_path / "support"))
        made = mgr.create()
        assert made["ok"] is True
        with tarfile.open(made["path"], "r:gz") as tf:
            manifest = json.load(tf.extractfile("beast-support/manifest.json"))
            safe_state = json.load(tf.extractfile("beast-support/state.json"))
        assert manifest["support_state"] == "customized"
        assert manifest["expert_mode_enabled"] is True
        assert manifest["customized"] is True
        assert safe_state["owner.override_count"] == 3
        assert safe_state["owner.last_override.target"] == "theme_manager"
    finally:
        store.close()

