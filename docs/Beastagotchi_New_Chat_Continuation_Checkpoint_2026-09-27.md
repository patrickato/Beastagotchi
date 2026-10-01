# Beastagotchi / Monstergotchi — New Chat Continuation Checkpoint

**Date:** 2026-09-27  
**Status:** canonical handoff for continuing in a fresh ChatGPT conversation  
**Repository:** `patrickato/Beastagotchi`  
**Preservation branch:** `openai/v019-visual-reference-archive`

---

# START HERE IN A NEW CHAT

The pre-build design/reconciliation phase is now complete enough to build from.

The immediate next task is **not another brainstorm**. Resume from the current release truth gate:

> **Return to `v0.19-unified-experience` Gate 1, finish the real generated-renderer acceptance, then run the physical Pi/TFT/touch/thermal/framebuffer acceptance session.**

Do **not** make the newly approved AI/security/hardware expansion architecture block v0.19 closure. After v0.19 closes, continue the new architecture foundation using PR #22 as the starting implementation spine rather than rewriting it.

Current post-v0.19 implementation sequence:

**A. correctness/contracts → B. runtime/scheduler/arbitration → C. Providers/Abilities/System Graph → D. Pwnagotchi/Bettercap truth bridge → E. Scope/Evidence/Capture Intelligence → F. Doctor v1 → G. Tool Catalog/Help/Search → H. Security Workspace v1 → I. presentation substrate → J. optional Broad AI → K. Creature perception/expression.**

The next hardware-hacking/security-crossover research batch is deliberately **deferred until after release**.

---

# 1. Current branch / PR state

## Stable
- `main` = v0.18.1 reference/rollback baseline.

## Active release branch
- `v0.19-unified-experience`
- Draft PR #9: **open, unmerged**.
- Gate 1 remains the current release truth gate.

## Architecture implementation branch
- `openai/v019-architecture-foundation-tranche1`
- Draft PR #22: **open, unmerged**.
- Existing foundation is valid and should be retained.

PR #22 already contains:
- shared stateful-manager ownership;
- thread-safe SQLite runtime ownership;
- restart-safe/private bridge state;
- canonical presentation preference store;
- typed registry substrate;
- partial ActionSpec migration via `RegisteredActionBroker`;
- Signal/Event registry foundations;
- shared durable Transaction Engine;
- Pack install adapted through the Transaction Engine;
- migration ledger + regression tests.

Known remaining debt on PR #22:
- many actions still unmigrated;
- authority metadata not fully centralized;
- database migration/version discipline needs more work;
- EventBus typed/drop observability later;
- ModuleRuntime/Scheduler not yet implemented;
- presentation surface stack not yet migrated;
- physical validation still required where marked.

---

# 2. Canonical architecture direction

The following architecture decisions are approved.

## Hard semantic kernel / wild ecosystem
- Deterministic factual core.
- Mature tools are integrated/wrapped/orchestrated rather than unnecessarily rebuilt.
- Owner Space remains real Linux/root/CLI territory.
- Guided workflows never remove Full Tool access.
- Unknown remains unknown.
- Simulated remains labeled simulated.
- Real/live data is preferred over demo/fake data.

## One conceptual execution model

`Truth → Capability → Action → Transaction → Procedure → Doctor → History → Presentation`

Singular systems:
- one Doctor;
- one System Graph;
- one Action/Transaction/Procedure model;
- one capability/provider lifecycle;
- one presentation platform;
- one content/storage model;
- one owner customization/provenance history.

## Full-but-not-cluttered product rule

A concept earns a top-level product identity only when it serves a distinct user job. Otherwise it becomes a view, Tool, Instrument, Procedure, Provider, Workspace component, diagnostic pack, Surface, or query over an existing system.

Primary facets remain:
1. Companion / Life
2. Instrument / Observe
3. Operate / Toolbelt
4. Explore / Field
5. Create / Workshop
6. Connect / Exchange
7. Steward / Care

Cross-cutting:
- Universal Search;
- Automation;
- Support Bundle;
- History / Journal.

