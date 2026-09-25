# Beastagotchi Visual Scene Architecture v0.1

Date: 2026-09-24

## Why this exists

The first v0.19 Unified Experience pass improved spacing, touch geometry and
information hierarchy, but it still treated most themes as palette/background
variants of one shared dashboard. That was a mismatch with the approved
Beastagotchi concept language, where WOPR, Cyberpunk, Classic, LCARS, Black Ice,
etc. are intentionally different *interfaces*, not recolors.

Physical TFT testing remains important, but this defect is visible off-screen and
does not require a real panel to prove. Gate 1 visual acceptance is therefore
re-opened before the physical session.

## Architectural rule

A Beastagotchi theme may control three separate layers:

1. **palette / atmosphere** — colors, background motion, scanline/glow behavior;
2. **scene composition** — the structural Home-page arrangement and information
   hierarchy;
3. **visual assets** — optional mascot/illustration/content art layered under
   truthful live state.

Themes are no longer assumed to be palette-only.

## home_scene

Theme.home_scene is a semantic scene identifier loaded from Theme JSON.

Built-in v0.19 scene families currently include:

- hero
- hero_cyber
- hero_ice
- hero_synth
- hero_tactical
- wopr
- lcars
- terminal

Unknown or absent scene identifiers fail closed to the previous page renderer.
This keeps old Theme Packs compatible while allowing newer packs to opt into
structural composition.

## Scene requirements

A scene must:

- consume canonical Beast state rather than create demo telemetry;
- keep unavailable values visibly unavailable;
- keep the validated global touch model intact unless a new physical touch gate
  proves a replacement;
- preserve page/swipe navigation;
- avoid decorative marks that can be mistaken for measured RF/GPS truth;
- remain renderable without optional visual assets;
- degrade to procedural artwork if an asset is missing or unreadable.

## Concept-derived visual assets

The first scene block includes three small project-owned portrait assets derived
from the Beastagotchi concept boards already created for this project:

- beastui/assets/home/classic_portrait.png
- beastui/assets/home/cyberpunk_portrait.png
- beastui/assets/home/blackice_portrait.png

These are not whole-screen screenshots. They are illustration layers embedded in
a live renderer. The surrounding status, metrics, navigation, theme motion,
scanline and state continue to be generated at runtime.

The renderer adds a subtle live luminance pulse and scan pass so the portrait
layer participates in the living UI rather than behaving as a dead wallpaper
panel.

## Current implementation

beastui/home_scenes.py now owns structural Home scenes.

The first scene conversion covers the current v0.19 gallery families:

- Classic
- Cyberpunk
- Black Ice
- Synthwave
- Hunter
- Amber Tactical
- Ghost Minimal
- WOPR / NORAD
- LCARS
- Retro CRT

Native Pwnagotchi presentation and existing dedicated minimal/starcore/matrix
paths remain separate.

The global header/footer renderer also now honors more of the theme's structural
identity instead of drawing the exact same rounded-button chrome everywhere.

## Next visual work

This milestone is not the end of visual reconstruction. The next blocks should
build on this scene contract rather than fall back to card-wall cleanup:

- Visual Asset Interop for Pack-owned portrait/background/icon sets;
- richer state-reactive mascot animation and expression layers;
- semantic render layers for alert/reaction/transport/rare/monster precedence;
- scene-specific iconography and typography;
- richer Capture/Map/Recon structures where concept references warrant them;
- physical TFT verification only after the off-screen composition again matches
  the intended Beastagotchi product language closely enough to justify it.

## Gate implication

The previously recorded READY FOR PHYSICAL CLOSE decision is superseded by the
owner's visual rejection of the actual generated v0.19 gallery. Source/package
preparation remains valid, but Gate 1 returns to **ACTIVE — VISUAL RECONSTRUCTION**
until the new renderer is accepted off-screen.
