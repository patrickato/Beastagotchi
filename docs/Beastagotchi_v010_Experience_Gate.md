# Beastagotchi v0.10.0 — Visualization & Theme-Breadth Gate

v0.10.0 intentionally pivots away from Matrix-only iteration after the v0.9.5 physical pass. The goal is to prove that the architecture expands across the entire product rather than accumulating one highly-polished theme.

## Physical checks

1. Control Center exposes a large-target **Visualizer Studio** entry.
2. Visualizer Studio can change Recon, Spectrum, Captures and System renderers with large left/right controls.
3. Direct graph tapping still cycles the appropriate renderer without stealing footer taps.
4. Spectrum modes are visibly distinct, especially Bars / Donut / Waterfall / Waveform.
5. System modes are visibly distinct, especially Line / Area / Histogram.
6. Classic Theme Studio exposes Grid / Scanline / Ambient Pulse.
7. Starcore exposes Stars / Twinkle / Orbit Arc.
8. Black Ice exposes Frost / Drift / Crystals.
9. Hunter exposes Grid / Reticle / Embers.
10. Minimal exposes Ambient / Panels.
11. Native Pwnagotchi remains intact.
12. Matrix remains available but is no longer the primary development target for this gate.

## Touch rule

Footer zones always win over page graph hit zones. New visualizer controls use large explicit regions and do not depend on tiny labels.
