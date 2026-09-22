from __future__ import annotations

import os
from typing import Any

from .base import Collector
from ..util import read_text

class StorageCollector(Collector):
    name = "storage"
    interval = 10.0
    priority = 50

    def collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize; free = st.f_bavail * st.f_frsize
        values["storage.root.free_bytes"] = free
        values["storage.root.used_pct"] = round((total - free) / total * 100, 2) if total else 0.0
        mounts = []
        root_ro = False
        for line in read_text("/proc/mounts").splitlines():
            p = line.split()
            if len(p) < 4: continue
            item = {"source": p[0], "mount": p[1], "fstype": p[2], "options": p[3].split(",")}
            mounts.append(item)
            if p[1] == "/": root_ro = "ro" in item["options"] and "rw" not in item["options"]
        values["storage.mounts"] = mounts
        values["storage.root.readonly"] = root_ro
        return values
