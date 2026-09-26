# Beastagotchi Pre-Implementation Discussion Queue

**Date:** 2026-09-25  
**Updated:** 2026-09-26  
**Status:** owner-requested discussion checkpoints before full architecture implementation resumes

## Current status

- **1. Correctness tranche:** complete for the bounded pre-discussion block.
- **2. Product facets / Toolbelt:** discussion complete; ideas preserved, consolidated and owner-prioritized.
- **3. Windows Beast Sandbox:** direction selected and preserved (WSL2 + guided Docker + Beast-native virtual providers + SSH physical Pi + record/replay; QEMU not required).
- **3A. “Full but not cluttered” reconciliation:** complete and preserved.
- **4. Final whole-project fresh-eyes / epiphany review:** complete and preserved as candidate findings.
- **4A. Owner feedback on fresh-eyes review:** complete enough to establish important corrections; preserved in a dedicated addendum.
- **5. Doctor deep-dive / jam session:** **NEXT.**
- **6. Capability Expansion Pass:** pending.
- **7. Cross-layer X + Y => Z jam session:** pending.
- **8. AI role/capability discussion:** pending; AI remains optional, not assumed.
- **9. Monster / breeding / perception / expression jam:** pending.
- **10. Final reconciliation:** pending — classify approved / modify / reserve / reject and fold approved decisions into contracts/roadmap.
- **11. Resume implementation:** remains paused until these pre-building discussions are reconciled.

---

## 1. Complete the already-started correctness tranche — COMPLETE

Do not leave partially-started foundation work hanging. Finish/verify the bounded correctness work already underway before reopening broad product ideation.

## 2. Beastagotchi product facets / Toolbelt — COMPLETE FOR THIS DISCUSSION PHASE

Step back from pages/features and identify the major user-facing facets of Beastagotchi as a whole.

Resulting records include:
- seven provisional product facets;
- Toolbelt taxonomy (Instrument / Tool / Procedure / Workspace);
- accepted 1–15 Toolbelt candidate priority order;
- singular-Doctor rule;
- Owner Space / managed-boundary direction;
- one-System-Graph consolidation;
- adjacent-ecosystem directions;
- “full but not cluttered” reconciliation.

Key principle:

> Broad capability does not require broad primary navigation.

## 3. Windows Beast Sandbox — DIRECTION SELECTED

Selected direction:
- WSL2 as the primary everyday Beast Sandbox;
- Docker accepted when hidden behind simple BeastLab controls for disposable/destructive tests;
- Beast-native virtual hardware providers inside WSL;
- SSH-connected physical Pi as a first-class real-hardware validation path;
- record/replay strongly selected, initially allowing manual file transfer;
- QEMU explicitly not required unless a future concrete need justifies reopening the discussion.

Sandbox remains a **development/test aid**, not a requirement for Beastagotchi itself.

Physical Pi remains authoritative for RF/monitor mode, exact Pi hardware/kernel/device-tree, SPI TFT, GPIO/touch timing and physical thermal/performance validation.

## 3A. Full-but-not-cluttered reconciliation — COMPLETE

Preserve:
- one Doctor, many specialties;
- one System Graph, many views;
- one managed mutation stack (Action -> Transaction -> Procedure);
- coherent capability/provider lifecycle;
- Workspaces rather than mini-app proliferation;
- Search/History/Automation/Support as cross-cutting infrastructure;
- curated/contextual surfacing rather than app-drawer-first UX.

See `docs/Beastagotchi_Full_Not_Cluttered_Reconciliation_2026-09-26.md`.

## 4. Final whole-project fresh-eyes / epiphany review — COMPLETE

Owner explicitly authorized the pass on 2026-09-26.

Findings preserved at:

`docs/Beastagotchi_Fresh_Eyes_Epiphany_Review_2026-09-26.md`

Important status note: these are **candidate findings**, not silently approved canon.

