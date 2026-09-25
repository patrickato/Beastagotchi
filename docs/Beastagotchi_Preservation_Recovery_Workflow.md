# Beastagotchi Preservation & Recovery Workflow

**Status:** required continuity process for long-running development.

Beastagotchi is expected to span many conversations, releases, physical tests and
development sessions. No single chat, memory summary, Library file or Git branch
is sufficient by itself. Preservation therefore uses several independent layers.

## Layer 1 — Original ChatGPT conversations

Keep Beastagotchi development chats saved. Do not delete a historical development
chat merely because it is superseded.

When practical, keep Beastagotchi chats inside one ChatGPT Project so future
project chats can use the earlier chats/files as project context.

Pinned versus archived is organizational only; neither substitutes for a backup.

## Layer 2 — ChatGPT Project context

The preferred working organization is one Beastagotchi/Monstergotchi Project
containing the long-running development chats and relevant reference files.

Project context improves continuity but is **not** treated as a guaranteed
word-for-word transcript retrieval API. Important decisions still move into the
repository.

## Layer 3 — Private Library preservation

Private/recovered conversation material, account-export extracts and other
material inappropriate for the public repository belong in the user's private
Library preservation area.

As of 2026-09-23 a private preservation bundle was created containing currently
recoverable conversation-style records, the recovery review, checksums and
historical checkpoint evidence.

Do not copy private raw transcripts, credentials, captures, exact location
history or unrelated personal content into this public repository.

## Layer 4 — GitHub engineering source of truth

The repository preserves sanitized durable engineering truth:

- source code and tests;
- current completion matrix;
- continuity ledger;
- active checkpoint;
- architecture/specifications;
- validation reports;
- release/install/rollback instructions;
- issues and PR history;
- explicit supersession notes.

Current development follows:

`main` stable baseline → milestone branch → CI/source gate → target/off-screen
validation where applicable → physical validation where required → promotion.

Historical artifacts are not silently rewritten. A later document explicitly
supersedes an earlier one.

## Layer 5 — Frozen Git preservation points

At major recovery or milestone boundaries, create a named preservation branch or
equivalent immutable Git reference so the exact repository state remains easy to
locate even after active development moves forward.

2026-09-23 preservation reference:

- branch: `preservation-2026-09-23`
- source checkpoint lineage: v0.19 Unified Experience
- current preservation pass began from green head
  `e5134012af7ff33f4646441ad535401296abd119`

The branch may be advanced only during the same preservation pass; after the pass
is declared complete it should be treated as frozen evidence.

## Layer 6 — Literal ChatGPT account data export

Cross-chat retrieval can be selective. For literal account-level chat-history
backup, periodically request ChatGPT's data export and store the downloaded ZIP
securely outside the live conversation.

When an export is available, preserve the original export unchanged. Then extract
the Beastagotchi conversations into separate reviewable files while retaining
the original export as provenance.

An imported/exported transcript may be used to improve recovery, but should not
silently overwrite repository engineering status. Reconcile it against current
code, tests and later physical decisions.

## Recurring checkpoint rule

During active Beastagotchi development:

1. At substantial implementation milestones, update the repository checkpoint,
   completion matrix and any affected specification.
2. At least daily during active work, create a preservation checkpoint of new
   durable project state when tooling permits.
3. Periodically request/download a full ChatGPT account export for literal
   transcript retention.
4. Before a conversation becomes too large or a new Beastagotchi chat is started,
   make sure current durable state exists outside that chat.
5. If a future assistant cannot read a historical chat completely, recover from:
   repository → Library preservation → exported transcript → historical artifacts,
   rather than guessing.

## Evidence levels remain separate

Never collapse these into one status:

1. source/CI validation;
2. clean-package validation;
3. target/off-screen Pi validation;
4. physical display/touch/runtime validation;
5. long-duration operational acceptance.

A file existing in GitHub is not physical sign-off. A physically rejected
calibration or UI choice remains rejected even if an older report described it as
numerically attractive.

## Current non-negotiable preservation rule

A useful project decision must not exist **only** in conversation.

It must become one or more of:

- implementation;
- test;
- specification;
- completion-matrix entry;
- continuity-ledger entry;
- active checkpoint;
- validation report;
- issue/PR;
- private preservation artifact.

This is the long-term defense against chat truncation, memory drift, accidental
scope loss and handoff failure.
