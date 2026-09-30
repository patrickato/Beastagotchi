# Beastagotchi Pre-Implementation Continuity Checkpoint

**Date:** 2026-09-26  
**Purpose:** durable handoff/checkpoint before the remaining pre-implementation discussions. If chat context is lost, start here and follow linked records.

---

# Project state

Beastagotchi is a modular local-first platform built on top of a protected Pwnagotchi + Bettercap foundation, targeting Raspberry Pi 4 8GB with the owner's 3.5-inch 480x320 ILI9486/XPT2046 display as the reference physical unit.

Core product principles remain:

- Pwnagotchi/Bettercap remain protected underlying engines and independently usable;
- one canonical truth model;
- real/live data over fabricated/demo telemetry;
- unknown remains unknown;
- synthetic state must be explicitly marked;
- owner sovereignty: managed core, open machine;
- large capability/content universe, small active runtime working set;
- full capability without UI clutter;
- efficiency before degradation;
- Doctor as singular cross-cutting diagnostic/repair system;
- one System Graph, many views;
- Action -> Transaction -> Procedure for managed mutation;
- broad extensibility through Providers/Capabilities/Packs/SDK/Owner Space.

Physical Gate 1 visual acceptance is still unresolved and must not be falsely claimed complete.

---

# Important branches / PR context

## Active historical/product branch
`v0.19-unified-experience`

Contains the mature v0.19 product/runtime work and remains unmerged pending gates.

## Architecture preservation/discussion branch
`openai/v019-visual-reference-archive`

Use this branch for preservation of architecture reviews, owner decisions, discussion ledgers and pre-implementation checkpoints.

## Architecture implementation tranche branch
`openai/v019-architecture-foundation-tranche1`

Contains already-completed bounded foundation implementation including:
- shared manager ownership;
- SQLite thread hardening;
- preference store foundation;
- bridge restart/privacy corrections;
- typed registries;
- RegisteredActionBroker migration seed;
- RuntimeBeastCore composition adapter;
- migration ledger;
- shared Transaction engine;
- Pack-install outer Transaction integration.

Implementation remains intentionally paused while pre-implementation discussion finishes.

## Claude review branch
`claude/beastagotchi-foundation-review-2026-09-25`

Preserve as independent review input; do not blindly adopt.

---

# Architecture review state

Architecture Parts 1–11 have been reviewed and preserved, covering:

1. stable kernel contracts;
2. authority/ownership;
3. registries;
4. Transactions/Procedures;
5. runtime/resource control;
6. content/storage/distribution;
7. lifecycle/progression/lineage/discovery;
8. extension SDK/compatibility/trust;
9. presentation platform;
10. provisioning/update/recovery/reproducibility;
11. synthesis/migration strategy.

No flag-day rewrite is planned.

---

# Product structure already agreed

Seven provisional user-facing facets:

1. Companion / Life;
2. Instrument / Observe;
3. Operate / Toolbelt;
4. Explore / Field;
5. Create / Workshop;
6. Connect / Exchange;
7. Steward / Care.

These are product lenses, **not mandatory tabs**.

Toolbelt taxonomy:
- Instrument = observe ongoing truth;
- Tool = bounded operation;
- Procedure = multi-step goal/workflow;
- Workspace = interactive environment containing Instruments/Tools/Procedures.

Apps are packaging/presentation, not another capability type.
Automation is invocation mode, not another capability type.

---

# Singular Doctor rule

There is **one Doctor, many specialties**.

Doctor is intended to become the one-stop entry point for problems across Pwnagotchi, Beastagotchi and the underlying Linux/Pi system.

Do not proliferate separate TFT Doctor / Radio Doctor / Storage Doctor products.

Doctor should consume machine-wide probes/evidence, diagnose, repair automatically where safe, verify repairs, remember previous successful resolutions, and walk the owner through remaining steps.

Upcoming dedicated Doctor discussion is required before implementation resumes.

See:
`docs/Beastagotchi_PostFreshEyes_Owner_Feedback_Addendum_2026-09-26.md`

---

# System Graph rule

Use one underlying System Graph / dependency/ownership substrate.

