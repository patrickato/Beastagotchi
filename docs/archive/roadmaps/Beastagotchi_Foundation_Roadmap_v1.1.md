# Beastagotchi Foundation Roadmap v1.1

## Gate A — Design Foundation
- [x] Product philosophy
- [x] Main page architecture
- [x] Canonical state namespaces
- [x] Theme/layout/renderer/face separation
- [x] Interaction principles
- [x] Performance budgets
- [x] First implementation theme set
- [x] First implementation renderer set
- [x] First implementation face set

## Gate B — Live Data Audit
- [x] Expected data-source map
- [x] Run source-probe bundle on real Pi
- [x] Confirm Pwnagotchi version/service/config paths
- [x] Confirm radio interfaces and supported channels
- [x] Confirm GPS device/gpsd path
- [x] Confirm handshake directory and AP-cache schema
- [x] Confirm plugin configuration source
- [x] Confirm systemd service names
- [x] Confirm framebuffer/touch target
- [x] Mark primary canonical keys SUPPORTED / DERIVED / BRIDGE / RUNTIME VERIFY
- [ ] Runtime-test corrected Bettercap active-caplet API collector
- [ ] Capture GPS TPV/SKY with real fix
- [ ] Inventory actual capture files under configured handshake directory
- [ ] Inventory custom plugin files
- [ ] Observe exact 2.9.5.9 `epoch_data` through bridge plugin

**Gate status:** PASS — remaining items are runtime validation tasks and do not block core implementation.

## Gate C — Beast Core Skeleton
- [x] package skeleton
- [x] state registry
- [x] event bus
- [x] collector scheduler
- [x] SQLite foundation
- [x] Linux/system collector
- [x] storage collector
- [x] radio collector
- [x] GPS collector
- [x] Pwnagotchi fallback collector
- [x] corrected active-caplet Bettercap collector
- [x] service collector
- [x] hardware collector
- [x] local read-only HTTP API
- [x] optional Pwnagotchi Beast Bridge plugin prototype
- [ ] validate all collectors on actual Pi
- [ ] add canonical health state/staleness rules
- [ ] add time-series sampling/retention policy
- [ ] add WebSocket transport
- [ ] action broker interface
- [ ] privilege/action policy
- [ ] config manager
- [ ] incident/health engine

## Gate D — UI Engine Skeleton
- [ ] framebuffer compositor
- [ ] RGB565 direct-flush path
- [ ] touch dispatcher using existing affine calibration
- [ ] navigation stack
- [ ] persistent footer
- [ ] swipe/scroll/tap/long-press
- [ ] quick drawer
- [ ] notification overlay
- [ ] theme loader
- [ ] layout loader
- [ ] widget model
- [ ] renderer interface
- [ ] face pack interface
- [ ] adaptive frame-rate/load shedding

## Gate E — Reference Experience
- [ ] Classic Beast reference theme
- [ ] Home
- [ ] Recon
- [ ] Networks
- [ ] Spectrum
- [ ] Captures
- [ ] Map
- [ ] Beast
- [ ] System
- [ ] native 480×320 QA for every screen

## Gate F — Customization Proof
- [ ] six reference themes
- [ ] nine initial graph renderers
- [ ] five initial face packs
- [ ] density profiles
- [ ] layout presets
- [ ] live renderer switching
- [ ] live theme switching
- [ ] persistent user presets

## Gate G — Operational Apps
- [ ] logs
- [ ] diagnostics
- [ ] service manager
- [ ] plugin manager
- [ ] storage
- [ ] backup/restore
- [ ] timeline
- [ ] incidents
- [ ] sessions
- [ ] developer center

## Gate H — Expansion
- [ ] desktop/phone web UI
- [ ] second radio / Kismet
- [ ] Bluetooth
- [ ] SDR / ADS-B / rtl_433
- [ ] Meshtastic
- [ ] sensors/power/IMU
- [ ] dock mode
- [ ] AI/voice

## Next physical gate

Install the **read-only Beast Core Foundation v0.1** beside the existing Beast previews, run a one-shot collector snapshot, then temporarily start `beast-core.service` and capture `/state` plus its service log. No Pwnagotchi or Bettercap configuration changes are required for this first test.
