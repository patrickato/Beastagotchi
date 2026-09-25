from __future__ import annotations

import copy
import hashlib
import json
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

    @staticmethod
    def _incident_recurrence(rows: list[dict[str, Any]]) -> dict[str, Any]:
        severity_rank = {"critical": 3, "warning": 2, "warn": 2, "info": 1}
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            kind = str(row.get("kind") or "").strip()
            if not kind:
                continue
            opened = float(row.get("opened_at") or 0.0)
            last_seen = float(row.get("last_seen") or opened or 0.0)
            resolved = row.get("resolved_at")
            status = str(row.get("status") or "unknown")
            severity = str(row.get("severity") or "warning").lower()
            item = grouped.setdefault(kind, {
                "episodes": 0,
                "active": False,
                "first_seen": opened or None,
                "last_seen": last_seen or None,
                "last_resolved": None,
                "severity": severity,
                "latest_summary": str(row.get("summary") or kind),
            })
            item["episodes"] += 1
            item["active"] = bool(item["active"] or status == "open")
            if opened and (item["first_seen"] is None or opened < item["first_seen"]):
                item["first_seen"] = opened
            if last_seen and (item["last_seen"] is None or last_seen > item["last_seen"]):
                item["last_seen"] = last_seen
                item["latest_summary"] = str(row.get("summary") or kind)
            try:
                resolved_f = float(resolved) if resolved is not None else None
            except (TypeError, ValueError):
                resolved_f = None
            if resolved_f is not None and (
                item["last_resolved"] is None or resolved_f > item["last_resolved"]
            ):
                item["last_resolved"] = resolved_f
            if severity_rank.get(severity, 0) > severity_rank.get(str(item["severity"]).lower(), 0):
                item["severity"] = severity
        ordered = sorted(
            grouped.items(),
            key=lambda pair: float(pair[1].get("last_seen") or 0.0),
            reverse=True,
        )[:64]
        out: dict[str, Any] = {}
        for kind, item in ordered:
            item["recurrent"] = int(item.get("episodes", 0) or 0) >= 2
            out[kind] = item
        return out

    def refresh_recurrence(self) -> bool:
        if self.store is None or not hasattr(self.store, "recent_incidents"):
            return False
        try:
            recurrence = self._incident_recurrence(self.store.recent_incidents(200))
        except Exception as exc:
            self.load_error = repr(exc)
            return False
        if recurrence == self.data.get("recurrence"):
            return False
        self.data["recurrence"] = recurrence
        self.data["updated_at"] = float(self.clock())
        self._persist()
        return True

    @staticmethod
    def _fingerprint_hash(fingerprint: dict[str, Any]) -> str:
        payload = json.dumps(fingerprint or {}, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _checkpoint_meta(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if not isinstance(row, dict):
            return None
        return {
            "id": row.get("id"),
            "saved_at": row.get("saved_at"),
            "label": row.get("label"),
            "sha256": row.get("sha256"),
        }

    def save_known_good(
        self,
        fingerprint: dict[str, Any],
        *,
        label: str = "owner",
        now: float | None = None,
    ) -> dict[str, Any]:
        fingerprint = copy.deepcopy(fingerprint or {})
        digest = self._fingerprint_hash(fingerprint)
        rows = list(self.data.get("known_good") or [])
        latest = rows[-1] if rows else None
        if isinstance(latest, dict) and latest.get("sha256") == digest:
            return {
                "saved": False,
                "reason": "unchanged",
                "checkpoint": self._checkpoint_meta(latest),
            }
        ts = float(self.clock() if now is None else now)
        row = {
            "id": f"kg-{int(ts * 1000)}-{digest[:12]}",
            "saved_at": ts,
            "label": str(label or "owner")[:80],
            "sha256": digest,
            "fingerprint": fingerprint,
        }
        rows.append(row)
        self.data["known_good"] = rows[-self.max_known_good:]
        self.data["updated_at"] = ts
        self._persist()
        return {
            "saved": True,
            "reason": "created",
            "checkpoint": self._checkpoint_meta(row),
        }

    def known_good_history(self) -> list[dict[str, Any]]:
        return [
            meta for meta in (
                self._checkpoint_meta(row)
                for row in reversed(self.data.get("known_good") or [])
            )
            if meta is not None
        ]

    def latest_known_good(self) -> dict[str, Any] | None:
        rows = self.data.get("known_good") or []
        return copy.deepcopy(rows[-1]) if rows else None

    def diff_known_good(self, current: dict[str, Any]) -> dict[str, Any]:
        latest = self.latest_known_good()
        if latest is None:
            return {
                "found": False,
                "changed": False,
                "change_count": 0,
                "changes": {},
                "checkpoint": None,
            }
        before = latest.get("fingerprint") if isinstance(latest.get("fingerprint"), dict) else {}
        after = copy.deepcopy(current or {})
        keys = sorted(set(before) | set(after))
        changes = {
            key: {"before": copy.deepcopy(before.get(key)), "after": copy.deepcopy(after.get(key))}
            for key in keys
            if before.get(key) != after.get(key)
        }
        return {
            "found": True,
            "changed": bool(changes),
            "change_count": len(changes),
            "changes": changes,
            "checkpoint": self._checkpoint_meta(latest),
        }

    def summary(self) -> dict[str, Any]:
        return copy.deepcopy({
            "schema": self.data.get("schema", self.SCHEMA),
            "identity": self.data.get("identity") or {},
            "coverage": self.data.get("coverage") or {},
            "recurrence": self.data.get("recurrence") or {},
            "known_good_count": len(self.data.get("known_good") or []),
            "known_good_latest": self._checkpoint_meta(
                (self.data.get("known_good") or [])[-1]
                if self.data.get("known_good") else None
            ),
            "updated_at": self.data.get("updated_at"),
            "load_error": self.load_error,
        })
