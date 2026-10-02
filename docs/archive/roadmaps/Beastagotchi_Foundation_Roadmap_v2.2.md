# Beastagotchi Foundation Roadmap v2.2

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
- [x] experimental pooled affine calibration physically A/B tested
- [x] **original pre-v0.9.2 calibration selected as the better real-world calibration**
- [x] do not auto-apply the rejected candidate
- [ ] finish applying measured hitbox/edge-padding standards to every app/control
- [ ] final Gate-C regression pass after the control library is unified

**STATUS: FUNCTIONALLY PASSED; CONTROL-POLISH REMAINS**

## Gate D — Visual / Theme Engine
- [x] structural theme manifests
- [x] Classic / Matrix / Starcore / Black Ice / Hunter / Minimal
- [x] layered compositor/effects
- [x] Theme Library + Theme Studio foundations
- [x] renderer switching
- [x] Rare Moment top-layer compositor
- [x] stock-style Pwnagotchi replica themes
- [x] **Native Pwnagotchi Frame Bridge architecture**
- [x] **Native RAW / Native Dark / Native Light / Native Chroma profiles implemented**
- [ ] physically validate exact Jayofelony 480×320 native frame passthrough
- [ ] expand Native Chroma into Korrie71-style per-element/effect family
- [ ] independent primary/secondary/tertiary/quaternary palette controls
- [ ] mature Matrix renderer / remove remaining TFT artifact
- [ ] production-quality theme cards/previews
- [ ] larger high-detail theme library

**STATUS: ACTIVE — NATIVE PWNAGOTCHI PHYSICAL GATE NEXT**

## Gate E — Beast Experience
- [x] levels 1–100 + evolution stages
- [x] persistent XP/profile
- [x] lifetime discoveries/vendor catalog foundation
- [x] achievement rarity/catalog foundation
- [x] rare-event schedule / omen / witness model
- [x] seasonal/day/moon context groundwork
- [ ] interactive Achievements / Awards / Secrets / Collections app
- [ ] progress trackers and locked/unlocked browsing
- [ ] BeastDex / Network Encyclopedia
- [ ] Capture Vault
- [ ] Session / Expedition system and recap
- [ ] production Beast personality/animation system
- [ ] seasonal/weather/celestial overlays
- [ ] Cipher Console secret-input app
- [ ] Memory Vault / scrapbook
- [ ] high-quality Rare Cinematic asset pipeline

**STATUS: ACTIVE**

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
- [x] versioned A–G roadmaps restored
- [x] Native Pwnagotchi bridge documented
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

1. Physically validate Native Dark/Light against the live Jayofelony frame.
2. Lock Native Frame Bridge if source is 480×320 and visually exact.
3. Finish global touch hitbox standards using the restored calibration.
4. Expand Native Chroma/Korrie71-style effects using the real Pwnagotchi frame as the source.
5. Continue Theme Studio + Matrix corrections.
6. Build interactive Achievements and richer Rare Event Director.
7. Continue Sessions/BeastDex/Capture Vault/Hardware/Plugin work.
