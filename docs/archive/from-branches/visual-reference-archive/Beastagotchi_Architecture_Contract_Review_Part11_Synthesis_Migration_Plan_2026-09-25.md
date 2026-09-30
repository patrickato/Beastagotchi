# Beastagotchi Architecture Contract Review — Part 11: Architecture Synthesis & Migration Plan

**Date:** 2026-09-25  
**Status:** architecture-review synthesis; implementation-order proposal  
**Inputs:** Architecture Contract Review Parts 1-10, completed Structure Deep Dive, current v0.19
source/CI/visual state, independent Claude foundation review, owner implementation-process guidance.

---

# 1. Purpose

Parts 1-10 define a substantially clearer Beastagotchi target architecture.

The purpose of Part 11 is to prevent two opposite failures:

1. **documentation-only architecture** — beautiful contracts that never reach the running Pi;
2. **architecture rewrite fever** — trying to replace the whole working system at once because a
   cleaner target now exists.

The migration principle is:

> **Evolve behind stable contracts. No flag-day rewrite.**

and:

> **Fix correctness first, introduce leverage points second, migrate working domains gradually.**

---

# 2. What the architecture review concluded

Beastagotchi does **not** need a foundational rewrite.

It has a strong existing base:

- canonical StateRegistry;
- truthful unknown/stale/error semantics;
- read-broad/act-narrow authority;
- SQLite persistence;
- Action boundary;
- dependency/capability resolution;
- Resource Governor;
- dirty-row framebuffer output;
- SceneRuntime direction;
- rollback-minded Pack/update/recovery work;
- persistent creature/lineage/progression foundation;
- strong CI/test culture;
- cautious physical presentation ownership.

What it needs is consolidation around first-class contracts:

- typed registries;
- one Transaction Engine;
- ModuleRuntime/Scheduler;
- explicit authority handles;
- shared presentation abstractions;
- Content Store/storage budgets;
- Progression Rule/Life Ledger evolution;
- Provisioner/Recovery orchestration.

These are extensions/consolidations of the current architecture, not replacements for its core philosophy.

---

# 3. Cross-part architecture map

## Kernel

- State;
- Signal;
- Event;
- Capability/Provider;
- Action;
- Transaction;
- Module lifecycle;
- Policy/Authority;
- Provenance;
- persistence mechanisms.

## Core platform services

- ModuleRuntime/Scheduler;
- ResourceGovernor;
- Doctor;
- Incident handling;
- Procedures;
- Transaction Engine;
- Dependency/Capability Resolver;
- provider arbitration;
- Provisioner/Recovery.

## Beast domain

- device identity;
- roster/creature identity;
- Life Ledger;
- XP/Level;
- Life Phase/Growth Form;
- Achievements/Memories;
- lineage/synthesis;
- Rarity/Mastery/Ascension;
- discovery/secret systems.

## Ecosystem/content

- Packs;
- Content Store;
- Depot;
- Collections;
- extension SDK;
- Content Sources;
- compatibility knowledge;
- optional media.

## Presentation

- Surface;
- SurfaceStack;
- Navigation;
- InputRouter;
- Scene;
- Experience;
- Choreography;
- PresentationSession;
- Presentation Broker;
- Studio/mirror clients.

## Lifecycle/distribution

- Device BOM;
- Rebuild Manifest;
- Device Passport;
- Provisioner;
- UpdateAdapters;
- Recovery Vault;
- Known-Good;
- Rescue Plane.

Dependencies generally point downward.

---

# 4. Contracts considered architecturally stable enough to build against

The following concepts are now strong enough to treat as durable design direction.

## Truth

- one canonical current truth;
- unknown stays unknown;
- State != Event;
- provenance matters;
- privacy cannot be silently downgraded.

## Authority

- read broad, act narrow;
- resolution != mutation;
- policy blocker != technical blocker;
- managed mutation goes through Action;
- consequential mutation uses Transaction;
- owner governs the machine.

## Runtime

- recurring work belongs to ModuleRuntime/Scheduler;
- large known ecosystem != large active working set;
- optional/ambient work yields before operational truth;
- static presentation does not redraw without cause.

