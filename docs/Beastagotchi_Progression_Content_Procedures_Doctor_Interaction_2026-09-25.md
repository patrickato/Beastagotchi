# Beastagotchi Progression, Content Delivery, Procedures & Doctor Interaction Notes

**Date:** 2026-09-25  
**Status:** architectural/product design record; not all items are release-blocking

## 1. Progression must comfortably support level 100

Level 100 must be a real long-term progression target, not a number that assumes the owner has
completed every secret, achievement, rare event or optional content item.

Design requirements:
- reaching level 100 should take meaningful time;
- no single category is required to be exhausted;
- multiple independent XP/progression sources must overlap;
- enough total earnable progression must exist that missed/retired/seasonal/rare content does not
  permanently strand a Beast below level 100;
- normal Pwnagotchi/Beast activity should remain a major source of progression;
- achievements, discoveries, milestones, Doctor/maintenance events, expeditions, location/context,
  secrets, Rare Moments, roster activity and optional interactions may add additional routes;
- progression economics should support future expansion without changing historical truth;
- post-release content may add new progression opportunities rather than requiring every future
  branch to exist on day one.

The economy should be designed with **surplus progression opportunity** rather than exact-completion
math.

## 2. Breeding / synthesis / Monsters / reveals

Breeding/synthesis should have its own meaningful visual lifecycle when content supports it.

Potential choreography:
- eligibility / readiness;
- owner confirmation/choice;
- pairing/inputs;
- synthesis/breeding sequence;
- incubation/build/formation phase if applicable;
- reveal;
- Monster classification / rarity / lineage result;
- larger celebratory cinematic for Monster or exceptional outcomes;
- memory/achievement/roster update.

Monster reveals should generally feel more significant than ordinary Beast creation/reveal.

These sequences should remain choreography/content-driven so different lineages can represent
creation differently.

## 3. Release completeness versus future content

Not every post-release content branch must be finished before initial Beastagotchi release if the
core contract already supports it and users cannot legitimately reach it immediately.

Examples:
- later breeding-age content;
- advanced Monster reveal variants;
- future legendary/rare branches;
- additional cinematics;
- later progression content.

If a future-facing control or page must already exist in the UI, it must be honest:
- `COMING SOON`;
- `UNDER CONSTRUCTION`;
- unavailable/dimmed with reason;
- roadmap/version hint where appropriate.

Never present an unfinished feature as if it is active.

## 4. Optional content delivery

Beast Studio/WebUI should be capable of becoming the primary content manager.

Potential distribution sources:
- GitHub Releases for project-owned versioned downloadable bundles;
- project Depot/catalog metadata referencing upstream/project/community sources;
- direct project content hosting later if scale requires it;
- optional mobile companion application in the future;
- local import from file/URL;
- local/network libraries.

GitHub is suitable for many project-owned Packs/releases but should not be assumed to be the
forever CDN for an arbitrarily huge media ecosystem.

Users should be able to build named local selections such as:
- My Faces;
- My Experiences;
- My Cinematics;
- Trip/Offline Set;
- Minimal Set;
- Full Local Set;
- custom named collections.

Content manager should understand available / installed / enabled / active / cached / pinned.

## 5. New platform concept: Procedures / Runbooks / Recipes

The owner idea of pressing one item and executing a known sequence should become a first-class
platform concept rather than a collection of hidden shell scripts.

Working term: **Procedure**.

A Procedure is a reusable, inspectable, owner-invoked workflow composed from registered Actions,
read-only probes and Transactions.

Examples:
- Gather My Info;
- Clean Up;
- Prepare Device for Offline Use;
- Full Doctor Checkup;
- Build Support Bundle;
- Validate Display/Touch;
- Plugin Health Audit;
- Backup Before Trip;
- Storage Audit;
- Network/Radio Diagnostics;
- Refresh Compatibility Information;
- Validate Known-Good Drift;
- Prepare for Upgrade;
- Recovery Intake;
- Performance/Thermal Snapshot.

A Procedure declares:
- id/title/description;
- scope: Pi / Pwnagotchi / Beastagotchi / cross-layer;
- read-only vs mutating;
- risk class;
- required privileges;
- required capabilities;
- expected duration;
- ordered steps;
- owner confirmations;
- whether secrets/credentials are ever required;
- outputs/artifacts;
- verification;
- rollback/transaction behavior;
- audit/provenance;
- compatibility requirements.

### Consent / privileged input

Do not casually collect administrator passwords in WebUI forms.

Preferred designs:
- use a narrowly scoped privileged Beast helper/service where appropriate;
- rely on the owner's existing authenticated/operator session;
- request explicit confirmation before privileged Actions;
- if an external credential is genuinely unavoidable, use an ephemeral one-shot secret channel,
  never write it to logs/state/history/database, zero/discard it after the immediate operation, and
  make that behavior explicit to the owner.

A Procedure must show a plan before mutation when practical.

### Output modes

The same Procedure may produce:
- raw technical transcript;
- downloadable report;
- clean human-readable summary;
- machine-readable JSON/status;
- Doctor interpretation;
- Studio/TFT presentation.

Example: `Gather My Info`

Raw probes may collect non-secret platform/build/display/kernel/Python/storage/provider/plugin data.
The default owner-facing result should be synthesized:

    Platform: Raspberry Pi 4 Model B
    OS/Image: Jayofelony Pwnagotchi <version>
    Beastagotchi: <version>
    Python: <version>
    Kernel: <version>
    Display: ILI9486 480x320
    Touch: XPT2046/ADS7846
    Storage: <summary>
    Doctor: <summary>
    Plugins: <healthy / attention / disabled counts>

