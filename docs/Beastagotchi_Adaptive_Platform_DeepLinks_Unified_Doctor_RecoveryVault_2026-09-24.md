# Beastagotchi Adaptive Platform, Deep-Link, Unified Doctor & Recovery Vault Architecture
## 2026-09-24

Status: active architecture direction for v0.19+.

This record extends the Maturity Review, Capability Platform review and Cohesion/
Backup/BenchLink architecture.

## 1. One Beast platform, many hardware capacities

Beastagotchi should target **capabilities and resource classes**, not a short
whitelist of Raspberry Pi model names.

The same platform should be able to scale down or up depending on:
- CPU architecture/core count/performance;
- RAM;
- storage type/free space/endurance;
- framebuffer/DRM/display resolution;
- touch/input devices;
- GPU/display backend;
- network interfaces;
- optional hardware capabilities;
- measured thermal/performance behavior.

Board model may refine quirks/defaults, but should not be the primary product
boundary.

### Initial compute tiers

- **constrained** — Zero 2 W-class / ~512–768 MB systems; restrained motion,
  smaller caches, fewer background conveniences by default.
- **compact** — ~1–2 GB systems.
- **full** — Pi 4/400-class and comparable SBCs with several GB RAM.
- **enhanced** — Pi 5/high-memory/reference-superset-class systems.
- future measurement can refine these tiers without changing Experience schemas.

These are default-budget hints, not arbitrary hard feature bans.

The Resource Governor and real measurements remain authoritative.

### Initial display classes

- micro;
- reference 480×320 class;
- medium ~800×480;
- large tablet/portable display;
- desktop/command-center class.

A Scene/Experience can provide target-specific variants while sharing Signals,
Actions and semantics.

### Role-based deployment is more important than board branding

A device may serve one or more roles:

**Full Beast Host**
- Pwnagotchi/Bettercap;
- Beast Core;
- local UI;
- optional Studio.

**Compact Beast Host**
- same identity/core contracts;
- lighter Experience/runtime defaults;
- optional heavy services dormant/offloaded.

**Display / Command Node**
- large touchscreen/HDMI/DSI system;
- consumes Beast Signals/Events;
- richer renderer;
- may not own the radio/Pwnagotchi engine.

**Studio / Bench Node**
- laptop/Pi/SBC running Studio/BenchLink-facing tools;
- visualization, debugging, backups and development support.

**Sensor / Satellite Node**
- Pi Zero/ESP32/other small device producing approved Signals through Beast Bus.

**Recovery Node**
- laptop/NAS/another Beast/SBC that can receive verified rescue backups.

This allows Pi Zero 2 W, Pi 4, Pi 400-style systems, Pi 5, Compute Modules,
tablet-like touch builds and non-Raspberry-Pi Linux SBCs to participate at the
capacity they can host.

### Portability contract

The portable Beast layer should prefer:
- Python/Linux APIs;
- systemd where available;
- /proc and /sys;
- fbdev/DRM abstractions;
- udev/evdev/libgpiod;
- D-Bus service providers;
- capability adapters.

Raspberry-Pi-specific tools such as `vcgencmd` remain optional provider data,
not assumptions that prevent another SBC from running Beast.

---

## 2. Adaptive Platform Profile is now implemented

`beastcore/platform_profile.py` provides read-only derived guidance from live
canonical state.

It publishes:
- compute tier;
- display class;
- model/architecture/RAM/core evidence;
- primary display;
- budget hints;
- explicit policy stating that board names are hints only and technical
  requirements are the only legitimate hard blockers.

Core exposes the result at:

`GET /platform-profile`

This is an input to the future Experience Compiler and Resource Governor. It is
not permission to silently disable arbitrary features.

---

## 3. Deep Links / Hyperlinks are a first-class platform contract

The user's hyperlink idea is adopted.

However, Beast should not scatter brittle hard-coded web URLs through the
product.

Define a semantic **Beast Link** object.

Conceptual examples:

- `doctor/finding/<id>`
- `signals/system.temp.cpu_c`
- `capabilities/location.position`
- `settings/presentation`
- `plugins/<id>`
- `runbooks/<id>`
- `backup/center`
- `backup/create?kind=critical-state`
- `hardware/device/<id>`
- `experiences/<id>/edit`
- `expeditions/<id>/replay`

A Beast Link may render differently by surface:

### WebUI / Studio
Normal clickable hyperlink/router navigation.

### Touch UI
Tap target, button, contextual-help action or Universal Inspect command.

### Phone/companion
Local deep link into the relevant page.

