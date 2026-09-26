# Beastagotchi Architecture Contract Review — Part 4: Transactions & Procedures

**Date:** 2026-09-25  
**Status:** proposed architecture contract  
**Depends on:** Kernel, Authority/Ownership, Registries

---

# 1. Transaction and Procedure are different

## Transaction
A managed mutation safety envelope.

Question:
> "How do we change something consequential and prove it succeeded or recover safely?"

## Procedure
An owner/operator workflow.

Question:
> "How do we accomplish a useful multi-step goal using probes, Actions, Transactions and Doctor?"

A Procedure may invoke several Transactions.

A Transaction does not need to know about Procedure UX.

---

# 2. Transaction lifecycle

Canonical state machine:

    planned
       |
    preparing
       |
    prepared
       |
    applying
       |
    applied
       |
    probation
       |
    verifying
      /  verified failed
    |       |
 committing rolling_back
    |       |
 committed rolled_back

Additional terminal states:
- cancelled_before_apply;
- rollback_failed;
- indeterminate;
- superseded.

Do not report "success" merely because an apply command returned exit code 0.

---

# 3. TransactionSpec

Each transactional Action references a registered TransactionSpec or Transaction adapter.

Candidate fields:
- transaction type/id;
- schema/version;
- originating Action;
- actor;
- SubjectRef target;
- risk/consent class;
- required Capabilities;
- required storage/resources;
- preparation/snapshot adapter;
- apply steps;
- probation policy;
- verification checks;
- rollback/compensation adapter;
- restart/reboot policy;
- timeout policy;
- privacy/logging policy;
- Doctor hooks;
- support/recovery hints.

The spec is the recipe.
A TransactionRun is one execution instance.

---

# 4. TransactionRun journal

Every run receives a durable id.

Persist:
- id;
- spec id/version;
- Action id;
- actor;
- subject;
- correlation/causation refs;
- requested_at;
- state;
- state transition timestamps;
- plan snapshot;
- before fingerprint;
- artifacts/snapshots;
- step results;
- verification evidence;
- probation evidence;
- outcome;
- rollback evidence;
- after fingerprint;
- error;
- customization/override refs.

Journal writes should happen before dangerous boundaries where possible.

---

# 5. Crash/reboot recovery

A first-class Transaction must survive process/service interruption.

At startup, TransactionEngine scans non-terminal runs.

For each:
- inspect durable state;
- ask adapter how to recover/resume;
- determine whether apply occurred;
- verify external state;
- continue probation/verification;
- rollback if policy/evidence requires;
- otherwise mark indeterminate and require owner/Doctor intervention.

Never blindly replay a mutating step after restart unless it is explicitly idempotent.

---

# 6. Idempotency

Each step declares one of:

- read_only;
- idempotent;
- idempotent_with_key;
- non_idempotent;
- compensatable.

For mutating steps, persist completion evidence before moving to next step.

If an external operation supports idempotency keys, use TransactionRun id/step id.

For non-idempotent operations, recovery must inspect state rather than simply run again.

---

# 7. Snapshot and rollback are not always identical

"Rollback" may mean:

## Exact restore
Return to byte/state-identical prior state.

Examples:
- restore config file;
- restore prior inert Pack directory.

## Compensating action
Perform a safe inverse that returns service semantics, not identical bytes.

## Re-provision
Recreate the prior supported platform state from BOM + backup.

## Manual recovery
No safe automated inverse exists.

TransactionSpec must declare rollback capability honestly:
- exact;
- compensating;
- reprovision;
- manual;
- none.

UI/Doctor must not promise "fully reversible" when only best-effort compensation exists.

---

# 8. Transaction classes

## Local/simple transactional
No restart boundary.

Examples:
- Pack install;
- bounded content cleanup.

## Service-boundary
Requires stop/restart/quiesce.

Examples:
- plugin/config update;
- provider handoff.

## Presentation-boundary
Requires exclusive display/input ownership.

## Reboot-boundary
Transaction continues across device reboot.

