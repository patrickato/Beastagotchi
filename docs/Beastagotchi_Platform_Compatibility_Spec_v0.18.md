# Beastagotchi Platform & Compatibility Specification v0.18

## Purpose
v0.18 builds on the validated v0.17 platform boundary with owner-authorized Operator privilege sessions, staged recovery planning, declarative Mission Packs, a canonical living-Beast personality state, and the first native-responsive Beast Board surface. Pwnagotchi and Bettercap remain protected engines underneath Beast Core.

## 1. Startup truthfulness
Beast Core distinguishes STARTING from DEGRADED. Concurrent collectors receive finite startup grace. Critical Pwnagotchi, Bettercap, or read-only-root failures become CRITICAL. Target validation waits for semantic readiness rather than treating an open HTTP port as completed boot.

## 2. Display compatibility and responsive migration
480×320 remains the validated reference/minimum Beast canvas for legacy pages. Beast separates logical composition from physical output through `DisplayTransform`, with aspect-preserving fit, explicit diagnostic stretch, centered letter/pillar bars, selectable resampling, and reverse physical-touch mapping.

v0.18 introduces the first **native-responsive** surface: user-composed Dashboard/Boards can compose directly into larger 640×480 and 800×480 targets from the same logical grid. Legacy Beast pages remain compatibility-scaled until migrated individually. Therefore:

- Dashboard/Boards: native responsive composition is supported by the v0.18 renderer path.
- Legacy pages: larger-output proofs remain compatibility scaling, not a claim of full responsive layout support.
- 480×320 remains the physically validated production reference target for this release.

## 3. Field Library
Field Library remains offline-first. Text, Markdown, configuration, HTML and related formats are indexed directly. EPUB text extraction is dependency-free. PDF text extraction uses PyMuPDF or pypdf only when already available. SQLite FTS5 is used for ranked full-text search when supported, with graceful fallback to LIKE search when unavailable. ZIM remains catalogued pending deliberate Kiwix/libzim integration.

Beast Studio import/open is constrained by file type, sanitized filename/path handling, size limits, private storage and non-execution of imported documents.

## 4. Beast Operator privilege sessions
Operator privileges are represented by a real owner-authorized Beast session rather than caller-supplied claims. Sessions support Observer, Operator, Maintainer and Administrator tiers, have bounded lifetimes, expire automatically, can be revoked explicitly, and are auditable.

Structured tools consult the active session. A caller cannot obtain Administrator authority by merely supplying a string. The Action Broker remains the mutation boundary.

## 5. Structured Operator tools
AI/automation uses structured Beast tools rather than a hidden unrestricted shell. Current capabilities include state/search/library/incident/job reads, action planning, allow-listed service restart, verified backup creation, plugin transactions, enrolled-container control, support-bundle creation, and recovery staging/planning. Broad shell authority is not exposed as a normal tool.

## 6. Recovery Center boundary
v0.18 implements:

`backup -> verify -> stage -> dry-run restore plan`

Backup verification checks archive boundaries, rejects links, validates the manifest, verifies SHA-256, and runs SQLite `quick_check` on the embedded Beast database. Staging extracts only into an isolated restore area. Dry-run planning compares staged content against live managed targets and reports create/replace/unchanged outcomes.

v0.18 intentionally does **not** apply a live restore. A future restore transaction must include a rescue backup, service quiesce ordering, verification and rollback.

## 7. Mission Packs
Mission Packs are declarative user/shareable bundles of intent. They may define description, preferred Context Deck/theme/layout, checklist, Field Library tags/documents, capability requirements, suggested apps and safe structured actions. Mission Packs do not embed arbitrary shell commands.

Built-in examples include Field Survey, Road Trip, Lab Diagnostics and Home Base. Capability requirements are evaluated against the actual machine so unavailable hardware is surfaced truthfully.

## 8. Living-Beast personality state
Beast Core derives canonical personality/expression state from real conditions including health, Pwnagotchi/Bettercap state, governor/thermal condition, GPS status, Expedition activity, AP discovery activity, recent captures, time-of-day, CPU load and progression state.

Canonical outputs include expression/state plus underlying energy, curiosity, focus, confidence and stress values. Face Engine prefers canonical Beast expression and falls back to native Pwnagotchi mood when Beast personality state is unavailable.

## 9. Optional workload and whole-Pi capabilities
Container Center remains capability-driven and does not install Docker/Podman automatically. Arbitrary containers are visible read-only; mutation is limited to explicitly Beast-enrolled containers. Bluetooth, Pi clocks/GPU memory, display/DRM outputs and other capabilities remain observational unless the user deliberately enables a corresponding module.

## 10. Release boundary
v0.18 does not claim:
- fully migrated native-responsive layouts for every legacy Beast page;
- one-click live disaster restore;
- a local LLM runtime installed by default;
- unrestricted AI shell/root authority;
- automatic container installation;
- automatic Bluetooth scanning.

Those remain later layers on the validated v0.18 platform boundaries.
