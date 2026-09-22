from __future__ import annotations

import copy
import json
import time
import tomllib
from pathlib import Path
from typing import Any

from .base import Collector


_SECRET_WORDS = ("password", "passwd", "secret", "token", "api_key", "apikey", "private", "credential", "key")


def _safe_field_rows(opts: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Describe plugin config without leaking credentials through Beast state."""
    if not isinstance(opts, dict):
        return []
    rows: list[dict[str, Any]] = []
    for key, value in sorted(opts.items()):
        if key == "enabled":
            continue
        lk = str(key).lower()
        sensitive = any(word in lk for word in _SECRET_WORDS)
        typ = type(value).__name__
        if isinstance(value, bool): typ = "bool"
        elif isinstance(value, int) and not isinstance(value, bool): typ = "int"
        elif isinstance(value, float): typ = "float"
        elif isinstance(value, str): typ = "str"
        elif isinstance(value, list): typ = "list"
        elif isinstance(value, dict): typ = "object"
        preview: Any = None
        if not sensitive and isinstance(value, (bool, int, float, str)):
            preview = value
        rows.append({"key": str(key), "type": typ, "sensitive": sensitive, "preview": preview})
    return rows


class PwnagotchiCollector(Collector):
    name = "pwnagotchi"
    interval = 2.0
    priority = 30

    def __init__(self, config_path: str = "/etc/pwnagotchi/config.toml") -> None:
        self.config_path = Path(config_path)
        self.handshake_dir = Path("/etc/pwnagotchi/handshakes")
        self.session_dir = Path("/etc/pwnagotchi/sessions")
        self.bridge = Path("/run/beastagotchi/pwnagotchi_bridge.json")
        self.custom_plugin_dir = Path("/etc/pwnagotchi/custom-plugins")
        self.conf_d = Path("/etc/pwnagotchi/conf.d")
        self._cfg_cache: dict[str, Any] = {}
        self._cfg_sig: tuple[int, int] | None = None
        self._inventory_cache: dict[str, Any] = {}
        self._inventory_at = 0.0
        self._cache_summary_value = (0, 0, 0, 0)
        self._cache_summary_at = 0.0
        self._session_cache: dict[str, Any] = {}
        self._session_sig: tuple[str, int, int] | None = None

    def _config(self) -> dict[str, Any]:
        try:
            st = self.config_path.stat()
            sig = (int(st.st_mtime_ns), int(st.st_size))
            if sig == self._cfg_sig:
                return copy.deepcopy(self._cfg_cache)
            obj = tomllib.loads(self.config_path.read_text(errors="replace"))
            self._cfg_cache = obj if isinstance(obj, dict) else {}
            self._cfg_sig = sig
            return copy.deepcopy(self._cfg_cache)
        except Exception:
            return copy.deepcopy(self._cfg_cache)

    def _latest_session_stats(self) -> dict[str, Any]:
        try:
            files = sorted(self.session_dir.glob("stats_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not files:
                return {}
            fp = files[0]
            st = fp.stat()
            sig = (str(fp), int(st.st_mtime_ns), int(st.st_size))
            if sig == self._session_sig:
                return copy.deepcopy(self._session_cache)
            obj = json.loads(fp.read_text(errors="replace"))
            data = obj.get("data", {}) if isinstance(obj, dict) else {}
            row = data[sorted(data.keys())[-1]] if data else {}
            self._session_sig = sig
            self._session_cache = row if isinstance(row, dict) else {}
            return copy.deepcopy(self._session_cache)
        except Exception:
            return copy.deepcopy(self._session_cache)

    def _cache_summary(self, *, max_age: float = 10.0) -> tuple[int, int, int, int]:
        now = time.monotonic()
        if now - self._cache_summary_at < max_age:
            return self._cache_summary_value
        ap_count = client_count = handshake_count = hidden_count = 0
        cache = self.handshake_dir / "cache"
        try:
            for p in cache.glob("*.apcache"):
                try:
                    obj = json.loads(p.read_text(errors="replace"))
                    ap_count += 1
                    client_count += len(obj.get("clients") or [])
                    handshake_count += 1 if obj.get("handshake") else 0
                    hidden_count += 1 if not obj.get("hostname") or obj.get("hostname") == "<hidden>" else 0
                except Exception:
                    pass
        except Exception:
            pass
        self._cache_summary_value = (ap_count, client_count, handshake_count, hidden_count)
        self._cache_summary_at = now
        return self._cache_summary_value

    def _inventory(self, main: dict[str, Any], *, max_age: float = 30.0) -> dict[str, Any]:
        now = time.monotonic()
        if now - self._inventory_at < max_age and self._inventory_cache:
            return copy.deepcopy(self._inventory_cache)
        plugin_files: dict[str, str] = {}
        try:
            for fp in self.custom_plugin_dir.glob("*.py"):
                plugin_files[fp.stem] = str(fp)
        except Exception:
            pass
        try:
            dropins = [str(fp) for fp in sorted(self.conf_d.glob("*.toml"))]
        except Exception:
            dropins = []
        configured = main.get("plugins") or {}
        if not isinstance(configured, dict):
            configured = {}
        plugins = []
        for name in sorted(set(configured) | set(plugin_files)):
            opts = configured.get(name) if isinstance(configured, dict) else None
            plugins.append({
                "name": name,
                "enabled": bool(opts.get("enabled", False)) if isinstance(opts, dict) else False,
                "configured": isinstance(opts, dict),
                "installed_custom": name in plugin_files,
                "path": plugin_files.get(name),
                "config_fields": _safe_field_rows(opts),
            })
        repos = main.get("custom_plugin_repos") or []
        if not isinstance(repos, list):
            repos = []
        out = {
            "platform.plugins": plugins,
            "plugins.repos": [str(x) for x in repos],
            "plugins.repo_count": len(repos),
            "plugins.configured_count": sum(1 for x in plugins if x.get("configured")),
            "plugins.enabled_count": sum(1 for x in plugins if x.get("enabled")),
            "plugins.installed_custom_count": sum(1 for x in plugins if x.get("installed_custom")),
            "plugins.custom_dir": str(self.custom_plugin_dir),
            "plugins.custom_count": len(plugin_files),
            "plugins.conf_d": str(self.conf_d),
            "plugins.dropins": dropins,
        }
        self._inventory_cache = copy.deepcopy(out)
        self._inventory_at = now
        return out

    def collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        cfg = self._config()
        main = cfg.get("main", {}) if isinstance(cfg, dict) else {}
        bc = cfg.get("bettercap", {}) if isinstance(cfg, dict) else {}
        if bc.get("handshakes"):
            self.handshake_dir = Path(str(bc["handshakes"]))

        values.update(self._inventory(main if isinstance(main, dict) else {}))

        stats = self._latest_session_stats()
        mapping = {
            "num_peers": "peers",
            "num_handshakes": "handshakes",
            "num_deauths": "deauths",
            "num_associations": "assocs",
        }
        for src, dst in mapping.items():
            if src in stats:
                values[f"pwnagotchi.{dst}"] = stats[src]

        # Pwnagotchi's on-disk cache is historical/capture metadata, not the
        # authoritative live AP list. Keep it in its own namespace so it can
        # never race Bettercap's live wifi.* keys.
        aps, clients, cache_hs, hidden = self._cache_summary()
        values["pwnagotchi.cache.ap_count"] = aps
        values["pwnagotchi.cache.client_count"] = clients
        values["pwnagotchi.cache.handshake_ap_count"] = cache_hs
        values["pwnagotchi.cache.hidden_count"] = hidden
        values["captures.total"] = cache_hs
        values["captures.directory"] = str(self.handshake_dir)
        if "pwnagotchi.handshakes" not in values:
            values["pwnagotchi.handshakes"] = cache_hs

        return values
