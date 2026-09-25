from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any


_TOKEN = re.compile(r"^[A-Za-z0-9_.:-]{1,192}$")


class ProviderPreferenceManager:
    """Persistent owner preference for capability providers.

    Preferences are policy only. They do not themselves enable a plugin, start a
    service, switch hardware ownership or perform failover.
    """

    schema = 1

    def __init__(
        self,
        path: str = "/var/lib/beastagotchi/provider-preferences.json",
        *,
        clock=time.time,
    ) -> None:
        self.path = Path(path)
        self.clock = clock

    def _default(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "preferences": {},
            "updated_at": None,
            "updated_by": None,
        }

    @staticmethod
    def _clean_token(value: Any, label: str) -> str:
        text = str(value or "").strip()
        if not _TOKEN.fullmatch(text):
            raise ValueError(f"invalid {label}")
        return text

    def _read(self) -> dict[str, Any]:
        row = self._default()
        try:
            obj = json.loads(self.path.read_text())
            if isinstance(obj, dict):
                raw = obj.get("preferences")
                if isinstance(raw, dict):
                    clean: dict[str, dict[str, Any]] = {}
                    for cap, entry in list(raw.items())[:256]:
                        try:
                            c = self._clean_token(cap, "capability")
                        except ValueError:
                            continue
                        if not isinstance(entry, dict):
                            continue
                        provider = str(entry.get("provider") or "").strip()
                        if not _TOKEN.fullmatch(provider):
                            continue
                        clean[c] = {
                            "provider": provider,
                            "set_at": entry.get("set_at"),
                            "set_by": str(entry.get("set_by") or "")[:160] or None,
                        }
                    row["preferences"] = clean
                row["updated_at"] = obj.get("updated_at")
                row["updated_by"] = str(obj.get("updated_by") or "")[:160] or None
        except Exception:
            pass
        row["schema"] = self.schema
        return row

    def _write(self, row: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(row, indent=2, sort_keys=True, default=str) + "\n")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)

    def snapshot(self) -> dict[str, Any]:
        row = self._read()
        simple = {
            capability: str(entry.get("provider") or "")
            for capability, entry in row["preferences"].items()
            if str(entry.get("provider") or "")
        }
        return {
            **row,
            "values": simple,
            "count": len(simple),
        }

    def set(self, capability: str, provider: str, *, actor: str = "owner") -> dict[str, Any]:
        capability = self._clean_token(capability, "capability")
        provider = self._clean_token(provider, "provider")
        row = self._read()
        now = float(self.clock())
        row["preferences"][capability] = {
            "provider": provider,
            "set_at": now,
            "set_by": str(actor or "owner")[:160],
        }
        row["updated_at"] = now
        row["updated_by"] = str(actor or "owner")[:160]
        self._write(row)
        return self.snapshot()

    def clear(self, capability: str, *, actor: str = "owner") -> dict[str, Any]:
        capability = self._clean_token(capability, "capability")
        row = self._read()
        if capability in row["preferences"]:
            row["preferences"].pop(capability, None)
            row["updated_at"] = float(self.clock())
            row["updated_by"] = str(actor or "owner")[:160]
            self._write(row)
        return self.snapshot()

    def state_patch(self) -> dict[str, Any]:
        row = self.snapshot()
        return {
            "providers.preferences": dict(row["values"]),
            "providers.preference_count": int(row["count"]),
            "providers.preferences.updated_at": row["updated_at"],
            "providers.preferences.updated_by": row["updated_by"],
            "providers.preferences.entries": dict(row["preferences"]),
        }
