# Beastagotchi v0.9.5 — Focused Physical Follow-up

## Why this build exists

The v0.9.4 validation archive and physical notes were enough to identify the temporary pink/magenta diagonal lines. They were not Matrix-rain columns: the saved framebuffer showed ordinary vertical green rain, while the event history recorded a thermal transition into `critical` at 80.34 C. Matrix's severe-event reaction used the danger color and moved its small bars in X and Y together, which visually formed a short-lived diagonal sweep.

## Gate 1 — Matrix event reaction

- Normal rain remains vertical.
- Event-reaction bars now use fixed X coordinates and animate only in height/intensity.
- Severe thermal/fault reactions use stationary danger corner brackets.
- Theme Studio exposes `REACTIONS = ON/OFF` so event visuals can be isolated or disabled by the user.
- The one protected horizontal scanline remains independent.

## Gate 2 — Matrix customization

Physically verify only the pieces not checked in v0.9.4:

- `GREEN + ACCENTS OFF` is green only;
- Custom Primary alone works;
- Secondary/Tertiary/Quaternary can be added independently;
- Sparse/Drift/Short and Deluge/Torrent/Extreme look clearly different;
- Background/Mixed/Foreground visibly change layering.

## Gate 3 — Achievement touch ergonomics

Achievement Explorer no longer relies on expanded hitboxes that can overlap adjacent rows. The screen is partitioned into non-overlapping touch zones for tabs, filter/sort, two cards, and bottom navigation.

Acceptance: ordinary finger taps should change the intended control on the first or second natural attempt without careful stylus-like aiming.

## Already passed / no need to repeat

- Native Pwnagotchi RAW bridge;
- restored/original touch calibration;
- Rare Moment presentation mechanics;
- stock Pwnagotchi frame source;
- basic swipe/page navigation.

The final Rare Moment art-quality target remains much higher than the procedural mechanics previews.
