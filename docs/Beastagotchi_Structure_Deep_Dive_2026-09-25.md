# Beastagotchi Structure Deep Dive

**Date:** 2026-09-25  
**Status:** active architectural review  
**Method:** inspect current docs and actual code, preserve strengths, identify structural debt without
assuming a rewrite is required.

---

# Layer 1 — Linux/Pi, Pwnagotchi and Beastagotchi boundary

## Core structural principle: three distinct layers

Treat these as related but distinct ownership domains:

1. **Linux / Raspberry Pi platform**
   - hardware;
   - kernel/drivers;
   - filesystem/storage;
   - systemd/services;
   - networking;
   - packages;
   - thermals/power;
   - framebuffer/input devices.

2. **Pwnagotchi platform**
   - Pwnagotchi agent/runtime;
   - Bettercap relationship;
   - radio behavior;
   - Pwnagotchi plugin callbacks;
   - Pwnagotchi configuration;
   - native Pwnagotchi UI/frame;
   - Pwnagotchi session/capture semantics.

3. **Beastagotchi platform**
   - canonical Beast state;
   - Doctor;
   - progression/identity/roster;
   - Experiences/Scenes;
   - Packs/Apps/Procedures;
   - Studio;
   - Beast-managed Actions/Transactions;
   - Beast persistence/content/recovery.

A cross-layer feature may span all three, but it must not erase ownership boundaries.

Procedures and Doctor should explicitly know/report which layer a finding or Action belongs to.

---

## Three-lane Pwnagotchi boundary

### Lane A — OBSERVE

Beast may observe Pwnagotchi through supported/read-only mechanisms.

Current strong implementations:
- `pwnagotchi_plugin/beast_bridge.py` uses supported plugin callbacks and performs no Bettercap/
  radio mutation;
- bridge output is written atomically under `/run`;
- `BridgeCollector` caches unchanged JSON and gives live callback data high source priority;
- `PwnagotchiCollector` reads version/config/session/cache/plugin inventory without mutating them;
- secret-bearing config fields expose presence/type but not credential values.

Desired rule:
> Observation adapters may learn broadly, but do not acquire behavioral authority merely because
> they can see Pwnagotchi internals.

### Lane B — PRESENT

Physical display/touch ownership is a separate concern from data observation.

Current strong implementations:
- ADR 0003 requires exactly one physical presentation owner;
- `PresentationBroker` models Native / Theme Manager / Beast ownership independently;
- current executor remains disabled until physical handoff adapters are validated;
- Native Pwnagotchi Bridge consumes Pwnagotchi's own rendered frame rather than reconstructing the
  stock UI, allowing Beast to remain the display owner while preserving real upstream visuals.

Desired rule:
> Reading Pwnagotchi state, rendering a Pwnagotchi-derived view, and owning the framebuffer are
> three different permissions/capabilities.

### Lane C — MUTATE

Normal observation/plugin bridge code must not silently mutate Pwnagotchi.

Future supported changes to:
- config;
- plugin state;
- service state;
- presentation settings;
- package/dependency state;

should pass through explicit Beast Actions/Transactions with:
- plan;
- ownership/privilege check;
- backup/snapshot when relevant;
- owner consent according to risk;
- execution;
- verification;
- rollback/probation where relevant;
- audit/provenance.

Manual/root owner escape remains available outside the managed path.

---

## What is especially good today

1. **Pwnagotchi remains an upstream substrate rather than becoming a hidden Beast implementation
   detail.**
2. **The bridge is intentionally read-only.**
3. **Live callback telemetry and slower filesystem/config observation are separated.**
4. **Native UI fidelity uses the actual upstream frame rather than guessing at Pwnagotchi state.**
5. **Presentation ownership is explicit and intentionally not yet auto-executed.**
6. **Beast can evolve substantially without requiring Jayofelony/Pwnagotchi to absorb Beast-specific
   progression/UI/Doctor logic.**

These are structural strengths worth preserving.

---

## Fresh-eye concerns / improvements

### A. Formalize upstream authority per Signal

