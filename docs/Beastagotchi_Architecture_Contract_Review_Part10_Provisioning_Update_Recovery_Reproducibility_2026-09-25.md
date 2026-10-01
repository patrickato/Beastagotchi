# Beastagotchi Architecture Contract Review — Part 10: Provisioning, Update, Recovery & Reproducibility

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** Architecture Parts 1-9, completed Structure Deep Dive, current development-safe installers,
BackupManager, Pack update/probation/rollback work, SupportBundle privacy boundary, Recovery Vault/
known-good direction, owner offline/local-first and owner-sovereignty guidance.

---

# 1. Purpose

Beastagotchi eventually needs to be installable and recoverable by people who did not participate in
its development.

The lifecycle platform must support:

- adding Beastagotchi to an existing supported Pwnagotchi;
- building reproducible Beast-ready images;
- optional prebuilt images where licensing permits;
- first boot;
- component/profile selection;
- upgrades;
- migrations;
- rollback;
- backup;
- restore;
- device rebuild;
- offline preparation;
- rescue from broken UI/Core/storage;
- uninstall/detach;
- support evidence;
- exact artifact provenance.

The goal is not merely:

> "installation succeeded."

The goal is:

> **the owner can explain, reproduce, repair, update and if necessary remove what Beastagotchi did.**

---

# 2. Current behavior worth protecting

Current development tooling already demonstrates the desired caution.

## Core install

Current install:
- preserves existing Beast config;
- preserves existing database;
- installs code/services;
- does not automatically enable/start Core.

## UI install

Current UI install:
- validates the expected Pwnagotchi Python/Pillow environment;
- preserves existing touch calibration;
- refuses to invent calibration when none exists;
- leaves Beast UI stopped/disabled;
- protects physical display ownership.

## Uninstall

Current uninstall:
- releases display ownership where possible;
- removes runtime/services;
- preserves Beast config/history/database.

## Backup

Current BackupManager:
- uses SQLite online backup;
- limits known source paths;
- inspects archive structure;
- rejects traversal/links;
- quick-checks staged SQLite;
- stages restore data away from live paths;
- deliberately does not apply restore directly.

## Pack updates

Current Pack update flow:
- verifies source/staging;
- checks compatibility;
- installs transactionally;
- performs probation;
- attempts rollback when probation fails;
- does not silently activate the updated Pack.

## Support bundle

Current support bundle:
- is sanitized by default;
- excludes credentials;
- excludes raw AP/client/network identifiers;
- excludes GPS coordinates;
- excludes raw Pwnagotchi logs.

These are foundation strengths.

---

# 3. Provisioner

Introduce a first-class **Beast Provisioner**.

Provisioner is the orchestration layer for:

- install;
- first boot;
- profile selection;
- dependency closure;
- upgrade preparation;
- rebuild;
- detach/uninstall planning.

It consumes:

- platform discovery;
- PwnagotchiAdapter;
- Device BOM/Profile;
- Content Store;
- Dependency/Capability Resolver;
- Storage Budget Manager;
- Transaction Engine;
- Recovery Vault;
- Doctor/verification evidence.

It does not invent its own mutation path.

Consequential changes execute through registered Actions/Transactions.

---

# 4. Provisioning lifecycle

Canonical lifecycle:

    discover
      ->
    compatibility/preflight
      ->
    plan
      ->
    owner choices/consent
      ->
    rescue point / backup
      ->
    acquire
      ->
    verify artifacts
      ->
    install/configure
      ->
    migrate
      ->
    start/probation
      ->
    validate
      ->
    create known-good
      ->
    first-run/genesis
      ->
    handoff

Every stage is inspectable.

Power loss/restart should resume or recover safely.

---

# 5. Discovery

Provisioner discovers actual local truth:

- board/model/architecture;
- RAM/CPU;
- storage topology;
- free space/reserve;
- exact Pwnagotchi/Jayofelony version/build;
- Bettercap/runtime;
- Python environment;
- display/touch;
- current presentation owner;
- plugins;
- services;
- hardware providers;
- existing Beast state;
- existing customizations;
- Recovery Vault availability;
- network/Internet availability.