---

# 3. Doctor / Broad AI / Creature split — KEEP THIS CHANGE

This was explicitly approved and should not be collapsed back together.

## Doctor
Doctor stays the specialist deterministic clinician/caretaker.

Doctor owns:
- Machine Census;
- vital signs;
- Probe Blocks;
- evidence;
- competing hypotheses;
- confidence;
- Known-Good / What Changed?;
- repair planning;
- Transactions/rollback;
- functional verification;
- Doctor knowledge/fleet evidence.

Doctor works fully with AI disabled.

## Broad AI
Broad AI is a **separate optional conversational assistant/orchestrator**.

It can call:
- Doctor;
- Search;
- Abilities;
- Software/Security Catalog;
- Security Workspace;
- managed Actions/Procedures;
- Full Tool handoffs;
- Home Base.

Mental model:
> **Broad AI = “Ask Beast anything.”**

The model may live on:
- Pi where practical;
- paired phone;
- Home Base/PC;
- self-hosted local model;
- optional cloud provider.

Weak boards such as Pi Zero 2 W remain fully functional without local inference.

## Creature
Creature remains a third distinct identity:
- personality;
- progression;
- perception;
- expression;
- lineage;
- memories;
- relationships.

Creature never becomes the factual authority.

Approved mental model:
> **Broad AI = general conversational assistant. Doctor = specialist clinician. Creature = living identity.**

---

# 4. Doctor direction

One Doctor covers:
- Pi/board/hardware;
- Linux/kernel/drivers/device tree/services/packages/filesystems/networking;
- display/touch/SPI/I2C/GPIO/USB/Bluetooth/audio;
- Pwnagotchi/Bettercap/plugins/capture pipeline;
- Beast Core/UI/Studio/Packs/providers/services/history;
- attached hardware and managed ecosystem.

Reasoning model:

`Machine Census → symptom → dependency path → competing hypotheses → targeted probes → evidence/confidence → repair plan → snapshot/rollback → repair → functional verification → cleanup → learn`

Principles:
- **Running != working.**
- **Doctor finds it → uses it → puts it back.**
- Doctor investigates aggressively, repairs conservatively, and asks intelligently.
- Healthy systems teach normal; failures teach what breaks.
- Fleet knowledge never replaces patient-specific evidence.

Confidence vocabulary:
- Possible
- Supported
- Likely
- Strongly supported
- Confirmed
- Contradicted

Doctor presentation remains a skin/Experience, not the capability itself.

---

# 5. Search / knowledge / software model

Federated Search should span:
- local state/capabilities/settings/apps;
- local files;
- Doctor knowledge;
- offline manuals/wiki/PDF/TXT/datasheets;
- Chronicle/Expeditions/history;
- current web search;
- GitHub/project docs;
- Global Doctor;
- provider/search-engine sources.

Search Broker can serve User, Doctor, Guided Software, Studio, and Broad AI.

Useful mature backends/candidates:
- SQLite FTS;
- Recoll/Xapian;
- ripgrep;
- Kiwix/ZIM;
- MapLibre + PMTiles;
- optional SearXNG/Home Base.

Guided Software rule:
> **Make complex software approachable without hiding, crippling, or replacing the real software.**

Typical ladder:
1. Focused / Guided
2. Advanced Guided
3. Full Tool
4. Owner Space/raw CLI/config/root

---

# 6. Providers / Abilities / resource model

One hardware/software primitive may support many experiences.

Examples:
- RTL-SDR → FM, rtl_433, ADS-B, AIS, satellite, Spectrum Lab;
- GPS → maps, Expedition, SKY, SDR presets, Homecoming;
- audio output → alerts + radio + creature expression;
- offline corpus → Doctor + Search + tutorials + Studio.

Abilities should describe what the current machine can actually do now.

Candidate status vocabulary:
- READY
- AVAILABLE
- FULL TOOL
- OWNER SPACE
- NEEDS HARDWARE
- NEEDS SOFTWARE
- CONTEXT/LICENSING REQUIRED
- conflicting/unavailable where appropriate

