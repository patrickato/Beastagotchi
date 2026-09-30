# Beastagotchi Toolbelt Candidate Idea Ledger

**Date:** 2026-09-26
**Status:** discussion candidates; preserved so ideas do not disappear. This file does **not** mean every item is owner-approved or committed to the roadmap.

## Product rule: one Doctor

Beastagotchi should have **one Doctor**.

Names such as “TFT Doctor,” “Monitor-Mode Doctor,” “Storage Doctor,” and similar phrases used during brainstorming are shorthand for **diagnostic domains**, not separate Doctor products, engines, personas, or top-level UI destinations.

The intended model is:

- **Doctor** = the single cross-cutting diagnostic/interpretation/recommendation system.
- **Condition packs / diagnostic knowledge** = domain-specific symptoms, checks, evidence patterns, likely causes, confidence, and remediation guidance.
- **Probes / Instruments** = gather truth without pretending to know more than the system can observe.
- **Tools** = bounded operations Doctor may recommend or invoke subject to authority/policy.
- **Procedures** = multi-step diagnostic or remediation workflows that Doctor can launch, monitor, and interpret.
- **Transactions** = safe mutation/verification/rollback substrate for consequential repairs.
- **History / Transaction Journal / customization ledger** = evidence Doctor uses to answer “what changed?” and distinguish fault from intentional owner customization.
- **Workspaces / Surfaces** = places where Doctor findings are shown contextually; they do not create new Doctors.

Example: a display failure is handled by the same Doctor using display/TFT condition knowledge + framebuffer/SPI/device-tree probes + relevant Procedures. A monitor-mode failure is handled by the same Doctor using radio condition knowledge + interface/driver/regulatory probes + relevant Procedures.

This avoids duplicate diagnostic systems, duplicated UI, duplicated history, contradictory recommendations, and fragmented ownership of truth.

## Related owner-sovereignty rule

**Beastagotchi is an open platform with a managed core, not a locked appliance. Unsupported does not mean forbidden.**

Owner-controlled software/extensions may coexist with Beast. Beast may observe them generically, show health/resource/resource-ownership effects, preserve them in backups when appropriate, and mark resulting customization/drift, while only guaranteeing behavior that remains inside managed contracts.

## Fifteen strongest candidate additions

### 1. “What Changed?”
**Purpose:** explain meaningful differences between a known-good state and now.

**Tie-in:** Transaction Journal + customization/override ledger + config snapshots + package/service history + Doctor + Recovery Vault + Device Passport.

**Avoid duplication:** this should be a Doctor/history capability surfaced in Steward/System workspaces, not a separate diagnostics product.

### 2. System Graph
**Purpose:** one underlying graph for Machine Map, Capability Graph, Pipeline Inspector, and Resource/Device Claim Map views.

**Nodes may include:** hardware, buses, drivers, interfaces, services, providers, modules, capabilities, storage, surfaces, owner extensions.

**Edges may include:** owns, depends-on, provides, consumes, routes-to, conflicts-with, blocks, presents-through.

**Tie-in:** Capability Resolver + ModuleRuntime/Scheduler + Doctor + Device Passport + provisioning/BOM + Toolbelt + Steward.

**Avoid duplication:** Machine Map, Capability Graph, Pipeline Inspector, and Claim Map should be views/queries over the same graph, not four separate systems.

### 3. Monitor-mode diagnostic knowledge
**Purpose:** let the single Doctor diagnose monitor-interface/radio-path failures.

**Tie-in:** Radio Workspace + System Graph pipeline view + driver/PHY/interface/regulatory probes + Bettercap/Pwnagotchi state + Procedures + history.

**Avoid duplication:** no “Monitor-Mode Doctor” product. This is a Doctor condition pack / diagnostic domain.

### 4. TFT/display diagnostic knowledge
**Purpose:** let the single Doctor diagnose SPI/DRM/framebuffer/device-tree/touch/presentation failures.

**Tie-in:** Display Instrumentation + System Graph + device-tree/bus probes + Presentation Broker + Procedures + known-good configuration/history.

**Avoid duplication:** no “TFT Doctor” product. This is a Doctor condition pack / diagnostic domain.

### 5. Power Detective
**Purpose:** turn Pi undervoltage/throttling/power-quality evidence into understandable incidents and correlations.