## Extensibility

- typed registries;
- declarative-first ecosystem;
- executable extension authority is scoped;
- install != activate;
- identity/integrity/compatibility/trust/authority remain distinct.

## Presentation

- Surface owns semantic job;
- Experience owns visual grammar;
- Scene consumes canonical truth;
- physical owner != presentation source != remote viewer;
- primary navigation is curated, not a page ceiling.

## Progression

- one primary Level 1-100;
- orthogonal lifetime dimensions;
- durable lineage/roster;
- versioned/provenanced rules;
- deeper discovery may yield deeper rewards;
- owner-hostile anti-tamper is forbidden.

## Lifecycle

- plan before mutation;
- apply success != verified success;
- restore/update/install are recoverable workflows;
- tested artifact = released artifact;
- rebuildability is first-class.

---

# 5. Concepts intentionally still provisional

Do not freeze these prematurely.

- exact class/module names;
- exact registry API method names;
- exact contract version numbers;
- exact ActorRef syntax;
- exact handle class names;
- exact trust-tier labels;
- exact ResourceGovernor mode names;
- exact display-tier names;
- exact Surface availability vocabulary;
- exact Life Phase names;
- exact rarity vocabulary;
- exact XP coefficient/reward amounts;
- synthesis thresholds/probabilities;
- Ascension requirements;
- exact storage reserve MB/percent;
- exact sandbox/process-isolation mechanism;
- final publisher/signature infrastructure;
- final first-boot UI;
- final public package repository/CDN choices.

Architecture should preserve their semantics while allowing these details to be tuned from evidence.

---

# 6. Immediate correctness block — before architectural expansion

These are not glamorous, but they have disproportionate value.

## C1 — single ownership of stateful domain managers

Inject the Core-owned instances into ActionBroker instead of creating duplicate:

- roster;
- global sync;
- memory engine;
- other stateful managers found during audit.

One conceptual manager -> one runtime owner.

## C2 — SQLite connection/thread ownership

Fix/verify Store connection ownership before expanding worker-thread mutations.

Choose a clear model such as:

- per-thread connections;
- serialized DB worker;
- event-loop-owned writes;
- another measured safe design.

Add explicit tests.

## C3 — bridge event sequence restart handling

Sequence/restart logic must not silently discard valid post-restart events.

## C4 — bridge/runtime file privacy

Review permissions for local state/bridge artifacts.

Private diagnostic/progression/network-related state should not become world-readable accidentally.

## C5 — duplicated schema/preference/version truth

Centralize current duplicated literals/stores where identified:

- PresentationPreferenceStore;
- schema versions;
- project version metadata;
- other duplicated defaults.

These are low-risk, high-confidence fixes.

---

# 7. Keep Gate 1 separate from long-term architecture migration

The current v0.19 visual/physical acceptance gate remains real.

Do not require Parts 1-10 to be fully implemented before v0.19 can ever be promoted.

Likewise, do not use architecture work to quietly declare Gate 1 passed.

v0.19 promotion decision should consider:

- current runtime correctness;
- accepted renderer direction;
- physical TFT/touch/thermal/framebuffer evidence;
- release boundary;
- migration risk.

Long-term architecture implementation continues in bounded follow-on blocks.

---

# 8. Migration strategy

For each current subsystem:

1. define target contract;
2. add adapter around existing implementation;
3. add conformance tests;
4. move one consumer;
5. compare behavior;
6. migrate remaining consumers;
7. remove legacy path only after evidence;
8. preserve rollback or branch checkpoint.

Do not replace working code merely because the new interface exists.

---

# 9. Phase 0 — architecture record and conformance harness

Before large runtime migration:

- preserve Parts 1-11;
- define architecture contract version marker;
- create machine-readable architecture/conformance metadata where useful;
- add tests for key invariants;
- create a migration ledger.

The migration ledger tracks each target contract as:

- current;
- adapter available;
- partially migrated;
- canonical;
- legacy retained;
- legacy removable;
- physically validated.

This prevents ambiguous half-migrations.

---

# 10. Phase 1 — correctness and persistence foundation

