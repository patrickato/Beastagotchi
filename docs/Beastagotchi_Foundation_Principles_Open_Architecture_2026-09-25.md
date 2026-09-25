# Beastagotchi Foundation Principles & Open Architecture Notes

**Date:** 2026-09-25  
**Status:** active architectural guidance / discussion record  
**Purpose:** preserve owner intent and architectural constraints without prematurely freezing implementation

## 1. Structure and architecture are first-class product work

Beastagotchi's foundation is not merely an implementation detail. The structure and architecture
determine how much the project can grow without becoming brittle, slow, dangerous or creatively
restricted.

Therefore foundation work may deliberately pause feature accumulation long enough to:
- inspect current ownership/layer boundaries;
- identify accidental ceilings;
- replace repeated switch/dispatch logic with registries where growth is intended;
- harden truth, provenance, persistence, transaction and recovery contracts;
- loosen presentation/content extension points;
- reduce duplicated orchestration;
- improve module/resource lifecycle;
- preserve compatibility while refactoring incrementally.

The project should prefer **evolution behind stable contracts** over flag-day rewrites.

---

## 2. No arbitrary product ceilings

Do not impose arbitrary upper limits on:
- Experiences;
- pages;
- Scenes;
- layers;
- Packs;
- faces;
- apps;
- overlays;
- visual families;
- renderers;
- hardware providers;
- optional content;
- user/community-created extensions;

unless a real hardware, resource, usability, safety, data-integrity or maintainability constraint
requires one.

Small curated defaults are desirable for usability. Defaults are not architectural limits.

A bounded *primary navigation surface* may exist while the total page/app/content universe remains
open-ended.

---

## 3. Reference Experiences are examples, not roots

Atlas, Forge, Observatory, Habitat and Monolith are Gate-1 reference/proof Experiences.

They demonstrate structural variety and validate the Experience-DNA/Scene model. They are not:
- a closed set;
- five root categories;
- the only valid aesthetic directions;
- a taxonomy users/community content must fit inside.

Built-in family names are organizing vocabulary. Namespaced extension vocabulary is permitted and
should remain possible.

---

## 4. Hard kernel, wild ecosystem — with owner sovereignty

The project benefits from a small dependable semantic kernel:
- Signal;
- Event;
- Action;
- Capability;
- Scene;
- Experience;
- Transaction;
- Persistence;
- Identity;
- Policy/provenance.

These contracts should be strict enough to keep truth, compatibility, rollback and diagnostics
understandable.

However, "hard" must not mean "owner cannot override their own machine."

Managed defaults should be:
- safe;
- recoverable;
- supportable;
- clearly explained.

Technically possible unsupported/customized operations should still have explicit owner paths,
such as:
- Expert Mode;
- administrator session;
- manual configuration;
- direct local shell/root escape hatch.

When policy is overridden:
- mark the installation customized/unsupported where applicable;
- preserve audit/provenance;
- warn about compatibility/rollback implications;
- do not pretend a policy preference is a technical impossibility.

Technical impossibility, policy refusal and unsupported-owner override are distinct concepts.

The owner retains sovereignty over the local open-source machine.

---

## 5. Large universe, lean active runtime

The project may become very large in available capability/content.

That does **not** mean all capability/content should:
- be running;
- be decoded into RAM;
- poll hardware;
- consume CPU;
- wake services;
- remain resident in the active filesystem working set.

Architectural target:
- broad installed/discoverable universe;
- small active working set;
- dormant optional providers;
- cached assets only when useful;
- lazy loading;
- bounded decoded-art caches;
- per-module resource attribution;
- adaptive update cadences;
- inactive Scenes/Experiences dormant;
- resource cost visible in Studio/Doctor/Performance Lens.

Thermal behavior—especially on Raspberry Pi 4—is a first-class engineering concern.

The preferred solution is efficient architecture and scheduling rather than arbitrarily deleting
features or relying on chronic throttling.

---

## 6. Optional content storage is not "USB required"

Future content architecture should not assume an always-connected external USB device.

Preferred model:
- **system SD** contains the core runtime, currently active content, essential fallbacks and a
  configurable local content/cache budget;
- **optional local storage** may include larger SD cards, secondary partitions, USB/SSD, etc.;
- **optional network/library sources** may include NAS or user-controlled machines;
- **remote catalog/depot** may advertise optional content where connectivity is available;
- active content may be copied/cached locally before use so loss of an external source does not
  break the active Experience unexpectedly.

A user with only one large SD card should have a complete, pleasant system.

External storage is an optional expansion path, not a basic requirement.

Packs/content may be installable at different granularity where the media format permits it:
- full Pack;
- optional component/module;
- asset subset;
- target/display variant;
- language/sound/art bundle;
- high-resolution extras.

Pack authors may also intentionally publish indivisible small Packs where splitting adds no value.

---

## 7. Future complete Beastagotchi distribution / installer

Explore a polished distribution/provisioning path that can produce a highly complete supported
system rather than requiring users to assemble dozens of pieces manually.

