# Beastagotchi Owner Sovereignty / Unrestricted Mode — v0.1

**Status:** approved architecture / persistent Expert Mode + bounded plugin policy override implemented  
**Date:** 2026-09-24

## Principle

Beastagotchi is an owner-controlled open platform, not a locked appliance.

Safe defaults, compatibility checks, transactional changes, rollback, curated
sources and support boundaries exist to help the owner make informed choices.
They are not intended to permanently prevent the owner from modifying their own
device.

The platform therefore distinguishes:

- **managed/supported path** — Beast can validate, explain, snapshot, execute,
  observe health and roll back;
- **owner override path** — the owner deliberately proceeds outside normal Beast
  compatibility/support policy;
- **technical impossibility** — a requested action cannot actually work because
  a required resource, privilege, hardware device or executable mechanism does
  not exist.

A Beast policy warning is not the same thing as a technical impossibility.

## Owner authority

On a locally owned/administered device, the owner should be able to:

- install an arbitrary Pwnagotchi plugin;
- import a custom Beast Pack;
- add a custom repository/source;
- install additional OS packages or Python modules;
- enable or disable services;
- use unsupported hardware;
- edit configuration manually;
- run custom scripts/applications;
- choose conflicting or experimental components;
- replace or disable Beast-managed components;
- work directly through SSH/root/console outside Beast UI.

Beast should make the supported path easy, but must not present supported policy as
ownership authority over the machine.

## Modes

### Managed mode — default

Normal operation.

Beast:
- validates dependencies and conflicts;
- uses trusted/known sources when possible;
- snapshots before mutation;
- uses structured Action Broker operations;
- performs health probation;
- rolls back failed managed transactions;
- labels unsupported combinations;
- protects continuity/recovery paths from accidental taps.

### Expert / Owner Override mode

Explicit local opt-in.

This mode reveals unsupported/manual operations and permits policy bypasses that
are technically possible.

Examples:
- install an unrecognized plugin;
- use an uncurated repository;
- proceed despite a compatibility warning;
- enable two conflicting providers;
- install a package Beast does not recommend;
- bypass a recommended dependency/provider choice;
- disable a Beast component;
- edit raw configuration.

The UI should continue to explain:
- what is known;
- what is unknown;
- what Beast expects may break;
- what will lose managed rollback/support;
- what data may leave the device;
- what downstream components depend on the change.

Warnings remain informational once the owner explicitly chooses to proceed,
except where the action is technically impossible.

## Override granularity

Support both:

1. **per-action override** — "Proceed unsupported anyway";
2. **persistent Expert Mode** — exposes advanced/custom operations until disabled.

The owner should not need to fight the interface repeatedly after deliberately
enabling Expert Mode.

Persistent Expert Mode should remain visibly indicated so the current support
state is obvious.

## Local authorization

Owner Override is a local administrative capability, not a remote unauthenticated
API.

A future implementation should require an explicit local owner/admin action to
enter Expert Mode. Appropriate mechanisms may include:
- Beast Studio local admin session;
- physical-device confirmation;
- console/SSH command;
- explicit local configuration flag.

The exact UX can stay convenient while preventing an arbitrary network client from
silently switching the device into unrestricted administration.

## Policy blocker versus technical blocker

Requirement and action plans should classify blockers.

### Policy blocker
Beast's managed path recommends stopping.

Examples:
- unsupported version;
- untrusted source;
- display-owner collision;
- protected Beast component;
- provider conflict;
- missing rollback guarantee;
- resource/thermal warning.

Policy blockers are owner-overridable.

### Technical blocker
The requested operation cannot presently execute as described.

Examples:
- no writable filesystem;
- required executable truly absent when the action depends on it;
- insufficient privilege;
- impossible architecture/binary format;
- referenced file/source does not exist;
- required physical hardware is absent for a hardware-only function.

A technical blocker may become resolvable through another action, but "override"
must not pretend an impossible operation succeeded.

## Protected/self-disabling components

Some components, such as the Beast Bridge or currently active presentation owner,
may be protected from casual one-tap removal because disabling them can remove the
very UI/control path performing the operation.

That protection is a **managed-path safety feature**, not an ownership lock.

When Beast cannot safely self-remove a component from its own active control
plane, it should:
- explain why;
- offer a shutdown/maintenance plan where possible;
- provide exact manual/root instructions;
- preserve backups/config snapshots where possible;
- allow the owner to complete the change outside the running control plane.

## Unsupported/custom state

Proceeding outside the managed path should not trigger punishment or artificial
feature locks.

Beast may mark the installation as:
- customized;
- unsupported;
- dependency state unknown;
- rollback not guaranteed;
- source trust unknown.

That status exists for troubleshooting accuracy.

Beast Doctor and Support Bundles should report the customization so failures are
not misdiagnosed as a stock/managed configuration.

## Recovery philosophy

Before a risky owner override, Beast should offer:
- config snapshot;
- package/service plan;
- export of current BOM;
- recovery checkpoint;
- exact undo steps where known.

The owner may choose to continue even when complete rollback is unavailable.

The project should prefer informed freedom over forced lockout.

## Plugin & Capability Center behavior

