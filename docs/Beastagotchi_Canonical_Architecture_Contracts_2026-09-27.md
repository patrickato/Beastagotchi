# Beastagotchi Canonical Architecture Contracts

**Date:** 2026-09-27  
**Status:** canonical pre-implementation architecture rewrite after Doctor, Capability Expansion, AI, Monster, and Security/Pentest reconciliation  
**Implementation:** still paused until the companion build-order/roadmap rewrite is completed

---

# 1. Product identity

Beastagotchi is a modular, local-first platform built around a protected Pwnagotchi + Bettercap foundation.

The system is not a replacement for Pwnagotchi, Bettercap, Linux, mature security tools, or expert workflows. It is the integration, truth, orchestration, lifecycle, presentation, learning, history, and companion layer that makes those capabilities coherent and approachable.

Primary rule:

> **Do not build something merely because we can. If a mature tool already does it well, integrate, wrap, orchestrate, and teach it. Build Beast-native code where the missing value is integration, presentation, orchestration, lifecycle, safety, discovery, verification, history, or Guided use.**

Owner-space rule:

> **Unsupported does not mean forbidden. Beast-managed workflows, Full Tools, and Owner Space coexist.**

Truth rule:

> **Real/live data over fake/demo telemetry. Unknown remains unknown. Derived/estimated values stay labeled as such.**

---

# 2. Layer model

Canonical conceptual stack:

**Truth -> Capability -> Action -> Transaction -> Procedure -> Doctor -> History -> Presentation**

Cross-cutting services:
- Search/Knowledge
- Scope/Authority
- Evidence/Provenance
- Help/Learn
- Secrets/Privacy
- Automation/Scheduling
- Home Base/Companion routing
- Broad AI (optional)

Presentation may expose many pages, Workspaces, Tools, Experiences, views, and overlays, but those are not separate truth stores.

---

# 3. Composition and ownership contract

There is one runtime composition root for Beast-owned stateful services.

Stateful managers/stores have one conceptual owner and are injected into consumers rather than recreated independently.

Preserve the existing PR #22 foundation:
- Core-owned shared stateful managers;
- one normal SQLite connection per calling thread through the ThreadBoundStore model;
- shared presentation preference contract;
- adapter-first migration rather than flag-day replacement.

SQLite/database schema migrations must become explicit versioned migrations using SQLite `user_version` or equivalent durable schema-version tracking before broad new persistence domains are added.

---

# 4. Typed registry contract

Stable typed registries are the canonical catalog substrate.

Registry entries must support, where applicable:
- stable ID;
- display metadata;
- provenance/source;
- trust/test status;
- version/generation;
- requirements/dependencies;
- privacy classification;
- hardware/software compatibility;
- enabled/available state;
- replacement/activation protections.

Existing typed registry substrate from PR #22 is preserved.

Registry families eventually include:
- Actions;
- Signals;
- Events;
- Providers;
- Abilities;
- Procedures;
- Tools/Tool Adapters;
- Help sources;
- Surfaces/Experiences;
- Packs/Collections;
- optional Probe/diagnostic descriptors where useful.

Do not invent separate bespoke catalogs where one typed registry family can represent the same concern.

---

# 5. Provider contract

A Provider is a normalized source of capability/truth from hardware, software, services, remote nodes, or external tools.

Examples:
- GPS/gpsd;
- Bettercap;
- Pwnagotchi bridge;
- Kismet;
- RTL-SDR/rtl_433;
- battery/UPS monitor;
- phone sensor/provider;
- Home Base service;
- ESP32/M5Stack external sense;
- future camera/audio/measurement providers.

A Provider must declare:
- identity/version/source;
- what primitive capabilities it supplies;
- readiness/health;
- dependencies;
- resource ownership/conflicts;
- data freshness and source quality;
- privacy/sensitivity;
- start/stop/lifecycle semantics;
- optional Doctor probes/health checks.

Providers do not own unrelated presentation or duplicate state that belongs to core stores.

---

# 6. Ability contract

Abilities answer:

> **What can this specific Beast do right now, and what could it do with one missing piece?**

Abilities are derived from current Providers, hardware, installed software, policy, context, and resource conflicts.

