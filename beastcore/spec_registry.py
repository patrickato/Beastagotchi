from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .registry import RegistryError, SpecMetadata, TypedRegistry


PlanFn = Callable[[dict[str, Any]], dict[str, Any]]
PerformFn = Callable[[dict[str, Any], str], dict[str, Any]]


@dataclass(frozen=True)
class ActionSpec:
    meta: SpecMetadata
    planner: PlanFn | None = None
    performer: PerformFn | None = None
    authority: str = "operator"
    risk: str = "C1"
    mutation: str = "managed"
    verification: str = "handler"
    target_hint: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignalSpec:
    meta: SpecMetadata
    value_type: str = "unknown"
    category: str | None = None
    unit: str | None = None
    privacy: str = "local"
    publication: str = "never"
    freshness_sec: float | None = None
    history_supported: bool = False
    provider_semantics: str = "canonical_state"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventSpec:
    meta: SpecMetadata
    severity_default: str = "info"
    privacy: str = "local"
    durability: str = "durable"
    transient: bool = False
    payload_schema: Mapping[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()


_PRIVACY_RANK = {
    "public": 0,
    "local": 1,
    "profile": 2,
    "activity": 2,
    "local_system": 2,
    "local_operational": 3,
    "peer_identity": 3,
    "sensitive_location": 4,
    "sensitive_capture": 5,
    "secret": 6,
}


class ActionSpecRegistry(TypedRegistry[ActionSpec]):
    def __init__(self) -> None:
        super().__init__(
            "action",
            metadata=lambda item: item.meta,
            serializer=lambda item: {
                "authority": item.authority,
                "risk": item.risk,
                "mutation": item.mutation,
                "verification": item.verification,
                "target_hint": item.target_hint,
                "tags": list(item.tags),
                "planner_registered": item.planner is not None,
                "performer_registered": item.performer is not None,
            },
        )

    def plan(self, action_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        spec = self.get(action_id)
        if spec.planner is None:
            raise RegistryError(f"action {action_id} has no registered planner")
        return spec.planner(dict(payload or {}))

    def perform(self, action_id: str, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        spec = self.get(action_id)
        if spec.performer is None:
            raise RegistryError(f"action {action_id} has no registered performer")
        return spec.performer(dict(payload or {}), str(actor))


class SignalSpecRegistry(TypedRegistry[SignalSpec]):
    def __init__(self) -> None:
        super().__init__(
            "signal",
            metadata=lambda item: item.meta,
            serializer=lambda item: {
                "value_type": item.value_type,
                "category": item.category,
                "unit": item.unit,
                "privacy": item.privacy,
                "publication": item.publication,
                "freshness_sec": item.freshness_sec,
                "history_supported": bool(item.history_supported),
                "provider_semantics": item.provider_semantics,
                "tags": list(item.tags),
            },
        )

    def _check_replacement(self, old: SignalSpec, new: SignalSpec) -> None:
        super()._check_replacement(old, new)
        old_rank = _PRIVACY_RANK.get(old.privacy, 99)
        new_rank = _PRIVACY_RANK.get(new.privacy, 99)
        if new_rank < old_rank:
            raise RegistryError(
                f"signal {old.meta.id} privacy downgrade {old.privacy}->{new.privacy} is not allowed"
            )


class EventSpecRegistry(TypedRegistry[EventSpec]):
    def __init__(self) -> None:
        super().__init__(
            "event",
            metadata=lambda item: item.meta,
            serializer=lambda item: {
                "severity_default": item.severity_default,
                "privacy": item.privacy,
                "durability": item.durability,
                "transient": bool(item.transient),
                "payload_schema": dict(item.payload_schema),
                "tags": list(item.tags),
            },
        )

    def _check_replacement(self, old: EventSpec, new: EventSpec) -> None:
        super()._check_replacement(old, new)
        old_rank = _PRIVACY_RANK.get(old.privacy, 99)
        new_rank = _PRIVACY_RANK.get(new.privacy, 99)
        if new_rank < old_rank:
            raise RegistryError(
                f"event {old.meta.id} privacy downgrade {old.privacy}->{new.privacy} is not allowed"
            )