Resource conflicts require explicit arbitration/lease/sequence rather than hidden competition.

---

# 7. Security / Pentest deep-dive — PRE-RELEASE DISCUSSION CLOSED

The security discussion was intentionally inserted after the first reconciliation and before final architecture freeze.

Approved operating hierarchy:

1. **Beast-managed**
2. **Authorized / Guided Lab**
3. **Full Tool**
4. **Owner Space**

Hard-boundary operations are not turned into first-party Beast automation, but Beast does not pretend the underlying technology does not exist.

Core security direction:
- preserve Pwnagotchi/Bettercap as genuine wireless-security foundations;
- Security Workspace;
- Pwnagotchi Truth Cockpit;
- radio/adapter qualification;
- Capture Intelligence;
- authorized assessment sessions;
- packet/802.11 education;
- known-network security baseline/drift;
- deauth/rogue/incident detection;
- topology/service discovery for owned/authorized networks;
- Home Base heavy analysis;
- reporting/remediation/re-test;
- lab/CTF learning environments;
- mature tools integrated rather than cloned.

Do **not** blindly add Kali repositories to the Jayofelony base. Prefer Debian/RPi packages, upstream releases, isolated environments, containers where appropriate, and Home Base/VM for heavy tools.

---

# 8. Security ecosystem architecture promoted

The following connective architecture is approved and should survive beyond individual tool choices:

## Tool Adapter Manifest
Machine-readable metadata for mature tools:
- detection/install method;
- help/man entry points;
- input/output formats/APIs;
- resource/hardware requirements;
- permission/risk classification;
- Guided/Lab/Full Tool/Owner Space boundaries;
- Home Base suitability;
- provenance/license.

## Assessment Scope Passport
Shared scope object across security tools:
- authorized hosts/APs/devices/lab environments;
- session/engagement identity;
- shared provenance for resulting artifacts/findings.

## Security Evidence Bus
Normalize evidence without replacing raw truth:

`Tool → raw evidence + normalized observation/finding → Search / Chronicle / Doctor / AI / Report`

Examples:
- Nmap → Service Observation
- Nuclei → Security Finding
- Pwnagotchi → Capture Evidence
- Kismet → Radio Observation
- Suricata → Incident Signal
- MobSF → App Finding
- YARA-X → File Finding

## Gadget Dock / Hardware Capability Portal
Plug supported hardware in and Beast should answer:
- what is it?
- firmware/client readiness?
- what abilities were added?
- what can I do now?

## Security Lab Capsules
Reusable controlled learning environments containing:
- in-scope vulnerable target;
- isolation;
- objective;
- reset/snapshot;
- Help/Learn material;
- cleanup.

## Repo Intake / Capability Harvest Pipeline
Given an interesting repo, inspect:
- license;
- dependencies;
- language/architecture support;
- hardware;
- CLI/API/help;
- I/O formats;
- network/resource behavior;
- then propose Guided/Provider/Full Tool/Home Base/boundary treatment.

## Security Capability Packs
Examples:
- Wireless Analysis
- Web/App Lab
- Firmware/RE
- Hardware Debug
- Forensics
- Defensive Sentinel
- CAN/Industrial
- Mobile Analysis
- Security Range

The next hardware-hacking/security-crossover idea-search batch is **post-release**.

---

# 9. Real projects/concepts approved as strong references/integrations

