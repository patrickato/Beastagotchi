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


---

# Layer 2B — Core engines, collectors and lifecycle ownership

## Current shape

`BeastCore` currently:
- constructs the canonical platform objects;
- constructs 19 collectors;
- constructs many independent engines/managers;
- owns a large number of hand-written async loops;
- manually creates each task in `run()`;
- manually chooses cadence and error behavior per loop.

This is functional and understandable at current scale, but every new subsystem increases the size
and responsibility of the Core composition root.

## Module concept earns a place — as lifecycle metadata, not a forced base class

A first-class **Module** concept appears justified.

The goal is not to force every collector/engine into identical implementation code.

Instead, a ModuleSpec / ModuleRegistration can describe lifecycle and platform behavior around an
existing object/function.

Candidate metadata:
- id;
- kind: collector / engine / service / optional worker;
- owner/component instance;
- cadence;
- source priority;
- stale threshold;
- resource class/cost;
- required capabilities;
- dependencies/order;
- enabled predicate;
- startup behavior;
- shutdown/checkpoint hook;
- health probe;
- failure policy;
- governor scaling policy;
- State namespaces/Signals produced;
- Events produced/consumed;
- persistence/backup scope.

The implementation may still be:
- a `Collector.collect()`;
- an engine `tick()`;
- an async callback;
- an event-driven subscriber.

Do not create inheritance complexity merely to make the types look uniform.

## Scheduler

A Core scheduler/ModuleRuntime should own the repeated mechanics:
- cadence/timers;
- cancellation;
- exception handling;
- health state;
- duration/runtime telemetry;
- backoff;
- stale marking;
- governor-based cadence scaling where allowed;
- event/update publication helpers;
- lifecycle start/stop ordering.

Benefits:
1. `core.py` becomes a composition manifest rather than dozens of custom loops.
2. Doctor gets generic module health automatically.
3. Studio can enumerate running/dormant modules automatically.
4. ResourceGovernor can influence optional/expensive cadence systemically.
5. Dormant optional capabilities can truly sleep.
6. Future Packs/providers can register bounded workers without editing Core's task list.
7. Performance attribution becomes much easier.

## Important governor distinction

Do **not** globally slow essential truth collectors merely because the Pi is hot.

Suggested resource classes:
- **critical/control** — health, power/thermal, presentation ownership, essential Pwnagotchi/bridge
  truth; never arbitrarily starved;
- **live/operational** — radio/GPS/core platform state; limited reduction only when safe;
- **derived** — overview, topology, library indexing, compatibility calculations;
- **ambient/optional** — decorative/previews/background enrichment; aggressively reducible/dormant.

The governor should express budgets/policy.
The scheduler should enforce the policy according to each module's declared class.

## Event-driven modules

Not every future module should poll.

ModuleRuntime should allow:
- periodic/tick;
- event subscription;
- signal-change subscription;
- on-demand/procedure;
- startup-only;
- idle/dormant until capability exists.

This is important for a large ecosystem with a small active working set.

## Core composition root

Preferred future Core shape:

    StateRegistry
    Store
    EventBus
    Registries
    ResourceGovernor
    ModuleRuntime
    ActionBroker
    TransactionEngine
    API

then:

    register(core_modules)
    discover(trusted_extension_modules)
    validate_dependencies()
    start()

instead of Core manually understanding every subsystem's loop.

## Duplicate conceptual managers — confirmed structural debt

`BeastCore` owns:
- `self.roster`;
- `self.global_sync`;
- `self.memories`.

`ActionBroker` currently constructs separate:
- `BeastRoster(store)`;
- `GlobalProfileSync(...)`;
- `BeastMemoryEngine(...)`.

Current severity:
- `BeastRoster` appears DB-backed and re-reads active state rather than caching it, so immediate
  divergence risk is lower than first suspected;
- the duplicate objects also share the same Store/SQLite connection.

Nevertheless this is the wrong ownership shape.

### Recommendation
Inject the Core-owned roster/global-sync/memory instances into ActionBroker.

Reasons:
- one conceptual owner represented by one runtime object;
- future in-memory caches cannot silently diverge;
- tests can assert identity;
- Action path and progression path share the same lifecycle;
- fewer hidden object graphs.

This is a relatively cheap, high-value cleanup and should likely precede large progression/
breeding expansion.

## What should stay deliberately simple

- collector implementations may remain simple classes;
- physical/debounce thresholds do not need dynamic plug-in systems;
- Core should remain one local process unless measurement proves a separate process is necessary;
- the scheduler should not become a mini-Kubernetes/systemd clone.

Use familiar lifecycle concepts without reproducing an operating system inside Beastagotchi.


---

# Layer 2C — Mutation authority: Actions, Transactions and owner override

## ActionBroker — keep the boundary, change the dispatch structure