Live bridge and slower Pwnagotchi collectors can both produce related state.

Current StateRegistry priorities reduce conflicts, but authority should become explicit for important
Pwnagotchi Signals:
- authoritative source;
- fallback source;
- freshness threshold;
- historical-only source.

Example:
- live AP/channel activity -> bridge/Bettercap live provider;
- historical capture/cache metadata -> filesystem collector;
- configured plugin inventory -> config/plugin collector.

Do not rely indefinitely on numeric source priority as the only documentation of semantic
authority.

### B. Bridge event sequence restart bug-risk

`BeastBridge` starts its event sequence at zero on plugin process/reload.

`BridgeCollector` keeps a local `_last_seq`.

If Pwnagotchi/bridge restarts while Beast Core remains alive, new events may begin again at sequence
1 while the collector remembers a larger old sequence and may ignore the new events until the
sequence exceeds the previous value.

Recommended correction:
- bridge instance/session UUID;
- boot/process generation;
- or explicit sequence-regression detection/reset.

This should be test-backed.

### C. Bridge file local privacy

The bridge currently writes mode `0644` while event content may include peer identity and
AP/client identifiers.

Review whether:
- `0640` with a Beast/Pwnagotchi group;
- `0600` with matching service ownership;
- or a sanitized split between general state and sensitive event detail

is more appropriate.

The answer should preserve practical interoperability while following least-privilege principles.

### D. Upstream path/version assumptions are scattered

Current code knows Pwnagotchi-specific paths such as:
- `/etc/pwnagotchi/config.toml`;
- handshake/session directories;
- custom plugin directory;
- native frame path;
- service names.

These assumptions are valid today but vulnerable to upstream changes.

Consider a versioned **Pwnagotchi Adapter / Upstream Platform Adapter** that centralizes:
- detected Pwnagotchi version/build;
- path discovery;
- feature/callback availability;
- native-frame source;
- configuration layout;
- service identities;
- supported managed mutations;
- compatibility profile.

Beast Core modules then ask the adapter rather than each hardcoding upstream details.

This adapter should not become an authority over Pwnagotchi behavior; it is an isolation boundary
against upstream churn.

### E. Bettercap/radio behavioral ownership must stay clear

Pwnagotchi owns normal radio/agent behavior.

Beast may:
- observe;
- diagnose;
- display;
- restart/recover through explicit Actions where appropriate.

The telemetry bridge itself should never become a covert Bettercap command channel.

If future Lab/advanced functionality intentionally controls radio behavior, it should be a separate
explicit capability/mode with its own authority, consent and audit—not an expansion of the read-only
bridge.

---

## Structural direction

Preferred relationship:

    Linux / Pi
        |
        +-- Pwnagotchi
        |      |
        |      +-- read-only callbacks / native frame / config evidence
        |      |
        |      +-- managed mutation adapters (only through Actions/Transactions)
        |
        +-- Beast Core
               |
               +-- canonical State / Signals / Events
               +-- Doctor / Procedures
               +-- Experience / Scene / UI / Studio

Possible isolation seam:

    Pwnagotchi Adapter
        |- version / compatibility
        |- paths / service identities
        |- observation sources
        |- native-frame source
        |- supported mutation adapters
        |- health evidence

The adapter should make upstream changes cheaper without turning Pwnagotchi into a Beast-owned
implementation detail.

---

## Layer-1 questions to carry forward

- Which Pwnagotchi data is truly canonical versus merely evidence/fallback?
- Which mutations should Beast ever support as managed Actions?
- Should the read-only bridge remain a file contract permanently, or gain an optional event-stream
  transport while retaining the file as a robust fallback?
- How should Pwnagotchi compatibility profiles be versioned/tested against upstream releases?
- What should Doctor be allowed to repair automatically versus only recommend?
- How do owner manual edits get detected and incorporated into known-good/customized state?


---

# Layer 2A — Canonical truth: StateRegistry, Signals and Events

## StateRegistry — protect this foundation

`StateRegistry` is currently one of the strongest structural components.

