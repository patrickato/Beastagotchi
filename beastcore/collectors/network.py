from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import Collector
from ..util import read_text, run


class NetworkCollector(Collector):
    """Read-only wired-network facts used by Dock mode and Hardware Studio."""
    name = "network"
    interval = 2.0
    priority = 65

    def _iface(self, name: str) -> dict[str, Any]:
        p = Path('/sys/class/net') / name
        if not p.exists():
            return {"name": name, "present": False}
        carrier = read_text(p/'carrier').strip()
        oper = read_text(p/'operstate').strip() or 'unknown'
        speed = read_text(p/'speed').strip()
        out: dict[str, Any] = {
            "name": name,
            "present": True,
            "carrier": carrier == '1',
            "operstate": oper,
        }
        if speed.lstrip('-').isdigit():
            out["speed_mbps"] = int(speed)
        rc, txt, _ = run(["ip", "-j", "addr", "show", "dev", name], timeout=2)
        if rc == 0:
            try:
                arr = json.loads(txt)
                if arr:
                    out["addresses"] = [a.get("local") for a in arr[0].get("addr_info", []) if a.get("local")]
                    out["mac"] = arr[0].get("address")
            except Exception:
                pass
        return out

    def collect(self) -> dict[str, Any]:
        eth = self._iface('eth0')
        vals: dict[str, Any] = {
            "network.ethernet": eth,
            "network.ethernet.present": bool(eth.get("present")),
            "network.ethernet.carrier": bool(eth.get("carrier")),
            "network.ethernet.operstate": eth.get("operstate", "missing"),
            # Internet reachability is intentionally not inferred from a route.
            # A default route means routed connectivity only.
            "network.internet.state": "unknown",
        }
        interfaces=[]
        try:
            for ipath in sorted(Path('/sys/class/net').iterdir()):
                name=ipath.name
                if name=='lo':continue
                interfaces.append(self._iface(name))
        except OSError:
            pass
        vals["network.interfaces"] = interfaces
        if eth.get("speed_mbps") is not None:
            vals["network.ethernet.speed_mbps"] = eth["speed_mbps"]
        rc, out, _ = run(["ip", "-j", "route", "show", "default"], timeout=2)
        if rc == 0:
            try:
                routes = json.loads(out)
                route = next((r for r in routes if r.get("dev") == 'eth0'), routes[0] if routes else None)
                if route:
                    vals["network.default.dev"] = route.get("dev")
                    vals["network.default.gateway"] = route.get("gateway")
                    vals["network.default.protocol"] = route.get("protocol")
                    vals["network.route.available"] = True
            except Exception:
                pass
        vals.setdefault("network.route.available", False)
        gw = vals.get("network.default.gateway")
        if gw:
            rc, out, _ = run(["ip", "neigh", "show", str(gw), "dev", "eth0"], timeout=2)
            if rc == 0:
                parts = out.split()
                if 'lladdr' in parts:
                    try: vals["network.default.gateway_mac"] = parts[parts.index('lladdr')+1].lower()
                    except Exception: pass
        return vals
