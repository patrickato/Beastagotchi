# Beastagotchi Lightbulb Review — Capability-Oriented Platform Expansion
## 2026-09-24

Status: protected design exploration promoted from discussion into project scope.

This review follows the maturity architecture review and the External Software /
Integration Strategy. It asks what becomes possible if Beastagotchi treats the
Linux/Raspberry Pi/open-source ecosystem as a large toolbox while preserving
canonical Beast contracts, resource discipline, local-first behavior and rollback.

The ideas below are not all immediate implementation tasks. Each is assigned a
role so it is not silently forgotten.

---

# 1. Aha: Beastagotchi should orchestrate capabilities, not packages

The user should think in terms of:

- camera;
- audio;
- maps;
- GPS;
- BLE;
- vector graphics;
- offline knowledge;
- local discovery;
- sandboxed apps;
- remote/satellite sensors;

not:

- which Debian package happens to provide that feature.

External packages/services are providers.

The stable Beast vocabulary remains:
- Signal;
- Event;
- Action;
- Capability;
- Scene;
- Experience.

This means a future Experience can require `audio.output` without depending on
PipeWire specifically, or `camera.capture` without caring whether a Pi camera,
USB camera or another provider supplies it.

**Decision:** extend the existing Dependency/Capability Resolver and Integration
Catalog rather than build another package manager abstraction.

---

# 2. Aha: Capability Recipes

A missing capability should eventually be able to produce an exact acquisition
plan.

Example:

`camera.capture`

Possible provider:
- Picamera2 / libcamera

Recipe:
1. detect supported camera hardware;
2. show exact packages to install;
3. show disk/resource impact;
4. snapshot relevant config;
5. acquire packages transactionally;
6. verify import/executable/device;
7. enable adapter;
8. probation-test capture;
9. keep or roll back.

A recipe is not an automatic installer. It is a declarative plan consumed by the
future Transaction Engine.

Potential recipe actions:
- apt package;
- Beast-owned Python wheel;
- service enable/start;
- file/config mutation;
- group/device permission;
- udev rule;
- Pack install;
- verification probe;
- rollback step.

**Status:** planned platform primitive.

---

# 3. Aha: Ghost Beast / Digital Twin / Replay Lab

Current real-state gallery tooling already proves that Beast UI can render from
captured canonical state.

Turn that into a first-class development and diagnostic system.

A Replay Bundle can contain sanitized:
- canonical Signal snapshots over time;
- durable Events;
- selected histories;
- Expedition route;
- capability inventory;
- display target;
- resource/governor state.

Uses:
- reproduce a field bug without the Pi present;
- replay an Expedition visually;
- compare old/new renderers against the same reality;
- build screenshots/video from real data;
- test Rare reactions deterministically;
- regression-test unavailable/stale/fault states;
- demonstrate Beast safely without fake production telemetry;
- develop a hardware feature from a contributor-provided sanitized recording.

Modes:
- REPLAY — clearly historical;
- SIMULATION — synthetic/dev-only and unmistakably labeled;
- LIVE — actual device.

Production UI must never blur those modes.

**Status:** high-value planned engineering block. Existing gallery/captured-state
infrastructure is the seed, so this is an evolution rather than a new system.

---

# 4. Aha: Choreography Engine

Several planned systems want to react to the same semantic events:
- Scene animation;
- Beast expression;
- notification;
- sound;
- haptic;
- LED;
- display lighting;
- Rare Moment;
- companion notification.

Do not let each subsystem independently react to an event.

Create a **Choreography Engine**.

Input:
- semantic Event;
- severity/rarity;
- current context;
- active Experience;
- hardware capabilities;
- quiet/reduced-motion/accessibility policy;
- Resource Governor state.

Output:
- coordinated timeline of presentation cues.

Example:

`progression.level_up`

0 ms:
- creature expression → excited

100 ms:
- aura bloom

250 ms:
- optional haptic pattern

300 ms:
- short audio cue

600 ms:
- level badge appears

2.5 s:
- return to normal scene

The same event on a Minimal Experience may only pulse the edge and update text.
On WOPR it may produce a terminal alert. On LCARS it may generate an LCARS
panel. The semantic event is shared; the Experience chooses choreography.

This also solves priority/preemption:
critical thermal warning > Rare cinematic > level-up > ambient motion.

