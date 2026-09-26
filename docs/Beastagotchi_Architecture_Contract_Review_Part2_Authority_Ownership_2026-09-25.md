# Beastagotchi Architecture Contract Review — Part 2: Authority & Ownership

**Date:** 2026-09-25  
**Status:** proposed architecture contract  
**Depends on:** Part 1 Stable Kernel

---

# 1. Ownership is multi-dimensional

Do not use "owns" as an ambiguous shorthand.

Beastagotchi distinguishes:

## Source Authority
The system that actually owns or directly measures the underlying reality.

Examples:
- Linux owns kernel/service/process state;
- Pwnagotchi owns normal agent/radio behavior;
- Bettercap owns its runtime/session state;
- Beast roster repository owns Beast identity records;
- physical display owner owns the framebuffer/input hook.

## Canonical Truth Authority
The place where Beast exposes the currently accepted semantic truth.

For live current values:
- StateRegistry.

For durable domain facts:
- the owning repository/domain store.

## Mutation Authority
The component allowed to execute a managed change.

Examples:
- Action handler / Transaction adapter;
- not Doctor;
- not a Scene;
- not a Pack manifest;
- not a capability resolver.

## Policy Authority
The component deciding whether the managed operation is permitted.

Includes:
- operator session;
- Action policy;
- owner mode;
- risk/consent policy;
- technical blockers;
- compatibility policy.

## Persistence Authority
The component/repository responsible for durable storage and migration of one domain.

## Presentation Authority
The component currently allowed to control physical display/touch presentation.

Exactly one physical presentation owner at a time.

These authorities may live in different components.

---

# 2. General authority law

> **Observing something does not grant authority to mutate it.**
>
> **Describing a capability does not grant authority to activate it.**
>
> **Rendering a control does not grant authority to execute its requested Action.**
>
> **Being root-capable does not mean every Beast component receives root authority.**

This is the core "read broad, act narrow" rule.

---

# 3. Platform ownership matrix

## Linux / Raspberry Pi

### Source authority
Owns:
- devices;
- kernel;
- drivers;
- CPU/memory/process state;
- filesystem;
- systemd;
- networking;
- framebuffer devices;
- input devices;
- package manager;
- thermal/governor facts.

### Beast observation
Through bounded collectors/adapters.

### Managed mutation
Only through registered Actions/Transactions and dedicated adapters.

### Never
A Scene/Pack/Doctor should not directly call arbitrary privileged Linux commands.

---

## Pwnagotchi / Bettercap

### Source authority
Pwnagotchi owns:
- agent behavior;
- normal radio policy;
- Bettercap relationship;
- Pwnagotchi plugin lifecycle;
- native Pwnagotchi config/UI semantics.

Bettercap owns:
- its direct session/runtime evidence.

### Beast canonical representation
Observed facts appear through State/Signals/Events.

### Managed mutation
Only through explicit Pwnagotchi/Bettercap adapter Actions.

The read-only bridge never becomes a covert command channel.

### Owner manual override
SSH/root/manual editing remains possible and is outside managed Beast authority.

---

## Beast Kernel / Core

### Canonical current truth
StateRegistry.

### Managed mutation gateway
Action authority.

### Consequential mutation lifecycle
Transaction authority.

### Runtime lifecycle
ModuleRuntime/Scheduler.

### Policy
Owner/operator/Action policy.

### Provenance
Shared journals/references.

### Core must not
- render product UI;
- contain Atlas/Forge/etc.;
- contain creature XP values;
- know GitHub-specific content semantics;
- own raw Pwnagotchi radio behavior.

---

## Beast Domain

Includes:
- roster;
- Beast/Monster identity;
- lineage;
- progression;
- Life Ledger;
- achievements/unlocks;
- memories;
- global Beast history.

### Source/canonical durable authority
Domain repository + validated domain rules.

### Mutation
Domain Actions/Transactions/rule engine.

### Presentation
Never authoritative.

A UI saying "Level 100" does not make a Beast Level 100.

---

## Doctor

### Authority
Diagnostic interpretation.

