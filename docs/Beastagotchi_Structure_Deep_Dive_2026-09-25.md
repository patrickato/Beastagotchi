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


---

# Layer 2F — Persistence and API boundaries

## SQLite is the right persistence technology

Keep one local SQLite database.

Current good choices:
- WAL mode;
- synchronous=NORMAL;
- batched sample writes;
- bounded history queries;
- pruning;
- FTS5 with graceful fallback;
- durable event/action/job/incident/roster data;
- low-frequency indexing where appropriate.

Do not replace SQLite with a network database, Redis or an ORM merely because Beastagotchi becomes
feature-rich.

## High-priority correctness issue: SQLite thread affinity

Confirmed structural issue:

- `Store.__init__` creates `self.conn = sqlite3.connect(self.path)` with default
  `check_same_thread=True`;
- `LocalActionServer` runs `ActionBroker.plan/perform` using `asyncio.to_thread()`;
- ActionBroker roster/global/memory objects are backed by the Core-owned Store/connection;
- `BeastRoster` directly holds `store.conn` and performs SQL through it.

The project already recognized thread affinity for:
- `Store.add_action()`;
- `Store.upsert_job()`;

and uses short-lived worker-thread connections there.

But roster/synthesis/presentation-preference/global/memory Action paths may still access the
event-loop-created connection from an Action worker thread.

### Priority
**High. Fix before expanding breeding/roster/Procedure mutations.**

### Preferred architectural remedies to evaluate

Do not simply set `check_same_thread=False` and hope concurrency is safe.

Better candidates:
1. **connection-per-thread / connection factory** for repository operations;
2. dedicated SQLite writer/DB worker with queued mutations;
3. async Action orchestration that delegates only filesystem/subprocess blocking work to threads
   while DB mutations remain on the owning thread;
4. repository-specific short-lived connections for mutation paths.

Selection should consider:
- WAL concurrency;
- transaction atomicity;
- current direct `store.conn` consumers;
- performance on Pi;
- testability.

Add explicit tests that execute representative roster/synthesis/memory Actions through
`LocalActionServer` / worker-thread execution against a real SQLite file.

## Schema migrations need a real version ladder

Current `_migrate()` is forward-only/ad-hoc column inspection.

This is acceptable during rapid prototyping but should not become the long-term database contract.

Add:
- `PRAGMA user_version`;
- ordered migrations;
- idempotent migration tests from representative historical schemas;
- backup/checkpoint before risky future migrations;
- Doctor visibility for migration failure.

Keep migrations additive/boring where possible.

## WAL management

WAL mode is appropriate.

Consider measured periodic checkpoint policy:
- not every transaction;
- checkpoint when WAL exceeds a threshold or during safe idle/dock windows;
- `wal_checkpoint(PASSIVE)` / `TRUNCATE` based on measured behavior;
- expose DB/WAL sizes to Performance/Doctor.

Do not over-optimize before measuring actual SD/write behavior.

## Repository boundaries

`db.py` is becoming a large multi-domain file.

Long-term, keep one Store/DB but expose domain repositories/facades:
- EventRepository;
- HistoryRepository;
- RosterRepository;
- IncidentRepository;
- ExpeditionRepository;
- ActionJournalRepository;
- LibraryRepository;
- DoctorRepository.

This is code organization and concurrency ownership—not a reason for multiple databases.

## HTTP API boundary is excellent

Current split should be preserved:

### Loopback HTTP/WebSocket
Read-only:
- state;
- Signals/telemetry;
- events/history;
- Doctor;
- Experiences;
- platform bundle;
- library/search;
- records.

### Unix-domain Action socket
Mutation:
- root-owned;
- dedicated local group;
- filesystem permissions;
- peer credentials;
- allow-listed ActionBroker;
- no generic shell primitive.

This is a strong security/ownership boundary.

Beast Studio/browser should continue to talk through its authenticated boundary rather than
directly receiving privileged socket access.

## WebSocket should become the normal live UI transport

The API already sends:
- initial full state snapshot;
- subsequent `state.changed` patches;
- Events;
- heartbeat with state sequence.

BeastUI currently still polls full `/live` snapshots every 0.5 seconds.

Preferred future data path:
1. full snapshot on connect/reconnect;
2. WebSocket state patches/events during normal operation;
3. batched HTTP for slower history/bulk resources;
4. sequence-gap detection;
5. resync snapshot on gap/reconnect.

