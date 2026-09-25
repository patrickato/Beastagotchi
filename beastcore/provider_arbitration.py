from __future__ import annotations

from typing import Any
import time


_INTEGRATION_WEIGHT = {
    "native": 100,
    "canonical": 90,
    "adapter": 80,
    "managed": 70,
    "config_only": 50,
    "superseded_by_beast": 40,
    "isolated": 20,
}


class CapabilityProviderArbitrator:
    """Read-only provider decision engine.

    This class explains which provider Beast would treat as canonical for a
    capability.  It does not enable/disable components, write preferences, start
    services, or perform failover.

    Policy:
    1. honor a valid explicit owner preference;
    2. otherwise prefer an already-live native/canonical Beast provider;
    3. otherwise accept one unambiguous selected+ready component;
    4. if several selected providers remain, require a choice but provide a
       deterministic recommendation and fallback order;
    5. available-but-unselected providers are alternatives, not silently active.
    """

    schema = 1

    def __init__(self, state) -> None:
        self.state = state

    @staticmethod
    def _norm(value: Any) -> str:
        return str(value or "").strip().lower().replace(" ", "_")

    def _preferences(self) -> dict[str, str]:
        raw = self.state.get("providers.preferences", {}) or {}
        if not isinstance(raw, dict):
            return {}
        out: dict[str, str] = {}
        for capability, provider in list(raw.items())[:256]:
            cap = self._norm(capability)
            val = str(provider or "").strip()
            if cap and val:
                out[cap] = val
        return out

    @staticmethod
    def _confidence_label(score: int) -> str:
        if score >= 80:
            return "high"
        if score >= 50:
            return "medium"
        return "low"

    def _native_health(self, provider: str) -> dict[str, Any]:
        key_map = {
            "native:gps": "gps.state",
            "native:power": "power.telemetry.available",
            "native:system": "system.cpu.total",
            "native:bluetooth": "bluetooth.adapter.present",
            "native:network": "network.internet.state",
            "native:display": "display.physical.width",
            "native:i2c": "capabilities.present",
            "native:gpio": "capabilities.present",
            "native:radio": "radio.primary.state",
            "native:captures": "captures.total",
            "native:pwnagotchi": "pwnagotchi.service.state",
        }
        key = key_map.get(provider)
        meta = None
        if key and hasattr(self.state, "meta"):
            try:
                meta = self.state.meta(key)
            except Exception:
                meta = None
        if isinstance(meta, dict):
            quality = str(meta.get("quality") or "live")
            updated = meta.get("updated_at")
            age = None
            if isinstance(updated, (int, float)):
                age = max(0.0, float(time.time()) - float(updated))
            if quality == "live" and not meta.get("error"):
                return {
                    "health_state": "healthy",
                    "confidence": "high",
                    "confidence_score": 95,
                    "freshness_sec": round(age, 3) if age is not None else None,
                    "evidence_quality": "live",
                    "health_key": key,
                }
            if quality == "stale":
                return {
                    "health_state": "stale",
                    "confidence": "medium",
                    "confidence_score": 55,
                    "freshness_sec": round(age, 3) if age is not None else None,
                    "evidence_quality": "stale",
                    "health_key": key,
                }
            return {
                "health_state": "degraded",
                "confidence": "low",
                "confidence_score": 25,
                "freshness_sec": round(age, 3) if age is not None else None,
                "evidence_quality": quality or "unknown",
                "health_key": key,
            }
        return {
            "health_state": "ready_unverified",
            "confidence": "medium",
            "confidence_score": 65,
            "freshness_sec": None,
            "evidence_quality": "presence_only",
            "health_key": key,
        }

    @staticmethod
    def _provider_component_id(provider: str) -> str | None:
        return provider.split(":", 1)[1] if provider.startswith("component:") else None

    def _candidate(
        self,
        capability: str,
        provider: str,
        component_by_id: dict[str, dict[str, Any]],
        resolved_components: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        cid = self._provider_component_id(provider)
        if cid is None:
            kind = provider.split(":", 1)[0] if ":" in provider else "native"
            health = self._native_health(provider)
            return {
                "provider": provider,
                "component": None,
                "kind": kind,
                "available": True,
                "selected": True,
                "ready": True,
                "integration": "native",
                "priority": 1000,
                "reason": "canonical/native provider is already live",
                **health,
            }

        component = component_by_id.get(cid, {})
        resolved = resolved_components.get(cid, {})
        available = bool(resolved.get("available", component.get("available", False)))
        selected = bool(resolved.get("selected", component.get("selected", component.get("enabled", False))))
        ready = bool(resolved.get("requirements_ready", False))
        integration = str(component.get("integration") or "config_only")
        declared_priority = component.get("provider_priority")
        try:
            declared_priority_i = int(declared_priority) if declared_priority is not None else 0
        except (TypeError, ValueError):
            declared_priority_i = 0
        score = _INTEGRATION_WEIGHT.get(integration, 30) + declared_priority_i + (10 if selected else 0)
        technical = list(resolved.get("technical_blockers") or [])
        policy = list(resolved.get("policy_blockers") or [])
        if not available:
            health_state = "unavailable"
            confidence_score = 10
            evidence_quality = "catalog_only"
        elif technical:
            health_state = "blocked"
            confidence_score = 15
            evidence_quality = "requirements_failed"
        elif policy:
            health_state = "needs_attention"
            confidence_score = 35
            evidence_quality = "requirements_uncertain"
        elif ready and selected:
            health_state = "ready_unverified"
            confidence_score = 70 if integration in {"native", "canonical", "adapter", "managed"} else 45
            evidence_quality = "requirements_ready"
        elif ready:
            health_state = "standby_ready"
            confidence_score = 60 if integration in {"native", "canonical", "adapter", "managed"} else 40
            evidence_quality = "requirements_ready"
        else:
            health_state = "unknown"
            confidence_score = 25
            evidence_quality = "unknown"
        return {
            "provider": provider,
            "component": cid,
            "kind": "component",
            "available": available,
            "selected": selected,
            "ready": ready,
            "integration": integration,
            "priority": score,
            "role": component.get("role"),
            "provider_group": component.get("provider_group"),
            "technical_blockers": technical,
            "policy_blockers": policy,
            "reason": "component provider",
            "health_state": health_state,
            "confidence": self._confidence_label(confidence_score),
            "confidence_score": confidence_score,
            "freshness_sec": component.get("freshness_sec"),
            "evidence_quality": evidence_quality,
            "health_key": component.get("health_key"),
        }

    @staticmethod
    def _rank(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            candidates,
            key=lambda row: (
                -int(row.get("priority", 0) or 0),
                not bool(row.get("selected")),
                str(row.get("provider") or ""),
            ),
        )

    def evaluate(
        self,
        components: list[dict[str, Any]],
        resolution: dict[str, Any],
    ) -> dict[str, Any]:
        component_by_id: dict[str, dict[str, Any]] = {}
        for i, row in enumerate(components[:512]):
            if not isinstance(row, dict):
                continue
            cid = str(row.get("id") or row.get("name") or f"component-{i}").strip()
            if cid:
                component_by_id[cid] = row

        resolved_components = resolution.get("components") if isinstance(resolution.get("components"), dict) else {}
        providers = resolution.get("providers") if isinstance(resolution.get("providers"), dict) else {}
        preferences = self._preferences()

        decisions: dict[str, dict[str, Any]] = {}
        choice_required_count = preference_problem_count = active_count = 0

        for capability, provider_names in sorted(providers.items()):
            if not isinstance(provider_names, list):
                continue
            candidates = [
                self._candidate(capability, str(provider), component_by_id, resolved_components)
                for provider in provider_names[:64]
                if str(provider).strip()
            ]
            ranked = self._rank(candidates)
            viable = [row for row in ranked if row["available"] and row["ready"]]
            selected = [row for row in viable if row["selected"]]
            native = [row for row in viable if row["component"] is None]

            preferred = preferences.get(self._norm(capability))
            preferred_row = next((row for row in viable if row["provider"] == preferred), None) if preferred else None
            preference_issue = None
            active = None
            recommendation = viable[0]["provider"] if viable else None
            decision_state = "unavailable"
            reason = "no ready provider is available"

            if preferred and preferred_row is not None:
                active = preferred_row["provider"]
                decision_state = "active_preference"
                reason = "explicit owner provider preference is available and ready"
            elif preferred:
                preference_problem_count += 1
                preference_issue = f"preferred provider {preferred} is not currently ready/available"
                if native:
                    active = native[0]["provider"]
                    decision_state = "active_fallback"
                    reason = "owner preference unavailable; canonical native provider used as fallback"
                elif len(selected) == 1:
                    active = selected[0]["provider"]
                    decision_state = "active_fallback"
                    reason = "owner preference unavailable; one selected ready provider remains"
                elif len(selected) > 1:
                    decision_state = "choice_required"
                    reason = "owner preference unavailable and multiple selected ready providers remain"
                elif viable:
                    decision_state = "available_unselected"
                    reason = "owner preference unavailable; ready providers exist but none is selected"
            elif native:
                active = native[0]["provider"]
                decision_state = "active_native"
                reason = "canonical/native provider is already live and is preferred for canonical truth"
            elif len(selected) == 1:
                active = selected[0]["provider"]
                decision_state = "active_selected"
                reason = "one selected ready provider is unambiguous"
            elif len(selected) > 1:
                decision_state = "choice_required"
                reason = "multiple selected ready providers exist and no explicit preference resolves them"
            elif viable:
                decision_state = "available_unselected"
                reason = "ready provider(s) exist but none is selected"

            if decision_state == "choice_required":
                choice_required_count += 1
            if active:
                active_count += 1

            alternates = [row["provider"] for row in viable if row["provider"] != active]
            fallback_chain: list[str] = []
            if active:
                fallback_chain.append(active)
            if recommendation and recommendation not in fallback_chain:
                fallback_chain.append(recommendation)
            fallback_chain.extend([p for p in alternates if p not in fallback_chain])

            decisions[str(capability)] = {
                "capability": str(capability),
                "state": decision_state,
                "active_provider": active,
                "recommended_provider": recommendation,
                "owner_preference": preferred,
                "preference_issue": preference_issue,
                "reason": reason,
                "alternates": alternates,
                "fallback_chain": fallback_chain,
                "candidate_count": len(candidates),
                "ready_candidate_count": len(viable),
                "selected_ready_count": len(selected),
                "choice_required": decision_state == "choice_required",
                "active_health": next((row.get("health_state") for row in candidates if row.get("provider") == active), None),
                "active_confidence": next((row.get("confidence") for row in candidates if row.get("provider") == active), None),
                "active_freshness_sec": next((row.get("freshness_sec") for row in candidates if row.get("provider") == active), None),
                "automatic_failover_enabled": False,
                "selection_mutation_enabled": False,
                "candidates": candidates,
            }

        return {
            "schema": self.schema,
            "mode": "read_only_policy",
            "selection_mutation_enabled": False,
            "automatic_failover_enabled": False,
            "owner_preferences_read_only": True,
            "decisions": decisions,
            "summary": {
                "capability_count": len(decisions),
                "active_count": active_count,
                "choice_required_count": choice_required_count,
                "preference_problem_count": preference_problem_count,
                "unavailable_count": sum(1 for row in decisions.values() if row["state"] == "unavailable"),
                "active_high_confidence_count": sum(1 for row in decisions.values() if row.get("active_confidence") == "high"),
                "active_medium_confidence_count": sum(1 for row in decisions.values() if row.get("active_confidence") == "medium"),
                "active_low_confidence_count": sum(1 for row in decisions.values() if row.get("active_confidence") == "low"),
            },
        }
