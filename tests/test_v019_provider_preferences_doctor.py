import os

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.doctor import BeastDoctor
from beastcore.events import EventBus
from beastcore.provider_arbitration import CapabilityProviderArbitrator
from beastcore.provider_preferences import ProviderPreferenceManager
from beastcore.state import StateRegistry


def test_provider_preferences_persist_privately_and_publish_flat_state(tmp_path):
    path = tmp_path / "provider-preferences.json"
    mgr = ProviderPreferenceManager(str(path), clock=lambda: 100.0)

    assert mgr.snapshot()["values"] == {}
    row = mgr.set("location.position", "component:pwndroid", actor="owner")
    assert row["values"] == {"location.position": "component:pwndroid"}
    assert row["preferences"]["location.position"]["set_at"] == 100.0
    assert (path.stat().st_mode & 0o777) == 0o600

    reloaded = ProviderPreferenceManager(str(path), clock=lambda: 200.0)
    assert reloaded.snapshot()["values"]["location.position"] == "component:pwndroid"
    patch = reloaded.state_patch()
    assert patch["providers.preferences"] == {"location.position": "component:pwndroid"}
    assert patch["providers.preference_count"] == 1

    cleared = reloaded.clear("location.position", actor="owner")
    assert cleared["values"] == {}


def test_provider_preference_action_requires_owner_authorized_operator_session(tmp_path):
    state = StateRegistry()
    store = Store(str(tmp_path / "beast.db"))
    events = EventBus()
    pref = ProviderPreferenceManager(str(tmp_path / "providers.json"), clock=lambda: 123.0)
    broker = ActionBroker(state, store, events, provider_preferences=pref)
    broker.operator_sessions.path = tmp_path / "operator-session.json"
    try:
        blocked = broker.plan(
            "provider.preference_set",
            {"capability": "location.position", "provider": "component:pwndroid"},
        )
        assert blocked["allowed"] is False
        assert "active operator session required" in blocked["blockers"]

        broker.operator_sessions.authorize("operator", 300, actor="owner")
        plan = broker.plan(
            "provider.preference_set",
            {"capability": "location.position", "provider": "component:pwndroid"},
        )
        assert plan["allowed"] is True
        assert plan["selection_mutation_enabled"] is False
        assert plan["automatic_failover_enabled"] is False
        assert any("dormant" in text for text in plan["warnings"])

        row = broker.perform(
            "provider.preference_set",
            {"capability": "location.position", "provider": "component:pwndroid"},
            actor="owner",
        )
        assert row["status"] == "success"
        assert row["target"] == "location.position"
        assert row["result"]["provider_switched"] is False
        assert state.get("providers.preferences") == {"location.position": "component:pwndroid"}

        saved = store.recent_actions(10)
        assert any(x["action"] == "provider.preference_set" and x["target"] == "location.position" for x in saved)
        assert store.search_events("provider.preference.changed", 10)

        cleared = broker.perform(
            "provider.preference_clear",
            {"capability": "location.position"},
            actor="owner",
        )
        assert cleared["status"] == "success"
        assert state.get("providers.preferences") == {}
    finally:
        store.close()


def test_provider_preference_can_be_saved_for_temporarily_unavailable_provider(tmp_path):
    state = StateRegistry()
    state.update_many(
        "plugin_integration",
        {
            "plugins.provider_decisions": {
                "location.position": {
                    "candidates": [
                        {"provider": "native:gps", "ready": True},
                        {"provider": "component:pwndroid", "ready": False},
                    ]
                }
            }
        },
    )
    store = Store(str(tmp_path / "beast.db"))
    events = EventBus()
    pref = ProviderPreferenceManager(str(tmp_path / "providers.json"))
    broker = ActionBroker(state, store, events, provider_preferences=pref)
    broker.operator_sessions.path = tmp_path / "operator-session.json"
    try:
        broker.operator_sessions.authorize("operator", 300, actor="owner")
        plan = broker.plan(
            "provider.preference_set",
            {"capability": "location.position", "provider": "component:pwndroid"},
        )
        assert plan["allowed"] is True
        assert "component:pwndroid" in plan["known_candidates"]
        row = broker.perform(
            "provider.preference_set",
            {"capability": "location.position", "provider": "component:pwndroid"},
            actor="owner",
        )
        assert row["status"] == "success"
        assert row["result"]["provider_switched"] is False
    finally:
        store.close()