Machine Map, Capability Graph, Pipeline Inspector, Device Claim Map and similar ideas should be views/queries over the same graph, not separate databases/systems.

---

# Owner Space / open-platform direction

Accepted philosophy:

> Beastagotchi is an open platform with a managed core, not a locked appliance. Unsupported does not mean forbidden. Owner-controlled extensions may coexist with Beast, but Beast only guarantees what remains inside its managed contracts.

Distinguish:
- allowing;
- accommodating;
- facilitating.

Unmanaged/custom states may include:
- managed;
- compatible;
- unmanaged;
- customized;
- conflicting.

Owner/root/manual escape remains available.

---

# Accepted Toolbelt candidate priority order

1. Owner Space / managed-boundary model
2. Transaction/history evidence
3. System Graph substrate
4. Device Passport/canonical inventory
5. What Changed? data capture
6. One Doctor with extensible condition knowledge
7. Radio Workspace
8. Power Detective
9. Storage Workspace
10. Display/radio diagnostic packs
11. Hardware Bench
12. Sensor Onboarding
13. Field RF Journal
14. Hardware-expanded Beast senses
15. BenchLink

These are not fifteen mandatory standalone apps.

---

# Windows Beast Sandbox — selected direction

Current accepted development/test direction:

- WSL2 = everyday Beast Sandbox/workshop;
- Docker = optional/guided disposable destructive test cells, hidden behind simple BeastLab controls where practical;
- Beast-native virtual hardware providers run inside WSL;
- SSH to the real Pi is a first-class validation path and fallback;
- record/replay strongly desired, manual transfer acceptable initially;
- QEMU explicitly not required unless a future concrete problem justifies reopening it.

Sandbox is a development aid, **not an end-user Beast dependency**.

Shadow Beast remains optional Sandbox-only candidate functionality.

Future Sandbox quality work should include real browser/end-to-end + visual regression testing and clear visual provenance labels.

---

# Fresh-eyes review status

Completed and preserved at:

`docs/Beastagotchi_Fresh_Eyes_Epiphany_Review_2026-09-26.md`

Important candidates discovered:
- time semantics + causal/correlation context;
- persistent-state custody descriptors;
- explicit physical/install/creature identity scopes;
- Incident -> Doctor -> Procedure -> replay learning loop;
- optional Shadow Beast;
- Universal Inspect / Why? candidate;
- Chronicle + Homecoming/debrief;
- composable context axes;
- managed egress explanation;
- RF/sensor perception + expression model;
- browser/visual regression + exact-render provenance.

Owner then corrected the review direction: these are useful, but the pass was too diagnostic/observability-heavy and did not adequately explore **new capabilities Beast can add**.

That correction is preserved at:

`docs/Beastagotchi_PostFreshEyes_Owner_Feedback_Addendum_2026-09-26.md`

---

# Important owner corrections after fresh-eyes

## Doctor
Doctor should have broad access to prewritten/on-demand machine probes across essentially the full Linux/Pi/Pwnagotchi/Beast stack.

Desired conceptual pipeline:

> Machine Census -> Probe Library -> Knowledge/Search -> Diagnosis -> Fix -> Verify -> Learn

Preserve:

> **Doctor finds it -> uses it -> puts it back.**

Doctor may eventually temporarily acquire trusted missing diagnostic/helper utilities through managed Actions/Transactions, use them, and remove/restore them when appropriate.

## Backups/recovery
Owner expects a full ladder from checkpoints/Known-Good through complete recovery backups/rebuild manifests to full SD image/mirror and rescue options.

Current implementation is partial; architecture must keep the entire ladder.

## Homecoming/debrief
Owner strongly likes the idea if expanded beyond another log.

Desired direction:
- real GPS/offline maps;
- plotted route/polyline;
- AP/observation points and visually distinct types;
- real Pwnagotchi/Bettercap/session/epoch information where available;
- captures/handshakes/peers;
- other provider/RF/sensor observations;
- beautiful visual summary;
- rendered debrief discarded by default after viewing unless owner snapshots/saves/exports it;
- underlying source/history retention handled separately.

## Home Base
Home Base should encompass owner-policy-governed queued uploads/downloads, NAS/library sync, backup replication, content, offline docs/maps, update staging, package/software acquisition and other heavy network/power-friendly work.