Canonical user-facing states include:
- READY;
- AVAILABLE;
- FULL TOOL;
- OWNER SPACE;
- NEEDS HARDWARE;
- NEEDS SOFTWARE;
- CONTEXT/LICENSING REQUIRED;
- CONFLICTED/UNAVAILABLE where appropriate.

Abilities are dynamic. Plugging in hardware, pairing a phone, reaching Home Base, gaining Internet, installing software, or losing a resource can change the graph immediately.

Abilities never become breeding/progression locks for fundamental machine capability.

---

# 7. Signal and Event contract

Signals represent current/observable state. Events represent things that happened.

They must use stable typed definitions and privacy metadata.

Examples:
- temperature/load/storage pressure;
- GPS fix/freshness;
- attached hardware;
- AP/client/radio observations;
- Pwnagotchi epoch/capture events;
- Doctor findings;
- task progress;
- known-network drift;
- external power/battery transitions;
- user/automation actions.

The EventBus remains transport, not the semantic catalog. Typed EventSpec/SignalSpec registries become canonical semantics over time.

Future EventBus work should add bounded/drop observability so dropped or backpressured events are visible rather than silent.

---

# 8. Action contract

An Action is a named Beast-managed operation.

Actions must declare:
- stable ID;
- inputs/schema;
- authority/risk class;
- requirements;
- whether mutation occurs;
- expected result/verification;
- privacy implications;
- applicable scope/context constraints;
- Transaction/Procedure relationship.

RegisteredActionBroker is the migration target. Legacy ActionBroker fallback remains temporarily for unmigrated actions only.

Authority/risk metadata must become centralized rather than being inferred ad hoc in individual handlers.

AI, UI, Automation, Doctor, and Procedures all call the same registered Action contract. None receive a separate hidden execution universe.

---

# 9. Transaction contract

A Transaction is the durable mutation envelope.

Canonical lifecycle:

**plan -> snapshot/recovery readiness -> execute -> verify actual outcome -> commit OR rollback -> verify rollback -> record receipt/cleanup obligation**

Preserve the shared Transaction Engine/FileTransactionJournal foundation from PR #22.

Required properties:
- durable identity/status;
- nested transaction linkage where needed;
- verification before commit;
- rollback and rollback-failure states;
- restart discovery/recovery;
- truthful live progress;
- evidence/receipts;
- cleanup obligations;
- secrets redaction in ordinary receipts/logs.

Migrate existing mutating workflows incrementally. Proven inner rollback systems may remain temporarily until equivalent shared-engine behavior is verified.

---

# 10. Procedure contract

A Procedure is a reusable multi-step workflow composed from Actions, checks, waits, branching, and verification.

Procedures are the managed orchestration layer for:
- guided setup;
- repairs;
- hardware qualification;
- security assessment steps;
- repeated owner workflows;
- onboarding;
- restore/recovery;
- later AI-drafted workflows after deterministic validation.

Procedures must be inspectable before execution and generate linked task/transaction evidence.

Procedures may wrap mature tool operations; they do not require Beast to reimplement the underlying tool.

---

# 11. Scope / authorization contract

Security and other context-sensitive workflows use one shared Scope object rather than each tool inventing its own target list.

A Scope may describe:
- owned/authorized hosts/subnets;
- owned/lab APs and clients;
- BLE/RFID/hardware lab targets;
- deliberately vulnerable VMs/containers/apps;
- assessment/session identity;
- time window;
- operator notes/authorization context.

Scope is evidence/context, not magical proof of external authorization.

Managed/Guided security workflows use the shared Scope where technically applicable.

Security capability classification remains:
1. Beast-managed;
2. Authorized/Guided Lab;
3. Full Tool;
4. Owner Space;
5. hard-boundary operations that Beast does not wrap/automate.

---

# 12. Evidence / observation / finding contract

Security and diagnostics must not degrade into unrelated tool output files.

Preserve raw evidence and normalize useful metadata upward.

Canonical high-level record families include:
- Evidence Artifact — immutable/referenceable source object such as PCAP, log, firmware image, screenshot, report, command output;
- Observation — something measured/seen without claiming it is bad;
- Finding — an interpreted condition with confidence/severity/provenance;
- Incident/Case — related observations/findings/evidence grouped around a problem or event;
- Receipt — what Beast changed and how it verified the result.