It provides:
- one canonical flat-key truth surface;
- source identity;
- freshness timestamp;
- quality state;
- error metadata;
- global sequence;
- source priority;
- thread-safe read/write;
- deep-copy isolation.

This allows collectors/providers to compete for the same semantic key without making UI/Doctor know
collector internals.

### Keep
- single canonical registry;
- flat semantic keys;
- metadata beside value;
- priority arbitration;
- stale/unavailable distinction;
- sequence/change tracking.

### Improve
1. **Explicit authority metadata**
   Numeric priority works, but important Signals should eventually declare intended authoritative
   provider/fallback semantics rather than making priority numbers the only documentation.

2. **Error arbitration**
   `set_error()` currently does not apply the same priority arbitration as `update_many()`.
   It is not a major active Core path today, but before broad adoption it should be hardened so a
   lower-priority provider error cannot incorrectly replace a healthy higher-priority source.

3. **Provenance/ownership introspection**
   Studio/Doctor should be able to answer:
   - who currently owns this key;
   - who else could provide it;
   - why this source won;
   - when fallback occurred.

Do not replace StateRegistry with a more elaborate database/event-sourcing system merely because
the project is growing.

## Signal — correct abstraction, metadata needs a registry

Signal v1 is structurally sound:
- it does not collect;
- it does not persist;
- it describes canonical StateRegistry values for presentation/integration consumers.

Current metadata is split between:
- `TelemetryCatalog.EXPLICIT/PREFIXES`;
- `SignalCatalog._PRIVACY_PREFIXES`;
- history prefixes;
- structured hints.

That is acceptable v1 but becomes a future extension choke point.

### Direction: SignalSpec registry

A SignalSpec may eventually declare:
- id/pattern/namespace;
- label/category;
- value type/structure;
- unit;
- cadence expectation;
- privacy class;
- publication policy;
- history policy;
- formatting hints;
- semantic bounds;
- authoritative/fallback provider semantics.

Core/built-ins register built-in specs.
Trusted extension contracts can register namespaced specs.
StateRegistry remains the actual value owner.

Telemetry Inspector, Studio, Scenes, Packs, Doctor and API should eventually consume one shared
Signal semantic source rather than growing independent metadata tables.

## Event — keep it light, make meaning explicit

Current `EventBus` is intentionally small:
- UUID;
- timestamp;
- type;
- source;
- severity;
- data;
- bounded recent history;
- async subscriber queues.

That is a good hot-path shape.

Current structural limitations:
- transient/durable semantics are partly hard-coded outside the Event contract;
- durability requires callers to remember to also write to Store;
- subscriber queue overflow is silently dropped;
- event payload shape is not registered/validated;
- there is no correlation/causation;
- privacy/publication semantics are absent from the event itself.

### Direction: EventSpec / Event envelope v2

Keep the EventBus fast, but allow an EventSpec registry to declare:
- type;
- default severity;
- transient/durable class;
- expected data keys/schema;
- privacy/publication class;
- retention expectation.

Add optional event envelope fields:
- correlation_id;
- causation_id;
- schema/version;
- privacy class.

Add delivery observability:
- dropped-event counter by subscriber/event type;
- lag/queue depth where useful.

Do **not** turn EventBus into a heavyweight message broker.

## SemanticEngine

The SemanticEngine is correctly observational:
- turns high-frequency state into low-volume meaningful transitions;
- debounces noisy GPS state;
- generates temperature-band transitions;
- distinguishes device-first from Beast-first discovery.

This belongs above StateRegistry and below progression/experience consumers.

Long-term semantic/event rules may become registrable, but physical thresholds/debounce logic
should remain deliberately boring and stable where possible.

## TelemetryCatalog vs SignalCatalog

They are not wrong, but they currently represent overlapping semantic layers.

Preferred future shape:
- StateRegistry: values + source/freshness/quality;
- SignalSpecRegistry: semantic metadata/policy;
- SignalCatalog/API: resolved public view over StateRegistry + SignalSpec;
- Telemetry Inspector: consumer of SignalCatalog.

Avoid two independent growing metadata vocabularies.

