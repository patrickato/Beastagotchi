# Beastagotchi Doctor Source Trust & Fleet Evidence Model

**Date:** 2026-09-26  
**Status:** preserved design direction; implementation details deferred  
**Purpose:** capture how Doctor should evaluate candidate fixes, external artifacts, and Global Doctor evidence without collapsing everything into one vague trust score.

## Core rule

Doctor should judge a candidate repair using multiple independent dimensions:

1. **Source provenance** — who published it, whether identity/source can be verified, whether source code/signatures/hashes exist.
2. **Patient match** — how closely the candidate applies to this exact Beast's hardware/software/config/symptom profile.
3. **Fleet evidence** — what happened on comparable Beasts that actually tried it.
4. **Recency** — whether evidence applies to current kernels/drivers/builds.
5. **Local diagnosis** — whether this Beast's observed failure supports the repair hypothesis.
6. **Recovery readiness** — snapshot/backups/rollback/probation/cleanup available before mutation.

Do not equate `official` with `works`, and do not equate `unofficial` with `bad`.

## Separate provenance from empirical outcome

**Provenance asks:**
> Who made this artifact and can Doctor establish what it is?

**Empirical evidence asks:**
> What actually happened when machines like this used it?

**Local diagnosis asks:**
> Does it make sense for this patient right now?

Doctor combines all three.

## Example evidence summary

A candidate community driver may show:

- source: community GitHub fork;
- official/vendor: no;
- source available: yes;
- release/hash verified: yes;
- hardware match: exact;
- kernel match: exact;
- symptom match: exact;
- fleet cases: 187;
- closely comparable cases: 52;
- verified successes in close cohort: 49;
- rollbacks: 2;
- unknown: 1;
- latest close success: 3 days ago;
- recovery snapshot: ready;
- rollback: ready.

This is more useful than an unexplained `82% confidence` value.

## Cohort-aware evidence

Overall popularity must never hide a bad local cohort.

Example:

> `97% success globally, but 0/13 success on your exact chipset + kernel generation.`

Doctor should reject/deprioritize the repair for this patient despite broad popularity.

Matching dimensions may include:

- board/platform/revision;
- architecture;
- exact peripheral IDs;
- kernel/build;
- driver/module version;
- Pwnagotchi/Jayofelony build;
- Bettercap version;
- Beast version;
- plugin/provider/package versions;
- relevant config fingerprint;
- failure/System Graph location;
- recent-change signature.

## Verified outcomes carry more weight than votes

Do not treat user thumbs-up/down as equivalent to Doctor-verified outcomes.

Strong evidence includes:

- capability demonstrably failed before;
- standardized probe evidence captured;
- repair applied through known Transaction/Procedure;
- intended capability actually worked afterward;
- probation passed;
- no immediate rollback;
- no immediate recurrence;
- later recurrence/failure recorded when known.

Negative evidence is retained. Failed fixes should be demoted/quarantined, not erased.

## Candidate recommendation classes

Names remain adjustable, but useful semantics include:

- **Verified** — strong provenance and strong applicable evidence;
- **Recommended** — good applicable evidence and reasonable provenance;
- **Community Proven** — unofficial but repeatedly verified on close matching systems;
- **Experimental** — plausible with limited evidence;
- **Unverified** — weak provenance/outcome evidence;
- **Known Bad / Incompatible** — evidence says not to use on this patient;
- **Obsolete** — historical solution no longer applicable to current versions;
- **Regression Suspected** — previously successful but recent matching failures indicate a compatibility change.

## Source tiers influence autonomy, not truth by themselves

Possible sources include:

- OS/vendor/project official repositories;
- official signed releases;
- known upstream GitHub projects;
- widely used community forks;
- forum-linked source code;
- unknown binary/archive links.

Doctor may search/read broadly, but mutation authority becomes stricter as provenance/risk weakens.

## Owner sovereignty + risk communication

Doctor's job is to:

- disclose source/provenance;
- explain evidence and close-match outcomes;
- explain uncertainty;
- prepare snapshot/rollback;
- show what will change;
- classify risk;
- verify actual outcome;
- clean up after the attempt.

If the owner explicitly chooses to proceed on a lower-trust path, Doctor should execute through managed recovery/Transaction mechanisms where technically possible and record the actual outcome.

## Fleet learning

The Global Doctor network may build empirical reputation from sanitized outcomes over time.

Useful aggregate facts include:

- verified uses;
- success/partial/rollback/unknown counts;
- success rates for specific cohorts;
- current-version recency;
- recurrence/regression patterns;
- maintainer-reviewed status where applicable;
- Sandbox/regression-test evidence;
- physical-device verification evidence.

A source/repair can lose confidence automatically for a cohort when new versions begin failing.

## Population-baseline relationship

Doctor may compare not only failed cases but healthy cohorts.

This enables statements such as:

> `This device enumerates differently from 97% of healthy matching units.`

or:

> `This driver's packet-flow pattern is outside the healthy cohort despite all services reporting active.`

Population baselines can therefore improve both diagnosis and repair verification.

## User-facing presentation

TFT should remain concise:

> `HIGH CONFIDENCE`  
> `49 / 52 close matches repaired successfully`  
> `hardware + kernel match`  
> `rollback ready`

Technical details/WebUI can expose source tier, exact cohort, failures, recency, matching dimensions, raw evidence, and repair provenance.

## Decision

This model is preserved for later implementation design. Exact scoring formulas, anti-abuse mechanics, signing, server architecture and schema are intentionally deferred.