Each normalized record should support:
- source/provider/tool;
- timestamp/trusted-time quality;
- scope/session linkage;
- patient/device linkage;
- provenance;
- confidence where interpreted;
- privacy/sensitivity;
- links back to raw evidence.

Normalization never replaces the original artifact.

---

# 13. Tool / Tool Adapter manifest contract

Mature programs are Full Tools, not Beast plugins merely because Beast integrates them.

A Tool Adapter/manifest describes enough metadata for Beast to make the tool discoverable and approachable without reimplementing it.

Candidate manifest fields:
- id/name/version/source/license;
- supported boards/architectures;
- install/update/remove method;
- resource footprint;
- hardware requirements;
- detection/version command;
- built-in help invocation (`--help`, `-h`, `help`, man/info, local docs);
- input/output formats;
- APIs/sockets/structured output;
- security/risk classification by operation where useful;
- Guided workflows available;
- Full Tool launch method;
- Home Base preference/requirement;
- Provider/evidence adapters;
- Doctor health hooks;
- secrets/network requirements.

Catalog ordering may show Featured/Core/Recommended first and A-Z thereafter. Popularity claims require real evidence; maturity/integration quality may be separate signals.

Repo Intake/Capability Harvest uses this same manifest model when evaluating external projects.

---

# 14. Help / Learn contract

Beast must make real software easier to learn without replacing its real documentation.

Help sources may include:
- program built-in help;
- man/info pages;
- installed docs;
- upstream README/manual;
- cached/offline knowledge;
- current web/project docs;
- Beast-specific Guided tutorials;
- Broad AI explanation over retrieved authoritative material.

Experience ladder:

**Focused/Guided -> Advanced Guided -> Full Tool -> Owner Space**

Broad AI may explain tool documentation and translate intent into existing managed workflows, but external text/instructions never automatically become execution authority.

---

# 15. Search / Knowledge contract

Search is federated and non-AI at its core.

Search may query:
- settings/state/registries;
- local files;
- structured Beast stores;
- Doctor knowledge/cases;
- Chronicle/history;
- offline manuals/wiki/reference datasets;
- GitHub/project docs;
- web/current sources;
- Global Doctor knowledge;
- tool/provider-specific search backends;
- Home Base/NAS stores.

AI synthesis may sit above retrieved results but does not replace Search or provenance.

Candidate mature backends remain Recoll/Xapian, SQLite FTS, ripgrep, exact registries, Kiwix/ZIM, MapLibre/PMTiles, and optional SearXNG/Home Base providers.

---

# 16. Doctor contract

There is one Doctor.

Doctor is the deterministic specialist diagnostic/repair system spanning:
- physical board/hardware;
- Linux/kernel/drivers/device-tree/services/storage/networking;
- Pwnagotchi/Bettercap/plugins/radio/capture pipeline;
- Beast Core/UI/Studio/Providers/transactions/history;
- attached supported hardware and managed ecosystem.

Canonical reasoning:

**Machine Census -> symptom -> affected capability -> dependency path -> competing hypotheses -> evidence -> next informative probe -> confidence -> repair plan -> recovery readiness -> repair -> functional verification -> cleanup -> learn**

Principles:
- Running != working.
- Doctor finds it -> uses it -> puts it back.
- Investigate aggressively; repair conservatively; ask intelligently.
- Known-Good / What Changed? are first-class evidence.
- Fleet/global cases never override local patient evidence.
- Healthy systems teach normal; failures teach failure.

Confidence vocabulary remains:
- Possible;
- Supported;
- Likely;
- Strongly supported;
- Confirmed;
- Contradicted.

Doctor works fully with AI disabled.

---

# 17. Broad AI contract

Broad AI is optional and separate from Doctor and Creature.

Mental model:
- **Broad AI = Ask Beast anything / conversational assistant and orchestrator.**
- **Doctor = specialist clinician.**
- **Creature = living identity/personality.**

Broad AI may run on:
- Pi where a lightweight model is useful;
- paired phone;
- Home Base/desktop;
- self-hosted model endpoint;
- optional remote/cloud provider.