Benefits:
- less JSON serialization;
- less copying;
- less localhost connection churn;
- lower CPU/heat;
- more immediate updates;
- clear resynchronization semantics.

The existing polling path can remain as fallback/recovery.

## API route growth

`LocalAPI` is accumulating a long route `if/elif` chain.

Like Actions/Pages, this is a future registry/router cleanup rather than an urgent architectural
failure.

A lightweight read-route registry can eventually map:
- path;
- handler;
- query schema;
- privacy/publication policy;
- cache class.

Do not introduce a heavy web framework merely to remove an if-chain unless there is another strong
reason.


---

# Layer 3A — Packs, content and executable trust boundaries

## Pack is a delivery envelope, not runtime authority

This distinction should become explicit.

A Beast Pack is a versioned/distributable envelope that may contain one or more logical things:
- themes;
- faces;
- animations;
- audio;
- layout/board definitions;
- missions/Experiences;
- lifecycle choreography;
- maps/data;
- apps;
- Procedures;
- hardware/provider declarations;
- trusted executable extensions.

Being delivered inside a Pack does **not** itself grant execution or mutation authority.

Pack lifecycle and content/runtime lifecycle must remain separate concepts.

## Current Pack intake is a strong security foundation

Current `PackIntakeManager` already:
- limits archive size;
- limits expanded size/member count;
- rejects path traversal;
- rejects links/devices;
- requires exactly one root manifest;
- stages before install;
- executes nothing.

Current `PackInstallManager`:
- installs verified content transactionally;
- snapshots previous versions;
- journals installs;
- verifies;
- rolls back;
- does not automatically activate services/plugins/code.

Current `PackActivationManager` for content-only Packs:
- allows only inert content classes;
- rejects Python/shell/shared libraries/executables/systemd units;
- rejects executable permission bits;
- rejects background services;
- rejects privileged permissions/service changes.

**Protect this separation.**

## Activation tiers

Formalize activation tiers instead of treating all Pack types equally.

Suggested model:

### Tier 0 — metadata/catalog only
- discoverable;
- previews/manifest;
- not installed;
- no runtime effect.

### Tier 1 — inert content
Examples:
- theme;
- face;
- animation recipe;
- audio/media;
- layout/board;
- mission data;
- map/data;
- lifecycle choreography data.

Properties:
- no executable code;
- no service mutation;
- no package installation;
- safe declarative parsing;
- can usually be enabled/disabled without restart.

### Tier 2 — declarative integration
Examples:
- Signal/Capability declarations;
- Procedure definitions composed from already-registered Actions;
- Experience Scene definitions using approved primitives;
- hardware profiles pointing at existing provider adapters.

Properties:
- still does not execute arbitrary code;
- may register declarative platform objects;
- validated against schemas/contracts.

### Tier 3 — trusted executable extension
Examples:
- genuinely new renderer primitive;
- hardware/provider adapter;
- new collector/module;
- specialized integration requiring Python/native code.

Properties:
- explicit trust/source;
- code review/signature/provenance policy;
- declared permissions;
- activation Transaction;
- resource/health contract;
- potentially service/package changes;
- never enabled merely because installation succeeded.

This tier should be comparatively rare.

## Current manifest strengths

Existing manifest already understands:
- identity/version/type;
- author/license/homepage/source;
- dependencies/conflicts;
- capabilities;
- permissions;
- services/restarts;
- display support;
- resource/thermal class;
- content roles;
- Signals provided/consumed;
- companion relationships;
- Beast/Pwnagotchi compatibility.

That is a good base.

## Missing manifest concepts for a large ecosystem

Add/version over time:
- **download_bytes**;
- **installed_bytes**;
- **temporary_install_bytes**;
- **decoded/working_set estimate** where meaningful;
- **components** / optional subpackages;
- object/content hashes;
- target/display variants;
- local/offline requirement;
- license per component/object where needed;
- content provenance;
- preview assets;
- cacheability/eviction policy;
- trust/activation tier;
- executable entrypoints only for trusted tier;
- Scene/App/Procedure registrations;
- lifecycle/choreography registrations.

These are necessary for 16/32 GB devices and accurate install planning.

## Current size ceilings need to become policy by tier

Pack intake currently defaults to roughly:
- 128 MiB compressed archive;
- 512 MiB expanded;
- 2048 members.

These are sensible anti-abuse defaults for today's Pack model.

They should not accidentally become the permanent maximum size of optional cinematic/map/media
content.

Future large media should preferably use:
- component/object downloads;
- Content Store objects;
- bounded per-object validation;
- streaming/staged acquisition;
- explicit storage planning;

