# Beastagotchi Development & Release Workflow

## Why this exists

Beastagotchi needs both frequent engineering checkpoints and uncluttered public
releases. Those are different things.

## Branch model

- `main` is the stable/baseline branch.
- A named milestone branch carries active development, currently
  `v0.19-unified-experience`.
- Work is committed to the milestone branch in bounded, meaningful blocks.
- GitHub Actions/CI runs on those development commits.
- Failed experiments are corrected on the milestone branch; they do not become
  releases.

## What counts as an ordinary development commit

Examples:
- one coherent subsystem;
- a safety/compatibility contract;
- a test-backed UI component family;
- documentation synchronized with an implemented feature;
- a bug fix required to restore a green source gate.

These commits provide rollback points and make collaborative review possible.
They are not announcements that users should install a new version.

## What counts as a milestone publication

A milestone publication may update `main`, create a tag, GitHub Release or
downloadable Pi package only when the block is substantial and appropriately
validated.

Typical gate:

1. source tests green;
2. compile/syntax gates green;
3. off-screen render/validation gate green where applicable;
4. migration/install path reviewed;
5. target-hardware test performed when the change affects hardware, display,
   touch, services or performance materially;
6. roadmap/checkpoint/completion matrix updated;
7. known limitations documented.

## User visual-test cadence

Do not require a physical Pi install for every small change. Generate off-screen
renders/galleries between physical tests. Request a new physical visual test
when a substantial visible interaction/UX milestone exists, or when source-only
validation cannot answer a hardware question.

## GitHub Releases

Releases should be meaningful snapshots, not every development commit. Prefer:

- release archive/package;
- SHA-256 sidecar;
- install/upgrade/rollback instructions;
- validation status;
- screenshots or comparison gallery when visual behavior changed;
- known limitations.

## Collaboration

External reviewers can inspect the active PR/branch without forcing unfinished
work into `main`. Korrie71 or other collaborators can review code/docs/renders,
open issues or PRs, and use the Pack/compatibility contracts while the current
stable baseline remains intact.


## Continuity preservation gate

Before a long conversation/thread is abandoned or a major development context is
moved, synchronize durable project truth into the repository:

- current implementation/checkpoint document;
- current completion matrix;
- roadmap when execution order changed;
- continuity ledger when protected scope/architecture changed;
- validation report when new target/physical evidence exists;
- preservation snapshot when recovery from chat/Library history was required.

Private chat transcripts are not a release artifact. Preserve the engineering
decisions and evidence needed for continuity without publishing credentials,
captures, precise location history or unrelated personal material.