Implement C1-C5.

Add:

- ordered SQLite migration ladder;
- WAL checkpoint policy;
- backup-safe DB snapshot API contract;
- provenance ids where missing.

Why first:

Every later subsystem depends on persistence and manager ownership being trustworthy.

---

# 11. Phase 2 — typed registry substrate

Build shared registry mechanics:

- stable namespaced ids;
- source/provenance;
- trust tier;
- schema/version;
- generations;
- deterministic validation;
- atomic candidate activation;
- introspection.

Then implement first typed registries:

1. ActionSpecRegistry;
2. SignalSpecRegistry;
3. EventSpecRegistry;
4. ModuleSpecRegistry;
5. Capability/Provider definitions.

Do not build one generic Registry of Everything.

---

# 12. Phase 3 — Action Registry

Convert twin Action plan/perform dispatch chains to registered Action handlers/specs.

Preserve:

- existing authorization;
- policy blockers;
- technical blockers;
- Expert Mode;
- audit;
- existing action ids.

Benefits:

- removes drift;
- enables Procedure/SDK composition;
- makes mutation inventory inspectable;
- prepares Transaction integration.

This is one of the highest-leverage migrations.

---

# 13. Phase 4 — Transaction Engine and shared journal

Implement:

- TransactionSpec;
- TransactionRun durable journal;
- state machine;
- snapshots;
- probation;
- verification;
- rollback;
- restart recovery;
- subject/resource locking;
- Event publication.

First adapters:

1. current Pack install/update;
2. Restore Transaction;
3. presentation ownership handoff when physical adapter is ready.

Then expand to:

- plugin/provider/config operations;
- platform updates;
- Expert override Transactions.

This becomes the common mutation/recovery substrate.

---

# 14. Phase 5 — customization/provenance journal

Unify owner/manual/Expert override evidence.

Record:

- actor;
- time;
- reason;
- before/after;
- Transaction;
- affected subjects;
- support state.

Feed:

- Doctor drift;
- Device Passport;
- Support Bundle;
- Known-Good comparison;
- Reconcile Device.

Customized state becomes explainable history, not a vague flag.

---

# 15. Phase 6 — ModuleRuntime / Scheduler

Wrap current collectors/engines incrementally.

ModuleSpec declares:

- execution mode;
- cadence;
- dependencies/order;
- resource class;
- health;
- timeout/backoff;
- Signals/Events/Capabilities;
- startup/shutdown.

Scheduler owns recurring wakeups.

ResourceGovernor becomes systemic rather than opt-in.

Do not require every module to inherit one giant base class.

---

# 16. Phase 7 — live transport / performance consolidation

After module/state contracts stabilize:

- WebSocket initial snapshot;
- state/event patches;
- sequence-gap resync;
- HTTP bulk/history fallback;
- bounded subscriber queues;
- drop/lag observability.

Keep current polling as fallback during migration.

Add byte-budgeted caches and preview coalescing.

---

# 17. Phase 8 — presentation structural seam

Do not redesign every pixel.

First introduce structural wrappers:

1. SurfaceSpec/SurfaceRegistry around current pages/Apps/overlays;
2. SurfaceSession/SurfaceStack;
3. InputRouter;
4. NavigationController;
5. shared PresentationPreferenceStore;
6. PresentationSession.

Current renderers continue behind adapters.

This reduces BeastUI composition-root growth without forcing visual regression.

---

# 18. Phase 9 — Scene/Experience convergence

Choose one visually stable Surface/Experience pair.

Migrate it through:

- declarative/compiled Scene;
- SceneRuntime;
- same canonical Signals;
- same pixels or intentionally improved output;
- dirty-region performance evidence.

Only after fidelity is proven:

- migrate more built-ins;
- expand community Experience path.

Do not dogfood a weaker path simply for ideological purity.

---

# 19. Phase 10 — Choreography

Wrap existing:

- Monster reveal;
- Rare Moment presentation;
- Doctor treatment/recovery presentation;

into ChoreographySpec/runtime.

Preserve semantic truth outside presentation.

Add:

- reduced-motion fallback;
- enhancement ladder;
- optional media fallback.