Approved/useful references include:
- Bjorn architecture ideas;
- P4wnP1 A.L.O.A. neutral USB gadget/recovery primitives;
- ESP32 Marauder / Bruce as external senses/coprocessor reference;
- Kismet as structured radio Provider candidate;
- Zeek + Arkime for Home Base Security Time Machine;
- OpenCanary Sentinel Mode;
- Lynis Doctor security instrument;
- RaspAP concepts for scoped lab/network roles;
- Cockpit as Guided UI + real Linux precedent;
- Node-RED as optional advanced automation Full Tool;
- Home Assistant provider/entity/event/action architectural precedent;
- Binwalk Firmware Autopsy;
- Nuclei vulnerability-check integration;
- ZAP/mitmproxy application traffic lab;
- MobSF mobile analysis Home Base provider;
- Ghidra/Cutter Home Base RE handoff;
- Proxmark3/ChameleonUltra RFID/NFC family;
- KillerBee/Kismet Zigbee/802.15.4;
- Ubertooth Bluetooth specialist Provider;
- GreatFET/Facedancer USB Hardware Lab;
- OpenCanary/Cowrie/T-Pot deception ladder;
- Suricata Home Base packet-security analysis;
- osquery + YARA-X + Sigma defensive-query ecosystem;
- Juice Shop/WebGoat/CTFd Security Range;
- Syft/Trivy SBOM/software X-Ray;
- Sigstore/Cosign artifact trust/provenance;
- Gitleaks/secret-leak guard;
- Semgrep Studio/repo-intake analyzer;
- testssl.sh TLS inspector;
- sigrok/PulseView Logic Analyzer Lab;
- OpenOCD/flashrom MCU/firmware debug/recovery;
- SocketCAN/can-utils CAN Lab;
- Sleuth Kit/Volatility/Timesketch forensics;
- Greenbone/OpenVAS Home Base vulnerability provider;
- Bettercap caplets → Beast Procedures where appropriate;
- Bettercap REST/event data → structured Provider/truth source.

Wazuh remains optional. MISP/OpenCTI remain reserved until a real need appears. Velociraptor is a useful DFIR reference/Home Base optional tool, not a required dependency.

---

# 10. Pwnagotchi custom-plugins — approved candidates

These are real Pwnagotchi `custom-plugins`, not generic Beast extensions.

## High-priority approved

### `beast-bridge`
- subscribes to Pwnagotchi lifecycle/events;
- emits normalized local structured events to Beast;
- keeps Pwnagotchi independently usable;
- intended to cover handshakes, epochs, AP observations, channel activity, association/deauth events, peers, session/UI context.

### `capture-ledger`
- durable metadata/sidecar for captures;
- timestamp, interface/radio, channel, AP/client context, session, optional location/freshness, file hash, duplicate relation.

### `radio-vitals`
- lightweight truth about monitor-radio health;
- interface existence;
- channel/hop behavior;
- frame-reception evidence;
- radio resets/failures;
- capture-pipeline health.

Additional ideas remain candidates, not equal-priority commitments:
- known-network-watch;
- homecoming-queue;
- peer-journal.

Do **not** put Doctor, Broad AI, Search, Security Workspace, Hardware Bench, maps, generic Automation, Home Base or full Linux applications inside Pwnagotchi custom-plugins.

Plugin manifests/sidecars are approved as a Beast layer for compatibility/config/dependency/trust/provenance metadata.

---

# 11. Monster / perception / expression decisions

Approved rule:
> **Beast senses truthfully. The creature interprets those senses through traits, memory, lineage and context, then expresses that interpretation through whatever outputs exist. Breeding changes interpretation/expression, not fundamental machine capability.**

Foundational Monster layer:
- deterministic identity/state;
- traits/affinities;
- structured progression/events/memory;
- perception feed from Beast Signals/Events;
- semantic expression states;
- TFT fallback expression;
- owner controls;
- strict truth boundary.

Later/reserved:
- deeper genetics;
- rare mutation chains;
- complex morphology;
- cross-device breeding;
- richer AI dialogue;
- extended social/fleet mechanics.

AI is optional for expression/narration and never required for progression, rare events, breeding or unlocks.

---

# 12. Secrets / privacy

Standing rule:
> **Catalog everything important; store secrets securely; redact them from ordinary views/logs; reveal them to the owner on explicit request.**

Refinement:
> **Collect richly where justified locally; share minimally and intentionally.**

Global Doctor/support bundles/ordinary screenshots/logs must not leak secret values.

Broad AI external routing follows owner privacy/context-routing policy.

---

# 13. Beast Sandbox

