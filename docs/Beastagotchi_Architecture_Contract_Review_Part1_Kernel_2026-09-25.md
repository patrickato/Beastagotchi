# Beastagotchi Architecture Contract Review — Part 1: Stable Kernel

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** current v0.19 source, completed Structure Deep Dive, independent Claude foundation review,
owner foundation/progression/touch guidance.

---

# 1. What "kernel" means here

The Beastagotchi kernel is **not**:
- the Linux kernel;
- a separate microkernel process;
- a security sandbox;
- every important Beastagotchi subsystem;
- every concept that feels foundational.

It is the smallest set of semantic/runtime contracts that nearly every higher layer can rely on
without knowing specific product features.

The kernel should change rarely.

Higher platform layers should be able to grow dramatically without forcing kernel changes.

Working principle:

> **Hard kernel. Wild ecosystem.**

A concept belongs in the kernel only if removing it would force multiple unrelated platform layers to
invent incompatible replacements.

---

# 2. Proposed Kernel v1

## K1 — State

### Contract
One canonical current-truth substrate.

Current implementation:
`StateRegistry`.

Stable semantics:
- canonical key/value state;
- source;
- update timestamp;
- sequence;
- quality;
- error;
- priority/arbitration;
- freshness/staleness;
- thread-safe reads/writes;
- no invented truth.

### Kernel guarantee
Consumers may ask:
- what is the current value?
- who supplied it?
- how fresh/healthy is it?
- what sequence/version is it?

### Not owned by State
State does not decide:
- UI presentation;
- persistence policy;
- progression;
- health interpretation;
- owner action.

**Decision:** sacred kernel concept.

---

## K2 — Signal

### Contract
A typed/semantic description of State.

A SignalSpec describes:
- canonical id/namespace;
- value type/shape;
- unit;
- semantic category;
- privacy/publication policy;
- expected cadence/freshness;
- history policy;
- formatting hints;
- authoritative/fallback provider semantics.

State holds values.
Signal describes meaning.

### Kernel guarantee
Consumers do not need to know which collector/plugin produced a value in order to interpret it.

### Registration
Built-ins register stable SignalSpecs.
Extensions may register namespaced SignalSpecs under policy.

An extension cannot downgrade canonical privacy classification.

**Decision:** stable extensible kernel concept.

---

## K3 — Event

### Contract
A bounded semantic transition/fact.

Event envelope:
- id;
- timestamp;
- type;
- source;
- severity;
- data;
- optional correlation id;
- optional causation id;
- schema/version;
- privacy/publication class.

EventSpec may describe:
- expected fields;
- default severity;
- transient/durable class;
- retention expectations.

### Kernel guarantee
Events represent things that happened, not current truth.

Current truth remains State.

### Delivery
Fast in-memory fanout remains appropriate.
Dropped delivery must be observable.

Durable events may be journaled according to EventSpec/policy.

**Decision:** stable extensible kernel concept.

---

## K4 — Capability

### Contract
A named statement of what can be provided/performed/observed.

CapabilitySpec describes:
- id;
- semantics;
- requirement class;
- compatibility/version;
- privacy/risk where relevant.

Provider registration describes:
- provider id;
- capabilities supplied;
- readiness/health evidence;
- confidence/freshness;
- technical requirements;
- resource class;
- conflict/selection metadata.

### Critical authority rule
Capability resolution/arbitration is read-only.

It may answer:
- what exists?
- what can satisfy this?
- what is blocked?
- what is recommended?

It may **not** silently activate/switch/mutate a provider.

Provider activation belongs to Action/Transaction.

**Decision:** stable extensible kernel concept.

---

## K5 — Action

### Contract
An explicitly registered managed operation.

ActionSpec declares:
- stable id;
- parameter schema;
- plan;
- perform adapter;
- required operator/authority;
- risk class;
- required capabilities;
- owner-override policy;
- privacy/audit policy;
- mutation class:
  - read-only operation;
  - simple mutation;
  - transactional mutation;
- verification requirements.

### Kernel guarantee
Managed mutation occurs through registered Actions rather than arbitrary command execution.

### Critical non-goal
The Action system does not prevent a root owner from manually editing their machine outside Beast.

It governs **managed Beast operations**.

**Decision:** sacred managed-mutation kernel concept.

