# Beastagotchi Doctor Knowledge Runtime & PwnDoctor Cross-Pollination Review
## 2026-09-24

Status: active architecture direction.

This document records the review of the Pwnagotchi-only Doctor roadmap and the new direction it suggests for Beastagotchi.

Reviewed source:
- patrickato/test-plugins @ claude/happy-newton-60zxt8
- pwnagotchi-plugins/DOCTOR_ROADMAP.md
- pwnagotchi-plugins/BUILD_LIST.md
- pwnagotchi-plugins/README.md
- PwnDoctor v0.4 implementation and tests
- Claude's Beast-side Doctor cross-pollination note

## 1. Preserve the central insight

The PwnDoctor and Beast Doctor are complementary.

PwnDoctor is strongest at broad direct host sensing, condition matching, confidence-gated detection, bounded remediation, circuit breaking, verify-after-action, incident lifecycle and known-good drift.

Beast Doctor is structurally stronger at canonical Signals, the dependency/provider graph, blast radius, Action Broker, owner policy, Recovery Vaults, update/recovery state, Packs/Capabilities and cross-surface Explain/Inspect UX.

The desired Beast Doctor flow is:

Observe -> Explain -> Resolve knowledge -> Plan -> Preview impact -> Snapshot -> Authorize -> Execute through Action Broker -> Probation -> Verify -> Commit/Rollback -> Record

## 2. Do not let Doctor become a monolith

Doctor should have a small trusted runtime plus externally loadable knowledge.

Doctor Kernel responsibilities:
- incident lifecycle
- evidence/confidence model
- probe scheduler
- policy/autonomy engine
- condition evaluator
- knowledge resolver
- remediation planner
- Action Broker integration
- verification/probation
- circuit breakers
- audit/provenance

Doctor Knowledge / Skill Packs may contain:
- conditions
- runbooks
- version applicability
- read-only probes
- optional remediation recipes
- support evidence recipes
- deep links
- validation rules

The Doctor grows mostly by adding packs, not by accumulating giant if/else blocks in core.

## 3. Doctor Knowledge Resolver / Skill Cache

The user's key idea is adopted: Doctor should be able to know what knowledge/tool it needs, fetch that bounded resource from an approved source, use it, and cache/archive it rather than requiring every possible ailment to ship permanently in Core.

This becomes the Doctor Knowledge Resolver.

Resolution order:
1. built-in critical conditions/runbooks
2. already-installed/cached Doctor Packs
3. installed plugin/Pack-provided health knowledge
4. local Runbook Registry / Field Library
5. trusted project catalogs/repositories
6. explicitly approved external source

Pack classes:

### Knowledge Pack
Data only: condition definitions, cause/explanation, applicability, runbooks, links and provenance. May be automatically fetched when policy permits because it cannot execute code.

### Probe Pack
Adds read-only diagnostics. Requires declared inputs, time/resource limits, isolation where practical, no arbitrary mutation and provenance/hash verification.

### Remedy Pack
Adds remediation recipes or new Action adapters. It never gains permission merely because it was downloaded. It must pass trust policy, schema validation, action allow-listing, blast-radius analysis, snapshot/rollback support, owner autonomy policy and probation/verification requirements.

Fetched knowledge should normally be cached rather than deleted immediately for offline use, reproducible incident explanation, support provenance and faster repeat diagnosis.

Cache metadata should include version, hash, source, fetched_at, last_used, applies_to, expiration/update policy, pinned/critical status and storage budget. Suggested persistent location: /var/lib/beastagotchi/doctor/. Ephemeral probe state belongs under /run rather than persistent SD storage.

## 4. Dynamic acquisition must not become arbitrary web-code execution

Doctor may fetch knowledge broadly. Doctor may fetch tools narrowly.

A web search result or README must never become executable root code merely because Doctor found it useful.

Acquisition flow:
Need identified -> source resolved -> provenance verified -> schema/type classified -> bounded download -> checksum/signature/trust checks -> sandbox/read-only test -> register capability -> use -> record provenance

If a missing package/executable is required, Doctor invokes the Capability Recipe / Transaction path rather than silently installing packages.

## 5. Improve PwnDoctor's two-level risk model

The current safe/risky model is a good prototype but too coarse for Beast. Each Action/remedy should independently declare:
- reversible
- destructive/data-loss potential
- persistence
- service interruption
- connectivity impact
- privacy impact
- recovery dependency
- reboot required
- blast radius
- confidence requirement
- probation duration
- emergency suitability