Do not hard-code one supported Pi path where capability evidence can answer the question.

---

# 6. Plan before mutation

Provisioner presents a complete plan where practical.

Plan includes:

- components added/removed/changed;
- source/version/hash;
- package/service changes;
- config files touched;
- expected downloads;
- installed bytes;
- temporary peak bytes;
- post-operation reserve;
- service restarts;
- reboot requirement;
- presentation-owner implications;
- migrations;
- backup/rescue point;
- rollback path;
- unknowns/blockers;
- requested owner choices.

Unknown remains unknown.

---

# 7. Distribution Profile

A Distribution Profile describes the intended product composition class.

Possible profiles:

## Core / Minimal

- Beast Core;
- UI/Studio;
- Doctor essentials;
- safe fallback Experience;
- essential dependencies.

## Recommended

- common project-owned Experiences/content;
- normal Doctor/Procedures;
- broadly useful integrations installed dormant where appropriate.

## Full

- broad project-owned optional ecosystem fitting available storage;
- larger local content set;
- still not "everything enabled."

## Custom

Owner-selected component/content/capability closure.

## Reference / Development Monster Build

- broad compatibility universe;
- developer/diagnostic tooling;
- validation/reference content.

All profiles remain one Beastagotchi architecture.

---

# 8. Device BOM

The **Device Bill of Materials** is the reproducible description of expected device composition.

Candidate fields:

- base/upstream image/distribution id;
- upstream source/hash/version;
- Beast version/commit/build;
- kernel/SDK contract versions;
- Python/runtime;
- OS/package dependencies;
- schema/migration level;
- hardware/display/touch profiles;
- selected Beast components;
- plugins/integrations;
- Pack/content versions/hashes;
- Collections;
- provider preferences;
- storage profile;
- known validation suite;
- known-good fingerprint;
- customized-state references.

A BOM is not a backup and not a Collection.

---

# 9. Rebuild Manifest

**Recommended new object:** a privacy-aware **Rebuild Manifest** derived from Device BOM + current owner selections.

Purpose:

> recreate the same logical Beastagotchi installation without necessarily cloning every byte.

It may contain:

- exact component ids/versions/hashes;
- original acquisition sources;
- selected content;
- required dependencies;
- display/touch profile identifiers;
- schema versions;
- enabled/active states;
- provider preferences;
- owner-created content references;
- expected validation checks;
- omitted-secret placeholders.

It should not contain secret values by default.

This enables:
- Clone My Setup;
- reinstall after SD failure;
- migrate to a larger card;
- reproduce a support environment;
- build offline recovery media.

---

# 10. Backup versus rebuild versus image

Keep three concepts distinct.

## Backup

Preserves irreplaceable/current data.

## Rebuild Manifest

Describes reproducible composition and sources.

## Full-system image

Copies broad filesystem/device state.

A full image is not always the best recovery artifact.

Large caches/reacquirable content may not need to be copied into normal backups.

---

# 11. Recovery ladder

Use distinct recovery scopes.

## Transaction micro-snapshot

Small before-state needed for one mutation.

## Rollback Snapshot

Application/component state needed to reverse a change.

## Known-Good Snapshot

A verified application-level checkpoint with provenance.

## Critical State Backup

Smallest irreplaceable owner/system state.

## Rebuild Bundle

Critical state + Rebuild Manifest + sources/hashes/metadata needed to reconstruct.

## Full Offline Backup

Critical state plus selected/pinned content for offline recovery.

## Full-system/Bare-metal image

Optional comprehensive imaging where appropriate.

## Emergency Rescue

Minimal independent path to recover irreplaceable data from a failing/broken system.

Do not confuse these scopes.

---

# 12. Known-Good checkpoint

Known-Good means:

- explicit checkpoint;
- verification completed;
- source/build known;
- relevant component fingerprint known;
- compatibility/support state recorded;
- Doctor/health evidence recorded;
- owner/customization state recorded.

It does not mean "perfect forever."