rather than simply raising one monolithic archive limit to many gigabytes.

## Validation by content type

Current content-only activation performs useful type-specific validation for themes/faces/
animations/layouts/boards/missions.

As content grows, each declarative content role should have a schema validator.

Do not rely only on "contains no .py" as proof that data is valid.

Examples:
- audio: supported codec/duration/size;
- image: format/dimensions/decompression bounds;
- video/cinematic: codec/resolution/duration/decoder requirements;
- map/data: schema/version/size;
- Scene definition: allowed primitives/Signals/touch/Actions;
- Procedure definition: registered steps only;
- lifecycle choreography: bounded stage/event grammar.

---

# Layer 3B — Experiences, Pages and Scenes

## Hidden ceiling confirmed: Experience metadata is open; rendering is not yet fully open

Current strengths:
- ExperienceDNA allows built-in or namespaced extension vocabulary;
- Pack Mission/Experience definitions can provide DNA/policy;
- Experience Compiler is read-only and capability/platform aware;
- it honestly reports missing page coverage/native target support;
- built-in renderer lookup already uses a registry.

Current limitation:
- Pack Experiences ultimately reference renderer coverage known by the core;
- a new Pack may define new DNA, but it cannot yet invent a truly new safe renderer/Scene grammar
  without trusted Python/core code;
- built-in Experience surfaces are duplicated between
  `beastcore/experience_surfaces.py` and `beastui/experience_registry.py`;
- built-ins are imperative Python renderers while Pack Experiences are pushed toward declarative
  composition.

Therefore the architecture is **open in intent but still partially privileged in implementation**.

## Convergence target: data-first Scene definitions

Preferred long-term path:

    Experience DNA
          +
    Page/Surface declarations
          +
    Scene definitions
          +
    approved render primitives
          +
    Signal bindings
          +
    assets/content
          ↓
    Experience Compiler
          ↓
    compiled Scene target
          ↓
    Scene Runtime / compositor

Most new community Experiences should be possible as **data/content**, not arbitrary Python.

A Scene definition can declare:
- layer id;
- primitive/component kind;
- bounds/layout constraints;
- z;
- Signal bindings;
- update class;
- resource class;
- touch/action binding;
- reduced-motion behavior;
- privacy;
- assets;
- formatting/transforms;
- fallback behavior.

The renderer executes only approved primitives/components.

## Built-ins should dogfood the same path where practical

Claude independently highlighted this and the fresh review agrees.

Atlas/Forge/Observatory/Habitat/Monolith can remain hand-tuned during Gate 1, but the target should be
that first-party Experiences eventually compile through the same Scene contracts available to
third-party declarative content.

Benefits:
- community Experiences are not second-class;
- Studio can fork/edit built-ins;
- exact preview uses the same compiler;
- Pack validation is meaningful because first-party code exercises it;
- page/surface registration becomes data-driven;
- render optimization applies consistently.

This migration should be incremental; do not sacrifice current visual fidelity merely to achieve
architectural purity quickly.

## Trusted renderer extensions remain possible

Data-first Scenes cannot predict every future visual idea.

A trusted executable extension tier may register:
- new approved primitive;
- new renderer/component;
- specialized visualization.

Then declarative Scenes can use that primitive by namespaced id.

This preserves:
- open-ended creativity;
- safe default content path;
- rare escape hatch for genuinely new rendering capabilities.

## Page Registry

Current:
- primary page list remains fixed;
- Apps have a registry, but built-in definitions are still static;
- Experience page surfaces are explicit tables;
- UI Pages class still implements hard-coded page methods.

Future PageSpec should declare:
- id;
- label;
- semantic group;
- renderer/Scene;
- required Signals/Capabilities;
- input model;
- visibility/context rules;
- navigation priority;
- source Pack/App;
- supported render targets;
- availability state;
- Doctor/help hooks.

Sources may include:
- core;
- App;
- Experience;
- Pack;
- trusted extension;
- temporary/event surface.

Primary carousel is a curated view over the Page Registry, not the complete universe.

## App Registry

An App Registry already exists, which is good.

Extend its registration source rather than replacing it:
- built-in;
- Pack declarative App;
- trusted extension;
- optional capability.

Apps may open:
- page;
- overlay;
- workspace;
- Procedure;
- external/Studio deep-link where allowed.

Avoid requiring every new capability to become a primary swipe page.

## SceneRuntime is good but currently descriptive, not the complete renderer

