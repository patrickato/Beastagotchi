# Policy-Driven Auto-Staging — v0.19

The Update Center now honors the user's auto_stage policy for update artifacts
that already pass the trusted-source and SHA-256 eligibility rules.

Automatic staging requires both docked state and Internet connectivity reported
as online, reachable, or up.

The metadata checker remains rate-limited. The automation loop runs at low
frequency and stages at most one remote artifact per pass to avoid update
bursts, unnecessary heat, and SD-card churn.

Policy behavior:

- manual: no automatic download
- notify: report update only
- auto_stage: download, SHA-256 verify, and stage
- auto_install: currently performs the same safe staging step, then records
  install pending

The last point is intentional. Auto-install is user intent, not permission for
Beast to improvise an unsafe component installer.

Automation de-duplication and retry state is stored in:

/var/lib/beastagotchi/updates/automation.json

Each attempt records component, version, policy, time, Action Broker ID,
staged path/SHA-256 on success, failure detail, and whether installation remains
pending.

Automatic staging invokes the same structured update.stage Action Broker action
as a manual WebUI request, with actor automation:update, so the operation is
preserved in durable action/event history.

Actual auto-install remains locked until each runtime component has an explicit
rescue-backup, mutation, restart, health-probation, and rollback adapter.
