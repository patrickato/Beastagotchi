# Beast Pack Transactional Install / Rollback — v0.19

This milestone advances Beast Packs from **verified staging** to a persistent,
transactional installed-pack registry.

It deliberately does **not** cross the activation boundary.

## Current lifecycle

```
archive
  → inbox
  → inspect
  → verified staging
  → INSTALL PLAN
  → rescue snapshot (when replacing an installed version)
  → inert installed registry
  → structural probation / verification
  → transaction journal

future:
  → pack-type activation plan
  → service/config/display changes
  → live health probation
  → commit or automatic rollback
```

## Transaction guarantees

Each registry install receives a transaction ID and durable
`transaction.json` record under:

`/var/lib/beastagotchi/packs/transactions/`

When replacing an existing pack, the previous registry copy is retained as a
pack-local rescue payload. The newest rollback payloads are retained; older
payloads may be pruned while their transaction journals remain.

The installer checks:

- verified staging state
- capability requirements
- pack dependencies
- enabled conflicts
- declared Beastagotchi/Pwnagotchi version bounds
- manifest identity before and after copy
- installed state marker
- installed transaction marker
- post-copy file-tree digest

If the install fails after work begins, it attempts to restore the previous
registry copy automatically.

Manual rollback is permitted only when the transaction being rolled back is the
one currently installed. This prevents an old rollback request from overwriting a
newer pack version.

## Still intentionally locked

"Installed" currently means **managed by Beast**, not **running**.

Registry installation does not:

- import or execute Python
- run shell scripts
- install apt/pip dependencies
- enable Pwnagotchi plugins
- start/restart services
- register systemd units
- alter framebuffer/touch ownership
- add network listeners

Those effects require future pack-type-specific activation adapters using the
Action Broker, pre-change recovery backups and real service-health probation.

## WebUI direction

Beast Studio is the intended workshop for this lifecycle. Local uploads are
bounded to the pack inbox and privileged verification/install/rollback goes
through the Unix-socket Action Broker. The browser never receives arbitrary
filesystem or shell privileges.