---

## K6 — Transaction

### Contract
A durable mutation lifecycle for operations that need safety/recovery.

Canonical lifecycle:

    plan
      -> prepare/snapshot
      -> apply
      -> probation/observe
      -> verify
      -> commit
          or
      -> rollback
      -> journal

TransactionSpec declares:
- id/type;
- actor;
- target;
- originating Action;
- plan;
- before state/fingerprint;
- steps;
- verification;
- probation;
- rollback adapter;
- restart/reboot effects;
- required resources/storage;
- outcome.

### Kernel guarantee
Consequential managed mutations can prove:
- what was intended;
- what changed;
- whether it worked;
- how it was rolled back;
- who/what initiated it.

Not every Action requires a Transaction.

**Decision:** missing current implementation, but required kernel concept.

---

## K7 — Module

### Contract
A lifecycle/scheduling declaration around a runtime component.

ModuleSpec describes:
- id/version;
- kind;
- dependencies/order;
- execution mode:
  - periodic;
  - event-driven;
  - signal-driven;
  - on-demand;
  - startup-only;
  - dormant-until-capability;
- cadence;
- resource class;
- governor scaling;
- startup/shutdown/checkpoint;
- health probe;
- failure/backoff policy;
- Signals/Events/Capabilities provided/consumed;
- persistence/backup scope.

### Important restraint
Module is **not** a mandatory inheritance hierarchy.

Existing collectors/engines/functions may be wrapped/registered as modules.

### Kernel guarantee
Core can enumerate, start, stop, throttle, diagnose and attribute runtime work without hardcoding
every subsystem loop.

**Decision:** stable runtime-kernel concept.

---

## K8 — Policy / Authority

### Contract
A generic decision layer that answers whether a managed operation is permitted.

Policy concepts:
- actor/operator identity;
- Managed/Expert/customized state;
- technical blocker versus policy blocker;
- consent requirement;
- local-presence requirement where appropriate;
- owner override availability;
- privilege/risk classification.

### Kernel guarantee
A policy refusal is not represented as technical impossibility.

Owner sovereignty remains explicit.

### ActorRef
Kernel should use a generic actor reference:
- system;
- owner/operator session;
- automation;
- Procedure;
- module;
- remote authenticated client.

This is **not** Beast creature identity.

**Decision:** kernel cross-cutting contract.

---

## K9 — Provenance / Journal reference

### Contract
Every important managed mutation and authoritative derived result can say:
- who/what produced it;
- under which rules/version;
- from which source;
- with which Transaction/Action/Event;
- whether state is managed/verified/customized/restored/imported.

This does not require one giant provenance database.

It requires common identifiers and references that higher layers can persist.

### Examples
- Action audit -> Transaction id;
- Life Ledger entry -> ruleset hash + source Event;
- Pack object -> source/hash/license;
- known-good checkpoint -> originating Transaction;
- owner override -> actor + before/after;
- Doctor finding -> evidence references.

**Decision:** kernel cross-cutting contract.

---

## K10 — Persistence boundary

Persistence is necessary infrastructure but **domain schemas are not kernel semantics**.

Kernel-level persistence contract should provide only common mechanisms:
- schema/version migration;
- transaction-safe repository access;
- append-only journal primitives;
- durable metadata;
- backup/checkpoint hooks;
- concurrency/thread ownership rules.

Current implementation may remain one SQLite database.

Higher layers own their domain repositories/tables.

### Kernel guarantee
Higher layers do not directly invent incompatible migration/concurrency behavior.

### Non-goal
Do not introduce a generic ORM/domain-object framework.

**Decision:** kernel infrastructure contract, not a semantic product object.

---

# 3. Stable platform contracts that are NOT kernel

These are first-class and important, but intentionally one layer above the kernel.

## P1 — Doctor
Consumes:
- State/Signals;
- Events/incidents;
- Module health;
- Capabilities/providers;
- Transaction outcomes;
- known-good/provenance.

Produces:
- findings;
- explanations;
- recommendations;
- Patient Chart;
- links to Actions/Procedures.

Doctor does not need to be a universal kernel dependency.

**Decision:** diagnostics platform layer.

## P2 — Procedure
Orchestrates:
- probes;
- Actions;
- Transactions;
- Doctor interpretation;
- reports/artifacts.

