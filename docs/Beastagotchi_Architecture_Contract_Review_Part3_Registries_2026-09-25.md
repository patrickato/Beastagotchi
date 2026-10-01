# Beastagotchi Architecture Contract Review — Part 3: Registry Contracts

**Date:** 2026-09-25  
**Status:** proposed architecture contract  
**Depends on:** Part 1 Kernel, Part 2 Authority/Ownership

---

# 1. Why registries exist

Registries prevent Beastagotchi from turning every extensible concept into:
- a hard-coded tuple;
- an `if/elif` ladder;
- a central switch statement;
- a merge-conflict hotspot.

They also provide:
- validation;
- namespacing;
- trust/provenance;
- deterministic discovery;
- introspection;
- compatibility/version checks.

A registry is not merely a Python dictionary.

---

# 2. Typed registries, not one Registry of Everything

Share registration mechanics, but keep domain-specific types.

Good:

    SignalSpecRegistry
    EventSpecRegistry
    CapabilitySpecRegistry
    ProviderSpecRegistry
    ActionSpecRegistry
    ModuleSpecRegistry

Platform registries:

    SurfaceSpecRegistry
    ExperienceRegistry
    ScenePrimitiveRegistry
    ProcedureSpecRegistry
    ProgressionRuleRegistry
    ContentSourceRegistry
    UpdateAdapterRegistry

Do **not** replace these with one generic dynamically typed bag.

Each registry must enforce its own semantic rules.

---

# 3. Common registration metadata

Every registrable definition should carry or be wrapped with common metadata:

- stable id;
- schema version;
- definition version;
- source/provenance;
- namespace owner;
- trust tier;
- compatibility constraints;
- registration generation;
- optional deprecation/supersession metadata.

Optional:
- labels/descriptions;
- resource class;
- feature flags.

The common metadata does not erase domain-specific fields.

---

# 4. Namespacing

## Reserved namespaces

Core/project-controlled namespaces are reserved.

Examples:
- `core.*`;
- `beast.*`;
- canonical established Signal namespaces such as `system.*`, `gps.*`, `wifi.*`, etc.

Third-party content cannot shadow or replace these merely by declaring the same id.

## Extension namespaces

Third-party ids must derive from a stable extension/Pack namespace.

Examples:

    acme.weather.surface
    jane42.biomech.experience
    pack.author.plugin.action

Exact public naming convention may be finalized later.

Requirements:
- lowercase canonical form;
- bounded length;
- stable once published;
- no visual-confusable alias trickery;
- registry knows the owning source.

---

# 5. Duplicate and replacement rules

Default:
> duplicate id = registration error.

A definition cannot silently shadow another.

Replacement is allowed only when:
- same namespace/source authority;
- explicit upgrade/update semantics;
- compatibility validation succeeds;
- activation uses a Transaction;
- rollback can restore the previous registry generation.

Core ids cannot be replaced by lower-trust sources.

---

# 6. Registry generations

Definitions should be immutable within one active generation.

Dynamic extension install/activation should not mutate live registries piecemeal.

Preferred lifecycle:

    active Generation N
          |
    stage candidate definitions
          |
    validate local schemas
          |
    resolve cross-registry references
          |
    apply trust/policy rules
          |
    calculate dependency graph
          |
    reject conflicts/cycles
          |
    build Generation N+1
          |
    atomic commit/swap
          |
    publish registry.changed
          |
    consumers resync

If any step fails:
- Generation N remains active;
- staged definitions remain inert;
- Doctor/Studio can explain why activation failed.

Rollback:
- restore Generation N metadata/definitions;
- undo associated executable activation via Transaction if necessary.

This gives runtime stability while preserving extensibility.

---

# 7. Registration phases

Suggested phases:

## Bootstrap
Core/built-in registrations.

## Trusted discovery
Project/trusted installed executable integrations.

## Declarative discovery
Installed inert/declarative Packs.

## Validate/finalize
Cross-reference and policy validation.

## Runtime
Registries are read-mostly immutable snapshots.

## Transactional reload
A Pack/plugin activation may create a new generation.

Do not allow arbitrary registry mutation from random runtime callbacks.

---

# 8. Trust tiers

Registry mechanics must distinguish source trust.

Working conceptual tiers:

## Core
Shipped with Beastagotchi.

May register all supported contract classes.

## Project/trusted executable
Explicitly trusted code integration.

May register executable handlers/modules/primitives within granted authority.

## Verified declarative
Schema-validated inert Pack content.

May register declarative specs allowed by its type.

## Catalog-only/uninstalled
Metadata visible for discovery.

May not enter active runtime registries.

The exact signature/source-trust technology can evolve.
Do not equate "came from GitHub" with trusted.

---

# 9. Introspection contract

