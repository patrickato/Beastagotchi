from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dependency_resolver import DependencyCapabilityResolver


# Curated possibilities, not a base dependency list and not an installer.
# Integrations are capability-oriented so Beast features depend on what a
# backend provides rather than importing one external project everywhere.
INTEGRATIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "vector-cairo-svg", "label": "Cairo + SVG Visual Assets",
        "category": "visual", "lane": "os_packages", "maturity": "candidate",
        "provides": ["visual.vector", "visual.svg", "visual.high_quality_2d"],
        "requires": ["package:python3-cairo", "package:librsvg2-bin"],
        "activation": "on_demand", "isolation": "in_process_adapter",
        "purpose": "High-quality vector assets and scalable scene material without replacing the framebuffer path.",
    },
    {
        "id": "system-psutil", "label": "psutil Rich System Telemetry",
        "category": "telemetry", "lane": "os_packages", "maturity": "candidate",
        "provides": ["system.telemetry.rich", "process.telemetry.rich"],
        "requires": ["package:python3-psutil"],
        "activation": "collector_adapter", "isolation": "in_process_adapter",
        "purpose": "Richer process/system metrics while Beast canonical state remains the source of truth.",
    },
    {
        "id": "hardware-pyudev", "label": "udev Hotplug Discovery",
        "category": "hardware", "lane": "os_packages", "maturity": "candidate",
        "provides": ["hardware.hotplug", "hardware.udev_events"],
        "requires": ["package:python3-pyudev"],
        "activation": "event_adapter", "isolation": "in_process_adapter",
        "purpose": "Event-driven USB/serial/input/radio arrival and removal instead of repeated inventory polling.",
    },
    {
        "id": "input-evdev", "label": "Linux evdev Input",
        "category": "input", "lane": "os_packages", "maturity": "candidate",
        "provides": ["input.evdev", "input.hotplug_devices"],
        "requires": ["package:python3-evdev"],
        "optional_requirements": ["capability:hardware.hotplug"],
        "activation": "event_adapter", "isolation": "in_process_adapter",
        "purpose": "Unified buttons, rotary encoders, keyboards and alternate input devices through Linux input events.",
    },
    {
        "id": "gpio-libgpiod", "label": "libgpiod GPIO Backend",
        "category": "hardware", "lane": "os_packages", "maturity": "candidate",
        "provides": ["gpio.character_device", "hardware.gpio_events"],
        "requires": ["package:python3-libgpiod", "gpio.available"],
        "optional_requirements": ["package:gpiod"],
        "activation": "hardware_adapter", "isolation": "in_process_adapter",
        "purpose": "Modern Linux GPIO backend for buttons, LEDs, haptics, fans and accessories.",
    },
    {
        "id": "i2c-smbus", "label": "Linux SMBus/I2C Backend",
        "category": "hardware", "lane": "os_packages", "maturity": "candidate",
        "provides": ["hardware.i2c_access"],
        "requires": ["package:python3-smbus", "i2c"],
        "optional_requirements": ["package:i2c-tools"],
        "activation": "hardware_adapter", "isolation": "in_process_adapter",
        "purpose": "Standard I2C access for power monitors, sensors, RTCs and expansion hardware.",
    },
    {
        "id": "bluetooth-bleak", "label": "Bleak / BlueZ BLE Backend",
        "category": "bluetooth", "lane": "os_packages", "maturity": "candidate",
        "provides": ["bluetooth.ble_scan", "bluetooth.gatt_client", "hardware.ble_sensor"],
        "requires": ["package:python3-bleak", "package:bluez", "bluetooth.adapter"],
        "activation": "capability_adapter", "isolation": "in_process_adapter",
        "purpose": "Passive BLE discovery plus opt-in GATT sensor/accessory integrations using BlueZ.",
    },
    {
        "id": "discovery-zeroconf", "label": "mDNS / Zeroconf Discovery",
        "category": "connectivity", "lane": "os_packages", "maturity": "candidate",
        "provides": ["discovery.local_mdns", "companion.local_discovery"],
        "requires": ["package:python3-zeroconf"],
        "optional_requirements": ["network.route"],
        "activation": "on_demand", "isolation": "in_process_adapter",
        "purpose": "Zero-configuration discovery of Beast Studio and local companion services without cloud registration.",
    },
    {
        "id": "studio-aiohttp", "label": "aiohttp Async Studio Transport",
        "category": "studio", "lane": "os_packages", "maturity": "candidate",
        "provides": ["studio.async_http", "studio.websocket", "companion.live_stream"],
        "requires": ["package:python3-aiohttp"],
        "activation": "future_server_adapter", "isolation": "process_boundary_preferred",
        "purpose": "Mature async HTTP/WebSocket transport for the future Studio controller split and live companions.",
    },
    {
        "id": "filesystem-watchdog", "label": "Watchdog File Events",
        "category": "platform", "lane": "os_packages", "maturity": "candidate",
        "provides": ["filesystem.events", "content.hot_reload"],
        "requires": ["package:python3-watchdog"],
        "activation": "event_adapter", "isolation": "in_process_adapter",
        "purpose": "Event-driven Pack/theme/library/config discovery instead of periodic directory scans where appropriate.",
    },
    {
        "id": "media-ffmpeg", "label": "FFmpeg Media Pipeline",
        "category": "media", "lane": "external_process", "maturity": "candidate",
        "provides": ["media.transcode", "media.audio_decode", "media.video_decode", "rare.cinematic_assets"],
        "requires": ["package:ffmpeg", "executable:ffmpeg", "executable:ffprobe"],
        "activation": "on_demand_subprocess", "isolation": "sandboxed_process",
        "purpose": "Prepare/decode media and authored Rare Moment assets without implementing codecs inside Beast.",
    },
    {
        "id": "capsule-zbar", "label": "ZBar Capsule Receiver",
        "category": "capsules", "lane": "external_process", "maturity": "candidate",
        "provides": ["capsule.qr_receive", "barcode.decode"],
        "requires": ["package:zbar-tools", "executable:zbarimg"],
        "activation": "on_demand_subprocess", "isolation": "sandboxed_process",
        "purpose": "Decode received Capsule QR images using a mature barcode implementation instead of writing a decoder.",
    },
    {
        "id": "runtime-bubblewrap", "label": "Bubblewrap App Sandbox",
        "category": "security", "lane": "os_packages", "maturity": "candidate",
        "provides": ["runtime.sandbox.namespaces", "pack.code_isolation"],
        "requires": ["package:bubblewrap", "executable:bwrap"],
        "activation": "runtime_service", "isolation": "host_security_primitive",
        "purpose": "Namespace sandbox option for future code-bearing Apps/Renderer/Integration Packs.",
    },
    {
        "id": "bus-mqtt", "label": "MQTT Beast Bus Adapter",
        "category": "integration", "lane": "os_packages", "maturity": "candidate",
        "provides": ["beastbus.mqtt", "integration.home_automation", "satellite.pubsub"],
        "requires": ["package:python3-paho-mqtt"],
        "optional_requirements": ["network.route"],
        "activation": "optional_service", "isolation": "adapter_service",
        "purpose": "Optional bridge for Home Assistant, local brokers, ESP32/Pi satellites and lab integrations.",
    },
    {
        "id": "location-gpsd", "label": "gpsd Location Service",
        "category": "location", "lane": "os_service", "maturity": "established",
        "provides": ["location.position", "location.fix", "location.satellites", "location.receiver_or_gpsd"],
        "requires": ["package:gpsd"],
        "optional_requirements": ["service:gpsd.service"],
        "activation": "provider_service", "isolation": "external_service",
        "purpose": "Established multi-client GPS provider so Beast does not own serial receiver details.",
    },
)