Doctor may:
- inspect;
- correlate;
- explain;
- remember;
- recommend;
- request a Procedure/Action;
- verify results.

Doctor may not directly:
- mutate files/services/packages;
- change progression;
- activate providers;
- own physical presentation;
- bypass Action policy.

Doctor treatment is a request into Action/Transaction authority.

---

## Procedure

### Authority
Orchestration.

Procedure may:
- run registered probes;
- invoke Actions;
- initiate Transactions;
- request Doctor interpretation;
- produce artifacts/reports.

Procedure may not:
- execute arbitrary shell merely because a Procedure manifest says so;
- bypass operator/Action policy;
- write directly into unrelated repositories.

---

## UI / Studio / Remote clients

### Authority
Request + presentation.

They may:
- read permitted State/Signals;
- render;
- request Actions/Procedures;
- edit safe presentation preferences through a dedicated store;
- submit content to bounded intake.

They may not:
- directly mutate privileged platform state;
- downgrade privacy;
- write progression truth;
- directly switch physical owners without Action/Transaction.

Studio pairing/authentication does not itself equal root authority.

---

## Packs / community extensions

### Authority
Determined by trust tier and registered capability token/handle.

Declarative content can:
- register allowed namespaced specs;
- request existing Actions;
- provide Scenes/Surfaces/content.

It cannot:
- grant itself privileged Action authority;
- directly write arbitrary DB state;
- lower privacy classifications;
- claim high-priority State namespaces reserved to Core;
- mutate Linux/Pwnagotchi directly.

Trusted executable extensions receive explicitly bounded handles, not the entire Core object graph.

---

# 4. State authority: canonical does not mean physical ownership

StateRegistry is the canonical Beast truth surface, but it does not magically become the physical
source of all facts.

Every State value should be conceptually traceable to:

    physical/domain source
        ->
    observation/provider
        ->
    arbitration
        ->
    StateRegistry
        ->
    consumers

For a Beast-owned durable fact:

    domain repository
        ->
    domain engine
        ->
    StateRegistry projection

Examples:

### CPU temperature
Linux sensor -> system collector -> StateRegistry -> Doctor/UI.

### Active Beast
Roster repository -> roster/progression projection -> StateRegistry -> UI/Studio.

### Current provider
Provider evidence -> arbitrator -> StateRegistry decision view.

### Physical presentation owner
Validated presentation state + service evidence -> presentation broker -> StateRegistry.

---

# 5. State write rules

## Core-reserved namespaces
Some namespaces must be protected from arbitrary extensions.

Examples:
- system.*;
- owner.*;
- doctor.*;
- presentation.*;
- progression.*;
- roster.*;
- transaction.*;
- capabilities canonical decisions.

Third-party extensions should normally publish into namespaced areas or through registered canonical
providers.

## Priority
Extensions do not choose an arbitrarily high State priority.

Provider/Module registration assigns the allowed priority/authority class.

## Canonical provider promotion
A third-party provider may become the canonical provider for a Capability only through resolver/
arbitrator policy.

It does not gain canonical authority merely by writing the same key faster.

---

# 6. Operator and authority levels

Current levels:
- observer;
- operator;
- maintainer;
- administrator.

Keep the concept, but treat exact names/permissions as platform policy rather than immutable kernel
vocabulary until the permission matrix is finalized.

## Observer
Read-only.

## Operator
Normal reversible operational requests:
- select provider preference;
- run safe Procedures;
- some service-level operations.

## Maintainer
Maintenance affecting installed components/config under controlled Transactions.

## Administrator
Expert Mode / high-impact platform operations.

### Important
Beast operator level is not Linux UID/root.

An administrator Beast session authorizes Beast policy.
The actual privileged adapter still operates through the bounded Action channel.

---

# 7. Managed / Expert / Customized / Manual

These are related but distinct.

## Managed
- supported policy;
- full validation/recovery expectations;
- normal UI prevents unsupported managed operations.

## Expert
- temporary/explicit owner permission to override selected Beast policy blockers;
- technical blockers remain blockers;
- override still uses normal Action/Transaction adapters;
- audit/provenance retained.

