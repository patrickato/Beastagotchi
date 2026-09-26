from __future__ import annotations

import re
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable, Generic, Iterable, Mapping, TypeVar


T = TypeVar("T")

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,126}$")
_TRUST_RANK = {
    "catalog": 0,
    "unverified": 1,
    "verified_declarative": 2,
    "trusted_executable": 3,
    "project": 4,
    "core": 5,
}


class RegistryError(ValueError):
    pass


class RegistryFrozenError(RegistryError):
    pass


class DuplicateSpecError(RegistryError):
    pass


class StaleRegistryCandidateError(RegistryError):
    pass


@dataclass(frozen=True)
class SpecMetadata:
    id: str
    schema_version: int = 1
    definition_version: str = "1"
    source: str = "core"
    namespace_owner: str = "core"
    trust_tier: str = "core"
    compatibility: Mapping[str, Any] = field(default_factory=dict)
    deprecated: bool = False
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        clean = str(self.id or "").strip()
        if not _ID_RE.fullmatch(clean):
            raise RegistryError(f"invalid registry id: {self.id!r}")
        object.__setattr__(self, "id", clean)
        if int(self.schema_version) < 1:
            raise RegistryError("schema_version must be >= 1")
        tier = str(self.trust_tier or "").strip()
        if tier not in _TRUST_RANK:
            raise RegistryError(f"unknown trust tier: {tier}")
        object.__setattr__(self, "trust_tier", tier)


@dataclass(frozen=True)
class RegistryCandidate(Generic[T]):
    kind: str
    base_generation: int
    items: tuple[T, ...]


class TypedRegistry(Generic[T]):
    """Small shared mechanics for Beast typed registries.

    The registry knows identity, source/trust metadata, deterministic ordering,
    generations and atomic candidate replacement. Domain semantics live in the
    typed registry/spec classes rather than in this generic substrate.
    """

    def __init__(
        self,
        kind: str,
        *,
        metadata: Callable[[T], SpecMetadata],
        serializer: Callable[[T], Mapping[str, Any]] | None = None,
    ) -> None:
        self.kind = str(kind or "registry")
        self._metadata = metadata
        self._serializer = serializer
        self._items: dict[str, T] = {}
        self._generation = 0
        self._frozen = False
        self._lock = RLock()

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def frozen(self) -> bool:
        with self._lock:
            return self._frozen

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)

    def ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._items))

    def get(self, spec_id: str) -> T:
        key = str(spec_id or "").strip()
        with self._lock:
            try:
                return self._items[key]
            except KeyError as exc:
                raise RegistryError(f"unknown {self.kind} id: {key}") from exc

    def maybe_get(self, spec_id: str) -> T | None:
        with self._lock:
            return self._items.get(str(spec_id or "").strip())

    def _check_replacement(self, old: T, new: T) -> None:
        old_meta = self._metadata(old)
        new_meta = self._metadata(new)
        if _TRUST_RANK[new_meta.trust_tier] < _TRUST_RANK[old_meta.trust_tier]:
            raise RegistryError(
                f"{self.kind} {old_meta.id} trust downgrade "
                f"{old_meta.trust_tier}->{new_meta.trust_tier} is not allowed"
            )
        if old_meta.namespace_owner != new_meta.namespace_owner and new_meta.trust_tier != "core":
            raise RegistryError(
                f"{self.kind} {old_meta.id} namespace owner change requires core authority"
            )

    def register(self, item: T, *, replace: bool = False) -> T:
        meta = self._metadata(item)
        with self._lock:
            if self._frozen:
                raise RegistryFrozenError(
                    f"{self.kind} registry is frozen; use a candidate activation"
                )
            existing = self._items.get(meta.id)
            if existing is not None and not replace:
                raise DuplicateSpecError(f"duplicate {self.kind} id: {meta.id}")
            if existing is not None:
                self._check_replacement(existing, item)
            self._items[meta.id] = item
            self._generation += 1
            return item

    def freeze(self) -> int:
        with self._lock:
            self._frozen = True
            return self._generation

    def build_candidate(self, items: Iterable[T], *, merge: bool = False) -> RegistryCandidate[T]:
        with self._lock:
            candidate: dict[str, T] = dict(self._items) if merge else {}
            base_generation = self._generation
            incoming_ids: set[str] = set()
            for item in items:
                meta = self._metadata(item)
                if meta.id in incoming_ids:
                    raise DuplicateSpecError(f"duplicate {self.kind} id in candidate: {meta.id}")
                incoming_ids.add(meta.id)
                existing = candidate.get(meta.id)
                if existing is not None:
                    # merge=True may intentionally replace an already-active id,
                    # but replacement still obeys trust/namespace protection.
                    if not merge or meta.id not in self._items:
                        raise DuplicateSpecError(f"duplicate {self.kind} id in candidate: {meta.id}")
                    self._check_replacement(existing, item)
                candidate[meta.id] = item
            return RegistryCandidate(
                kind=self.kind,
                base_generation=base_generation,
                items=tuple(candidate[k] for k in sorted(candidate)),
            )

    def activate_candidate(self, candidate: RegistryCandidate[T]) -> int:
        if candidate.kind != self.kind:
            raise RegistryError(
                f"candidate kind {candidate.kind!r} does not match registry {self.kind!r}"
            )
        with self._lock:
            if candidate.base_generation != self._generation:
                raise StaleRegistryCandidateError(
                    f"stale {self.kind} candidate: base={candidate.base_generation} "
                    f"active={self._generation}"
                )
            new_items: dict[str, T] = {}
            for item in candidate.items:
                meta = self._metadata(item)
                if meta.id in new_items:
                    raise DuplicateSpecError(f"duplicate {self.kind} id in candidate: {meta.id}")
                old = self._items.get(meta.id)
                if old is not None:
                    self._check_replacement(old, item)
                new_items[meta.id] = item
            self._items = new_items
            self._generation += 1
            self._frozen = True
            return self._generation

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            rows = []
            for key in sorted(self._items):
                item = self._items[key]
                meta = self._metadata(item)
                row: dict[str, Any] = {
                    "id": meta.id,
                    "schema_version": meta.schema_version,
                    "definition_version": meta.definition_version,
                    "source": meta.source,
                    "namespace_owner": meta.namespace_owner,
                    "trust_tier": meta.trust_tier,
                    "compatibility": dict(meta.compatibility),
                    "deprecated": bool(meta.deprecated),
                    "superseded_by": meta.superseded_by,
                }
                if self._serializer is not None:
                    row.update(dict(self._serializer(item)))
                rows.append(row)
            return {
                "kind": self.kind,
                "generation": self._generation,
                "frozen": self._frozen,
                "count": len(rows),
                "items": rows,
            }
