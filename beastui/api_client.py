from __future__ import annotations

import json
import time
import urllib.request
import urllib.parse
from typing import Any


class BeastAPI:
    def __init__(self, base: str = "http://127.0.0.1:8090", timeout: float = 1.5) -> None:
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.last_ok = 0.0
        self.last_error: str | None = None

    def _get(self, path: str) -> Any:
        with urllib.request.urlopen(self.base + path, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def state(self) -> dict[str, Any]:
        try:
            obj = self._get("/state?meta=0")
            self.last_ok = time.time(); self.last_error = None
            return obj if isinstance(obj, dict) else {}
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {}

    def live(self, events: int = 24) -> dict[str, Any]:
        """Fetch state + durable event feed in one localhost transaction."""
        try:
            obj = self._get(f"/live?events={int(events)}")
            self.last_ok = time.time(); self.last_error = None
            return obj if isinstance(obj, dict) else {}
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {}

    def events(self, limit: int = 24) -> list[dict[str, Any]]:
        try:
            obj = self._get(f"/events?limit={int(limit)}&transient=0")
            return obj if isinstance(obj, list) else []
        except Exception:
            return []

    def history(self, key: str, limit: int = 60) -> list[dict[str, Any]]:
        try:
            obj = self._get(f"/history?key={urllib.parse.quote(key)}&limit={int(limit)}")
            return (obj or {}).get("samples") or []
        except Exception:
            return []

    def history_batch(self, keys: tuple[str, ...] | list[str], limit: int = 64,
                      *, channel_limit: int = 90, expedition_points: int = 256) -> dict[str, Any]:
        try:
            joined = ",".join(str(k) for k in keys)
            q = urllib.parse.urlencode({
                "keys": joined,
                "limit": int(limit),
                "channel": int(channel_limit),
                "expedition_points": int(expedition_points),
            })
            obj = self._get("/history-batch?" + q)
            return obj if isinstance(obj, dict) else {}
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {}

    def telemetry(self, keys: list[str] | tuple[str, ...] | None = None) -> list[dict[str, Any]]:
        try:
            q = ""
            if keys:
                q = "?" + urllib.parse.urlencode({"keys": ",".join(keys)})
            obj = self._get("/telemetry" + q)
            return obj if isinstance(obj, list) else []
        except Exception:
            return []

    def platform_bundle(self) -> dict[str, Any]:
        try:
            obj=self._get("/platform-bundle")
            return obj if isinstance(obj,dict) else {}
        except Exception as exc:
            self.last_error=type(exc).__name__;return {}

    def library(self, query: str = "", limit: int = 50) -> dict[str, Any]:
        try:
            q=urllib.parse.urlencode({"q":query,"limit":int(limit)})
            obj=self._get("/library?"+q)
            return obj if isinstance(obj,dict) else {}
        except Exception:return {}

    def library_item(self, doc_id: str) -> dict[str, Any]:
        try:
            q=urllib.parse.urlencode({"id":str(doc_id)})
            obj=self._get("/library-item?"+q)
            return obj if isinstance(obj,dict) else {}
        except Exception:return {}

    def search(self, query: str, limit: int = 12) -> dict[str, Any]:
        try:
            q=urllib.parse.urlencode({"q":query,"limit":int(limit)})
            obj=self._get("/search?"+q)
            return obj if isinstance(obj,dict) else {}
        except Exception:return {}

    def backup_inspect(self, name: str) -> dict[str, Any]:
        try:
            q=urllib.parse.urlencode({"name":str(name)})
            obj=self._get("/backup-inspect?"+q)
            return obj if isinstance(obj,dict) else {}
        except Exception as exc:
            self.last_error=type(exc).__name__;return {}

    def plugins(self) -> dict[str, Any]:
        try:
            obj = self._get("/plugins")
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def capsule_export(
        self,
        *,
        capsule_type: str = "lineage",
        beast_id: str | None = None,
        include_name: bool = True,
        include_achievements: bool = False,
        include_appearance: bool = True,
        qr_chars: int = 220,
    ) -> dict[str, Any]:
        try:
            q = {
                "type": str(capsule_type or "lineage"),
                "name": "1" if include_name else "0",
                "achievements": "1" if include_achievements else "0",
                "appearance": "1" if include_appearance else "0",
                "qr_chars": max(128, min(2400, int(qr_chars))),
            }
            if beast_id:
                q["beast_id"] = str(beast_id)
            obj = self._get("/capsule/export?" + urllib.parse.urlencode(q))
            return obj if isinstance(obj, dict) else {}
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {}