## Customized
A factual device state:
- one or more managed assumptions were intentionally overridden/modified.

Customized is not an error by itself.

Doctor/support adjusts claims accordingly.

## Manual / Unrestricted owner modification
Owner used SSH/root/files/code outside managed contracts.

Beast should:
- detect drift where practical;
- describe it honestly;
- attempt diagnosis;
- not pretend it never happened.

It cannot promise rollback for changes it never observed.

---

# 8. Customization / Override Journal

Current OwnerMode keeps summary state.
Future architecture should add an append-only customization journal.

Entry:
- id;
- actor;
- timestamp;
- subject;
- Action/Transaction id where applicable;
- policy blockers overridden;
- before fingerprint;
- after fingerprint;
- reason/comment if supplied;
- revert reference if available.

Doctor, support, known-good, Recovery and provenance can all consume this.

Do not use "customized=true" as the only historical record.

---

# 9. Technical blocker vs policy blocker vs unknown

Every managed plan should distinguish:

## Technical blocker
Operation cannot currently succeed safely/physically.

Examples:
- hardware absent;
- required service unavailable;
- no rollback snapshot for a handoff that requires one;
- insufficient disk.

Expert Mode does not magically override physics.

## Policy blocker
Operation could technically happen but managed Beast policy refuses it.

Examples:
- unsupported provider choice;
- risky plugin conflict;
- unvalidated compatibility combination.

Owner may explicitly override when the Action allows it.

## Unknown
Evidence is insufficient.

Do not silently convert Unknown into either Allowed or Impossible.

Doctor/Procedure may recommend a diagnostic.

---

# 10. Consent classes

Not every Action should interrupt the owner.

Proposed policy classes:

## C0 — read-only / observational
No mutation.
May run automatically.

Examples:
- diagnostics;
- health probe;
- plan;
- inventory.

## C1 — low-risk reversible maintenance
May be owner-configured for automatic execution if:
- Transaction/recovery behavior is proven;
- effect is bounded;
- no owner content loss;
- policy explicitly enables it.

Examples might include a validated restart-and-verify of a non-critical Beast service.

Do not populate this category casually.

## C2 — consequential managed mutation
Explicit owner confirmation.

Examples:
- plugin activation;
- provider handoff;
- config change;
- presentation handoff;
- Pack executable activation.

## C3 — high-impact / Expert / administrator
Requires elevated Beast operator session and explicit confirmation.

Examples:
- unsupported policy override;
- dependency/package mutation;
- major restore;
- platform update;
- dangerous destructive cleanup.

## C4 — physical/local-presence required
Reserved for operations where remote confirmation is inappropriate.

Examples may include:
- certain display/input recovery;
- hardware calibration;
- recovery steps where physical observation is necessary.

Exact membership remains Action-specific.

---

# 11. Automatic remediation

Doctor may recommend automatic remediation only through Actions whose policy explicitly permits it.

Automatic remediation requires:
- registered Action;
- proven bounded effect;
- appropriate consent class;
- verification;
- rollback where consequential;
- rate limit/backoff;
- recurrence guard;
- journal entry.

Doctor does not acquire a special bypass channel.

Example:

    Doctor detects restart loop
      ->
    treatment policy allows one restart-and-verify attempt
      ->
    Action/Transaction
      ->
    verification
      ->
    Doctor observes result

If it recurs, escalation replaces repeated automatic attempts.

---

# 12. Presentation authority

Exactly one physical presentation owner at a time.

Separate:

## Desired owner
Owner preference/policy.

## Active owner
Validated actual owner.

## Presentation source
What content is shown.

## Remote viewer
Who can observe remotely.

## Input focus
Which client/source currently has authorized input routing.

A remote mirror does not become physical display owner.

A desired owner is not reported as active until verification succeeds.

---

# 13. Persistence authority

Each durable domain has one repository authority.

Examples:
- roster repository owns durable creature identity;
- progression/Life Ledger repository owns progression provenance;
- Incident repository owns detailed incidents;
- Doctor Patient Chart owns compact medical memory;
- Transaction journal owns mutation history.

Other components consume APIs/projections.

