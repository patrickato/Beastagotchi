# Beastagotchi Doctor Deep-Dive / Jam

**Date:** 2026-09-26  
**Status:** active design jam; preserve agreed direction and open questions before implementation resumes

---

# Core vision

Doctor is intended to be one of Beastagotchi's signature systems:

> **One stop shop for anything wrong anywhere in the physical Pi, Linux platform, Pwnagotchi/Bettercap stack, plugins/integrations, Beast Core/UI/Studio, attached hardware or managed ecosystem.**

Doctor is not "a log viewer." Logs, commands, probes, inventories, telemetry, files, package manifests, device-tree facts, configuration, histories and other evidence are Doctor's instruments.

Normal user mental model:

> **Something is wrong -> Doctor.**

Raw/manual access remains available to experts/Owner Space.

---

# 1. Doctor patient model

Doctor should be able to interrogate the full relevant stack.

## Physical / board layer

Examples:
- board model/revision;
- SoC/RAM;
- firmware/bootloader;
- temperature/throttle/power evidence;
- storage devices/partitions/filesystems;
- attached USB hardware;
- Bluetooth/radio hardware;
- display/touch hardware;
- GPIO/SPI/I2C/serial devices;
- audio;
- future sensors/providers.

## Linux/platform layer

Examples:
- kernel/version/modules/drivers;
- device tree/overlays;
- boot config;
- systemd/services;
- processes;
- permissions;
- packages/package manager state;
- runtimes/Python/environments/libraries/dependencies;
- filesystem trees/files/configuration;
- network interfaces/routes/DNS/sockets/firewall/VPN where applicable;
- Wi-Fi PHY/regulatory/monitor-mode state;
- Bluetooth;
- USB topology;
- storage/mount/read-only/error state;
- journal/dmesg/crash evidence;
- resources/performance.

## Pwnagotchi / Bettercap layer

Examples:
- exact versions/builds;
- Jayofelony image/version;
- config/drop-ins;
- plugins/settings/dependencies;
- service/process state;
- agent behavior;
- Bettercap/API;
- managed/monitor interfaces;
- driver/PHY/regulatory/channel capabilities;
- capture/handshake/peer/session/epoch facts;
- patches/customizations;
- expected vs actual paths/files/dependencies.

## Beast layer

Examples:
- Core/UI/Studio versions;
- Signals/Events/Capabilities/Providers;
- Actions/Transactions/Procedures;
- Packs/extensions;
- Presentation/Experience/Scenes;
- System Graph;
- Resource Governor;
- Expeditions/Missions;
- creature/progression/memory/PeerDex/global/content state;
- Home Base;
- Search/Field Library;
- Recovery/backup state;
- customization/Owner Space changes;
- Doctor's own health/evidence.

---

# 2. Probe strategy

Doctor should not constantly run every deep probe.

## Machine Census

Deep first-install / major-upgrade / deliberate refresh / major hardware-change inventory.

Goal:

> learn nearly everything slow-changing that is useful about this patient.

Persist concise canonical facts/fingerprints rather than needless full duplication of the filesystem.

## Vital signs

Cheap/live/regular facts already available through normal State/Signals.

## Fault-family Probe Blocks

Prewritten deep diagnostic kits selected automatically by symptom/failure family.

Examples:
- DISPLAY-DEEP;
- RADIO-DEEP;
- STORAGE-DEEP;
- POWER-DEEP;
- BOOT-DEEP;
- NETWORK-DEEP;
- PWNAGOTCHI-DEEP;
- BETTERCAP-DEEP;
- PLUGIN-DEEP;
- BEAST-CORE-DEEP.

These are Doctor instruments, not separate Doctor products.

## Open-ended escalation

When known probe blocks do not explain the issue, Doctor may:
- run additional bounded probes;
- inspect relevant files/trees;
- compare Known-Good;
- inspect change/Transaction history;
- search local/offline knowledge;
- search approved online/current sources when available;
- acquire an additional diagnostic/helper capability;
- ask the user for a physical observation/action only when machine evidence cannot answer it.

Principle:

> relevant diagnostic evidence is generally more useful than artificially tiny output; avoid unbounded/noisy collection but do not fail because one needed fact was never gathered.

---

# 3. Patient knowledge + medical library

Doctor reasoning should combine:

## Patient knowledge

Facts about **this specific Beast installation/hardware/current state**.

## Medical/knowledge library

Reusable information from sources such as:
- Beast docs;
- Pwnagotchi/Jayofelony docs;
- Bettercap docs;
- Linux man pages/docs;
- Raspberry Pi docs;
- plugin READMEs;
- hardware manuals/datasheets;
- owner-added notes/docs;
- offline TXT/Markdown/PDF/wiki content;
- previous solved Doctor cases/resolutions;
- current official docs/GitHub/community material when online/permitted.