Current SceneRuntime tracks:
- semantic layers;
- Signal dependencies;
- dirty layers/bounds;
- cost;
- cacheability;
- resource class;
- touch/privacy/reduced-motion metadata.

This is excellent.

But today imperative renderers still draw pixels directly and SceneRuntime records what happened.

Long-term architecture should become:

    SceneSpec
       ->
    SceneCompiler
       ->
    SceneRuntime/Scheduler
       ->
    Renderer/Compositor
       ->
    framebuffer

This turns dirty-region metadata from an inspection tool into a true execution optimization.

## Scene cache budgets

Current compositor caches are count-limited (24 entries), not memory-budgeted.

For a large asset ecosystem:
- track bytes;
- active/inactive references;
- decode cost;
- last use;
- pinned state;
- governor pressure.

Cache eviction should be byte/resource-budget based.

The active Experience plus nearby/likely-needed surfaces can remain warm; the rest should be cold.


---

# Layer 3C — Content Store, storage pools and small-card scaling

## Current storage model

Today installed Packs are directory copies under:
- built-in: `/opt/beast-ui/packs`;
- installed: `/var/lib/beastagotchi/packs/installed`;
- staged: `/var/lib/beastagotchi/packs/staged`.

Pack update rollback may additionally retain previous full directory copies.

This is simple and correct at current scale.

It will duplicate bytes as the media ecosystem grows and does not yet distinguish:
- reusable shared assets;
- installed logical content;
- evictable downloads/cache;
- active decoded working set;
- optional large media.

## First-class Content Store

Introduce a **Content Store** as a separate concept from Pack.

A Pack is a manifest/distribution envelope.
A Content Object is an immutable validated object identified by digest.

Candidate Content Object metadata:
- SHA-256/object id;
- media/content kind;
- size;
- MIME/format;
- source/provenance;
- author/license;
- compatibility/target class;
- validation status;
- installed/cached/pinned references;
- last access;
- eviction eligibility;
- decode/resource hints.

Logical Pack/component manifests reference objects.

This enables:
- deduplication;
- integrity verification;
- exact provenance;
- component installs;
- safe cache eviction;
- corruption checks;
- re-download/reconstruction;
- content sharing between Experiences/Packs without duplicate storage.

## Do not confuse five independent state axes

Avoid one giant lifecycle enum for every question.

Useful orthogonal state:

### Presence
- catalog_only;
- cached/acquired;
- installed.

### Selection
- disabled;
- enabled.

### Retention
- evictable;
- pinned_local.

### Runtime residency
- cold;
- warm/decoded;
- active.

### Trust
- metadata_only/untrusted;
- verified_inert;
- trusted_declarative;
- trusted_executable.

Example:
A cinematic may be installed + enabled + evictable + cold + verified_inert.
The active face may be installed + enabled + pinned + warm + verified_inert.

This models reality better than forcing both through one sequential state.

## Storage pools

The architecture should understand storage *roles*, not require a particular physical device.

### Core/system pool — normally SD
Contains:
- Beast/Pwnagotchi runtime;
- database;
- essential recovery;
- fallback Experience/face/fonts/icons;
- active configuration.

Non-evictable by normal cache policy.

### Local content pool — normally SD
User-selected installed optional content.

A one-card device is fully supported.

### Local cache pool — normally SD
Evictable:
- previews;
- downloaded archives;
- catalog thumbnails;
- inactive reacquirable objects;
- temporary staging.

Bounded by policy.

### Optional expansion/library pools
May be:
- larger secondary filesystem;
- USB/SSD;
- NAS/network library;
- desktop/mobile transfer source.

Never required for normal Beastagotchi.

### Remote catalog/source
Metadata and downloadable objects, not runtime storage.

## Active content must survive source loss

If an Experience/face/cinematic is active or explicitly pinned for offline use, required objects must
be staged locally.

Losing:
- Internet;
- NAS;
- phone;
- USB source;

must not break the currently active UI.

External storage is a library/source, not an umbilical cord.

## Storage budget manager

Introduce a storage-policy component that knows:
- actual filesystem free bytes;
- protected system reserve;
- protected owner-data reserve;
- temporary Transaction requirement;
- cache budget;
- installed optional-content budget;
- rollback payload cost.

Before installation, plan must answer:
- download bytes;
- installed delta;
- temporary peak bytes;
- rollback bytes;
- free bytes after operation;
- reserve after operation.

Never use nominal “16 GB / 32 GB” alone.

