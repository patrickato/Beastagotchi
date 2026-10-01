# Beastagotchi Post-Reconciliation Build Order and Roadmap

**Date:** 2026-09-27  
**Status:** canonical build-order rewrite paired with `Beastagotchi_Canonical_Architecture_Contracts_2026-09-27.md`  
**Purpose:** stop feature-discussion scope creep, close v0.19 truthfully, then resume implementation in dependency-ordered, test-backed tranches.

---

# 1. Release-boundary decision

The large Doctor/Capability/AI/Monster/Security expansion does **not** become a new prerequisite list for v0.19.

v0.19 already has an established release truth gate:
1. owner accepts actual generated flagship renderer off-screen;
2. exact tested source is staged on the reference Pi;
3. physical 480x320 readability/touch/navigation/QR/glare/smoothness/thermal/framebuffer evidence is collected;
4. physical-only defects are fixed and re-tested;
5. presentation ownership/handoff state remains explicit and rollback-safe;
6. only then is v0.19 promotion decided.

Do not invalidate this evidence by inserting a broad new runtime architecture rewrite before Gate 1 closes.

Therefore:

> **Close the current v0.19 branch as the Unified Experience release line first. Resume the newly reconciled platform architecture on the next development line immediately afterward.**

Draft PR #22 remains valuable architecture work and should be carried forward/rebased rather than discarded.

---

# 2. Immediate work — finish v0.19

## V19-1 — Off-screen visual acceptance

Use the actual generated 480x320 outputs for the five flagship Experience families and required translated pages.

Acceptance asks:
- does the generated renderer finally resemble the intended product language rather than earlier card/dashboard prototypes?;
- are creature/art/layout focal points convincing?;
- do text hierarchy and touch targets remain readable?;
- do important live values remain real/canonical?;
- are all five families structurally distinct rather than recolors?

No source-only claims count.

## V19-2 — Reference Pi physical session

After owner off-screen acceptance:
- stage exact commit-pinned artifact;
- preserve config and DB backup;
- run bounded acceptance harness;
- test touch/navigation;
- test QR phone scanning where applicable;
- test display ownership/rollback behavior that is currently enabled;
- capture framebuffer/write telemetry;
- capture sustained thermal/performance evidence;
- inspect glare/readability/animation/smoothness on the actual 3.5-inch TFT.

The physical Pi/TFT is final visual truth.

## V19-3 — Physical-only fixes

Only fix issues actually exposed by the physical run unless a critical regression is discovered.

Avoid reopening broad redesign.

## V19-4 — v0.19 promotion decision

When Gate 1 is physically closed:
- run full source/CI regression;
- update gate ledger;
- decide whether v0.19 merges/promotes as the new stable baseline;
- preserve exact release SHA/artifact/provenance.

### v0.19 non-blocking items

These may remain later tracks and must not prevent v0.19 solely because they are incomplete:
- deep Security Workspace;
- Broad AI;
- deep Doctor rebuild;
- new Provider/Ability framework;
- Home Base heavy security tools;
- deep breeding/genetics;
- hardware-hacking expansion;
- responsive 5-inch/large-display completion;
- public Global Interaction backend;
- full Pack consumer universe.

---

# 3. Post-v0.19 development-line bootstrap

After v0.19 promotion, create/rebase the next active development line from the stable release.

Then rebase/reconcile draft PR #22 onto that line.

Do not merge PR #22 blindly by commit count. Preserve its tested behavior while resolving any v0.19-close changes explicitly.

Bootstrap acceptance:
- full CI green;
- architecture migration ledger updated to new base;
- no state-manager ownership regressions;
- no DB/thread regressions;
- no bridge/privacy regressions;
- no Pack transaction regressions;
- basic Pi service startup/bridge sanity after rebase.

---

# 4. Architecture Tranche A — correctness contracts become canonical

**Goal:** finish the structural work already started in PR #22 before adding many new subsystems.

## A1 — DB migration/versioning

Implement explicit schema versioning/migrations before more stores appear.

Acceptance:
- deterministic forward migration;
- backup/recovery behavior;
- migration tests from supported prior schemas;
- no silent schema drift.

## A2 — Registered Action migration

Migrate remaining Beast-managed Actions incrementally into ActionSpec/RegisteredActionBroker.