Every registry should support bounded read-only introspection for:
- Doctor;
- Studio;
- support bundle;
- `beastctl`;
- tests.

Common outputs:
- active generation;
- count;
- registered ids;
- source;
- version;
- trust tier;
- compatibility;
- validation state;
- disabled/deprecated state;
- dependency/reference status.

Registry introspection must not expose secrets.

---

# 10. Determinism

Registry results should be deterministic.

Do not let:
- filesystem enumeration order;
- import order;
- race timing;

change semantic resolution.

Prefer:
- sort by canonical id;
- explicit declared priority where needed;
- deterministic tie rules;
- hard error on unresolved ambiguous ties for authority-sensitive cases.

---

# 11. Cross-registry references

Definitions may reference other registries.

Examples:
- Surface references Scene + Actions;
- Procedure references Actions;
- Provider references Capabilities;
- Module declares Signals/Events/Capabilities;
- Progression Rule references Events + Unlocks + Choreography.

Activation must validate all required references before commit.

Unknown optional reference:
- may degrade/fallback according to contract.

Unknown required reference:
- blocks activation honestly.

---

# 12. Dependency/cycle rules

Registries that allow dependency graphs must detect cycles before commit.

Examples:
- Module A Requires Module B while B Requires A;
- Procedure A invokes B and B invokes A without bounded recursion;
- content component circular requirements.

Do not discover fatal cycles after runtime start.

---

# 13. Core kernel registries

## SignalSpecRegistry

Extension permissions:
- core defines canonical Signals;
- declarative/trusted extension may add namespaced Signals;
- canonical privacy cannot be downgraded;
- source priority/authority is assigned by registration policy, not extension input alone.

Must expose:
- type/structure;
- unit;
- privacy/publication;
- history;
- freshness expectations;
- authority/provider semantics.

---

## EventSpecRegistry

Extensions may add namespaced event types.

EventSpec declares:
- schema;
- default severity;
- durability/retention class;
- privacy/publication;
- expected fields.

Core can reserve canonical event families.

Unknown event type in strict managed runtime should be observable as:
- unregistered;
- not silently accepted as equivalent to a known semantic event.

Development mode may permit diagnostics for unregistered events.

---

## CapabilitySpecRegistry

Capabilities describe semantics, not implementations.

Extensions may:
- register namespaced Capabilities;
- reference existing public Capabilities.

Core may reserve critical canonical capabilities.

CapabilitySpec does not activate anything.

---

## ProviderSpecRegistry

Providers:
- declare capabilities provided;
- health/readiness evidence;
- dependencies;
- resource class;
- conflicts;
- adapter reference where trusted.

Declarative providers may describe already-existing external capability evidence.

Executable activation adapters require trusted executable authority.

Provider registration never performs activation.

---

## ActionSpecRegistry

Core principle:
> registering an Action is not enough to gain privileged execution.

### Declarative content
May normally:
- reference/request existing Actions;
- define parameter presets/workflows through Procedures.

It may **not** inject arbitrary executable Action handlers.

### Trusted executable extension
May register an Action handler if:
- source trust permits;
- required authority handles are granted;
- risk/consent class is declared;
- plan + perform + verify contract validates.

Core-reserved Actions cannot be shadowed.

---

## ModuleSpecRegistry

Only executable/trusted runtime code can register actual Modules.

Declarative content may influence configuration/enablement but cannot invent executable loops.

ModuleSpec must declare:
- lifecycle;
- execution mode;
- dependencies;
- resource class;
- health;
- outputs/inputs.

Modules are finalized before scheduling in one registry generation.

---

# 14. Platform registries

## SurfaceSpecRegistry

Declarative Pack-friendly.

May register:
- page;
- overlay;
- drawer;
- transient;
- cinematic;
- workspace.

Surface may reference:
- Scene;
- Actions;
- Procedure;
- Signals;
- Capabilities.

A Surface reference does not grant Action authority.

---

## ExperienceRegistry

Declarative by default.

Experience declares:
- DNA;
- Surface/Scene variants;
- asset/content references;
- capability requirements;
- fallbacks.

Built-ins should eventually use the same registry path.

---

## ScenePrimitiveRegistry

Existing safe primitives/components are broadly usable by declarative Scenes.

A **new executable primitive** requires trusted code registration.

This is the escape hatch for genuinely new visual grammar without making all Experiences executable.

---

## ProcedureSpecRegistry

Declarative Procedures may register if all steps are composed from:
- registered probes;
- registered Actions;
- registered Transactions/Procedure-safe substeps.

A Procedure cannot elevate its own consent/risk authority.

The effective Procedure risk is at least the maximum risk of its steps.

Recursive/cyclic invocation must be rejected or explicitly bounded.

---

## ProgressionRuleRegistry

Built-in/project rules may contribute normal canonical XP.

