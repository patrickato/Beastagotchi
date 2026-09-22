from __future__ import annotations

from typing import Any

from .plugin_broker import DISPLAY_OWNERS, PROTECTED_PLUGINS


# These bindings describe where useful output from common Pwnagotchi plugins is
# already represented in Beast's canonical state. They do not claim that a
# plugin is the exclusive source of a value; Beast may prefer a better native
# collector (for example gpsd) while still integrating the plugin's capability.
KNOWN_BINDINGS: dict[str, dict[str, Any]] = {
    "gps": {"namespaces": ["gps."], "role": "location", "integration": "canonical"},
    "gpsd": {"namespaces": ["gps."], "role": "location", "integration": "canonical"},
    "memtemp": {"namespaces": ["system.cpu.", "system.memory.", "system.temp."], "role": "system_telemetry", "integration": "canonical"},
    "session-stats": {"namespaces": ["pwnagotchi."], "role": "session_stats", "integration": "canonical"},
    "session_stats": {"namespaces": ["pwnagotchi."], "role": "session_stats", "integration": "canonical"},
    "ups_lite": {"namespaces": ["power."], "role": "power", "integration": "adapter"},
    "pisugar": {"namespaces": ["power."], "role": "power", "integration": "adapter"},
    "bt-tether": {"namespaces": ["network."], "role": "connectivity", "integration": "managed"},
    "bt_tether": {"namespaces": ["network."], "role": "connectivity", "integration": "managed"},
    "webgpsmap": {"namespaces": ["gps.", "expedition."], "role": "map", "integration": "superseded_by_beast"},
    "theme_manager": {"namespaces": [], "role": "legacy_ui", "integration": "isolated"},
    "fancygotchi": {"namespaces": [], "role": "legacy_ui", "integration": "isolated"},
    "beast_bridge": {"namespaces": ["pwnagotchi.", "radio.hop."], "role": "bridge", "integration": "native"},
}


class PluginIntegrationEngine:
    """Normalize Pwnagotchi plugin inventory for Beast UI/Studio.

    A plugin may be installed and enabled without having a Beast data adapter.
    Beast makes that distinction visible instead of pretending all plugins are
    equally integrated.  This catalog is the basis for a future transactional
    config broker/toggle UI with rollback.
    """

    def __init__(self, state) -> None:
        self.state = state

    @staticmethod
    def _binding(name: str) -> dict[str, Any]:
        key = name.lower().replace(" ", "_")
        direct = KNOWN_BINDINGS.get(key)
        if direct:
            return dict(direct)
        # tolerate common hyphen/underscore spelling differences
        direct = KNOWN_BINDINGS.get(key.replace("-", "_")) or KNOWN_BINDINGS.get(key.replace("_", "-"))
        return dict(direct or {"namespaces": [], "role": "plugin", "integration": "config_only"})

    def tick(self) -> dict[str, Any]:
        raw = self.state.get("platform.plugins", []) or []
        rows: list[dict[str, Any]] = []
        enabled = integrated = display_isolated = 0
        enabled_display_conflicts: list[str] = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                if not name:
                    continue
                bind = self._binding(name)
                is_enabled = bool(item.get("enabled"))
                if is_enabled:
                    enabled += 1
                level = str(bind.get("integration") or "config_only")
                if level not in {"config_only", "isolated"}:
                    integrated += 1
                if level == "isolated":
                    display_isolated += 1
                normalized = name.lower().replace("-", "_")
                protected = normalized in {x.replace("-", "_") for x in PROTECTED_PLUGINS}
                display_owner = normalized in {x.replace("-", "_") for x in DISPLAY_OWNERS}
                if display_owner and is_enabled:
                    enabled_display_conflicts.append(name)
                rows.append({
                    **item,
                    "role": bind.get("role", "plugin"),
                    "integration": level,
                    "namespaces": list(bind.get("namespaces") or []),
                    "display_policy": "beast_adapter" if level not in {"isolated", "config_only"} else "legacy_isolated" if level == "isolated" else "config_only",
                    "status": "enabled" if is_enabled else "disabled",
                    "protected": protected,
                    "legacy_display_owner": display_owner,
                    "toggle_capable": bool(item.get("configured") or item.get("installed_custom")),
                    "restart_required": None,  # learned registry can make this plugin-specific later
                })
        rows.sort(key=lambda r: (not bool(r.get("enabled")), str(r.get("name", "")).lower()))
        return {
            "plugins.catalog": rows,
            "plugins.catalog_count": len(rows),
            "plugins.enabled_count": enabled,
            "plugins.integrated_count": integrated,
            "plugins.display_isolated_count": display_isolated,
            "plugins.display_conflicts_enabled": enabled_display_conflicts,
            "plugins.display_conflict_count": len(enabled_display_conflicts),
            "plugins.integration_policy": "canonical_data_first",
        }