For an unsupported plugin, Beast should be able to say:

> Plugin is not in the compatibility registry. Dependencies and side effects are
> unknown. Beast can install/copy it, but cannot guarantee configuration,
> compatibility or rollback.

Actions:
- **Inspect**
- **Install unsupported**
- **Show manual instructions**
- **Cancel**

If a known conflict exists:

> Theme Manager and Beast UI both request framebuffer ownership.

Managed recommendation:
- switch through Presentation Broker.

Expert choices may include:
- proceed anyway;
- stop Beast UI and enable Theme Manager manually;
- open exact manual instructions.

## Dependency/BOM behavior

The Dependency & Capability Resolver remains advisory in Owner Override mode.

It should still calculate:
- missing requirements;
- conflicts;
- provider overlap;
- data egress;
- version mismatch;
- resource impact.

But policy conflicts become warnings rather than absolute prohibition when the
owner explicitly overrides them.

The full BOM remains useful precisely because Expert Mode makes arbitrary
customization possible.

## Generic/manual administration

The long-term system may expose an owner-authorized direct administration surface
for operations that do not fit a curated Beast action.

That capability must remain clearly separate from normal app/plugin automation.

Design goals:
- local owner authorization;
- obvious elevated-mode indicator;
- no silent background elevation;
- command/action audit where practical;
- no claim of managed rollback for arbitrary commands;
- no requirement that every future Linux modification first be blessed by the
  Beast compatibility registry.

SSH/root console remains the ultimate escape hatch even if Beast's own managed
UI does not yet expose a given operation.

## Security model

Owner freedom does not mean removing ordinary access control.

Beast should still protect the device from:
- unauthenticated remote callers;
- accidental taps;
- silent privilege escalation by plugins;
- background components changing unrelated settings without authorization.

The distinction is:

**the authenticated owner can override Beast policy; arbitrary software or remote
clients cannot impersonate that owner decision.**

## Licensing / warranty / liability posture

Beastagotchi is GPLv3-licensed. GPLv3 sections 15 and 16 already provide a strong
"as-is" warranty disclaimer and limitation of liability to the extent permitted
by applicable law.

Project documentation may clearly state that:
- unsupported/custom modifications are performed at the user's risk;
- compatibility and rollback are not guaranteed outside managed paths;
- third-party plugins/packages/services have their own licenses, terms and risks.

The project should **not** claim that a sentence in the UI can guarantee zero
liability in every jurisdiction. Legal effect depends on applicable law and the
circumstances. Any additional project-specific legal wording intended for public
distribution should be reviewed separately.

This architecture decision is about technical owner freedom, not an attempt to
override third-party licenses, service terms or applicable law.

## Current implementation boundary

Implemented now:
- architecture decision documented and tracked in roadmap/matrix/continuity;
- persistent `OwnerModeManager` state at
  `/var/lib/beastagotchi/owner-mode.json` with mode file permissions `0600`;
- entering/leaving persistent Expert Mode is an audited Action Broker mutation
  requiring an active owner-authorized `administrator` session;
- read-only owner-mode status is exposed through canonical Core state,
  `GET /owner-mode`, and structured Operator tools;
- PluginBroker plans distinguish policy blockers from technical blockers;
- plugin toggles may use explicit `owner_override=true` only while Expert Mode
  is enabled;
- technical blockers remain non-overridable;
- successful policy overrides retain the existing PluginBroker snapshot,
  config verification, Pwnagotchi restart/health observation and rollback path;
- successful policy overrides persist a customized/support state with override
  count, last action/target and policy-blocker evidence;
- sanitized Support Bundles include Expert/customized status so a custom system
  is not misrepresented as fully managed;
- override use and Expert Mode changes generate durable action/event audit
  evidence;
- older managed PluginBroker callers/test doubles remain compatible; an older
  broker cannot silently accept an override it does not understand;
- SSH/root/manual administration remains outside Beast policy as the final escape
  hatch.

Not implemented yet:
- dedicated Beast Studio/TFT Expert Mode control/indicator;
- arbitrary/unknown plugin installer/source import executor;
- generalized unsupported package/service executor;
- raw config editor;
- exact generated manual maintenance instructions for all self-disabling actions;
- owner-authorized direct administration/shell surface;
- a verified "return to managed baseline" operation that can clear customized
  support state after proving the machine matches a known managed configuration.

This milestone intentionally enables owner override only for the existing,
transactional plugin-toggle path. It does not turn Expert Mode into a generic
unchecked command executor.

## Implementation order

1. Add a dedicated Beast Studio/TFT Expert Mode control and obvious indicator.
2. Extend policy-vs-technical blocker schemas beyond PluginBroker into the common
   Dependency & Capability Resolver.
3. Add reverse `used_by` impact to override confirmations.
4. Add exact manual-instruction escape hatches for operations Beast cannot safely
   perform on itself.
5. Add transactional arbitrary plugin/source import where technically possible.
6. Add package/service custom operations with dry-run/audit.
7. Add a verified return-to-managed-baseline workflow before offering to clear
   customized support state.
8. Consider a direct owner administration surface only after its local-auth,
   audit and recovery boundaries are explicit.
