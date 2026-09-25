from __future__ import annotations

from typing import Any

from .doctor_patient import DoctorPatientChart


class BeastDoctor:
    """Read-only explanation/diagnostic layer over canonical Beast state."""

    schema = 1

    def __init__(self, state, store=None) -> None:
        self.state = state
        self.patient = DoctorPatientChart(store)

    @staticmethod
    def _norm(value: Any) -> str:
        return str(value or "").strip().lower().replace(" ", "_")

    def _observed(self, key: str) -> tuple[bool, Any]:
        marker = object()
        value = self.state.get(key, marker)
        return value is not marker, None if value is marker else value

    def patient_identity(self) -> dict[str, Any]:
        """Privacy-light technical identity for compatibility reasoning."""
        return {
            "model": self.state.get("system.model"),
            "architecture": self.state.get("system.architecture"),
            "kernel": self.state.get("system.kernel"),
            "python_version": self.state.get("system.python.version"),
            "os_id": self.state.get("system.os.id"),
            "os_version_id": self.state.get("system.os.version_id"),
            "os_build_id": self.state.get("system.os.build_id"),
            "pwnagotchi_version": self.state.get("pwnagotchi.version"),
        }

    def diagnostic_coverage(self) -> dict[str, Any]:
        """Report what Doctor can currently observe without implying health."""
        rows: list[dict[str, Any]] = []

        def add(area: str, keys: tuple[str, ...], *, unavailable_values: set[str] | None = None) -> None:
            seen: list[tuple[str, Any]] = []
            for key in keys:
                observed, value = self._observed(key)
                if observed:
                    seen.append((key, value))
            if not seen:
                status = "unknown"
                reason = "no diagnostic evidence is currently published"
            else:
                status = "covered"
                reason = "diagnostic evidence is available"
                unavailable = {str(x).lower() for x in (unavailable_values or set())}
                if unavailable and any(str(value).lower() in unavailable for _, value in seen):
                    status = "unavailable"
                    reason = "the subsystem or specialist probe reports unavailable"
            rows.append({
                "area": area,
                "status": status,
                "observed_keys": [key for key, _ in seen],
                "reason": reason,
            })

        add("system", ("system.kernel", "system.architecture", "system.temp.cpu_c"))
        add("storage", ("storage.root.readonly", "storage.root.used_pct", "storage.mounts"))
        add("display", ("display.framebuffers", "display.outputs"))
        add(
            "radio",
            ("radio.primary.state", "radio.primary.name", "radio.primary.supported_channels"),
            unavailable_values={"unavailable", "missing"},
        )
        add(
            "gps",
            ("gps.state", "gps.fix"),
            unavailable_values={"unavailable"},
        )
        add("power_telemetry", ("power.telemetry.available", "power.ups.state"))
        add("network", ("network.route.available", "network.interfaces"))
        add("pwnagotchi_service", ("pwnagotchi.service.state",))
        add("bettercap_service", ("bettercap.state", "bettercap.service.state"))
        add("plugins", ("plugins.requirements_summary", "plugins.provider_summary"))

        counts = {
            "covered": sum(1 for row in rows if row["status"] == "covered"),
            "unavailable": sum(1 for row in rows if row["status"] == "unavailable"),
            "unknown": sum(1 for row in rows if row["status"] == "unknown"),
        }
        return {
            "schema": 1,
            "count": len(rows),
            "counts": counts,
            "complete": counts["unknown"] == 0,
            "items": rows,
        }

    def _decisions(self) -> dict[str, dict[str, Any]]:
        raw = self.state.get("plugins.provider_decisions", {}) or {}
        return raw if isinstance(raw, dict) else {}

    def _used_by(self, provider: str) -> dict[str, list[str]]:
        plugin_map = self.state.get("plugins.requirements_used_by", {}) or {}
        pack_map = self.state.get("packs.requirements_used_by", {}) or {}
        plugins = list(plugin_map.get(provider) or []) if isinstance(plugin_map, dict) else []
        packs = list(pack_map.get(provider) or []) if isinstance(pack_map, dict) else []
        return {
            "plugins": sorted({str(x) for x in plugins}),
            "packs": sorted({str(x) for x in packs}),
        }

    @staticmethod
    def _candidate_map(decision: dict[str, Any]) -> dict[str, dict[str, Any]]:
        rows = decision.get("candidates") or []
        return {
            str(row.get("provider")): row
            for row in rows
            if isinstance(row, dict) and row.get("provider")
        }

    def explain_capability(self, capability: str) -> dict[str, Any]:
        cap = self._norm(capability)
        decision = self._decisions().get(cap)
        if not isinstance(decision, dict):
            return {
                "schema": self.schema,
                "found": False,
                "capability": cap,
                "summary": f"No provider decision is currently available for {cap or 'that capability'}.",
                "recommendations": ["Refresh capability inventory or inspect the dependency graph."],
            }

        active = decision.get("active_provider")
        candidates = self._candidate_map(decision)
        active_row = candidates.get(str(active)) if active else None
        used = self._used_by(str(active)) if active else {"plugins": [], "packs": []}
        dependents = sorted(set(used["plugins"] + used["packs"]))
        alternates = []
        for provider in list(decision.get("alternates") or []):
            row = candidates.get(str(provider), {})
            alternates.append({
                "provider": provider,
                "health_state": row.get("health_state"),
                "confidence": row.get("confidence"),
                "ready": bool(row.get("ready")),
                "selected": bool(row.get("selected")),
                "technical_blockers": list(row.get("technical_blockers") or []),
                "policy_blockers": list(row.get("policy_blockers") or []),
            })

        recommendations: list[str] = []
        if decision.get("choice_required"):
            recommendations.append("Choose a preferred provider; Beast will not silently collapse multiple selected providers.")
        if decision.get("preference_issue"):
            recommendations.append("Review the saved provider preference or restore the preferred provider.")
        if decision.get("state") == "unavailable":
            recommendations.append("Inspect requirements for the unavailable providers and satisfy a valid provider dependency.")
        if active_row and active_row.get("health_state") in {"stale", "degraded", "blocked", "needs_attention"}:
            recommendations.append("Inspect the active provider health before relying on it for a critical operation.")
        if not recommendations:
            recommendations.append("No provider action is currently required.")

        if active:
            summary = f"{cap} is using {active}: {decision.get('reason') or 'provider policy selected it'}."
        elif decision.get("choice_required"):
            summary = f"{cap} has multiple ready selected providers and requires an owner choice."
        elif decision.get("state") == "available_unselected":
            summary = f"{cap} has a ready provider available but none is currently selected."
        else:
            summary = f"{cap} currently has no ready active provider."

        return {
            "schema": self.schema,
            "found": True,
            "capability": cap,
            "state": decision.get("state"),
            "summary": summary,
            "active_provider": active,
            "active_health": decision.get("active_health"),
            "active_confidence": decision.get("active_confidence"),
            "active_freshness_sec": decision.get("active_freshness_sec"),
            "reason": decision.get("reason"),
            "owner_preference": decision.get("owner_preference"),
            "preference_issue": decision.get("preference_issue"),
            "recommended_provider": decision.get("recommended_provider"),
            "fallback_chain": list(decision.get("fallback_chain") or []),
            "alternates": alternates,
            "used_by": used,
            "dependent_count": len(dependents),
            "dependents": dependents,
            "if_active_provider_is_lost": {
                "affected_components": dependents,
                "ready_alternate_count": sum(1 for row in alternates if row.get("ready")),
                "automatic_failover_enabled": bool(decision.get("automatic_failover_enabled", False)),
                "effect": "dependent components may degrade or become unavailable until a provider is restored or selected",
            },
            "recommendations": recommendations,
        }

    def explain_provider(self, provider: str) -> dict[str, Any]:
        provider = str(provider or "").strip()
        capabilities: list[dict[str, Any]] = []
        for cap, decision in self._decisions().items():
            if not isinstance(decision, dict):
                continue
            candidate = next(
                (row for row in decision.get("candidates") or [] if isinstance(row, dict) and row.get("provider") == provider),
                None,
            )
            if candidate is None:
                continue
            capabilities.append({
                "capability": cap,
                "active": decision.get("active_provider") == provider,
                "decision_state": decision.get("state"),
                "health_state": candidate.get("health_state"),
                "confidence": candidate.get("confidence"),
                "ready": bool(candidate.get("ready")),
                "selected": bool(candidate.get("selected")),
                "used_by": self._used_by(provider),
                "technical_blockers": list(candidate.get("technical_blockers") or []),
                "policy_blockers": list(candidate.get("policy_blockers") or []),
            })
        return {
            "schema": self.schema,
            "found": bool(capabilities),
            "provider": provider,
            "capability_count": len(capabilities),
            "capabilities": capabilities,
        }

    def snapshot(self) -> dict[str, Any]:
        decisions = self._decisions()
        items: list[dict[str, Any]] = []
        for capability, decision in sorted(decisions.items()):
            if not isinstance(decision, dict):
                continue
            severity = None
            summary = None
            if decision.get("choice_required"):
                severity = "warning"
                summary = "Multiple ready providers require an owner choice."
            elif decision.get("preference_issue"):
                severity = "warning"
                summary = str(decision.get("preference_issue"))
            elif decision.get("state") == "unavailable":
                used = self._used_by(str(decision.get("active_provider") or ""))
                if used["plugins"] or used["packs"]:
                    severity = "warning"
                    summary = "No ready provider is available for a capability with known dependents."
            elif decision.get("active_health") in {"stale", "degraded", "blocked", "needs_attention"}:
                severity = "warning"
                summary = f"Active provider health is {decision.get('active_health')}."
            elif decision.get("active_confidence") == "low":
                severity = "info"
                summary = "Active provider evidence confidence is low."

            if severity and summary:
                items.append({
                    "kind": "provider",
                    "capability": capability,
                    "severity": severity,
                    "summary": summary,
                    "active_provider": decision.get("active_provider"),
                    "recommended_provider": decision.get("recommended_provider"),
                })

        plugin_summary = self.state.get("plugins.requirements_summary", {}) or {}
        pack_summary = self.state.get("packs.requirements_summary", {}) or {}
        if isinstance(plugin_summary, dict) and int(plugin_summary.get("active_technical_blocker_count", 0) or 0):
            items.append({
                "kind": "dependencies",
                "scope": "plugins",
                "severity": "warning",
                "summary": f"{int(plugin_summary.get('active_technical_blocker_count', 0) or 0)} active plugin technical blocker(s).",
            })
        if isinstance(pack_summary, dict) and int(pack_summary.get("active_technical_blocker_count", 0) or 0):
            items.append({
                "kind": "dependencies",
                "scope": "packs",
                "severity": "warning",
                "summary": f"{int(pack_summary.get('active_technical_blocker_count', 0) or 0)} active Pack technical blocker(s).",
            })

        items = items[:64]
        coverage = self.diagnostic_coverage()
        identity = self.patient_identity()
        self.patient.observe_identity_coverage(identity, coverage)
        patient_memory = self.patient.summary()
        return {
            "schema": self.schema,
            "state": "attention" if items else "ok",
            "attention_count": len(items),
            "explainable_capability_count": len(decisions),
            "items": items,
            "provider_summary": self.state.get("plugins.provider_summary", {}) or {},
            "support_state": self.state.get("owner.support_state", "managed"),
            "patient": {
                "schema": 1,
                "identity": identity,
                "coverage": coverage,
                "privacy_class": "technical_identity_only",
                "memory": patient_memory,
            },
        }

    def state_patch(self) -> dict[str, Any]:
        row = self.snapshot()
        patient = row.get("patient", {})
        coverage = patient.get("coverage", {}) if isinstance(patient, dict) else {}
        return {
            "doctor.state": row["state"],
            "doctor.attention_count": row["attention_count"],
            "doctor.explainable_capability_count": row["explainable_capability_count"],
            "doctor.items": row["items"],
            "doctor.patient.identity": patient.get("identity", {}) if isinstance(patient, dict) else {},
            "doctor.patient.memory": patient.get("memory", {}) if isinstance(patient, dict) else {},
            "doctor.patient.updated_at": ((patient.get("memory") or {}).get("updated_at")
                                          if isinstance(patient, dict) else None),
            "doctor.coverage": coverage,
            "doctor.coverage.covered_count": int((coverage.get("counts") or {}).get("covered", 0) or 0),
            "doctor.coverage.unavailable_count": int((coverage.get("counts") or {}).get("unavailable", 0) or 0),
            "doctor.coverage.unknown_count": int((coverage.get("counts") or {}).get("unknown", 0) or 0),
        }
