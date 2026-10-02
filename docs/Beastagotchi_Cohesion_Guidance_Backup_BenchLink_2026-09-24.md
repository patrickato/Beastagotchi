# Beastagotchi Cohesion, Guidance, Backup & Bench-Link Architecture
## 2026-09-24

Status: active product/architecture direction.

This document preserves the latest design decisions around **cohesion**,
Choreography, secrets/rares, Doctor, contextual help, verified runbooks, optional
AI assistance, backup/recovery, Exact Remote Mirror, and a future local
development/support link.

## Product standard: COHESIVE

Add **cohesive** to the permanent Beastagotchi product vocabulary.

A subsystem should not merely exist. It should connect naturally to the rest of
the platform through shared contracts.

Examples:
- a new hardware provider should expose Capabilities and Signals;
- Doctor should understand those Capabilities and their health;
- Universal Inspect should explain their visible values;
- Experiences/Scenes may consume them;
- Choreography may react to their Events;
- Backup/recovery should know whether their configuration is durable;
- support bundles should include sanitized evidence;
- the Runbook Registry should know how to diagnose common failures;
- optional AI may explain the same evidence and runbook to the user.

The aim is **depth through connection**, not a pile of unrelated features.

---

# Choreography Engine must include secrets, rares and hidden systems

The Choreography Engine is not only for routine events.

It must be able to coordinate:
- progression;
- achievements;
- Rare Moments;
- Rare Cinematics;
- secrets;
- hidden achievements;
- Easter eggs;
- ciphers/codes;
- seasonal events;
- lineage/Monster synthesis;
- peer encounters;
- Expeditions;
- AI/personality moments;
- system/health warnings;
- recovery/safe-mode events;
- optional sound/haptics/LED/accessory reactions.

## Spoiler-safe architecture

Hidden content must not leak merely because Choreography, Universal Inspect,
Doctor, Studio or support tooling can enumerate normal events.

Rules:
- hidden trigger definitions are not exposed by default;
- normal catalogs may expose only opaque/aggregate capability where needed;
- a secret becomes a normal semantic Event only after its trigger rules permit it;
- support bundles omit spoiler payloads unless explicit spoiler/debug export is
  enabled;
- Studio has an explicit creator/spoiler mode rather than accidentally revealing
  secrets;
- optional AI/Guide must obey the same spoiler policy;
- replay can reproduce an already-earned hidden event without exposing unrelated
  hidden triggers.

The Choreography Engine coordinates presentation after the event exists; the
Secret/Rare engines remain authoritative about whether the event should exist.

---

# Doctor + Runbook Registry + optional AI Guide

This becomes a cohesive troubleshooting/assistance stack rather than one giant
AI feature.

## 1. Beast Doctor — deterministic evidence and triage

Doctor performs bounded, preferably read-only checks:
- service health;
- collector freshness;
- provider/capability health;
- network/DNS/routes;
- display/input ownership;
- filesystem/storage health;
- power/thermal/throttle state;
- package/dependency state;
- configuration validity;
- backup freshness;
- update state;
- plugin/Pack conflicts;
- known failure signatures.

Doctor may run inexpensive background checks and raise attention states.

Doctor does **not** silently perform risky remediation.

## 2. Runbook Registry — verified procedures

Create a local registry of machine-usable troubleshooting and tutorial material.

Sources may include:
1. Beastagotchi-owned/versioned runbooks;
2. Pwnagotchi/Jayofelony documentation and applicable READMEs;
3. installed plugin/Pack documentation;
4. Linux/Raspberry Pi package/man-page information;
5. locally cached external procedures that have been reviewed/verified;
6. user-authored local procedures.

A machine-readable runbook can declare:
- id/title;
- applies-to versions/hardware;
- symptoms/signatures;
- required probes;
- interpretation rules;
- safe read-only checks;
- remediation plan;
- mutation/risk class;
- reboot/restart impact;
- rollback;
- validation;
- source/provenance;
- reviewed-at/version.

The desired path is:

**Detect → Explain → Evidence → Matching Runbook → Plan → Authorization →
Transaction → Verify → Record**

## 3. Optional AI Guide — interpretation, not authority

AI can add value by:
- summarizing logs;
- correlating Doctor findings;
- translating technical evidence into plain language;
- finding the best matching local runbook;
- answering "what does this mean?";
- guiding a user through a procedure;
- comparing current state with known-good state;
- drafting a bounded Action/Transaction plan;
- summarizing support bundles.

Deterministic probes and runbooks remain the factual authority.

Possible providers:
- local model when hardware/resources permit;
- remote provider only with explicit opt-in and privacy filtering;
- no-AI mode remains fully functional.

