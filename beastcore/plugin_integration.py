from __future__ import annotations

from typing import Any

from .plugin_broker import DISPLAY_OWNERS, PROTECTED_PLUGINS
from .theme_manager_interop import ThemeManagerProbe
from .dependency_resolver import DependencyCapabilityResolver


# These bindings describe where useful output from common Pwnagotchi plugins is
# already represented in Beast's canonical state. They do not claim that a
# plugin is the exclusive source of a value; Beast may prefer a better native
# collector (for example gpsd) while still integrating the plugin's capability.
KNOWN_BINDINGS: dict[str, dict[str, Any]] = {
    # Jayofelony stock/default plugin family.  Requirement metadata here is a
    # declarative compatibility catalog, not permission to install packages or
    # start services.  The future Dependency & Capability Resolver will turn
    # these declarations into live SATISFIED / NEEDS_SETUP / CONFLICT states.
    "auto_backup": {
        "namespaces": ["backups."], "role": "backup", "integration": "superseded_by_beast",
        "provides": ["backup.pwnagotchi"], "requires": ["storage.writable"],
        "egress": "none", "credential_required": False,
    },
    "auto-update": {
        "namespaces": ["updates."], "role": "updater", "integration": "superseded_by_beast",
        "provides": ["update.pwnagotchi"], "requires": ["network.internet"],
        "egress": "software_update", "credential_required": False,
    },
    "bt-tether": {
        "namespaces": ["network."], "role": "connectivity", "integration": "managed",
        "provides": ["network.internet", "network.bluetooth_tether"],
        "requires": ["bluetooth.adapter", "phone.bluetooth_tether"],
        "provider_group": "internet", "egress": "network", "hardware_specific": True,
    },
    "bt_tether": {
        "namespaces": ["network."], "role": "connectivity", "integration": "managed",
        "provides": ["network.internet", "network.bluetooth_tether"],
        "requires": ["bluetooth.adapter", "phone.bluetooth_tether"],
        "provider_group": "internet", "egress": "network", "hardware_specific": True,
    },
    "fix_services": {
        "namespaces": [], "role": "pwnagotchi_resilience", "integration": "config_only",
        "provides": ["pwnagotchi.self_repair"], "requires": ["radio.onboard"],
        "egress": "none", "hardware_specific": True,
    },
    "gpio_buttons": {
        "namespaces": [], "role": "input", "integration": "config_only",
        "provides": ["input.buttons"], "requires": ["gpio.available"],
        "provider_group": "input", "egress": "none", "hardware_specific": True,
    },
    "gps": {
        "namespaces": ["gps."], "role": "location", "integration": "canonical",
        "provides": ["location.position", "location.fix", "location.satellites"],
        "requires": ["location.receiver_or_gpsd"], "provider_group": "location",
        "egress": "none", "hardware_specific": True,
    },
    "gpsd": {
        "namespaces": ["gps."], "role": "location", "integration": "canonical",
        "provides": ["location.position", "location.fix", "location.satellites"],
        "requires": ["gpsd.service"], "provider_group": "location", "egress": "none",
    },
    "gps_listener": {
        "namespaces": ["gps."], "role": "location", "integration": "config_only",
        "provides": ["location.position"], "requires": ["location.source"],
        "provider_group": "location", "egress": "none",
    },
    "grid": {
        "namespaces": ["peerdex."], "role": "peer_network", "integration": "config_only",
        "provides": ["peer.pwngrid_publish"], "requires": ["network.internet"],
        "egress": "peer_metadata", "credential_required": False,
    },
    "logtail": {
        "namespaces": ["incidents."], "role": "logs", "integration": "superseded_by_beast",
        "provides": ["logs.pwnagotchi_view"], "requires": ["pwnagotchi.logs"],
        "egress": "none",
    },
    "memtemp": {
        "namespaces": ["system.cpu.", "system.memory.", "system.temp."],
        "role": "system_telemetry", "integration": "canonical",
        "provides": ["system.telemetry"], "requires": [], "provider_group": "system_telemetry",
        "egress": "none",
    },
    "ohcapi": {
        "namespaces": [], "role": "external_capture_processor", "integration": "config_only",
        "provides": ["capture.external_processing"], "requires": ["network.internet", "capture.handshake"],
        "egress": "capture_artifacts", "credential_required": True,
    },
    "pisugar": {
        "namespaces": ["power."], "role": "power", "integration": "adapter",
        "provides": ["power.battery.telemetry"], "requires": ["hardware.pisugar"],
        "provider_group": "power", "egress": "none", "hardware_specific": True,
    },
    "pisugarx": {
        "namespaces": ["power."], "role": "power", "integration": "config_only",
        "provides": ["power.battery.telemetry"], "requires": ["hardware.pisugar"],
        "provider_group": "power", "egress": "none", "hardware_specific": True,
    },
    "pwncrack": {
        "namespaces": [], "role": "external_capture_processor", "integration": "config_only",
        "provides": ["capture.external_processing"], "requires": ["network.internet", "capture.handshake"],
        "egress": "capture_artifacts", "credential_required": True,
    },
    "pwndroid": {
        "namespaces": ["gps.", "network."], "role": "phone_provider", "integration": "config_only",
        "provides": ["location.position", "network.phone_link"],
        "requires": ["phone.pwndroid"], "provider_group": "location",
        "egress": "phone_link", "hardware_specific": True,
    },
    "session-stats": {
        "namespaces": ["pwnagotchi."], "role": "session_stats", "integration": "canonical",
        "provides": ["session.metrics"], "requires": [], "egress": "none",
    },
    "session_stats": {
        "namespaces": ["pwnagotchi."], "role": "session_stats", "integration": "canonical",
        "provides": ["session.metrics"], "requires": [], "egress": "none",
    },
    "switcher": {
        "namespaces": [], "role": "scheduler", "integration": "config_only",
        "provides": ["automation.legacy_scheduler"], "requires": ["systemd"],
        "egress": "command_dependent",
    },
    "ups_lite": {
        "namespaces": ["power."], "role": "power", "integration": "adapter",
        "provides": ["power.battery.telemetry"], "requires": ["hardware.ups_lite", "i2c"],
        "provider_group": "power", "egress": "none", "hardware_specific": True,
    },
    "ups_hat_c": {
        "namespaces": ["power."], "role": "power", "integration": "config_only",
        "provides": ["power.battery.telemetry"], "requires": ["hardware.ups_hat_c", "i2c"],
        "provider_group": "power", "egress": "none", "hardware_specific": True,
    },
    "webcfg": {
        "namespaces": [], "role": "configuration", "integration": "superseded_by_beast",
        "provides": ["pwnagotchi.runtime_config"], "requires": ["pwnagotchi.webui"],
        "egress": "local_web",
    },
    "webgpsmap": {
        "namespaces": ["gps.", "expedition."], "role": "map", "integration": "superseded_by_beast",
        "provides": ["map.handshake_history"], "requires": ["location.position"],
        "egress": "local_web",
    },
    "wigle": {
        "namespaces": [], "role": "external_location_exporter", "integration": "config_only",
        "provides": ["location.external_export"], "requires": ["network.internet", "location.position"],
        "egress": "location_and_network_metadata", "credential_required": True,
    },
    "wittypi": {
        "namespaces": ["power."], "role": "power", "integration": "config_only",
        "provides": ["power.battery.telemetry"], "requires": ["hardware.wittypi", "i2c"],
        "provider_group": "power", "egress": "none", "hardware_specific": True,
    },
    "wpa-sec": {
        "namespaces": [], "role": "external_capture_processor", "integration": "config_only",
        "provides": ["capture.external_processing"], "requires": ["network.internet", "capture.handshake"],
        "egress": "capture_artifacts", "credential_required": True,
    },

    # Presentation / Beast-native integration entries.
    "theme_manager": {
        "namespaces": [], "role": "legacy_ui", "integration": "isolated",
        "provides": ["presentation.theme_manager"], "requires": ["display.primary"],
        "provider_group": "presentation", "egress": "local_web",
    },
    "fancygotchi": {
        "namespaces": [], "role": "legacy_ui", "integration": "isolated",
        "provides": ["presentation.fancygotchi"], "requires": ["display.primary"],
        "provider_group": "presentation", "egress": "none",
    },
    "beast_bridge": {
        "namespaces": ["pwnagotchi.", "radio.hop."], "role": "bridge", "integration": "native",
        "provides": ["beast.pwnagotchi_bridge"], "requires": ["pwnagotchi.service"],
        "egress": "local_only",
    },
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
        self.theme_manager_probe = ThemeManagerProbe()
        self.requirements = DependencyCapabilityResolver(state)

    @staticmethod
    def _binding(name: str) -> dict[str, Any]:
        key = name.lower().replace(" ", "_")
        direct = KNOWN_BINDINGS.get(key)
        if direct:
            return dict(direct)
        # tolerate common hyphen/underscore spelling differences
        direct = KNOWN_BINDINGS.get(key.replace("-", "_")) or KNOWN_BINDINGS.get(key.replace("_", "-"))
        return dict(direct or {
            "namespaces": [], "role": "plugin", "integration": "config_only",
            "provides": [], "requires": [], "egress": "unknown",
        })

    def tick(self) -> dict[str, Any]:
        raw = self.state.get("platform.plugins", []) or []
        rows: list[dict[str, Any]] = []
        enabled = integrated = display_isolated = 0
        enabled_display_conflicts: list[str] = []
        theme_manager_interop: dict[str, Any] | None = None
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
                interop = None
                if normalized == "theme_manager":
                    interop = self.theme_manager_probe.probe(item.get("path"))
                    theme_manager_interop = interop
                rows.append({
                    **item,
                    "role": bind.get("role", "plugin"),
                    "integration": level,
                    "namespaces": list(bind.get("namespaces") or []),
                    "provides": list(bind.get("provides") or []),
                    "requires": list(bind.get("requires") or []),
                    "optional_requirements": list(bind.get("optional_requirements") or []),
                    "provider_group": bind.get("provider_group"),
                    "data_egress": str(bind.get("egress") or "unknown"),
                    "credential_required": bool(bind.get("credential_required", False)),
                    "hardware_specific": bool(bind.get("hardware_specific", False)),
                    "requirements_resolution": "catalog_only",
                    "display_policy": "beast_adapter" if level not in {"isolated", "config_only"} else "legacy_isolated" if level == "isolated" else "config_only",
                    "status": "enabled" if is_enabled else "disabled",
                    "protected": protected,
                    "legacy_display_owner": display_owner,
                    "toggle_capable": bool(item.get("configured") or item.get("installed_custom")),
                    "restart_required": None,  # learned registry can make this plugin-specific later
                    **({"interop": interop} if interop is not None else {}),
                })
        rows.sort(key=lambda r: (not bool(r.get("enabled")), str(r.get("name", "")).lower()))
        resolved = self.requirements.resolve_components(rows)
        component_results = resolved.get("components") or {}
        for row in rows:
            status = component_results.get(str(row.get("name") or ""))
            if isinstance(status, dict):
                row.update(status)
        used_by = resolved.get("used_by") or {}
        for row in rows:
            provider = f"component:{row.get('name')}"
            row["used_by"] = list(used_by.get(provider) or [])
        return {
            "plugins.catalog": rows,
            "plugins.catalog_count": len(rows),
            "plugins.enabled_count": enabled,
            "plugins.integrated_count": integrated,
            "plugins.display_isolated_count": display_isolated,
            "plugins.display_conflicts_enabled": enabled_display_conflicts,
            "plugins.display_conflict_count": len(enabled_display_conflicts),
            "plugins.integration_policy": "canonical_data_first",
            "plugins.requirements_model": "dependency_capability_resolver_v0.1_read_only",
            "plugins.requirements_executor_enabled": False,
            "plugins.requirements_summary": dict(resolved.get("summary") or {}),
            "plugins.requirements_providers": dict(resolved.get("providers") or {}),
            "plugins.requirements_used_by": dict(used_by),
            "plugins.theme_manager.inspectable": bool(theme_manager_interop and theme_manager_interop.get("inspectable")),
            "plugins.theme_manager.version": theme_manager_interop.get("version") if theme_manager_interop else None,
            "plugins.theme_manager.capabilities": list(theme_manager_interop.get("capabilities") or []) if theme_manager_interop else [],
            "plugins.theme_manager.managed_handoff_supported": bool(theme_manager_interop and theme_manager_interop.get("managed_handoff_supported")),
            "plugins.theme_manager.compatibility_handoff_evidence": bool(theme_manager_interop and theme_manager_interop.get("compatibility_handoff_evidence")),
        }
