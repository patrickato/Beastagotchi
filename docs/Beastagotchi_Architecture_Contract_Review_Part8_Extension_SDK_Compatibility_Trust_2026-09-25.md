# Beastagotchi Architecture Contract Review — Part 8: Extension SDK, Compatibility & Trust

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** Architecture Parts 1-7, completed Structure Deep Dive, current v0.19 Pack/Experience/
plugin/provider work, independent Claude foundation review, PwnDoctor Condition Pack trust work,
owner open-architecture and sovereignty guidance.

---

# 1. Purpose

Beastagotchi is intended to become an unusually open local platform.

Third parties should eventually be able to add:

- Experiences;
- Surfaces;
- Scenes;
- faces;
- visual primitives;
- choreography;
- apps;
- Packs;
- Procedures;
- Doctor knowledge;
- Signals/Events;
- capability providers;
- hardware adapters;
- content sources;
- progression content;
- integration modules;
- carefully bounded Actions.

They should be able to do that **without editing central Beastagotchi switch statements**.

At the same time, installing one extension must not silently grant it:

- root;
- direct database writes;
- arbitrary State authority;
- arbitrary filesystem access;
- arbitrary network egress;
- operator-session authority;
- Expert Mode authority;
- privacy reclassification;
- package/service mutation;
- direct progression writes;
- unrestricted subprocess execution.

The architectural target is:

> **Easy to extend. Hard to accidentally own the machine.**

and:

> **No ambient authority. Extensions receive only the handles they were actually granted.**

---

# 2. Do not overload the word "trust"

An extension has several independent properties.

Do not compress them into one trusted/untrusted boolean.

## Identity

Who claims to have produced it?

Possible evidence:
- project-owned namespace;
- publisher key/signature;
- source repository identity;
- local owner-created identity;
- unknown.

Identity does not prove safety.

## Integrity

Are the bytes/manifest exactly the object that was acquired?

Evidence:
- hash;
- signed digest;
- verified archive;
- content-addressed object.

Integrity does not prove publisher identity unless signature semantics do.

## Compatibility

Does it match the current contracts/platform/capabilities?

Compatibility does not grant authority.

## Trust class

What registration/execution class may this source participate in?

Examples:
- catalog only;
- inert/unverified content;
- verified declarative;
- project/trusted executable;
- core.

Trust class does not itself grant every privilege.

## Authority

Which actual handles/operations may this active extension use?

Authority is explicit and scoped.

## Reputation / evidence

What has been observed historically?

Examples:
- project-tested;
- community-tested;
- physically validated on exact platform;
- owner-local proven;
- unknown.

Reputation is evidence, not privilege.

## Support state

How will Beast/Doctor describe the installation?

Examples:
- supported;
- compatible-by-contract;
- experimental;
- customized;
- unknown;
- incompatible.

**Invariant:** identity, integrity, compatibility, trust, authority, reputation and support state remain separate facts.

---

# 3. Extension classes

Use a small number of understandable extension classes rather than one universal plugin format.

## Declarative content

Preferred/default ecosystem path.

Examples:
- Experience DNA;
- Scene/Surface definitions;
- face data;
- choreography;
- Procedure composition;
- Doctor knowledge;
- Progression rules;
- content metadata;
- Collections;
- compatibility definitions.

Declarative content contains no arbitrary executable code.

It is schema-validated before registration.

## Trusted executable extension

Used only where genuine code is required.

Examples:
- new hardware/protocol adapter;
- executable provider;
- new Scene primitive;
- new Content Source adapter;
- specialized collector;
- bounded Action handler;
- unusual device integration.

Executable extension receives scoped SDK handles.

## Pwnagotchi plugin

Remains part of the underlying Pwnagotchi plugin system where it genuinely belongs.

Beast normally adapts its useful facts/capabilities rather than cloning it.

## Companion Expansion

One user-facing feature may contain multiple internal pieces:

- Pwnagotchi plugin;
- Beast Pack;
- Beast App;
- provider/adapter;
- optional media.

The user may experience one product even when implementation spans layers.

## Owner/manual code

