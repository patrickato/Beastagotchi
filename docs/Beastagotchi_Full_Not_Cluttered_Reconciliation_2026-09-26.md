# Beastagotchi — “Full but Not Cluttered” Reconciliation

**Date:** 2026-09-26  
**Status:** pre-fresh-eyes reconciliation checkpoint; product/architecture cleanup after facets, Toolbelt, Claude review, and Sandbox discussion

## Purpose

This pass checks recent Beastagotchi ideation against three owner goals:

1. **make Beastagotchi the best it can reasonably be;**
2. **“think of everything” without leaving obvious capability gaps;**
3. **make it full, but not cluttered.**

This is not a new brainstorming pass. It consolidates what already exists so later implementation does not multiply systems merely because brainstorming used several names for related ideas.

---

## Primary anti-clutter rule

> **A concept earns its own top-level product identity only when it serves a distinct user job. Otherwise it should become a view, Instrument, Tool, Procedure, diagnostic condition pack, Workspace component, Surface, or query over an existing system.**

Related rules:

- one canonical truth source per concept;
- one capability may appear through many presentations/workflows;
- internal architecture names do not automatically become menu items;
- broad capability universe does not imply broad primary navigation;
- progressive disclosure is preferred over removing capability;
- normal/default UX is curated; Expert/Owner paths remain available;
- absent hardware/capability is explicit, never faked;
- context and Universal Search should surface uncommon capability without crowding primary UI.

---

# 1. Systems that should remain singular

## Doctor

There is **one Doctor**.

Display, monitor-mode, storage, power, service, Pack, provider, progression, and other diagnostics are modular knowledge/condition domains consumed by the same Doctor.

Do not create separate “TFT Doctor,” “Radio Doctor,” “Storage Doctor,” etc.

## System Graph

There is one underlying graph of relevant hardware/software/capability/resource relationships.

The following are views/queries over that graph rather than separate systems:

- Machine Map;
- Capability Graph;
- Pipeline Inspector;
- Resource/Device Claim Map;
- dependency view;
- provider-path view;
- fault-path highlighting.

The graph should consume canonical inventory/capability/provider/runtime truth rather than establish a second truth store.

## Action / Transaction / Procedure execution

Do not create feature-specific mutation engines.

- **Action** = bounded managed operation;
- **Transaction** = consequential mutation with durable plan/apply/verify/rollback/journal semantics;
- **Procedure** = multi-step goal/workflow composed from probes, Actions, Transactions, waits, Doctor interpretation, etc.

Update, Pack, restore, owner override, provider handoff, recovery, and future workflows should converge on these shared contracts where appropriate.

## Capability / Provider lifecycle

External hardware/software/integrations should reuse one general lifecycle:

**Discovery -> Capability -> Health -> Usage**

Discovery Inbox, Sensor Onboarding, provider health, Hardware Bench, Device Passport, Doctor, Owner Space, and future BenchLink should reuse these contracts rather than each inventing discovery/health logic.

## Presentation platform

Surface / Scene / Experience / Choreography / PresentationSession / Presentation Broker remain the shared presentation model.

Do not create feature-specific rendering stacks merely because a Workspace or lifecycle moment looks different.

## Content/storage model

Packs, Content Store, Collections, storage pools/budgets, Depot/catalog, optional assets, Recovery Vault content, and Capability Archive should share storage/content truths where their semantics overlap.

No feature should create a parallel library/database merely for presentation convenience.

## Owner customization boundary

Owner Space, Expert Mode, customized state, unmanaged extensions, support status, “What Changed?”, and recovery reasoning should converge on one customization/provenance history rather than separate flags and logs.

---

# 2. Named ideas that should NOT become separate apps/systems

## Power Detective

Keep the idea, but treat it as an analysis/correlation capability within Steward/System Health plus Doctor evidence and relevant Instruments.

It does not need its own application family.

## Monitor-mode and TFT diagnostics

Keep the diagnostic depth, but implement as Doctor condition knowledge + probes + Procedures.

## “What Changed?”