AI does not receive secrets/captures/private RF/location data unless the user
explicitly authorizes that scope.

---

# Contextual Help / “?” / Explain This

The user's idea is adopted as a first-class interaction pattern.

Important controls, settings and statuses may expose a small contextual help
affordance.

Desktop/WebUI:
- hover may show a short tooltip;
- click opens the richer explainer.

Touch:
- tap the help affordance;
- long-press on supported elements may invoke Universal Inspect.

The panel should answer, as applicable:
- What is this?
- Why does it matter?
- What is its current state?
- Where did this value come from?
- Why is this disabled/unavailable?
- What will happen if I change it?
- What depends on it?
- Does it require restart/reboot?
- Is rollback available?
- What is the privacy/resource impact?
- How do I fix/configure it?
- Show the relevant runbook/documentation.

This is not a static tooltip system. It should reuse Signal, Action, Capability,
Doctor, dependency and Runbook metadata.

The UI should remain uncluttered: show contextual help where it provides real
value, not a question-mark beside every label.

---

# Backup and Recovery architecture

Backup must cover everything from tiny safe snapshots to complete bare-metal
recovery.

## Tier 0 — transactional snapshots

Automatic and cheap.

Before Beast mutates important configuration:
- exact affected file/state;
- previous version/hash;
- owning transaction;
- rollback metadata.

Examples:
- plugin toggle/config;
- Experience apply;
- presentation switch;
- Pack activation;
- provider preference;
- network/display config.

## Tier 1 — Critical State Backup

Fast backup of the things that are difficult or impossible to recreate.

Examples:
- Beast database;
- roster/progression/lineage/memories;
- Beast configuration/preferences;
- Pwnagotchi config;
- custom plugins and their configuration;
- Beast Packs/Experience definitions and local user content;
- themes/faces/custom assets;
- display/touch configuration;
- important service/unit overrides;
- recovery metadata;
- package/provider manifests;
- carefully handled secrets.

Secrets should support separate encryption/exclusion policy.

This tier should be small enough to perform frequently.

## Tier 2 — Rebuild Bundle

Goal:

> Flash a compatible base image to a replacement SD and reconstruct the device.

Contains Critical State plus:
- OS/Pwnagotchi/Beast versions;
- package/BOM inventory;
- enabled services;
- boot configuration/overlays;
- filesystem mounts;
- relevant network/display/hardware-role configuration;
- plugin/Packs inventory;
- dependency/provider selections;
- checksums;
- restore manifest;
- ordered restore plan.

This may be more useful than a raw disk image across some version/hardware
changes because its contents are explainable and selectively restorable.

## Tier 3 — Bare-Metal / Full-System Backup

Goal:

> Recreate the entire SD/storage state as closely as practical.

Possible implementations may include:
- filesystem-aware image/partition backup;
- block image compressed with checksums;
- quiesced/offline clone;
- validated restore to same-size-or-larger media.

A raw live `dd` of a busy mounted filesystem is not the default professional
backup strategy.

Full-system imaging should prefer a quiesced/offline/docked maintenance path
when possible.

## Tier 4 — Emergency Rescue

Triggered by serious evidence such as:
- repeated MMC/I/O errors;
- filesystem remounting read-only;
- corruption indicators;
- rapidly recurring storage incidents;
- critically low free space threatening databases/logs;
- failed integrity checks.

Important rule:

**Do not respond to suspected failing media by immediately stressing it with the
largest possible full-image read.**

Preferred escalation:
1. preserve the smallest irreplaceable Critical State to a different healthy
   destination;
2. verify that rescue;
3. capture diagnostics/manifests;
4. expand to a Rebuild Bundle if reads remain stable;
5. attempt full imaging only when appropriate and preferably from a safer
   maintenance/offline context.

Doctor may automatically create a small emergency state snapshot only when a
configured healthy destination exists and the operation is low-risk; otherwise
it should urgently recommend the action and explain why.

## Destinations

Potential targets:
- alternate local storage;
- USB drive;
- NAS/network share;
- SFTP/SSH destination;
- user-controlled companion/laptop;
- removable media;
- manually exported archive.

Cloud is optional, never required.

## Backup truth

Every backup should record:
- type/tier;
- source device/fingerprint;
- timestamp;
- included/excluded scopes;
- software versions;
- checksums;
- encryption state;
- verification result;
- restore compatibility;
- last tested restore where known.

A backup that has never been verified is labeled accordingly.

## Backup UX

Backup Center should answer:
- Am I protected?
- What would I lose right now?
- When was each tier last created?
- Where are my copies?
- Have they been verified?
- Can this backup rebuild a blank SD?
- What is excluded?
- How much space will this require?
- What should I do before an update or risky experiment?

Doctor should integrate backup freshness into triage.