This unlocks Genesis, Ascension and richer lifecycle events later.

---

# 20. Phase 11 — Content Store and storage budgets

Build Content Store index over existing Pack/assets without moving all bytes.

Add:

- five-axis content state;
- storage pools;
- retention classes;
- active-required locality;
- Collections;
- Storage Budget Manager;
- Rebuild references.

Only later add automatic cache eviction.

Do not delete/move existing content until the new index proves trustworthy.

---

# 21. Phase 12 — Extension SDK

Build over registries/Actions/Modules/Content Store.

First public SDK surfaces:

- scoped read Signals;
- namespaced Signal/Event registration;
- declarative Surface/Scene/Experience;
- Procedure composition;
- provider registration;
- extension-private storage.

Then:

- bounded executable Module;
- Action handler registration for trusted extensions;
- Network/Secret/Filesystem handles;
- Grant Receipt;
- permission-diff updates.

Unknown arbitrary community Python stays manual/Expert until real isolation policy exists.

---

# 22. Phase 13 — SDK Reference Extension

**Recommended implementation artifact:** ship a deliberately small reference/conformance extension.

It should demonstrate, without requiring dangerous authority:

- manifest;
- namespace;
- namespaced Signal;
- Event;
- declarative Surface;
- Experience variant;
- Procedure using safe existing probe/action;
- extension-private storage;
- resource declaration;
- compatibility metadata;
- Grant Receipt;
- install/disable/uninstall;
- tests.

This becomes:

- SDK documentation by example;
- CI fixture;
- regression detector;
- community template.

Do not make the reference extension a toy that bypasses real contracts.

---

# 23. Phase 14 — Progression Rule Engine / Life Ledger evolution

Preserve current roster/progression while introducing:

- ProgressionRuleRegistry;
- rule versions;
- Ledger provenance/hash chain;
- rebuildable materialized progression;
- integrity state;
- Doctor explanation.

Then separate:

- Life Phase;
- Growth Form;
- Rank/Title;
- Mastery.

Final economy remains unfrozen until simulation.

---

# 24. Phase 15 — synthesis/lineage extensibility

Introduce:

- MaturityPolicy;
- SynthesisRecipe;
- inheritable heritage schema;
- modifier provenance;
- diminishing combination;
- outcome/rarity + mutation separation.

Current v1 synthesis remains one registered recipe.

Do not alter existing offspring history during migration.

---

# 25. Phase 16 — progression simulator

Before final XP/reward/breeding balance:

- simulate light/typical/active/heavy usage;
- simulate different activity styles;
- estimate L10/L25/L50/L70/L85/L100;
- estimate synthesis timing;
- detect dominant repeatable sources;
- evaluate rare modifier stacking;
- evaluate Pack-rich and Pack-poor users.

Bring final product-facing values to owner for discussion.

This is exactly the class of decision where owner input matters.

---

# 26. Phase 17 — Provisioner/BOM/Passport

Implement:

- Device BOM;
- Rebuild Manifest;
- Device Passport;
- profile planning;
- storage planning;
- component UpdateAdapters.

Wrap current shell installers as Provisioner stages/adapters first.

Do not discard known-safe installer behavior prematurely.

---

# 27. Phase 18 — Recovery Vault / Restore / Rescue Plane

Build:

- Recovery Vault provider registry;
- Restore Transaction;
- Rebuild/Clone paths;
- minimal Rescue Plane CLI;
- Verify My Recovery Procedure;
- Prepare Recovery Kit Procedure.

Physically validate on reference Pi.

Recovery is not complete until it works when UI/normal Core is unavailable.

---

# 28. Phase 19 — reproducible image path

After Provisioner stabilizes:

- reproducible image builder;
- exact upstream artifact acquisition;
- hashes;
- component BOM;
- Beast injection/config;
- first-boot state machine;
- validation;
- release manifest.

Only then consider official prebuilt Beast images where licensing/maintenance permit.

---

# 29. Phase 20 — public ecosystem hardening

Before calling the SDK/public ecosystem stable:

- version public contracts;
- deprecation policy;
- conformance tooling;
- compatibility evidence model;
- permission diff;
- resource lint;
- privacy lint;
- Pack/extension templates;
- contribution docs;
- support expectations;
- signing/provenance where useful.

Do not promise permanent API stability before the migration teaches us what the right API actually is.

---

# 30. Parallel work lanes

Not all work must be serial.

Safe parallel lanes after the core substrate is stable:

## Presentation lane

- Surface/Input/Scene;
- Gate-1 physical acceptance;
- Experience fidelity;
- mirror tooling.

## Doctor/Procedure lane

- probe registry;
- Patient Chart;
- Procedure catalog;
- treatment UX.

## Content/ecosystem lane

- Content Store;
- Depot;
- SDK;
- compatibility knowledge.

## Creature lane

- Ledger/rules;
- lifecycle vocabulary;
- simulator;
- synthesis.

## Lifecycle lane

- Provisioner;
- Backup/Recovery;
- Device Passport.

Cross-lane work merges only through stable shared contracts.

---

# 31. Architecture dependency rule

Before implementing a higher-level feature, ask:

> Does it require a missing lower-level contract that we already know we need?

If yes:
- implement the lower-level seam first when cost is reasonable.

If no:
- do not invent abstraction solely because one might be useful someday.

This prevents both technical debt and speculative overengineering.

---

# 32. Feature completeness as a graph

**Recommended new project quality model:** treat feature completeness as a graph of connected concerns.

A significant feature may connect to:

- Signal/Event truth;
- capability/provider;
- Action/Transaction;
- Doctor;
- Procedure;
- Surface/Experience;
- help/runbook;
- privacy;
- resource budget;
- backup/recovery;
- support bundle;
- update/uninstall;
- progression/memory;
- content/SDK;
- physical validation.

Not every feature needs every edge.

But the graph makes missing expected edges visible.

Example:
a new hardware provider that has no health, Doctor explanation, resource class, dependency metadata or
uninstall path is not fully integrated even if its happy-path collector works.

---

# 33. Cohesion Lint

Build a future automated **Cohesion Lint** over registries/metadata.

Possible checks:

- Signal has privacy/history/freshness;
- Provider has health/requirements;
- Action has plan/risk/verify;
- Transaction has rollback/recovery;
- Module has resource/lifecycle;
- Surface references valid Actions/Signals;
- Pack has provenance/license/size;
- extension has compatibility/authority metadata;
- feature has Doctor/help/runbook where required;
- backup scope exists for irreplaceable state;
- physical target claim has evidence.

This cannot judge whether a product is beautiful or fun.

It can catch architectural orphaning.

---

# 34. Golden Path test

Maintain one end-to-end "Golden Path" scenario through the real contracts.

Candidate flow:

1. canonical Signal appears;
2. Surface displays it;
3. Doctor explains a related benign condition;
4. Procedure proposes a safe Action;
5. Action plan is authorized;
6. Transaction executes/verifies;
7. State/Event updates;
8. Surface reflects result;
9. Transaction/Doctor history records it;
10. support/recovery evidence can explain what happened.

A compact integration test like this protects cross-layer cohesion.

---

# 35. Reference hardware classes

Validation should include more than one synthetic platform profile over time.

At minimum:

- constrained/Zero-2-class;
- reference Pi 4 8 GB + 480x320 ILI9486/XPT2046;
- enhanced/Pi-5-class;
- generic ARM64 Linux SBC;
- larger display class.

The reference Pi 4 remains the primary physical truth target for current development.

---

# 36. Physical-test batching

Respect the owner's development preference:

- build meaningful blocks;
- source-test thoroughly;
- inspect off-screen artifacts;
- bundle physical acceptance work.

Do not require dozens of tiny "run this one command" interruptions when CI/off-screen evidence can cover the work.

Physical tests occur when hardware truth is actually necessary.

When requested, provide:

- exact commands;
- expected result;
- clear evidence capture;
- stopping point.

---

# 37. Owner-input boundary

Continue implementation autonomously for:

- internal refactors;
- registry mechanics;
- tests;
- migrations;
- obvious correctness;
- standard security/privacy;
- helper naming;
- low-level engineering.

