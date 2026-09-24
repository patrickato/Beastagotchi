# Beastagotchi Capability Provider Arbitration — v0.1

**Status:** read-only policy engine implemented  
**Date:** 2026-09-24

## Purpose

The Dependency & Capability Resolver answers **what can provide a capability**.

Provider Arbitration answers the next question:

> If several things can provide the same capability, which one should Beast treat
> as canonical right now, which are alternates, and when should the owner be asked
> to choose?

Examples:
- USB/gpsd versus PwnDroid for `location.position`;
- Beast native UPS telemetry versus PiSugar/UPS-Lite/WittyPi for
  `power.battery.telemetry`;
- Ethernet, Bluetooth tether or another future transport for Internet;
- Native / Theme Manager / Beast for presentation ownership;
- multiple future sensors or radio adapters providing the same logical service.

## Current policy

The current engine is deliberately **read-only**.

For each capability:

1. If a future explicit owner preference exists and that provider is ready,
   prefer it.
2. Otherwise prefer a live native/canonical Beast provider. This keeps one
   canonical truth source and avoids replacing good native telemetry merely
   because a compatibility plugin is installed.
3. Otherwise, if exactly one selected+ready component provides the capability,
   that provider is unambiguous.
4. If several selected+ready non-native providers remain, report
   `choice_required`. Do not silently pick one.
5. If ready providers exist but none is selected, report
   `available_unselected`.
6. If nothing ready can provide the capability, report `unavailable`.

A deterministic recommendation and fallback chain are produced for explanation
and future UI, but the engine does not mutate selection.

## Decision states

- `active_preference` — explicit owner preference is ready;
- `active_native` — native/canonical provider is live;
- `active_selected` — one selected ready non-native provider exists;
- `active_fallback` — preferred provider is unavailable and an unambiguous live
  fallback exists;
- `choice_required` — several selected providers are viable;
- `available_unselected` — provider(s) exist but none is active;
- `unavailable` — no ready provider exists.

Every decision includes:
- active provider;
- recommendation;
- owner preference if any;
- reason;
- alternates;
- ordered fallback chain;
- candidate readiness/selection metadata;
- policy/technical blockers for component candidates.

## Native-first does not mean owner-locked

Native-first is the default automatic policy because Beast's canonical collectors
already feed normalized state and avoid duplicate polling.

It is **not** an ownership restriction.

The architecture explicitly reserves owner preference/override. A later
transactional preference action can let an owner pin PwnDroid over USB GPS,
PiSugar over a native UPS adapter, or another valid provider.

Owner Sovereignty remains authoritative: automatic policy is convenience, not a
permanent prohibition.

## Current implementation

- `beastcore/provider_arbitration.py`
- `CapabilityProviderArbitrator`
- attached to every `DependencyCapabilityResolver.resolve_components()` graph;
- PluginIntegrationEngine exposes provider decisions and summary;
- dependency Local API/platform bundle expose the decisions;
- configured-but-disabled plugins may remain **available alternates** rather than
  disappearing from the graph;
- provider mutation is disabled;
- automatic failover is disabled.

## Why failover is not enabled yet

Automatic failover sounds simple but can create bad behavior without hysteresis
and ownership rules:

- GPS briefly loses fix and Beast flaps to a phone and back;
- Bluetooth tether reconnects repeatedly and changes the network route;
- two battery drivers fight over the same I2C device;
- presentation owners race for the framebuffer;
- a degraded provider causes repeated service restarts.

Before auto-failover becomes executable, Beast should have:
- per-capability failover policy;
- provider health confidence;
- minimum dwell/cooldown time;
- explicit resource ownership;
- rollback;
- audit events;
- owner pin/Auto modes;
- privacy/egress consideration;
- context awareness (Field versus Dock/Home).

## UX direction

A future Capability Center should show something like:

**LOCATION**
- Active: Native GPS / gpsd
- Health: Ready
- Alternates: PwnDroid
- Policy: Auto
- Used by: Map, Expeditions, capture context, Memories
- Failover: Off / available
- Why this provider?: Native canonical source is live

Owner actions:
- **AUTO**
- **PIN THIS PROVIDER**
- **TRY ALTERNATE**
- **PROVIDER DETAILS**

For ambiguous states:

**POWER TELEMETRY**
- PiSugarX: selected / ready
- UPS-Lite: selected / ready
- Active: none
- Status: CHOICE REQUIRED

Beast should explain the conflict instead of pretending two sources are one truth.

## Design ideas unlocked by arbitration

### Context-aware provider profiles

Provider preference can eventually vary by context.

Example:
- Field: PwnDroid Internet + USB GPS;
- Dock: Ethernet + fixed GPS antenna;
- Home: Ethernet + Home Base services;
- Battery-critical: disable expensive alternates and prefer lowest-cost provider.

This should be policy-driven and transparent, not hidden magic.

### Graceful degradation

Capabilities should know whether losing them is:
- fatal;
- degraded-but-usable;
- cosmetic.

If GPS vanishes during an Expedition, the Expedition should continue while route
recording becomes degraded, rather than the entire mission failing.

### Hot-plug arrival

When a new device appears, Beast can say:

> u-blox GNSS detected. It can provide Location. Current provider is PwnDroid.
> Keep current / switch / use as fallback?

No reboot or manual dependency hunt should be required when the adapter is already
supported.

### Failover rehearsal

Before trusting automatic failover in the field, Beast could provide a
**TEST FAILOVER** operation:
- snapshot current provider;
- temporarily hand over;
- verify canonical telemetry;
- restore;
- report success/failure.

This fits Beast's existing probation/rollback philosophy.

### Provider confidence

Future provider health can carry confidence:
- high: live direct hardware telemetry;
- medium: provider alive but stale/partial;
- low: inferred/fallback source.

Consumers could request:
- any location;
- high-confidence location;
- low-power location;
- privacy-local-only location.

That turns capabilities from a Boolean into a richer contract without forcing
every app to understand every device.

### Capability leasing

For scarce resources such as framebuffer, SDR, camera, microphone or exclusive
radio modes, a future provider may require a **lease**.

Beast can then answer:
- who owns this resource;
- who is waiting;
- whether sharing is safe;
- what must stop before another app starts.

Presentation Broker is effectively the first example of this concept.

### Dependency/update impact simulation

Because USED BY already exists, Update Center can eventually perform:

> If I update/remove this provider, what capabilities and apps become degraded?

This can become a preflight simulation before updates or removals.

### Known-good build fingerprint

The resolver + BOM + arbitration graph can produce a compact reference-build
fingerprint:
- active capabilities;
- active providers;
- alternates;
- dependency versions;
- customization state.

That gives Beast Doctor a powerful "what changed since known-good?" comparison.

## Next implementation steps

1. Add a persistent owner provider-preference store and transactional set/clear
   action. Do not silently create preferences.
2. Surface provider decisions/reasons in Beast Studio/Capability Center.
3. Add provider-health freshness/confidence metadata.
4. Add context-aware policy inputs without enabling automatic switching yet.
5. Add explain/Doctor queries:
   - Why is this provider active?
   - What happens if I disable it?
   - What alternate can replace it?
6. Add failover simulation.
7. Only then enable per-capability automatic failover where the provider handoff
   is proven safe.