Expert mode may reveal the detailed technical evidence and raw transcript.

## 6. Procedures are not arbitrary executable buttons

The normal platform should not make opaque scripts equivalent to trusted Actions.

Managed Procedures should use:
- registered probes;
- registered Actions;
- Transactions;
- capability checks;
- typed outputs;
- verification;
- audit.

Expert/manual users remain free to run their own shell scripts outside the managed Procedure
contract, and future community Procedure packs may exist with explicit provenance/trust status.

## 7. Doctor interaction model

Doctor is not only a background scanner and not only a text page.

Doctor should have multiple interaction surfaces sharing one canonical Patient Chart.

### Doctor can be called by the owner
- quick Doctor status from TFT;
- full Doctor page on TFT;
- Studio/WebUI Doctor workspace;
- Procedure: Full Checkup;
- Procedure: Diagnose This;
- context action from another page/plugin/provider;
- CLI/headless access later.

### Doctor can call the owner
Doctor may surface:
- passive status indicator;
- transient notice;
- attention badge;
- finding card;
- interactive recommendation;
- confirmation-required treatment;
- critical full-screen intervention when justified;
- post-treatment verification/result;
- recurrence / chronic-condition message;
- drift / known-good warning.

Severity should control interruption level.

### Doctor response layers
1. **Glance:** Healthy / Attention / Critical + small reason.
2. **Explain:** plain-language summary of what is wrong and why it matters.
3. **Evidence:** exact Signals/probes/history that support the finding.
4. **Plan:** what Doctor proposes to do.
5. **Consent:** required when policy/risk says so.
6. **Treat:** registered Action/Transaction.
7. **Verify:** prove fixed / failed / unknown.
8. **Remember:** Patient Chart recurrence/remedy outcome/known-good drift.
9. **Escalate:** owner, support bundle, manual instructions or community report when Doctor cannot
   safely resolve it.

### Visual interaction principle

Doctor should feel like a living subsystem of Beastagotchi rather than a generic Linux log viewer.
Its presentation may be visual, textual and interactive simultaneously:
- body/system health map;
- affected subsystem highlighting;
- timeline/recurrence;
- known-good comparison;
- before/after state;
- decision trace;
- treatment progress;
- owner prompts.

Raw terminal/log evidence remains available underneath the clean interpretation.


## 7A. Doctor heartbeat / vital-sign affordance

A small persistent **heart / vital-sign / heartbeat** affordance is a preferred Doctor entry point
for the TFT.

It should feel alive rather than like a static status LED.

Possible semantic states:
- **green** — healthy / no action needed;
- **yellow / amber** — attention / advisory;
- **red** — critical / owner action strongly recommended;
- **blue** — informational / observation / recovery / Doctor watching a condition, exact semantic
  meaning to be finalized before implementation.

Visual behavior may reinforce severity:
- healthy: slow calm pulse / soft heartbeat;
- attention: slightly stronger or irregular pulse;
- critical: faster/stronger pulse or sharper waveform, without becoming seizure-like or annoying;
- recovery/observation: cool pulse, breathing glow or alternate cadence.

The icon may include:
- heart silhouette;
- ECG/vital line;
- glow;
- hue shift;
- aura;
- brief flash;
- pulse/throb.

These effects are presentation semantics, not additional factual telemetry.

Tap/activate should navigate to the health/Patient Chart surface, with deeper Doctor/actions available
from there.

Experience-specific rendering is encouraged:
- Forge may render the health pulse like a machine status oscillator;
- Observatory may render it as a trace;
- Habitat may render it more organically;
- Monolith may reduce it to one restrained glowing mark.

Same canonical Doctor state, different Experience presentation.

## 7B. Clearer owner-facing treatment language

Avoid making the primary call-to-action unnecessarily clinical or ambiguous.

Preferred primary labels depend on context:
- **TAKE ACTION** — broad/default recommendation;
- **FIX THIS** — simple low-risk remediation where the result is obvious;
- **START TREATMENT** — Doctor-oriented but understandable;
- **RUN CHECK** / **RUN DIAGNOSTIC** — investigation, not treatment;
- **REPAIR & VERIFY** — suitable when rollback/verification is part of the transaction;
- **RESTART & VERIFY** — explicit service recovery case.

"Plan Treatment" can remain an explanatory/internal concept, but the user-facing button should say
what will actually happen.

The plan screen still appears before mutation when appropriate.

## 8A. Procedures must surface Doctor next steps

Any Procedure whose results correspond to Doctor findings should expose those findings directly.

A Procedure result may offer:
- `VIEW DOCTOR`;
- `TAKE ACTION`;
- a specific Action such as `CLEAN CACHE`, `RESTART & VERIFY`, or `BUILD SUPPORT BUNDLE`;
- `DETAILS / EVIDENCE`;
- `IGNORE / REMIND LATER` where appropriate.

The user should not be forced to manually leave the Procedure, open Doctor, find the same finding,
and rediscover an already-known next step.

Doctor remains the health authority; Procedure results may provide contextual deep links/actions
into that authority.


## 8. Doctor and Procedures reinforce each other

Doctor may recommend a Procedure.
A Procedure may invoke Doctor intake/verification.
Doctor may explain Procedure results.
Transactions generated by Procedures should feed Doctor Patient Chart and recovery evidence.

This creates a useful loop:

    observe -> explain -> plan -> approve -> execute -> verify -> summarize -> remember

without forcing every useful workflow to be hand-authored as bespoke UI logic.
