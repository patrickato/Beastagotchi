# Beastagotchi v0.9.5 — Physical Validation Review

## Result

v0.9.5 completed the focused Matrix/Achievement follow-up well enough to stop treating Matrix as the primary development target. It is not declared a final/stable release; its validated pieces are carried forward into the v0.10.0 breadth gate.

## Archive observations

- Beast Core reported `healthy` with 273 keys live, 0 stale and 0 unavailable at collection time.
- Production touch state remained the restored/original calibration selected by the physical A/B test.
- UI preferences confirmed the expanded Matrix controls were persisted, including Mixed layer, Deluge density, Torrent speed, Custom palette, Extreme trail, 20% foreground, Heavy accents and Reactions On.
- Native Pwnagotchi remained available in the inherited bridge lineage.
- Thermal history repeatedly crossed warm/hot bands and reached 80.34 C during the validation session. This reinforces the planned Resource Governor/thermal budget work; it does not change the visual-quality target.

## Physical/video observations

- Touch and swipes were reported good overall.
- Achievement Explorer was usable, though some controls still felt compact.
- Native/stock Pwnagotchi continued to work.
- Matrix rain visibly changed with density/speed settings and remained predominantly vertical in the reviewed footage.
- The test did not fully exercise every custom color-slot combination, so those controls remain implemented but not exhaustively physically signed off.

## Development consequence

Repeated v0.8–v0.9 Matrix work was bug-driven: scanline/event-reaction confusion, TFT Moiré appearance and the temporary magenta thermal-reaction sweep each needed isolation on real hardware. The comprehensive Beastagotchi scope did not change.

Starting with v0.10.0, the visual-development center of gravity moves back to:

- renderer/chart breadth;
- non-Matrix theme customization;
- theme-native visual identities;
- layouts/widgets;
- and the wider Gate E/F experience/app/hardware roadmap.

Matrix remains in regression coverage rather than monopolizing the next development gates.