A headless Core could operate without Procedures.

**Decision:** orchestration platform layer.

## P3 — ResourceGovernor
Consumes runtime evidence and emits budgets/policy.

ModuleRuntime enforces those budgets.

The kernel requires resource-class metadata and scheduling hooks, but the current Governor algorithm
may evolve.

**Decision:** core platform service, not semantic kernel concept.

## P4 — Beast Identity / Roster / Lineage
This is central to the product, but it is a Beastagotchi domain model.

Includes:
- Device identity;
- roster;
- active Beast;
- Beast/Monster kind;
- lineage;
- ancestry;
- generation;
- progression/life history.

Kernel needs generic ActorRef/SubjectRef/provenance, not Beast lineage semantics.

Keeping Beast identity above the kernel allows future creature/lifecycle evolution without destabilizing
unrelated platform subsystems.

**Decision:** protected domain-core contract, not lowest kernel.

## P5 — Progression / Life Ledger
Uses:
- Event;
- State;
- persistence;
- provenance;
- identity.

It may be highly stable later, but its economy/rules are explicitly still being tuned.

**Decision:** Beast domain platform.

## P6 — Content Store / Packs / Depot / Collections
Uses:
- persistence;
- transactions;
- capabilities;
- provenance;
- modules where executable extensions exist.

It is ecosystem infrastructure, not required to define State/Action/Event itself.

**Decision:** content platform.

## P7 — Scene / Surface / Experience / Choreography
Presentation contracts:
- Scene;
- Surface;
- Experience;
- Choreography;
- Page/navigation;
- renderer primitives.

These are foundational **presentation platform** concepts.

They should not contaminate headless Core semantics.

**Decision:** presentation platform, not kernel.

## P8 — Provisioner / Recovery Vault / Update adapters
Use:
- Actions;
- Transactions;
- persistence;
- capabilities;
- provenance;
- Doctor.

**Decision:** lifecycle/distribution platform.

---

# 4. Explicitly NOT kernel

Do not freeze these into the kernel:

- Atlas / Forge / Observatory / Habitat / Monolith;
- built-in page names;
- built-in Experience families;
- specific Growth-stage names;
- level thresholds/XP coefficient;
- breeding level;
- rarity vocabulary;
- mutation probabilities;
- Doctor visual language;
- TFT dimensions;
- ADS7846 specifics;
- Jayofelony paths;
- GitHub as a content source;
- Linux package names;
- concrete plugins;
- current UI layouts;
- current database table layout;
- specific Procedure list;
- specific Achievement list;
- specific hardware providers.

These belong in registries, adapters, configuration, content, or domain policy.

---

# 5. Generic references versus domain objects

To keep the kernel reusable without becoming abstract nonsense, standardize a few lightweight refs.

## ActorRef
Who initiated something.

Examples:
- `owner:session-123`
- `system:doctor`
- `automation:update`
- `procedure:prepare-offline`

## SubjectRef
What the operation/evidence concerns.

Examples:
- `device:local`
- `beast:founder`
- `module:gps`
- `provider:gpsd`
- `pack:example.foo`
- `surface:doctor.home`

The kernel does not need to understand every subject type.

## ProvenanceRef
Pointers to:
- Event;
- Action;
- Transaction;
- ruleset;
- source artifact/hash;
- checkpoint.

This gives different domains a shared language for explanation/audit without making one giant base
class.

---

# 6. Registry model

The kernel should expose a small registry substrate rather than one bespoke implementation per domain.

Registry requirements:
- stable namespaced ids;
- duplicate-id rejection unless explicit version/update semantics permit replacement;
- source/provenance;
- schema/version;
- trust/registration tier;
- validation;
- deterministic enumeration;
- immutable registration after runtime start where appropriate;
- Doctor/Studio introspection.

Kernel registries likely include:
- SignalSpec;
- EventSpec;
- CapabilitySpec;
- ProviderSpec;
- ActionSpec;
- ModuleSpec.

Platform registries may use the same registry substrate:
- SurfaceSpec;
- Scene primitive;
- Experience;
- Procedure;
- Progression rule;
- Content source;
- Update adapter.

Do not create a universal dynamically typed "Registry of Everything" API that erases domain-specific
validation.

