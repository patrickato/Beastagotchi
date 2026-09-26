# Beastagotchi Fresh-Eyes / Epiphany Review

**Date:** 2026-09-26  
**Status:** discussion findings / candidate directions; **not owner-approved canon**  
**Purpose:** zoom out from the existing roadmap and ask what Beastagotchi becomes when already-built or already-planned systems are connected more deliberately. This is not a rewrite proposal.

---

# Executive verdict

The review found no reason to restart Beastagotchi or replace the current architecture. The strongest opportunities are mostly **connections between things Beast already has**, plus a handful of foundation corrections that are much cheaper to fix now than later.

The broad conclusion is:

> **Beastagotchi is closer to a coherent local-first field companion/platform than the feature list makes obvious. The next leverage comes from correlation, provenance, rehearsal, context, identity, and presentation discipline—not from adding dozens of new standalone apps.**

The project should continue to favor:

- one Doctor with many specialties;
- one System Graph with many views;
- one mutation path through Actions / Transactions / Procedures;
- one canonical truth model;
- large capability universe, small active working set;
- context-driven surfacing instead of giant navigation piles;
- real technical/environmental truth becoming creature experience without invented telemetry;
- owner sovereignty, with managed behavior remaining explainable and recoverable.

---

# A. Foundation findings that deserve promotion

## A1. Add causal/correlation context to important durable activity

Today Beast has Events, Incidents, Actions, Transactions, Procedures, Doctor findings, jobs and replay-worthy state, but there is no universal way to say:

> these facts are part of the same story.

Recommended future envelope fields where applicable:

- stable object/event id;
- wall-clock timestamp;
- monotonic timestamp where meaningful;
- boot id;
- runtime/instance id;
- correlation id;
- causation / parent id;
- source/provenance.

Do **not** import an observability framework wholesale. Steal the correlation pattern.

Benefits:

- Doctor can connect a power event -> USB reset -> radio loss -> incident;
- `What Changed?` can distinguish one managed Transaction from unrelated drift;
- replay can preserve causal grouping;
- Procedures can show which Actions/Transactions they caused;
- support evidence becomes substantially easier to interpret.

## A2. Fix time semantics before history becomes more authoritative

Current code often uses wall time (`time.time()`) for both human timestamps and age/freshness decisions. Wall time can jump after clock synchronization or manual correction.

Recommended rule:

> **monotonic time for age/order/timeout logic; wall time for human dates; boot identity links the two.**

Add explicit time quality / authority evidence rather than pretending every timestamp is equally trustworthy.

Candidate canonical facts:

- `time.quality` (unknown / approximate / synchronized / high-confidence);
- `time.source`;
- `time.last_sync_at`;
- `time.clock_jump_detected`;
- current boot id.

Consequences:

- State freshness must not depend solely on wall time;
- rare-event missed-window accounting should not trust a badly wrong clock;
- replay/Chronicle can preserve within-boot order even if wall time was uncertain;
- GPS time may contribute evidence but should have confidence requirements.

This is infrastructure, **not a Clock app**.

## A3. Explicit identity scopes

Keep distinct:

1. **physical device identity** — this board/hardware installation target;
2. **Beastagotchi installation / household identity** — the continuing logical installation that may survive an SD-card or Pi replacement;
3. **creature identity** — each Beast / Monster lineage member;
4. session/Expedition/Incident identity.

This prevents ambiguous restore/clone behavior.

Examples:

- restore after SD failure: preserve installation identity;
- migrate to a replacement Pi: preserve installation identity, update physical Device Passport;
- Clone My Setup to a second Pi: copy composition/preferences/content, normally generate a new installation identity;
- creature lineage remains its own identity domain.

Do not freeze a user-facing name for installation identity yet. (“Den” is one possible future metaphor, not an approved term.)

## A4. Persistent-state custody descriptors

A concrete recovery gap exposed the need for this: current backup scope does not automatically include every durable identity-critical file (for example the Rare Moment per-device secret seed).

Avoid fixing this with an ever-growing hand-coded path list. Instead let managed components/extensions declare their durable state using shared descriptors.

Useful independent axes:

### Durability / importance
- critical;
- owner-created / irreplaceable;
- rebuildable;
- cache / reacquirable.

### Sensitivity
- public;
- private;
- sensitive;
- secret-critical.