Doctor should map general advice against the actual patient before recommending/executing it.

No blind execution of arbitrary Internet snippets.

---

# 4. Find it -> use it -> put it back

Owner phrase to preserve:

> **Doctor finds it -> uses it -> puts it back.**

Doctor should not stop at "required thing not installed" when a managed resolution is reasonably possible.

Missing requirement may include:
- driver/module;
- package;
- runtime/library;
- parser/helper utility;
- hardware-query tool;
- manual/reference dataset;
- map/catalog;
- other trusted required resource.

Candidate resource-resolution hierarchy:

1. present but misconfigured/not detected;
2. Beast-managed local cache/content pool;
3. owner/local storage/library;
4. previously downloaded/staged resource;
5. Home Base/NAS resource pool;
6. trusted OS/package repository;
7. trusted vendor/project source;
8. known official GitHub/release source;
9. broader web Search as discovery evidence, requiring stronger verification before managed use;
10. queue for later if connectivity is unavailable.

Managed lifecycle:

> identify exact need -> resolve compatible artifact -> plan/snapshot -> acquire to staging -> verify provenance/integrity/compatibility -> unpack/build if required -> install/configure -> verify requested function -> probation/reboot if needed -> commit -> retain required runtime/recovery artifact -> delete temporary archive/extracted debris -> update inventory/evidence.

Failure path:

> verify failure -> rollback -> clean staging/debris -> preserve evidence -> continue diagnosis / ask owner when required.

"Put it back" means return the machine to a **clean intentional state**. It does not mean remove a driver/library that must remain installed for the repair to persist.

---

# 5. Queued acquisition

If a needed resource cannot be obtained in the field/offline:

Doctor can offer:
- Queue for next Internet;
- Queue for Home Base;
- Dismiss;
- owner-selected alternative source later.

The resource request should record:
- what is needed;
- why;
- requesting subsystem/Doctor case;
- compatible version/architecture/kernel constraints when known;
- preferred/trusted sources;
- install vs reference-only intent;
- whether acquisition may happen automatically or must ask first.

When an allowed connection appears, the generic Home Base/Acquisition system may download/stage/sort/verify it and return the result to Doctor.

Download != install/apply.

---

# 6. Cleanup / hygiene

Temporary artifacts created by managed Doctor work must have explicit cleanup ownership.

Examples:
- ZIP/TAR/package downloads;
- extracted install directory;
- temporary build tree;
- helper binaries;
- disposable caches;
- temporary diagnostic output beyond retention policy.

Desired behavior:
- successful Transaction cleans its own temporary artifacts;
- rollback cleans failed-path debris;
- interrupted operations journal cleanup obligations;
- broader Beast Clean Up/housekeeping may later remove registered orphaned debris;
- never delete unknown owner files merely because they look temporary.

---

# 7. Existing systems Doctor should reuse

Doctor should not become a second architecture.

Reuse:
- canonical State / Signals / Events;
- System Graph;
- Device Passport/inventory;
- Known-Good / What Changed?;
- Action Broker;
- Transaction Engine;
- Procedures;
- Recovery Vault/backups;
- Search / Field Library / offline knowledge;
- Acquisition Queue / Home Base;
- Resource Governor;
- Incident history;
- support/debug evidence where useful.

---

# 8. Open design question: Doctor autonomy

Still to resolve during this jam:

Possible spectrum:

1. **Clinic:** acts only when owner opens Doctor.
2. **Physician:** proactively notices and reports problems.
3. **Mechanic:** automatically performs harmless/reversible repairs.
4. **Caretaker:** proactively investigates, resolves what policy permits, queues missing resources, verifies the result, and bothers the owner only for consequential/ambiguous/physical decisions.

Current assistant recommendation is between Mechanic and Caretaker, with owner policy/authority governing automatic mutation.

Need owner jam/input before freezing exact behavior.

---

# 9. Full-tool access principle (cross-reference)

Guided Beast experiences do not remove expert access to complete underlying software.

Example SDR pattern:
- Guided/Focused Beast experience;
- Advanced guided controls;
- Open Full Tool/application.

This may generalize to other complex software and should be examined during Capability Expansion.

See:
`docs/Beastagotchi_Celestial_SDR_and_Queue_Idea_Addendum_2026-09-26.md`

---

# 10. Status / next

Doctor deep-dive is **active**.

Next jam topics should include:
- Doctor autonomy/proactivity;
- how diagnoses become confidence-ranked hypotheses;
- how Doctor chooses probe blocks/escalation;
- repair authority and owner-consent policy;
- physical-action handoff/walkthroughs;
- how previous solved cases influence future repair;
- how online/community fixes are vetted/translated into Procedures;
- whether Doctor needs a dedicated owner-facing "case" UX or simply uses Incidents behind the scenes;
- how Doctor exposes technical depth to expert users without burdening beginners.
