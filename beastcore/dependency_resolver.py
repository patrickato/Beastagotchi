from __future__ import annotations

import importlib.util
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .util import run


_HARD_FAILURES = {
    "hardware_absent",
    "service_inactive",
    "configuration_missing",
    "credential_missing",
    "missing_installable",
    "missing_user_action",
}
_POLICY_FAILURES = {
    "unknown",
    "version_incompatible",
    "conflict",
    "unsupported",
    "provider_available_not_selected",
}


@dataclass(frozen=True)
class RequirementResult:
    requirement: str
    kind: str
    status: str
    satisfied: bool
    remediation: str
    detail: str = ""
    evidence: dict[str, Any] | None = None
    providers: tuple[str, ...] = ()
    optional: bool = False

    @property
    def technical_blocker(self) -> bool:
        return (not self.optional) and self.status in _HARD_FAILURES

    @property
    def policy_blocker(self) -> bool:
        return (not self.optional) and self.status in _POLICY_FAILURES

    def as_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["providers"] = list(self.providers)
        row["technical_blocker"] = self.technical_blocker
        row["policy_blocker"] = self.policy_blocker
        return row


class DependencyCapabilityResolver:
    """Side-effect-free dependency/capability inspection.

    The resolver reads canonical Beast state and performs bounded presence
    probes. It never installs packages, starts services, writes configuration or
    selects providers. Unknown evidence stays unknown.
    """

    schema = 1

    def __init__(
        self,
        state,
        *,
        command_runner: Callable[..., tuple[int, str, str]] = run,
        which: Callable[[str], str | None] = shutil.which,
        path_exists: Callable[[str], bool] | None = None,
        module_finder: Callable[[str], Any] | None = None,
    ) -> None:
        self.state = state
        self.command_runner = command_runner
        self.which = which
        self.path_exists = path_exists or (lambda p: Path(p).exists())
        self.module_finder = module_finder or importlib.util.find_spec

    @staticmethod
    def _norm(value: Any) -> str:
        return str(value or "").strip().lower().replace(" ", "_")

    def _services(self) -> dict[str, dict[str, Any]]:
        rows = self.state.get("platform.services", []) or []
        out: dict[str, dict[str, Any]] = {}
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                unit = str(row.get("unit") or "").strip()
                if unit:
                    out[unit.lower()] = row
        return out

    def _capability_names(self) -> set[str]:
        vals = self.state.get("capabilities.present", []) or []
        return {self._norm(x) for x in vals if str(x).strip()} if isinstance(vals, list) else set()

    def native_providers(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}

        def add(cap: str, provider: str) -> None:
            out.setdefault(cap, [])
            if provider not in out[cap]:
                out[cap].append(provider)

        caps = self._capability_names()
        gps_state = str(self.state.get("gps.state", "") or "").lower()
        if gps_state in {"fixed", "connected_no_fix"}:
            add("location.position", "native:gps")
            add("location.fix", "native:gps")
            add("location.satellites", "native:gps")
            add("location.receiver_or_gpsd", "native:gps")
            add("location.source", "native:gps")
        if bool(self.state.get("power.telemetry.available", False)):
            add("power.battery.telemetry", "native:power")
        if self.state.get("system.cpu.total") is not None or self.state.get("system.temp.cpu_c") is not None:
            add("system.telemetry", "native:system")
        if bool(self.state.get("bluetooth.adapter.present", False)) or "bluetooth" in caps:
            add("bluetooth.adapter", "native:bluetooth")
        if bool(self.state.get("network.route.available", False)):
            add("network.route", "native:network")
        internet = self.state.get("network.internet.state")
        if internet is True or str(internet or "").lower() in {"online", "available", "reachable", "connected"}:
            add("network.internet", "native:network")
        if "display" in caps or self.state.get("display.physical.width") is not None or self.path_exists("/dev/fb1"):
            add("display.primary", "native:display")
        if "i2c" in caps or self.path_exists("/dev/i2c-1"):
            add("i2c", "native:i2c")
        if self.path_exists("/dev/gpiomem") or "gpio" in caps:
            add("gpio.available", "native:gpio")
        if str(self.state.get("radio.primary.state", "") or "").lower() == "available":
            add("radio.onboard", "native:radio")
            add("radio.wifi.monitor", "native:radio")
        if self.state.get("captures.directory") is not None or self.state.get("captures.total") is not None:
            add("capture.handshake", "native:captures")
        if self.which("systemctl"):
            add("systemd", "native:systemd")
        if self.state.get("pwnagotchi.service.state") is not None:
            add("pwnagotchi.service", "native:pwnagotchi")
            add("pwnagotchi.logs", "native:pwnagotchi")
            add("pwnagotchi.webui", "native:pwnagotchi")
        return out

    def _result(
        self,
        requirement: str,
        kind: str,
        status: str,
        *,
        remediation: str,
        detail: str = "",
        evidence: dict[str, Any] | None = None,
        providers: list[str] | tuple[str, ...] | None = None,
        optional: bool = False,
    ) -> RequirementResult:
        return RequirementResult(
            requirement=requirement,
            kind=kind,
            status=status,
            satisfied=status == "satisfied",
            remediation=remediation,
            detail=detail,
            evidence=evidence or {},
            providers=tuple(providers or ()),
            optional=optional,
        )

    def _resolve_service(self, requirement: str, unit: str, *, optional: bool) -> RequirementResult:
        row = self._services().get(unit.lower())
        if row is None:
            return self._result(
                requirement, "service", "unknown", remediation="inspect",
                detail=f"{unit} is not present in the canonical service inventory",
                optional=optional,
            )
        load = str(row.get("load") or "unknown").lower()
        active = str(row.get("active") or "unknown").lower()
        if load == "not-found":
            return self._result(
                requirement, "service", "missing_installable", remediation="confirm_transactional",
                detail=f"{unit} is not installed", evidence={"load": load, "active": active},
                optional=optional,
            )
        if active == "active":
            return self._result(
                requirement, "service", "satisfied", remediation="none",
                evidence={"load": load, "active": active, "sub": row.get("sub")},
                providers=[f"service:{unit}"], optional=optional,
            )
        if active in {"inactive", "failed", "deactivating"}:
            return self._result(
                requirement, "service", "service_inactive", remediation="confirm_transactional",
                detail=f"{unit} is {active}", evidence={"load": load, "active": active, "sub": row.get("sub")},
                optional=optional,
            )
        return self._result(
            requirement, "service", "unknown", remediation="inspect",
            detail=f"{unit} state is {active}", evidence={"load": load, "active": active},
            optional=optional,
        )

    def _resolve_prefixed(self, requirement: str, *, optional: bool) -> RequirementResult | None:
        if ":" not in requirement:
            return None
        kind, value = requirement.split(":", 1)
        kind = self._norm(kind)
        value = str(value).strip()
        if not value:
            return self._result(requirement, kind or "unknown", "unknown", remediation="inspect", optional=optional)

        if kind == "service":
            return self._resolve_service(requirement, value, optional=optional)

        if kind == "executable":
            found = self.which(value)
            if found:
                return self._result(requirement, kind, "satisfied", remediation="none", evidence={"path": found}, providers=[f"executable:{value}"], optional=optional)
            return self._result(requirement, kind, "missing_installable", remediation="confirm_transactional", detail=f"executable {value} was not found in PATH", optional=optional)

        if kind == "python":
            try:
                found = self.module_finder(value) is not None
            except Exception:
                found = False
            if found:
                return self._result(requirement, kind, "satisfied", remediation="none", providers=[f"python:{value}"], optional=optional)
            return self._result(requirement, kind, "missing_installable", remediation="confirm_transactional", detail=f"Python module {value} was not found", optional=optional)

        if kind == "path":
            if self.path_exists(value):
                return self._result(requirement, kind, "satisfied", remediation="none", evidence={"path": value}, providers=[f"path:{value}"], optional=optional)
            return self._result(requirement, kind, "missing_user_action", remediation="guided", detail=f"{value} does not exist", optional=optional)

        if kind == "package":
            rc, out, _ = self.command_runner(["dpkg-query", "-W", value], timeout=2)
            if rc == 0:
                version = out.strip().split(None, 1)[1] if len(out.strip().split(None, 1)) == 2 else None
                return self._result(requirement, kind, "satisfied", remediation="none", evidence={"package": value, "version": version}, providers=[f"package:{value}"], optional=optional)
            return self._result(requirement, kind, "missing_installable", remediation="confirm_transactional", detail=f"OS package {value} is not installed", optional=optional)

        if kind in {"config", "credential"}:
            current = self.state.get(value)
            present = current not in {None, "", False}
            if present:
                return self._result(requirement, kind, "satisfied", remediation="none", evidence={"present": True}, providers=[f"{kind}:{value}"], optional=optional)
            status = "credential_missing" if kind == "credential" else "configuration_missing"
            detail = "required credential is not configured" if kind == "credential" else f"required configuration {value} is missing"
            return self._result(requirement, kind, status, remediation="guided", detail=detail, evidence={"present": False}, optional=optional)

        if kind == "capability":
            return self.resolve_requirement(value, optional=optional)

        return self._result(requirement, kind, "unknown", remediation="inspect", detail=f"unknown requirement type {kind}", optional=optional)

    def _resolve_abstract(self, requirement: str, *, optional: bool) -> RequirementResult:
        req = self._norm(requirement)
        native = self.native_providers()
        if req in native:
            return self._result(requirement, "capability", "satisfied", remediation="none", providers=native[req], optional=optional)

        if req.endswith(".service"):
            return self._resolve_service(requirement, req, optional=optional)

        if req == "storage.writable":
            ro = self.state.get("storage.root.readonly")
            if ro is False:
                return self._result(requirement, "storage", "satisfied", remediation="none", providers=["native:storage"], optional=optional)
            if ro is True:
                return self._result(requirement, "storage", "configuration_missing", remediation="guided", detail="root filesystem is read-only", optional=optional)

        if req == "network.internet":
            state = self.state.get("network.internet.state")
            if state is False or str(state or "").lower() in {"offline", "unavailable", "down"}:
                return self._result(requirement, "connectivity", "missing_user_action", remediation="guided", detail="Internet reachability is unavailable", optional=optional)
            if bool(self.state.get("network.route.available", False)):
                return self._result(
                    requirement, "connectivity", "unknown", remediation="inspect",
                    detail="a default route exists but Internet reachability is intentionally not inferred from it",
                    evidence={"default_route": True}, optional=optional,
                )

        if req == "bluetooth.adapter" and self.state.get("bluetooth.adapter.present") is False:
            return self._result(requirement, "hardware", "hardware_absent", remediation="guided", detail="no Bluetooth controller is detected", optional=optional)

        if req == "i2c" and self.state.get("capabilities.present") is not None:
            return self._result(requirement, "hardware", "hardware_absent", remediation="guided", detail="/dev/i2c-1 is not available", optional=optional)

        if req == "display.primary" and self.state.get("capabilities.present") is not None:
            return self._result(requirement, "hardware", "hardware_absent", remediation="guided", detail="primary framebuffer/display capability is not detected", optional=optional)

        if req.startswith("hardware."):
            inventory = self.state.get("platform.hardware")
            if isinstance(inventory, list):
                return self._result(requirement, "hardware", "unknown", remediation="inspect", detail="hardware inventory exists but no dedicated detector is registered for this requirement", optional=optional)

        return self._result(requirement, "capability", "unknown", remediation="inspect", detail="no canonical provider/evidence currently satisfies this requirement", optional=optional)

    def resolve_requirement(
        self,
        requirement: str,
        *,
        optional: bool = False,
        providers: list[str] | tuple[str, ...] | None = None,
    ) -> RequirementResult:
        req = str(requirement or "").strip()
        if not req:
            return self._result("", "unknown", "unknown", remediation="inspect", optional=optional)
        if providers:
            return self._result(req, "capability", "satisfied", remediation="none", providers=list(providers), optional=optional)
        prefixed = self._resolve_prefixed(req, optional=optional)
        if prefixed is not None:
            return prefixed
        return self._resolve_abstract(req, optional=optional)

    def resolve_components(self, components: list[dict[str, Any]]) -> dict[str, Any]:
        normalized: list[dict[str, Any]] = []
        for i, raw in enumerate(components[:512]):
            if not isinstance(raw, dict):
                continue
            cid = str(raw.get("id") or raw.get("name") or f"component-{i}").strip()
            if not cid:
                continue
            normalized.append({
                **raw,
                "_id": cid,
                "_norm": self._norm(cid).replace("-", "_"),
                "_enabled": bool(raw.get("enabled", raw.get("active", True))),
            })

        provider_index: dict[str, list[str]] = {
            cap: list(providers) for cap, providers in self.native_providers().items()
        }
        for row in normalized:
            if not row["_enabled"]:
                continue
            for capability in row.get("provides") or []:
                cap = self._norm(capability)
                if not cap:
                    continue
                provider_index.setdefault(cap, [])
                provider = f"component:{row['_id']}"
                if provider not in provider_index[cap]:
                    provider_index[cap].append(provider)

        used_by: dict[str, set[str]] = {}
        results: dict[str, dict[str, Any]] = {}
        technical_total = policy_total = unresolved_total = 0
        active_technical_total = active_policy_total = active_unresolved_total = 0

        for row in normalized:
            mandatory: list[RequirementResult] = []
            optional_rows: list[RequirementResult] = []
            for req in list(row.get("requires") or [])[:128]:
                name = str(req).strip()
                providers = provider_index.get(self._norm(name), [])
                rr = self.resolve_requirement(name, providers=providers)
                mandatory.append(rr)
                for provider in rr.providers:
                    used_by.setdefault(provider, set()).add(row["_id"])
            for req in list(row.get("optional_requirements") or [])[:128]:
                name = str(req).strip()
                providers = provider_index.get(self._norm(name), [])
                rr = self.resolve_requirement(name, optional=True, providers=providers)
                optional_rows.append(rr)
                for provider in rr.providers:
                    used_by.setdefault(provider, set()).add(row["_id"])

            conflict_rows: list[RequirementResult] = []
            conflicts = {self._norm(x).replace("-", "_") for x in row.get("conflicts") or []}
            if conflicts:
                for other in normalized:
                    if other["_norm"] in conflicts and other["_enabled"]:
                        conflict_rows.append(self._result(
                            f"conflict:{other['_id']}", "conflict", "conflict",
                            remediation="choose_provider",
                            detail=f"conflicts with enabled component {other['_id']}",
                        ))

            all_required = mandatory + conflict_rows
            technical = [x.requirement for x in all_required if x.technical_blocker]
            policy = [x.requirement for x in all_required if x.policy_blocker]
            unresolved = [x.requirement for x in mandatory if x.status == "unknown"]
            technical_total += len(technical)
            policy_total += len(policy)
            unresolved_total += len(unresolved)
            if row["_enabled"]:
                active_technical_total += len(technical)
                active_policy_total += len(policy)
                active_unresolved_total += len(unresolved)
            if technical:
                readiness = "blocked"
            elif policy:
                readiness = "needs_attention"
            else:
                readiness = "ready"

            results[row["_id"]] = {
                "requirements_resolution": "read_only",
                "selected": bool(row["_enabled"]),
                "requirements_ready": not technical and not policy,
                "requirements_status": readiness,
                "technical_blockers": technical,
                "policy_blockers": policy,
                "owner_override_available": bool(policy) and not technical,
                "required_results": [x.as_dict() for x in mandatory],
                "optional_results": [x.as_dict() for x in optional_rows],
                "conflict_results": [x.as_dict() for x in conflict_rows],
                "unresolved_requirements": unresolved,
            }

        return {
            "schema": self.schema,
            "execution_enabled": False,
            "provider_selection_enabled": False,
            "components": results,
            "providers": {k: list(v) for k, v in sorted(provider_index.items())},
            "used_by": {k: sorted(v) for k, v in sorted(used_by.items())},
            "summary": {
                "component_count": len(results),
                "selected_component_count": sum(1 for row in normalized if row["_enabled"]),
                "active_technical_blocker_count": active_technical_total,
                "active_policy_blocker_count": active_policy_total,
                "active_unresolved_count": active_unresolved_total,
                "catalog_technical_blocker_count": technical_total,
                "catalog_policy_blocker_count": policy_total,
                "catalog_unresolved_count": unresolved_total,
            },
        }
