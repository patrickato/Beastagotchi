from __future__ import annotations

import json
from typing import Any

from .base import Collector
from ..util import channel_to_band, parse_iw_dev, read_text, run

class RadioCollector(Collector):
    name = "radio"
    interval = 1.0
    priority = 60

    def __init__(self, primary: str = "wlan0mon") -> None:
        self.primary = primary
        self._supported: list[int] | None = None
        self._support_refresh = 0

    def _supported_channels(self) -> list[int]:
        code = "import json,pwnagotchi.utils as u; print(json.dumps(u.iface_channels(%r)))" % self.primary
        rc, out, _ = run(["/opt/.pwn/bin/python3", "-c", code], timeout=4)
        if rc == 0:
            try:
                return [int(x) for x in json.loads(out.strip())]
            except Exception:
                pass
        return []

    def collect(self) -> dict[str, Any]:
        rc, out, _ = run(["iw", "dev"], timeout=2)
        if rc != 0:
            return {"radio.primary.state": "unavailable"}
        interfaces = parse_iw_dev(out)
        values: dict[str, Any] = {"radio.interfaces": interfaces}
        primary = next((x for x in interfaces if x.get("name") == self.primary), None)
        if primary:
            values["radio.primary.state"] = "available"
            values["radio.primary.name"] = self.primary
            for src, dst in (("mode", "mode"), ("mac", "mac"), ("channel", "channel"), ("frequency_mhz", "frequency_mhz")):
                if src in primary:
                    values[f"radio.primary.{dst}"] = primary[src]
            values["radio.primary.band"] = channel_to_band(primary.get("channel"), primary.get("frequency_mhz"))
            values["radio.hop.current"] = primary.get("channel")
            values["radio.primary.operstate"] = read_text(f"/sys/class/net/{self.primary}/operstate").strip() or "unknown"
            for stat in ("rx_bytes", "tx_bytes"):
                raw = read_text(f"/sys/class/net/{self.primary}/statistics/{stat}").strip()
                if raw.isdigit():
                    values[f"radio.primary.{stat}"] = int(raw)
        else:
            values["radio.primary.state"] = "missing"

        self._support_refresh += 1
        if self._supported is None or self._support_refresh >= 30:
            self._supported = self._supported_channels()
            self._support_refresh = 0
        values["radio.primary.supported_channels"] = self._supported or []
        return values