**Status:** promote to Visual Runtime / Experience architecture.

---

# 5. Aha: Beast Senses

Optional hardware can become a coherent conceptual layer:

- eyes → camera;
- ears → microphone/audio input;
- location sense → GPS;
- proximity → BLE;
- motion/orientation → IMU;
- environment → temperature/humidity/pressure/light;
- RF senses → Wi-Fi/SDR/rtl_433/ADS-B;
- touch → touchscreen/buttons;
- voice → optional speech stack.

These are capabilities, not required peripherals.

This gives Hardware Studio a human-readable model:
**BEAST SENSES**

Each sense can show:
- provider;
- health;
- permissions;
- current usage;
- Signals produced;
- Apps/Scenes using it.

This is more cohesive than a generic USB-device inventory while remaining
technically truthful.

**Status:** product/UX concept for Hardware Studio.

---

# 6. Aha: Hotplug Role Wizard

Use udev/hardware discovery to react when new equipment appears.

Example:

NEW DEVICE
- USB serial adapter
- VID/PID known
- candidate roles:
  - GPS receiver
  - environmental sensor
  - Meshtastic
  - generic serial source

User chooses a role.

Beast then explains:
- provider;
- dependencies;
- Signals it would produce;
- conflicts;
- permission changes;
- power/resource expectations.

Never guess and mutate merely because a USB device was inserted.

**Status:** planned Hardware Studio workflow.

---

# 7. Aha: Linux D-Bus becomes a provider highway

Many mature Linux services already expose event-driven APIs.

Use D-Bus where appropriate rather than continually parsing CLI output.

Potential adapters:
- NetworkManager;
- BlueZ;
- systemd;
- UPower if present;
- desktop/notification services on larger-display builds;
- future modem services.

`python3-dbus-next` is now represented in the Integration Catalog as an optional
system provider layer.

Important:
- do not require NetworkManager on a Jayofelony image that does not use it;
- treat it as one provider;
- preserve existing native collectors/fallbacks.

**Status:** cataloged candidate.

---

# 8. Aha: Systemd is an App Runtime primitive, not only a service launcher

For code-bearing third-party Beast Apps, systemd can provide:
- dedicated UID;
- restart policy;
- watchdog;
- CPU accounting/quota;
- memory limits;
- process limits;
- filesystem restrictions;
- environment;
- capability bounding;
- private temp;
- logging;
- lifecycle supervision.

Bubblewrap can add optional namespace isolation.

Future App permission model can map declarations into runtime policy.

Example App manifest:

permissions:
- signals.read: [gps.*, expedition.*]
- events.read: [expedition.*]
- actions.request: []
- network: none
- filesystem: private
- camera: false

resources:
- memory_max_mb: 96
- cpu_quota_pct: 15

Beast Core remains outside the App process.

**Status:** high-priority prerequisite before broad code-bearing Pack execution.

---

# 9. Aha: Systemd watchdog should protect Beast itself

Core has internal health checks, but a process can hang badly enough that its own
health loop cannot report failure.

Use a future systemd watchdog handshake:
- Beast Core emits readiness;
- periodically pets watchdog only while its event loop remains responsive;
- systemd restarts Core on a true hang;
- Black Box/incident logic records the restart after recovery.

This is complementary to Beast Doctor, not a replacement.

**Status:** small future reliability block.

---

# 10. Aha: Last-Known-Good Experience / visual safe mode

Because Experiences will become more powerful, presentation needs its own rescue
path.

Before applying a new Experience:
- compile;
- snapshot active presentation;
- start timed preview;
- monitor UI heartbeat;
- require KEEP;
- otherwise revert.

At boot:
- if UI crashes repeatedly after a presentation change, load last-known-good;
- if that fails, load a minimal built-in Safe Experience;
- never lose Core/Pwnagotchi merely because a theme/Scene is broken.

This generalizes the existing timed preview/revert idea.

**Status:** promote to Experience Compiler + Transaction Engine requirements.

---

# 11. Aha: Asset Compiler

Do expensive media/asset preparation at Pack stage/install time, not every frame.

Possible inputs:
- SVG;
- PNG/JPEG;
- GIF/video;
- audio;
- fonts;
- large maps;
- creature sprites.

