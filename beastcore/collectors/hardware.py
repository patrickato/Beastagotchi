from __future__ import annotations

from typing import Any
from .base import Collector
from ..util import run

class HardwareCollector(Collector):
    name = "hardware"
    interval = 30.0
    priority = 50

    def collect(self) -> dict[str, Any]:
        rc, out, _ = run(["lsusb"], timeout=3)
        devices = []
        if rc == 0:
            for line in out.splitlines():
                parts = line.split(" ", 6)
                devices.append({"raw": line, "id": parts[5] if len(parts) > 5 else ""})
        return {"platform.hardware": devices}