Acceptance:
- stable IDs/input schemas;
- existing behavior preserved;
- legacy fallback shrinks measurably;
- tests for each migrated action family.

## A3 — centralized authority/risk metadata

Action metadata becomes the source for UI/Procedure/AI/Automation authorization decisions.

Do not let Broad AI or individual screens invent a parallel permission model.

## A4 — activate Signal/Event specs

Move from registry substrate-only to real semantic catalog ownership while EventBus remains transport.

Add bounded queue/drop/backpressure observability.

## A5 — Transaction expansion

Migrate the next mutation families through the shared Transaction engine:
- update/install/remove where practical;
- backup/restore mutation stages;
- plugin/config changes;
- provider preference/config changes that warrant durable rollback.

Keep proven inner rollback until equivalent verification exists.

### Tranche A exit gate

- shared ownership canonical;
- versioned DB migrations canonical;
- Action registry is normal path for managed mutations;
- Signal/Event semantic catalogs active;
- Transaction engine handles representative non-Pack mutation families;
- CI + Pi runtime sanity green.

---

# 5. Architecture Tranche B — runtime lifecycle, progress, arbitration

**Goal:** stop background work and resource ownership from being scattered hidden loops.

## B1 — ModuleRuntime

Create declared lifecycle ownership for long-running/recurring Beast modules.

## B2 — Scheduler

Support cadence/context-triggered background work with explicit cancellation/restart semantics.

## B3 — Task/progress primitive

Unify truthful task state across:
- Doctor;
- downloads;
- Pack installs;
- updates;
- indexing;
- backups/restores;
- Home Base handoffs;
- later security analysis.

Exact percentage only when measurable; otherwise stages/activity.

## B4 — resource leases/arbitration

Start with resources we already know conflict:
- Wi-Fi radio roles;
- SDR tuner ownership;
- GPIO/SPI/I2C resources;
- presentation/display ownership where appropriate.

### Tranche B exit gate

At least one real background module and one conflicting hardware resource must prove the new lifecycle/arbitration model end-to-end.

---

# 6. Architecture Tranche C — Provider + Ability + System Graph

**Goal:** make “what can this Beast do?” a real dynamic system.

## C1 — ProviderRegistry

Define ProviderSpec/runtime provider state and lifecycle.

Initial representative providers should be chosen from already-existing reality, not hypothetical hardware:
- Pwnagotchi bridge;
- Bettercap;
- GPS if available in test/Sandbox;
- system health/power facts.

## C2 — AbilityRegistry / resolver

Derive READY/AVAILABLE/NEEDS HARDWARE/NEEDS SOFTWARE/FULL TOOL/etc. from real Provider/dependency state.

Reuse/merge with the existing Dependency & Capability Resolver from v0.19 rather than creating a competing graph.

## C3 — System Graph integration

Dependencies, providers, abilities, tools, actions, hardware and `USED BY` relations become queryable through one graph view/model where practical.

## C4 — Device Passport

Expose stable actual-machine facts needed by Doctor, Abilities, hardware onboarding and compatibility decisions.

### Tranche C exit gate

Plug/remove/change one representative provider and prove Abilities/System Graph update without restart or duplicated truth.

---

# 7. Architecture Tranche D — Pwnagotchi/Bettercap truth bridge

**Goal:** make the foundation engine observable through stable structured contracts without modifying Pwnagotchi core unnecessarily.

## D1 — `beast-bridge`

Harden/extend the existing bridge plugin around normalized events and versioned local schema.

Initial events:
- lifecycle;
- epoch/session;
- AP/client observations where available;
- associations/deauth events;
- capture/handshake events;
- peer events;
- channel activity/context.

## D2 — Bettercap Provider

Consume structured Bettercap API/session/event truth where available rather than parsing terminal prose.

## D3 — `radio-vitals`

Prove actual packet/frame reception and channel behavior, not merely interface existence.

## D4 — `capture-ledger`

Attach durable provenance/session/hash/duplicate metadata to captures.

### Tranche D exit gate

On the real reference Pi:
- radio/device path known;
- monitor interface known;
- channel behavior visible;
- actual frame reception proven;
- Bettercap visibility proven;
- Pwnagotchi event bridge proven;
- capture artifact provenance proven.

