# Beast Pack SDK — v0.19

Beast Packs are optional capability/content bundles for Beastagotchi. The base
platform stays small and stable; Packs live in managed storage and enter through
the same inspect → verify → stage → install lifecycle.

## Start here

Every Pack archive contains exactly one root `manifest.json`. The archive may
optionally have a single top-level folder; intake normalizes that away.

Supported archives:

- `.zip`
- `.tar.gz`
- `.tgz`

The current intake limit is 128 MiB compressed, 512 MiB unpacked and 2048 archive
members. Symlinks, hard links, devices, absolute paths and path traversal are
rejected.

## Minimal manifest

```json
{
  "id": "my-pack",
  "label": "My Pack",
  "version": "1.0.0",
  "pack_type": "theme",
  "resource_class": "none",
  "thermal_class": "static",
  "source": {
    "type": "github_release",
    "url": "https://github.com/owner/repository/releases",
    "channel": "stable"
  }
}
```

IDs use lowercase letters, numbers, dots, underscores and hyphens. Keep the ID
stable forever; versions change, identity does not.

## Current content-only activation tier

These classes may be enabled without executing Pack code:

`theme, face, animation, audio, layout, board, data, map`

This tier rejects executable/code-like files, executable permission bits,
privileged permission requests, background services and service restart
declarations.

Not every safe class has a consumer yet. **Theme, Board and Layout Packs are the
first fully connected v0.19 consumers.**

### Theme Pack

```
manifest.json
themes/
  orchard.json
```

Each theme filename must match its internal `id`. Built-in Beast theme IDs win
collisions.

### Board Pack

```
manifest.json
boards/
  field.json
```

A Board file is a dashboard destination:

```json
{
  "id": "field",
  "label": "Field Board",
  "widgets": [
    {
      "id": "cpu",
      "key": "system.cpu.total",
      "label": "CPU",
      "style": "radial",
      "x": 0, "y": 0, "w": 4, "h": 3,
      "min": 0, "max": 100
    }
  ]
}
```

Enabled Board Packs appear as **read-only launcher destinations**. Beast scopes
their runtime IDs by Pack so community boards cannot collide with personal
boards. Their telemetry still comes from canonical live Beast state.

### Layout Pack

```
manifest.json
layouts/
  triad.json
```

A Layout uses the same widget geometry as a Board, but it is a **template**.
Beast Studio shows enabled Layout Pack templates and imports one only when the
user explicitly asks. Importing creates a normal editable personal Board; the
Pack template remains untouched.

## Widget contract

The 480×320 reference Dashboard uses a 12×8 logical grid. Current generic widget
styles are:

- `metric`
- `bar`
- `radial`
- `microtrend`

A widget binds a canonical Beast telemetry key. Unknown/malformed fields are
normalized by Beast Studio rather than trusted blindly.

## Distribution

The recommended v0.19 distribution is a GitHub Release containing:

- the Pack archive;
- a SHA-256 sidecar asset.

Example:

```
field-layouts-1.0.0.zip
field-layouts-1.0.0.zip.sha256
```

A repository appearing in a Depot catalog does **not** automatically become a
trusted unattended-update source. Depot discoverability and source trust are
separate boundaries.

See the examples under `pack-sdk/examples/`.