Keep as a high-value owner-facing capability, but it should query shared Transaction history, customization ledger, snapshots/fingerprints, package/service/config history, and Device Passport changes.

Do not build a special “What Changed database.”

## Device Passport

Device Passport is a durable report/snapshot/view over canonical identity, inventory, capability, provenance, versions, and known-good state.

It should not maintain an independent competing hardware inventory.

## Discovery Inbox

Discovery Inbox is an owner-facing intake Surface over the shared discovery/provider lifecycle.

It is not a second discovery engine.

## Capability Archive

Capability Archive should be primarily a view/index over canonical durable artifacts/history/content such as snapshots, Bench sessions, device profiles, saved Procedures, field records, Capsules, and owner-created tools.

Do not create another general-purpose storage subsystem for it.

## Recipes / Blueprints

Recipes are declarative reusable compositions of existing Instruments, Tools, Procedures, conditions, defaults, Workspaces, and/or Choreography.

They must not become a second automation or Procedure engine.

## Transaction Inspector / Procedure Tracer

These are views over shared execution history, primarily useful in Steward and Developer/Expert contexts.

## Field RF Journal

This is an Explore/History interpretation of privacy-curated canonical RF/environment observations, not a separate capture engine.

## Hardware-expanded Beast senses/expression

This is a consequence of capabilities/providers becoming available, not a separate creature subsystem.

Real capability may enable new Companion/Explore/Presentation behavior; absent capability remains absent.

---

# 3. Workspace consolidation

Workspaces should be broad coherent working environments, not dozens of mini-apps.

## Radio Workspace

May contain channel coverage, regulatory/interface views, Bettercap/Pwnagotchi health, epochs, timelines, relevant Tools/Procedures, Field RF context, and Doctor findings.

## Storage Workspace

May contain devices, filesystems, mounts, health, capacity, errors, performance, roles, Recovery Vault/content relationships, and relevant Procedures.

## Hardware Bench

May contain USB, GPIO, I2C, SPI, serial, sensors, claims/conflicts, peripheral qualification, Bench Logger, and related Procedures.

## Steward/System Health surface

Doctor, “What Changed?”, Device Passport, Transactions/Procedures history, known-good/recovery, power/thermal/resource incidents, support bundles, drift/customization, and system status should feel like one care/stewardship area even though their underlying services remain modular.

Do not necessarily create a monolithic “System Health engine”; this is a product/presentation grouping over shared services.

---

# 4. Facets remain semantic, not navigation cages

Current useful product facets remain:

1. Companion / Life
2. Instrument / Observe
3. Operate / Toolbelt
4. Explore / Field
5. Create / Workshop
6. Connect / Exchange
7. Steward / Care

These are lenses for judging product balance and user purpose. They should **not** be hardcoded as seven mandatory top-level tabs.

A Surface or Workspace may legitimately serve several facets.

Examples:

- Radio Workspace spans Observe + Operate + Explore + Steward;
- Hardware Bench spans Operate + Create + Observe;
- Doctor primarily serves Steward but appears contextually everywhere;
- Field RF Journal spans Explore + Companion + Observe;
- Sensor capability may feed Observe + Companion + Explore.

This overlap is desirable when it reuses one capability rather than duplicating it.

---

# 5. Cross-cutting concepts that need a home but should not become facets

## Universal Search

Keep as a cross-cutting discovery/navigation mechanism for a very large capability/content universe.

Search should find Workspaces, Tools, Procedures, settings, Packs, Doctor knowledge/results, historical artifacts, owner extensions, capabilities, and help where appropriate.

It is not an eighth facet.

## Automation

Automation is primarily an invocation/scheduling mode over Actions/Procedures/recipes and event/condition triggers.

Do not build an unrelated second execution model.

## Support Bundle

Support export belongs to Steward/Doctor/recovery workflows and should consume provider diagnostic contracts, Device Passport, Doctor evidence, versions, selected logs, and privacy policy.

It is not a standalone product pillar.

## History / Journal

Durable history is shared infrastructure consumed by many facets, not its own product side.

---

# 6. Sandbox implications that architecture should anticipate now

