# Beastagotchi Update Manager Spec v0.1

## Goal
Safely keep selected Beastagotchi components, approved Pwnagotchi plugins and companion tools current when network access is available, especially while docked.

## Policy per component
Each enrolled component has one policy:
- `manual`
- `notify`
- `auto_stage`
- `auto_install`

Default third-party software to `notify` or `auto_stage`, not blind `auto_install`.

## Supported source types
- GitHub Releases/tags
- pinned Git commits
- project-specific release manifests
- Debian/apt packages where appropriate
- Pwnagotchi plugin repositories

## Safe update transaction
1. Check connectivity and policy trigger.
2. Fetch metadata only.
3. Compare installed/source version and compatibility constraints.
4. Download into staging; never update live files in place.
5. Verify checksum/signature when provided.
6. Static conflict scan and dependency check.
7. Create Beast recovery backup/config snapshot.
8. Run package/plugin self-tests in staging when available.
9. Generate an action plan and affected-service restart graph.
10. Install atomically or via versioned directory/symlink where possible.
11. Restart only required services.
12. Observe health for a configurable probation window.
13. Commit success or automatically roll back.
14. Write a structured update log and incident on failure.

## Triggers
- Dock transition + internet available.
- Scheduled daily/weekly check.
- Manual `Check for updates` action.
- Optional startup check with rate limiting.

## UI
Update Center shows Installed / Available / Policy / Compatibility / Last checked / Last result. Users can pin versions, ignore releases, view release notes and roll back.

## Important rule
Never implement this as an unconditional `git pull && restart`. The Update Manager should treat every update as a transactional change using the same Beast Action Broker, backup and health machinery already built for plugins/services.