Strong candidates included:
- reliable time semantics + causal/correlation context;
- explicit identity scopes + persistent-state custody descriptors;
- Incident -> Doctor -> Procedure -> replay learning loop;
- Shadow Beast as optional Sandbox concept;
- Universal Inspect / Why?;
- Chronicle + Homecoming debrief;
- composable context axes;
- exact render provenance + browser/visual regression;
- managed egress preview;
- RF/sensor capability universe + perception/expression channels.

## 4A. Owner feedback / correction after fresh-eyes review — COMPLETE ENOUGH TO SET NEXT ORDER

The owner accepted several foundation findings but correctly identified that the fresh-eyes pass over-weighted observability/diagnostics and under-delivered on **new capability expansion**.

Important corrections:

### Doctor is the one-stop diagnostic/repair system

Do not turn logs, probes, command outputs or subsystems into separate diagnostic products.

Doctor should be able to access/query/inspect as much machine truth as practical across:
- board/SoC/RAM/firmware/kernel/drivers/device tree;
- storage/filesystems/mounts/permissions;
- systemd/services/processes/journal;
- packages/libraries/runtimes/dependencies;
- networking/Wi-Fi/Bluetooth/routes/DNS/sockets/regulatory state;
- USB/GPIO/SPI/I2C/serial and attached hardware;
- display/framebuffer/DRM/touch/device configuration;
- power/thermal/throttling/telemetry;
- Pwnagotchi/Bettercap/config/plugins/capture pipeline;
- Beastagotchi Core/UI/Studio/Packs/providers/Actions/Transactions/Procedures/history;
- relevant files/file trees/configuration and other bounded probes.

`debug`/logs are evidence sources. Doctor is the interpreter/fixer.

Desired model to discuss:

> Machine Census -> Probe Library -> Knowledge Library/Search -> Diagnosis -> Fix -> Verify -> Learn

Also preserve owner idea:

> **Doctor finds it -> uses it -> puts it back.**

Where a missing diagnostic/helper utility is needed, Doctor may eventually be able to identify, safely acquire/stage, use and optionally remove it through the normal managed mutation/authority path.

### Doctor knowledge should span local/offline/online sources

Potential knowledge inputs:
- Beastagotchi docs;
- Pwnagotchi/Jayofelony docs;
- Bettercap docs;
- Linux/man pages;
- Raspberry Pi docs;
- hardware manuals/datasheets;
- plugin README/how-to material;
- owner-added notes/text/PDF/wiki material;
- previous successful Doctor resolutions;
- current online docs/GitHub/issues/forums/web when available and permitted.

Do not blindly execute Internet advice. Map it against the specific Beast's actual state and turn applicable remedies into bounded plans/Procedures.

### Recovery ladder remains broad

Preserve the intended spectrum from small logical checkpoints/Known-Good through recovery backups/rebuild manifests and ultimately full SD-card image/mirror workflows where appropriate.

Current implementation is not yet the entire finished ladder.

### Sandbox/Shadow Beast remain optional development aids

They can improve validation but Beastagotchi itself must not depend on them. SSH/manual physical validation remains valid fallback.

### Universal Inspect / Why? remains optional/low-cost

Only worthwhile if it is a contextual drill-down into existing truth, Doctor/history/System Graph—not another standalone inspector/log product.

### Chronicle only earns its place if reused broadly

Chronicle should correlate existing authoritative stores; never become another giant history/log database.

Potential consumers:
- Companion/life history;
- Homecoming debrief;
- Doctor;
- Search;
- Hall of Legends;
- lineage/progression;
- Expeditions.

### Homecoming / Expedition debrief needs deeper product design

Potential truthful inputs include all pertinent information Beast/Pwnagotchi can access for that session, subject to owner privacy/retention policy:
- GPS route/distance/time;
- AP/network discoveries;
- channel/radio activity/coverage;
- Pwnagotchi/Bettercap session/epoch data;
- captures/handshakes/peers;
- PeerDex encounters;
- progression/achievement/rare-event changes;
- health/incidents;
- other active provider observations.

