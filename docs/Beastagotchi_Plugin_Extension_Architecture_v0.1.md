# Beastagotchi Plugin & Extension Architecture v0.1

**Status:** active architecture / Companion Expansion + Beast Capsule direction approved  
**Updated:** 2026-09-24

## Core rule

Not every Beastagotchi extension should become a Pwnagotchi plugin.

Use the narrowest extension layer that actually needs the capability.

The platform distinguishes four user-facing extension classes:

1. **Pwnagotchi Plugin**
2. **Beast Pack**
3. **Beast App**
4. **Companion Expansion**

Adapters remain an implementation pattern used to bridge existing plugins,
hardware and services into canonical Beast state/events.

## 1. Pwnagotchi Plugin

A custom component belongs in the underlying Pwnagotchi plugin system when it
genuinely needs Pwnagotchi's own lifecycle or callback surface.

Examples:
- peer detected/lost callbacks;
- handshake/session/epoch callbacks;
- Bettercap/Pwnagotchi integration;
- native Pwnagotchi plugin hooks;
- an upstream-compatible feature that should remain useful when Beast UI/Core is
  disabled.

Normal install target remains:

`/etc/pwnagotchi/custom-plugins/`

Beast-managed config should prefer isolated TOML drop-ins under
`/etc/pwnagotchi/conf.d/` where compatible.

### Design rule

A Pwnagotchi plugin should normally be a **sensor or actuator**, not a duplicate
Beast application.

It may tell Beast:

- a peer appeared;
- a capture/session event happened;
- a hardware/service capability is present;
- new telemetry exists;
- a bounded action is available.

It should generally not own:
- Beast progression;
- the trophy cabinet;
- lineage state;
- Beast UI page layout;
- the full dependency graph;
- global Beast configuration.

Those remain canonical Beast concerns.

## 2. Beast Pack

A Beast Pack carries modular Beast-side content or bounded capability metadata.

Examples:
- Theme/Face/Animation/Audio Packs;
- Board/Layout/Context Deck Packs;
- Mission/data/map Packs;
- achievement/trophy catalogs;
- widget bundles;
- capsule schemas/templates;
- challenge definitions;
- hardware adapter metadata;
- visualizers/renderers;
- offline libraries/data.

Rather than creating a new technical `pack_type` for every idea, manifests may
now carry **content roles**.

Examples:

`achievement_catalog`  
`trophy_art`  
`widget_bundle`  
`challenge_catalog`  
`capsule_schema`  
`beastdex_cards`

This keeps Depot taxonomy broad and stable while allowing highly specific
content.

## 3. Beast App

A Beast App is a deeper interactive Beast-side function/tool.

Examples:
- Cipher Console;
- Spectrum Analyzer;
- advanced Map/Expedition viewer;
- Beast Doctor graph viewer;
- Capsule Workshop;
- Hardware Studio;
- future Container Center.

Apps may consume canonical Beast state/events and Action Broker operations.
They should not create a second hidden truth source.

## 4. Companion Expansion

A Companion Expansion is the user-facing bundle for features that legitimately
span more than one extension class.

Example:

**GPS Expedition Expansion**

may contain:
- a thin Pwnagotchi callback plugin;
- a Beast integration adapter;
- a map/Board Pack;
- an achievement catalog;
- Mission definitions;
- Studio UI;
- Doctor rules;
- dependency declarations.

To the user it is one coherent install. Internally each component lives in the
correct subsystem.

Pack manifests now support:

- `extension_class = "pack" | "companion"`;
- `content_roles`;
- `signals_provides`;
- `signals_consumes`;
- `offline_transports`;
- `capsule_types`;
- `companion.pwnagotchi_plugins`;
- `companion.beast_apps`;
- `companion.beast_packs`.

This metadata is descriptive. It does not silently install/execute the component
parts.

## Adapter pattern

An adapter translates an existing Pwnagotchi plugin/service/hardware source into
canonical Beast capabilities/events.

Example:

`gps plugin -> location.position -> Beast Core -> Map/Expedition/Achievements`