The owner may run arbitrary local code outside the managed SDK.

Beast may report it as customized/unsupported.

Owner sovereignty remains intact.

---

# 4. Extension manifest

Every managed extension should have machine-readable metadata.

Common fields may include:

- stable extension id;
- namespace;
- display name;
- publisher/source identity;
- version;
- manifest schema version;
- extension class;
- license;
- source/provenance;
- artifact hash/signature evidence;
- Beast contract version range;
- upstream/Pwnagotchi compatibility claims;
- architecture/platform constraints;
- required Capabilities;
- optional Capabilities;
- provided Capabilities;
- requested SDK handles/permissions;
- registered object types;
- resource class/budget hints;
- data-egress class;
- secret requirements;
- storage cost;
- backup scope;
- activation/restart requirements;
- migration requirements;
- support/reputation evidence;
- uninstall/retained-state policy.

Unknown fields are handled according to schema-version compatibility rules.

Unknown required semantics fail honestly.

---

# 5. Namespaces

Third-party extensions own a stable namespace.

Examples:

    author.project
    org.feature
    user.localname

Objects may derive ids such as:

    author.project.signal.temperature
    author.project.surface.dashboard
    author.project.procedure.field_check
    author.project.action.calibrate

Core-reserved namespaces cannot be shadowed.

Lower-trust extensions cannot register look-alike replacements under core ids.

Renaming a public namespace is a compatibility event, not cosmetic cleanup.

---

# 6. Public SDK principle

The SDK exposes **contracts**, not Beast Core internals.

Preferred public interfaces include:

- read Signals/State through scoped read handles;
- subscribe to registered Events;
- publish namespaced Signals within granted authority;
- emit namespaced Events;
- register declarative Surfaces/Scenes/Experiences;
- request existing Actions;
- contribute bounded trusted Action handlers;
- register Providers/Capabilities;
- register Modules;
- use extension-private persistent storage;
- access Pack/content objects;
- request owner-approved external/network resources;
- expose Doctor evidence/runbook metadata.

Do not hand extensions:

- Core object graph;
- raw Store/SQLite connection;
- raw operator session;
- raw root shell;
- arbitrary filesystem root;
- unrestricted secrets store.

---

# 7. Capability handles

Executable extensions receive explicit handles.

Illustrative handle families:

## ReadStateHandle

Scoped to allowed namespaces/signals.

May:
- read current values;
- inspect quality/source/freshness where permitted;
- subscribe to changes.

May not:
- write State.

## PublishSignalHandle

Scoped to extension-owned or explicitly delegated Signals.

Carries:
- allowed namespace;
- maximum provider priority;
- privacy floor;
- value/schema constraints.

May not:
- overwrite core authority by self-declaration;
- downgrade privacy.

## EmitEventHandle

Scoped Event namespaces/types.

Enforces:
- schema;
- privacy;
- payload bounds;
- rate/budget.

## RequestActionHandle

May request only allowed registered Actions.

It does not bypass:
- operator authorization;
- plan/consent;
- technical blockers;
- Transaction policy.

The extension is a requester, not Action authority.

## PersistentKVHandle

Extension-private namespaced storage with:
- quota;
- migration/version;
- backup policy.

No raw SQL.

## ContentHandle

Scoped access to extension/content objects.

No arbitrary filesystem traversal.

## SceneRegistrationHandle

May register:
- allowed Surfaces;
- Scenes;
- Experiences;
- declarative visual assets.

Executable primitive registration requires higher trust.

## ModuleHandle

Allows a trusted extension to register runtime work under Part 5 scheduling/resource policy.

No unmanaged permanent loop.

## NetworkHandle

Where needed, grants bounded external communication policy.

May encode:
- allowed destinations/classes;
- local-only;
- owner-approved Internet;
- bandwidth/rate class;
- privacy/data-egress class.

## SecretHandle

Where genuinely required, an extension receives only the specific secret capability it needs.

Prefer:
- opaque/ephemeral token use;
- one-shot access;
- no logging;
- no canonical State publication.

Secret presence may be visible without secret value exposure.