Known-Good is a comparison point.

---

# 13. Recovery Vault

Recovery Vault is a provider capability, not one directory.

Possible Vaults:

- USB flash/SSD/HDD;
- second healthy filesystem;
- BenchLink laptop;
- NAS/SFTP/local server;
- another explicitly paired Beast;
- restic repository;
- rclone-backed destination;
- future encrypted owner-controlled store.

No cloud is mandatory.

Vault declares:

- capacity/free space;
- health/readiness;
- encryption/protection;
- transport;
- retention;
- supported backup classes;
- verification capability.

---

# 14. Emergency rescue protocol

For suspected failing SD/storage:

1. reduce unnecessary writes;
2. assess readable state;
3. locate independent healthy Recovery Vault;
4. rescue smallest irreplaceable Critical State first;
5. verify destination checksum;
6. save build/recovery metadata;
7. expand recovery only if source remains stable and useful.

Do not immediately hammer a failing card with the largest possible image read.

---

# 15. Restore Transaction

Live restore is a first-class Transaction.

Lifecycle:

    inspect archive
      ->
    verify manifest/hash/structure
      ->
    stage isolated
      ->
    dry-run diff
      ->
    owner confirmation
      ->
    create rescue backup
      ->
    quiesce affected services
      ->
    validate staging again
      ->
    apply
      ->
    migrate if required
      ->
    restart
      ->
    probation
      ->
    verify
      ->
    commit
         or rollback to rescue state

Restore cannot be one unchecked extract-over-live command.

---

# 16. Restore independence

Recovery must not depend exclusively on the subsystem being recovered.

Provide a minimal rescue path such as:

- CLI;
- systemd rescue helper;
- boot-time recovery command;
- offline/recovery media path.

If Studio is broken, Studio cannot be the only restore UI.

If Core DB is broken, the restore engine cannot require that same DB to boot normally first.

---

# 17. First boot as a state machine

Future Beast-ready distribution uses resumable first boot.

Possible stages:

1. storage/filesystem expansion where safe;
2. platform discovery;
3. upstream Pwnagotchi health;
4. Beast DB/schema initialization;
5. display/touch detection;
6. network state;
7. owner setup;
8. install/profile/content selection;
9. provider/plugin choices;
10. stack validation;
11. initial backup/rescue checkpoint;
12. Doctor Patient Chart identity/coverage;
13. first known-good checkpoint;
14. optional Genesis/creation Choreography;
15. normal runtime handoff.

Every completed stage is recorded.

Power loss does not restart destructive steps blindly.

---

# 18. Idempotency

Provisioning steps declare whether they are:

- idempotent;
- resume-safe;
- one-shot;
- verification-only;
- rollback-required.

After restart, Provisioner checks actual state before repeating work.

Never blindly replay a mutating step because a boolean says "unfinished."

---

# 19. Upstream adapter

Pwnagotchi/Jayofelony environment knowledge should live behind a versioned adapter.

Adapter owns knowledge such as:

- configuration locations;
- service names;
- Python environment;
- framebuffer/native-frame paths;
- storage layout;
- supported update strategy;
- plugin locations;
- release/version evidence.

This prevents upstream assumptions from spreading through Beast code.

---

# 20. Upstream platform update

Updating Pwnagotchi/Jayofelony is a special platform Transaction.

Plan includes:

- exact source/version/hash;
- Beast compatibility;
- adapter compatibility;
- owner config/state preservation;
- plugin/integration compatibility;
- migration;
- Pwnagotchi/Bettercap validation;
- Beast bridge validation;
- presentation validation;
- recovery strategy.

A major image replacement may require export/re-provision rather than pretending file rollback can undo an entire image change.

---

# 21. Component UpdateAdapter

Different components update differently.

Use typed adapters for:

- Beast Core;
- Beast UI/Studio;
- Beast Pack;
- plugin/integration;
- Theme Manager;
- Pwnagotchi platform;
- future firmware/hardware helpers.

Each adapter knows:

- quiesce;
- snapshot;
- stage;
- apply;
- restart/reload;
- probation;
- verification;
- rollback.