### First-class small-card profiles

16 GB and 32 GB remain reference qualification targets.

A small card should change:
- cache size;
- how many optional assets are kept locally;
- whether large optional cinematic/HD components are installed;

not whether Beastagotchi is a complete functional system.

## Cache eviction rules

Automatic eviction may remove only reproducible/reacquirable content.

Never auto-evict:
- database;
- captures/handshakes;
- irreplaceable owner data;
- active content;
- pinned offline collection;
- recovery baseline;
- unsynchronized user-created content.

Candidate eviction order:
1. expired temporary staging;
2. stale previews;
3. superseded downloads;
4. cold unpinned cache objects;
5. old optional content explicitly marked evictable.

Doctor/Procedure should explain what can be reclaimed before destructive cleanup.

## Content-addressed implementation note

A possible local object path:

    /var/lib/beastagotchi/content/objects/sha256/<prefix>/<digest>

Manifests/index metadata can live in SQLite or bounded JSON metadata.

Do not prematurely commit to symlink/hardlink implementation:
- hardlinks deduplicate well on one filesystem but not across storage pools;
- symlinks complicate trust/path validation;
- manifest-level object resolution is more portable but requires loader changes.

Prototype/measure before choosing the materialization mechanism.

## Runtime asset budget

Disk size and RAM/render working set are separate budgets.

Current compositor cache is entry-count limited.

Future AssetRuntime should expose:
- decoded bytes;
- object count;
- decode time;
- last use;
- active references;
- cache hits/misses;
- target/device variant.

Governor can reduce:
- warm-neighbor count;
- high-resolution assets;
- ambient layers;
- decoded cache budget;

without uninstalling anything.

---

# Layer 3D — Depot, sources, components and user Collections

## Depot is already correctly separated from trust

Current Depot v1:
- imports bounded metadata;
- supports discovery/search/filtering;
- compares catalog entries to local Packs;
- reports duplicate-ID conflicts;
- grants no trust;
- installs nothing;
- uses GitHub Release metadata only in v1.

This is a very strong starting boundary.

Keep:
> discovery != trust != acquisition != verification != installation != activation.

## Source abstraction

GitHub Releases are an excellent initial source because current code already supports bounded release
metadata and SHA-256 verification.

Do not hard-wire the ecosystem to GitHub forever.

Future SourceAdapter registry may support:
- GitHub Release;
- project-hosted/CDN;
- local file/import;
- local network/library;
- optional mobile/desktop companion transfer;
- other explicitly supported community sources.

Every source still feeds the same verification/intake/content-store contracts.

A source location does not grant executable trust.

## Optional components

Pack manifests should support components/subsets.

Example:

    frostline:
      core_scene          5 MB    required
      reference_tft_art  18 MB    recommended
      faces              12 MB    optional
      audio              40 MB    optional
      genesis_video      85 MB    optional
      studio_hd_art     280 MB    optional
      large_display     160 MB    optional

The installer selects:
- required components;
- target-relevant components;
- owner choices;
- storage fit.

Small Packs can remain indivisible.

Do not force authors to over-componentize trivial content.

## Collections

Introduce a lightweight **Collection** concept for owner-selected sets.

Examples:
- My Daily Beast;
- Camping Set;
- Road Trip;
- Minimal;
- Full Local;
- Diagnostics Kit;
- My Favorite Faces.

A Collection primarily stores references/policy, not duplicate bytes:
- Pack/component ids + versions/hashes;
- Experiences;
- faces;
- audio/cinematic selections;
- optional Apps/Procedures;
- desired enabled state;
- offline/pin policy;
- perhaps presentation preset references.

Actions:
- resolve;
- install missing;
- pin for offline;
- activate selected presentation;
- export manifest;
- clone to another Beast.

### Prepare Device for Offline Use

This Procedure naturally consumes a Collection:
1. resolve dependencies;
2. calculate peak/storage reserve;
3. acquire missing objects;
4. verify;
5. pin required objects;
6. validate active Experience/face/media;
7. run Doctor/storage check;
8. report offline readiness.

## Collection versus Pack

Pack:
- author/distributor's versioned deliverable.

Collection:
- owner's selection of things from potentially many Packs.

Do not require an owner to repack content merely to remember a preferred setup.

A Collection can later be exported as a shareable manifest, and optionally as a self-contained bundle
where licensing permits.

## Collection versus presentation preset

Keep these related but separable.

A presentation preset answers:
- what should the UI look/behave like?

A Collection answers:
- what content/components should this device have/retain?