Examples: stopping wpa_supplicant may be low-risk when it is demonstrably hijacking the monitor adapter and not providing the uplink, but it is not universally safe. Vacuuming journald removes diagnostic history. Remounting a read-only filesystem read/write can be the wrong response when media failure is suspected.

## 6. Verification truth rule

If remediation executes but post-action verification cannot run, the outcome is executed / verification_unknown. Never silently treat failed verification collection as success.

Suggested outcomes: resolved_verified, improved_verified, unchanged_verified, worsened_verified, executed_verification_unknown, execution_failed, rolled_back_verified, rollback_verification_unknown.

## 7. Persistent circuit breakers

Remediation attempt budgets must survive process restarts. Store bounded records for condition/action, timestamps, outcomes, failure streak, last successful remedy and last rollback.

## 8. Remedy efficacy can guide but not grant authority

Track remedy success rate, recurrence, time-to-recurrence and per-device history. Use it to rank suggestions, stop ineffective repeated repairs and escalate chronic incidents. Do not let historical success automatically raise privilege or override evidence-confidence requirements.

## 9. Avoid false precision in a 0-100 health score

A single health number can imply more certainty than exists. Preferred primary status remains OK / ATTENTION / DEGRADED / ACTION REQUIRED / UNKNOWN-INCOMPLETE EVIDENCE. A future numeric value must be a transparent summary index with visible components and confidence, not a diagnosis truth score.

## 10. One Doctor, provider-contributed knowledge

The PwnDoctor roadmap's 'become the hub' idea is accepted. Plugins/providers should be able to contribute Signals, health findings, condition definitions, runbooks, support evidence, safe Actions/remedies and backup scope.

Beast should not create competing Radio Doctor / Display Doctor / Storage Doctor products. Those are specialist probes/views behind one Doctor.

## 11. Avoid persistent JSON-file chatter

For plain Pwnagotchi, prefer an in-process provider registry where practical, or ephemeral JSON snapshots under /run/pwnagotchi/health.d/, over frequent writes to /etc/pwnagotchi or other SD-backed state.

A provider snapshot can declare provider/plugin id, timestamp, health, confidence, observations, conditions, version and optional deep link.

## 12. Condition Packs should be shared across projects

A neutral schema should support id, schema/version, applies_to, required Signals, detect boolean tree, severity, confidence, symptom, cause, runbook, deep links, optional remedy, verification, causal relationships and provenance.

PwnDoctor can bind canonical names to local collectors. Beast Doctor can bind the same condition to StateRegistry/Signal definitions. The projects can share knowledge without sharing identical engines.

## 13. On-demand consults

A useful user-facing metaphor is: Doctor consults a specialist.

Examples:
- display problem -> load Display knowledge/probe
- no captures -> consult Radio/Pwnagotchi condition pack
- unfamiliar UPS -> resolve UPS provider health pack
- new Jayofelony release -> load matching compatibility pack
- unknown plugin crash -> fetch its verified README/runbook metadata

## 14. Upstream compatibility becomes a Doctor knowledge source

Jayofelony release compatibility should feed Doctor. A release-specific Compatibility Pack can provide expected paths, service names, plugin API signatures, default config schema, Python/kernel/driver expectations, migration notes, changed system files, required Beast shims and known Doctor conditions.

Unknown upstream versions trigger compatibility probing/safe mode rather than blind failure.

## 15. Tailscale / WireGuard / NAS cohesion

These are optional connectivity/storage providers. Doctor consumes their health for remote WebUI/Studio reachability, BenchLink, Recovery Vault access, support collection and backup destination health. Doctor diagnoses the transport but does not own its implementation.

## 16. Recommended near-term project handling

Do not abandon Beastagotchi for a long plugin detour.

Recommended sequence:
1. preserve and assimilate the PwnDoctor architectural lessons now
2. define shared Condition Pack v1 + Doctor Knowledge Resolver contract
3. keep Claude's plugin branch intact as the Pwnagotchi research implementation
4. create a separate integration/review branch before merging those plugins to test-plugins/main
5. physically validate a focused subset first: Doctor, display_setup_helper, why_no_handshakes, captive_portal, conflict_referee, mesh_vpn_presence and stat_source_bridge
6. feed lessons back into Beast
7. return primary implementation attention to Beast v0.19 visual reconstruction, Scene/Signal/Experience work

This is a bounded cross-pollination sprint, not a project pivot.

## 17. New project principle

Doctor does not need to know everything at boot. Doctor needs to know how to recognize what it does not know, resolve the right trusted knowledge, and use it safely.

Also refine Claude's phrase 'sensing is broad and unlimited' to: sensing is broad but bounded, because network-active, expensive, privacy-sensitive or intrusive probes require cadence and policy.
## 18. Reuse Beast Pack infrastructure rather than inventing another package taxonomy