## FilesystemHandle

If needed, scope to:
- extension-owned directory;
- explicit imported/exported object;
- approved device path capability.

Avoid arbitrary filesystem access by default.

---

# 8. No self-granted privilege

Manifest declarations are requests/evidence, not authority.

An extension cannot gain power merely by writing:

    requires_root = true
    trust = core
    priority = 999
    privacy = public
    action = arbitrary_shell

Registration policy resolves what may actually be granted.

Core/project policy owns:
- maximum Signal priority;
- privacy floor;
- action exposure;
- executable trust;
- handle scope;
- system mutation authority.

---

# 9. Extension Grant Receipt

**New recommended contract:** every activated executable extension receives a durable **Grant Receipt**.

The receipt records the exact authority actually resolved at activation time.

Candidate fields:

- extension id/version/hash;
- manifest id/hash;
- source/publisher evidence;
- registry generation;
- compatibility result;
- support state;
- requested handles;
- granted handles/scopes;
- denied handles/reasons;
- operator/owner consent references;
- Expert/customized override references;
- activation Transaction id;
- resource class/budgets;
- data-egress grant;
- secret-access class;
- activation timestamp;
- revocation/deactivation state.

Why this matters:

- Doctor can answer "what can this extension actually do?";
- support bundles can show authority without exposing secrets;
- updates can diff old vs new requested permissions;
- suspicious permission expansion becomes visible;
- rollback/revocation has one authoritative record;
- owner consent can be tied to the exact version/hash.

This is intentionally similar to an install/permission receipt, not a security theater badge.

---

# 10. Permission-diff rule

An update that requests **more authority** than the installed version had is not a routine silent update.

Examples:

- new network egress;
- new secret access;
- broader State read scope;
- new Action request scope;
- new filesystem path;
- new executable Module;
- higher Signal authority.

The update plan must show the permission diff.

Policy may require explicit owner consent.

A version that merely changes inert assets without authority expansion may follow a lighter update path.

---

# 11. Declarative-first rule

Most community creativity should not require executable code.

Prefer declarative contracts for:

- Experiences;
- Surfaces;
- Scenes;
- choreography;
- Progression rules;
- Achievements;
- Memories;
- Procedures composed from existing Actions;
- Doctor knowledge;
- compatibility metadata;
- content catalogs;
- collections.

Benefits:
- safer;
- inspectable;
- hot-reloadable;
- portable;
- easier to validate;
- lower resource cost;
- easier to preview;
- easier to share.

Executable escape hatches remain available when data cannot express the feature honestly.

---

# 12. Executable-extension admission

Executable code is higher risk because it can contain arbitrary behavior.

Managed executable admission should evaluate:

- source identity/provenance;
- artifact integrity;
- compatibility;
- declared handles;
- code trust class;
- resource class;
- update source;
- rollback path;
- filesystem/network/secret requirements;
- restart effects;
- Doctor/self-health hooks.

Official/project executable integrations can be more trusted than unknown community code without
pretending they are infallible.

Owner may still explicitly install unsupported executable code.

---

# 13. Staging / quarantine

Acquisition should not equal execution.

A useful lifecycle for executable extensions:

    discovered
      ->
    acquired
      ->
    verified
      ->
    staged/quarantined
      ->
    manifest inspected
      ->
    compatibility resolved
      ->
    grant plan produced
      ->
    owner/policy consent
      ->
    activation Transaction
      ->
    probation
      ->
    healthy active
         or rollback/deactivate

During staging/quarantine:
- metadata/content may be inspected;
- code is not imported/executed merely to discover its manifest;
- previews use inert/declarative metadata where possible;
- compatibility is evaluated without granting runtime authority.

Do not import unknown Python just to ask it what permissions it wants.

---

# 14. Manifest parsing must be inert

Manifests must be parseable as data.

Good:
- JSON;
- TOML;
- YAML only with safe parser/strict schema if used;
- signed detached metadata.

Bad:
- Python file imported to return a manifest;
- shell script run to determine compatibility;
- setup hook executed during discovery.