Bring owner into:

- major visual/product direction;
- final progression economy;
- synthesis/rarity odds;
- naming/tone of major systems;
- public irreversible contracts;
- owner-facing workflow tradeoffs;
- materially different design forks;
- decisions where engineering does not determine the best product outcome.

Do not let owner input become a bottleneck.

Do not let engineering autonomy erase owner product intent.

---

# 38. Idea-generation rule

Architecture is a foundation, not a creativity ceiling.

Continue proactively asking:

- what existing Linux/Pi tool already solves this?
- what other project has a useful pattern?
- what can be unified across two systems?
- what new capability emerges from data we already collect?
- what can become fun instead of merely technical?
- what can become recoverable/observable instead of fragile?
- what owner workflow are we making unnecessarily hard?
- what would a community developer wish existed?
- what new Beast/Monster behavior becomes possible from current provenance/history/context?

New ideas may revise earlier plans when they produce a better product.

Approved ideas are not silently discarded; they are implemented, planned, experimental, reserved or
explicitly retired with reason.

---

# 39. Do not let architecture become a cage

Warning signs:

- refusing a useful feature because no existing registry type fits;
- forcing every Experience into current DNA vocabulary;
- requiring every community idea to be declarative even when code is genuinely necessary;
- denying owner control to protect support policy;
- preserving a bad abstraction because it was called "kernel";
- optimizing for theoretical elegance over physical Pi behavior;
- rewriting visually successful code before the replacement matches it.

Stable contracts exist to enable change, not forbid it.

---

# 40. Architecture-change process

If implementation proves a contract wrong:

1. document the conflict;
2. determine whether the issue is implementation-specific or architectural;
3. propose revision;
4. assess compatibility impact;
5. update contract/version;
6. migrate deliberately.

Do not quietly violate architecture in code.

Do not preserve wrong architecture merely to avoid editing docs.

---

# 41. Contract maturity labels

Useful labels:

## Proposed
Direction documented; implementation may still teach us.

## Provisional
Implemented in at least one path; compatibility not frozen.

## Stable
Multiple consumers/use cases; tests; deliberate compatibility promise.

## Frozen for major release
Public compatibility commitment; breaking changes require major contract transition.

Most Parts 1-10 are currently **proposed architecture direction**, with several concepts already
implemented/provisional in v0.19.

Do not mislabel them as final public SDK promises yet.

---

# 42. Versioning the architecture

Introduce an architecture/contract bundle version when runtime migration begins.

This version identifies compatible combinations of:

- kernel contracts;
- registry schemas;
- SDK;
- Surface/Scene;
- Progression rules;
- BOM/manifests.

It is separate from marketing/product release number.

Exact scheme remains provisional.

---

# 43. Release boundaries

A release may ship while later architecture phases remain incomplete if:

- shipped behavior is honest;
- migration compatibility is preserved;
- unfinished features are not falsely presented;
- safety/recovery expectations are met;
- documented blockers are not release-critical.

Do not make "complete entire roadmap" the prerequisite for every release.

---

# 44. Branch strategy

Protect stable main.

Use bounded feature/migration branches with:

- one coherent architectural block;
- tests;
- docs;
- CI;
- evidence.

Large cross-cutting migrations may use a dedicated integration branch before entering the active release branch.

Keep collaborator-owned branches/areas separate until reviewed.

---

# 45. Evidence hierarchy

When evidence conflicts, prefer:

1. physical measured target behavior;
2. current source/runtime behavior;
3. automated tests/CI artifacts;
4. current authoritative architecture docs;
5. historical docs/checkpoints;
6. assumptions/mockups.

A screenshot concept does not overrule a real renderer.

An old checkpoint does not overrule current source.

A green test does not overrule failed physical touch behavior.

---

# 46. Definition of architectural progress

Do not measure progress only by number of docs or lines changed.

Useful measures:

- duplicate ownership removed;
- hard-coded switch lists replaced where extension pressure exists;
- mutations recoverable;
- modules observable/resource-controlled;
- Surfaces isolated;
- active working set smaller;
- state truth cleaner;
- compatibility explainable;
- restore actually works;
- SDK extension possible without Core edits;
- progression reconstructable;
- physical UI better;
- owner workflow simpler.

