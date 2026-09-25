# Beastagotchi v0.19 — Beast Packs / Update Policy Foundation Checkpoint

## What this milestone adds
- Read-only Beast Pack manifest registry.
- Lifecycle visibility for builtin / installed / staged packs.
- Capability, dependency and enabled-conflict blockers.
- Declared resource class and thermal class for every pack.
- Source URLs are sanitized before presentation.
- Update-policy intent for Beastagotchi, Pwnagotchi, Theme Manager and installed packs.
- Policies: manual / notify / auto_stage / auto_install.
- Beast Studio Packs / Update Center surface.
- Policy file is local, atomic and mode 0600.
- Pack installer and update executor remain locked.

## Important safety boundary
Selecting auto_install in v0.19 records the user's future intent only. It cannot
download or install anything. Execution remains disabled until metadata checking,
verified staging, compatibility scanning, backup, health probation and rollback
are implemented through the Action Broker.

## Resource rule
Inactive packs do not gain a runtime merely because they are cataloged. Future
pack installers must preserve this rule.

## Next
1. Build source-metadata checker without installation.
2. Add signed/checksummed staging format.
3. Connect backup/config snapshot plan.
4. Add dependency/conflict planner.
5. Add probation + rollback transaction.
6. Only then enable optional automatic execution.
