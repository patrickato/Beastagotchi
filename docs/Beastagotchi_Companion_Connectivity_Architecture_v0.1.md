# Beastagotchi Companion & Connectivity Architecture v0.1

## Principle
If a useful interface/capability exists natively in the underlying Pwnagotchi environment, installing Beastagotchi should not make it disappear. Beast should preserve direct access, safely expose it, or provide an adapter with equivalent capability where practical.

## Companion surfaces
- physical TFT/HDMI/DSI Beast UI;
- responsive local Beast Studio/WebUI;
- native Pwnagotchi WebUI access;
- Korrie71 Theme Manager WebUI when installed;
- future installable PWA/phone-home-screen Beast companion;
- external-display Command Center.

## Connectivity paths
Support/capability discovery should account for:
- Ethernet/docked LAN;
- Wi-Fi management connectivity and optional isolated management AP;
- USB networking/RNDIS/gadget paths provided by the underlying platform;
- Bluetooth/BLE adapter presence and future explicitly designed companion workflows;
- optional second Wi-Fi adapter roles without disturbing the radio dedicated to Pwnagotchi.

No cloud account or mandatory Internet service is required for normal Beast operation.

## Settings architecture
Settings should have one canonical backend/API and multiple clients rather than separate conflicting copies in TFT, WebUI and phone UI. Clients may present different subsets appropriate to screen size, touch technology and risk level.

Deep configuration, theme/layout authoring, package management, backups, logs, diagnostics and update policy are WebUI-first. Critical field actions, presentation switching, health/attention, quick plugin/app toggles and recovery entry points remain reachable on-device.