The adapter approach is preferred to forking/reimplementing a mature upstream
plugin merely to make Beast understand it.

## Signals and achievements

Plugins/extensions should emit truthful normalized **signals/events**.

Examples:

- `gps.fix.changed`
- `peer.encountered`
- `expedition.completed`
- `power.low_battery`
- `hardware.connected`

The canonical Achievement/Trophy Engine decides whether those facts satisfy an
achievement.

A plugin should not normally issue:

> grant achievement X

This prevents third-party plugins from bypassing progression rules and lets one
signal feed many independent Achievement Packs.

Conversely, an Achievement Pack should be able to define new rules/rewards
without needing to modify the plugin that supplies the underlying fact.

## Generic plugin UI

A plugin should not need custom Beast rendering just to become useful.

Future Plugin & Capability Center behavior should be able to generate a generic
native Beast card from declarations such as:

- provided capabilities;
- canonical values;
- health;
- dependencies;
- actions;
- data-egress class;
- config schema;
- `USED BY` graph.

A purpose-built Beast Pack/App may later provide a richer view.

## Plugin profiler direction

Because Beast may host many installed plugins, optimization should be
evidence-driven.

A future Plugin Profiler should track where practical:

- callback duration;
- exceptions/failures;
- last successful callback;
- stale output;
- approximate CPU/time contribution;
- repeated restart/failure patterns.

Doctor could then identify a misbehaving plugin rather than imposing arbitrary
plugin-count limits.

## Pwnagotchi plugin lifecycle

Managed Beast states remain:

`AVAILABLE -> STAGED -> INSTALLED -> ENABLED`

Known/trusted plugins may remain installed but disabled for fast activation.
Unreviewed code remains staged until compatibility/dependencies are understood.

The Plugin & Capability Center / Dependency Resolver additionally distinguishes:

- installed;
- configured;
- selected;
- ready;
- active provider;
- alternate provider;
- blocked;
- unsupported/customized.

## Managed writes

Before Beast performs managed plugin installation/configuration it should provide:

- configuration snapshot;
- TOML/config validation;
- dependency check;
- compatibility fingerprint;
- explicit restart requirements;
- data-egress/credential warning;
- post-change health observation;
- automatic rollback where technically possible;
- action history;
- Owner Override path for policy-only blockers.

Owner Sovereignty remains authoritative. Unsupported/manual installation remains
possible; Beast should explain consequences instead of pretending ownership of
the user's Pi.

## Presentation ownership

Legacy display-drawing plugins must not race Beast UI for the framebuffer.

Useful plugin data should normally flow:

`plugin -> adapter -> canonical Beast state/event -> active renderer`

Plugins that truly own presentation are handled through Presentation Broker
rather than by allowing multiple framebuffer owners to draw simultaneously.

## Beast Capsules and offline extension transport

Extensions may advertise Capsule types and offline transports.

The Beast Capsule contract is transport-neutral. A Lineage Capsule, Challenge
Capsule or future BeastDex card should be the same logical payload whether moved
by:

- QR;
- animated/multi-frame QR;
- local file;
- USB/SD;
- NFC;
- Bluetooth/local direct transfer;
- Beast-to-Beast transport;
- local WebUI/phone.

This creates an **offline ecosystem**, not merely an offline-capable application.

See:
- `Beastagotchi_Beast_Capsules_Offline_Ecosystem_v0.1.md`

## Decision guide

Choose **Pwnagotchi Plugin** when the feature fundamentally needs Pwnagotchi
callbacks/lifecycle.

Choose **Beast Pack** when it is content/data/presentation/rules/assets.

Choose **Beast App** when it needs a deeper interactive Beast-native experience.

Choose **Companion Expansion** when one user-facing feature spans several of
those layers.

Use an **Adapter** when useful functionality already exists elsewhere and only
needs normalization into Beast.

This is intentionally designed to keep Pwnagotchi authentic, Beast Core coherent,
and the long-term extension ecosystem large without becoming monolithic.
