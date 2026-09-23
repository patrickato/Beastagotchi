# Beastagotchi Foundation Roadmap v2.3

This roadmap reflects the v0.9.5 working tree built from the physically working v0.9.3 Pi checkpoint. A checked item means the capability exists or has passed the stated gate; it does **not** mean every previous version is a stable release.

## Gate A — Hardware / Source Truth
- [x] Pi 4 / display / touch / radio hardware inventory
- [x] Pwnagotchi / Bettercap / GPS source audit
- [x] canonical data keys and source priority
- [x] verified storage/service/config paths
- [x] safe source probes and validation archives

**STATUS: PASSED**

## Gate B — Beast Core
- [x] Beast Core daemon
- [x] State Registry + Event Bus
- [x] SQLite/history foundation
- [x] collector freshness/health
- [x] Pwnagotchi callback bridge
- [x] context engine
- [x] capability/power/dock foundations
- [x] progression/lifetime encounter foundations
- [x] detailed achievement progress catalog
- [x] awards/evolution/aura catalog exposure

**STATUS: PASSED / EXTENDING**

## Gate C — Physical Display & Input
- [x] reversible physical display handoff
- [x] automatic rollback
- [x] native 480×320 RGB565 framebuffer output
- [x] reliable SYN_REPORT touch sampling
- [x] reliable arrows/swipes/long-press
- [x] deep Touch Lab: 3 stylus + 3 finger passes
- [x] pressure characterized
- [x] touch target-size policy derived
- [x] experimental pooled affine transform physically A/B tested
- [x] **restored/original calibration selected as production**
- [x] rejected candidate removed from normal upgrade flow
- [x] reusable visual-bounds vs touch-bounds hitbox layer
- [x] edge hitboxes preserve minimum target size by shifting inward
- [ ] **IN PROGRESS:** measured hitbox policy applied across major v0.9.5 surfaces
- [ ] final whole-UI physical regression

**STATUS: FUNCTIONALLY PASSED; FINAL CONTROL-POLISH GATE IN v0.9.5**

## Gate D — Visual / Theme Engine
- [x] structural theme manifests
- [x] Classic / Matrix / Starcore / Black Ice / Hunter / Minimal
- [x] layered compositor/effects
- [x] Theme Library + Theme Studio foundations
- [x] renderer switching
- [x] Rare Moment top-layer compositor
- [x] stock-style Pwnagotchi replica themes
- [x] Native Pwnagotchi Frame Bridge architecture
- [x] Native RAW / Dark / Light / Chroma profiles
- [x] **Native RAW physically validated from real Jayofelony 480×320 frame**
- [x] Native Chroma effect-stack foundation on exact native mask
- [x] independent Matrix primary/secondary/tertiary/quaternary slots
- [x] true one-color Matrix mode; no forced red accent
- [x] expanded Matrix density/speed/trail/glyph/layer controls
- [ ] **IN PROGRESS:** physical TFT de-Moiré correction via irregular spacing + micro-jitter
- [ ] physical validation of v0.9.5 Matrix corrections
- [ ] mature Korrie71-inspired per-element/effect family
- [ ] production-quality theme cards/previews
- [ ] much larger high-detail theme library

**STATUS: ACTIVE — v0.9.5 PHYSICAL GATE**

## Gate E — Beast Experience
- [x] levels 1–100 + evolution stages
- [x] persistent XP/profile
- [x] lifetime discoveries/vendor catalog foundation
- [x] achievement rarity/catalog foundation
- [x] detailed current/target/progress metadata
- [x] interactive Achievements / Awards tabs
- [x] locked/unlocked/near filters
- [x] progress/rarity/name sorting and detail cards
- [x] rare-event schedule / omen / witness model
- [x] Rare Event presentation families: fade/drift/cross/orbit/ghost/storm/apparition/cinematic
- [x] seasonal/day/moon context groundwork
- [ ] Secrets / Collections tabs and richer reward presentation
- [ ] BeastDex / Network Encyclopedia
- [ ] Capture Vault
- [ ] Session / Expedition system and recap
- [ ] production Beast personality/animation system
- [ ] seasonal/weather/celestial overlays
- [ ] Cipher Console secret-input app
- [ ] Memory Vault / scrapbook
- [ ] high-quality Rare Cinematic asset pipeline

**STATUS: ACTIVE; ACHIEVEMENT + RARE SYSTEMS NOW INTERACTIVE**

## Gate F — Extensions / Hardware / Apps
- [x] extension architecture specification
- [x] Capability Bus foundation
- [x] Power Core foundation
- [x] Dock/Field logic foundation
- [ ] Plugin Manager catalog/stage/install/enable workflow
- [ ] config broker + conf.d generation + rollback
- [ ] Hardware Studio
- [ ] AWUS036ACM enrollment/profile
- [ ] secondary Wi-Fi / Bluetooth roles
- [ ] RTL-SDR receive-app framework
- [ ] UPS/current telemetry hookup
- [ ] Replay / Simulation / Showcase modes
- [ ] Resource Governor

**STATUS: FOUNDATION BUILT; IMPLEMENTATION PENDING**

## Gate G — GitHub / Public Release
- [x] living master README
- [x] changelog
- [x] contribution draft
- [x] spoiler/secret docs
- [x] versioned A–G roadmaps
- [x] Native Pwnagotchi bridge documented
- [x] exact working-Pi checkpoint captured for forensic/reference comparison
- [ ] final repository layout
- [ ] `main` / `develop` / `feature/*` workflow
- [ ] clean installer / upgrader / uninstaller / migrations
- [ ] full user guide
- [ ] full developer guide
- [ ] theme/effect/plugin author guides
- [ ] third-party attribution/license inventory
- [ ] CI + clean release packaging
- [ ] v1.0 release candidate
- [ ] public GitHub-ready v1.0

**STATUS: PREPARING**

## Immediate order

1. Physically validate v0.9.5 as one combined UX/theme/achievement gate.
2. If touch/hitboxes pass, close Gate C except future app-specific testing.
3. If Matrix de-Moiré fails, use the physical v0.9.5 archive/video to isolate the final TFT artifact rather than changing unrelated compositor layers.
4. Expand Native Chroma into the richer Korrie71-inspired Classic+ family.
5. Build the production Theme Studio color/effect editor and saved variants.
6. Continue Achievement rewards/collections, Rare Director and cinematic benchmark.
7. Move into Sessions / BeastDex / Capture Vault.
8. Continue Plugin Manager / Hardware Studio / RF-app foundations.
9. Convert the mature tree into the final Git workflow and public packaging path.
