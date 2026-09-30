# Beastagotchi Procedure Idea Catalog

**Date:** 2026-09-25  
**Status:** idea catalog / architectural input  
**Purpose:** preserve useful Procedure concepts before implementation hardens the contract

A **Procedure** is a named, inspectable workflow composed from registered probes, Actions and
Transactions. It is not an opaque shell shortcut.

## Procedure result rule

If a Procedure discovers information that maps to a Doctor condition, the result should surface:
- Doctor status / advisory / diagnosis;
- severity;
- plain-language explanation;
- recommended next Action(s);
- direct navigation into Doctor / Patient Chart;
- direct owner-approved action where policy permits.

Example:

    STORAGE AUDIT COMPLETE
    1.4 GB safely reclaimable
    Doctor: 1 advisory
    WAL growth exceeds expected range

    [ VIEW DOCTOR ]
    [ CLEAN CACHE ]
    [ DETAILS ]

Procedure output and Doctor should reinforce each other rather than forcing the owner to manually
translate technical output into health meaning.

---

# PI / PLATFORM PROCEDURES

## Gather My Device Info
Read-only.
Collect:
- Pi model / RAM;
- OS/image;
- kernel;
- Python;
- storage;
- filesystem;
- display;
- touch;
- thermals;
- clocks/throttle state;
- network interfaces;
- services;
- package/runtime summary.

Outputs:
- clean summary;
- expert evidence;
- optional report file;
- Doctor advisories where applicable.

## Storage Audit
Read-only scan of:
- free space;
- protected reserve;
- large files;
- caches;
- old logs;
- stale support bundles;
- Pack versions;
- temporary render assets;
- SQLite/WAL size.

May offer:
- Clean Up Optional Cache;
- prune known-safe temporary data;
- open Doctor if storage health issue exists.

## Clean Up
Plan-first cleanup.
Possible safe categories:
- expired temp files;
- stale previews;
- superseded Pack downloads;
- evictable cached content;
- expired support bundles;
- old installer staging;
- old temporary render exports.

Never includes owner data/captures/recovery/active content unless explicitly selected.

## Thermal Snapshot
Collect:
- CPU temp;
- clocks;
- throttle flags;
- CPU utilization;
- load;
- per-service/process cost;
- governor state;
- recent thermal history.

Doctor may interpret persistent heat or throttling.

## Performance Snapshot
Collect:
- Beast CPU/RAM;
- top processes;
- UI render/write timings;
- framebuffer dirty ratio;
- service CPU/RSS;
- storage I/O;
- governor state.

## Service Health Audit
Read-only service inventory with state, restart count, recent failure evidence and Doctor mapping.

## Validate Display & Touch
Checks:
- framebuffer;
- geometry;
- driver/overlay;
- touch device;
- transform/calibration;
- presentation owner;
- physical-test readiness.

## Backup Before Trip
Plan/check free space, create validated backup/recovery checkpoint, verify archive, summarize result.

## Prepare Device for Upgrade
Check:
- storage reserve;
- backup;
- known-good state;
- package/Pack compatibility;
- power;
- network;
- current customized state.

## Recovery Intake
Collect a recovery-safe diagnostic bundle before mutation.

---

# PWNAGOTCHI-LAYER PROCEDURES

## Pwnagotchi Health Check
Read-only:
- service state;
- version;
- Bettercap;
- monitor interface;
- supported channels;
- plugin load state;
- config parse;
- capture path;
- recent errors.

Doctor maps relevant findings.

## Radio Diagnostic
Read-only staged checks:
- interface existence;
- monitor mode;
- channel activity;
- Bettercap state;
- regulatory constraints;
- AP visibility;
- capture-path sanity.

May offer owner-approved restart/recovery Actions.

## Plugin Health Audit
Inventory:
- installed;
- configured;
- enabled;
- loaded;
- failing;
- missing dependency;
- stale/incompatible;
- duplicate/conflicting provider.

## Config Sanity Check
Parse and validate known Pwnagotchi config without blindly modifying it.

## Capture Pipeline Check
Validate paths/permissions/state relevant to capture persistence without exposing captured content.