Desired visual direction includes real local/offline mapping:
- real route polyline;
- plotted observation/discovery points;
- visually distinct classes/types;
- optional coverage/heat/radar/provider overlays where appropriate;
- tap/inspect summaries;
- attractive visual summaries rather than forcing the owner to read raw lines.

Derived debrief reports should **not** automatically accumulate forever. Candidate behavior:
- generate/view on demand or at Homecoming;
- discard rendered report by default after viewing;
- owner may snapshot current page;
- owner may save/export/share the full debrief;
- underlying source Expedition/history retention remains separately governed.

### Home Base is already broader than update staging

Home Base/trusted network/external power should remain the preferred context for owner-approved queued work, including potentially:
- user uploads/downloads;
- content/Packs;
- offline docs/manuals/wiki material;
- offline maps/data;
- backup replication;
- NAS/library sync;
- exports;
- update download/staging;
- package/software acquisition;
- indexes/media/content preparation;
- future optional models/large assets.

Use policy: automatic / ask / manual as appropriate. Do not silently apply consequential changes.

### Search target is all-encompassing/federated

Desired Search should eventually be able to search, as technically possible and policy-allowed:
- local Beast state/settings/capabilities/apps/hardware/files;
- offline docs/manuals/wiki/text/PDF/datasheet/help material;
- owner-added library material;
- history/Expeditions/Memories/Incidents/Doctor cases;
- Packs/Procedures/Tools;
- external/current Internet/web/documentation/GitHub/forum sources when online.

Exact architecture still open for discussion. Prefer one federated Search service rather than separate search silos.

### AI remains an open question

Do not assume AI belongs, and do not arbitrarily confine it to one role if it is eventually used.

Dedicated discussion must explore possible value, cost and boundaries across:
- creature/personality interaction;
- Doctor reasoning/explanation;
- natural-language operation;
- Search/Field Library;
- planning/Procedure authoring;
- Homecoming/debrief narration;
- Studio development/content creation;
- voice/audio;
- semantic correlation;
- local vs remote models;
- bounded tool/Action use.

Deterministic Core truth/authority must remain distinct from probabilistic AI output.

### Monster unlock concept should be revisited

Do not lock fundamental hardware/software capabilities behind breeding/progression.

Future jam should explore whether breeding/lineage unlocks instead affect:
- instincts;
- talents;
- inherited behaviors;
- affinities;
- cross-capability combinations;
- special Procedures/Missions;
- expression styles;
- discovery mechanics;
- rare interactions;
- other identity/experience layers.

Perception <-> Expression is a strong concept to preserve:
- hardware/providers give the Beast new senses;
- displays/LED/audio/haptics/etc. give it new ways to express/react;
- Choreography targets capabilities with graceful fallback.

---

## 5. Doctor deep-dive / jam session — NEXT

Purpose: define Doctor as a signature Beastagotchi capability, not a log viewer.

Discussion targets:
- comprehensive Machine Census;
- static vs boot-time vs on-demand/deep probes;
- Probe Library categories and dependencies;
- automatic fault-family selection of relevant probe blocks;
- escalation when initial probes are inconclusive;
- Knowledge Library and federated search use;
- known fixes/workarounds/how-to material;
- Doctor learning from previous successful resolutions;
- safe automatic repair scope;
- when/why user consent is required;
- `find it -> use it -> put it back` helper/tool acquisition;
- verification/rollback;
- clear owner guidance for anything Doctor cannot complete automatically;
- how Doctor uses System Graph, Actions, Transactions, Procedures, Incident history and Known-Good without exposing those as separate diagnostic clutter.

Desired owner-facing promise:

> **Something is wrong with Pwnagotchi or Beastagotchi? Start with Doctor.**

## 6. Capability Expansion Pass — PENDING

This pass must explicitly answer:

> **What new things can Beastagotchi actually DO because it sits on top of Pwnagotchi + Linux + a Raspberry Pi + Beast architecture?**