This tranche should directly resolve the class of “service active but handshakes/capture pipeline not truly working” problems that motivated the Doctor work.

---

# 8. Architecture Tranche E — Evidence, Scope, Capture Intelligence

**Goal:** give diagnostics/security one common factual substrate before adding many tools.

## E1 — Evidence Artifact store

Reference/hash raw artifacts without forcing every artifact into one DB blob.

## E2 — Observation / Finding records

Implement source/provenance/confidence/privacy/session/device links.

## E3 — Scope Passport

One owner-defined authorized/lab/session scope consumable by supported security Procedures/Tools.

## E4 — Capture Intelligence v1

For Pwnagotchi/Bettercap captures show:
- artifact identity/hash;
- duplicate relation;
- session;
- interface/channel context;
- participant/AP context where available;
- deterministic quality/usefulness facts where safely derivable;
- Full Tool handoff.

### Tranche E exit gate

A single captured artifact must be traceable from source event -> raw evidence -> normalized observation -> session/scope -> UI/Search -> Full Tool handoff.

---

# 9. Architecture Tranche F — Doctor v1 on the new substrate

**Goal:** turn the Doctor design into a functioning evidence-based clinician without waiting for Broad AI.

## F1 — Machine Census + vital signs

Inventory slow-changing patient facts plus cheap live health state.

## F2 — Probe descriptor/library

Start with fault families already proven valuable:
- RADIO-DEEP;
- DISPLAY-DEEP;
- STORAGE-DEEP;
- POWER-DEEP;
- PLUGIN/BEAST-CORE health.

## F3 — Known-Good / What Changed?

Capture healthy baselines and relevant change history.

## F4 — hypothesis/evidence/confidence model

Doctor findings explicitly link to evidence and competing/rejected hypotheses.

## F5 — repair Procedure integration

At least one bounded repair must use:
Doctor diagnosis -> proposed Procedure -> Transaction -> verification -> receipt -> Known-Good update.

### Tranche F exit gate

Use two real historical failures as acceptance cases:
1. ILI9486/display path failure family;
2. Pwnagotchi radio/capture/channel failure family.

Doctor must distinguish “running” from “functioning” in both.

---

# 10. Architecture Tranche G — Tool Catalog + Help/Learn + Search integration

**Goal:** create the ramp from beginner to real Linux/security software before trying to integrate hundreds of programs.

## G1 — Tool Adapter manifest

Implement detection/install/help/input/output/resource metadata.

## G2 — Help/Learn broker

Support built-in help/man/local docs/upstream docs and Beast tutorials.

## G3 — federated Search hooks

Registries, files, Doctor knowledge, local docs and selected web/project providers become one Search flow with provenance.

## G4 — representative Full Tools

Prove the pattern with a deliberately small set:
- Nmap-style network discovery/service tool;
- Wireshark/TShark capture analysis handoff;
- Kismet or equivalent radio observation provider if resource fit is acceptable;
- one hardware/firmware tool later only if it helps prove the manifest abstraction.

Do not turn the representative set into an enormous catalog before the adapter model is stable.

### Tranche G exit gate

A novice can ask/find “what can I do?”, learn the relevant real tool, run one bounded Guided workflow, inspect raw output, and graduate to the Full Tool without duplicated truth.

---

# 11. Architecture Tranche H — Security Workspace v1

**Goal:** prove the security architecture with a small coherent vertical slice rather than shipping Kali-in-a-menu.

Release-v1 Security Workspace should initially compose:
- Scope Passport;
- owned/lab network discovery;
- device/service observations;
- Wi-Fi/Pwnagotchi radio/capture view;
- Capture Intelligence;
- findings/evidence/history;
- Help/Learn;
- remediation/re-test where deterministic;
- Full Tool handoffs.

Representative Guided workflows:
1. qualify current Wi-Fi adapter/radio path;
2. inspect one owned/lab network safely;
3. inspect one capture and open it in the Full Tool;
4. compare known-network/security baseline where available;
5. generate a bounded session report.

Do not block this tranche on every post-release security integration.

---

# 12. Architecture Tranche I — Presentation substrate migration

**Goal:** migrate UI architecture only after the underlying truth contracts exist, while preserving the v0.19 visual language.

