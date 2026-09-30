# Beastagotchi Linux/Tooling Refinements

**Date:** 2026-09-27  
**Status:** owner decisions / candidate refinements

## Approved/refined directions

1. Software/Abilities Catalog should be broad and user-choice driven. Populate it with useful programs, libraries, dependencies and categories. Beast may surface compatibility/trust/dependency impact, but should not artificially restrict what the owner may install/use through Owner Space.
2. Guided Software remains a strong general pattern.
3. One-click install/download catalog modeled loosely on Ninite-style ease is approved conceptually.
4. Guided Terminal should not become an overbuilt teaching shell. Prefer mature terminal enhancements and integrate them where they materially improve usability.
5. Full terminal access inside Beastagotchi remains preferred.
6. Contextual command explanation should be opt-in/non-annoying.
7. Live progress should remain visible in the originating page; Task Center is for backgrounded work.
8. Prefer mature existing tools over rebuilding equivalent functionality from scratch.
9. Free/low-cost online storage/database options should be investigated for Global Doctor/public metadata/indexes/shared resources before assuming paid hosting.
10. Browser/PWA cache remains a valid auxiliary cache/provider, not a sole durable store.
11. Field Readiness and enhanced Rebuild Manifest staging are deferred for later development.
12. Workshop Project archival/share remains after-release work.
13. User-registered scripts/tools remain a strong open-platform idea.
14. Beast's strongest identity in this cluster remains: translate user intent into the appropriate Linux/Pi/Pwnagotchi tool/capability, while retaining direct access to the full underlying software.

## Terminal enhancement candidates

Prefer integrating mature shells/enhancers rather than inventing a terminal parser from scratch.

Candidate options to evaluate:
- Bash + `ble.sh` for syntax highlighting, autosuggestions/completion improvements and interactive editing while retaining Bash semantics.
- Zsh + `zsh-syntax-highlighting` and optional autosuggestions for a richer interactive shell, without changing scripts that explicitly invoke Bash.
- Fish shell as an optional user shell because syntax highlighting, suggestions and completion are built in; evaluate compatibility/learning implications before making it a default.
- WebUI terminal front end such as xterm.js-style rendering can provide color, resizing and mobile/desktop UX while the backend remains a normal PTY/shell.

Guided Terminal should add only Beast-specific value such as:
- contextual task shortcuts;
- optional Explain action;
- links to docs/Doctor/Search;
- easy SSH host selection;
- clear working-directory/context presentation;
- large-screen handoff from TFT.

## Free/shared backend direction

Investigate a composable free-first architecture rather than one giant hosted backend. Potential split:

- static/public project content and indexes: GitHub repositories/releases/Pages where appropriate;
- structured Doctor/fleet/public metadata: free-tier hosted database/serverless service;
- larger immutable public assets: object storage/release assets/CDN where free quotas permit;
- user-private data: user-selected storage destinations; do not centralize private data by default;
- Beast clients cache/index relevant subsets locally.

Doctor Collective should prefer compact structured case/baseline records rather than raw log uploads, keeping storage/bandwidth manageable.

Exact provider selection remains open pending current-service/free-tier review and implementation needs.