## Platform/image-boundary
May require external backup/re-provision rather than ordinary rollback.

Examples:
- major Pwnagotchi/image update.

The same journal contract applies, but recovery adapters differ.

---

# 9. Probation

Some changes cannot be verified instantly.

Probation may include:
- minimum healthy runtime;
- no restart loop;
- required Signals fresh;
- provider remains available;
- display/input ownership stable;
- no new critical Doctor incident;
- resource/thermal budget within limits.

Probation policy declares:
- duration;
- sample cadence;
- pass conditions;
- fail-fast conditions;
- allowable degraded state.

Governor may reduce nonessential background work during probation so verification is meaningful.

---

# 10. Verification

Verification must be semantic.

Examples:

Bad:
- `systemctl restart` returned 0.

Good:
- service active;
- stayed active for N seconds;
- expected socket/API available;
- expected Signal fresh;
- no immediate restart loop;
- dependent Module healthy.

Verification result:
- pass;
- fail;
- unknown/insufficient_evidence.

Unknown is not pass.

---

# 11. TransactionEngine authority

TransactionEngine:
- executes registered transaction adapters;
- persists state transitions;
- enforces timeout/recovery;
- coordinates snapshots;
- invokes verification;
- invokes rollback;
- emits Events;
- exposes status.

It does not:
- decide owner policy by itself;
- invent Actions;
- bypass Action authorization;
- interpret Doctor health beyond registered verification.

ActionBroker authorizes.
TransactionEngine executes safely.

---

# 12. Transaction Events

Canonical event family may include:
- transaction.planned;
- transaction.prepared;
- transaction.applying;
- transaction.applied;
- transaction.probation_started;
- transaction.verification_passed;
- transaction.verification_failed;
- transaction.rollback_started;
- transaction.rolled_back;
- transaction.rollback_failed;
- transaction.committed;
- transaction.indeterminate.

Events reference TransactionRun id.

State exposes compact current/active summaries.

Durable journal remains the authoritative history.

---

# 13. Transaction artifacts

Artifacts may include:
- config snapshots;
- prior Pack version;
- backup archive;
- staged update;
- validation report;
- diff;
- evidence bundle.

Each artifact records:
- path/object id;
- hash;
- size;
- sensitivity;
- retention policy;
- transaction id.

Recovery Vault/Content Store may own artifact bytes while Transaction journal references them.

---

# 14. Transaction retention

Do not retain every rollback payload forever.

Separate:
- compact journal history;
- rollback artifacts;
- support evidence.

Retention policy may depend on:
- transaction class;
- storage budget;
- known-good state;
- owner pinning;
- whether a later successful baseline supersedes old rollback data.

Never evict the only recovery path for an active probation transaction.

---

# 15. Simple Actions

Not every mutation needs TransactionEngine.

A simple Action may:
- validate;
- authorize;
- perform;
- verify;
- audit.

Examples:
- low-risk preference metadata;
- acknowledgement;
- some bounded local state changes.

ActionSpec explicitly says whether:
- no mutation;
- simple mutation;
- Transaction required.

Do not make ordinary UI operations bureaucratic.

---

# 16. ProcedureSpec

A Procedure is declarative orchestration.

Candidate metadata:
- id/version;
- title/description;
- scope;
- source/trust;
- expected duration;
- read-only/mutating;
- effective risk class;
- required operator level;
- required Capabilities;
- inputs;
- optional ephemeral secret inputs;
- ordered/branched steps;
- outputs/artifacts;
- Doctor interpretation hook;
- cancellation policy;
- resume policy.

---

# 17. Procedure step types

Allowed managed step types:

## Probe
Read-only registered diagnostic/query.

## Action
Call registered Action.

## Procedure
Call another Procedure if dependency graph is acyclic/bounded.

## Wait/observe
Wait for condition/Signal/Event with timeout.

## Transform
Pure bounded data transformation over prior outputs.

## Doctor interpret
Ask Doctor to interpret gathered evidence/result.

## Present choice
Request explicit owner selection/consent.

## Emit artifact/report
Build bounded result artifact.

