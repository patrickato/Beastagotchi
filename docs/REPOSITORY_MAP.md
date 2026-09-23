# Repository Map

## Runtime code

### `beastcore/`
Canonical state, persistence, events, collectors, actions, backup/recovery, progression, incidents, missions, operator policy/tools, plugin/service/container brokers and support bundles.

### `beastui/`
Physical UI engine, framebuffer writer, touch input, pages/apps, themes, native Pwnagotchi bridge presentation, reactions, responsive primitives and widget renderers.

### `beaststudio/`
Responsive local WebUI, action client and local library-file access surface.

### `pwnagotchi_plugin/`
`beast_bridge.py`, the deliberately small read-only callback bridge from Pwnagotchi into Beast Core state.

## System integration

- `config/` — Beast Core/touch reference configuration.
- `systemd/` — Beast Core service.
- `ui_systemd/` — Beast UI and Beast Studio services.
- `display_handoff/` — physical display ownership claim/release/rollback validation.
- `tools/` — diagnostics, render galleries, touch/calibration, display-conflict and support utilities.

## Validation

- `tests/` — source/unit/regression tests.
- `validate_v*.sh` — target validation collectors for specific development milestones.
- `docs/archive/validation/` — historical human-readable source/target/physical validation evidence.

## Documentation

Current/authoritative specifications and milestone documents stay directly in `docs/`.
Clearly superseded roadmaps, matrices, checkpoints, drafts and validation reports
belong under `docs/archive/` so the active documentation root stays readable.

Do not archive a file merely because its version number is old: if current runtime,
installers, tests or active documentation still depend on its exact path, keep it
active until those references are migrated safely. Use `docs/README.md` as the
navigation/source-of-truth layer.
