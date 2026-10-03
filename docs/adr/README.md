# Architecture Decision Records

ADRs capture decisions that would be costly to rediscover or accidentally reverse later. They complement the larger Design Bible/specifications.

## Status vocabulary

An ADR's **Status** records the state of the *decision*, not how far it is built:

- **Proposed** — put forward (e.g. an open ADR PR); not yet accepted by Patrick.
- **Accepted** — the decision stands. Patrick accepts or rejects ADRs (`AGENTS.md` §3).
- **Superseded** — replaced by a later ADR; the Status links to it.
- **Deprecated** — withdrawn without a direct replacement.

Implementation progress lives in the Completion Matrix, not here. An ADR may carry an optional **Implementation:** line (`in progress` / `partial` / `complete`) that points there — but an unfinished implementation never turns an accepted decision back into "planned".

## Rules map (where each rule lives)

Beastagotchi's rules intentionally live in three places for three audiences: **ADRs** (the decision + rationale), the **`AGENTS.md` golden rules** (the agent quick-reference), and the **Design Bible §1 principles** (the product identity). This table is the single index — each rule has one canonical home (its ADR, where one exists) and the others cross-reference it.

| Rule | ADR | Golden rule | Bible principle |
|---|---|---|---|
| Protect the Pwnagotchi engine | 0001 | §2.1 | #1 |
| Canonical state flows through Beast Core | 0002 | — | §33 |
| Exactly one physical presentation owner | 0003 | §4 (hard limit) | — |
| TFT is the cockpit; WebUI is the workshop | 0004 | §2.5 | — |
| Optional growth uses Beast Packs | 0005 | — | #9, #10 |
| Recovery evidence persists locally | 0006 | — | — |
| No silent scope loss | 0007 | §2.2 | #12 |
| Live data, never decorative fiction | 0008 | §2.4 | #3, #13 |
| Layer separation (UI / theme / layout / renderer / face) | — | — | #4–#7, §33 |
| Visual richness degrades gracefully | — | — | #8 |
| Offline exchange is first-class | — | — | #11 |

Rules without an ADR live in the Bible as their canonical home. Promote one to an ADR when it becomes a decision that would be costly to reverse.

## The ADRs

- 0001 — Protect the Pwnagotchi engine
- 0002 — Canonical state flows through Beast Core
- 0003 — Exactly one physical presentation owner
- 0004 — TFT is the cockpit; WebUI is the workshop
- 0005 — Optional growth uses Beast Packs
- 0006 — Recovery evidence persists locally
- 0007 — No silent scope loss
- 0008 — Live data, never decorative fiction
