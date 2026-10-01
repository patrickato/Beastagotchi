# Beastagotchi Doctor Knowledge / Learning Jam

**Date:** 2026-09-26  
**Status:** active design jam / candidate direction; not final implementation canon

## Goal

Doctor should be able to use a very broad body of knowledge without confusing discovery with truth or automatically applying unverified Internet folklore.

Core distinction:

> **Finding a possible answer is not the same as proving that answer applies to this Beast.**

Doctor combines patient-specific evidence with reusable knowledge, then validates applicability before proposing or executing a repair.

---

# 1. Knowledge sources

Potential knowledge sources include:

## Patient-local truth
- current State/Signals/Events;
- Device Passport / Machine Census;
- file/config/package/runtime state;
- System Graph;
- Known-Good / What Changed?;
- Incidents / previous Doctor cases;
- Action/Transaction/Procedure history;
- owner customizations and override ledger.

## Built-in / offline curated knowledge
- Beastagotchi docs;
- Pwnagotchi/Jayofelony docs cached locally;
- Bettercap docs;
- Raspberry Pi docs;
- Linux man pages/reference material;
- plugin/package READMEs;
- hardware manuals/datasheets;
- known compatibility tables;
- prewritten Probe Blocks / diagnostic signatures;
- owner-added docs/notes;
- Field Library / offline wiki/manual collections.

## Online/current sources when allowed/available
- official project/vendor documentation;
- official package/release metadata;
- GitHub repositories/releases/issues/discussions;
- project/community forums;
- other owner-selected trusted sources;
- broader web Search for discovery.

## External analyst assistance
- Claude or another AI collaborator during project development;
- optional future runtime AI only if later approved.

AI/model output is advisory evidence, not canonical truth or authority.

---

# 2. Source/evidence ranking

Candidate ranking dimensions rather than one simplistic trust number:

- source authority;
- applicability to exact hardware/OS/kernel/software version;
- recency/version compatibility;
- reproducibility;
- whether it conflicts with current patient evidence;
- whether owner customization changes applicability;
- whether the remedy has succeeded/failed previously on this patient;
- mutation/risk level;
- rollback availability.

A current official driver guide that matches the exact chipset/kernel may rank above an old forum workaround. A prior successful repair on the same patient may be powerful evidence, but should still be invalidated if the environment changed materially.

---

# 3. Knowledge should be structured around questions and applicability

Doctor should not merely ingest text blobs.

Useful normalized knowledge record / remedy metadata may include:
- problem/symptom signature;
- affected capability/component;
- required/contradicting evidence;
- applicable hardware IDs/models;
- applicable OS/kernel/package/Pwnagotchi/Beast versions;
- known incompatible versions;
- required dependencies/resources;
- diagnostic probes;
- proposed repair steps;
- mutation/risk class;
- verification test;
- rollback/recovery method;
- original source/provenance/date;
- local success/failure history;
- confidence/applicability status.

Do not expose this as another mandatory user-facing database; Doctor/Search/Studio can consume it.

---

# 4. Internet/community fixes become candidates, not commands

Example:

Doctor finds three suggested fixes for an RTL-SDR or TFT problem.

Instead of executing one blindly, Doctor should ask internally:

1. Does this fix target the same hardware/device ID?
2. Same architecture?
3. Same kernel/API generation?
4. Same Pwnagotchi/Beast version?
5. Does current patient evidence support the stated failure mechanism?
6. Does the remedy conflict with owner customizations?
7. Can it be rehearsed/validated safely?
8. Can it be rolled back?
9. What functional test proves it actually fixed the problem?

Only then can the advice be translated into a bounded Procedure/repair plan.

---

# 5. Learning from solved cases

When Doctor resolves an incident, preserve useful structured outcome information:

- symptom/signature;
- root cause if confirmed;
- probes that were decisive;
- failed hypotheses;
- repair/Procedure/Transaction used;
- exact patient version/context;
- verification evidence;
- recurrence count;
- whether later upgrades invalidate the old remedy.

Future recurrence may then truthfully say:

> "This pattern occurred before. The previous repair succeeded under a materially similar configuration."

Do not let one successful fix become universal folklore; retain applicability constraints.

---

# 6. Home Base knowledge maintenance

Home Base can be a good time for optional/owner-policy-governed knowledge work:

- refresh official docs/release metadata;
- obtain queued manuals/datasheets;
- update offline indexes/search corpus;
- fetch requested plugin/project docs;
- refresh compatibility metadata;
- acquire queued diagnostic resources;
- prune expired/reacquirable cache;
- verify important retained resources.

This is background maintenance, not automatic mutation of the live system unless separately approved.

---

# 7. Search and Doctor share knowledge infrastructure

Do not build a separate Internet search stack exclusively for Doctor.

The broader federated Search/Knowledge substrate should serve:
- owner Search;
- Doctor;
- Guided Software tutorials;
- Studio/developer help;
- Field Library;
- future optional AI.

Doctor adds patient context, diagnostic reasoning, repair authority and verification on top of shared retrieval.

---

# 8. Claude as development collaborator

Claude remains available as a project-development second brain.

Useful roles during Doctor buildout:
- independently review Probe Blocks;
- research vendor/project documentation;
- propose diagnostic trees;
- adversarially test repair logic;
- compare alternate remedies;
- generate test cases;
- review Procedure safety/rollback completeness;
- work on a separate branch for later human/assistant review.

Claude output should always be reconciled against repository contracts, tests and authoritative sources.

---

# 9. Owner-facing explanation

Doctor should be able to explain *why* it believes a repair is appropriate without drowning beginners.

Possible levels:

## Simple
> "Your display driver is missing after the kernel update. I found the matching supported driver and can repair it."

## Explain
> Show decisive evidence, source and what will change.

## Technical
> Full hypotheses, probes, source links/metadata, version applicability, Procedure plan, diffs and Transaction details.

This aligns with the broader Guided Software principle: approachable by default, full depth always available.

---

# 10. Live status integration

Knowledge lookup/diagnosis should emit live truthful operation status, e.g.:

> Comparing patient state...
> Searching local knowledge...
> Checking official project docs...
> 3 candidate remedies found.
> Eliminating 2 incompatible with kernel 6.x...
> Verifying remaining repair plan...

Do not fabricate percentages when discovery work is indeterminate.

See `docs/Beastagotchi_Live_Operation_Status_2026-09-26.md`.

---

# 11. Open questions for continued jam

- How much online searching may Doctor perform automatically vs only when asked?
- Which source classes may be auto-trusted for acquisition vs only used as information?
- Should owner be able to pin/ban/prefer sources?
- How should old remedies expire when kernel/Pwnagotchi/Beast versions change?
- Should community-submitted Doctor knowledge ever become a Pack/catalog type?
- How much solved-case detail should be retained by default?
- How aggressively should Doctor use Sandbox/replay to validate novel fixes when development infrastructure is available?