## Restart & Verify Pwnagotchi
Mutating.
Plan:
- restart;
- wait;
- verify service;
- verify radio;
- verify API/runtime recovery;
- report.

---

# BEASTAGOTCHI-LAYER PROCEDURES

## Full Doctor Checkup
Run Doctor's complete supported diagnostic suite and summarize Patient Chart status.

## Compare to Known-Good
Show drift by subsystem and link changes to override/transaction history where possible.

## Pack Health Audit
Check:
- Pack integrity;
- dependencies;
- compatibility;
- active references;
- broken assets;
- version/update state.

## Experience Health Audit
Check:
- active Experience;
- required Signals;
- missing optional Capabilities;
- Scene/render target compatibility;
- resource cost;
- missing assets;
- degraded fallbacks.

## Content Store Audit
Check:
- installed/cached/pinned objects;
- deduplication opportunities;
- orphaned objects;
- broken references;
- evictable cache;
- protected active set.

## Prepare for Offline Use
Given a saved collection / active setup:
- resolve required content;
- verify it is local;
- pin required assets;
- cache optional dependencies;
- validate storage reserve;
- generate offline-readiness result.

## Build Support Bundle
Privacy-aware support export with owner preview.

## Validate Known-Good Drift
Doctor-centric comparison and explanation of current deviations.

## Refresh Compatibility Information
Update local catalog/compatibility knowledge where connectivity exists; no silent activation.

## Validate Backup / Recovery
Prove that recovery material can be read and corresponds to the expected state.

## Performance / Thermal Check
Beast-focused interpretation of active UI/Scene/module cost.

---

# CROSS-LAYER PROCEDURES

## Gather Everything I Need for Support
Combines Pi + Pwnagotchi + Beast evidence into one privacy-reviewed support result.

## Complete Health Check
Pi -> Pwnagotchi -> Beastagotchi -> Doctor synthesis.

## Prepare for Offline Trip
Storage + content + GPS/provider + backup + Doctor + selected collection pinning.

## Prepare for Update
Pi storage/power + Pwnagotchi compatibility + Beast backup + Pack compatibility + Doctor clearance.

## Diagnose "Something Is Wrong"
Guided broad intake that narrows by evidence instead of making the owner pick the subsystem first.

## Validate Whole Stack
Checks:
- OS;
- Pwnagotchi;
- Bettercap;
- Beast Core;
- UI;
- Studio;
- plugins;
- Packs;
- presentation;
- storage;
- Doctor.

## Safe Restart Stack
Ordered restart/verification of relevant services with clear owner confirmation.

## Export My Device Profile
Sanitized shareable inventory for community/help requests.

---

# FUTURE / ADVANCED IDEAS

## Trip Mode Preparation
Select collection + offline content + navigation/GPS + power profile + backup + reduced logging if
appropriate.

## Benchmark My Beast
Controlled render/system benchmark with a clean result and comparison to prior local baseline.

## "Why Is This Slow?"
Guided performance triage using current resource evidence.

## "Why Is This Hot?"
Thermal causality procedure that correlates load, services, clocks, UI cost and ambient behavior.

## "What Changed?"
Transaction/override/update/change-history review since a selected date or known-good checkpoint.

## "Make This Shareable"
Take current Experience/face/collection/customization and produce an exportable Pack/collection
manifest where licensing/provenance permits.

## "Clone My Setup"
Generate a reproducible manifest of Beast-owned configuration/content choices for another device.

## "Reset Just This"
Scoped recovery procedure for one subsystem rather than factory-resetting the whole device.

## "Check Before I Leave"
Fast pre-trip/pre-field checklist:
- storage;
- battery/power;
- Doctor;
- GPS if expected;
- radio;
- active content local;
- backup age.

## "Explain This Device"
Human-readable system overview for owners who do not want raw Linux detail.

---

# Procedure UX principle

A Procedure should have:
1. plain-language purpose;
2. scope;
3. read-only/mutating label;
4. expected duration;
5. preview/plan;
6. consent where required;
7. live progress;
8. clean result;
9. Doctor interpretation;
10. next Actions;
11. raw evidence for experts;
12. artifact/report/export where useful.

A Procedure should never strand the owner at a technical result without an obvious next step when
Beastagotchi already knows the relevant Doctor or Action path.