class IntegrationCatalog:
    """Read-only catalog of useful external software Beast can leverage.

    It never installs, enables, downloads or executes anything.  The existing
    DependencyCapabilityResolver supplies availability evidence so a future
    Studio UI can explain what is already usable and what an explicit
    transaction would need to acquire.
    """

    schema = 1

    def __init__(self, state, resolver: DependencyCapabilityResolver | None = None) -> None:
        self.state = state
        self.resolver = resolver or DependencyCapabilityResolver(state)

    def entries(self) -> list[dict[str, Any]]:
        rows = [deepcopy(x) for x in INTEGRATIONS]
        graph = self.resolver.resolve_components(rows)
        resolved = graph.get("components") or {}
        for row in rows:
            status = resolved.get(row["id"], {}) if isinstance(resolved, dict) else {}
            if isinstance(status, dict):
                row.update(status)
            row["install_policy"] = "explicit_transaction_only"
            row["auto_install"] = False
            row["base_dependency"] = False
        return rows

    def snapshot(self) -> dict[str, Any]:
        items = self.entries()
        counts: dict[str, int] = {}
        for row in items:
            key = str(row.get("requirements_status") or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return {
            "schema": self.schema,
            "mode": "read_only_catalog",
            "execution_enabled": False,
            "automatic_install_enabled": False,
            "count": len(items),
            "status_counts": counts,
            "lanes": sorted({str(x.get("lane")) for x in items if x.get("lane")}),
            "categories": sorted({str(x.get("category")) for x in items if x.get("category")}),
            "items": items,
        }
