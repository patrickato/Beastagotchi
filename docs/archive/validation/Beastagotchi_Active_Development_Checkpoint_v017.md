# Beastagotchi Active Development Checkpoint — v0.17 release-candidate branch

Status: feature-frozen; clean-package gate in progress. Do not deploy until final archive passes exact-archive validation.

Validated inherited base: v0.16.0 target archive audited on physical Pi.
Current automated suite: 185/185 passing.
Current validation gallery: 30 reference 480×320 frames + 640×480 and 800×480 compatibility proofs, all correct-size and nonblank.

Completed since v0.16:
- semantic Core startup health/readiness and immediate plugin inventory reconciliation
- display compatibility transform (480×320 logical canvas to arbitrary physical output + reverse touch mapping)
- Studio selectable 480×320 / 640×480 / 800×480 compatibility previews with non-reference warnings
- richer Field Library extraction (EPUB, optional PDF extractors)
- ranked FTS5 Field Library search when available with graceful fallback
- safe authenticated Field Library upload/open through Beast Studio
- structured Beast Operator tool registry with privilege tiers and no generic shell primitive
- explicit Beast-managed container control boundary
- Bluetooth capability telemetry
- cached Pi ARM/core clock + GPU-memory telemetry
- privacy-sanitized Support Bundle action/job and Studio control
- read-only recovery backup verification: path/link/manifest/SHA-256/SQLite integrity, without restore apply

Explicitly NOT claimed in v0.17:
- native responsive 640×480/800×480 layouts
- one-click restore/disaster recovery
- local AI runtime installed by default
- unrestricted always-on root shell for AI
- automatic Bluetooth scanning
- automatic Docker/Podman installation

Next step: clean staging -> exact archive -> fresh extraction -> tests/compile/syntax/gallery -> physical target validator only if all pass.