Discovery must not execute the thing being discovered.

---

# 15. Compatibility is a vector, not one version string

"Works with Beastagotchi v0.19" is too weak.

Compatibility may depend on:

- Beast contract version;
- specific API/schema versions;
- Python/runtime ABI;
- CPU architecture;
- OS/distribution;
- Pwnagotchi/Jayofelony version/build;
- Bettercap behavior/version;
- required Capabilities;
- display/input profile;
- hardware presence;
- storage/resource class;
- extension dependencies;
- conflicting providers;
- presentation owner constraints.

Represent compatibility as evidence across dimensions.

A single summary may be derived, but the underlying reasons remain inspectable.

---

# 16. Compatibility result vocabulary

Possible states:

## validated

Tested against the exact declared environment/contract.

May include:
- CI validated;
- physical validated;
- owner-local validated.

These are different evidence classes.

## compatible_by_contract

Required contracts/capabilities match, but the exact environment has not been physically/empirically validated.

## unknown

Insufficient evidence.

Unknown is not compatible.

## incompatible

A known requirement cannot be met.

## customized

The device or extension is outside the tested supported path but may still function.

## blocked

Policy or technical blocker prevents managed activation.

Summary must preserve the distinction between:
- technical incompatibility;
- unverified/unknown;
- policy refusal.

---

# 17. Compatibility fingerprint

**Recommended new object:** produce a compact Compatibility Fingerprint for an installed/active extension.

Possible inputs:

- Beast contract versions;
- extension id/version/hash;
- platform profile;
- upstream Pwnagotchi build;
- relevant provider/capability versions;
- Python/architecture;
- required registry generations;
- display/input class if relevant;
- dependency closure.

This helps Doctor/support answer:

> "It worked yesterday. What changed?"

Fingerprints may be stored in known-good/Patient Chart history without exposing secrets.

---

# 18. Contract versioning

Public extension contracts need explicit version semantics.

Separate:

- Beast product/release version;
- kernel contract version;
- SDK contract version;
- manifest schema version;
- individual object schema versions.

Do not force every additive SDK change to require a Beast major version.

Rules:

- backward-compatible additive fields allowed where specified;
- extensions declare supported contract ranges;
- removed/deprecated semantics have migration windows;
- unknown required semantics fail honestly;
- stable ids are not renamed casually.

---

# 19. API versus implementation

Public SDK behavior is a compatibility promise.

Internal classes/files are not automatically public API.

Document which interfaces are:

- public/stable;
- public/experimental;
- project-internal;
- deprecated.

Third parties should not have to import deep private Core modules for normal extension development.

If an internal refactor preserves the public contract, extensions should remain unaffected.

---

# 20. Built-ins should dogfood public contracts

Where practical, built-in content should use the same SDK path that third-party content uses.

Examples:

- built-in Experiences through Experience/Scene contracts;
- project Procedures through Procedure registry;
- project declarative Progression rules through the same rule schema;
- project Doctor knowledge through the same knowledge schema.

This exposes weaknesses before community developers suffer them.

Exceptions are allowed where privileged core behavior genuinely belongs to Core.

Do not fake parity where built-ins require authority that third parties should not receive.

---

# 21. Signatures and provenance

Artifact signatures can prove:

- publisher-key identity;
- artifact integrity;
- provenance continuity.

They do **not** prove:

- correctness;
- safety;
- compatibility;
- quality;
- authority.

A valid signature from a known author does not bypass permission review.

An unsigned local owner-created Pack is not automatically malicious.

Signature policy should be useful evidence, not centralized gatekeeping.

---

# 22. Publisher identity

A future publisher identity system may support:

- project key;
- organization keys;
- community author keys;
- local owner key;
- rotated/revoked keys.

Namespace ownership may be associated with publisher identity.

Do not require a central online account for local creation/use.

Offline signature verification should remain possible.

---

# 23. Reputation

Reputation is optional evidence accumulated from:

- project testing;
- CI;
- exact physical validation;
- community reports;
- owner-local success;
- Doctor history.

Do not turn reputation into automatic privilege escalation.

