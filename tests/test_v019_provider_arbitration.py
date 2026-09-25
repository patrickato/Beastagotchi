from beastcore.dependency_resolver import DependencyCapabilityResolver
from beastcore.provider_arbitration import CapabilityProviderArbitrator


class _S:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def _resolution(state, components):
    return DependencyCapabilityResolver(
        state,
        which=lambda name: "/usr/bin/systemctl" if name == "systemctl" else None,
        path_exists=lambda path: False,
    ).resolve_components(components)


def test_native_provider_wins_when_live_and_no_owner_preference():
    state = _S({"gps.state": "fixed"})
    components = [
        {
            "id": "pwndroid",
            "available": True,
            "selected": True,
            "integration": "config_only",
            "provides": ["location.position"],
            "requires": [],
        }
    ]
    graph = _resolution(state, components)
    decision = graph["arbitration"]["decisions"]["location.position"]

    assert decision["state"] == "active_native"
    assert decision["active_provider"] == "native:gps"
    assert "component:pwndroid" in decision["alternates"]
    assert decision["automatic_failover_enabled"] is False
    assert decision["selection_mutation_enabled"] is False


def test_explicit_owner_preference_can_choose_ready_component_over_native():
    state = _S({
        "gps.state": "fixed",
        "providers.preferences": {"location.position": "component:pwndroid"},
    })
    components = [
        {
            "id": "pwndroid",
            "available": True,
            "selected": True,
            "integration": "config_only",
            "provides": ["location.position"],
            "requires": [],
        }
    ]
    graph = _resolution(state, components)
    decision = graph["arbitration"]["decisions"]["location.position"]

    assert decision["state"] == "active_preference"
    assert decision["active_provider"] == "component:pwndroid"
    assert decision["owner_preference"] == "component:pwndroid"
    assert "native:gps" in decision["alternates"]


def test_multiple_selected_non_native_providers_require_choice():
    state = _S({})
    components = [
        {
            "id": "provider-a",
            "available": True,
            "selected": True,
            "integration": "adapter",
            "provides": ["custom.capability"],
            "requires": [],
        },
        {
            "id": "provider-b",
            "available": True,
            "selected": True,
            "integration": "managed",
            "provides": ["custom.capability"],
            "requires": [],
        },
    ]
    graph = _resolution(state, components)
    decision = graph["arbitration"]["decisions"]["custom.capability"]

    assert decision["state"] == "choice_required"
    assert decision["active_provider"] is None
    assert decision["recommended_provider"] == "component:provider-a"
    assert decision["selected_ready_count"] == 2
    assert graph["arbitration"]["summary"]["choice_required_count"] == 1


def test_available_but_unselected_provider_is_not_silently_activated():
    state = _S({})
    components = [
        {
            "id": "optional-provider",
            "available": True,
            "selected": False,
            "integration": "adapter",
            "provides": ["custom.capability"],
            "requires": [],
        }
    ]
    graph = _resolution(state, components)
    decision = graph["arbitration"]["decisions"]["custom.capability"]

    assert decision["state"] == "available_unselected"
    assert decision["active_provider"] is None
    assert decision["recommended_provider"] == "component:optional-provider"
    assert decision["fallback_chain"] == ["component:optional-provider"]


def test_unavailable_owner_preference_falls_back_to_live_native_provider():
    state = _S({
        "gps.state": "connected_no_fix",
        "providers.preferences": {"location.position": "component:missing-provider"},
    })
    graph = _resolution(state, [])
    decision = graph["arbitration"]["decisions"]["location.position"]

    assert decision["state"] == "active_fallback"
    assert decision["active_provider"] == "native:gps"
    assert "not currently ready/available" in decision["preference_issue"]
    assert graph["arbitration"]["summary"]["preference_problem_count"] == 1


def test_unready_component_is_not_considered_viable_provider():
    state = _S({
        "platform.services": [
            {"unit": "gpsd.service", "load": "loaded", "active": "inactive", "sub": "dead"}
        ]
    })
    components = [
        {
            "id": "gps-provider",
            "available": True,
            "selected": True,
            "integration": "adapter",
            "provides": ["location.position"],
            "requires": ["gpsd.service"],
        }
    ]
    graph = _resolution(state, components)
    decision = graph["arbitration"]["decisions"]["location.position"]

    assert decision["state"] == "unavailable"
    assert decision["ready_candidate_count"] == 0
    assert decision["candidates"][0]["technical_blockers"] == ["gpsd.service"]
