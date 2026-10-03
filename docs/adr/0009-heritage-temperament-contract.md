# ADR 0009 — Heritage temperament is a canonical `beast.*` contract

**Status:** Accepted

**Implementation:** complete (landed with the finding-F5 PR #39, merged 2026-10-03).

Heritage already derives five temperament axes per Beast — `curiosity`, `social`, `focus`,
`boldness`, `nocturnal`, each an integer `0..100` (`beastcore/heritage.py`, `TEMPERAMENT_AXES`).
Until finding F5 these axes were published nowhere and read by nothing at runtime, so every Beast
produced identical `PersonalityEngine` output regardless of lineage. This ADR makes temperament a
first-class, live contract so a Beast's inherited nature actually shapes how it behaves.

Beast Core publishes, for the **active Beast only**, the canonical keys:

- `beast.temperament.curiosity`
- `beast.temperament.social`
- `beast.temperament.focus`
- `beast.temperament.boldness`
- `beast.temperament.nocturnal`

The contract:

- **Type / range:** integer `0..100`. `0` is a real value (the minimum), never a stand-in for
  "unknown".
- **Source:** the real stored identity via `heritage.normalize_parent_traits` — never invented
  (ADR-0008).
- **Unknown / absent:** when there is no active Beast, or its identity cannot be read, every axis
  is published as **neutral (50)**; a consumer that finds an axis absent also treats it as 50.
  Neutral reproduces the pre-F5 behaviour exactly, so Beasts without heritage data are unchanged.
- **No stale values:** when the active Beast changes (or becomes unreadable) the axes are
  re-published for the new Beast, or cleared to neutral; a previous Beast's temperament is never
  left showing as live (ADR-0008).
- **Consumption:** `PersonalityEngine` applies modest, bounded, clamped biases from four axes
  (`curiosity`, `focus`, `boldness`, `nocturnal`) to the expressed drive scalars (`beast.energy`,
  `beast.curiosity`, `beast.focus`, `beast.stress`). **Mood _selection_ is unchanged** —
  temperament colours the numbers, not which mood is chosen. `social` is reserved for the
  forthcoming needs / peer system.
- **Presentation** may read `beast.temperament.*` to flavour appearance, but — like all
  expression — must not re-derive mood from it (the creature boundary, `AGENTS.md` §7).

Rationale: temperament is how lineage and breeding become _felt_ rather than cosmetic — two Beasts
in identical conditions now diverge — which serves the north star (expose the real depth the
platform already computes, shown truthfully). Promoting it to a documented contract rather than an
ad-hoc key is required because it extends the `beast.*` vocabulary, a joint seam on which
presentation and the future needs system will depend.

Scope note: this is a governance / seam decision. Claude owns creature _truth_ (heritage,
personality) and proposes this contract; it touches the `beast.*` expression vocabulary, where
**OpenAI holds the pen and both agents review**, and **Patrick accepts ADRs** (`AGENTS.md` §3, §7).
It was **accepted by Patrick** via the #39 merge (2026-10-03) and its row is recorded in the ADR rules map. (OpenAI/Codex, the seam's pen-holder, requested this ADR during the #39 review and did not post a change to its content.)

Alternatives considered:

- _Pass temperament into `PersonalityEngine` by a side channel instead of state._ Rejected: the
  engine's contract is to derive expression from canonical state alone; a side channel is less
  legible and cannot be tested through the normal state path.
- _Publish under a non-`beast.*` namespace to avoid this ADR._ Rejected: temperament is Beast
  creature-truth and belongs in the `beast.*` vocabulary; sidestepping the review the vocabulary
  requires would be rules-lawyering, not honesty.

Cross-references:

- State contract: ADR-0002 (canonical state flows through Beast Core).
- Live-data honesty / no stale values: ADR-0008; `AGENTS.md` §2.4.
- Creature boundary and seam ownership: `AGENTS.md` §7 (lanes; creature boundary).
- Implementation: `beastcore/core.py` (`_sync_temperament`), `beastcore/personality.py`; tests
  `tests/test_v019_personality_temperament.py`, `tests/test_v019_core_temperament_sync.py`.
