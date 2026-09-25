# Beastagotchi v0.19 Experience-DNA Diversification Checkpoint
## 2026-09-24

Branch: `v0.19-unified-experience`

Gate 1 remains active. This checkpoint records the architectural correction away from over-reliance on the old named-theme cluster.

## Core correction

Classic, Cyberpunk, Black Ice, WOPR/NORAD, LCARS, Hunter, Matrix, Retro CRT, Synthwave, Starcore and similar identities remain valid presets/references, but they are no longer treated as the primary product taxonomy.

Beastagotchi now models Experience intent through `beastcore/experience_dna.py`.

## Implemented

- 16 broad built-in visual families;
- independent layout, density, motion, creature-presence, utility, playfulness, alert, input, Doctor-visibility and mystery axes;
- namespaced Pack/community presentation extensions;
- built-in Experience DNA for Atlas, Forge, Observatory, Habitat, Monolith, Dossier, Stillwater and Bench;
- explicit `LEGACY_REFERENCE_IDENTITIES` set;
- adaptive constrained/compact/full/enhanced variants using PlatformProfile compute/display classes;
- context-sensitive Doctor visibility without replacing Experience identity;
- Beast Studio schema exposure for Experience families/DNA;
- tests protecting breadth, adaptive identity preservation and namespaced extension behavior;
- first five prototype briefs defining composition/data hierarchy/motion/Doctor behavior;
- grayscale structural silhouette proofs for Atlas, Forge, Observatory, Habitat and Monolith;
- tests ensuring those silhouettes are not identical dashboard clones;
- CI artifact generation for the silhouette proof set;
- roadmap, Theme Studio, Experience spec, collaborator handoff and Gate 1 updated to the new direction.

## First prototype order

1. Atlas — Expedition / map-first
2. Forge — Industrial / cockpit-cluster
3. Observatory — Scientific / split-console
4. Habitat — Companion / creature-first
5. Monolith — Premium / immersive-HUD

These five must differ in grayscale silhouette, primary content hierarchy, creature presence, motion language and Doctor relationship before palette is considered.

## Permanent anti-loop rule

A new Experience is not meaningfully new when it mainly changes color, reuses the same dominant widget geometry, keeps the creature in the same box, or overlays Doctor identically.

Choice/variety should come from stable semantic composition axes, not an ever-growing pile of hard-coded skins.

## Next implementation block

- inspect CI-generated structural silhouette artifact;
- begin actual Atlas Home Scene prototype from the brief, without inheriting legacy grid/scanline/neon assumptions;
- follow with Forge and Observatory before deciding whether the composition model is diverse enough;
- keep Habitat and Monolith as deliberate counterexamples to instrument-heavy design;
- do not stage on physical TFT until off-screen visual direction is accepted.