# Beastagotchi Platform & Compatibility Specification v0.17

## Purpose
v0.17 converts the v0.16 Operations/Knowledge foundation into a more portable and owner-operable platform without weakening the protected Pwnagotchi/Bettercap engine. The milestone focuses on truthful startup readiness, display portability, offline knowledge usability, structured Operator tools, optional workload boundaries, Pi hardware telemetry, and privacy-safe troubleshooting.

## 1. Startup truthfulness
Beast Core distinguishes STARTING from DEGRADED. Concurrent collectors are allowed a finite startup grace; a never-successful collector becomes degraded after that grace. Critical Pwnagotchi, Bettercap, or read-only-root failures become CRITICAL. Target validation must wait for semantic readiness rather than treating an open HTTP port as a completed boot.

Plugin integration is refreshed immediately when the Pwnagotchi collector publishes its inventory so Plugin Manager cannot briefly expose a misleading empty catalog after restart.

## 2. Display compatibility boundary
480×320 remains the validated reference/minimum UI canvas. Beast now separates the logical Beast canvas from the physical output surface.

`logical canvas -> DisplayTransform -> physical surface`

DisplayTransform supports aspect-preserving fit, explicit stretch for diagnostics, centered letter/pillar bars, selectable resampling, and reverse physical-touch mapping into logical Beast coordinates. Touches in compatibility bars are ignored.

Compatibility proofs at 640×480 and 800×480 are deliberately **not** claims of native responsive layout support. Beast Studio labels them as compatibility-scaled output and keeps spatial layout editing on the 480×320 reference canvas until the responsive layout engine is implemented.

## 3. Field Library
Field Library remains offline-first. Text, Markdown, config, HTML and related text formats are directly indexed. When SQLite FTS5 is available, ranked full-text search is used; custom SQLite builds without FTS5 fall back to the existing LIKE search path rather than breaking the library. EPUB extraction is dependency-free. PDF text extraction uses PyMuPDF or pypdf only when already available; otherwise the document remains catalogued instead of forcing a package onto the protected image. ZIM remains catalogued pending deliberate Kiwix/libzim integration.

Beast Studio supports authenticated local import/open for a constrained document whitelist. Imports are filename-sanitized, path-traversal resistant, size-limited, atomically written, private by default, and never executed.

## 4. Beast Operator tool surface
AI integration uses structured Beast tools rather than a hidden generic shell. Tool access is privilege-tiered (Observer / Operator / Maintainer / future owner-authorized Administrator session). Current structured capabilities include state/search/library/incident/job reads, action planning, allow-listed service restart, verified backup creation, plugin transaction, enrolled-container control, and sanitized support-bundle creation.

The absence of a generic `shell.exec` primitive is intentional. A future broad administrative session must be explicit, owner-authorized, time-limited and audited.

## 5. Optional workload isolation
Container Center remains capability-driven. Docker/Podman is never installed merely because Beast supports it. If a runtime exists, arbitrary containers are visible read-only. Mutation is permitted only for containers explicitly enrolled with a Beast-managed label. This creates a future isolation boundary for optional/community workloads without moving Pwnagotchi, Bettercap or Beast Core into containers.

## 6. Whole-Pi capability telemetry
Beast now exposes read-only Bluetooth adapter state without automatically scanning and samples Pi ARM/core clocks plus GPU memory through cached low-frequency reads. Observability must not become the reason the device runs hot.

## 7. Support bundles
The owner can create a privacy-sanitized Support Bundle through the Action Broker/Task Center/Beast Studio. Default bundles intentionally omit SSID/BSSID/client identities, GPS coordinates, IP/MAC identifiers, credentials, raw Pwnagotchi configuration and raw logs. The resulting private archive is retained with bounded history and SHA-256 metadata.


## 8. Recovery verification
Recovery archives can be inspected without restoring them. Verification is constrained to Beast backup roots and checks archive path boundaries, disallows links, validates the manifest format, calculates SHA-256, and runs SQLite `quick_check` on the embedded database snapshot. v0.17 intentionally stops at **ready to stage**; no verified archive is automatically applied over the live system.

## 9. Release boundary
v0.17 does not claim:
- native responsive 640×480/800×480 layouts;
- a local LLM runtime installed by default;
- automatic Bluetooth discovery/scanning;
- automatic container installation;
- unrestricted AI shell/root authority;
- one-click disaster restore.

Those remain deliberate later layers on top of the now-established boundaries.