Avoid multiple components directly editing the same tables with independent semantic rules.

This also supports fixing current SQLite concurrency/duplicate-manager debt.

---

# 14. Mutation sequence

Canonical managed mutation flow:

    requester
       |
       v
    ActionSpec lookup
       |
       v
    parameter validation
       |
       v
    capability / technical resolution
       |
       v
    policy + operator authorization
       |
       v
    PLAN returned to owner/client
       |
       v
    consent if required
       |
       +---- simple Action ----> perform -> verify/audit
       |
       +---- Transaction ------> snapshot -> apply -> probation
                                   |               |
                                   +<- rollback <- failed verify
                                                   |
                                              commit/journal
       |
       v
    State/Event updates
       |
       v
    Doctor observes/interprets

No UI/Doctor/Procedure shortcut bypasses this path.

---

# 15. Preference authority

Not all writes need ActionBroker.

Safe user preferences may use typed dedicated stores.

Examples:
- visual palette;
- Experience preference;
- face choice;
- dashboard arrangement;
- reduced-motion preference;
- provider preference that does not itself activate anything.

Dedicated preference store must still provide:
- schema;
- validation;
- atomic write;
- migration;
- change provenance/generation.

The moment a "preference" requires system mutation, an Action/Transaction performs that mutation.

This keeps ordinary personalization lightweight.

---

# 16. Owner sovereignty invariant

The architecture must preserve:

> **Beastagotchi governs its managed path; the owner governs the machine.**

Therefore:
- Beast can refuse to perform an unsupported managed Action;
- Expert Mode can allow structured override when technically feasible;
- root/manual owner may bypass Beast entirely;
- Beast can label/support/diagnose customized state;
- Beast must not sabotage the owner's machine to enforce policy.

This also applies to progression integrity:
- verified provenance may be withheld when history is inconsistent;
- local owner customization remains possible;
- no destructive anti-tamper.

---

# 17. Extension authority tokens/handles

Do not pass trusted extensions unrestricted Core internals.

Future extension runtime should receive only declared handles.

Examples:
- ReadStateHandle(namespaces);
- PublishSignalHandle(namespace, max_priority);
- EmitEventHandle(event_namespace);
- RequestActionHandle(allowed_actions);
- ContentHandle(pack_scope);
- SceneRegistrationHandle(namespace);
- ModuleHandle(resource_class);
- PersistentKVHandle(pack_namespace, quota).

Higher-trust executable integrations can receive more handles after explicit policy.

No handle:
- raw Store connection;
- root shell;
- operator-session mutation;
- privacy reclassification;
- arbitrary State priority;
- arbitrary filesystem access by default.

Exact isolation mechanism may initially be API discipline in-process, later strengthened if needed.

---

# 18. Authority invariants for tests

1. Resolver/arbitrator never performs provider activation.
2. Doctor never performs direct system mutation.
3. Procedure never bypasses Action authority.
4. UI/Studio privileged operations use Action authority.
5. Extension metadata cannot authorize itself.
6. State priority comes from registration/policy, not arbitrary extension input.
7. One physical display owner is active at a time.
8. Desired presentation owner != active owner until verified.
9. Technical blockers cannot be Expert-overridden as if they were policy.
10. Expert override marks/journals customized state.
11. Durable domain truth has one repository authority.
12. Root/manual changes remain possible but are outside managed guarantees.
13. Automatic remediation is rate-limited, verified and policy-bound.
14. Remote input and remote viewing have separate permissions.
15. Safe preferences cannot silently smuggle privileged mutation.

---

# 19. Immediate current-code implications

This authority contract strengthens several already-identified changes:

- inject the single Core-owned roster/global-sync/memory objects into ActionBroker;
- fix SQLite connection ownership;
- replace Action if-chains with ActionSpec registry;
- add Transaction Engine/journal;
- add append-only customization journal;
- make State provider priority part of registration;
- centralize presentation preferences;
- keep provider resolver/arbitrator read-only;
- retain Action Unix socket as privileged boundary;
- add typed extension handles rather than exposing Core internals.

No wholesale rewrite is required.