### QR / support
A local/share-safe link may direct an authorized companion to the exact help,
runbook or support location.

### External documentation
Explicit URL with provenance. External links should never silently perform
configuration or leak private context.

### Link behavior

Links can include a return target/breadcrumb so the user can follow guidance and
return to the original problem.

Doctor/runbooks should be able to emit links such as:

> DNS is unavailable on the active tether.
> [Open Connectivity]
> [Show evidence]
> [Open matching runbook]

or:

> Critical State backup is stale.
> [Open Backup Center]
> [Create Critical State backup]

The user remains in control.

---

## 4. One Doctor, modular specialists

There should be **one Beast Doctor from the user's perspective**.

Do not create competing RadioDoctor / DisplayDoctor / StorageDoctor products.

Internally Doctor may load specialist **probes**:

- core/service probe;
- Pwnagotchi probe;
- Bettercap/radio probe;
- connectivity/DNS/USB/Bluetooth probe;
- display/touch probe;
- storage/filesystem/SD probe;
- power/thermal probe;
- plugin/Pack/dependency probe;
- update/package probe;
- backup/recovery probe;
- hardware/capability probe;
- Experience/presentation probe.

Benefits of internal modularity:
- probes can have independent cadence;
- expensive probes stay on-demand;
- hardware-specific probes can be optional;
- failures in one probe do not disable diagnosis;
- tests stay bounded;
- Packs/providers can contribute new diagnostics.

But all results flow through one Doctor severity/evidence/runbook/recommendation
model.

### Background vs on-demand

**Background**
- inexpensive health/freshness checks;
- critical filesystem/I/O indicators;
- service loss;
- serious thermal/power conditions;
- backup freshness;
- known high-confidence failure signatures.

**On-demand**
- expensive package scans;
- deeper log correlation;
- intrusive hardware tests;
- display test patterns;
- network probes that create traffic;
- lengthy integrity checks.

Doctor may work quietly in the background and surface only meaningful changes.

### Doctor partners

Doctor remains diagnosis authority while integrating with:
- Incident Engine;
- Runbook Registry;
- Universal Inspect;
- Contextual Help;
- Backup/Recovery Coordinator;
- Action/Transaction Engine;
- Capability Resolver;
- optional AI Guide;
- BenchLink;
- support bundles.

AI explains/correlates; Doctor's deterministic evidence remains authoritative.

---

## 5. Rollback Snapshot / Known-Good Snapshot

Add a distinct concept between tiny transaction snapshots and disaster backups.

A **Rollback Snapshot** captures the system state needed to answer:

> Put the important Beast/Pwnagotchi configuration back the way it was before
> this change.

Possible contents:
- Pwnagotchi/Beast configs;
- active Experience/presentation;
- plugin enable/config state;
- provider preferences;
- package/provider fingerprint;
- display/touch config;
- service override state;
- boot overlays relevant to Beast;
- DB checkpoint where necessary;
- checksums and provenance.

A **Known-Good Snapshot** is a verified Rollback Snapshot marked after successful
health/probation.

Use cases:
- before updates;
- before large Pack changes;
- before display ownership changes;
- before dependency acquisition;
- before advanced Expert Mode changes;
- Doctor recommendation when state starts drifting.

Important:
ext4 does not magically become a filesystem-snapshot system because Beast calls
something a Snapshot. On ordinary SD/ext4 installs this is an application-level
consistent checkpoint. If a future platform offers Btrfs/LVM/ZFS-native
snapshots, that can become another provider.

---

## 6. Recovery Vault

Backup destinations should become **Capabilities**.

The backup engine should not assume the source SD is also the destination.

A Recovery Vault is an independent destination capable of receiving one or more
backup tiers.

Potential providers:

### Local independent storage
- USB flash/SSD/HDD;
- second internal drive;
- other mounted healthy filesystem.

### BenchLink laptop
When the development/support laptop is connected, it can advertise itself as a
high-priority emergency Recovery Vault.

This is especially attractive during development because rescue data leaves the
Pi immediately.

### NAS / SFTP / local server
User-owned LAN destination.

### Another Beast
Optional trusted peer recovery destination with explicit pairing and storage
policy.

### Restic repository
Encrypted deduplicating snapshot backend supporting local, SFTP, object
storage and additional backends.

### rclone transport / crypt
Optional transport to a user-selected provider, with client-side encryption
when configured.

No cloud provider is mandatory and Beastagotchi should not operate a central
backup cloud by default.

### Recovery Vault policy

User can configure ordered preferences such as:

1. attached USB SSD;
2. BenchLink laptop;
3. home NAS;
4. encrypted remote vault.