---

# Exact Remote Mirror

Preserve as a high-value Studio/diagnostic feature.

It should display the **actual output produced for the physical framebuffer**,
not a browser recreation.

Optional overlays:
- semantic layer IDs/bounds;
- touch zones;
- current touch point;
- dirty regions;
- render timing;
- Signal quality/source;
- current Scene/Experience;
- framebuffer byte/write metrics.

Use cases:
- UI creation;
- physical troubleshooting;
- remote visual verification;
- touch calibration;
- performance investigation;
- comparing the concept with real generated output.

Remote control/input requires explicit authorization and visible indication.

---

# Beast DevLink / BenchLink

The user's “Pi plugged into laptop while both are networked” idea is worth
formalizing.

A future local companion tool can connect to the Pi over:
- Ethernet;
- USB gadget networking;
- Wi-Fi/LAN;
- SSH/local Beast API;
- optionally a direct USB/serial control channel where useful.

Possible capabilities:
- Exact Remote Mirror;
- Signal/Event stream;
- logs/Doctor findings;
- file/config diff;
- support-bundle capture;
- source/artifact staging;
- explicit Action/Transaction execution;
- benchmark capture;
- screenshots/video;
- version/fingerprint comparison;
- restore/recovery assistance.

Architecture rule:
- the Pi remains authoritative;
- no unauthenticated remote root shell;
- mutation goes through explicit owner-authorized Action/Transaction boundaries
  when possible;
- SSH/root remains the manual escape hatch.

This does not mean the current ChatGPT session can directly enter the user's LAN.
The value is that DevLink can make the device dramatically easier to inspect,
manipulate and export evidence from during development/support, including bundles
that can then be supplied to an assistant.

## AI/tool bridge extension

BenchLink should eventually be able to expose a **narrow structured local tool
interface** suitable for AI-capable clients as well as human tools.

Candidate read-only tools:
- get_health;
- get_signals;
- get_events;
- get_doctor_findings;
- get_capabilities;
- get_dependency_graph;
- capture_exact_mirror;
- collect_support_bundle;
- search_runbooks;
- explain_current_incident;
- compare_known_good_fingerprint.

Candidate mutating tools remain separate and owner-authorized:
- plan_backup;
- execute_previously_reviewed_transaction;
- stage_verified_artifact;
- apply_explicit_configuration_plan;
- rollback_transaction.

Do **not** expose unrestricted shell/root or Pwnagotchi attack controls as the
default AI interface.

The structured bridge may later use an MCP-like/local-tool protocol or another
appropriate transport. The stable requirement is the permissioned tool model,
not one specific AI vendor/protocol.

---

# Pwnagotchi-first usefulness

Not every idea must wait for Beastagotchi.

Some diagnostics, backup, display, connectivity and plugin-management concepts
can be prototyped as normal Jayofelony-compatible Pwnagotchi plugins/helpers.

Useful prototypes may later become Beast adapters instead of being discarded.

The separate `patrickato/test-plugins` repository is the experimentation area
for that work. Beastagotchi remains the primary integrated platform.

---

# Cohesion test for future ideas

Before adding a major feature, ask:

1. Which Signals does it consume/produce?
2. Which Events does it emit/react to?
3. Which Actions does it expose?
4. Which Capabilities does it require/provide?
5. Does Doctor understand its health/failures?
6. Is there contextual help/runbook coverage?
7. Is its important state backed up?
8. Can an Experience/Scene use it coherently?
9. Does Choreography need to react to it?
10. What does recovery/rollback look like?
11. What is its privacy/security boundary?
12. Can optional AI assist without becoming the authority?

If those answers are coherent, the feature belongs to the platform instead of
becoming an isolated bolt-on.


---

# Cohesion Graph / Cohesion Lint

Once Signals, Events, Actions, Capabilities, Scenes, Runbooks and backup scopes
are registries, Beast can inspect its own integration completeness.

A future Cohesion Graph can answer:
- which feature produces/consumes this Signal?
- which Event triggers this choreography?
- which Action changes this capability?
- which Doctor probe watches it?
- which runbook explains failure?
- which backup tier preserves its state?
- which Experience/Scene uses it?
- what rollback path exists?

A Cohesion Lint pass can warn during development/Pack intake when a feature has
important missing integration edges.

Examples:
- mutable setting has no rollback/snapshot;
- provider has no health probe;
- important state is absent from backup policy;
- Action has no contextual help;
- capability requirement has no remediation/runbook;
- hidden/secret event leaks spoiler metadata;
- Scene binds a privacy-sensitive Signal to a public surface;
- App has a permission but no declared reason/consumer.

This turns **cohesive** from a subjective design aspiration into something Beast
can partially verify.