A popular extension receives no extra machine authority merely because many users like it.

---

# 24. Resource declarations

Executable Modules/visual primitives must participate in Part 5.

Declare:

- execution mode;
- cadence;
- resource class;
- timeout;
- backoff;
- expected CPU/memory/I/O class;
- network behavior;
- storage writes;
- health probe;
- dormancy conditions.

Scheduler/Governor controls execution.

An extension cannot self-declare critical_control and thereby outrank the platform.

Critical resource class requires registration policy approval.

---

# 25. Extension health

Every executable extension should expose generic health where feasible:

- starting;
- healthy;
- dormant;
- degraded;
- failed;
- backoff;
- stopped.

Doctor may additionally interpret domain-specific findings.

Extension failure must not silently corrupt the health status of the entire platform.

A failed optional extension should normally degrade that capability, not crash Core.

---

# 26. Failure isolation

Initial implementation may use in-process extension code where practical.

But architecture must avoid claiming that Python import boundaries are a security sandbox.

Possible maturity path:

## Phase A — API discipline

- trusted executable only;
- scoped handle objects;
- no Core object exposure;
- code review/project trust;
- scheduler timeout/backoff;
- transactional activation.

## Phase B — process isolation where justified

Potentially:
- separate worker process;
- Unix-domain RPC;
- restricted environment/user;
- filesystem/network restrictions;
- restart/crash isolation.

Use stronger isolation first for:
- unknown/community executable code;
- network-facing adapters;
- fragile native dependencies;
- high-risk integrations.

Do not implement heavyweight sandbox machinery merely for appearance.

---

# 27. Extension crash behavior

An optional extension crash should:

- mark the Module/provider unhealthy;
- capture bounded evidence;
- back off/restart according to policy;
- notify Doctor when meaningful;
- keep Core operational where possible;
- preserve Transaction/registry truth.

Repeated crash loops are bounded.

No uncontrolled respawn storm.

---

# 28. Network egress

Every extension with external communication should declare data-egress behavior.

Examples:

- none/local-only;
- owner LAN;
- specific upstream service;
- generic Internet;
- telemetry/analytics;
- user-content upload.

Where practical expose:

- destination class/domain;
- data categories;
- credential requirement;
- frequency/bandwidth.

Owner can understand what leaves the Pi.

Do not silently broaden egress during update without a permission diff.

---

# 29. Privacy authority

Extensions cannot downgrade canonical privacy.

Examples:

- a core Signal marked secret/private cannot be re-registered public;
- an extension cannot export SSID/GPS/capture data merely because it can read a related Signal;
- publication/export policies remain separate from internal read permission.

An extension may declare **stricter** handling for its own data.

---

# 30. Secrets

Secrets are not ordinary config values.

Stable rules:

- canonical State exposes presence/status, not secret value;
- support bundles omit secrets;
- logs omit/redact secrets;
- declarative content cannot read arbitrary credentials;
- SecretHandle access is scoped and auditable;
- ephemeral use is preferred;
- extension uninstall/revocation clears its stored secret where policy says so;
- owner can inspect which extension requires which secret class.

No Pack gains all credentials because one dependency needs one token.

---

# 31. Filesystem access

Default executable extension filesystem access should be limited to:

- extension-owned state/cache;
- explicitly imported content;
- specific device capability paths when granted.

System files/config mutations occur through Actions/Transactions.

A hardware adapter may need a device node/path; that path is a declared capability, not universal filesystem access.

---

# 32. Subprocess / command execution

No generic public "run arbitrary shell command" SDK primitive.

Where external tools are legitimately required:

- register a bounded adapter;
- fixed/validated executable;
- typed parameters;
- timeout;
- environment control;
- output bounds;
- resource class;
- provenance;
- verification.

Owner manual shell remains available outside the managed SDK.

---

# 33. System/package/service mutation

Extensions may **request** registered operations.

They do not directly:

- apt install;
- pip into Pwnagotchi;
- rewrite systemd;
- restart arbitrary services;
- replace kernel modules;
- modify presentation ownership.

