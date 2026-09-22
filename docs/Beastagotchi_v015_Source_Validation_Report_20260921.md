# Beastagotchi v0.15.0 Source Validation Report — 2026-09-21

## Result
PASS for clean-source packaging gate.

## Scope
v0.15.0 is the Spatial Studio / User Boards milestone. It extends the v0.13 platform and live-data architecture without changing the protected Pwnagotchi/Bettercap ownership model.

## Clean package checks
- Python compileall: PASS
- Shell syntax for installers/validator/display handoff: PASS
- Embedded Beast Studio JavaScript syntax (`node --check`): PASS
- Automated regression suite: 135 / 135 PASS
- Module version identity: beastcore = beastui = beaststudio = 0.15.0
- Exact clean-archive extraction test: PASS
- Off-screen validation gallery from previously collected real target state: 23 / 23 frames PASS
- Every gallery frame: 480x320 and nonblank

## New validated capabilities
- variable-count Dashboard instruments rather than a fixed six slots;
- shared 12x8 spatial layout model between Studio and the TFT compositor;
- add/remove/show/hide instruments;
- geometry editing plus direct drag/move/resize overlay in Studio;
- z-order / bring-front behavior and hit-testing of overlapping instruments;
- named custom live Boards;
- custom Boards registered dynamically into the App universe;
- Board compatibility with Context Deck ids;
- exact-preview editing remains draft-based until atomic Apply;
- canonical live telemetry semantics preserved for all generic instruments.

## Explicitly still incomplete
The spatial composer currently targets the generic Dashboard/Board instrument surface. Arbitrary editing of every built-in page's internal widgets, structured list/map/plugin widgets, grouping/alignment/multi-select, timed Try-On-Device, and import/export/community composition packs remain later milestones and are recorded in the completion matrix.

## Physical test philosophy
v0.15 should be tested as a broad integrated milestone, not as a sequence of single-control micro-gates. The primary physical questions are overall visual cleanliness, touch/drag usability in the web Studio when controlling the Pi, performance/temperature behavior, and whether custom Boards feel like a useful expansion path.
