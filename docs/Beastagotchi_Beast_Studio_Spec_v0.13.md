# Beastagotchi Beast Studio Specification v0.13

Beast Studio is the end-user authoring/control surface for Beastagotchi. Its quality target is a clean, uncluttered editor with immediate feedback, while extending far beyond a traditional theme manager.

## Current production foundation
- paired-token web UI;
- exact 480x320 preview rendered by the real Beast UI compositor with current Core telemetry;
- theme/page selection and structural theme controls;
- renderer selection;
- six-slot Live Dashboard data binding with labels/renderers;
- Undo / Redo / Reset / atomic Apply and rolling preference backups;
- Plugin integration view with enabled/integration/protection state;
- privileged plugin toggles through a local allow-listed action broker with snapshot/verification/rollback.

## Architecture
`Live Data -> Widget -> Renderer -> Skin -> Layout -> Theme -> Animation -> Compositor`

Studio edits declarative preferences/configuration wherever possible. Normal visual customization must not require editing Python.

## Planned layers
1. Appearance: themes, palettes, typography, panel geometry, backgrounds/effects.
2. Layout: create pages, move/resize/show/hide, z-order, density and responsive rules.
3. Widgets: select canonical data, renderer, history window, smoothing, units, thresholds and labels.
4. Beast: faces, animation/personality packs, reactions and progression presentation.
5. Plugins: install/stage/enable/configure/health/adapters.
6. Hardware: roles, status, rules and hardware-specific presentation.
7. Audio/haptics/lighting: event mappings and profiles.
8. Context Decks: Field/Home/Docked/Radio/SDR/custom navigation and layouts.
9. Rules: safe structured trigger -> condition -> action automation.
10. Packages: save variants, import/export, community packs, rollback/version history.

The physical TFT should remain clean; Studio is where deep authoring can use a larger phone/desktop canvas.
