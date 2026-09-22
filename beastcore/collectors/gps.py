from __future__ import annotations

import json
import socket
from typing import Any

from .base import Collector


class GPSCollector(Collector):
    name = "gps"
    interval = 1.0
    priority = 70

    def __init__(self, host: str = "127.0.0.1", port: int = 2947) -> None:
        self.host = host
        self.port = port

    def collect(self) -> dict[str, Any]:
        # Explicitly clear fix-derived fields when a fix disappears. This prevents a
        # previous HDOP/speed/location from looking current while gpsd reports no fix.
        values: dict[str, Any] = {
            "gps.fix": False,
            "gps.state": "unavailable",
            "gps.mode": 0,
            "gps.latitude": None,
            "gps.longitude": None,
            "gps.altitude_m": None,
            "gps.speed_mps": None,
            "gps.heading_deg": None,
            "gps.accuracy_m": None,
            "gps.hdop": None,
            "gps.satellites_visible": 0,
            "gps.satellites_used": 0,
        }
        try:
            with socket.create_connection((self.host, self.port), timeout=1.5) as s:
                s.settimeout(1.5)
                s.sendall(b'?WATCH={"enable":true,"json":true};\n?POLL;\n')
                data = b""
                while len(data) < 262144:
                    try:
                        chunk = s.recv(65536)
                        if not chunk:
                            break
                        data += chunk
                        if b'"class":"POLL"' in data:
                            break
                    except socket.timeout:
                        break
            values["gps.state"] = "connected_no_fix"
            tpv = None
            sky = None
            for line in data.decode(errors="replace").splitlines():
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("class") == "POLL":
                    if obj.get("tpv"):
                        tpv = obj["tpv"][-1]
                    if obj.get("sky"):
                        sky = obj["sky"][-1]
                elif obj.get("class") == "TPV":
                    tpv = obj
                elif obj.get("class") == "SKY":
                    sky = obj
            if tpv:
                mode = int(tpv.get("mode", 0) or 0)
                values["gps.fix"] = mode >= 2
                values["gps.mode"] = mode
                values["gps.state"] = "fixed" if mode >= 2 else "connected_no_fix"
                mapping = {
                    "lat": "latitude",
                    "lon": "longitude",
                    "altMSL": "altitude_m",
                    "alt": "altitude_m",
                    "speed": "speed_mps",
                    "track": "heading_deg",
                    "eph": "accuracy_m",
                }
                for src, dst in mapping.items():
                    if src in tpv and tpv[src] is not None:
                        # altMSL wins if both altitude fields exist.
                        key = f"gps.{dst}"
                        if dst == "altitude_m" and values[key] is not None:
                            continue
                        values[key] = tpv[src]
            if sky:
                sats = sky.get("satellites") or []
                values["gps.satellites_visible"] = len(sats)
                values["gps.satellites_used"] = sum(1 for x in sats if x.get("used"))
                if "hdop" in sky and sky["hdop"] is not None:
                    values["gps.hdop"] = sky["hdop"]
        except Exception as exc:
            values["gps.error"] = type(exc).__name__
        return values
