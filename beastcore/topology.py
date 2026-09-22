from __future__ import annotations

from typing import Any


class ServiceTopologyEngine:
    """Build a live dependency map from canonical Beast state.

    Edges express software/data dependencies, not inferred network topology.
    """

    def __init__(self, state) -> None:
        self.state = state

    @staticmethod
    def _norm(v: Any) -> str:
        return str(v if v is not None else "unknown").lower()

    @staticmethod
    def _node(node_id: str, label: str, kind: str, state: str, detail: str = "") -> dict[str, Any]:
        return {"id": node_id, "label": label, "kind": kind, "state": state, "detail": detail}

    def tick(self) -> dict[str, Any]:
        radio_state = self._norm(self.state.get("radio.primary.state", "available" if self.state.get("radio.primary.name") else "unknown"))
        better = self._norm(self.state.get("bettercap.state"))
        pwn = self._norm(self.state.get("pwnagotchi.service.state"))
        bridge = self._norm(self.state.get("pwnagotchi.bridge.state"))
        core = self._norm(self.state.get("health.core.state"))
        ui = "active" if any(isinstance(r,dict) and r.get("unit") == "beast-ui.service" and r.get("active") == "active" for r in (self.state.get("platform.services") or [])) else "inactive"
        studio = "active" if any(isinstance(r,dict) and r.get("unit") == "beast-studio.service" and r.get("active") == "active" for r in (self.state.get("platform.services") or [])) else "inactive"
        gps = self._norm(self.state.get("gps.state", "fix" if self.state.get("gps.fix") else "unknown"))

        nodes = [
            self._node("radio", "Wi-Fi PHY", "hardware", radio_state, str(self.state.get("radio.primary.name") or "--")),
            self._node("bettercap", "Bettercap", "service", better),
            self._node("pwnagotchi", "Pwnagotchi", "service", pwn),
            self._node("bridge", "Beast Bridge", "adapter", bridge),
            self._node("core", "Beast Core", "service", core),
            self._node("ui", "Beast UI", "client", ui),
            self._node("studio", "Beast Studio", "client", studio),
            self._node("gps", "GPS", "hardware", gps),
        ]
        edges = [
            {"from":"radio","to":"bettercap","kind":"radio"},
            {"from":"bettercap","to":"pwnagotchi","kind":"control"},
            {"from":"pwnagotchi","to":"bridge","kind":"callbacks"},
            {"from":"bridge","to":"core","kind":"telemetry"},
            {"from":"bettercap","to":"core","kind":"telemetry"},
            {"from":"gps","to":"core","kind":"telemetry"},
            {"from":"core","to":"ui","kind":"api"},
            {"from":"core","to":"studio","kind":"api"},
        ]
        important = {n["id"]: n["state"] for n in nodes}
        failures = [k for k in ("radio","bettercap","pwnagotchi","bridge","core") if important.get(k) not in {"active","running","ready","available","healthy","fix","connected","connected_no_fix"}]
        return {
            "topology.nodes": nodes,
            "topology.edges": edges,
            "topology.failure_count": len(failures),
            "topology.failures": failures,
        }