Weak boards such as Pi Zero 2 W require no local inference.

Broad AI may:
- explain;
- synthesize Search results;
- answer natural-language capability questions;
- call Doctor;
- query Abilities/System Graph;
- draft configuration/Procedures/code;
- request existing managed Actions;
- launch/handoff to Full Tools;
- provide optional Creature/session narration.

Broad AI may not:
- become the factual source of truth;
- gain a hidden unrestricted root shell;
- silently bypass Action/Transaction/authority contracts;
- convert external prompt instructions into authority;
- become required for core Beast operation.

Exact models are implementation-time/provider choices, not architecture contracts.

---

# 18. Creature / Monster contract

Creature state is deterministic Beast data, not an LLM memory blob.

Substrate includes:
- identity;
- traits/affinities;
- progression/events;
- structured memories;
- relationships/peer history;
- semantic mood/expression state;
- lineage hooks for later expansion.

Perception pipeline:

**truthful Beast Signals/Events -> creature interpretation through traits/memory/context -> semantic expression state -> available output surfaces**

Adding hardware can broaden perception/expression (GPS, SDR, sensors, LEDs/audio/haptic/etc.) but breeding/progression never gates fundamental owner machine capability.

Deep breeding/genetics/morphology/rare mutation economies remain post-release expansion over this substrate.

---

# 19. Presentation / Surface contract

Doctor, Creature, Security, Radio, Hardware Bench, etc. are capabilities/Experiences over common truth—not separate state silos.

Target presentation substrate remains:
- SurfaceRegistry;
- SurfaceStack;
- InputRouter;
- NavigationController;
- shared presentation preferences;
- preview/runtime asset/layout reuse where practical.

TFT constraints:
- 480x320 clarity;
- large touch targets;
- low-cost rendering;
- current status/task/next action;
- minimal scrolling;
- no graph/animation clutter for its own sake.

WebUI/Studio may be richer.

Live preview is part of the WebUI/Studio direction. Fidelity rule:
- reuse actual assets/layout/state/theme/render logic where practical;
- label browser-vs-physical differences honestly;
- physical Pi/TFT remains final visual truth.

No arbitrary fixed page count.

---

# 20. ModuleRuntime / Scheduler / Task contract

Recurring Beast-owned work must migrate from scattered loops toward an explicit ModuleRuntime/Scheduler.

A scheduled/background unit should declare:
- identity/owner;
- cadence/trigger;
- resource needs;
- conflicts/leases;
- expected cost;
- power/network/context requirements;
- cancellation/restart semantics;
- progress/task visibility;
- evidence/history policy.

Task Center aggregates background work if the user leaves context; it is not required as the only place progress may be shown.

Automation remains:

**When Signal/Event X -> if condition Y -> perform Action/Procedure Z**

Advanced visual orchestration may later integrate a mature Full Tool such as Node-RED rather than growing a giant proprietary language.

---

# 21. Resource arbitration contract

Shared hardware/resources require explicit leasing/arbitration rather than silent contention.

Examples:
- one SDR serving incompatible frequencies;
- one Wi-Fi adapter assigned to Pwnagotchi vs management vs lab role;
- camera/mic/output device ownership;
- GPIO/SPI/I2C conflicts;
- external displays;
- Home Base heavy-worker slots.

The arbitration layer informs Abilities and Procedures when a capability is temporarily unavailable/conflicted and may offer switching/sequencing where safe.

---

# 22. Pwnagotchi / Bettercap boundary contract

Pwnagotchi and Bettercap remain protected underlying engines and independently usable.

### `beast-bridge` Pwnagotchi custom-plugin
High-priority bridge candidate. It subscribes to Pwnagotchi lifecycle/radio events and emits normalized local structured events upward without forcing Beast logic into Pwnagotchi core.

### `capture-ledger` Pwnagotchi custom-plugin
High-priority candidate. Captures durable sidecar/provenance metadata for capture artifacts and sessions.

### `radio-vitals` Pwnagotchi custom-plugin
High-priority candidate. Exposes lightweight evidence about monitor-interface existence, channel behavior, actual packet reception, radio resets/failures, and capture-pipeline health.