The selected Beast Sandbox direction reinforces rather than complicates the production architecture.

## Virtual providers

Virtual radio/display/touch/power/storage/GPIO/sensor/etc. implementations should use the **same provider/capability contracts** as physical providers wherever practical.

Simulation provenance must remain explicit.

Do not create a parallel “test-only Beast truth model.”

## Record/replay

Incident capture/replay should serialize/reconstruct canonical Signals, Events, capability changes, transaction/history context, and selected diagnostic evidence using stable schemas.

This should become a conformance/regression asset, not merely a debug log dump.

## SSH-connected physical validation

Remote Pi probes/validation should reuse Doctor/probe/Procedure contracts where possible.

Do not create a giant unrestricted remote-shell control layer as the managed Sandbox interface.

## Docker

Disposable test cells are implementation/testing infrastructure. Docker should remain hidden behind understandable Beast Sandbox operations where practical.

## QEMU

Not required. Do not reintroduce by default.

---

# 7. Claude review reconciliation

Claude's strongest recommendations and the current architecture are converging rather than competing.

- shared stateful manager ownership -> implemented/accepted correctness rule;
- Action registry -> current typed/registered Action migration;
- shared Transaction contract/journal -> implemented foundation and expanded into “What Changed?”/recovery history;
- scheduler/governor -> remains planned ModuleRuntime work;
- presentation convergence -> preserved, with **data-first but code-extensible** rather than pure-data absolutism;
- DB hardening -> partially addressed, ordered migrations/checkpoint policy remain future work;
- customization/override ledger -> elevated in importance and tied to Owner Space/Doctor/recovery;
- capability graph -> expanded into the shared System Graph concept;
- lifecycle choreography -> preserved as content-driven presentation over durable Core identity/lineage;
- beastctl/shared surfaces -> retained as a likely future interface over the same Actions/Procedures rather than another behavior implementation.

No current Claude recommendation requires a competing subsystem.

---

# 8. Deliberate deferrals

Strong ideas that architecture should permit now but implementation should not rush:

- BenchLink protocol;
- broad Sensor Onboarding catalog;
- hardware-expanded creature senses beyond the provider contracts required to support them;
- large community Recipe/Blueprint ecosystem;
- advanced Capability Archive UX;
- automated SSH synchronization/control beyond bounded validated operations;
- exhaustive hardware-specific diagnostics;
- public SDK breadth beyond proven stable contracts.

Deferral means **preserve the seam**, not forget the idea.

---

# 9. “Full but not cluttered” feature test

Before promoting a future idea into a new visible product concept, ask:

1. **Does it serve a unique user job?**
2. **Can it reuse existing canonical State/Signals/Events/Capabilities/Actions/Transactions/Procedures?**
3. **Would making it separate create parallel truth, history, mutation, diagnosis, or storage?** If yes, merge it.
4. **Can it live contextually inside an existing Workspace or Surface?** If yes, prefer that.
5. **Is it frequent/important enough to deserve primary navigation, or should Search/context/Expert mode surface it?**
6. **If the hardware/capability is absent, can the UX explain that truthfully without dead/fake UI?**
7. **Does it add real value, or merely expose a Linux/Pi command that already exists without interpretation?**

A broad underlying platform plus a curated visible experience is the target.

---

# 10. Reconciliation result

No foundational backtrack is required before the final fresh-eyes review.

The recent Toolbelt/facet/Sandbox discussions fit the existing architecture with a manageable set of consolidations:

- one Doctor;
- one System Graph;
- one managed mutation stack;
- one capability/provider lifecycle;
- coherent Workspaces rather than mini-app proliferation;
- curated facets rather than tab cages;
- one owner-customization/provenance story;
- Sandbox simulations using production contracts;
- cross-cutting Search/Automation/History/Support rather than new product silos.

The project remains broad in capability without requiring a correspondingly cluttered default UI.

## Next checkpoint

The next major discussion is the owner-requested **whole-project fresh-eyes / epiphany review**.

Per owner instruction, do not start that review automatically. Begin only after explicit owner authorization.
