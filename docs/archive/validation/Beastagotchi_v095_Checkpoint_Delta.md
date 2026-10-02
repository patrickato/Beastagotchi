# Beastagotchi v0.9.5 — Known-Good Pi Checkpoint Delta

## Baseline

The baseline is the user-supplied `beast-current-checkpoint.tar.gz`, captured immediately after the v0.9.3 Native Pwnagotchi RAW test worked physically.

The checkpoint reported:

- active touch transform: restored/original production calibration;
- touch-calibration state: `mode = restored`;
- Native Pwnagotchi source: available;
- source dimensions: 480×320;
- configured source rotation: 180°;
- exact 480×320 check: true.

The v0.9.5 installer preserves the existing active touch transform and does not replace it with the rejected Touch-Lab candidate.

## Core source delta from the checkpoint

Only these Beast Core modules changed for v0.9.5:

- `beastcore/__init__.py` — version;
- `beastcore/api.py` — detailed Achievements/Awards API exposure;
- `beastcore/progression.py` — progress/catalog/award metadata;
- `beastcore/rare.py` — rare presentation-family metadata.

All other Beast Core source modules in the checkpoint remain unchanged in this gate.

## UI source delta from the checkpoint

Changed or added UI modules:

- `beastui/__init__.py` — version;
- `beastui/backgrounds.py` — Matrix options, strict palettes and de-Moiré behavior;
- `beastui/engine.py` — hitboxes, Theme Studio controls and interactive Achievement Explorer;
- `beastui/hitbox.py` — new measured touch-target geometry layer;
- `beastui/native_effects.py` — new Native Chroma effect stack;
- `beastui/pwn_native.py` — Native Chroma effect integration;
- `beastui/rare_overlay.py` — expanded rare presentation movement/styles;
- `beastui/themes/matrix.json` — expanded Matrix theme defaults.

The Native Pwnagotchi bridge architecture itself is preserved: Jayofelony's live frame remains the authoritative source for Native RAW/Dark/Light/Chroma.

## Why this matters

This keeps the physical test narrow and auditable. v0.9.5 does not replace the entire known-working stack. It changes the UI/experience components that need physical validation while retaining the checkpoint's working collectors, display handoff, input reader, framebuffer path and Native Pwnagotchi source model.
