from __future__ import annotations

import copy
import time
from typing import Any


class DoctorPatientChart:
    """Compact durable Beast Doctor memory.

    Detailed incidents remain owned by IncidentEngine/Store. This chart keeps only
    privacy-light identity, diagnostic coverage, recurrence summaries and bounded
    known-good fingerprints. Writes occur only when the compact chart changes.
    """

    SCHEMA = 1
    META_KEY = "doctor.patient.v1"

    @classmethod
    def blank(cls) -> dict[str, Any]:
        return {
            "schema": cls.SCHEMA,
            "identity": {},
            "coverage": {},
            "recurrence": {},
            "known_good": [],
            "updated_at": None,
        }

    def __init__(self, store=None, *, clock=time.time, max_known_good: int = 5) -> None:
        self.store = store
        self.clock = clock
        self.max_known_good = max(1, min(int(max_known_good), 20))
        self.data = self.blank()
        self.load_error: str | None = None
        self._load()

    def _load(self) -> None:
        if self.store is None:
            return
        try:
            raw = self.store.get_meta_json(self.META_KEY, None)
            if not isinstance(raw, dict):
                return
            if int(raw.get("schema", self.SCHEMA)) != self.SCHEMA:
                self.load_error = f"unsupported patient schema {raw.get('schema')}"
                return
            merged = self.blank()
            for key in merged:
                if key in raw:
                    merged[key] = copy.deepcopy(raw[key])
            self.data = merged
        except Exception as exc:
            self.load_error = repr(exc)

    def _persist(self) -> bool:
        if self.store is None:
            return False
        return bool(self.store.set_meta_json(self.META_KEY, self.data))

    def observe_identity_coverage(
        self,
        identity: dict[str, Any],
        coverage: dict[str, Any],
        *,
        now: float | None = None,
    ) -> bool:
        changed = False
        identity = copy.deepcopy(identity or {})
        coverage = copy.deepcopy(coverage or {})
        if identity != self.data.get("identity"):
            self.data["identity"] = identity
            changed = True
        if coverage != self.data.get("coverage"):
            self.data["coverage"] = coverage
            changed = True
        if changed:
            self.data["updated_at"] = float(self.clock() if now is None else now)
            self._persist()
        return changed

    def summary(self) -> dict[str, Any]:
        return copy.deepcopy({
            "schema": self.data.get("schema", self.SCHEMA),
            "identity": self.data.get("identity") or {},
            "coverage": self.data.get("coverage") or {},
            "recurrence": self.data.get("recurrence") or {},
            "known_good_count": len(self.data.get("known_good") or []),
            "known_good_latest": (self.data.get("known_good") or [])[-1]
            if self.data.get("known_good") else None,
            "updated_at": self.data.get("updated_at"),
            "load_error": self.load_error,
        })