Do not use one "replace directory and restart" algorithm for everything.

---

# 22. Update discovery versus installation

Update flow keeps stages distinct:

    discover
      ->
    compatibility
      ->
    notify/select
      ->
    stage
      ->
    verify
      ->
    plan permission/dependency/migration diff
      ->
    apply Transaction
      ->
    probation
      ->
    verify
      ->
    commit/rollback

Automatic discovery does not imply automatic application.

---

# 23. Update policy

Per component class owner policy may support:

- manual;
- notify;
- auto-stage;
- auto-install where explicitly proven safe.

High-impact platform/Pwnagotchi/display-owner updates remain conservative.

Automatic mutation requires evidence-backed rollback/probation.

---

# 24. Update probation

Apply success is not update success.

Probation may inspect:

- Core health;
- Pwnagotchi/Bettercap state;
- filesystem read-only status;
- presentation conflicts;
- provider/module health;
- database integrity;
- expected Signals;
- UI render health;
- extension health.

Verification is component-specific.

Unknown evidence remains unknown.

---

# 25. Artifact provenance

Every official/staged update records:

- source;
- exact version;
- commit/build;
- SHA-256 or stronger artifact digest;
- signature/publisher evidence if used;
- acquisition time;
- compatibility result;
- tested evidence;
- Transaction id.

A Git branch name alone is not a release artifact identity.

---

# 26. Tested artifact = released artifact

Official release discipline:

- freeze source;
- build artifact;
- hash/sign as appropriate;
- test that artifact;
- physically validate exact artifact where required;
- publish the exact tested artifact.

Do not validate one commit and then release a different working tree.

---

# 27. Artifact signing

Signatures may strengthen:

- publisher identity;
- artifact integrity;
- release provenance.

Signatures do not prove:

- compatibility;
- correctness;
- safety.

Unsigned owner-local builds remain possible.

---

# 28. Schema migration

Use explicit ordered schema migrations.

Prefer:

- SQLite user_version or equivalent canonical migration level;
- one-way migration steps with documented rollback/recovery;
- idempotent detection;
- tests from supported old versions;
- backup before consequential migration.

Do not scatter ad-hoc "if column missing then alter" logic indefinitely.

---

# 29. Migration compatibility window

Public releases should document which prior states can upgrade directly.

Examples:

- direct supported;
- requires intermediate migration;
- export/rebuild recommended;
- unsupported/unknown.

Do not silently attempt an untested multi-year schema jump.

---

# 30. Rollback and migration

Rollback is easiest before irreversible migration.

If an update requires irreversible data migration:

- snapshot old state;
- preserve prior schema copy;
- clearly mark rollback limits;
- verify migration before deleting old artifacts.

Where exact rollback is impossible, use compensating/re-provision recovery honestly.

---

# 31. Rescue plane

**Recommended new concept:** maintain a minimal **Beast Rescue Plane** independent of the rich runtime.

Purpose:

- inspect install;
- show version/BOM;
- verify DB;
- inspect backups;
- create emergency backup;
- restore;
- release display ownership;
- disable broken optional modules;
- generate sanitized support bundle;
- re-provision core components.

It should have minimal dependencies and work headless.

This is not a second full Beast Core.

It is a small recovery/control surface.

---

# 32. Rescue Plane trust boundary

Rescue operations are powerful.

Require:

- local/admin authorization;
- explicit plan;
- Transaction/provenance where applicable.

Keep rescue tooling small enough to audit.

Do not load arbitrary community extension code in Rescue Plane by default.

---

# 33. Recovery Media / Offline Rescue Kit

Future Procedure:

**PREPARE RECOVERY KIT**

May create owner-selected removable/local bundle containing:

- Critical State Backup;
- Rebuild Manifest;
- Beast release artifact;
- dependency/content manifests;
- selected offline content;
- checksums/signatures;
- rescue instructions/tools.

This allows recovery when Internet is unavailable.

---

# 34. Device Passport

**Recommended new owner-facing object:** Device Passport.