A named user experience may reference both.

This prevents a 300 MB media bundle from being duplicated every time the owner saves a slightly
different UI arrangement.

## Install/provisioning BOM relationship

A future complete Beastagotchi installer and a Collection can share lower-level reference formats.

A full device BOM may add:
- upstream Pwnagotchi version/hash;
- Beast version;
- OS/package requirements;
- hardware/display profile;
- selected Packs/plugins/components;
- known-good validation.

One resolver/manifest vocabulary is preferable to maintaining unrelated “installer list” and
“content list” formats.

## Community contribution path

Depot/Studio can eventually provide actions such as:
- submit Pack metadata;
- report compatibility result;
- generate sanitized issue;
- export support bundle;
- open upstream/project issue template;
- propose Experience/Scene;
- submit physical-device validation result.

Keep GitHub/project contribution as the canonical public-development highway initially; a native
mobile application is optional convenience, not a foundation requirement.


---

# Layer 3E — Surfaces, overlays, cinematics and lifecycle choreography

## Avoid a registry explosion

The UI currently has several presentation concepts:
- primary Pages;
- App launcher destinations;
- overlays;
- drawers;
- Experience-specific pages;
- Monster reveal;
- Rare Moment overlay;
- notices;
- native Pwnagotchi presentation;
- future Doctor interventions / creation cinematics.

Creating an unrelated registry for every one of these would solve switch statements by replacing them
with registry sprawl.

A cleaner presentation abstraction is **Surface**.

## Surface

A Surface is a user-visible presentation destination/state.

Possible kinds:
- `page` — persistent/swipe/navigation destination;
- `overlay` — modal/detail surface;
- `drawer` — navigation/tool shell;
- `transient` — notice/status;
- `cinematic` — bounded event/lifecycle presentation;
- `workspace` — larger/Studio/external-target surface;
- `native` — upstream/native presentation surface.

A SurfaceSpec may declare:
- id;
- kind/modality;
- label/category;
- semantic navigation group;
- Scene/renderer reference;
- requirements/capabilities;
- Signal dependencies;
- input/dismiss behavior;
- priority/layering;
- Experience variant hooks;
- source;
- target/display support;
- availability state/reason;
- help/Doctor hooks;
- Actions/Procedures exposed.

Then:
- **Page Registry** becomes a filtered view of Surface Registry;
- **App Registry** launches a Surface, Procedure or external workspace;
- **Experience** provides alternate Scene implementations for the same semantic Surface;
- cinematics/reveals use the same layering/input contracts without pretending they are ordinary
  pages.

This is a presentation-layer structure, not necessarily a new Beast Core kernel primitive.

## Primary navigation

Primary carousel remains curated.

A Surface may be:
- primary;
- secondary;
- app-only;
- contextual;
- event-triggered;
- hidden until unlocked.

This permits hundreds of available Surfaces without navigation clutter.

## Availability / Coming Soon

The owner explicitly wants future-facing features to be able to appear honestly before completion.

Surface availability should support:
- `ready`;
- `degraded`;
- `preview`;
- `coming_soon`;
- `unavailable`;
- `hidden`.

A `coming_soon` Surface may show:
- honest label;
- reason;
- prerequisite/progression if relevant;
- optional target release/roadmap wording when known.

It must not expose a control that appears functional but silently does nothing.

Use sparingly: do not fill the device with advertisements for unfinished ideas.

## Choreography

Creation/hatching/assembly, breeding/synthesis, Monster reveals, Rare Moments and some Doctor/
recovery experiences share a common visual need:

> a bounded sequence of Scenes/stages driven by real state/events and optional owner input.

Introduce a declarative **Choreography** contract.

A ChoreographySpec may declare:
- id/version/source;
- trigger Event/condition;
- stages;
- Scene/Surface reference per stage;
- duration or completion condition;
- skippable/non-skippable policy;
- owner interaction points;
- required/optional content;
- resource/thermal class;
- reduced-motion fallback;
- missing-media fallback;
- completion Event;
- witness/acknowledgement behavior;
- rarity/tier variants.

Core owns the truth:
- creature created;
- synthesis completed;
- Monster identity/heritage;
- achievement unlocked;
- Rare Moment exists.

Choreography owns how that truth is presented.

## Content-driven lifecycle examples

No universal egg requirement.

Content may define:

    incubate -> crack -> hatch -> reveal

or:

    parts -> assembly -> boot -> awaken

or:

    excavate -> fracture -> emerge

