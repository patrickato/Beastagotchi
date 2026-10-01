# Beastagotchi Doctor Collective Knowledge Network

**Date:** 2026-09-26  
**Status:** strong candidate / active Doctor jam; not final implementation canon

## Core idea

> **Every successfully diagnosed Beast/Pwnagotchi can teach every other Doctor, without requiring raw personal data to be globally exposed.**

A Doctor case may produce a structured, privacy-sanitized knowledge contribution describing:

- normalized hardware fingerprint;
- relevant OS/kernel/driver/runtime versions;
- Pwnagotchi/Bettercap/Beast versions;
- relevant provider/plugin/package versions;
- symptom/failure signature;
- evidence/probes that mattered;
- hypotheses considered/rejected;
- exact repair Procedure/steps used;
- artifact/source provenance;
- outcome (success/failure/rollback/partial);
- verification evidence;
- later recurrence/regression information;
- case age/recency;
- optional owner notes where explicitly shared.

The global service can aggregate many such reports into reusable empirical knowledge.

Example owner-facing result:

> `43 comparable cases found.`  
> `31 match this Beast's hardware/software profile at >=79%.`  
> `Repair path A succeeded on 28/31 closely matching cases.`  
> `3 failures were all kernel 6.x + driver revision Z; your Beast uses the corrected revision.`

Doctor then combines this evidence with official documentation, this patient's live state, Known-Good history, and local Doctor knowledge before recommending or acting.

## Privacy / identity

Do not upload raw machine dumps by default.

Preferred public contribution is a **normalized case envelope**, not a personal diagnostic archive.

Use privacy controls and pseudonymous identifiers inspired by existing Global publish concepts:

- no owner name/account identity required for case utility;
- no raw SSIDs/BSSIDs/peer identities/GPS routes/capture content by default;
- secrets/tokens/passwords/private keys never uploaded;
- file contents only when specifically safe/normalized/approved;
- exact local paths/usernames may be normalized where possible;
- hardware/software versions and configuration facts included only when diagnostically useful;
- public Doctor identity may be pseudonymous/rotatable;
- opt-in / policy-controlled upload and automatic sync;
- owner can inspect contribution summary before first upload / when policy requires.

A public case identifier should not imply a stable real-world person identity.

## Matching

Similarity should be evidence-based rather than one opaque percentage.

Potential dimensions:

- board/platform;
- architecture;
- kernel generation/build;
- driver/module versions;
- exact peripheral hardware/USB IDs;
- display/radio/controller family;
- Pwnagotchi build/version;
- Bettercap version;
- Beast version;
- plugin/provider/package versions;
- relevant configuration fingerprint;
- symptom signature;
- System Graph failure location;
- recent change signature.

Doctor may derive a human-friendly similarity score while retaining the component explanation:

> `79% comparable overall`  
> `hardware: exact`  
> `kernel: close`  
> `driver: exact`  
> `Pwnagotchi: same branch`  
> `display config: differs`

## Confidence / competence growth

A repair/fix should accumulate evidence rather than being globally stamped true after one success.

Candidate evidence affecting confidence:

- official/vendor documentation support;
- Beast-maintainer reviewed Procedure;
- successful local verification;
- number of independent successful cases;
- number of closely matching successful cases;
- failures/rollbacks;
- recurrence after apparent success;
- hardware/software similarity;
- age/recency;
- compatibility with current kernel/runtime generations;
- deterministic Sandbox/regression-test evidence;
- physical-device verification.

Do not erase bad outcomes merely because a fix is no longer recommended. Negative evidence prevents repeated mistakes.

Possible states:

- experimental;
- community-reported;
- repeatedly successful;
- high-confidence for matching profile;
- maintainer-reviewed;
- deprecated;
- regression-suspected;
- quarantined/unsafe;
- obsolete for current versions.

## Community repair lifecycle

Example:

1. Doctor finds an unofficial community driver/fix.
2. Source is clearly labeled lower-trust/unofficial.
3. Owner chooses to proceed after seeing relevant risk and rollback state.
4. Beast snapshots/backs up relevant state.
5. Transaction installs/applies the candidate fix.
6. Doctor verifies the real outcome, not merely process success.
7. Cleanup removes staging/debris.
8. If opted in, Doctor contributes a sanitized structured result to the Global Doctor network.
9. Additional independent successful/failing cases update empirical confidence.
10. Future Doctors use the aggregate evidence as one input, never as permission to bypass local compatibility/authority checks.

## Global search integration

Doctor/Search should be able to query the collective database alongside:

- local patient history;
- previous local Doctor cases;
- offline docs/manuals;
- official documentation;
- GitHub/project issues;
- broader web/community sources when allowed.

A global Doctor result is **structured empirical evidence**, not equivalent to an official source.

## Home Base integration

Home Base may become a preferred synchronization context for Doctor knowledge.

Policy-controlled jobs may include:

- upload newly resolved sanitized cases;
- upload later success/failure/recurrence outcomes;
- pull knowledge updates relevant to this hardware/software inventory;
- pre-cache likely fixes/Procedures for installed hardware;
- update official/offline documentation;
- download high-value diagnostic resources;
- receive advisories for configurations matching newly discovered regressions.

This does not require downloading the entire global database. The service can return deltas / relevant subsets based on the local Device Passport and installed components.

## Doctor presentation opportunity

Doctor may expose collective evidence visually:

> `FOUND 43 SIMILAR CASES`  
> `31 CLOSE MATCHES`  
> `28 VERIFIED FIXES`  
> `3 FAILURES — DIFFERENT DRIVER REVISION`

Technical detail can show exact comparison dimensions, case provenance and source tiers.

## Global infrastructure relationship

Existing Global profile sync already demonstrates useful patterns: opt-in policy, pseudonymous public ID, privacy sanitization, content hashing and queued future connector behavior.

Doctor collective knowledge should reuse those architectural lessons but remain a **separate schema/data stream** from public creature/profile publishing.

No creature-profile publication should be required to contribute/consume Doctor knowledge.

## Principle

> **The fleet learns, but each Doctor still treats its own patient.**

Global evidence improves diagnosis. The local Doctor remains responsible for checking the current machine, presenting risk, obtaining required authority, applying through Transactions/Procedures, and verifying the result.
