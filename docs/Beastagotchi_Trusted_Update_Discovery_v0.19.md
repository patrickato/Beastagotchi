# Trusted Update Discovery — v0.19

Beastagotchi now has a read-only update-awareness layer designed around the
future docked/connected workflow.

## Background checks

When the device is both:

- docked, and
- reporting Internet connectivity,

Beast Core may perform a bounded GitHub **release metadata** lookup for trusted
components. Checks are cached and rate-limited (default: once per hour).

No release archive is downloaded.

The metadata lookup runs in a worker thread so a slow network cannot block the
main Beast Core event loop.

## Built-in trusted metadata sources

The initial built-in trust set is deliberately small:

- `patrickato/Beastagotchi`
- `Korrie71/pwnagotchi-theme-manager`
- `jayofelony/pwnagotchi`

A third-party Beast Pack does **not** become trusted just because its manifest
contains a GitHub URL.

Additional repositories can later be added to the local trust file:

`/var/lib/beastagotchi/ui/trusted_sources.json`

Example:

```json
{
  "github_repositories": [
    "author/project"
  ]
}
```

## What Beast records

For each supported component Beast can expose:

- installed version
- latest release tag
- whether the latest tag appears newer
- metadata check time/result
- whether the source is trusted
- whether the release exposes a SHA-256 digest or sidecar path
- the user's update policy
- whether the component is eligible for future auto-staging

## Important distinction

`auto_stage_eligible=true` means the metadata satisfies the current prerequisites
for a *future* verified download/staging implementation.

It does **not** mean Beast can download it today.

Remote download execution and automatic installation remain locked.

## Why explicit trust matters

Community growth means Beastagotchi may eventually know about many repositories.
Silently making every repository named by a downloaded manifest part of an
automatic update supply chain would be unsafe. Discovery and trust are therefore
separate decisions.

The intended future path is:

trusted metadata → verified asset download → safe staging → transactional install
→ pack-type activation → live probation → commit/rollback.