No generic:
- shell;
- arbitrary Python eval;
- raw SQL;
- unrestricted filesystem mutation.

Expert owners may still run such tools outside the managed Procedure system.

---

# 18. Procedure plan phase

Before execution, ProcedureEngine resolves:
- all steps;
- Actions;
- effective risk;
- Capabilities;
- technical blockers;
- operator requirements;
- expected mutations;
- expected artifacts;
- approximate time;
- storage/resource requirements.

Owner sees one coherent plan.

For a Procedure containing several C2/C3 Actions, avoid consent-spamming for every step if one
up-front consent can validly cover the declared plan.

If execution deviates materially from the approved plan, request fresh consent.

---

# 19. Effective Procedure risk

A Procedure cannot lower the risk of its contained Actions.

Effective risk is at least:
- maximum child Action/Transaction risk;
- plus Procedure-specific amplification if many steps compound risk.

A declarative Procedure cannot turn a C3 Action into C1.

---

# 20. Procedure atomicity

Do not pretend a long Procedure is one giant database transaction.

Example:
"Prepare Device for Offline Use" may:
- inspect storage;
- acquire content;
- verify;
- pin;
- backup;
- run Doctor.

If step 5 fails, steps 1-4 may still be useful.

Procedure has **workflow/saga semantics**:
- durable step history;
- known completed work;
- optional compensation;
- resume/retry from safe boundary.

Only individual Actions that require atomic mutation use TransactionEngine.

---

# 21. ProcedureRun journal

Persist:
- run id;
- ProcedureSpec id/version;
- actor;
- start/end;
- inputs excluding secrets;
- step states;
- Action/Transaction ids;
- outputs;
- findings;
- artifacts;
- cancellation/retry state;
- summary.

This enables:
- resume after restart;
- Doctor explanation;
- support;
- Studio progress UI.

---

# 22. Procedure result contract

Every Procedure produces a structured result:

- status;
- plain-language summary;
- technical summary;
- findings;
- Doctor findings;
- completed/skipped/failed steps;
- Actions/Transactions performed;
- artifacts;
- evidence refs;
- next Actions;
- next Procedures;
- support/recovery guidance.

This implements the owner requirement:
> if a Procedure finds something Doctor understands, show the Doctor interpretation and available
> treatment Actions right there.

---

# 23. Procedure -> Doctor -> Action handoff

Example:

    STORAGE AUDIT
       |
       +-- finds low reserve / WAL growth
       |
       v
    Doctor interprets
       |
       v
    result shows:
      [ VIEW DOCTOR ]
      [ CLEAN OPTIONAL CACHE ]
      [ RUN DB CHECK ]
      [ DETAILS ]

The owner is not forced to leave the result and rediscover the issue elsewhere.

Doctor remains interpretation authority.
Buttons still invoke registered Actions/Procedures.

---

# 24. Doctor -> Procedure handoff

Doctor may recommend:
- Full Radio Checkup;
- Storage Audit;
- Prepare Support Bundle;
- Validate Display/Touch;
- Plugin Health Audit.

Doctor recommendation records:
- finding id;
- evidence;
- recommended Procedure id;
- why.

Procedure result references the originating finding for correlation.

---

# 25. Ephemeral secrets

Avoid collecting passwords in ordinary Procedure fields.

Preferred:
- existing authenticated operator/session;
- narrow privileged helper/adapters.

If a third-party credential is truly required:
- explicitly request it;
- mark secret;
- keep memory-only where possible;
- never persist to Procedure journal;
- never include in logs/events/support;
- discard immediately after use.

Procedure result may store only:
- credential supplied: yes/no;
- operation result.

---

# 26. Cancellation

Procedure:
- may cancel between safe steps;
- cannot arbitrarily interrupt a Transaction during an unsafe apply boundary.

If owner cancels while Transaction is active:
- Transaction completes safe boundary/rollback according to its policy;
- Procedure becomes cancelled_after_safe_point.

UI must explain this rather than appearing unresponsive.

---