def test_native_provider_health_uses_canonical_state_metadata():
    state = StateRegistry()
    state.update_many("gps", {"gps.state": "fixed"}, priority=70)
    arbitration = CapabilityProviderArbitrator(state).evaluate(
        [],
        {
            "components": {},
            "providers": {"location.position": ["native:gps"]},
        },
    )
    decision = arbitration["decisions"]["location.position"]
    candidate = decision["candidates"][0]

    assert decision["active_provider"] == "native:gps"
    assert decision["active_health"] == "healthy"
    assert decision["active_confidence"] == "high"
    assert isinstance(decision["active_freshness_sec"], float)
    assert candidate["evidence_quality"] == "live"


def test_beast_doctor_explains_provider_reason_alternates_and_downstream_impact():
    state = StateRegistry()
    state.update_many(
        "plugin_integration",
        {
            "plugins.provider_decisions": {
                "location.position": {
                    "capability": "location.position",
                    "state": "active_native",
                    "active_provider": "native:gps",
                    "recommended_provider": "native:gps",
                    "owner_preference": None,
                    "preference_issue": None,
                    "reason": "canonical/native provider is already live and is preferred for canonical truth",
                    "alternates": ["component:pwndroid"],
                    "fallback_chain": ["native:gps", "component:pwndroid"],
                    "choice_required": False,
                    "active_health": "healthy",
                    "active_confidence": "high",
                    "active_freshness_sec": 1.2,
                    "automatic_failover_enabled": False,
                    "candidates": [
                        {
                            "provider": "native:gps",
                            "ready": True,
                            "selected": True,
                            "health_state": "healthy",
                            "confidence": "high",
                        },
                        {
                            "provider": "component:pwndroid",
                            "ready": True,
                            "selected": False,
                            "health_state": "standby_ready",
                            "confidence": "low",
                            "technical_blockers": [],
                            "policy_blockers": [],
                        },
                    ],
                }
            },
            "plugins.requirements_used_by": {
                "native:gps": ["webgpsmap"],
            },
            "plugins.provider_summary": {"active_count": 1},
            "plugins.requirements_summary": {"active_technical_blocker_count": 0},
        },
        priority=80,
    )
    state.update_many(
        "packs",
        {
            "packs.requirements_used_by": {"native:gps": ["expedition-map"]},
            "packs.requirements_summary": {"active_technical_blocker_count": 0},
        },
        priority=70,
    )

    doctor = BeastDoctor(state)
    explain = doctor.explain_capability("location.position")

    assert explain["found"] is True
    assert explain["active_provider"] == "native:gps"
    assert explain["active_confidence"] == "high"
    assert explain["used_by"]["plugins"] == ["webgpsmap"]
    assert explain["used_by"]["packs"] == ["expedition-map"]
    assert explain["dependent_count"] == 2
    assert explain["if_active_provider_is_lost"]["automatic_failover_enabled"] is False
    assert explain["alternates"][0]["provider"] == "component:pwndroid"
    assert explain["recommendations"] == ["No provider action is currently required."]


def test_beast_doctor_surfaces_choice_required_without_making_choice():
    state = StateRegistry()
    state.update_many(
        "plugin_integration",
        {
            "plugins.provider_decisions": {
                "power.battery.telemetry": {
                    "state": "choice_required",
                    "active_provider": None,
                    "recommended_provider": "component:pisugarx",
                    "choice_required": True,
                    "reason": "multiple selected ready providers exist and no explicit preference resolves them",
                    "candidates": [],
                }
            },
            "plugins.provider_summary": {"choice_required_count": 1},
            "plugins.requirements_summary": {"active_technical_blocker_count": 0},
        },
    )
    state.update_many("packs", {"packs.requirements_summary": {"active_technical_blocker_count": 0}})

    doctor = BeastDoctor(state)
    snap = doctor.snapshot()
    explain = doctor.explain_capability("power.battery.telemetry")

    assert snap["state"] == "attention"
    assert snap["attention_count"] == 1
    assert snap["items"][0]["capability"] == "power.battery.telemetry"
    assert explain["active_provider"] is None
    assert any("Choose a preferred provider" in x for x in explain["recommendations"])