Pwnagotchi custom-plugins stay lightweight/event-centric. Doctor, Broad AI, Security Workspace, Search, Home Base, etc. do not live inside custom-plugins.

### Bettercap Provider
Where structured Bettercap REST/session/event data exists, consume it directly rather than grepping console output.

Bettercap Caplets may be cataloged/explained and, where appropriate, wrapped as Procedures. Unknown or sensitive caplets are never silently trusted or automatically elevated.

---

# 23. Capture Intelligence contract

A capture is a first-class Evidence Artifact, not merely a file path/count.

Capture metadata may include:
- hash/duplicate relation;
- session/scope;
- adapter/interface;
- channel/band;
- AP/client context;
- timestamp/trusted-time quality;
- optional location source/freshness;
- content/quality summary where deterministically inspectable;
- downstream compatible Full Tools.

The system should distinguish artifact creation from artifact usefulness/verification.

Raw PCAP remains available and may be handed to mature tools such as Wireshark/TShark/Kismet/Home Base analyzers.

---

# 24. Security Workspace contract

Security is a major Beast capability family, not a hidden side feature.

Security Workspace composes:
- Scope;
- radio/network/device observations;
- captures/evidence;
- findings;
- tools;
- session history;
- Help/Learn;
- remediation/re-test;
- Full Tool handoffs.

It does not become a generic autonomous attack engine.

Managed capability may include discovery, analysis, protocol education, capture management, radio qualification, authorized lab validation, vulnerability/configuration assessment, defensive monitoring, reporting, and re-test workflows.

Where sensitive offensive operations exceed Beast-managed boundaries, the full independent tool may still exist in Owner Space; Beast does not provide the prohibited wrapper/automation.

---

# 25. Hardware Bench contract

Hardware Bench is the coherent physical-computing workspace for:
- GPIO;
- I2C;
- SPI;
- UART/serial;
- 1-Wire/PWM;
- USB serial;
- sensors;
- logic analyzers;
- Pico/ESP32-class coprocessors;
- power/current/voltage devices;
- firmware/debug adapters;
- later CAN/RS-485/industrial interfaces.

Hardware onboarding should identify only what evidence supports, then show Ready/Install/Queue/Learn/Full Tool paths.

Pin/bus/resource ownership participates in shared arbitration and System Graph.

Approved long-term integrations include mature logic-analysis, firmware/debug, RFID/NFC, Zigbee/BLE, CAN/embedded, and external security-device ecosystems; the next hardware-hacking expansion batch is explicitly post-release research.

---

# 26. Home Base / Companion contract

Phone and Home Base are capability extensions, not mandatory servers.

Phone goals:
- accountless local pairing where practical;
- rich WebUI/companion surface;
- context handoff/deep links;
- temporary Providers;
- notifications;
- file/link/text handoff;
- tether/Internet path;
- Guided SSH.

Home Base goals:
- heavy computation;
- large indexing/search;
- artifact analysis;
- maps/docs/packages/model staging;
- backup/replication;
- acquisition queue fulfillment;
- optional strong local Broad AI;
- heavy security/full-tool providers.

Pi-local core remains functional when phone/Home Base/cloud are absent.

---

# 27. Acquisition / Software Catalog / Packs contract

One Software Catalog presents available software/tools/providers/packs without making every program a bespoke subsystem.

Acquisition lifecycle:

**identify -> locate -> stage -> integrity/provenance checks -> snapshot/recovery readiness -> install/configure -> verify actual function -> retain required artifacts -> clean debris -> update inventory/evidence**

Queued acquisition may be fulfilled later via Internet or Home Base.

Capability/Security Packs group manifests/providers/help/integrations rather than blindly installing enormous distributions.

Approved pack families include, eventually:
- Wireless Analysis;
- Web/App Lab;
- Firmware/Reverse Engineering;
- Hardware Debug;
- Forensics;
- Defensive Sentinel;
- CAN/Industrial;
- Mobile Analysis;
- Security Range.

Do not blindly add Kali repositories to the Jayofelony/Pwnagotchi base. Prefer native Debian/Raspberry Pi packaging, upstream releases, isolated Python environments/pipx, selected binaries, containers where sensible, and Home Base for heavy tools.

---

# 28. Artifact trust / software provenance contract