Compile/cache target-ready forms:
- fitted 480x320/800x480 images;
- prebuilt masks;
- RGB565-friendly assets where useful;
- animation frame strips;
- audio normalized to target format;
- thumbnails;
- metadata;
- checksums.

Tools can include:
- Cairo/librsvg;
- Pillow;
- FFmpeg.

The runtime then performs cheap composition.

**Status:** promote to Pack/Visual Runtime design.

---

# 12. Aha: Multi-backend presentation without multi-backend semantics

The 3.5-inch SPI TFT and a future HDMI/DSI display have radically different
constraints.

Do not force one renderer backend onto both.

Possible providers:
- Pillow/RGB565 → reference SPI TFT;
- web Canvas/SVG → Studio/phone;
- experimental LVGL/SDL/OpenGL → richer Linux displays;
- future specialized GPU/DRM path.

They consume the same Scene semantics where practical.

LVGL is interesting because current LVGL supports Linux/SDL and OpenGL-class
backends, animations, widgets and multi-display behavior. However, Beast should
**not** base its public Studio/schema on LVGL's XML/UI-editor format: the current
LVGL XML specification places restrictions on third-party public editors/tools.
Use the MIT-licensed runtime only if it earns a role.

**Status:** LVGL cataloged as experimental large-display backend research.

---

# 13. Aha: Exact Remote Mirror

Studio should eventually be able to show the exact framebuffer output the TFT is
receiving, not merely a browser approximation.

Possible modes:
- periodic PNG;
- efficient changed-region stream;
- low-rate MJPEG/WebSocket frames when appropriate.

Overlay optional semantic information in Studio:
- touch boxes;
- layer IDs;
- dirty regions;
- render cost;
- Signal quality.

This gives us:
- remote visual diagnosis;
- direct comparison between concept and actual renderer;
- touch troubleshooting;
- easier physical validation;
- creator preview.

Remote input must require explicit local/authorized control and should be
visibly indicated on the device.

**Status:** planned Studio/Visual Runtime tool.

---

# 14. Aha: Design-Time Performance Compiler

Experience compilation can estimate cost before activation.

Each layer/provider declares a cost class and benchmark hints.

The compiler can predict:
- static cache size;
- animated layer count;
- update cadence;
- likely dirty area;
- required libraries/services;
- memory class;
- target-specific concerns.

After running, Beast replaces estimates with measured data.

Studio can show:
**Estimated: Medium**
**Measured on this Pi: 3.8 ms p95 compose, 14% dirty rows, 6.2% UI CPU**

This closes the loop between customization and performance.

**Status:** planned Experience Compiler / Performance Lens integration.

---

# 15. Aha: Offline Knowledge should be a real platform capability

Kiwix/ZIM is mature and available on arm64.

Field Library can eventually index/launch:
- Beast/Pwnagotchi docs;
- Linux manuals;
- hardware manuals;
- Raspberry Pi docs;
- user-chosen offline reference collections.

`kiwix-serve` can be on-demand rather than always running.

A Pack could declare a curated ZIM source/reference without bundling it into
every Beast install.

**Status:** Integration Catalog candidate + existing Gate 9/Kiwix scope upgraded
from "reader idea" to provider architecture.

---

# 16. Aha: Offline Map Packs

The existing Map/Expedition system should not require Internet map tiles.

Use Map Pack providers:
- compact raster tiles;
- MBTiles;
- PMTiles/vector tile sources;
- optional browser MapLibre-style renderer for Studio/phone.

TFT still uses deliberately simplified route/field visualization.

Studio/phone can provide rich mapping from the same Expedition data.

Map Packs can be region-scoped and removable.

**Status:** promote within existing Map Pack / Expedition scope.

---

# 17. Aha: Memory Films

Beast already has:
- Expedition history;
- events;
- route;
- creature participation;
- captures metadata;
- Rare Moments;
- achievements;
- optional future user-approved camera images;
- presentation assets.

A future Memory Film generator could turn an Expedition into a short local
recap:
- route animation;
- distance/stat highlights;
- Beast reactions;
- discoveries;
- achievements;
- optional photos;
- ending summary.

FFmpeg can assemble/export media; Beast supplies the semantics/story.

This is not fake telemetry. It is visualization of persisted history.

