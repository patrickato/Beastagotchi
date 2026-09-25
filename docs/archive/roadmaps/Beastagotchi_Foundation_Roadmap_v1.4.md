# Beastagotchi Foundation Roadmap v1.4

## Gate A — Design Foundation
- [x] Product philosophy and modular visual architecture
- [x] Main page architecture
- [x] Canonical state namespaces
- [x] Theme/layout/renderer/face separation
- [x] Adaptive context / progression specification
- [x] Interaction and performance principles

## Gate B — Live Data Audit
- [x] Real-Pi source audit
- [x] Bettercap authenticated API runtime validation
- [x] Radio/interface/channel runtime validation
- [x] Service parser runtime validation
- [x] Pwnagotchi cache/session fallback validation
- [x] Exact Pwnagotchi 2.9.5.9 callbacks observed through Beast Bridge
- [ ] Capture sustained GPS TPV/SKY with a real fix and motion sample (opportunistic)

**Gate status: PASS.**

## Gate C — Beast Core Skeleton
- [x] package skeleton
- [x] canonical state registry
- [x] source priority/fallback behavior
- [x] event bus
- [x] collector scheduler
- [x] SQLite WAL foundation
- [x] bounded durable time-series sampler + retention
- [x] system/radio/GPS/Bettercap/Pwnagotchi/service/storage/hardware collectors
- [x] per-collector health/timing/error/freshness state
- [x] read-only HTTP API
- [x] read-only WebSocket state/event streaming
- [x] Pwnagotchi Beast Bridge event-ring plugin
- [x] automatic passive motion/context engine foundation
- [x] semantic/meaningful-event engine foundation
- [x] transient-vs-durable event separation
- [x] GPS current-value clearing semantics
- [x] GPS semantic debounce / motion-context grace
- [ ] config manager
- [ ] action broker + privilege policy
- [ ] incident/health engine + bounded flight recorder

## Gate D — UI Engine Skeleton
- [x] 480×320 compositor skeleton
- [x] RGB565 direct framebuffer flush path
- [x] existing affine touch calibration loader
- [x] ADS7846 event-node rediscovery
- [x] horizontal navigation + persistent arrows/home
- [x] quick drawer interaction foundation
- [x] theme manifest loader
- [x] face engine / context accessory foundation
- [x] event-reaction contract foundation
- [x] adaptive frame-rate/load shedding foundation
- [x] eight main page render contracts
- [x] off-screen renderer validated under `/opt/.pwn` Python on target Pi
- [x] reversible display-ownership tooling implemented
- [ ] physical LCD orientation/readability validation
- [ ] physical touch/gesture validation
- [ ] confirm persistent Beast UI display ownership
- [ ] notification stack / context menus / scrolling model
- [ ] graph renderer registry and per-widget renderer switching

## Gate E — Reference Experience
- [ ] Classic Beast reference theme polish
- [ ] Home / Recon / Networks / Spectrum / Captures / Map / Beast / System production pages
- [ ] native 480×320 QA and touch-size audit

## Gate F — Customization Proof
- [ ] six reference structural themes
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

## Current physical gate

Install Beast Core v0.5 + Beast UI v0.2, then run the timed `claim_display_test.sh` handoff. The script keeps Pwnagotchi/Bettercap active, disables only Pwnagotchi's LCD renderer, starts Beast UI as the intended framebuffer owner, and automatically restores the prior configuration if the test is not confirmed.
