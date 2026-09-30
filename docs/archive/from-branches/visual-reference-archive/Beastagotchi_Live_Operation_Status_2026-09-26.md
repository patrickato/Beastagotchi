# Beastagotchi Live Operation Status / Progress Pattern

**Date:** 2026-09-26  
**Status:** strong candidate cross-cutting platform requirement; preserve for final reconciliation

## Core principle

> **When Beastagotchi is doing meaningful work, the owner should be able to see what it is doing now, what stage it is in, what remains, and whether it is waiting on anything.**

People trust systems more when visible progress is truthful and current. Beastagotchi should therefore expose live operation status for long-running or multi-step work without forcing every subsystem to invent its own progress UI.

## Cross-cutting scope

Potential consumers include:
- Doctor diagnosis/repair;
- Actions / Transactions / Procedures;
- queued acquisitions/downloads;
- Home Base jobs;
- backups / restore / verification;
- updates / staging / installation;
- Pack installation;
- indexing / Search / Field Library imports;
- offline map/data acquisition;
- Guided Software setup;
- SDR scans/decoders where long-running work is explicit;
- migrations;
- cleanup/housekeeping;
- Sandbox/test runs where surfaced to the owner.

This should be a shared progress/status contract, not dozens of unrelated progress bars.

## Truthful progress rule

Do not fabricate percentages.

### Determinate work
If the total is genuinely known, expose real measurable progress, for example:
- 47 / 100 files;
- 312 MB / 900 MB;
- 8 / 12 validation checks;
- 73% only when derived from real measurable work.

### Indeterminate/staged work
If a truthful percentage cannot be known, show current stage and live activity, for example:

> Diagnosing -> Comparing Known-Good -> Fetching Driver -> Verifying -> Installing -> Reboot Required -> Testing

Use spinner/pulse/stage count/time-active/recent-message rather than fake "63%".

## Candidate operation status model

A long-running managed operation may expose:
- operation id;
- parent/correlation id;
- title / plain-language purpose;
- current state: queued / running / waiting / blocked / succeeded / failed / rolled-back / cancelled;
- current phase;
- current step and total steps when meaningful;
- measured completed/total units where meaningful;
- start time / elapsed duration;
- current activity text;
- last meaningful update;
- blocker / waiting reason;
- whether owner input is required;
- cancel/pause/resume availability where technically safe;
- link to technical details / Transaction / Procedure / Doctor case;
- final verification result.

## Presentation behavior

The same operation can be surfaced at multiple depths:

### Compact
Small status strip/icon/toast:
> Doctor: Testing radio repair...

### Expanded
Current phases and progress:
> 4 of 6 — Verifying monitor interface

### Technical details
Exact Procedure/Action/Transaction, probes, stdout/stderr, artifacts and evidence for expert/Owner Space users.

This supports "simple enough for beginners, complete enough for experts."

## Doctor-specific behavior

Owner selected **Option C** for Doctor proactivity/presentation:

> **Quiet caretaker by default, visibly communicative when Doctor is opened, an important issue occurs, approval/input is required, or verbose/expert mode is enabled.**

Examples:

Normal background repair:
> Doctor corrected a transient provider fault.

Owner-visible active case:
> Checking radio pipeline...
> Monitor interface present.
> Bettercap running but packet flow is flat.
> Testing channel/driver path...

Approval needed:
> Cause identified. A driver/package change is required. Review repair plan.

This can later use Beast/creature presentation/choreography where appropriate, but the underlying status must remain technically truthful.

## Anti-goals

- no fake percentages;
- no meaningless animation with no current status underneath;
- no forced popups for every tiny background action;
- no separate progress implementation for each subsystem;
- no hiding a stalled/blocked operation behind an endless spinner;
- no claiming success before functional verification.

## Architecture fit

Prefer a shared operation/progress event/state contract consumed by TFT UI, Studio/WebUI, notifications and relevant APIs.

It should correlate naturally with:
- Action;
- Transaction;
- Procedure;
- Doctor case/Incident;
- Acquisition Queue;
- future Task/Job runtime.

Do not invent a parallel execution engine merely to provide progress reporting.

## Status

Preserve as a strong candidate requirement. Exact schema/UI implementation remains for architecture reconciliation/build planning.