# 27. Concurrency

TransactionEngine should prevent conflicting simultaneous mutations.

Use SubjectRef/resource locks.

Examples:
- two config mutations on same file/service;
- two presentation-owner switches;
- Pack install + update of same Pack.

Read-only Procedures may run concurrently.

ProcedureEngine acquires locks only through child Actions/Transactions, not by inventing hidden global
locks.

---

# 28. Reboot and resume

ProcedureRun may span reboot.

On startup:
- recover active TransactionRuns first;
- then reconcile ProcedureRuns;
- mark already-completed steps;
- resume wait/probe stages according to policy;
- request owner input again if previous consent no longer safely covers the resumed plan.

Examples:
- platform update;
- restore;
- "prepare then reboot then validate."

---

# 29. Progress UI

TFT:
- concise step/progress state;
- no terminal-log flood;
- meaningful owner decisions.

Studio:
- full step tree;
- live evidence;
- Transaction links;
- logs/evidence;
- cancellation/approval.

CLI:
- exact text/scriptable output.

All surfaces consume the same ProcedureRun/TransactionRun truth.

---

# 30. Procedure trust

## Core/project Procedure
May use registered Actions according to their policy.

## Community declarative Procedure
May compose only Actions exposed to its trust tier.

It cannot request hidden privileged Actions merely by knowing their ids.

## Trusted executable extension
May contribute probes/Actions separately through their registries.
Procedure itself remains orchestration.

---

# 31. Initial Procedure catalog

Already-preserved useful candidates include:
- Gather My Device Info;
- Storage Audit;
- Clean Up;
- Thermal Snapshot;
- Performance Snapshot;
- Service Health Audit;
- Validate Display & Touch;
- Backup Before Trip;
- Prepare Device for Upgrade;
- Recovery Intake;
- Pwnagotchi Health Check;
- Radio Diagnostic;
- Plugin Health Audit;
- Config Sanity Check;
- Capture Pipeline Check;
- Restart & Verify Pwnagotchi;
- Full Doctor Checkup;
- Compare to Known-Good;
- Pack Health Audit;
- Experience Health Audit;
- Content Store Audit;
- Prepare for Offline Use;
- Build Support Bundle;
- Validate Backup/Recovery;
- Complete Health Check;
- Diagnose Something Is Wrong;
- Validate Whole Stack;
- Safe Restart Stack;
- Check Before I Leave;
- What Changed?;
- Why Is This Slow?;
- Why Is This Hot?;
- Clone My Setup.

The catalog is extensible.
The kernel does not know these names.

---

# 32. Transaction/Procedure invariants

1. Apply success != Transaction success.
2. Consequential Transaction success requires verification.
3. Unknown verification is not pass.
4. Transaction state survives Core restart.
5. Non-idempotent steps are never blindly replayed.
6. Rollback capability is described honestly.
7. Procedure cannot lower child Action risk.
8. Procedure has no raw shell/eval/SQL escape primitive.
9. Procedure result always records child Action/Transaction refs.
10. Doctor findings can appear directly in Procedure results.
11. Doctor never bypasses Action/Transaction authority.
12. Cancellation respects safe mutation boundaries.
13. Secrets never enter durable Procedure logs.
14. Conflicting Transactions are serialized by Subject/resource.
15. A long Procedure is not falsely represented as one atomic transaction.

---

# 33. Migration from current v0.19

Incremental path:

1. Create Transaction journal schema + TransactionEngine state machine.
2. Wrap existing Pack install/update transaction first.
3. Wrap presentation handoff planner/executor once physical adapter is ready.
4. Wrap restore apply.
5. Migrate plugin/provider/config operations that need probation/rollback.
6. Reuse existing Action audit rows but link them to Transaction ids.
7. Create ProcedureEngine + ProcedureSpec registry.
8. Implement read-only Procedures first:
   - Gather My Info;
   - Full Doctor Checkup;
   - Storage Audit.
9. Add mutating Procedures composed from already-proven Actions.
10. Expose shared progress in TFT/Studio/CLI.