These require registered Actions/Transactions and appropriate authority.

An owner in Expert/manual mode may still perform unsupported changes.

---

# 34. State publication authority

An extension may publish only Signals it owns or is explicitly registered as a Provider for.

Registration policy assigns:

- max priority;
- freshness;
- privacy;
- schema;
- authority relationship.

A provider cannot win canonical truth by simply publishing faster or choosing a larger priority value.

---

# 35. Progression authority

Extensions do not write XP/Level/Achievement rows directly.

They emit:

- canonical/namespaced Events;
- truthful facts;
- registered Progression rules.

Progression Engine decides canonical rewards under Part 7.

This prevents a visual Pack from granting itself infinite XP.

Owner custom rules remain possible under customized provenance.

---

# 36. Procedure authority

Declarative community Procedures may compose only Actions/Probes exposed to their trust tier.

Knowing a privileged Action id does not grant access.

Effective risk/consent is inherited from child operations.

Procedure cannot hide a C3/C4 mutation inside a friendly C1 wrapper.

---

# 37. Presentation authority

An extension may register presentation content.

It does not gain physical framebuffer ownership by registration.

Presentation owner switching remains a managed Action/Transaction.

Remote preview/rendering does not equal physical owner.

Input routing/focus follows Presentation/Surface contracts, not arbitrary callbacks from extensions.

---

# 38. Extension-private persistence

Provide bounded extension-private persistence.

Preferred model:
- namespaced KV/document store or registered repository;
- quotas;
- schema version;
- backup inclusion policy;
- migration hooks;
- cleanup/export semantics.

Avoid third-party arbitrary writes into Core domain tables.

Cross-domain sharing occurs through Signals/Events/registered objects.

---

# 39. Update semantics

Extension update stages a new version alongside the current known-good version where rollback policy requires.

Update evaluates:

- artifact integrity;
- manifest/schema;
- compatibility;
- permission diff;
- storage peak;
- migration;
- registry candidate generation;
- restart requirement.

Activation uses Transaction when executable/authority-bearing behavior changes.

If probation fails:
- restore prior registry generation;
- restore prior executable/content version where possible;
- record Doctor/Transaction evidence.

---

# 40. State migration

Extensions own migrations for their extension-private state within the permitted store contract.

Migration must be:

- versioned;
- bounded;
- rollback-aware where feasible;
- executed during controlled activation/update.

An extension migration cannot mutate unrelated Core tables.

If an extension is too old for a safe migration path:
- activation is blocked/unknown;
- owner may export/manual-recover;
- data is not silently discarded.

---

# 41. Uninstall

Uninstall distinguishes:

- runtime/code removal;
- content removal;
- cache removal;
- extension-private durable state;
- owner-created artifacts;
- secrets;
- historical provenance.

Default behavior should avoid destroying irreplaceable owner state.

Offer explicit choices where meaningful:

- disable only;
- remove runtime;
- remove cache/content;
- export state then remove;
- purge extension state.

Historical Life Ledger/Achievement/Transaction facts referencing the extension remain valid history.

---

# 42. Revocation

Authority can be revoked without deleting content.

Examples:

- remove NetworkHandle;
- revoke SecretHandle;
- disable Module;
- remove Action request permission;
- quarantine executable version.

Grant Receipt records revocation.

Doctor can explain capability degradation caused by revoked authority.

---

# 43. Support bundle integration

Support output may include:

- extension id/version/hash;
- manifest schema;
- compatibility summary;
- granted-handle classes;
- health;
- registry generation;
- recent Transaction failures;
- customized override status.

Exclude:
- secret values;
- private payload contents;
- raw sensitive network/location data.

---

# 44. Doctor integration

Doctor should be able to answer:

- Is the extension healthy?
- What capability does it provide?
- What version/hash is active?
- What changed recently?
- What authority was granted?
- Did authority expand on update?
- Is compatibility known or inferred?
- Is a dependency missing?
- Is the extension crashing/backing off?
- Is the device customized because of it?
- Can it be safely disabled/rolled back?
- What uses it?

Doctor does not become extension mutation authority.

