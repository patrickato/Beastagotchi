# Beastagotchi Theme Studio — v0.10.0

Theme Studio is a schema-driven customization surface. Its long-term rule is that themes control much more than palette: background/texture/animation, panel geometry, typography, icons, face treatment, graph defaults, transitions, navigation, density, reactions and ambient effects.

## Interaction model

Theme Library uses large paged cards suitable for the 480×320 resistive display. A theme opens a full-screen detail editor. Changes preview live and become persistent only after APPLY; CANCEL returns to the previously applied theme/options.

Physical controls must obey the production touch policy: large non-overlapping hit regions, with visual bounds permitted to be smaller than touch bounds.

## Matrix

Matrix remains the most mature theme schema and serves as an advanced effect-system reference, not the only customization target.

- Layer: Background / Mixed / Foreground
- Density: Sparse / Light / Normal / Dense / Heavy / Storm / Deluge
- Speed: Drift / Slow / Normal / Fast / Fury / Torrent
- Trail: Short / Normal / Long / Extreme
- Glyphs: Mixed / Digits / Binary / Hex / Symbols
- Palette: Green / Cyan / Violet / Red / Amber / Rainbow / Holiday / Custom
- Accents: Off / Sparse / Medium / Heavy / Balanced
- Foreground share: 0–50%
- Custom slots: Primary / Secondary / Tertiary / Quaternary
- Reactions: On / Off

Single-color mode is strict: a preset with Accents=Off must not invent a secondary color.

## Native Chroma

Native Chroma uses the actual live Jayofelony frame as the authoritative Pwnagotchi face/layout source.

- Ink source: Mood / Fixed
- Fixed palette: Green / Cyan / Amber / Violet / Red / White / Rainbow
- Glow: Off / Soft / Strong
- Effect: Clean / Scanlines / Vignette / Grain / Pulse / Glitch / Halo

Beast may transform presentation, but does not reconstruct the Native Pwnagotchi face/actions.

## Classic Beast — v0.10 breadth controls

- Grid: Off / Light / Normal / Dense
- Scanline: On / Off
- Pulse: Off / Subtle / Active

The goal is to let Classic range from the original clean neon instrument panel to a busier animated HUD without requiring a separate hard-coded theme.

## Starcore — v0.10 breadth controls

- Stars: Sparse / Normal / Dense / Nebula
- Twinkle: Off / Low / Normal / High
- Orbit: On / Off

These settings alter field density, star brightness cadence and orbital/accent geometry while keeping Starcore readable.

## Black Ice — v0.10 breadth controls

- Frost: Light / Normal / Heavy / Whiteout
- Drift: Still / Slow / Normal / Fast
- Crystals: Off / Subtle / Active

Background frost and foreground crystals are separate effect layers.

## Hunter — v0.10 breadth controls

- Grid: Off / Light / Normal / Dense
- Reticle: On / Off
- Embers: Off / Sparse / Normal / Heavy

Hunter's tactical geometry and foreground ember pass are independently controllable.

## Minimal Field — v0.10 breadth controls

- Ambient: Off / Soft
- Panels: Soft / Normal

Minimal deliberately preserves a low-noise presentation. Its options should not turn it into another dense theme.

## Visualizers and themes

Theme and visualization are separate axes. A page's data renderer can be changed without switching its theme. The renderer library currently includes line, area, multi-line, bars, stacked bars, histogram, heatmap, waterfall, waveform, radial, donut, radar, polar, signal meter, timeline and numeric+microtrend primitives.

Future Theme Studio work will add theme-specific graph skins so the same data renderer can look genuinely native to Starcore, Black Ice, Hunter, etc., rather than merely changing colors.

## Reserved customization growth

- arbitrary color picker/sliders in the companion/web editor;
- Primary/Secondary/Tertiary/Quaternary weights;
- animation intensity and resource profile;
- face packs/accessories where compatible;
- seasonal overlays and event-reaction intensity;
- per-theme default graph/renderers;
- widget/layout presets;
- save-as-variant / favorites / tags;
- import/export/shareable community theme packages.

---

## v0.19 architecture note — Theme is no longer the top-level identity

Theme Studio remains a valid low-level visual editor, but Beastagotchi now treats Theme as one component inside a broader Experience.

The product must not keep expanding by adding only more hard-coded named themes.

Experience DNA may select or generate very different combinations of Scene/Layout, Theme, creature presence, density, motion, Doctor visibility, mission bias and target-display behavior.

The former flagship themes remain useful presets and compatibility references, but new visual development should preferentially prove new Experience families such as Expedition, Scientific, Industrial, Companion, Premium, Archive, Ecological, Nautical, Aviation, Analog, Educational and Calm.

A new Experience is not considered meaningfully distinct when it merely recolors the same geometry.