### Portability
- device-bound;
- installation-bound;
- cloneable;
- shareable/exportable only by policy.

### Lifecycle
- backup/restore handler;
- retention/purge policy;
- uninstall behavior;
- support-bundle behavior;
- migration semantics.

The same metadata can power Recovery Vault, rebuild/clone, privacy redaction, storage budgeting, uninstall and export rather than creating separate inventories.

## A5. Preserve the RF / sensor universe as capability families

Do not let recent Pwnagotchi/system work accidentally narrow the earlier Monstergotchi direction.

Future ADS-B, rtl_433, Meshtastic, BLE sensors, environmental sensors, camera/audio/external displays and similar additions should arrive as capability/provider families, not as a new permanent top-level mode for every technology.

Use:

- Providers -> canonical Signals/Events;
- Workspaces / Instruments for interaction;
- Expedition/session links for field context;
- System Graph for dependency/health;
- Doctor for diagnosis;
- progression/memory only from honest real observations.

---

# B. Strong X + Y = Z product connections

## B1. Incident -> Doctor -> Procedure -> Replay becomes a learning loop

Existing pieces:

- Incident Engine / Black Box;
- Doctor + Patient Chart recurrence memory;
- Procedures / Actions / Transactions;
- Sandbox record/replay;
- System Graph;
- Known-Good / What Changed?.

Combined result:

> **A failure can become reusable operational knowledge.**

Flow:

1. Incident opens with a bounded evidence snapshot.
2. Doctor explains the failing chain and likely blockers.
3. Owner or Procedure performs bounded recovery.
4. Verification determines whether the incident resolved.
5. Resolution records Procedure / Transaction references.
6. Real incident may be exported into the Sandbox replay corpus.
7. Future releases replay it as a regression scenario.
8. If the same incident recurs, Doctor can truthfully say what worked previously.

No separate “Doctor Case engine” is necessary. **Incident is the case envelope.** A future Casebook is a view.

## B2. Shadow Beast — rehearse against the logical twin before touching the Pi

Existing pieces:

- Device Passport / canonical inventory direction;
- Device BOM;
- Rebuild Manifest;
- Known-Good fingerprints;
- Beast Sandbox (WSL + Docker + virtual providers);
- SSH evidence from the physical Pi;
- Transactions / probation / verification.

Combined result:

> Build a logical **Shadow Beast** representing a particular physical installation closely enough to rehearse a planned change before applying it.

Potential uses:

- Pack/provider/config changes;
- upgrades/migrations;
- recovery plans;
- new Procedures;
- display/Experience changes;
- compatibility checks.

Safety rules:

- shadow uses a synthetic/shadow identity by default;
- real credentials omitted or replaced;
- external egress disabled/stubbed unless explicitly needed;
- Global Sync disabled;
- simulated/replayed state remains clearly labeled;
- passing Shadow validation does **not** replace physical validation.

This is an extension of existing “plan -> try -> probation -> verify -> rollback” philosophy, not a second architecture.

## B3. Preview-before-commitment becomes a broad Beast pattern

Experience Try-On already demonstrates:

> temporary change -> observe -> verify -> mandatory automatic rollback.

Where technically appropriate, reuse that pattern for:

- presentation changes;
- provider preference changes;
- selected configuration changes;
- Pack updates;
- recovery/restore staging;
- Shadow Beast rehearsals.

Do not force every change through an identical preview mechanism; the principle is **rehearse safely before permanent commitment when the system can prove rollback.**

## B4. Chronicle — one correlated life/field/system story, not another database

Existing durable truth is spread appropriately across:

- creature Memories;
- Expeditions;
- PeerDex;
- achievements/progression;
- rare moments;
- Incidents;
- Transactions;
- important Events;
- known-good/change history.

Do **not** merge those authorities into one giant table.

Instead provide a correlated **Chronicle / Timeline view** that can answer:

- what happened to this Beast?
- what happened on this Expedition?
- what changed on this installation?
- what failures/recoveries happened?
- who/what did we encounter?
- which achievements/rare events occurred?

This can support both technical history and emotional/life history without fabricating events.

## B5. Homecoming / Field Debrief

Existing pieces:

- persistent Expeditions;
- Dock/Home Base detection;
- creature Memories;
- achievements;
- PeerDex;
- route/capture/environment statistics;
- Choreography / Scenes;
- Steward / maintenance systems.

