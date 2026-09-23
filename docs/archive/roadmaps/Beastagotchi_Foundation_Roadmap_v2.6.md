# Beastagotchi Foundation Roadmap v2.6

v2.6 follows the full pinned-conversation continuity audit and the v0.11.0 implementation pass. The detailed source of truth is `Beastagotchi_Master_Completion_Matrix_v4.0.md`; the continuity source inventory is `Beastagotchi_Project_Continuity_Audit_v1.0.md`.

## Gates A–C — source truth, core foundation, physical input

- [x] Pi 4 / ILI9486 / ADS7846 / GPS / radio / Bettercap / Pwnagotchi source truth
- [x] canonical state/event/database/history platform and callback bridge
- [x] reversible framebuffer handoff and validated production touch calibration
- [x] physical Native Pwnagotchi preservation
- [ ] final whole-UI touch regression remains a v1.0 gate

**Status: FOUNDATION PASSED / REGRESSION MAINTAINED**

## Gate D — UI / Themes / Visualizers / Layouts

- [x] 9-page carousel including Expedition
- [x] Visualizer Studio and broad renderer library
- [x] Classic / Matrix / Starcore / Black Ice / Hunter / Minimal Field
- [x] Synthwave / Amber Tactical / Ghost Minimal implementation
- [x] temporary governor-driven visual load shedding without overwriting saved preferences
- [ ] per-widget renderer/data-aware eligibility
- [ ] independent layout system and move/resize/show/hide
- [ ] broader structural-theme catalog and community packages

**Status: ACTIVE — THREE NEW THEMES AWAIT PHYSICAL SIGN-OFF**

## Gate E — Beast Experience / Progression / Expeditions

- [x] finite level 1–100 / evolution / achievements / Rare Moment foundations
- [~] persistent Expedition engine: automatic begin/recovery across controlled or unclean restarts, GPS route, distance, unique APs, captures, XP, thermal/CPU/battery extrema
- [~] Expedition touchscreen page and Map integration
- [ ] manual named Begin/End, notes/tags, polished recap, records and replay
- [ ] mature personality animation, Collections/Secrets/Memory Vault/Cipher Console

**Status: ACTIVE — EXPEDITION FOUNDATION AWAITS PHYSICAL SIGN-OFF**

## Gate F — Apps / Plugins / Hardware Expansion

- [x] Capability Bus / Power-Dock / Plugin lifecycle architectures
- [ ] Network Encyclopedia / BeastDex and production Capture Vault
- [ ] full offline map system/layers and RF Universe
- [ ] Plugin Manager + config broker/rollback/quarantine
- [ ] Hardware Studio + accessory enrollment
- [ ] second Wi-Fi/Kismet, Bluetooth, SDR, ADS-B, rtl_433 and Mesh modules
- [ ] Dock/Home Base automation and companion web UI

**Status: PLATFORM FOUNDATION BUILT / APP IMPLEMENTATION PENDING**

## Gate G — Reliability / Resource Governor / v1.0

- [x] cached data feed, render timing and adaptive FPS foundation
- [x] Resource Governor FULL / GUARDED / REDUCED / SURVIVAL foundation
- [x] thermal thresholds, live-vs-historical throttle handling and recovery hysteresis
- [x] UI effect/FPS/history/cinematic load-shedding foundation
- [ ] per-module cost declarations and SD-card write budgets
- [ ] Black Box/self-healing/backup/restore/recovery UI
- [ ] final Git workflow, installer/upgrader/migrations, CI/reproducible packaging and public docs

**Status: ACTIVE — GOVERNOR AWAITS REAL-PI VALIDATION**

## Current physical gate — v0.11.0

1. Confirm Governor mode, budget and recovery behavior on the real Pi.
2. Confirm no false SURVIVAL state from historical throttle bits.
3. Confirm themes visually reduce work under pressure but saved Theme Studio choices remain unchanged.
4. Confirm Expedition persists and recovers across controlled Beast Core restart and accumulates real GPS/AP data.
5. Evaluate Synthwave, Amber Tactical and Ghost Minimal on the ILI9486 panel.
6. Regression-check footer/touch navigation, Native RAW, Pwnagotchi/Bettercap coexistence and general thermals.

After that physical gate, the next implementation block should deepen **Expeditions + Network Encyclopedia/Capture Vault foundations** while continuing the Resource Governor into explicit module/app resource declarations. Plugin Manager/Hardware Studio remain high-priority platform milestones rather than being dropped.