A compact human/machine-readable summary of:

- Beast version;
- upstream Pwnagotchi version;
- platform/display;
- Device BOM id/fingerprint;
- schema level;
- known-good checkpoint;
- support/customized state;
- active Experience;
- Recovery Vault status;
- last successful backup;
- last update Transaction;
- compatibility summary.

Think of this as "what exactly is this Beast?" rather than a verbose support dump.

It can be shown in Studio, CLI, QR/local file and support workflows.

Privacy-sensitive fields are excluded by default.

---

# 35. Clone My Setup

Using Device BOM + Rebuild Manifest + owner-selected backup:

- install supported base;
- acquire exact components;
- restore irreplaceable state;
- restore content selections;
- restore preferences;
- validate;
- create new known-good.

Secrets may require explicit re-entry rather than insecure copying.

Hardware-specific bindings may require reassignment.

Clone means logical composition, not necessarily bit-identical disk.

---

# 36. Backup scopes

Expose clear owner choices.

## Essential Backup

- identity/roster/progression;
- database;
- critical config;
- presentation preferences;
- owner-created metadata;
- rebuild manifest.

## Full Offline Backup

Essential + selected/pinned content required for offline function.

## Device Clone Bundle

Essential + BOM/Rebuild Manifest + enough selected state to reconstruct on another compatible device.

## Full Image

Optional lower-level imaging.

---

# 37. Backup encryption

Some backups contain sensitive configuration.

Support encrypted destinations/providers where practical.

Do not invent custom cryptography.

Use mature tools/formats/providers where appropriate.

Owner should understand whether a Vault is encrypted at rest and/or in transport.

---

# 38. Backup verification

A backup is not complete merely because archive creation returned success.

Verify:

- artifact readable;
- manifest valid;
- hashes valid;
- SQLite quick_check;
- expected critical files present;
- destination durable/readable.

Record verification result.

---

# 39. Restore rehearsal

Future optional Procedure:

**VERIFY MY RECOVERY**

May:

- inspect latest backup;
- stage into isolated location;
- validate DB/manifests;
- calculate restore plan;
- confirm source availability;
- report missing reproducible content;
- avoid mutating live system.

This catches broken backups before disaster.

---

# 40. Support Bundle

Support remains sanitized-by-default.

Future bundle may add:

- Device Passport;
- BOM fingerprint;
- extension Grant Receipts summary;
- Transaction summaries;
- known-good drift;
- compatibility explanations;
- Module health;
- presentation/session health.

Still exclude sensitive network/location/capture/secret data by default.

---

# 41. Contribution highway

Support and validation should flow naturally into contribution.

Possible Studio/CLI flows:

- Report a Problem;
- Submit Compatibility Result;
- Submit Physical Validation;
- Suggest Feature;
- Export Experience/Pack;
- Share Procedure;
- Build Issue Bundle;
- Copy sanitized diagnostics.

Do not require storing a GitHub personal access token on every Pi for basic participation.

---

# 42. Update/recovery and Doctor

Doctor consumes lifecycle evidence.

Doctor can say:

- update failed during probation;
- rollback succeeded;
- backup stale;
- Recovery Vault missing;
- current state drifted from known-good;
- schema migration incomplete;
- restore staged but not applied;
- BOM differs from expected;
- unsupported manual changes detected.

Doctor does not execute lifecycle mutation directly.

It links to Actions/Procedures.

---

# 43. Transaction Journal integration

All consequential lifecycle mutations reference the shared Transaction Journal.

Examples:

- install;
- update;
- restore;
- provider switch;
- presentation ownership;
- plugin activation;
- schema migration;
- Expert override.

This allows:

- one audit story;
- known-good drift explanation;
- Doctor timeline;
- support history;
- targeted rollback.

Avoid bespoke audit formats per subsystem.

---

# 44. Customized/manual state

Owner manual/root changes remain allowed.

Provisioner/Doctor may detect drift.

Possible handling:

- record customized state;
- explain difference from BOM/known-good;
- offer adopt/reconcile/revert paths;
- avoid pretending support guarantees still apply.

