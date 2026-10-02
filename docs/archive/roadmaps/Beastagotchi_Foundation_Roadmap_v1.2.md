# Beastagotchi Foundation Roadmap v1.2

## Gate A — Design Foundation
- [x] Product philosophy and modular visual architecture
- [x] Main page architecture
- [x] Canonical state namespaces v2
- [x] Theme/layout/renderer/face separation
- [x] Adaptive context / progression specification
- [x] Interaction and performance principles

## Gate B — Live Data Audit
- [x] Real-Pi source audit
- [x] Bettercap authenticated API runtime validation
- [x] Radio/interface/channel runtime validation
- [x] Service parser runtime validation
- [x] Pwnagotchi cache/session fallback validation
- [ ] Capture GPS TPV/SKY with a real fix and motion sample
- [ ] Observe exact 2.9.5.9 epoch data through enabled Beast Bridge

**Gate status: PASS.** Remaining items are opportunistic runtime observations.

## Gate C — Beast Core Skeleton
- [x] package skeleton
- [x] canonical state registry
- [x] source priority/fallback behavior
- [x] event bus
- [x] collector scheduler
- [x] SQLite WAL foundation
- [x] bounded durable time-series sampler + retention
- [x] system/radio/GPS/Bettercap/Pwnagotchi/service/storage/hardware collectors
- [x] per-collector health, timing, error and freshness state
- [x] read-only HTTP API
- [x] read-only WebSocket event/state streaming
- [x] Pwnagotchi Beast Bridge event-ring plugin
- [x] safe automatic motion/context engine foundation
- [ ] validate v0.3 on actual Pi
- [ ] validate Beast Bridge callbacks on actual Pwnagotchi 2.9.5.9
- [ ] config manager
- [ ] action broker + privilege policy
- [ ] incident/health engine and bounded flight recorder

## Gate D — UI Engine Skeleton
- [ ] framebuffer compositor
- [ ] RGB565 direct-flush path
- [ ] touch dispatcher using existing affine calibration
- [ ] navigation stack/footer/drawer/notifications
- [ ] widget + renderer interfaces
- [ ] theme/layout/face loaders
- [ ] adaptive frame-rate/load shedding

## Gate E — Reference Experience
- [ ] Classic Beast reference theme
- [ ] Home / Recon / Networks / Spectrum / Captures / Map / Beast / System
- [ ] native 480×320 QA

## Gate F — Customization Proof
- [ ] six reference themes
- [ ] graph renderer switching
- [ ] face packs/evolution layers
- [ ] density/layout presets
- [ ] theme-specific event reactions and session auras

## Gate G — Operational Apps
- [ ] logs / diagnostics / services / plugins / storage / backup
- [ ] timeline / incidents / sessions / developer center
- [ ] progression level 1–100, achievements, collections and Easter eggs

## Gate H — Expansion
- [ ] web/phone UI
- [ ] second radio / Scout
- [ ] Bluetooth / SDR / ADS-B / rtl_433 / Meshtastic
- [ ] sensors/power/IMU/dock
- [ ] optional 2.5D/3D renderers
- [ ] AI/voice

## Next physical gate

Install Beast Core v0.3, validate HTTP/WebSocket/health/history state, then install the read-only Beast Bridge and restart Pwnagotchi once to observe real callback data. No active radio behavior is added by this gate.
