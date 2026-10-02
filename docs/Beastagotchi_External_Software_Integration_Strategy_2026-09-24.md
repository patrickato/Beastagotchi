# Beastagotchi External Software / Integration Strategy — 2026-09-24

Status: active architecture guidance for v0.19+

## Principle

Beastagotchi should aggressively reuse proven Linux/Raspberry Pi/Python/browser software when it buys real capability.

The rule is **not** "avoid dependencies".

The rule is:

> External software may provide implementation capability; Beast contracts own product semantics.

A renderer library may draw. A BLE library may speak GATT. FFmpeg may decode media. gpsd may own GPS device I/O. bubblewrap/systemd may isolate a process. None of those should become the canonical definition of Beast state, progression, user policy, recovery or UI structure.

## Dependency lanes

### 1. Base Beast runtime

Very small, always-present, release-tested dependencies required for Beast Core/UI itself.

Adding here has the highest bar.

### 2. Beast-owned Python runtime

Optional Python packages installed into the Beast-owned path rather than Pwnagotchi's environment.

Use for capability adapters that are safe to import in-process.

Install/remove must be explicit, version-pinned/provenanced and reversible.

### 3. Debian / OS packages

Prefer Debian packages when the capability is fundamentally a Linux/system service or mature native library.

Examples:
- Cairo / librsvg
- psutil
- pyudev
- evdev
- libgpiod
- SMBus/I2C
- Bleak/BlueZ
- gpsd
- FFmpeg
- ZBar
- bubblewrap

These should be detected through the existing Dependency & Capability Resolver.

### 4. External services/processes

Some software is better treated as a provider process than linked into Beast.

Examples:
- gpsd
- FFmpeg jobs
- future Kismet/SDR/radio services
- map/tile servers
- local AI services
- optional brokers

Beast communicates through a narrow adapter and supervises health/cost.

### 5. Browser-vendored assets

Studio/companion functionality may use mature JavaScript libraries without requiring a Node runtime on the Pi.

Build/vendor pinned static assets during release.

Good candidates include:
- uPlot for time-series charts;
- interact.js for drag/resize/direct manipulation;
- MapLibre/Leaflet-style mapping where appropriate;
- CodeMirror-class editors for advanced text/config work.

### 6. Sandboxed code-bearing Packs/Apps

Third-party executable content should not be imported directly into Beast Core merely because it is convenient.

Preferred future execution boundary:
- dedicated unprivileged user;
- systemd unit/transient unit;
- filesystem restrictions;
- resource limits;
- restricted address families/network access;
- optional bubblewrap namespace isolation;
- explicit Signal/Action/API contract.

This gives users an open platform without making the trusted Core a plugin soup.

### 7. Development-only tooling

Profilers, test generators, image/media compilers, lint tools and asset build pipelines may be much heavier than production.

They do not need to run on the field device.

## Current first catalog

`beastcore/integration_catalog.py` is a read-only catalog of optional outside backends.

It reuses the existing DependencyCapabilityResolver.

Current candidates include:
- Cairo + librsvg;
- psutil;
- pyudev;
- evdev;
- libgpiod;
- SMBus/I2C;
- Bleak + BlueZ;
- Zeroconf;
- aiohttp;
- watchdog;
- FFmpeg;
- ZBar;
- bubblewrap;
- Paho MQTT;
- gpsd.

The catalog:
- reports capabilities;
- reports requirements;
- reports current readiness;
- identifies dependency lane/isolation intention;
- never installs anything;
- never auto-enables anything;
- never makes an optional integration a base dependency.

Core exposes this through `/integrations` for future Studio/Doctor use.

## High-value opportunity areas

### Visual Runtime

Use external libraries selectively for what they are good at:
- Pillow/Numpy: existing raster compositor + RGB565 path;
- Cairo: vector geometry, scalable masks/art;
- librsvg: SVG ingestion/pre-render;
- FFmpeg: authored media preparation/decode;
- browser Canvas/SVG: rich Studio preview/editing.

Do not replace the known-good framebuffer writer merely to adopt a larger graphics stack.

### Hardware Studio

Use Linux's existing hardware abstractions:
- udev for hotplug;
- evdev for input;
- libgpiod for GPIO;
- SMBus/I2C for sensors/power;
- BlueZ/Bleak for BLE;
- gpsd for GPS.

This turns hardware support into adapters and capabilities rather than bespoke loops.

### Studio / companions

A future controller split may use aiohttp/WebSockets on Beast-owned infrastructure.

Do not hold long-running connections through Pwnagotchi's own web server.

Vendor lightweight client libraries instead of shipping a full frontend build toolchain on the Pi.

### Local discovery

Zeroconf/mDNS can make Beast Studio/companion discovery feel appliance-like:
- `beastagotchi.local`;
- discoverable local Studio service;
- future local Beast services.

No cloud account required.

### Capsules

Keep qrcode for generation.

Use ZBar or another mature decoder for receive instead of implementing QR decoding.

Camera support remains optional.

### Audio / cinematics

Use FFmpeg as a bounded backend for:
- converting Pack media at install/stage time;
- extracting frame/audio assets;
- validating codecs/dimensions/duration;
- rare-event media.

Prefer preprocessed lightweight runtime assets on the 3.5-inch target where that is cheaper than live video decode.

### Beast Bus / satellites

MQTT is a strong optional transport for:
- Home Assistant;
- local automations;
- ESP32/Pi Zero satellites;
- dock services;
- lab integrations.

MQTT is an adapter transport, not the canonical internal state model.

### Sandboxed extension execution

Code-bearing Apps/Packs should graduate toward process isolation.

systemd already provides strong service sandbox/resource controls; bubblewrap is an additional namespace tool.

The future App Runtime can expose a small local protocol:
- subscribe to approved Signals;
- emit declared signals/events;
- request approved Actions;
- write only its managed data area;
- consume declared capabilities.

## Installation philosophy

Beast should eventually support:

**DISCOVER → EXPLAIN → PLAN → ACQUIRE → VERIFY → ENABLE → PROBATION → KEEP/ROLL BACK**

Never:
- silently apt install because a screen was opened;
- pip-install into Pwnagotchi's environment;
- enable a service merely because it is present;
- execute downloaded Pack code inside Core;
- assume Internet access;
- treat catalog presence as trust.

Expert Mode may allow unsupported paths, but technical truth, provenance, blast radius and rollback remain visible.

## Catalog growth rule

The integration catalog is intentionally expandable.

A candidate earns a place when it can plausibly:
- replace bespoke code with proven software;
- unlock a meaningful capability;
- improve reliability/performance;
- improve interoperability;
- reduce maintenance;
- enable a Pack/App/hardware family;
- or provide unusually good UX.

Being available is not enough. Beast should not collect dependencies as trophies.

## Immediate implications

1. Continue the Scene/Visual Runtime work with Pillow as the proven framebuffer backend, while allowing Cairo/SVG and media helpers as optional asset/runtime providers.
2. Use the Integration Catalog in the future Plugin & Capability Center.
3. Make the future Experience Compiler resolve external capabilities through the same dependency graph.
4. Build Hardware Studio around event-driven Linux providers where possible.
5. Design code-bearing Pack execution around systemd/bubblewrap-style isolation before enabling arbitrary third-party code.
6. Prefer vendored lightweight browser libraries for Studio power rather than hand-building charting/drag/map systems.
7. Keep expanding the catalog as new useful projects are discovered.