For downloads/Packs/plugins/tools/repo intake, track what is knowable:
- source/provenance;
- hashes;
- signatures/attestations where supported;
- license;
- version;
- dependency inventory/SBOM where valuable;
- scanner findings as findings, not absolute truth.

Security expansion approved long-term concepts include SBOM/software inventory, artifact signature verification, secret-leak checks before owner-selected exports/publishing, and optional code-audit tooling.

These do not all block first release, but the metadata model should not prevent them.

---

# 29. Secrets / privacy contract

Standing rule:

> **Catalog everything important; store secrets securely; redact them from ordinary views/logs; reveal them to the owner on explicit request.**

Refinement:

> **Collect richly where justified locally; share minimally and intentionally.**

Secrets are first-class metadata/payload objects. Ordinary logs, screenshots, Doctor reports, support bundles, Broad AI context, and Global Doctor uploads redact secret values by default.

Owner may explicitly reveal/export/use secrets when appropriate.

Global Doctor never receives secret values.

Deleting/rotating a secret should show known dependencies/consumers where available.

---

# 30. History / Chronicle / Known-Good contract

History is not one giant log file.

Persist structured, provenance-aware records that allow:
- What Changed?;
- Known-Good comparison;
- Doctor cases;
- sessions/Expeditions;
- capture lineage;
- security assessment history;
- creature memories;
- transaction receipts;
- device/hardware history;
- Homecoming summaries.

Trusted-time quality/source should be retained so correlation remains honest.

---

# 31. Platform-size / board contract

Beast must degrade by available capability, not by pretending all boards are equivalent.

Pi Zero 2 W:
- Pwnagotchi/Beast core remains valid;
- lightweight local services/presentation;
- Broad AI may be entirely external;
- heavy analysis routes to phone/Home Base/Full Tool elsewhere.

Pi 4:
- reference platform for current project;
- broad local capability with careful resource use;
- strong external/Home Base offload where useful.

Pi 5/future boards:
- may run more local providers/models/workloads;
- no architecture fork required.

The active runtime working set remains small even if the catalog/capability universe is huge.

---

# 32. Release-scope rule

Architecture may support far more than first release implements.

For pre-release implementation, prioritize substrate and representative vertical slices that prove the contracts.

Do not let post-release integrations (large security catalogs, deep hardware hacking, deep breeding genetics, advanced camera/CV/audio, enterprise DFIR/threat-intel platforms, large autonomous agents, etc.) continuously move the release boundary.

Post-release research explicitly includes the deferred next hardware-hacking/security-crossover batch.

---

# 33. Existing implementation foundation that remains valid

From draft PR #22, keep and build on:
- shared stateful-manager ownership;
- ThreadBoundStore SQLite model;
- bridge restart/privacy hardening;
- shared presentation preference store;
- typed registry substrate;
- RegisteredActionBroker migration seam;
- SignalSpec/EventSpec foundation;
- shared durable Transaction Engine;
- Pack install as first shared Transaction consumer;
- architecture migration ledger;
- test-backed adapter-first migration strategy.

Remaining technical debt/foundation work includes:
- migrate remaining Actions;
- centralize authority/risk metadata;
- activate canonical Signal/Event spec catalogs;
- add schema-versioned DB migrations;
- ModuleRuntime/Scheduler;
- Surface/Presentation substrate;
- resource arbitration;
- Provider/Ability registries;
- Scope/Evidence primitives;
- Tool/Help manifest substrate;
- Bettercap/Pwnagotchi bridge hardening and physical validation;
- physical Gate-1 visual/runtime acceptance.

---

# 34. Canonical product architecture summary

Beastagotchi should be:

> **A situationally composable platform whose deterministic core knows what is true, what the machine can do, what changed, what actions are available, how to perform changes safely, and how to verify outcomes. Mature external tools supply deep specialist capability. Doctor diagnoses. Broad AI converses and orchestrates optionally. Creature gives the machine identity and expression. Presentation makes the same underlying truth usable from a 480x320 TFT through phone/WebUI/Studio without creating competing systems.**

This document supersedes brainstorm-level architecture language where later reconciliation changed the meaning, but it does not erase reserved post-release ideas.