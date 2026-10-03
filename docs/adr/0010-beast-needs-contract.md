# ADR 0010 — The Beast's needs are a live, honest `needs.*` contract

**Status:** Proposed

**Implementation:** partial — `NeedsEngine` and the `needs.*` namespace land with the needs-system PR; cross-restart persistence and the needs→mood rewrite (which closes finding F1) are planned follow-ups.

Finding F1 showed the Beast's mood is effectively stuck on one or two states because it is an if-chain over a few instantaneous signals. Creature idea 1 replaces that with **needs**: a small set of drives that build up over hours and are eased by real events, so the Beast visibly *wants* things and two Beasts diverge over time. This ADR makes the needs a first-class, honest contract before anything consumes them.

`beastcore/needs.py` (`NeedsEngine`) publishes, under the **`needs.*`** namespace, four needs plus a source tag:

- `needs.curiosity_hunger` — rises since the last **lifetime-first** discovery (new AP/vendor); eased only by genuine novelty, so re-seeing the same networks cannot fake it.
- `needs.restlessness` — rises since real **GPS movement**; **unavailable** without a GPS fix (we cannot know movement, so we do not invent it).
- `needs.loneliness` — rises since the last **peer encounter** (PeerDex `last_seen_at`).
- `needs.tiredness` — integrates **heat / throttling / low battery / night**, and recovers when conditions are good. Neglect makes a Beast sleepy, never damaged.
- `needs.source` — provenance tag (`derived_live`).

The contract:

- **Type / range:** each need is an integer `0..100`, or **unavailable** (ADR-0008) when its driving signal is not present — never a fabricated number. (This is the same honesty rule applied to temperament in ADR-0009.)
- **Source:** derived live from canonical state the collectors already publish (`wifi.encounters.*`, `gps.*`, `peerdex.*`, `system.*`, `power.*`, `ambient.*`); the engine never changes Pwnagotchi behaviour.
- **Temperament modulation (idea 2):** heritage axes shift the rates — `curiosity` → how fast curiosity-hunger rises; `social` → how fast loneliness rises; `nocturnal` → night sleepiness; `boldness` → how much heat tires the Beast. Two Beasts in the same room then differ at no runtime cost.
- **Persistence:** needs are **session-live** in this first step (they start easing from boot). Cross-restart persistence — surviving restarts but fading gently while powered off (idea 1) — is a planned follow-up and does not change the key contract.
- **Consumption:** nothing rewires mood from needs **yet**. The needs→mood rewrite with hysteresis and expression cooldowns (which fixes F1) is a separate follow-up, so this step is additive and non-behavioural.

Rationale: needs are how the Beast becomes a creature that *wants, remembers and differs* rather than a readout — the north star (expose the real depth the platform computes, made engaging and shown truthfully). Publishing them honestly (unavailable, not faked) from the start keeps the creature layer credible.

Scope note: `needs.*` is a new **Core** state namespace (like `progression.*` or `context.*`), not the `beast.*` expression vocabulary, so it is Claude-lane creature truth rather than the joint seam. It is **Proposed** pending Patrick's acceptance; `NeedsEngine` is Core (Claude owns), reviewed by OpenAI.

Alternatives considered:

- _Keep the instantaneous mood if-chain and just add signals._ Rejected: F1 showed that does not produce variety; drives that accumulate over time do.
- _Fabricate a neutral value when a signal is missing (e.g. restlessness with no GPS)._ Rejected: that is exactly the ADR-0008 violation the temperament review (ADR-0009) corrected; absent signals are reported unavailable.

Cross-references:

- Live-data honesty / unavailable-not-faked: ADR-0008; temperament precedent ADR-0009.
- Canonical state contract: ADR-0002.
- Finding F1 and ideas 1+2: `collaboration/claude/BEASTAGOTCHI_CREATURE_IDEAS_AND_FINDINGS_2026-09-26.md`.
- Implementation: `beastcore/needs.py`, `beastcore/core.py` (`_personality_loop`); tests `tests/test_v019_needs_engine.py`.