Approved direction:
- WSL2 primary everyday Sandbox;
- Docker disposable/destructive cells;
- Beast-native virtual Providers;
- SSH physical Pi as first-class complement;
- Record/Replay strongly approved;
- QEMU deferred unless uniquely needed.

Virtual Providers should eventually include radio, TFT, touch, GPS, battery, thermal, USB, GPIO, sensors and storage where useful.

Sandbox/Shadow Beast is dev/testing support, not runtime dependency.

---

# 14. Current v0.19 truth / immediate next work

Current source/package preparation is mature, but Gate 1 is **not physically accepted**.

Do not mistake CI/source/gallery evidence for real hardware acceptance.

Immediate sequence:
1. inspect the current generated 480×320 renderer / latest accepted visual direction;
2. obtain/confirm owner off-screen acceptance of the actual generated renderer;
3. stage the exact tested artifact on the reference Pi;
4. run the bounded TFT/touch/QR/glare/smoothness/thermal/framebuffer session;
5. fix only physical-only findings;
6. explicitly close Gate 1;
7. decide v0.19 branch promotion/release boundary.

Do not expand the release target with the entire new architecture before this gate closes.

---

# 15. Post-v0.19 architecture implementation order

Canonical sequence from the new roadmap:

### A. Correctness / contracts
- continue Action/Transaction migration;
- central authority/risk metadata;
- DB schema/user_version discipline;
- registry/contract cleanup.

### B. Runtime / scheduler / arbitration
- ModuleRuntime;
- Scheduler;
- shared Task/Progress model;
- hardware/resource leases/arbitration.

### C. Providers / Abilities / System Graph
- Provider registry/lifecycle;
- dynamic Abilities;
- dependency/conflict graph;
- Device Passport integration.

### D. Pwnagotchi / Bettercap truth bridge
- promote/refine `beast-bridge`;
- structured Bettercap Provider;
- `radio-vitals`;
- preserve Pwnagotchi independence.

### E. Scope / Evidence / Capture Intelligence
- Assessment Scope Passport;
- evidence/observation/finding schema;
- `capture-ledger`;
- capture quality/provenance/dedup/session linkage.

### F. Doctor v1
- Machine Census;
- Vital Signs;
- Probe Blocks;
- Known-Good/What Changed?;
- evidence/confidence/repair/verify lifecycle.

### G. Tool Catalog / Help / Search
- Tool Adapter Manifests;
- built-in `--help`/man/info/docs hooks;
- Software/Security Catalog;
- federated Search.

### H. Security Workspace v1
- radio/capture/session truth;
- authorized assessment sessions;
- topology/service observations;
- reporting/re-test.

### I. Presentation substrate
- SurfaceRegistry / SurfaceStack / InputRouter / NavigationController;
- maintain preview fidelity and actual physical truth.

### J. Optional Broad AI
- provider-neutral model interface;
- privacy/context routing;
- structured access to Beast truth;
- managed Action bridge;
- no unrestricted hidden root authority.

### K. Creature perception / expression
- consume real Signals/Events;
- semantic expression states;
- no fake facts.

---

# 16. Key canonical docs created in this discussion phase

Most important recent docs on `openai/v019-visual-reference-archive`:

- `docs/Beastagotchi_Final_PreBuild_Reconciliation_2026-09-27.md`
- `docs/Beastagotchi_Security_Pentest_Deep_Dive_Batch_01_2026-09-27.md`
- `docs/Beastagotchi_Security_Pentest_Kali_Integration_Matrix_2026-09-27.md`
- `docs/Beastagotchi_Security_Ecosystem_Plugins_Flipper_and_Broad_AI_Addendum_2026-09-27.md`
- `docs/Beastagotchi_Current_Discussion_Queue_2026-09-27_Security_Deep_Dive.md`
- `docs/Beastagotchi_Security_Direct_Examples_AI_Doctor_and_Pwnagotchi_Plugin_Addendum_2026-09-27.md`
- `docs/Beastagotchi_Security_Ecosystem_Matrix_Batch_02_2026-09-27.md`
- `docs/Beastagotchi_Security_Ecosystem_Batch_02_Promotion_Decisions_2026-09-27.md`
- `docs/Beastagotchi_Security_Ecosystem_Matrix_Batch_03_2026-09-27.md`
- `docs/Beastagotchi_Security_Ecosystem_Batch_03_Promotion_Decisions_2026-09-27.md`
- `docs/Beastagotchi_Canonical_Architecture_Contracts_2026-09-27.md`
- `docs/Beastagotchi_PostReconciliation_Build_Order_and_Roadmap_2026-09-27.md`