**Status:** future delight/Memory Vault feature.

---

# 18. Aha: Experience Capsules / Hardware Capsules / Support Capsules

The transport-neutral Capsule model can eventually carry more than lineage.

Potential privacy-bounded types:
- Experience Capsule — share a composition/Pack references;
- Challenge Capsule — offline mission/challenge;
- Hardware Profile Capsule — share role configuration without credentials or
  machine-specific secrets;
- Support Capsule — sanitized diagnostic manifest / dependency fingerprint;
- Beast Card — public creature/profile;
- Trophy Proof — integrity/authenticity-backed achievement evidence.

QR is only one transport.

**Status:** consistent with existing Capsule roadmap; preserve as named types.

---

# 19. Aha: Capability Fingerprint

Every running Beast can calculate a non-secret fingerprint of its supported
environment:
- OS/version;
- Beast version;
- Pwnagotchi version;
- installed/active providers;
- hardware capabilities;
- selected dependency versions;
- display class;
- Pack versions;
- customized/managed state.

Uses:
- "what changed?" diagnostics;
- known-good comparisons;
- issue reports;
- Experience compatibility;
- update planning;
- regression reproduction.

Do not include:
- credentials;
- captures;
- private RF identities;
- precise location.

**Status:** strengthen existing known-good build fingerprint roadmap item.

---

# 20. Aha: Distributed Beast / satellites

Beast Bus can use multiple transports:
- MQTT;
- serial;
- BLE;
- local HTTP/WebSocket;
- future dedicated peer transport.

ESP32/Pi Zero nodes can become optional remote senses:
- environmental probe;
- remote display;
- button/indicator pod;
- GPS/IMU node;
- dock sensor;
- low-power BLE observer;
- battery/power monitor.

The main Beast consumes normalized Signals.

Satellites should not become trusted Core peers by default.

**Status:** retained and strengthened Beast Bus / hardware expansion scope.

---

# 21. Aha: Context Orchestrator

Beast already models context and dock state.

As capabilities grow, context can become a policy input:

- FIELD;
- DOCKED;
- HOME;
- VEHICLE;
- NIGHT;
- LOW POWER;
- LAB;
- PRESENTATION/DEMO.

Context may influence:
- Experience variant;
- brightness/audio;
- which optional services are awake;
- sync/update policy;
- logging resolution;
- companion behavior;
- map availability;
- hardware polling.

Important: context does not falsify telemetry or silently perform risky actions.

**Status:** evolve existing Context Engine, not a new subsystem.

---

# 22. Aha: The reference Pi becomes a capability laboratory

Maintain two explicit targets.

## Beast Baseline
Small, supported, ordinary installation.

## Monster/Superset Reference Build
Reference Pi with the broad validated provider universe installed.

The build fingerprint/BOM records:
- installed;
- active;
- dormant;
- selected providers;
- measured cost.

This lets Beast test integrations at scale without forcing them onto every user.

**Status:** promote existing superset BOM idea into named reference-build policy.

---

# 23. Immediate promoted work

Near-term architecture sequence is now:

1. keep active branch green;
2. continue Scene/Visual Runtime proof;
3. introduce Signal v1 over StateRegistry/Telemetry rather than replacing them;
4. keep expanding read-only Integration Catalog;
5. define Scene/Layer schema and semantic layer registry;
6. formalize captured-state Replay Bundle / Ghost Beast;
7. define Experience Compiler v1;
8. refactor Beast UI shell behind registries;
9. add timed preview + last-known-good presentation;
10. prototype the Transaction Engine / Capability Recipe boundary;
11. later add D-Bus/hotplug/systemd sandbox adapters as bounded providers.

The intent is not to pause visual work for months of backend work. These
contracts are introduced in small bounded slices while Home/major Scenes become
the visible proof.

---

# Final product principle

The project should exploit the ecosystem broadly while remaining conceptually
small.

A user may have hundreds of capabilities, Packs and integrations installed.

But Beast's mental model should remain:

**What do I know?** → Signals  
**What happened?** → Events  
**What can I do?** → Actions  
**What can this device provide?** → Capabilities  
**How should it look/behave?** → Scenes + Experience  
**Can I change it safely?** → Transaction + Recovery

That is the connective tissue that allows abundance without chaos.