or:

    pod -> breach -> reveal

or another namespaced lifecycle.

The same engine executes the stages.

## Built-in fallback + optional premium media

Every important lifecycle should have a lightweight built-in/procedural fallback.

Optional Packs may provide:
- richer art;
- sound;
- animation;
- video/cinematic;
- Experience-specific variant.

Therefore a 16 GB device never loses functionality merely because a 200 MB cinematic component is
not installed.

ResourceGovernor may substitute the lightweight fallback when thermal/resource policy requires it
without changing the underlying lifecycle truth.

## Monster reveal

Current `monster_reveal.py` proves the concept but is hard-coded:
- one procedural visual sequence;
- fixed-ish timing based on published state;
- global overlay behavior.

Migrate eventually to Choreography:
- ordinary synthesis reveal;
- first Monstergotchi reveal;
- mutation reveal;
- rare/legendary/mythic variants;
- lineage/Experience-specific content.

This directly supports the owner's desire for bigger/better Monster reveal hoopla without hardcoding
every future reveal into BeastUI.

## Rare Moments

Current RareMomentEngine correctly owns:
- deterministic schedule;
- rarity;
- history;
- active/omen truth.

Current Rare overlay owns presentation.

That separation is good.

### Current cross-layer debt
Rare acknowledgement is currently:
- UI writes `/var/lib/beastagotchi/ui/rare_ack.json`;
- Core Rare engine polls that file.

This is a small functional bridge, but it is hidden coupling.

Replace eventually with a registered low-risk interaction such as:
- `rare.acknowledge` Action;
- or a dedicated UI-input/Event channel;

so witness acknowledgement has:
- canonical actor/time;
- validation against active event;
- Event publication;
- persistence/history;
- no magic shared file.

No full Transaction is needed for a simple acknowledgement.

## Doctor interventions as Surfaces/Choreography

Doctor should be able to request presentation severity without owning pixels directly.

Examples:
- passive health heartbeat Surface;
- advisory transient Surface;
- finding detail Surface;
- critical intervention Surface;
- treatment-progress Choreography;
- recovery-verification Choreography.

Experience determines visual grammar.
Doctor determines semantic health state.
Action/Transaction performs mutation.

## Security of declarative Scene/Surface bindings

A third-party declarative Surface must not gain authority by declaring an action name.

Compiler must validate:
- referenced Action/Procedure is registered;
- operator/risk policy remains owned by ActionBroker;
- Signal privacy is inherited from canonical SignalSpec, not downgraded by Pack metadata;
- resource cost may be declared but can be clamped/reclassified by Beast;
- touch targets obey platform policy.

Third-party presentation requests capability; it does not grant itself capability.


---

# Layer 4A — BeastUI, touch/input and local presentation state

## BeastUI is the largest current presentation composition root

Current `beastui/engine.py` is approximately:
- 2,300 lines;
- 167 KiB source.

It currently owns or directly coordinates:
- theme discovery/options;
- presentation preferences;
- pages/navigation;
- Apps;
- many overlay booleans + offsets/detail state;
- touch/input routing;
- Native Pwnagotchi presentation;
- rare/Monster precedence;
- dashboard boards;
- telemetry/history snapshots;
- notices;
- transitions;
- frame cadence;
- resource/thermal adaptation;
- framebuffer writes;
- runtime performance telemetry.

This works, but it is becoming the primary scaling risk in the UI layer.

The correct goal is not arbitrary file splitting.
The goal is **responsibility extraction behind stable interfaces**.

## Touch acquisition — keep

`TouchInput` is structurally good:
- discovers ADS7846 dynamically;
- reads Linux input directly;
- samples complete SYN frames;
- filters/noise-hardens gestures;
- emits touch-down/drag/up/tap/long-press/swipe;
- writes bounded ephemeral traces under `/run`;
- separates physical calibration from logical UI behavior.

Keep physical-input acquisition separate from UI semantics.

## Input routing — current bottleneck

`BeastUI.on_input()` is a large explicit priority ladder:
- Monster reveal;
- Rare Moment;
- Native mode;
- App launcher;
- Capsule;
- Telemetry;
- Widget inspector;
- Correlation;
- Plugins;
- BeastDex;
- Capture Vault;
- Performance;
- platform overlays;
- Studio overlay;
- themes;
- visualizers;
- achievements;
- help;
- page navigation;
- drawer;
- etc.

This encodes z-order/modal precedence implicitly in code order.