Doctor recommends; Actions/Transactions execute.

---

# 45. Developer tooling

Provide a future **Beast Extension SDK/Workbench** with tools such as:

- manifest validator;
- registry reference validator;
- permission/grant linter;
- compatibility tester;
- Scene/Experience preview;
- Procedure dry-run validator;
- progression-rule simulator;
- resource-budget smoke test;
- privacy/data-egress lint;
- package builder;
- local signature/hash tool;
- test harness using sanitized canonical State;
- API/contract compatibility checker.

This lowers community contribution friction without lowering runtime authority boundaries.

---

# 46. Extension conformance levels

A useful developer-facing conformance report may show dimensions rather than one badge.

Example:

    Manifest/schema: PASS
    Declarative validation: PASS
    SDK contract: PASS
    Privacy lint: PASS
    Resource declaration: PASS
    CI on Pi4 profile: PASS
    Physical TFT: NOT TESTED
    Network egress: OWNER APPROVAL REQUIRED
    Executable trust: COMMUNITY / MANUAL
    Support state: EXPERIMENTAL

This is more truthful than "Verified Plugin".

---

# 47. Owner Sovereignty

Managed Beastagotchi may refuse to activate an extension when:

- required Capabilities are absent;
- artifact is corrupt;
- compatibility is known impossible;
- policy disallows the requested authority;
- rollback/recovery requirement cannot be met.

But:

- policy refusal is not technical impossibility;
- Expert Mode may allow structured override where technically feasible;
- root/manual owner can bypass the SDK entirely;
- Beast records customized state honestly;
- Beast never sabotages the machine to enforce extension policy.

---

# 48. Unknown community code

Do not create a false promise that arbitrary community Python is safe merely because Beastagotchi has a manifest.

Options may include:

- refuse managed in-process execution by default;
- require explicit Expert/manual enablement;
- run under future process isolation;
- offer declarative rewrite path;
- let owner manually install/run outside managed support.

The platform should be open without pretending Python is capability-safe by magic.

---

# 49. Public compatibility testing

The project may collect compatibility evidence.

Evidence rows should identify:

- extension version/hash;
- Beast version/contracts;
- Pwnagotchi/Jayofelony build;
- platform/hardware/display;
- relevant capabilities;
- test type:
  - CI;
  - simulated;
  - exact artifact physical;
  - owner report;
- pass/fail/unknown;
- timestamp.

Do not extrapolate exact physical validation from nearby versions without explicit rules.

This follows the conservative PwnDoctor compatibility model.

---

# 50. Compatibility knowledge Packs

Compatibility knowledge itself may be modular content.

Examples:

- known plugin/version quirks;
- hardware support matrices;
- Pwnagotchi release changes;
- display driver notes;
- dependency conflicts.

These may update without changing Core code.

Knowledge can inform Doctor/Resolver while execution authority remains separate.

---

# 51. Aha: permission changes are part of version semantics

An extension version that changes its authority needs is materially different even if its API remains compatible.

Therefore extension identity/version review should consider both:

- behavior/data schema compatibility;
- permission/authority compatibility.

A "minor" upstream version requesting new secret/network/root-like access may require major owner review.

Do not rely solely on semantic-version labels chosen by the extension author.

---

# 52. Aha: compatibility should explain itself

Compatibility should not be one hidden yes/no computation.

Resolver should retain reasons such as:

    compatible_by_contract because:
      Beast SDK 1.2 within [1.1,2.0)
      capability gps.position available via gpsd
      Python 3.13 supported
      display class compact supported

    unknown:
      exact Jayofelony 2.9.6 physical evidence absent

This explanation becomes reusable by:
- Studio;
- Doctor;
- CLI;
- installer;
- support bundle.

---

# 53. Aha: extension authority is revocable infrastructure

Handles should make authority revocable without necessarily uninstalling the extension.

This enables future owner policies such as:

- "Allow this Experience but no Internet";
- "Use this hardware provider read-only";
- "Keep this Pack installed but disable its executable Module";
- "Allow Doctor knowledge, not remedies";
- "Preview this Scene without enabling its Actions."

