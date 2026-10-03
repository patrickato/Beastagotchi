# ADR 0008 — Live data, never decorative fiction

**Status:** Accepted

Production views show real, live, or persisted data, or an explicit *unavailable*. Beastagotchi never fabricates telemetry: a value the device cannot currently determine is shown as unknown/unavailable, and unknown is never rendered as zero or a plausible-looking placeholder. Demo or replay data may exist only when it is clearly labelled as demo/replay.

Rationale: Beastagotchi is a field computer built around a real Pwnagotchi/Pi. Its credibility — and its usefulness — come from exposing the real machine and the real world, not from a screen that merely looks busy. A monitoring device that fakes a reading is worse than one that admits it does not know.

Cross-references:
- Engineering golden rule: `AGENTS.md` §2.4.
- Product principles: Design & Architecture Bible §1 — principle #3 (live data first) and principle #13 (live truth).