The ActionBroker concept is strong:
- allow-listed operations;
- plan before perform;
- operator/owner policy;
- no generic shell API;
- durable action audit;
- explicit broker adapters for plugins/services/containers/packs/etc.;
- owner override is distinct from technical capability.

This should remain the mutation doorway for managed Beast operations.

Current scaling concern:
- `plan()` and `perform()` are long parallel action-name dispatch chains;
- adding one Action requires editing both;
- third-party extension requires central Core edits;
- plan/perform drift becomes more likely as Action count grows.

### Direction: Action Registry

Each ActionSpec/handler should declare:
- action id;
- parameter schema;
- plan handler;
- perform handler;
- required operator level;
- owner-override policy;
- risk class;
- required capabilities;
- whether it is read-only / simple mutation / transactional mutation;
- verification behavior;
- privacy/logging policy;
- UI label/description hints if useful.

ActionBroker remains the authority:
1. lookup registered Action;
2. validate;
3. authorize;
4. plan;
5. dispatch through direct or Transaction path;
6. audit;
7. publish outcome.

Do not allow arbitrary third-party raw-shell handlers to masquerade as trusted Actions.

## Transaction — existing pattern, missing shared contract

The project already contains multiple transaction-like implementations:

### Pack install
- plan;
- compatibility check;
- staged/inert content;
- transaction id/directory;
- previous copy snapshot;
- journal;
- verification;
- rollback;
- bounded rollback payload retention.

### Pack update
- trusted source;
- verified download staging;
- intake;
- install;
- probation;
- automatic rollback on failed probation;
- history.

### Presentation switching
Current planner already models:
- prepare/release;
- acquire;
- verify;
- rollback path.

Physical execution is intentionally still disabled pending validation.

### Backup/support/jobs
Already model long-running status/result/artifact lifecycles.

These are convergent evidence that Transaction deserves a first-class platform contract.

## Proposed Transaction lifecycle

Not every Action needs this.

For consequential/reversible/multi-step mutations:

    PLAN
      ->
    SNAPSHOT / PREPARE
      ->
    APPLY
      ->
    PROBATION / OBSERVE
      ->
    VERIFY
      ->
    COMMIT
       or
    ROLLBACK
      ->
    JOURNAL / EXPLAIN

TransactionSpec may declare:
- id/kind;
- Action origin;
- actor;
- target;
- plan;
- before fingerprint/snapshot;
- ordered steps;
- verification conditions;
- probation interval;
- rollback adapter;
- restart/reboot requirements;
- resource/storage requirements;
- result;
- Doctor interpretation;
- timestamps.

## One Transaction Journal

A high-value longer-term consolidation is one append-only Transaction Journal consumed by:
- Doctor;
- Recovery Vault;
- support bundles;
- known-good drift;
- owner customization history;
- Studio history;
- Procedures.

This does not require every subsystem to store huge rollback payloads in one database.
The journal can reference subsystem-specific snapshots/artifacts.

## Simple Action versus Transaction

Avoid bureaucratizing the system.

Examples likely **not** requiring a full Transaction:
- read-only snapshot;
- provider preference selection that activates nothing;
- opening/saving a lightweight owner preference;
- Doctor known-good checkpoint if it only writes Doctor metadata.

Examples likely requiring Transaction:
- plugin enable/disable with service restart;
- package/dependency changes;
- Pack install/update/activation where executable behavior changes;
- presentation ownership switch;
- config rewrite;
- recovery restore;
- provider handoff/failover;
- major cleanup with destructive deletion;
- OS/base update.

The ActionSpec should declare which lifecycle it requires.

## Owner sovereignty — current design is good

`OwnerModeManager` makes a valuable distinction:
- Expert Mode is not OS privilege;
- normal brokers still execute the change;
- successful policy overrides mark the device customized;
- owner support state becomes visible.

Preserve:
- policy blocker != technical impossibility;
- local/root owner remains able to bypass Beast outside the managed system;
- managed override paths are explicit/audited.

### Improve: append-only customization ledger

Current OwnerMode retains summary/last-override state plus action audit.

Eventually unify this into an append-only customization/override ledger:
- actor;
- timestamp;
- action;
- target;
- reason/policy blocker;
- before/after;
- Transaction id;
- revert availability.

Doctor can then distinguish:
- unexplained drift;
- known owner customization;
- failed mutation;
- current managed state.

## Procedures sit above Actions/Transactions

Procedure is orchestration, not a competing mutation authority.

A Procedure:
- invokes probes;
- calls registered Actions;
- may start Transactions;
- gathers results;
- invokes Doctor interpretation;
- presents next steps.

This prevents a future Procedure ecosystem from becoming a shadow shell-script execution framework.


---

# Layer 2D — Capabilities, dependencies and providers