That is substantially more flexible than enable/disable alone.

---

# 54. Aha: staging can be useful before trust is decided

A community object can be valuable while still quarantined.

Examples:

- inspect manifest;
- preview declarative art/Scene;
- read documentation;
- evaluate dependency plan;
- compare permission requests;
- verify signature/hash;
- scan compatibility;
- export/share metadata.

This creates a rich Depot/Studio experience without forcing "install and execute" as the first step.

---

# 55. Migration from current v0.19

Incremental path:

1. Define SDK contract/version metadata.
2. Define ExtensionManifest schema over existing Pack/plugin/provider metadata.
3. Add Grant Receipt data model.
4. Add typed handles over existing read/request operations.
5. Convert Action registry first, preserving current broker authority.
6. Convert existing provider/collector integrations to Module/Provider registrations.
7. Add inert staging/quarantine path for executable extensions.
8. Add compatibility-vector/fingerprint model.
9. Add permission-diff to update planning.
10. Dogfood declarative SDK with built-in Experiences/Procedures/Progression where practical.
11. Add extension-private storage API.
12. Add Doctor extension-health/authority views.
13. Add developer Workbench/lint tooling.
14. Evaluate process isolation only after concrete executable-community use cases justify it.
15. Preserve manual/root owner paths throughout migration.

No flag-day plugin rewrite is required.

---

# 56. Extension SDK invariants

1. Installing content never silently grants execution authority.
2. A manifest requests authority; policy grants authority.
3. No extension self-assigns Signal priority, privacy downgrade or Core trust.
4. Identity/signature does not imply safety or authority.
5. Compatibility does not imply trust.
6. Trust class does not imply unlimited authority.
7. Reputation does not escalate privilege.
8. Authority is explicit, scoped and inspectable.
9. Authority expansion on update is visible.
10. Discovery/staging of unknown code does not require executing it.
11. Declarative content is preferred for ordinary ecosystem growth.
12. Executable extensions participate in ModuleRuntime/resource policy.
13. Extensions do not receive raw DB/Core/operator-session/root access by default.
14. System mutation goes through Actions/Transactions.
15. Progression mutation goes through canonical rules/engine.
16. Presentation registration does not grant physical display ownership.
17. Secrets are scoped and never ordinary telemetry/config output.
18. Canonical privacy cannot be downgraded by extensions.
19. Unknown compatibility remains unknown.
20. Physical validation claims identify the exact tested environment/artifact.
21. Built-ins dogfood public SDK paths where practical.
22. Optional extension failure does not crash Core by default.
23. Extension authority may be revoked independently of content retention.
24. Owner-created/unsigned content remains possible.
25. Owner manual/root escape remains possible.
26. Customized state is described, not punished.
27. No fake sandbox claim: in-process Python is trusted code, not isolated code.
28. Uninstall does not silently erase irreplaceable owner state.
29. Historical provenance survives extension removal.
30. Public SDK compatibility is more stable than internal implementation layout.

---

# 57. Part 8 conclusion

Beastagotchi should be able to grow into a very large community ecosystem without making every Pack
a root plugin and without turning the platform into a locked app store.

The extension model therefore separates:

- discovery;
- identity;
- integrity;
- compatibility;
- trust class;
- authority;
- reputation;
- support state;
- activation;
- runtime health.

The core design move is explicit scoped handles plus a durable Grant Receipt.

That creates a platform where the answer to:

> "Can this extension exist?"

is independent from:

> "Can it run?"

which is independent from:

> "What exactly can it do?"

which is independent from:

> "Do we know it works here?"

which is independent from:

> "Is it officially supported?"

That distinction is what allows **hard kernel, wild ecosystem** to stay real.

The next Architecture Contract Review should define the **Presentation Platform contract**:
Surface/Scene/Experience/Choreography, page/navigation registries, input routing, responsive/adaptive
display profiles, presentation ownership, remote/exact mirror surfaces, asset/dirty-region behavior,
and how built-in and community Experiences converge without sacrificing the visual fidelity target.