Important commits from the latest sequence:
- Security direct examples / AI/Doctor / plugins: `a8f52f14f06fa4fbac9e1586cd2096fb72b9ae34`
- Security Matrix Batch 02: `21669a828fc757013448bbbcf3d95b208fcaa104`
- Batch 02 promotion decisions: `5c1d6bfe06a604624d367899dfd9e33f7ba7308c`
- Batch 03 research: `9ab3092c96132ed673d79906635edc48dda074ef`
- Batch 03 promotion decisions: `5767d14adc06394b04c6362b3216345e179fad20`
- Canonical architecture contracts: `b673c5b95ff8c74908e14531f7d12b9265395ad5`
- Post-reconciliation build order/roadmap: `d8047f1b73a3a1de5010b7d46d4cfa6cefadf8dc`

Earlier comprehensive continuity remains in:
- `docs/Beastagotchi_PreImplementation_Continuity_Checkpoint_2026-09-26.md`
- `docs/Beastagotchi_Capability_Expansion_and_Doctor_Continuity_Checkpoint_2026-09-26.md`
- `docs/Beastagotchi_Doctor_Jam_2026-09-26.md`
- `docs/Beastagotchi_AI_Doctor_Architecture_Direction_2026-09-27.md`
- `docs/Beastagotchi_Monster_Breeding_Perception_Expression_Jam_2026-09-27.md`

---

# 17. Conversation flow / discussion state

Correct historical order:
1. Doctor deep-dive — complete
2. Capability Expansion — complete enough
3. Cross-layer X+Y=Z jam — complete enough
4. AI discussion — complete; later amended into Broad AI / Doctor / Creature split
5. Monster / breeding / perception / expression jam — complete
6. First approve/modify/reserve/reject reconciliation — complete
7. Security/Pentest/Pwnagotchi deep-dive — complete for pre-release planning
8. Security reconciliation/promotion cuts — complete
9. Canonical architecture rewrite — complete
10. Build order / roadmap rewrite — complete
11. **NEXT: return to v0.19 Gate 1 and resume release-closing work**

Post-release:
- deferred hardware-hacking/security crossover expansion;
- deeper Security Ecosystem Matrix work;
- richer plugin/repo harvest;
- broader hardware labs;
- advanced breeding/social/AI depth.

---

# 18. Interaction / collaboration rules worth carrying into the next chat

- Keep progress visible during tool-heavy work; do not disappear for long silent runs.
- Prefer meaningful development tranches, but report short checkpoints while working.
- Ask owner input for meaningful product/end-state/visual/reward/public-contract decisions, not every minor implementation detail.
- Proactively surface worthwhile ideas, especially unusual X+Y=Z / “holy shit” combinations.
- Preserve candidate ideas while clearly distinguishing them from approved canon.
- Do not invent needless terminology detached from the owner’s wording.
- Prefer mature-tool integration over rebuilding existing software.
- Push the Pi platform hard, but do not make Pi 5 resources mandatory where Zero 2 W / Pi 4 can remain useful through external Providers/Home Base.
- Never fake telemetry/progress/capability.
- Keep Pwnagotchi/Bettercap protected and independently usable.
- Full functionality should not depend on Broad AI.
- Broad AI should not silently acquire unrestricted root authority.

---

# 19. One-sentence continuation instruction

> **Load this checkpoint plus the canonical architecture/roadmap docs, verify the current `v0.19-unified-experience` branch state, and resume by closing Gate 1 visual/physical acceptance before beginning the post-v0.19 architecture implementation sequence.**
