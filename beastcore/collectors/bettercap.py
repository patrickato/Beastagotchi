from __future__ import annotations

import base64
import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

from .base import Collector
from ..util import run


class BettercapCollector(Collector):
    name = "bettercap"
    interval = 2.0
    priority = 80

    def __init__(self) -> None:
        self._caplet_cache: Path | None = None
        self._caplet_cfg: dict[str, str] | None = None
        self._caplet_checked_mono = 0.0
        self._caplet_sig: tuple[str, int, int] | None = None

    def _active_caplet(self, max_age: float = 30.0) -> Path | None:
        now = time.monotonic()
        if now - self._caplet_checked_mono < max_age and self._caplet_cache is not None:
            return self._caplet_cache if self._caplet_cache.is_file() else None
        self._caplet_checked_mono = now
        rc, out, _ = run(["pgrep", "-a", "bettercap"], timeout=2)
        if rc != 0:
            self._caplet_cache = None
            return None
        m = re.search(r"(?:^|\s)-caplet\s+([^\s]+)", out)
        if not m:
            self._caplet_cache = None
            return None
        name = m.group(1)
        candidates = [
            Path(name),
            Path("/usr/local/share/bettercap/caplets") / (name if name.endswith(".cap") else name + ".cap"),
            Path("/usr/share/bettercap/caplets") / (name if name.endswith(".cap") else name + ".cap"),
        ]
        self._caplet_cache = next((p for p in candidates if p.is_file()), None)
        return self._caplet_cache

    @staticmethod
    def _parse_caplet(path: Path) -> dict[str, str]:
        vals = {"address": "127.0.0.1", "port": "8081"}
        pat = re.compile(r"^\s*set\s+api\.rest\.(address|port|username|password)\s+(.+?)\s*$", re.I)
        for line in path.read_text(errors="replace").splitlines():
            m = pat.match(line)
            if m:
                vals[m.group(1).lower()] = m.group(2).strip().strip('"\'')
        if vals.get("address") in ("0.0.0.0", "::", ""):
            vals["address"] = "127.0.0.1"
        return vals

    def _config(self, caplet: Path) -> dict[str, str]:
        try:
            st = caplet.stat()
            sig = (str(caplet), int(st.st_mtime_ns), int(st.st_size))
            if sig == self._caplet_sig and self._caplet_cfg is not None:
                return dict(self._caplet_cfg)
            cfg = self._parse_caplet(caplet)
            self._caplet_sig = sig
            self._caplet_cfg = dict(cfg)
            return cfg
        except Exception:
            if self._caplet_cfg is not None:
                return dict(self._caplet_cfg)
            raise

    def collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        caplet = self._active_caplet()
        if not caplet:
            return {"bettercap.api.state": "caplet_not_found"}
        try:
            cfg = self._config(caplet)
        except Exception:
            return {"bettercap.api.state": "caplet_parse_error"}

        url = f"http://{cfg['address']}:{cfg['port']}/api/session"
        req = urllib.request.Request(url)
        if cfg.get("username") is not None:
            token = base64.b64encode(f"{cfg.get('username','')}:{cfg.get('password','')}".encode()).decode()
            req.add_header("Authorization", "Basic " + token)
        try:
            with urllib.request.urlopen(req, timeout=1.5) as r:
                obj = json.loads(r.read(2_000_000))
            values["bettercap.api.state"] = "available"
            wifi = obj.get("wifi") if isinstance(obj, dict) else None
            if isinstance(wifi, dict):
                aps = wifi.get("aps")
                clients = wifi.get("clients")
                if isinstance(aps, list):
                    values["wifi.aps"] = aps
                    values["wifi.ap_count"] = len(aps)
                    values["wifi.client_count"] = sum(len(x.get("clients") or []) for x in aps if isinstance(x, dict))
                    values["wifi.hidden_count"] = sum(
                        1 for x in aps if isinstance(x, dict) and (not x.get("hostname") or x.get("hostname") == "<hidden>")
                    )
                    values["wifi.vendor_count"] = len({x.get("vendor") for x in aps if isinstance(x, dict) and x.get("vendor")})
                    values["wifi.handshake_ap_count"] = sum(1 for x in aps if isinstance(x, dict) and bool(x.get("handshake")))
                if isinstance(clients, list):
                    values["wifi.client_count"] = len(clients)
        except Exception as exc:
            values["bettercap.api.state"] = "unavailable"
            values["bettercap.api.error"] = type(exc).__name__
        return values