Do not forcibly undo owner changes.

---

# 45. Reconciliation

Future Procedure:

**RECONCILE MY DEVICE**

Compare:

- current device;
- expected BOM;
- known-good;
- selected Profile/Collection;
- manual/customized changes.

Classify:

- expected;
- missing;
- extra;
- drifted;
- unknown;
- intentionally customized.

Offer owner-controlled actions.

Do not blindly force desired state.

---

# 46. Storage reserve during lifecycle work

Install/update/restore plan must account for:

- download artifact;
- staged artifact;
- extracted/install bytes;
- rollback copy;
- DB/WAL growth;
- temporary migration space;
- safety reserve.

If peak cannot fit safely, block managed operation or offer alternate Vault/pool.

Do not begin and discover halfway through that rollback space is gone.

---

# 47. Network/offline behavior

Lifecycle operations should clearly state network requirements.

Support:

- online acquisition;
- local file;
- USB/SD;
- network library;
- pre-staged offline bundle.

Core runtime remains useful offline.

Provisioning/recovery should not assume cloud connectivity.

---

# 48. Licensing and acquisition

Provisioner may know how to acquire third-party components without redistributing them.

Track:

- original source;
- license;
- redistribution permission;
- hash/version;
- acquisition recipe.

Do not bundle third-party software merely because it is publicly downloadable.

---

# 49. First-run Genesis boundary

Genesis/creature creation happens only after platform state is stable enough.

Before Genesis:

- database valid;
- critical services healthy;
- presentation usable;
- identity storage durable;
- known-good created or intentionally deferred.

Do not create emotionally important Beast identity before storage/migration is known broken.

---

# 50. Uninstall / detach

Provide owner choices:

- disable Beast UI / return Native presentation;
- remove UI only;
- remove optional content;
- remove Beast runtime;
- export then remove;
- full purge.

Before removing physical owner:

- release/restore presentation ownership;
- verify fallback/native path where possible.

Preserve owner history by default unless full purge is explicitly chosen.

---

# 51. Full purge

Full purge is explicit and high-impact.

Plan identifies:

- code;
- services;
- config;
- database;
- roster/progression;
- owner content;
- backups;
- secrets;
- caches.

Require clear confirmation.

Offer export/backup first.

---

# 52. Decommission / transfer

Future Device Procedure may prepare a Pi for transfer/sale:

- export owner state;
- remove secrets;
- clear private network/location data;
- detach accounts/tokens;
- reset roster/profile where owner chooses;
- preserve software baseline if desired.

This is distinct from uninstall.

---

# 53. CI lifecycle gates

Automated lifecycle tests should cover:

- clean install plan;
- idempotent rerun;
- upgrade from supported prior schema;
- interrupted Transaction recovery;
- failed probation rollback;
- backup inspect/stage;
- malicious archive rejection;
- restore dry-run;
- permission/update diff;
- uninstall preservation;
- Rebuild Manifest determinism;
- BOM comparison;
- offline install path where practical.

---

# 54. Physical lifecycle validation

Real Pi gates are required for relevant operations:

- fresh install;
- update/restart;
- display-owner preservation;
- touch calibration preservation;
- reboot resume;
- recovery media;
- restore;
- low-space behavior;
- power-loss/restart recovery where safely testable.

Do not infer physical correctness solely from desktop CI.

---

# 55. Aha: rebuildability is more valuable than giant backups

Many Beast bytes will be reproducible:

- official code;
- Packs;
- media;
- dependencies;
- generated caches.

Preserve irreplaceable state and exact provenance, then reacquire reproducible bytes.

This can make recovery smaller, faster and more robust than copying everything forever.

---

# 56. Aha: Device Passport + Rebuild Manifest become the bridge between Doctor, support and Provisioner

The same compact composition identity can answer:

- Doctor: what changed?
- Support: what exactly are you running?
- Provisioner: what should be here?
- Recovery: what must be restored/reacquired?
- Clone: what do I reproduce?
- Owner: what is this machine?

One shared model prevents five inconsistent inventories.