## Current boundary is strong

The current separation is structurally correct:

### DependencyCapabilityResolver
Answers:
- what a component requires;
- whether evidence satisfies it;
- technical blocker vs policy blocker;
- remediation class;
- which providers can satisfy it.

It is deliberately side-effect free.

### CapabilityProviderArbitrator
Answers:
- candidate providers;
- selected/ready state;
- active provider;
- owner preference;
- recommendation;
- fallback chain;
- health/confidence/freshness;
- whether an owner choice is required.

It is deliberately read-only:
- no automatic selection mutation;
- no automatic failover.

### ProviderPreferenceManager
Stores owner preference only.
Setting a preference does not enable/start/switch a provider.

Protect this separation.

## Future scaling concern

Native-provider discovery and some requirement knowledge currently live as hard-coded resolver logic.

As hardware/plugins/community providers grow, introduce registries rather than extending one giant
resolver indefinitely.

Potential contracts:
- CapabilitySpec;
- ProviderSpec;
- RequirementProbe.

A ProviderSpec may declare:
- provider id;
- capabilities provided;
- readiness/health evidence;
- confidence/freshness;
- technical requirements;
- selection state;
- activation adapter if one exists;
- resource cost;
- ownership/conflict class.

The read-only resolver/arbitrator consumes registrations.
Activation remains an Action/Transaction responsibility.

## Automatic failover

Do not enable merely because fallback chains exist.

Future automatic provider handoff should require:
- provider-specific Transaction adapter;
- snapshot/prepare;
- acquire;
- probation;
- verification;
- rollback;
- Doctor evidence;
- owner policy allowing automatic failover.

The current explicit `automatic_failover_enabled=False` is the correct default.

---

# Layer 2E — Doctor's structural place in Core

## Doctor is an interpreter/medical authority, not mutation authority

Current `BeastDoctor` is correctly read-only over canonical Beast state plus a durable Patient
Chart.

Doctor should own:
- diagnostic interpretation;
- Patient Chart;
- diagnostic coverage;
- recurrence memory;
- known-good comparison;
- causal/explanation output;
- recommendations;
- treatment outcome memory;
- health presentation semantics.

Doctor should **not** directly own:
- systemctl/package mutation;
- plugin mutation;
- provider switching;
- config rewriting;
- display ownership mutation;
- arbitrary shell execution.

Preferred treatment flow:

    Doctor finding
        ->
    explanation / evidence
        ->
    recommended Action or Procedure
        ->
    owner/policy approval
        ->
    ActionBroker / TransactionEngine
        ->
    verification evidence
        ->
    Doctor interprets result
        ->
    Patient Chart remembers

This supports the TFT heartbeat/health affordance while keeping authority clean.

## Doctor and IncidentEngine

IncidentEngine currently owns detailed durable system incidents.

Patient Chart correctly stores compact recurrence summaries instead of duplicating the Black Box.

Long-term Doctor should consume IncidentEngine/Store as one of its evidence sources rather than
re-implementing the same incident detectors.

Suggested hierarchy:
- collectors/modules publish canonical state;
- SemanticEngine produces meaningful transitions;
- IncidentEngine owns detailed condition episodes;
- Doctor interprets incidents + provider/dependency health + drift + diagnostic coverage;
- Patient Chart remembers compact patient history.

Avoid two independent systems separately deciding that the same condition exists.

## Doctor coverage should expand by evidence, not giant hard-coded if chains

As Module/Signal/Capability registries mature, Doctor can derive more of its diagnostic map from
registered metadata:
- module health probes;
- capability status;
- provider decisions;
- Signal freshness/quality;
- known conditions/runbooks;
- Transaction outcomes.

This lets Doctor coverage grow with the ecosystem.

Condition/runbook packs may teach Doctor how to interpret new conditions, but knowledge does not
inherit mutation authority.

## Doctor UI/actions

A Doctor finding should be able to expose contextual next steps:
- VIEW EVIDENCE;
- RUN DIAGNOSTIC;
- TAKE ACTION;
- FIX THIS;
- RESTART & VERIFY;
- RUN PROCEDURE;
- BUILD SUPPORT BUNDLE;
- IGNORE / REMIND LATER where appropriate.

These are links into registered Actions/Procedures, not direct Doctor-side mutations.

## Patient Chart

Current design is strong:
- privacy-light technical identity;
- diagnostic coverage;
- bounded recurrence;
- bounded known-good history;
- change-gated writes.

Future additions worth considering:
- successful/failed remedy history;
- Transaction references;
- owner-customization references;
- condition last-treatment/last-verified timestamps;
- chronic/recurrent classification;
- explicit "under observation/recovery" state for the proposed blue heartbeat status.

Do not turn Patient Chart into a full duplicate event database.