---

# 47. First implementation tranche after architecture review

Recommended first runtime tranche:

## A. Correctness
- shared manager injection;
- SQLite/thread safety;
- bridge sequence restart;
- local state permissions;
- preference/version source cleanup.

## B. Registry foundation
- typed Registry substrate;
- ActionSpecRegistry;
- SignalSpec/EventSpec skeleton.

## C. Transaction foundation
- Transaction journal/state machine;
- adapt Pack install/update.

## D. Tests/docs
- architecture invariant tests;
- migration ledger;
- one Golden Path integration test.

This tranche creates the foundation for almost everything else without touching the physical UI architecture deeply.

---

# 48. Second implementation tranche

After A-D are green:

- ModuleRuntime/Scheduler;
- ResourceGovernor integration;
- provider/collector wrapping;
- WebSocket patches;
- performance observability.

This improves efficiency and runtime control before the ecosystem expands further.

---

# 49. Third implementation tranche

Then:

- SurfaceRegistry;
- SurfaceStack;
- InputRouter;
- NavigationController;
- PresentationPreferenceStore;
- PresentationSession.

This attacks BeastUI scaling while preserving current renderers.

---

# 50. Fourth implementation tranche

Then parallelize:

- Scene/Experience compiled proof;
- Content Store;
- Extension SDK declarative path;
- Progression Rule/Ledger evolution;
- Provisioner/BOM foundation.

At that point the architecture becomes a platform rather than a collection of good subsystem designs.

---

# 51. What not to do next

Do not:

- rewrite all BeastCore modules;
- rewrite all UI renderers;
- migrate every Pack format at once;
- build a heavyweight plugin sandbox before one is needed;
- finalize XP numbers without simulation;
- enable automatic provider failover;
- enable physical Presentation Broker execution before real rollback evidence;
- bulk-install the entire known software universe;
- require NAS/USB/cloud;
- merge every experimental branch into stable main;
- spend weeks polishing architecture names while known correctness issues remain.

---

# 52. Architecture synthesis invariants

1. Current strong foundations are preserved.
2. Correctness precedes abstraction expansion.
3. Migration is adapter-first and incremental.
4. No flag-day rewrite.
5. Long-term architecture does not falsely block v0.19 release.
6. Gate-1 visual/physical acceptance remains separate truth.
7. Public compatibility is not frozen before implementation evidence.
8. Every consequential mutation converges on Transaction.
9. Every recurring workload converges on ModuleRuntime.
10. Every extensible domain converges on typed registries where growth justifies it.
11. UI semantic logic converges on Surface; visual grammar on Experience/Scene.
12. Large ecosystem remains a small active working set.
13. Progression remains reconstructable/provenanced and owner-respectful.
14. Provision/recovery becomes reproducible, not shell folklore.
15. Owner sovereignty survives every managed abstraction.
16. Physical Pi evidence outranks architectural elegance.
17. Features should become cohesive across expected system edges.
18. New ideas remain welcome even after contracts exist.
19. Architecture changes when evidence proves it should.
20. Work proceeds in meaningful test-backed blocks with selective owner consultation.

---

# 53. Part 11 conclusion

The architecture review is complete enough to stop expanding contracts for their own sake.

The project now has a coherent answer to:

- what truth is;
- who owns it;
- how mutation happens;
- how work runs;
- how extensions enter;
- how content is stored;
- how Beasts progress;
- how presentation composes;
- how installs/updates/recovery work;
- how the owner retains sovereignty.

The next useful step is **implementation**, beginning with the first tranche:

1. stateful-manager ownership correction;
2. SQLite/thread ownership;
3. bridge sequence/privacy fixes;
4. preference/version source cleanup;
5. typed registry substrate;
6. Action Registry;
7. Transaction Engine/journal;
8. adapt existing Pack transaction path;
9. architecture invariant tests and migration ledger.

This is intentionally not the most visually exciting block.

It is the block that makes the next several years of visually exciting work safer, faster and easier.