Doctor knowledge should normally travel through existing Beast Pack mechanics using content roles such as:
- doctor.condition
- doctor.runbook
- doctor.probe
- doctor.compatibility
- doctor.support_recipe

This preserves one intake/trust/checksum/dependency/update model. A Doctor role does not create a fifth user-facing extension class.

Standalone PwnDoctor can still consume the same neutral condition/runbook files without requiring Beast Packs.

## 19. Doctor coverage/self-health

Doctor should be able to explain what it can and cannot currently diagnose.

Each probe/provider should expose:
- available / unavailable / degraded
- last successful observation
- freshness
- permissions/capabilities required
- cost class
- reason unavailable

Doctor can then show a coverage view such as:
- storage: covered
- display: covered
- radio: covered
- UPS battery: specialist not installed
- GPS: hardware unavailable
- Jayofelony 2.9.x compatibility: pack loaded

This prevents a healthy-looking Doctor page from implying it checked things it could not observe.
## 20. Patient Chart — what Doctor keeps permanently close

The durable local Doctor memory should focus on **this exact patient**, not every possible ailment in the ecosystem.

Patient Chart contents may include:
- board/SBC identity and architecture
- CPU/RAM/storage profile
- display/touch hardware
- radios/adapters and assigned roles
- kernel/Nexmon/firmware/Pwnagotchi/Bettercap/pwngrid versions
- enabled plugins/providers and their versions
- known-good fingerprints/checkpoints
- recurring/chronic incidents
- remediation attempts and verified outcomes
- device-specific quirks learned with evidence
- backup/recovery freshness and available Recovery Vaults
- current Doctor probe/coverage map

The Patient Chart is bounded technical history, not an unlimited raw-log archive.

This gives Doctor continuity after reboot/offline use while letting generic medical knowledge remain modular.

Design sentence:

**Doctor permanently remembers the patient; Doctor does not permanently carry every medical textbook.**
## 21. Permanent local Doctor memory is split by responsibility

Doctor should keep three durable local records plus a modular knowledge library:

### Patient Chart — what is true about this patient
Hardware/build identity, known-good baselines, incident history, recurring conditions, verified remedy outcomes, device-specific quirks, backup/recovery state and diagnostic coverage.

### Standing Orders — what the owner permits
Autonomy ceiling, pre-authorized safe actions, confirm-required actions, emergency-rescue authorization, maintenance windows, privacy/network policy and remote-support policy.

### Local Formulary / Toolbox — what is available and proven
Installed diagnostic providers, executables/services, cached packs, remediation adapters, Recovery Vaults and locally validated component versions.

### Medical Library — generic knowledge
Condition packs, runbooks, compatibility notes and specialist knowledge resolved from built-in, cached or trusted external sources.

Contract sentence:

**Patient Chart says what is true. Standing Orders say what is permitted. Toolbox says what is available. Medical Library says what is known.**
## 22. PwnDoctor collaboration split

The standalone PwnDoctor collaboration now has an explicit division of labor based on demonstrated strengths.

### Claude lane — standalone Pwnagotchi product implementation
- collectors/effectors and new ailments
- built-in condition migration to bundled JSON packs
- ACTION_META-driven local policy engine
- plugin lifecycle/UI
- incident/verification loop implementation
- release engineering and physical-validation checklist
- offline-first standalone product behavior

### OpenAI lane — shared contract and hardening
- Condition Pack schema evolution
- canonical Signal/key stewardship
- loader/security/truth semantics
- Patient Chart model and chronic/recurrence memory
- guard-intent vocabulary
- provenance/signing later
- Jayofelony compatibility contracts
- Beastagotchi adapters/interoperability

### Shared review
Canonical-key changes, public schema changes, treatment-authority changes and public compatibility decisions require both sides to review before being treated as stable.

## 23. Chronic/recurrence Patient Chart rule

Patient Chart recurrence is **episode based, not scan based**.

A condition that stays open across many scans is one episode. Clearing and later reappearing creates another episode. This avoids false recurrence inflation and avoids needless SD writes.

The Chart may remember compact per-condition recurrence and remedy efficacy fields, while the Incident Engine remains the source of truth for the detailed open/resolved incident lifecycle.

## 24. Shared Condition Pack truth semantics

Condition expressions should be internally tri-state: true / false / unknown.

Detection fires only on proven true. Verification preserves unknown so missing post-action evidence yields `executed_verification_unknown`, never a false success or false failure.

This truth rule should be preserved when Beast Doctor eventually binds the same neutral Condition Pack schema to canonical Beast Signals.