Do not count “another log,” “another graph,” or “another diagnostic page” as the primary answer.

Review Beast as stacked layers:

1. physical Pi / board / attached hardware;
2. Linux/kernel/system services;
3. networking/radios/USB/Bluetooth/GPIO/SPI/I2C/serial/sensors;
4. Pwnagotchi + Bettercap;
5. Beast Core/contracts;
6. Tools/Procedures/Providers/extensions;
7. UI/Experiences/creature;
8. phone/desktop/Home Base/local network/other devices;
9. optional Internet/external services.

At every layer ask:
- what can we access?
- what can we add?
- what useful software/packages/libraries/services exist?
- what hardware expands capability?
- what belongs managed vs compatible vs Owner Space?
- what dependencies are needed?
- can Beast detect missing dependencies and explain/install them?
- what are the practical “must have,” “nice to have,” and weird-but-useful tools?
- what becomes possible when this layer combines with another?

Do not unnecessarily narrow the scan because of safety boundaries. Where Beast should not ship/facilitate a specific workflow, document the managed boundary and identify how the open platform can accommodate owner-supplied capability through generic providers/extensions where appropriate.

## 7. Cross-layer X + Y => Z jam session — PENDING

Run as an interactive owner/assistant creative session rather than a finished report.

Desired style:
- concrete idea;
- why the underlying layers make it possible;
- what the user gains;
- dependencies/hardware/software;
- what can be automatic vs optional;
- surprising combinations;
- questions/prompts that invite owner riffs.

Example pattern:
- GPS + Expedition + offline maps + Pwnagotchi observations -> real field map/history;
- sensors + creature + TFT/LED/audio -> perception/expression;
- Home Base + queued work + NAS + wall power -> field-to-home workflow;
- USB discovery + capability registry + Depot -> plug in hardware and immediately understand what new abilities it enables;
- Doctor + dependency catalog + knowledge search -> safely obtain/use/remove a needed diagnostic helper.

Ideas can be wild; later reconciliation will filter them.

## 8. AI role/capability discussion — PENDING

AI is optional.

Explore broadly before deciding:
- whether AI earns any place in Beastagotchi;
- local vs remote/hybrid models;
- resource/cost/privacy/offline implications;
- creature conversation/personality;
- Search/knowledge synthesis;
- Doctor copilot;
- natural-language operation;
- voice;
- Studio/development aid;
- Procedure/automation authoring;
- semantic/history correlation;
- content/Experience creation;
- bounded use of the same Operator Tools/Actions as other clients.

Do not let AI bypass canonical truth, authority or transaction safety.

## 9. Monster / breeding / perception / expression jam — PENDING

Revisit the original “Monster unlocks capabilities” concept.

Current direction:
- fundamental owner-accessible machine capabilities should normally **not** be progression-locked;
- breeding/lineage may instead unlock identity/behavior/combinations/Instinct-like traits;
- perception/expression connections are promising and should be explored creatively.

No reward odds/economy/end-state values should be frozen without owner input at the appropriate time.

## 10. Final reconciliation — PENDING

After discussions 5–9:

Classify meaningful proposals as:
- **APPROVE**;
- **MODIFY**;
- **RESERVE/LATER**;
- **REJECT**.

Then:
- update architecture contracts;
- update migration ledger;
- update roadmap/release horizon;
- update Toolbelt/capability ledgers;
- preserve any future ideas intentionally deferred;
- ensure “full but not cluttered” still holds;
- identify foundation changes that must precede feature work.

## 11. Resume implementation — PAUSED UNTIL RECONCILIATION

Only after the discussion queue above is completed/reconciled should full architecture implementation resume.

Implementation should continue in meaningful test-backed tranches, preserving:
- no flag-day rewrite;
- real/live data over fake data;
- unknown remains unknown;
- synthetic state explicitly labeled;
- owner sovereignty;
- Pwnagotchi/Bettercap remain protected underlying engines;
- physical Gate 1 UI acceptance remains honest and separate.
