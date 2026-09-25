# Beastagotchi Foundation Roadmap v2.5

v2.5 marks the deliberate return from Matrix-specific corrective work to full-product breadth. The detailed anti-forgetting source of truth is `Beastagotchi_Master_Completion_Matrix_v3.0.md`; this roadmap is the high-level A–G gate view.

## Gate A — Hardware / Source Truth

- [x] Raspberry Pi 4 8 GB / OS / runtime inventory
- [x] ILI9486 480×320 framebuffer source truth
- [x] ADS7846 touch source truth
- [x] GPS / Wi-Fi / Bettercap / Pwnagotchi source audit
- [x] service/config/storage/capture path audit
- [x] canonical data keys and source freshness
- [x] known-good physical Pi checkpoint
- [ ] public support-bundle hardware inventory export

**Status: PASSED**

## Gate B — Beast Core / Data Platform

- [x] Beast Core daemon
- [x] canonical State Registry + Event Bus
- [x] SQLite + history/time-series foundation
- [x] Pwnagotchi callback bridge
- [x] semantic Wi-Fi encounter/lifetime counters
- [x] context modes and progression
- [x] Dock/Field, ambient, Rare Moment foundations
- [x] read-only local API/history/catalog endpoints
- [ ] full Rules Engine editor
- [ ] richer time-series querying/downsampling
- [ ] self-healing/incident manager

**Status: PASSED / EXTENDING**

## Gate C — Physical Display / Touch / Ergonomics

- [x] reversible framebuffer handoff + automatic rollback
- [x] reliable taps, swipes and long-press
- [x] deep stylus/finger Touch Lab characterization
- [x] pressure characterized
- [x] alternate calibration physically A/B tested
- [x] restored/original calibration selected as production
- [x] rejected calibration quarantined as experimental
- [x] visual bounds separated from touch bounds
- [x] minimum target sizes / non-overlap policy established
- [x] footer priority protected from graph hit zones
- [ ] final whole-UI interaction regression
- [ ] optional pressure-based secret mechanics / drawing lab

**Status: VERY NEAR COMPLETE**

## Gate D — UI / Themes / Visualizers / Layouts

### Shell and preservation
- [x] 8-page main carousel
- [x] Control Center / Theme Library / Theme Studio
- [x] Native Pwnagotchi RAW/Dark/Light/Chroma bridge
- [x] original live Jayofelony face/actions physically validated
- [x] Classic / Matrix / Starcore / Black Ice / Hunter / Minimal families

### v0.10 visualization-breadth gate
- [x] Visualizer Studio foundation
- [x] generalized renderer selection beyond Spectrum
- [x] Recon renderer switching
- [x] Spectrum renderer switching
- [x] Captures renderer switching
- [x] System renderer switching
- [x] Line / Area / Multi-line / Bars / Stacked Bars primitives
- [x] Histogram / Heatmap / Waterfall / Waveform
- [x] Radial / Donut / Radar / Polar / Signal Meter
- [x] Timeline / numeric+microtrend
- [x] broader history cache for future visualizers
- [x] direct graph-tap cycling without stealing footer touches

### Theme breadth
- [x] Classic Grid / Scanline / Pulse controls
- [x] Starcore Stars / Twinkle / Orbit controls
- [x] Black Ice Frost / Drift / Crystal controls
- [x] Hunter Grid / Reticle / Embers controls
- [x] Minimal Ambient / Panel controls foundation
- [ ] Synthwave / Amber Tactical / Ghost Minimal
- [ ] Cyberpunk / Stealth / Red Alert / Forest
- [ ] Vaporwave / Space / Holographic / Golden / Samurai
- [ ] WOPR-NORAD / Steampunk / Blueprint / Terminal+ / Biohazard / Glitch / Comic
- [ ] seasonal/holiday theme families
- [ ] user/community theme packs

### Layout/customization depth
- [ ] per-widget renderer selection and data-aware eligibility
- [ ] theme-specific graph skins/animations
- [ ] arbitrary color picker and color weighting controls
- [ ] widget move/resize/show/hide
- [ ] independent layout save/load
- [ ] context-driven layouts
- [ ] production Theme Studio previews/cards

**Status: ACTIVE — BREADTH EXPANSION NOW PRIMARY**

## Gate E — Beast Experience / Personality / Progression / Secrets

- [x] finite Levels 1–100 and evolution stages
- [x] session aura foundation
- [x] interactive Achievements/Awards browser + rarity/progress
- [x] Rare Moment schedule/witness/presentation system
- [x] fade/drift/cross/orbit/ghost/storm/apparition/cinematic mechanics
- [x] season/day-phase/moon groundwork
- [ ] mature Beast animation/personality state machine
- [ ] Secrets / Collections / trophy cabinet
- [ ] hundreds of long-tail achievement chains
- [ ] production 5–60 s Rare Cinematics
- [ ] Cipher Console / puzzle inputs
- [ ] seasonal/weather/celestial production presentation
- [ ] Sessions / Expeditions / replay
- [ ] Memory Vault / scrapbook / records

**Status: ACTIVE**

## Gate F — Apps / Plugins / Hardware Expansion

- [x] Capability Bus architecture
- [x] Power/Dock architecture
- [x] plugin lifecycle/compatibility architecture
- [~] Networks / Recon / Spectrum / Captures / Map foundations
- [ ] Network Encyclopedia / BeastDex
- [ ] Capture Vault
- [ ] full offline/online Map system and layers
- [ ] Plugin Manager + config broker/rollback
- [ ] Hardware Studio
- [ ] AWUS036ACM / secondary Wi-Fi role system
- [ ] Bluetooth observer and device roles
- [ ] RTL-SDR receive-focused RF app suite
- [ ] UPS telemetry / power manager
- [ ] Resource Governor
- [ ] Replay / Simulation / Showcase modes
- [ ] companion Web UI

**Status: FOUNDATION BUILT / IMPLEMENTATION PENDING**

## Gate G — Reliability / Documentation / GitHub / v1.0

- [x] living master README
- [x] changelog
- [x] spoiler/secret documentation
- [x] versioned A–G roadmaps
- [x] Master Completion Matrix anti-forgetting ledger
- [x] known-good Pi checkpoint strategy
- [ ] performance/resource budgets and thermal governor
- [ ] backup/restore/recovery UI
- [ ] final repository layout
- [ ] `main` / `develop` / `feature/*` branch workflow
- [ ] installer/upgrader/uninstaller/migrations
- [ ] complete user/developer/theme/plugin authoring documentation
- [ ] third-party attribution/license inventory
- [ ] CI/release packaging
- [ ] v1.0 release candidate
- [ ] public GitHub-ready v1.0

**Status: PREPARING**

---

## Current physical gate: v0.10.0

The next physical test intentionally de-emphasizes Matrix. It validates:

1. Visualizer Studio navigation and renderer selection.
2. Representative new graph modes on Spectrum/System/Recon/Captures.
3. Classic/Starcore/Black Ice/Hunter/Minimal Theme Studio controls.
4. Footer/input priority after adding new graph hit zones.
5. Quick Native RAW regression only.
6. General thermal/performance behavior with more varied visuals.

A Matrix regression check remains, but Matrix is no longer the development center of gravity.