Possible goals:
- supported Jayofelony/Pwnagotchi base;
- Beastagotchi;
- compatible Beast-owned plugins/Packs/apps;
- selected external compatible integrations where licensing and project rules permit;
- dependency/package resolution;
- service setup;
- display/touch setup profiles;
- filesystem/SD expansion;
- first-boot validation;
- recovery baseline;
- known-good fingerprint;
- update/rollback path;
- optional content selection;
- plugin availability with explicit enable/opt-in where appropriate;
- owner choice between minimal / recommended / maximal profiles.

Important distinction:
- architecture/provisioning can support third-party components;
- redistribution rights/licenses must be independently verified;
- where redistribution is not permitted, installer recipes may acquire from the original source or
  guide the user instead of bundling the bytes;
- potentially sensitive/risky functionality must remain appropriately opt-in and governed by
  project distribution policy.

The "complete" experience should mean **complete orchestration**, not necessarily one giant archive
containing every third-party file.

---

## 8. Community contribution highway

Long-term project infrastructure should make it easy for users to contribute:
- issue/report;
- support bundle;
- hardware/profile evidence;
- Experience/Pack submission;
- plugin compatibility result;
- feature proposal;
- fix/PR;
- benchmark;
- physical-validation result.

Useful future tooling may pre-fill sanitized:
- Beast version;
- platform fingerprint;
- relevant provider versions;
- Doctor findings;
- error signatures;
- selected logs;
- compatibility data;

while excluding secrets/captures/location by default.

The goal is to turn real-world user diversity into useful project evidence rather than anecdotal
noise.

---

## 9. Optional Beast creation / birth / hatch / assembly layer

The digital-pet heritage is architecturally relevant but should not force mandatory "care chores."

Explore an optional lifecycle/choreography layer around initial Beast creation:
- owner makes initial choices;
- lineage/form/Experience inputs resolve;
- creation/assembly/incubation sequence;
- egg/pod/crate/foundry/robot/alien/etc. presentation appropriate to chosen content;
- hatch/birth/reveal cinematic;
- identity naming/reveal;
- celebratory first-state moment;
- transition into normal Beastagotchi runtime.

This should preferably be **content/choreography driven**, not hardwired to "all Beasts hatch from
eggs."

Different Packs/lineages may define:
- hatch;
- assemble;
- boot;
- awaken;
- excavate;
- summon;
- grow;
- discover;
- decode;
- emerge;

or another creation grammar entirely.

After creation, Beastagotchi should continue to grow primarily from real operation/progression.
Optional owner interaction may deepen:
- relationship;
- hidden triggers;
- achievements;
- Rare Moments;
- secrets;
- lineage;
- cosmetics;
- memories;
- contextual behavior;

without turning the system into a mandatory feeding/cleaning punishment loop.

No artificial death/neglect mechanic is required merely because Tamagotchi had one.

---

## 10. Efficiency research should exploit the established ecosystem

Beastagotchi should actively learn from established Raspberry Pi / Linux / Python practice rather
than reinventing every solution.

Research sources may include:
- upstream Linux/kernel/systemd documentation;
- Raspberry Pi engineering documentation;
- Python profiling/concurrency/runtime guidance;
- mature embedded/edge projects;
- open-source dashboards/appliances;
- forums/blogs/community reports;
- relevant Reddit/community discussions;
- hardware-specific benchmarks.

Candidate research topics:
- event-driven vs polling data paths;
- systemd socket/path/timer activation;
- process/service lifecycle;
- cgroups/resource accounting;
- I/O scheduling/write reduction;
- tmpfs/volatile caches;
- SQLite/WAL tuning;
- journald/log retention;
- framebuffer update efficiency;
- PIL/Pillow cache/resize/compositing patterns;
- asyncio/thread scheduling;
- thermal/cooling behavior;
- CPU governor behavior;
- hardware acceleration where practical;
- asset compression/decoding;
- memory-mapped/read-only assets;
- lazy imports/loading;
- service sandboxing;
- watchdog/restart strategies.

Adopt techniques based on measurement and fit, not novelty.

---

## 11. Foundation review priorities

Current high-leverage areas for deep review:
1. Page / Action / renderer / overlay / Signal-spec / module registries.
2. Decomposition of growing coordinators such as BeastUI, BeastCore orchestration and Beast Studio
   server without multiplying processes unnecessarily.
3. Generalized Transaction Engine.
4. Scene Specification -> Compiler -> Runtime/Scheduler -> Renderer -> Framebuffer separation.
5. Active-working-set / content-store / cache architecture.
6. Event semantics: durability, correlation, causation, privacy, delivery expectations.
7. WebSocket patch-driven UI feed with snapshot/resync fallback.
8. Module lifecycle/scheduler replacing repeated hand-written polling loops where beneficial.
9. SQLite repository boundaries while keeping one simple local database.
10. Stable third-party extension/SDK contracts and explicit ownership boundaries.

---

## Principle

**Harden the plumbing. Loosen the creativity.**

The project should be extremely dependable about truth, mutation, provenance, persistence,
compatibility and recovery while remaining unusually permissive about what users can create,
install, display, combine, extend and customize.
