# Beastagotchi Persistent Recovery & Logging Policy v0.1

## Requirement
Backups, rollback state, incidents, jobs/actions, support evidence and important logs must not exist only inside a browser/WebUI process. The WebUI and Beast UI are clients of persistent on-device records.

## Existing durable stores
- `/var/lib/beastagotchi/beast.db`
- `/var/lib/beastagotchi/backups/`
- `/var/lib/beastagotchi/config-snapshots/`
- `/var/lib/beastagotchi/restore-staging/`
- `/var/lib/beastagotchi/support/`
- `/var/lib/beastagotchi/library/`
- `/var/lib/beastagotchi/missions/`
- `/var/lib/beastagotchi/ui/`

Black Box incidents, durable jobs/action history and telemetry/history records should remain queryable even when Beast Studio is unavailable.

## Logging policy direction
Systemd/journald remains the primary raw service-log source where appropriate. Beast should provide bounded on-device log views/exports and Support Bundles rather than inventing unlimited duplicate logging. Persistent journal configuration and/or bounded Beast exports must be validated for the target image before becoming a default so SD-card write wear stays controlled.

## Recovery rule
Any future updater, plugin manager, Theme Manager integration, package installer or configuration editor that can materially change the running system must integrate with snapshot/preflight/health-check/rollback facilities rather than performing blind writes.