Combined result:

When an Expedition ends and the Beast reaches Home Base/dock, generate a truthful debrief from real collected data:

- duration/distance;
- new-to-device vs new-to-this-Beast discoveries;
- captures/XP deltas where applicable;
- peers encountered;
- rare moments / achievements;
- health/incidents during the trip;
- route/context summary.

The debrief can become a Companion-facing Choreography while optionally surfacing Steward tasks (backup recommended, storage low, update staged, etc.).

No fake emotional telemetry is required; presentation may be expressive while facts stay factual.

## B6. Universal Inspect / “Why?”

Signal metadata already exposes much of the needed truth: source, quality, freshness, privacy, unit, history support, errors and priority.

Make **Inspect / Why?** a platform interaction rather than another standalone app.

From any meaningful value/status/capability, owner can drill into:

- current value/state;
- source/provider;
- freshness/quality/confidence;
- privacy classification;
- recent history;
- System Graph dependency / used-by information;
- related incidents;
- Doctor explanation;
- relevant bounded Tools/Procedures.

This is a major anti-clutter feature because deep truth becomes available everywhere without adding another top-level destination.

## B7. Search evolves into a cross-platform “find anything” surface

Current Universal Search is a strong seed but limited in scope.

Future search may include:

- Workspaces/apps/surfaces;
- Signals/state;
- hardware/capabilities;
- Doctor findings/incidents;
- Procedures/Tools/Actions (Actions should normally expose plan before execution);
- Packs/content;
- creatures/achievements/memories;
- settings;
- Field Library/help/docs.

This can function as a command palette in Studio/desktop/phone while TFT uses contextual/recent shortcuts because text entry on 480x320 is limited.

## B8. Managed egress preview

Pieces already know parts of this:

- Capsule privacy envelope;
- sanitized Support Bundle;
- granular Global Sync policy;
- plugin `data_egress` metadata;
- extension SDK NetworkHandle/data-egress concepts.

Unify the managed-path explanation:

> **What data is about to leave this Beast, to whom, for what purpose, and under which owner policy?**

This is not a censorship/lockdown layer and does not constrain owner/root manual activity. It is explainability for Beast-managed connectors, exports and actions.

## B9. Hardware senses + expression channels

The already-accepted “hardware expands Beast perception” idea can be made more symmetric.

### Perception capabilities
Examples:
- environmental sensors;
- GPS;
- light/motion/orientation;
- supported RF/sensor providers.

### Expression capabilities
Examples:
- TFT/external displays;
- optional LED/lighting;
- optional audio;
- optional haptics;
- future paired physical accessories.

Choreography should target **capabilities**, with graceful fallback. Rare moments, homecoming, moods and lifecycle events can become richer on hardware that exists without requiring separate LED/audio architecture for each feature.

Owner policy, quiet hours and Resource Governor remain authoritative.

---

# C. Product grammar — prevent vocabulary and UX sprawl

Use these words consistently:

- **Facet** = *why* the user cares (Companion, Observe, Operate, Explore, Create, Connect, Steward).
- **Workspace** = where deeper interactive work happens.
- **Mission** = what the owner is doing now / contextual composition of useful destinations and presentation.
- **Instrument** = something observed.
- **Tool** = bounded operation/verb.
- **Procedure** = multi-step goal/workflow.
- **Capability** = what the system can do.
- **Provider** = what supplies a Capability/Signal.
- **Experience** = visual/presentation grammar and feel.
- **Doctor** = what is wrong / why / what is recommended.
- **Pack** = delivery/distribution unit, not a user purpose.
- **Surface / Scene / Choreography** = presentation platform objects.

### Important clarification

A Mission may **reference/select an Experience**, but Mission and Experience should not become aliases. One answers “what am I doing?”, the other answers “how is this presented?”.

Recipes/Blueprints should likewise be shareable authoring/templates over existing Missions/Procedures/Actions, **not another runtime execution engine**.

---

# D. Context should become composable axes, not an exploding mode enum

Current motion context (`pwn`, `walk`, `travel`, `wardrive`) is useful, but Beast is expanding beyond one-dimensional motion.

Prefer independent context facts/tags such as:

- motion: stationary / walking / moving / travel;
- operational: field / home / lab / sandbox;
- docked/home state;
- power: battery / external;
- active Mission;
- active Beast;
- resource/governor state;
- connectivity availability;
- presentation owner.