Every new Surface increases the chance that:
- a touch leaks through;
- an overlay wins at the wrong priority;
- close/back behavior differs;
- swipe semantics collide.

### Direction: SurfaceStack + InputRouter

A Surface instance should declare:
- id/kind;
- modality;
- z/priority;
- visible/active state;
- input handler;
- dismiss/back policy;
- bounds/hit regions;
- whether it captures tap/swipe/long-press;
- Scene renderer.

InputRouter:
1. normalizes gesture;
2. walks active SurfaceStack top-down;
3. dispatches to first Surface that accepts it;
4. only reaches primary navigation when no higher Surface consumes it.

Monster/Rare/critical Doctor priority becomes declarative rather than code-order magic.

## NavigationController

Separate:
- primary page index/group transitions;
- App launcher;
- back/close;
- context deck selection;
- Surface deep links.

Primary pages remain swipe-first.
Apps/overlays remain one layer deeper.
The controller consumes SurfaceRegistry rather than hard-coded overlay booleans.

## Overlay state

Current dozens of booleans/offset/detail fields should gradually become per-Surface state objects.

Example:

    SurfaceSession(
      id="capture_vault",
      offset=6,
      selected_id="...",
      opened_from="apps"
    )

This avoids one BeastUI object growing a permanent field for every future feature.

Do not convert all existing overlays at once; migrate opportunistically behind a Surface adapter.

## PresentationPreferenceStore

Current presentation preferences are implemented twice:
- BeastUI directly reads/writes `preferences.json`;
- Beast Studio independently validates, backs up and atomically writes the same file.

This creates schema/default/version drift risk.

Introduce one shared **PresentationPreferenceStore** responsible for:
- schema version;
- defaults;
- validation;
- atomic writes;
- backup/rollback history;
- change fingerprint;
- migration;
- preference-change event/signal.

Consumers:
- BeastUI;
- Beast Studio;
- future CLI/mobile client;
- roster preferred-presentation storage adapter.

BeastUI should consume the store rather than knowing file serialization details.

Studio may still edit preferences directly through this safe non-privileged contract; ordinary visual
preference changes do not need ActionBroker.

## Preference versus system mutation boundary

Presentation preferences include:
- theme;
- face/animation selection;
- renderer choice;
- dashboard layout;
- context decks;
- palette;
- correlation preferences.

These are safe owner presentation state.

Changes that affect:
- services;
- Pwnagotchi config;
- provider activation;
- package/plugin state;
- physical presentation owner;

remain Actions/Transactions.

Make this distinction explicit in code/contracts.

## Small confirmed metadata drift

Beast Studio currently reports schema `version: "0.18.0"` while the active development line is
v0.19.

This is a small bug, but it demonstrates why version/default/schema metadata should come from one
shared contract rather than duplicated literals.

## Render loop — keep the good behavior

Current UI loop already does several things well:
- DataFeed never blocks rendering;
- dirty Event gates rendering;
- adaptive FPS reacts to thermal/CPU/governor state;
- static pages do not redraw merely because FPS budget permits it;
- background layers have independent cadence;
- framebuffer writes use dirty-row spans;
- render/write timing is exposed.

Preserve these behaviors while extracting structure.

## Framebuffer writer — protect

Current `FrameBuffer`:
- RGB565 conversion;
- previous-frame comparison;
- dirty row/span merging;
- full-write threshold;
- write telemetry.

This is a strong physical-target optimization.

Scene dirty bounds should eventually inform compositor work **before** full-image generation, while
Framebuffer row diff remains the final physical safety net.

## DataFeed — migrate transport, preserve threading isolation

Current DataFeed:
- polls `/live` every 0.5 sec;
- batches history every 5 sec;
- avoids one request per graph;
- exposes lock-protected snapshots;
- only dirties UI when state/event sequence changes.

This is already improved over naïve polling.

Future:
- WebSocket initial snapshot + state/event patches;
- sequence-gap/reconnect full resync;
- HTTP batches for history/platform data;
- current polling mode as fallback.

Keep network I/O off the render thread.

## Proposed BeastUI target

    BeastUIShell
      |- RenderRuntime
      |- SurfaceStack
      |- InputRouter
      |- NavigationController
      |- PresentationPreferenceStore client
      |- DataFeed
      |- FrameBuffer
      |- TouchInput
      |- Transient/Notice controller

Feature-specific Surfaces own their own:
- view state;
- input;
- rendering;
- pagination/detail selection.

The shell coordinates; it does not accumulate every feature's fields forever.