---

# 57. Aha: Rescue Plane should remain boring

The recovery layer should intentionally be less creative than the main product.

No elaborate Experience dependency.
No giant plugin universe.
No need for the full compositor.

Its virtue is:

- small;
- predictable;
- inspectable;
- headless-capable;
- hard to break accidentally.

Beastagotchi can be wild above it because recovery stays boring below it.

---

# 58. Aha: successful mutation requires evidence, not optimism

Across install/update/restore:

- apply command success is not enough;
- service start success is not enough;
- file copy success is not enough.

Commit only after registered verification/probation evidence.

This is the lifecycle version of "unknown stays unknown."

---

# 59. Migration from current v0.19

Incremental path:

1. Define Device BOM/Rebuild Manifest schemas.
2. Add Device Passport read model.
3. Standardize component UpdateAdapter contract.
4. Add shared Transaction Engine/journal.
5. Link current Pack update into shared Transaction.
6. Add ordered SQLite schema migration ladder.
7. Build Restore Transaction over current inspect/stage behavior.
8. Add Recovery Vault provider registry.
9. Build minimal Rescue Plane CLI.
10. Convert install scripts into Provisioner adapters/stages rather than deleting them immediately.
11. Add idempotent first-boot state machine.
12. Add Reconcile/Verify Recovery read-only Procedures.
13. Add offline Recovery Kit generation.
14. Add upstream Pwnagotchi platform adapter/update strategy.
15. Add reproducible image builder.
16. Consider prebuilt image distribution only after licensing/maintenance decisions are resolved.

No flag-day replacement of working installers is required.

---

# 60. Lifecycle/recovery invariants

1. Plan before consequential mutation.
2. Apply success is not commit success.
3. Consequential lifecycle work uses Transaction.
4. Unknown verification remains unknown.
5. Every official artifact has exact provenance/hash.
6. Tested artifact is the released artifact.
7. Backup, Rebuild Manifest and full image are distinct.
8. Irreplaceable state is prioritized over reacquirable cache.
9. Restore stages and verifies before live apply.
10. Restore creates a rescue point first where feasible.
11. Recovery does not depend exclusively on the broken subsystem.
12. First boot is resumable/idempotent.
13. Lifecycle temporary peak storage is planned before mutation.
14. Small cards remain first-class.
15. Offline install/recovery is possible where artifacts are prepared.
16. Owner manual changes are not forcibly undone.
17. Customized state is described honestly.
18. Schema migrations are ordered/versioned.
19. Component classes may have different update adapters.
20. Physical presentation ownership is preserved during install/update/uninstall.
21. Touch calibration is preserved unless owner intentionally recalibrates.
22. Support bundles remain sanitized by default.
23. Recovery Vault is provider-based, not cloud-mandatory.
24. Full purge requires explicit owner intent.
25. Uninstall preserves owner history by default.
26. Rescue Plane stays minimal and independent.
27. BOM/Rebuild/Passport models do not contain secret values by default.
28. Lifecycle evidence feeds Doctor/known-good/support through common provenance.
29. Reproducible components should be reacquired rather than blindly duplicated forever.
30. Owner controls the machine even when managed support policy refuses an operation.

---

# 61. Part 10 conclusion

Beastagotchi should eventually be as easy to recover as it is exciting to customize.

The lifecycle foundation is:

- Provisioner plans;
- Device BOM describes composition;
- Rebuild Manifest describes reproducibility;
- Device Passport explains current identity;
- Transaction makes changes safe;
- Known-Good provides comparison;
- Recovery Vault preserves state;
- Rescue Plane works when the rich runtime does not;
- Doctor interprets lifecycle health;
- owner remains sovereign.

The next Architecture Contract Review should be the **Architecture Synthesis & Migration Plan**:
freeze the cross-part invariants, map current v0.19 components onto the target contracts, identify
the minimum new foundations that unlock the largest amount of future work, order implementation
into safe gates, define which contracts are stable versus still provisional, and prevent this
architecture review from becoming documentation that never reaches the running Pi.
