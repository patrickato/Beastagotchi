# Verified Update Staging — v0.19

Beastagotchi's Update Center now has a third safety layer:

1. trusted release metadata discovery
2. **verified release download staging**
3. future component-specific application

Only step 2 is added by this milestone.

## Trust boundary

The stager accepts GitHub release assets only when the component repository is
present in Beast's trusted-source policy.

A release asset URL must begin as HTTPS on `github.com`. Redirects are limited
to GitHub's release-asset infrastructure.

The Pwnagotchi platform image is deliberately excluded from the generic stager;
it needs its own image/platform update adapter.

## SHA-256 is mandatory

A remote archive is not staged unless Beast can establish an expected SHA-256
from either:

- GitHub release asset digest metadata (`sha256:...`), or
- a matching SHA-256 sidecar asset.

The downloaded bytes are hashed before they are moved into the durable staging
area. A mismatch aborts the transaction.

## Staging location

Verified remote updates live below:

`/var/lib/beastagotchi/updates/staged/<component>/<version>/`

Each staged artifact receives private `metadata.json` recording repository,
version, asset name, size, SHA-256 and verification time.

## Still not an updater executor

A successfully staged update has:

- `verified = true`
- `installed = false`
- `executed = false`

No current service is stopped or restarted and no live software tree is
modified.

Beast Studio may expose **STAGE VERIFIED UPDATE** when a trusted component has a
newer release with an acceptable archive and SHA-256 verification path.

Automatic policy-driven staging and actual update application remain later
gates.