## Search
Search target is broad/federated:
- local Beast;
- offline docs/manuals/wiki/PDF/TXT/datasheets;
- owner library;
- history/Doctor/Expeditions;
- Internet/web/GitHub/current docs when available.

## AI
AI is optional and not yet approved. Dedicated discussion must explore the full opportunity space without prematurely constraining it or assuming it belongs.

## Monster/breeding
Do not progression-lock fundamental machine capabilities. Revisit whether breeding unlocks Instincts/talents/behaviors/affinities/combinations/expression/discovery/etc.

Preserve **Perception <-> Expression** as a strong concept.

---

# Remaining discussion order before implementation resumes

## 1. Doctor deep-dive / jam — NEXT

Define Doctor's complete role, probe architecture, knowledge sources, automatic repair boundaries, helper acquisition, learning, verification and owner walkthrough behavior.

## 2. Capability Expansion Pass

Primary question:

> **What new things can Beastagotchi actually DO because it sits on Pwnagotchi + Linux + Raspberry Pi + Beast architecture?**

Review by layers, including tools/packages/libraries/services/hardware/integrations/convenience features/dependencies/Owner Space compatibility.

Diagnostics must not dominate this pass.

## 3. Cross-layer X + Y => Z jam

Interactive creative session. Combine layers/capabilities into surprising useful behaviors.

## 4. AI discussion

Explore if/where AI earns a place.

## 5. Monster / breeding / perception / expression jam

Revisit progression/lineage unlocks and hardware-as-senses/expression.

## 6. Final reconciliation

Classify proposals:
- APPROVE;
- MODIFY;
- RESERVE/LATER;
- REJECT.

Then update contracts/roadmap/migration order and resume implementation.

---

# Discussion style rule

For future ideation, use a jam-session format rather than fully concluding every idea before owner input.

Preferred pattern:

1. Idea.
2. Why it is possible.
3. Which layers combine.
4. What it unlocks.
5. Needed hardware/software/dependencies.
6. Optional vs automatic behavior.
7. Open forks/questions for owner input.
8. Preserve worthwhile owner additions immediately.

The owner wants creative, proactive ideation and does not want every tiny detail sent back for confirmation. Ask for owner decisions when end-state/product/economy/naming/irreversible choices genuinely need them.

---

# Safety / open-platform discussion rule

Capability exploration should be technically frank without pretending unavailable managed facilitation means technical impossibility.

Use:
- Beast-managed;
- compatible;
- Owner Space;
- outside managed facilitation.

Where Beast does not ship a purpose-built workflow, preserve/document generic extension/provider/dependency boundaries so owners can understand how they may fill gaps on their own Linux machine where appropriate.

---

# Important preservation records

- `docs/Beastagotchi_Toolbelt_Candidate_Idea_Ledger_2026-09-26.md`
- `docs/Beastagotchi_Full_Not_Cluttered_Reconciliation_2026-09-26.md`
- `docs/Beastagotchi_Fresh_Eyes_Epiphany_Review_2026-09-26.md`
- `docs/Beastagotchi_PostFreshEyes_Owner_Feedback_Addendum_2026-09-26.md`
- `docs/Beastagotchi_PreImplementation_Discussion_Queue_2026-09-25.md`
- this checkpoint file

Important recent preservation commits:
- `eaa4cbfda9774e77e2f86b5ec918a1d566b6c743` — fresh-eyes review
- `abb411185a516eb1b4a6c1022dbc7074730fa06f` — queue marked fresh-eyes complete
- `1cad3ba34128dde022f1dc6e5c2a29d0bebb3ffe` — expanded remaining discussion queue
- `99cebed053e1ba44aa36f80028daa9c3f674785b` — owner-feedback addendum

Earlier Sandbox / Toolbelt / reconciliation commits remain part of branch history.

---

# Exact resume point

**Do not resume full implementation yet.**

Next conversation/task:

> **Doctor deep-dive / jam session — define the one-stop machine-wide Doctor.**

After Doctor, proceed through Capability Expansion -> cross-layer jam -> AI -> Monster/perception/expression -> final reconciliation -> implementation.
