# Beastagotchi ↔ Korrie71 Theme Manager Integration Spec v0.1

## Problem
Both Beast UI and `Korrie71/pwnagotchi-theme-manager` can own the 480x320 framebuffer and raw touchscreen. Running both as independent display owners creates undefined rendering/input races. Theme Manager also provides a valuable Web UI, theme catalog/editor, touch menu, plugin controls, radar, cracking views, achievements and node support that should not be discarded.

## Principle
Both projects may be installed, enabled and healthy at the same time, but only one component owns physical display/touch presentation at a time.

## Proposed display ownership broker
Define one lease with explicit owner:
- `pwn-native`
- `korrie-theme-manager`
- `beast-ui`

A lease records owner, acquisition time, heartbeat and release method. Beast's current conflict gate becomes the first implementation of this broker.

## Theme Manager integration modes
Propose an upstream-friendly Theme Manager setting/API:
- `full`: current behavior; Theme Manager owns render + touch.
- `web_only`: Web UI, theme storage/editor and safe APIs stay active; framebuffer/touch hooks are not installed.
- `managed`: display hooks are active only while the ownership broker grants the Theme Manager lease.

The exact names are negotiable with Korrie; the capability boundary is the important part.

## Beast modes
### Korrie presentation mode
Pwnagotchi + Theme Manager own the screen. Beast Core, Beast Studio, telemetry/history, expeditions, backups, updater, hardware services and Web UI continue running headlessly.

### Beast presentation mode
Beast UI owns framebuffer/touch. Theme Manager remains loaded in `web_only/managed` mode so its editor, theme assets and APIs remain usable.

### Native recovery mode
Beast and Theme Manager release display ownership and normal Pwnagotchi presentation resumes.

## Interop APIs worth adding
- Theme list/current theme/theme JSON read endpoint.
- Request theme activation.
- Render/preview endpoint using synthetic or sanitized data.
- Capability/status endpoint reporting render-hook and touch-hook ownership.
- Export/import theme pack endpoint.
- Event notifications for theme changed/layout changed.

## Longer-term merge path
Do not copy two rendering engines into each other immediately. First share contracts: theme metadata, palette/effect descriptors, face packs, preview images and ownership state. Once stable, build translators so Beast can import selected Theme Manager theme assets/ideas while Theme Manager can consume Beast telemetry through a narrow adapter.
