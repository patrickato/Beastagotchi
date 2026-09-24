# Beastagotchi Doctor / Explain — v0.1

**Status:** first read-only dependency/provider explanation layer implemented  
**Date:** 2026-09-24

## Product goal

Beast Doctor should answer plain operational questions from canonical evidence:

- Why is this capability unavailable?
- Why is this provider active?
- What else depends on it?
- What alternate can replace it?
- Is the problem a missing dependency, owner choice, stale provider, conflict or
  unsupported/custom state?
- What would be affected if this component disappears?

Doctor is not a second telemetry system. It consumes existing Beast Core state,
Dependency & Capability Resolver output, provider arbitration, incident/action
history and later known-good fingerprints.

## Current implementation

Module:
- `beastcore/doctor.py`
- `BeastDoctor`

Read-only API:
- `GET /doctor`
- `GET /explain?capability=<capability>`
- `GET /explain?provider=<provider>`

Structured Operator tool:
- `doctor.explain`

Current capability explanation includes:
- provider decision state;
- active provider;
- reason for selection;
- owner preference and preference issue;
- active health/evidence confidence/freshness;
- recommendation;
- fallback chain;
- ready alternates;
- Plugin/PACK `USED BY` relationships;
- downstream component count;
- effect if the active provider disappears;
- explicit automatic-failover state;
- bounded recommendations.

Provider explanation can show all capabilities for which the provider appears,
whether it is active, its readiness/selection state and blockers.

## Doctor summary

The first summary can raise attention for:
- provider choice required;
- saved preference unavailable;
- capability unavailable where known dependents exist;
- stale/degraded/blocked active provider evidence;
- low-confidence active provider evidence;
- active Plugin or Pack technical blockers.

The summary is published into canonical state:
- `doctor.state`
- `doctor.attention_count`
- `doctor.explainable_capability_count`
- `doctor.items`

A low-frequency Core loop refreshes it.

## Truth rules

Doctor must obey the same evidence rules as the rest of Beast:

- never synthesize fake telemetry;
- unknown means unknown;
- readiness does not automatically mean runtime health;
- `ready_unverified` is different from `healthy`;
- stale evidence is labeled stale;
- a recommendation is not an executed action;
- owner preference does not mean Beast silently enabled the provider;
- automatic failover remains disabled until separately validated.

## Health / confidence semantics

Current arbitration exposes **evidence confidence**, not a vendor/device quality
score.

Initial classes:

### high
Live canonical StateRegistry evidence with freshness metadata.

### medium
Good presence/requirements evidence but incomplete direct runtime proof.

### low
Catalog-only, weak, blocked or uncertain evidence.

Generic component providers are not called "healthy" merely because their
dependencies resolve. They may be:
- `ready_unverified`;
- `standby_ready`;
- `needs_attention`;
- `blocked`;
- `unavailable`.

Provider-specific adapters can later supply richer runtime health.

## Owner provider preferences

Persistent owner provider policy is implemented in:

`beastcore/provider_preferences.py`

Storage:
`/var/lib/beastagotchi/provider-preferences.json`

Properties:
- private `0600` file;
- atomic replace;
- bounded capability/provider identifiers;
- set/clear actor and timestamp evidence;
- published canonical `providers.preferences` state.

Action Broker operations:
- `provider.preference_set`
- `provider.preference_clear`

An active owner-authorized Operator session is required.

Preference operations:
- do not enable plugins;
- do not start services;
- do not switch hardware;
- do not perform failover;
- can be saved while a known provider is temporarily unavailable;
- can remain dormant until the provider becomes ready.

This lets a user express intent without Beast making an uncontrolled handoff.

## Explain-before-act principle

A durable Beast design rule:

> Before Beast offers to change an important provider/component, it should first
> be able to explain the current state and likely downstream effect.

The desired future flow is:

1. **Explain**
2. **Plan**
3. **Preview impact**
4. **Snapshot**
5. **Execute**
6. **Observe probation**
7. **Rollback or accept**
8. **Record what happened**

This should apply beyond provider switching to:
- plugin disable/remove;
- Pack uninstall/update;
- service changes;
- hardware role reassignment;
- Presentation Broker handoff;
- future package/remediation actions.

## UX direction

Doctor should not become a wall of Linux jargon.

Example:

**LOCATION**
- Using: USB GPS
- Health: Healthy
- Evidence: High confidence · updated 1.2s ago
- Used by: Expeditions, Map, Capture context
- Backup provider: PwnDroid
- Automatic failover: Off

**Why?**
> USB GPS is providing live canonical location data. PwnDroid is ready as an
> alternate. No action is needed.

If the preferred provider disappears:

**LOCATION — DEGRADED POLICY**
> You asked Beast to prefer PwnDroid, but it is not currently ready. USB GPS is
> being used as the safe fallback. Your preference has not been erased.

Actions later:
- **DETAILS**
- **USE AUTO**
- **PIN PROVIDER**
- **TEST FAILOVER**

## Lightbulb directions

### What changed since known-good?

Doctor should eventually compare current:
- packages;
- services;
- providers;
- enabled Plugins/Packs;
- hardware;
- versions;
- owner customizations;
- config fingerprints

against a user-accepted known-good snapshot.

Instead of "something broke," Doctor can say:

> Since your known-good checkpoint, gpsd changed version and PwnDroid became the
> preferred Location provider.

### Causal chain explanation

Dependency graph relationships can become human-readable chains:

`Expedition route missing -> location.position unavailable -> preferred PwnDroid
not ready -> phone link absent`

This is more useful than surfacing four disconnected warnings.

### Blast-radius preview

Before disabling a provider:

> This will affect 4 consumers. USB GPS can replace 3. One feature has no
> alternate provider.

This should become a shared planning primitive for Update Center, Plugin Center,
Pack management and Hardware Studio.

### Recovery suggestions from evidence

Doctor can rank recovery options by reversibility:
1. restore existing provider;
2. use ready alternate;
3. guided user action;
4. transactional repair;
5. owner override/manual path.

It should never fabricate certainty merely to produce a fix.

### Field-mode Doctor

On the 480×320 TFT, Doctor can condense to:
- **OK**
- **ATTENTION**
- **DEGRADED**
- **ACTION REQUIRED**

with one tap into the causal explanation.

The full browser workshop can expose the entire dependency/provider graph.

## Support evidence

Sanitized support bundles now retain:
- managed/expert/customized support state;
- provider preference count and non-secret preference identifiers;
- Doctor state/attention count;
- provider summary.

Credentials, raw logs, network identifiers and GPS coordinates remain excluded by
default.

## Next steps

1. Add Beast Studio Provider/Capability/Doctor surfaces.
2. Add causal-chain explanations across requirements, not only provider choice.
3. Add provider-specific health adapters and freshness thresholds.
4. Add known-good fingerprint/checkpoint comparison.
5. Add pre-action blast-radius simulation.
6. Add context-aware Field/Dock/Home policy explanations.
7. Add transactional TEST FAILOVER after provider handoff primitives exist.
8. Only then consider automatic failover.
