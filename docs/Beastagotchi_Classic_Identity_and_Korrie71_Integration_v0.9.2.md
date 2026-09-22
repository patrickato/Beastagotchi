# Beastagotchi Classic Identity + Korrie71 Theme-Manager Integration — v0.9.2

## Identity rule
Beastagotchi permanently retains the original Pwnagotchi text-face language as a first-class option.

Core themes:
- **Pwnagotchi Dark** — black background, white stock-style text face.
- **Pwnagotchi Light** — white background, black stock-style text face.
- **Pwnagotchi Chroma** — stock-style Pwnagotchi text face with mood-reactive colors and Beast visual treatment.

Richer Beast character packs do not replace these. Both systems coexist.

## Korrie71 reference
Reference repository: `https://github.com/Korrie71/pwnagotchi-theme-manager`

That project is specifically aimed at the same 3.5-inch 480x320 framebuffer/Jayofelony environment and demonstrates a useful design vocabulary: colors and gradients, layered effects, per-element colors, mood-reactive styling, optional face packs, live preview/editor controls, touch theme/plugin management, and shareable JSON theme manifests.

Beastagotchi does **not** install the Korrie71 plugin as a runtime dependency because Beast owns the framebuffer and already has its own compositor, state model, touch stack and Theme Studio. Instead, Beast adopts compatible ideas natively:

- preserve original Pwnagotchi text faces
- per-mood face/color overrides
- per-element customization
- effect stacks and background/foreground layers
- live theme preview and edit/apply workflow
- small shareable theme manifests
- future import/translation adapter where practical

Per project direction, round/blob face packs are excluded from the built-in classic family. Optional image packs may still be supported as community content later.

## Public-release attribution
Korrie71's repository declares GPL-3.0. This integration is independently implemented from the documented behavior/design concepts rather than by copying its source. If source or assets are imported later, preserve upstream licensing and attribution in the public repository.