Presentation and surfacing rules consume combinations of tags/capabilities rather than inventing a permanent named “mode” for every combination.

This preserves the earlier mode ideas without letting `FIELD+HOME+LAB+TRAVEL+...` become a combinatorial switch statement.

---

# E. Home Base should become a maintenance *policy*, not another app

Dock/Home Base already exists as a real signal and updates already use dock+Internet readiness.

Generalize this so low-priority/heavy work can declare requirements/preferences such as:

- dock required / preferred;
- external power required / preferred;
- network required;
- heavy I/O class;
- heavy CPU class;
- safe on battery?;
- interruptible/resumable?;
- owner-visible approval required?;

Possible consumers:

- update discovery/staging;
- backup verification;
- Field Library indexing;
- media preparation;
- content acquisition;
- large support/recovery work;
- optional model/content maintenance.

This should integrate with ModuleRuntime/Task Center/Resource Governor rather than become a separate Home Base scheduler.

Consequential application still follows normal Actions/Transactions/consent rules.

---

# F. Validation / Sandbox findings

## F1. Browser + visual regression is mandatory for Studio/UI quality

Python/unit tests cannot prove the rendered browser/UI is correct.

Sandbox should eventually include:

- real browser end-to-end tests;
- deterministic state fixtures;
- screenshot/golden-frame comparisons;
- exact 480x320 DisplayProfile fixtures;
- interaction/touch simulation;
- build/display-profile metadata on rendered artifacts.

## F2. Visual provenance rule

Never blur these categories:

1. **Concept art** — desired art direction, clearly labeled.
2. **Simulated preview** — model/mock/prototype, clearly labeled.
3. **Exact software render** — generated by the same runtime Scene/renderer path and known DisplayProfile.
4. **Physical framebuffer/device capture** — actual output of physical runtime.
5. **Physical human acceptance** — owner sees/uses real device.

Concept art is not Gate 1 evidence. Exact Preview should use the real renderer wherever practical.

## F3. Validation ladder / receipt

Potential release/compatibility evidence ladder:

1. unit tests;
2. integration tests;
3. browser/visual tests;
4. Docker destructive tests;
5. synthetic virtual-hardware scenarios;
6. real incident replay;
7. Shadow Beast rehearsal;
8. physical Pi validation of exact artifact;
9. release exact tested artifact.

Persist enough validation evidence to feed:

- compatibility status;
- support/reputation evidence;
- Device Passport;
- release provenance;
- extension compatibility fingerprints.

Do not create a Validation app unless a unique user need appears; this is primarily evidence used by Studio/Doctor/support/release tooling.

## F4. Sandbox/SDK scenario contract

Providers/extensions may eventually ship optional:

- virtual provider fixtures;
- diagnostic evidence hook;
- named test scenarios;
- expected Signals/Events;
- expected health state;
- expected bounded Actions/Procedures.

This lets community integrations be tested without every developer owning every hardware combination.

---

# G. Social/local-first opportunities — strong but later

## G1. Local Encounter / Beast-to-Beast exchange

Existing PeerDex + Capsules + privacy policy can later support explicit local/offline Beast exchange:

- privacy-safe public Beast Capsule;
- recurring Beast-capable peer memory;
- optional shared Expedition/team summaries;
- lineage/ancestry exchange later if trust/provenance policy supports it.

Rules:

- no remote control by default;
- no mandatory cloud;
- owner-controlled disclosure;
- current Capsule hash integrity is not authentication, so unverified imported data must never silently grant irreversible progression/ancestry authority.

## G2. Legend Capsule / Hall of Legends artifact

When a creature legitimately reaches Hall of Legends, Beast could create a privacy-curated immutable-ish life summary derived from existing Chronicle facts:

- lineage/heritage;
- appearance;
- selected achievements;
- selected memories;
- Expedition counts/highlights;
- rare moments;
- owner-selected public details.

It could remain local, be exported as a Capsule, and later contribute bounded legacy metadata to descendants. This needs owner/product input before economics/reward semantics are frozen.

---

# H. Small but important UX requirements

## H1. Context-driven discovery, not app-drawer-first

The full app/workspace catalog may be huge and that is fine.

Normal UX should increasingly surface:

- current Mission;
- current context;
- Doctor attention;
- available Capabilities;
- recent/history relevance;
- owner favorites;
- Universal Search.

The full catalog remains available, but does not define the product mentally.

## H2. Cross-surface handoff

The small TFT should be able to hand deeper work to Studio cleanly.

Candidate interaction:

> `Open in Studio` -> local QR/deep link to the exact Incident/Pack/Device/Procedure/setting.

Studio can reciprocate with:

> `Show / Preview on Beast`.

Use local discovery/mDNS where available; no cloud requirement.

## H3. Accessibility / physical field ergonomics

DisplayProfile/presentation acceptance should eventually include:

- minimum touch-target guidance;
- scalable text where layout permits;
- high-contrast option;
- color-independent severity/state cues;
- reduced-motion preference;
- night/low-light behavior;
- outdoor readability considerations.

This belongs in presentation contracts and Gate acceptance, not as a separate Accessibility app.

---

# I. Complexity to kill / explicit non-goals

1. **No separate Doctor per subsystem.** One Doctor, modular specialties.
2. **No separate Machine Map / Capability Graph / Pipeline / Claim databases.** One System Graph, many views.
3. **No Recipe runtime.** Recipes/Blueprints author existing Missions/Procedures/Actions.
4. **No Chronicle mega-database.** Chronicle correlates existing authoritative stores.
5. **No giant mode enum for every contextual combination.** Use composable context axes/tags.
6. **No AI root brain.** AI is optional explain/search/plan client of bounded tools.
7. **No QEMU requirement for Sandbox.** Current accepted direction remains WSL + optional Docker + virtual providers + SSH + replay.
8. **No wholesale OpenTelemetry/Home Assistant/Mender adoption.** Borrow narrow mature patterns where useful.
9. **No A/B-rootfs project on the current upstream image solely because robust appliances use it.** Revisit only if Beast eventually owns a prebuilt image/update architecture where it pays for itself.
10. **Do not keep expanding monolithic server/action files indefinitely.** Existing migration toward registries/runtime contracts should continue incrementally; no flag-day rewrite.
11. **Do not make the app registry the navigation architecture.** Registry remains broad; surfacing remains curated/contextual.
12. **Do not turn Expedition into a universal sensor junk drawer.** New RF/sensor domains keep appropriate records and link to Expedition/session context.

---

# J. Strongest findings from this pass

If only a small number are promoted, the review recommends discussing these first:

1. **Causal/correlation context + reliable time semantics** — because history/Doctor/replay become much more trustworthy.
2. **Persistent-state custody + explicit identity scopes** — because recovery/clone/migration must preserve the right identity and not silently lose critical state.
3. **Incident learning loop** — because failures can become durable operational knowledge and regression tests.
4. **Shadow Beast** — because it can radically reduce risk and physical-Pi iteration.
5. **Universal Inspect / Why?** — because it exposes enormous depth without UI clutter.
6. **Chronicle + Homecoming Debrief** — because technical truth becomes a coherent creature/field life story without fake telemetry.
7. **Context-driven surfacing + composable context axes** — because Beast can become huge without becoming an app drawer.
8. **Exact render provenance + browser/visual regression** — because visual fidelity must be demonstrated, not asserted.
9. **Managed egress preview** — because owner sovereignty is stronger when managed behavior explains what leaves the device.
10. **RF/sensor capability universe + perception/expression channels** — because the Monstergotchi future remains broad without creating permanent UI clutter.

---

# K. What this review does *not* approve

This document intentionally does not freeze:

- final names such as Chronicle, Shadow Beast, Casebook or Den;
- exact reward/economy values;
- exact creature inheritance effects;
- exact retention periods;
- exact social protocol;
- automatic maintenance/application policy;
- navigation layout;
- release milestones.

Those are owner/product choices or implementation details to resolve at the appropriate gate.

---

# L. Suggested next step

Have the planned owner/assistant back-and-forth over these findings.

Then:

1. classify each important finding as **approved / modify / reserve / reject**;
2. fold approved foundation changes into Architecture Contract / migration ledger / roadmap;
3. adjust implementation ordering where a newly found foundation issue should be fixed early (especially time semantics, correlation context, persistent-state custody/identity);
4. resume implementation in meaningful tranches;
5. keep Gate 1 visual/physical acceptance independent and honest.
