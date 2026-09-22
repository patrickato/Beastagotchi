from __future__ import annotations

from typing import Any
from .base import Collector
from ..util import run

DEFAULT_UNITS = [
    "pwnagotchi.service",
    "bettercap.service",
    "gpsd.service",
    "pwngrid-peer.service",
    "NetworkManager.service",
    "systemd-timesyncd.service",
    "beast-core.service",
    "beast-ui.service",
    "beast-studio.service",
]

class ServicesCollector(Collector):
    name = "services"
    interval = 5.0

    def __init__(self, units: list[str] | None = None) -> None:
        self.units = units or DEFAULT_UNITS

    @staticmethod
    def _show(unit: str) -> dict[str, str]:
        props = "LoadState,ActiveState,SubState,MainPID,ExecMainStartTimestamp"
        rc, out, _ = run(["systemctl", "show", unit, "-p", props], timeout=2)
        if rc != 0:
            return {}
        result: dict[str, str] = {}
        for line in out.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            result[key] = value
        return result

    def collect(self) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        by_unit: dict[str, dict[str, Any]] = {}
        for unit in self.units:
            p = self._show(unit)
            item = {
                "unit": unit,
                "load": p.get("LoadState", "unknown"),
                "active": p.get("ActiveState", "unknown"),
                "sub": p.get("SubState", "unknown"),
                "pid": int(p.get("MainPID", "0") or 0),
                "started": p.get("ExecMainStartTimestamp", ""),
            }
            items.append(item)
            by_unit[unit] = item

        values: dict[str, Any] = {"platform.services": items}
        bc = by_unit.get("bettercap.service")
        if bc:
            values["bettercap.state"] = bc["active"]
            values["bettercap.service.substate"] = bc["sub"]
            values["bettercap.service.pid"] = bc["pid"]
        pw = by_unit.get("pwnagotchi.service")
        if pw:
            values["pwnagotchi.service.state"] = pw["active"]
            values["pwnagotchi.service.substate"] = pw["sub"]
            values["pwnagotchi.service.pid"] = pw["pid"]
        gpsd = by_unit.get("gpsd.service")
        if gpsd:
            values["gps.service.state"] = gpsd["active"]
        return values
