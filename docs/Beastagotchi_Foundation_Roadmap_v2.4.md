# Beastagotchi Foundation Roadmap v2.4

## Gate A — Hardware / Source Truth
- [x] Raspberry Pi 4 / display / touch inventory
- [x] Pwnagotchi / Bettercap / GPS source audit
- [x] radio / channel / monitor-mode audit
- [x] canonical data keys and source priority
- [x] verified storage, service and configuration paths
- [x] safe probe / validation workflow

**Status: PASSED**

## Gate B — Beast Core
- [x] Beast Core daemon
- [x] State Registry
- [x] Event Bus
- [x] SQLite/history foundation
- [x] collector freshness / health
- [x] Pwnagotchi callback bridge
- [x] context engine
- [x] progression / lifetime encounter model
- [x] detailed achievement and award catalogs
- [x] Rare Moment scheduler / witness model

**Status: PASSED / EXTENDING**

## Gate C — Physical Display & Input
- [x] reversible framebuffer ownership handoff
- [x] automatic rollback
- [x] reliable ADS7846 event synchronization
- [x] horizontal / vertical swipe classification
- [x] long-press handling
- [x] 3x stylus + 3x finger Touch Lab characterization
- [x] pressure characterization
- [x] alternate affine calibration physically A/B tested
- [x] restored/original calibration selected as production
- [x] global visual-bounds / touch-bounds model
- [x] Achievement Explorer non-overlapping physical touch partitions
- [ ] final whole-UI regression after v0.9.5

**Status: VERY NEAR COMPLETE**

## Gate D — Visual / Theme Engine
- [x] structural theme manifests
- [x] Classic / Matrix / Starcore / Black Ice / Hunter / Minimal
- [x] Theme Library / Theme Studio foundation
- [x] Native Pwnagotchi Bridge
- [x] Native RAW physically validated
- [x] Native Dark / Light / Chroma
- [x] Korrie71-inspired Beast-native effect direction
- [x] Matrix 1–4 color architecture
- [x] strict single-color Matrix mode
- [x] foreground/background Matrix layering
- [x] identified v0.9.4 magenta diagonal artifact as event reaction, not rain
- [x] v0.9.5 fixed-X Matrix reaction geometry
- [x] Matrix reaction On/Off customization
- [ ] physical confirmation that Matrix rain itself no longer produces diagonal TFT bands
- [ ] production-quality Classic+ effect library
- [ ] larger high-detail theme library / final cards / previews

**Status: ACTIVE**

## Gate E — Beast Experience
- [x] levels 1–100 / evolution stages
- [x] XP/profile persistence
- [x] achievement rarity and long-tail milestones
- [x] interactive Achievements / Awards browser
- [x] progress counters / bars / detail views
- [x] Rare Moment fade / drift / cross / orbit / ghost / storm / apparition / cinematic mechanics
- [x] seasonal / day-phase / moon groundwork
- [ ] Collections / Secrets presentation
- [ ] Sessions / Expeditions
- [ ] BeastDex / Network Encyclopedia
- [ ] Capture Vault
- [ ] production Beast personality animation system
- [ ] Cipher Console
- [ ] Memory Vault / scrapbook
- [ ] final high-quality Rare Cinematic assets

**Status: ACTIVE**

## Gate F — Extensions / Hardware / Apps
- [x] Plugin architecture specification
- [x] Capability Bus foundation
- [x] Power Core foundation
- [x] Dock / Field logic foundation
- [ ] Plugin Manager / staged install / enable workflow
- [ ] config broker / rollback
- [ ] Hardware Studio
- [ ] AWUS036ACM enrollment/profile
- [ ] RTL-SDR app framework
- [ ] secondary Wi-Fi / Bluetooth roles
- [ ] UPS telemetry hookup
- [ ] Replay / Simulation / Showcase
- [ ] Resource Governor / thermal-aware visual budget

**Status: FOUNDATION BUILT; IMPLEMENTATION PENDING**

## Gate G — Public / GitHub Release
- [x] living master README
- [x] changelog
- [x] contributing draft
- [x] spoiler / secret documentation
- [x] versioned A–G roadmaps
- [x] known-working Pi checkpoint
- [ ] final repository layout
- [ ] main / develop / feature branch workflow
- [ ] installer / upgrader / uninstaller / migration tooling
- [ ] complete user guide
- [ ] developer / theme / plugin authoring guides
- [ ] third-party attribution / license inventory
- [ ] CI tests / release packaging
- [ ] release candidate
- [ ] public GitHub-ready v1.0

**Status: PREPARING**

## Immediate physical gate after v0.9.5

Only three things need another user pass:

1. Matrix event reaction no longer creates a temporary pink/magenta diagonal sweep.
2. Matrix color/layer/density controls that were not checked in v0.9.4 behave distinctly and predictably.
3. Achievement Explorer controls are easier to hit after removal of overlapping touch regions.

Native RAW and Rare Moment mechanics do not need to be revalidated in this gate.