Implement/migrate:
- SurfaceRegistry;
- SurfaceStack;
- InputRouter;
- NavigationController;
- common task/progress overlays;
- Provider/Ability/Doctor/Security surfaces;
- faithful WebUI/Studio preview path.

Migrate pages incrementally; no flag-day renderer rewrite.

Physical TFT tests remain mandatory for meaningful presentation changes.

---

# 13. Architecture Tranche J — Broad AI optional assistant

**Goal:** add conversation after Beast already knows what is true and how to act.

## J1 — AI Provider abstraction

Support remote/local/Home Base providers without hard-coding one company/model.

## J2 — context/privacy router

Owner policy decides what local/system/search/evidence context may leave the Beast.

## J3 — structured Beast truth access

AI reads/query tools, not raw magical access to everything.

## J4 — managed Action bridge

Natural-language intent resolves to the same Action/Procedure/Transaction path as UI/Automation.

## J5 — first assistant roles

Prioritize:
- “Can my Beast do X?”;
- Search/documentation synthesis;
- Tool Tutor;
- Doctor explanation/consultation;
- optional session/Homecoming narration.

Broad AI is not a release dependency for Doctor or Security Workspace.

---

# 14. Architecture Tranche K — Creature perception/expression substrate

**Goal:** wire the existing roster/lineage system to real Beast senses without starting the giant genetics expansion.

Implement:
- semantic perception inputs from Signals/Events;
- deterministic traits/affinities;
- semantic expression state;
- structured meaningful memories;
- output adapters for available presentation surfaces.

Do not gate hardware/software capability behind creature progression.

Deep breeding/genetics/morphology/easter-egg economy remains a later content/system tranche.

---

# 15. Post-release / non-blocking expansion reservoir

Explicitly preserved but not allowed to move the immediate release boundary:

- second hardware-hacking/security-crossover research batch;
- deeper Proxmark/Ubertooth/KillerBee/GreatFET/Facedancer integrations;
- deeper CAN/industrial workflows;
- firmware reverse-engineering workbench depth;
- full forensics stack / Timesketch / heavy DFIR;
- Greenbone/Wazuh/MISP/OpenCTI-style integrations;
- Security Range/Capsules beyond first representative labs;
- deep CTF curriculum;
- Node-RED expert flow integration;
- specialized Doctor-trained/fine-tuned model;
- voice/STT/TTS;
- large autonomous agents;
- generative media;
- advanced camera/CV/audio/haptic expression;
- full Pico/ESP32 repurposable role cartridges;
- deep breeding/genetics/morphology/rare mutation chains;
- deferred Cross-Layer Batch 2 ideas;
- advanced predictive/anomaly health systems.

These remain design-compatible because the substrate above is meant to support them later.

---

# 16. Validation strategy for every tranche

Every implementation tranche must include:
1. contract tests;
2. regression tests for legacy behavior being replaced;
3. migration/rollback tests where state changes;
4. Sandbox/record-replay tests where hardware can be virtualized;
5. physical Pi validation when the contract touches real radio/display/touch/storage/power/hardware;
6. truthful update to the migration ledger;
7. no declaration of physical success from CI alone.

Use Beast Sandbox/virtual Providers to reduce iteration cost, not to replace final physical truth.

---

# 17. Recommended branch/PR strategy

Avoid one enormous post-v0.19 PR.

Recommended sequence:
- close/promote v0.19;
- rebase architecture foundation as Tranche A PR;
- B/C can be separate PRs or a tightly bounded pair;
- D/E should remain reviewable and physically testable;
- F Doctor should be its own major tranche;
- G/H Tool+Security can be separate but adjacent;
- Presentation, Broad AI, and Creature substrate each stay independent enough to roll back.

Each PR should leave legacy fallbacks intact until the replacement path is verified and the migration ledger marks the legacy path removable.

---

# 18. Immediate next action after this planning rewrite

The first implementation action is **not** new security code.

It is:

> **Return to the v0.19 Gate-1 renderer/physical acceptance path, finish the actual release truth gate, promote or explicitly decide v0.19, then bootstrap the next development line and rebase PR #22 as Architecture Tranche A.**

This order preserves the enormous new capability roadmap without sacrificing the discipline needed to actually ship a stable Beastagotchi.