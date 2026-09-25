# Beastagotchi v0.19 — Cross-Page Experience Fidelity Pass
## 2026-09-25

Branch: `v0.19-unified-experience`

Status: **cross-page visual-language consistency improved; owner acceptance and physical TFT
acceptance remain pending.**

## Purpose

After the Home fidelity pass, the existing cross-page proof revealed that several second pages
still fell back to the older card/module language. This pass translated those pages into the
same Experience-specific visual grammar as their Home surface.

## Retained changes

### Atlas Recon

- removed the large rounded survey card and three rounded sidebar cards;
- same full field canvas + ruled notebook margin as Atlas Home;
- relative RF diagram remains explicitly non-geographic/non-range;
- survey/band/position facts are edge annotations;
- full-width field-session ledger preserves context.

### Forge System

- removed four rounded system modules;
- one service chassis with shared rails/bus;
- compute gauge/memory bus, I/O ports/radio fabric, exposed power train and mounted
  Doctor/Governor stack;
- same material/operational language as Forge Home.

### Observatory Spectrum

- removed boxed main plot, boxed measurement column and boxed summary;
- open scientific axes and integrated lower observation readout;
- ruled measurement margin matches Observatory Home;
- no invented time-series or history.

### Habitat Beast

- replaced the old circle/dot-eye focal creature with the same layered organic facial language
  used by Habitat Home;
- growth path and real memory/capture counters remain spatial/environmental objects.

### Monolith Overview

No structural rewrite was required in this pass. It already preserved Monolith's negative-space,
one-primary-statement and sparse-fact grammar.

## Exact evidence

Cumulative code head:

`4328ebab8096532adac2ce8e62997cd4dad6e051`

CI: green.

Artifact:
- `v019-experience-page-translations`
- digest: `sha256:3a96130c1f76415e01595418d9e8d07063ffd19c145203fc3e1eb37256b16d40`

This remains implementation evidence, not owner acceptance.

## Next visual layer

With Home and first translation pages now structurally coherent, the next fidelity layer is
bounded ambient motion/choreography:

- never mutate canonical telemetry for animation;
- never animate measured graphs as if new observations occurred;
- creature/environment breathing/blink/light motion may be decorative/ambient;
- motion must be SceneRuntime-labelled as ambient/decorative where appropriate;
- generate deterministic multi-frame evidence before any TFT staging.

Gate 1 remains active.