Each provider reports:
- reachable;
- independent from source media;
- free capacity;
- encryption;
- estimated transfer class;
- last successful verification;
- allowed backup tiers.

Doctor/Recovery Coordinator can select the safest valid destination under the
configured policy.

---

## 7. Emergency Rescue Protocol

Storage failure is a special case.

If Doctor sees high-confidence serious media/filesystem trouble:

### Phase 1 — Stabilize
- stop avoidable writes where practical;
- reduce nonessential logging/indexing;
- do not start large local archives on the suspect medium.

### Phase 2 — Find independent Recovery Vault
Prefer:
- already mounted external healthy storage;
- connected BenchLink;
- configured reachable NAS/SFTP;
- encrypted remote if connectivity is healthy.

### Phase 3 — Rescue irreplaceable state first
Copy the smallest high-value set:
- Beast DB/roster/progression/memories;
- Pwnagotchi/Beast configs;
- custom plugins/Packs/Experiences;
- display/touch configuration;
- critical manifests/secrets according to policy.

Verify destination copies/checksums.

### Phase 4 — Capture recovery metadata
- system/build fingerprint;
- package/provider inventory;
- recent Doctor/incident evidence;
- filesystem/storage evidence;
- restore manifest.

### Phase 5 — Expand only if safe
Attempt Rebuild Bundle, then larger backup/image only if source reads remain
stable and the operation makes sense.

This prevents an emergency backup from worsening a failing SD.

---

## 8. Autonomous recovery boundaries

Allowed automatic behavior should be explicit and proportional.

Examples that may be reasonable when pre-authorized:
- create tiny transaction snapshot;
- create Critical State backup to a configured healthy Recovery Vault;
- pause nonessential writes after filesystem distress;
- switch to Safe Experience after repeated UI crash;
- create incident/support evidence;
- notify user urgently.

Require owner approval for:
- broad package mutation;
- filesystem repair;
- destructive cleanup;
- raw/full-media imaging;
- restore over current state;
- credential/cloud reconfiguration.

Emergency automation policy must be configurable.

---

## 9. Headless Doctor is a core requirement

Doctor must not depend on the TFT working.

A user with:
- no screen;
- broken display config;
- failed theme/presentation;
- touch failure;
- headless build

must still be able to access the same Doctor through:
- Beast Studio/WebUI;
- BenchLink;
- local API;
- optional support bundle;
- future companion.

The TFT, WebUI and phone are **views of one Doctor**, not separate diagnostic
systems.

---

## 10. Backup/Doctor/Deep-Link cohesion example

Doctor detects:
- repeated MMC I/O errors;
- filesystem still writable;
- attached USB SSD healthy;
- Critical State backup 9 days old.

Doctor creates one incident:

**STORAGE — CRITICAL**

Evidence:
- repeated MMC errors;
- source medium likely unstable.

Recommended:
1. reduce nonessential writes;
2. rescue Critical State to USB SSD;
3. verify;
4. prepare replacement SD.

Actions:
- [Show evidence]
- [Open storage runbook]
- [Rescue Critical State to USB SSD]
- [Open Backup Center]
- [Create support bundle]

Each action is a semantic Beast Link/Action.

If the user approves rescue, the Recovery Coordinator executes the bounded
transaction and Doctor verifies the result.

This is the intended meaning of **cohesive**.

---

## 11. Portability testing policy

Beast should grow a validation matrix, not merely a compatibility claim.

Suggested classes:

- Reference: Pi 4 8GB + 480×320 ILI9486.
- Constrained reference: Zero 2 W-class.
- High-performance reference: Pi 5-class.
- Large-display reference: HDMI/DSI/tablet-like touch.
- Generic ARM64 Debian/systemd SBC fixture/CI where hardware-independent code can
  be tested.

Support labels should distinguish:
- source-tested;
- emulated/off-screen tested;
- community-reported;
- physically validated.

Never claim equal hardware validation merely because the Python code imports.

---

## 12. Immediate consequences

- Adaptive Platform Profile is now code, not merely a roadmap note.
- Experience Compiler must consume platform/display profile.
- Scene runtime should support target variants and resource classes.
- Recovery Vault becomes a capability/provider family.
- Restic/rclone are cataloged candidates, not mandatory dependencies.
- Doctor terminology remains unified; specialists are probes/views.
- Deep Links become a shared navigation/help contract.
- Backup architecture adds Rollback/Known-Good Snapshots and independent
  Recovery Vault destinations.
- BenchLink should advertise recovery capability when a trusted laptop is
  connected.
