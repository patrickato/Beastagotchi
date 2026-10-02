# Beastagotchi Depot Catalog Contract — v0.19

The Depot is a discovery index, not an app store that bypasses Beast's safety
gates.

A catalog may tell Beast that a Pack exists, what it is, and where its GitHub
Release artifacts are. It does **not** grant trust, download by itself, install,
activate, or execute anything.

## Catalog v1

```json
{
  "schema": 1,
  "channel": "stable",
  "generated_at": "2026-09-23T00:00:00Z",
  "packs": []
}
```

Each Pack entry contains identity/version/type plus a bounded GitHub Release
source:

```json
{
  "id": "field-layouts",
  "label": "Field Layouts",
  "version": "1.0.0",
  "pack_type": "layout",
  "description": "Reusable field telemetry compositions.",
  "author": "Example",
  "license": "MIT",
  "tags": ["field", "dashboard"],
  "resource_class": "none",
  "thermal_class": "static",
  "compatibility": {
    "beast_min": "0.19.0"
  },
  "source": {
    "type": "github_release",
    "repository": "owner/field-layouts",
    "asset": "field-layouts-*.zip",
    "sha256_asset": "field-layouts-*.zip.sha256"
  }
}
```

The v1 parser intentionally supports GitHub Releases only because Beast already
has a bounded release-metadata client, SHA-256 verified staging, and an explicit
trusted-source policy for that source type.

## Security boundary

Catalog metadata is untrusted input. Parsing is bounded to 1 MiB and 512 entries
by default. Invalid entries are isolated and reported rather than poisoning the
whole catalog.

Even a valid entry has:

- `grants_trust = false`
- `installs_packs = false`

Unattended metadata checks/downloads remain subject to `TrustedSourcePolicy`.
Pack archives still pass through the normal intake, verification, staging,
transactional install and activation gates.

This means a public/community Depot can grow without turning a catalog maintainer
into a root-of-trust for the device.
