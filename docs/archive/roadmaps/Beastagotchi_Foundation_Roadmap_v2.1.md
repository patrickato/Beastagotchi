# Beastagotchi Foundation Roadmap v2.1

## Gate A — Hardware / Source Truth
- [x] Pi 4 / OS / storage inventory
- [x] Pwnagotchi / Bettercap / GPS source audit
- [x] Radio / channel / PHY verification
- [x] 480×320 ILI9486 framebuffer identification
- [x] ADS7846/XPT2046 input identification
- [x] Canonical data model and source priority
- [x] Safe validation/probe workflow

**Status: PASSED**

## Gate B — Beast Core
- [x] Beast Core daemon
- [x] State registry + event bus
- [x] SQLite/history foundation
- [x] Collector health/freshness
- [x] Pwnagotchi callback bridge
- [x] Bettercap / GPS / radio / system collectors
- [x] Context engine (PWN/WALK/TRAVEL/WARDRIVE)
- [x] Hardware/Capability Bus foundations
- [x] Power/Dock foundations
- [x] Progression + lifetime encounter foundations

**Status: PASSED / EXTENDING**

## Gate C — Physical Display & Human Input
- [x] Safe display ownership handoff
- [x] Automatic display rollback
- [x] Native RGB565 framebuffer writer
- [x] Reliable arrows/swipes/long-press
- [x] Physical gesture validation
- [x] 3× stylus + 3× finger Touch Lab characterization
- [x] Pooled affine calibration candidate (≈2 px median stylus residual)
- [x] Measured target-size policy
- [x] Reversible `beast-touchcal` manager
- [ ] Confirm new affine calibration on physical device
- [ ] Freeze final interaction/hitbox standard after physical check

**Status: 90% — PHYSICAL CONFIRMATION NEXT**

## Gate D — Visual / Theme Engine
- [x] Theme manifests + compositor layers
- [x] Classic Beast / Matrix / Starcore / Black Ice / Hunter / Minimal
- [x] Theme Library + Theme Studio foundation
- [x] Renderer swapping foundation
- [x] Rare overlay/cinematic framework
- [x] Pwnagotchi Original Dark
- [x] Pwnagotchi Original Light
- [x] Pwnagotchi Chroma / original-face mood-color foundation
- [x] Korrie71-native integration architecture documented
- [ ] Physical validation of Original Light/Dark/Chroma
- [ ] Classic+ palette/effect editor
- [ ] Independent primary/secondary/tertiary/quaternary colors
- [ ] Mature Matrix renderer cleanup/customization
- [ ] Production theme cards/previews
- [ ] Broader Korrie-style effect stack: glow/gradient/stars/grain/vignette/etc.

**Status: ACTIVE — ORIGINAL IDENTITY RESTORED IN CODE**

## Gate E — Beast Experience
- [x] Levels 1–100 + evolution stages
- [x] Persistent XP/profile
- [x] Lifetime first-seen AP/vendor tracking
- [x] Achievement rarity foundation
- [x] Session aura foundation
- [x] Rare Moment scheduling/witness model
- [x] Seasonal/day/moon groundwork
- [ ] Interactive Achievements / Awards / Secrets / Collections browser
- [ ] BeastDex / Network Encyclopedia
- [ ] Capture Vault
- [ ] Session start/end/report experience
- [ ] Production Beast personality/animation packs
- [ ] Seasonal/weather/celestial overlays
- [ ] Cipher Console
- [ ] Memory Vault / scrapbook
- [ ] Final high-detail Rare Cinematic packs

**Status: ACTIVE**

## Gate F — Extensions / Hardware / Apps
- [x] Plugin extension architecture specification
- [x] Capability Bus foundation
- [x] Power Core foundation
- [x] Dock/Field rule foundation
- [ ] Plugin catalog: Available → Staged → Installed → Enabled
- [ ] Plugin config fragment generator / rollback
- [ ] Hardware Studio
- [ ] AWUS036ACM enrollment/profile
- [ ] RTL-SDR app framework
- [ ] Secondary Wi-Fi / Bluetooth role manager
- [ ] Waveshare UPS telemetry physical hookup
- [ ] Replay / Simulation / Showcase modes
- [ ] Resource Governor

**Status: FOUNDATION BUILT; IMPLEMENTATION PENDING**

## Gate G — Public / GitHub Release
- [x] Living master README
- [x] Changelog
- [x] Contributing draft
- [x] Spoiler/secret documentation
- [x] A–G roadmap restored as a maintained artifact
- [ ] Final repository layout
- [ ] `main` / `develop` / `feature/*` workflow
- [ ] Clean installer/upgrader/uninstaller
- [ ] Migration/rollback tooling
- [ ] User guide + developer guide
- [ ] Theme/plugin authoring guides
- [ ] Third-party attribution/license inventory
- [ ] CI + release packaging
- [ ] v1.0 release candidate
- [ ] Public GitHub-ready v1.0

**Status: PREPARING**

---

## Current critical path

1. **Physical Gate C/D check:** validate pooled touch calibration + Original Dark/Light/Chroma on the real 3.5-inch screen.
2. Freeze measured global interaction/hitbox rules.
3. Continue Classic+ / Korrie-inspired native effects and Theme Studio customization.
4. Expand interactive achievements/secrets/seasonal experiences.
5. Continue hardware/plugin/app ecosystem and public-repository preparation.