**Tie-in:** Instrument facet + Doctor + Resource Governor + Thermal history + kernel events + USB/storage reset history + Device Passport.

**Avoid duplication:** belongs in System Health/Steward views and Doctor evidence, not a separate app family.

### 6. Radio Workspace
**Purpose:** coherent field/radio workspace combining channel coverage, interface state, regulatory state, Bettercap/Pwnagotchi health, epochs, timelines, and relevant Tools/Procedures.

**Tie-in:** Instrument + Toolbelt + Explore + Doctor + Field RF Journal.

**Avoid duplication:** Channel Coverage Analyzer, Interface Map, Regulatory Inspector, Epoch Lens, etc. are views/instruments inside this workspace.

### 7. Hardware Bench
**Purpose:** coherent hardware/electronics workspace for attached devices, buses, GPIO, serial, sensors, claims, conflicts, and relevant Tools/Procedures.

**Tie-in:** Toolbelt + Workshop + Instrument + Doctor + System Graph + BenchLink + Sensor Onboarding.

**Avoid duplication:** USB/I2C/SPI/GPIO inspectors should be views/tools in this workspace rather than independent top-level apps.

### 8. Sensor Onboarding
**Purpose:** detect a supported/recognizable sensor or peripheral, explain what it is, configure a provider with owner approval, verify real readings, and register canonical Signals.

**Tie-in:** Capability Resolver + Provider Registry + Instrument + Hardware Bench + Doctor + Packs/SDK.

**Managed-path rule:** detect -> explain -> offer -> verify; never blindly mutate because hardware appeared.

### 9. BenchLink
**Purpose:** generic bridge for Pico/ESP32/Arduino-class or other external devices to declare/publish Signals and bounded Actions into Beastagotchi.

**Tie-in:** Capability/Provider registries + Toolbelt + Instrument + Procedures + Doctor + automation + hardware-expanded Beast perception/expression.

**Boundary:** external devices do not receive ambient Beast authority merely by connecting.

### 10. Device Passport
**Purpose:** durable identity/BOM/capability record for the exact Beastagotchi device.

**Tie-in:** Provisioner + capability graph + firmware/kernel/hardware inventory + Packs/plugins + Recovery Vault + support bundles + known-good fingerprints.

**Avoid duplication:** should consume canonical inventory/capability data rather than maintain another parallel hardware database.

### 11. Storage Workspace
**Purpose:** one coherent home for physical devices, filesystems, mounts, roles, health, capacity, errors, performance, Recovery Vault/content-pool relationships, and relevant Procedures.

**Tie-in:** Steward + Toolbelt + Doctor + Content Store + Recovery Vault + System Graph.

**Avoid duplication:** Storage Pulse, Filesystem Explorer, Storage Doctor, removable-media tools, etc. become views/tools/procedures here; Doctor remains singular.

### 12. Transaction / Procedure visibility
**Purpose:** make Beast’s safety machinery understandable instead of invisible.

**Includes:** Transaction Inspector, Procedure Tracer, verification evidence, rollback status, stage provenance, and durable history.

**Tie-in:** Steward + Developer/Expert mode + Doctor + Recovery + support bundle + Action system.

**Avoid duplication:** one shared Transaction/Procedure truth rendered in multiple surfaces.

### 13. Field RF Journal
**Purpose:** privacy-curated history of real environmental/radio observations during Expeditions without requiring permanent raw identity retention by default.

**Tie-in:** Explore + Instrument + Companion/Life + Radio Workspace + progression/discovery + privacy policy.

**Rule:** derived environmental truth may feed discovery/progression; unknown remains unknown and sensitive/raw identifiers stay owner-controlled.

### 14. Owner Space / unmanaged-extension model
**Purpose:** preserve owner sovereignty while keeping the managed Beast path understandable and supportable.

**Suggested states:** managed, compatible, unmanaged, customized, conflicting.

**Tie-in:** Expert/Developer mode + customization ledger + Doctor + System Graph resource ownership + backups + Tool/Surface/Pack registration.

**Rule:** unsupported != forbidden; unmanaged software may coexist, but Beast does not pretend to guarantee or manage its internal behavior.