Share registration mechanics; keep typed contracts.

---

# 7. Versioning rules

Stable ids and schemas need explicit version semantics.

## IDs
Use namespaced stable identifiers where extension pressure exists.

Examples:
- `core.system.temp.cpu_c` or established canonical equivalent;
- `openai.example.action`;
- `pack.author.feature`.

Do not rename ids casually for aesthetics.

## Schema compatibility
Each contract should specify:
- schema version;
- backward-compatible additive changes;
- incompatible-major behavior;
- migration/adapter policy.

## Runtime compatibility
A Module/Pack/Provider may declare:
- Beast contract version range;
- required capabilities;
- optional capabilities;
- platform/upstream compatibility.

Unknown future fields should generally be ignored where safe.

Unknown required semantics should fail honestly rather than be guessed.

---

# 8. Kernel invariants

These should become testable architectural invariants.

1. **One canonical current truth:** StateRegistry.
2. **Unknown stays unknown.**
3. **State != Event.**
4. **Resolution != mutation.**
5. **Policy blocker != technical impossibility.**
6. **Managed mutation goes through Action authority.**
7. **Consequential reversible mutation uses Transaction.**
8. **Modules declare lifecycle/resource behavior rather than hiding permanent work loops.**
9. **No extension grants itself privilege by declaring metadata.**
10. **Privacy classification cannot be downgraded by lower-trust extension data.**
11. **One conceptual runtime owner for one stateful manager.**
12. **Owner root/manual escape remains possible outside the managed contract.**
13. **Customized/manual state is reported honestly rather than hidden.**
14. **Higher layers reference provenance rather than inventing disconnected audit schemes.**
15. **Kernel contracts contain no assumptions about one Experience, screen, lineage or content source.**

---

# 9. Proposed dependency direction

    Linux / upstream adapters
             |
             v
    +-------------------------+
    |   BEAST KERNEL          |
    |                         |
    | State / Signal / Event  |
    | Capability / Provider   |
    | Action / Transaction    |
    | Module lifecycle        |
    | Policy / Provenance     |
    | Persistence mechanisms  |
    +-------------------------+
             |
             v
    +-------------------------+
    | CORE PLATFORM SERVICES  |
    |                         |
    | Doctor / Governor       |
    | Procedures / Incidents  |
    | Provisioning / Recovery |
    +-------------------------+
             |
       +-----+------+
       |            |
       v            v
    Beast Domain   Content/Ecosystem
    Identity       Packs/Store/Depot
    Progression    Collections
    Lineage        Extensions
       |            |
       +-----+------+
             |
             v
    Presentation Platform
    Surface / Scene / Experience
    Choreography / Input / Studio

Dependencies should generally point downward.

Kernel must not import BeastUI, Studio, Progression, Packs or Doctor.

---

# 10. Claude review reconciliation

Claude independently judged:
- StateRegistry should be protected;
- read-broad/act-narrow should remain;
- Transaction is the missing first-class contract;
- Module lifecycle/scheduler is justified;
- registries should replace growing fixed lists;
- extension SDK must not own privileged mutation/privacy/state authority;
- presentation should converge on Scene runtime.

This review agrees with those findings.

One deliberate refinement:
Claude described Signal/Event/Action/Capability/Scene/Experience as the semantic kernel.

This review places **Scene/Experience in the presentation platform instead of the lowest kernel**.

Reason:
- headless Core/Doctor/Provisioner/Recovery/Progression do not require presentation semantics;
- keeping presentation above the kernel reduces coupling;
- Scene/Experience can still be stable first-class contracts.

---

# 11. Open questions before Kernel v1 is frozen

These should be resolved during the next authority/ownership review rather than guessed now:

1. Exact ActorRef/operator-session model.
2. Exact SubjectRef naming/versioning rules.
3. Whether durable Event journaling is automatic per EventSpec or explicitly invoked.
4. Transaction journal storage shape.
5. How lower-trust extensions register Actions without receiving arbitrary execution authority.
6. Whether Module registration is permitted after Core startup.
7. Which registries are built-in-only versus trusted-extension extensible.
8. Exact persistence connection/concurrency contract.
9. How owner/manual overrides are represented in the shared provenance/customization journal.
10. How trusted code extensions receive bounded capability tokens/handles.