Community declarative rules:
- may define namespaced/local achievements/unlocks;
- global canonical XP contribution is policy-controlled;
- cannot declare unbounded repeatable XP.

Rule validation includes:
- source Event/metric;
- caps/cooldowns;
- provenance;
- scope;
- reward bounds.

Life Ledger records the exact rule id/version used.

---

## ContentSourceRegistry

A Content Source Adapter knows how to acquire bytes/metadata from one source class.

Examples:
- GitHub Release;
- local file;
- network library;
- future CDN.

New executable source adapters require trusted code.

Catalog metadata cannot install itself.

---

## UpdateAdapterRegistry

High-trust only.

Component-specific adapters:
- Beast Pack;
- Beast Core;
- UI/Studio;
- Theme Manager;
- Pwnagotchi platform;
- plugins.

Update adapters perform consequential mutation through Transaction.

No declarative Pack can register an arbitrary update executor.

---

# 15. Availability, installation, registration and activation are different

Do not collapse these states.

A definition can be:

- known in catalog;
- downloaded/cached;
- installed;
- eligible to register;
- registered in candidate generation;
- active in current registry generation;
- selected/enabled;
- actually running/in-use.

Examples:
- an Experience may be installed and registered but not active;
- a Module may be registered but dormant;
- an Action may be registered but unavailable because Capabilities are missing;
- a Provider may be registered but unselected;
- a Pack may be installed yet none of its executable content activated.

---

# 16. Registry hot reload policy

Not all registries need the same hot-reload behavior.

## Safe to generation-reload live
Potentially:
- Surface;
- Experience;
- declarative Scene;
- Procedure;
- namespaced Signal/Event metadata;
- inert content definitions.

Subject to consumer resync.

## Prefer restart/controlled activation
Likely:
- executable Module;
- executable Action handler;
- new Scene primitive;
- Update adapter;
- low-level hardware/provider adapter.

These can still use registry generations, but activation may require a controlled service restart or
Transaction.

Do not promise universal hot reload.

---

# 17. Registry persistence

The active registry is primarily reconstructed from:
- built-in definitions;
- installed Pack manifests;
- trusted extensions;
- owner enablement/preferences.

Persist:
- installed source/version;
- active generation metadata;
- activation decisions;
- validation outcomes;
- owner selection;
- provenance.

Do not serialize arbitrary Python handler objects into SQLite.

Rebuild deterministic registries on startup.

---

# 18. Doctor integration

Doctor should see registry health generically.

Examples:
- unresolved reference;
- duplicate id;
- incompatible schema;
- disabled dependency;
- failed executable registration;
- stale provider;
- Pack definition rejected.

Doctor reports:
- affected component;
- reason;
- source;
- remediation;
- whether rollback/disable is available.

Doctor does not silently "fix" registry conflicts outside Action/Transaction policy.

---

# 19. Studio integration

Studio should consume registry introspection to build UI dynamically.

Examples:
- Apps/Surfaces list;
- Experiences;
- Procedures;
- providers;
- Actions available to current operator;
- content components;
- progression catalog.

This eliminates duplicated hard-coded browser lists.

Studio cannot mutate a registry directly.
It requests Pack/extension activation/deactivation through managed Actions/Transactions.

---

# 20. Registry migration path from v0.19

Incremental, not flag-day.

Recommended order:

1. Build typed registry substrate/generation mechanics.
2. Convert Action dispatch to ActionSpecRegistry.
3. Convert Signal metadata to SignalSpecRegistry.
4. Add EventSpecRegistry.
5. Add ModuleSpecRegistry around existing collectors/loops.
6. Convert Provider/Capability fixed knowledge.
7. Introduce SurfaceSpecRegistry and adapt current Pages/overlays.
8. Move Apps to launcher views over Surface/Procedure registries.
9. Move declarative Progression/Procedure definitions later.
10. Convert built-in Experiences progressively after visual fidelity is preserved.

Existing working code may register adapters around current implementations during migration.

---

# 21. Registry invariants

1. Duplicate active id is never silently resolved by import order.
2. Lower-trust source cannot replace higher-trust definition.
3. Core-reserved ids cannot be shadowed.
4. Definitions are immutable within one active generation.
5. Registry generation changes are atomic.
6. Failed candidate activation leaves prior generation valid.
7. Required cross-references resolve before commit.
8. Cycles are detected before activation where relevant.
9. Registry definitions do not confer authority beyond their trust/policy.
10. Registration order does not alter semantic outcome.
11. Studio/Doctor can inspect source/version/validation.
12. Runtime registries reconstruct deterministically after reboot.
13. Executable registration is stricter than declarative registration.
14. Pack installation does not imply registry activation.
15. Registry changes that affect executable authority use Actions/Transactions.