### 15. Hardware expands Beast perception and expression
**Purpose:** real attached hardware can add genuine senses/capabilities/presentation surfaces to the Beast.

**Examples:** environmental sensor -> ambient Signals; GPS -> location-aware Explore; light/accelerometer/power monitor -> additional context; external display/LED matrix -> presentation Surface; BenchLink device -> new physical capabilities.

**Tie-in:** Companion/Life + Instrument + Explore + Capability Resolver + Sensor Onboarding + BenchLink + Experiences/Choreography.

**Rule:** creature behavior should derive from real available capability/state, not pretend a sensor exists when it does not.

## Integration principles derived from this discussion

1. **One capability, many presentations/workflows.** Do not implement separate copies for TFT, Studio, CLI, Doctor, support, automation, and testing.
2. **One Doctor, many diagnostic domains.** Domain knowledge is modular; diagnostic authority and identity remain singular.
3. **Prefer one underlying System Graph over multiple topology/claim/pipeline databases.**
4. **Prefer Workspaces containing Instruments/Tools/Procedures over many top-level mini-apps.**
5. **Reuse canonical State/Signals/Events and durable history. Do not build parallel truth stores for convenience.**
6. **Detect -> explain -> offer -> verify** is the normal hardware/configuration onboarding path.
7. **Unknown/unmanaged remains explicit.** Beast must not fabricate compatibility, ownership, health, or recovery guarantees.
8. **Owner sovereignty survives the managed UX.** Root/manual customization remains possible; Beast records boundaries rather than pretending they do not exist.

## Provisionally accepted adjacent-ecosystem directions

The owner indicated general agreement with the following directions. Carry them forward as **provisionally accepted product concepts**, subject to later refinement and roadmap prioritization rather than treating them as separate new subsystems.

### Discovery Inbox
A common intake surface for newly observed hardware, plugins, Packs, owner-installed services, storage, displays, BenchLink peers, or other unassigned capabilities.

Possible owner choices are contextual, but the core pattern is: **inspect -> manage/use -> leave in Owner Space -> ignore**. Discovery does not imply automatic activation or authority.

### Standard diagnostic bundle contract
Providers, Packs, integrations, and managed extensions may expose structured, privacy-curated diagnostic evidence through one shared contract so Doctor, support bundles, and recovery tooling do not need bespoke log scraping for every extension.

This feeds the **single Doctor**; it does not create integration-specific Doctors.

### Capability Archive
A user-facing view over already-canonical durable content/history for saved hardware profiles, field/diagnostic snapshots, Beast Capsules, discovered environments, saved Procedures, owner-created tools, Bench sessions, and similar artifacts.

Prefer a view/index over existing stores rather than another independent storage database.

### Declarative Recipes / Blueprints
Reusable data-first compositions of existing Instruments, Tools, Procedures, Workspaces, conditions, defaults, and Choreography. Recipes should reuse existing execution primitives rather than become a parallel automation engine.

Community sharing should be possible without requiring executable code where declarative composition is sufficient.

### Integration/provider health contract
Anything that provides a capability should be able, where practical, to answer a common set of health questions: **what are you, what do you provide, are you healthy, and what evidence can be safely shared?**

Doctor, System Graph, Device Passport, Discovery Inbox, and support/recovery surfaces can all consume the same health contract.

### Unifying lifecycle

For external things entering Beastagotchi, prefer the lifecycle:

**Discovery -> Capability -> Health -> Usage**

- **Discovery:** Beast notices a thing without assuming ownership.
- **Capability:** determine what it can actually provide.
- **Health:** determine whether that provider/integration is currently functioning and expose evidence.
- **Usage:** allow Workspaces, Instruments, Procedures, Companion/Explore behavior, automation, or other consumers to use the capability according to authority and owner intent.

This lifecycle should reuse the Capability Resolver, Provider/Registry contracts, System Graph, Doctor, Owner Space, and canonical State rather than create a separate discovery platform.

## Approval status

The original fifteen items remain **preserved candidates** pending later owner classification as approved, modify/discuss, reserve, or reject.

The five adjacent-ecosystem directions above are **provisionally accepted** based on owner agreement. This means they should be carried forward and considered during architecture/product reconciliation, but their exact UX, implementation form, and release priority are not frozen.