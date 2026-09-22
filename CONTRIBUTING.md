# Contributing to Beastagotchi

Thank you for helping Beastagotchi grow. The project values practical testing, clear documentation, reversible changes and respect for the protected Pwnagotchi/Bettercap engine underneath Beast Core.

## Branch model

- `main` — validated public baseline and release-ready integration points.
- `develop` — active integration branch once established.
- `feature/<short-name>` — isolated work intended for review before integration.
- `fix/<short-name>` — focused corrective work.
- `docs/<short-name>` — documentation-only changes.

Small documentation corrections may target `main`; runtime changes should normally go through a feature/fix branch and pull request.

## Before changing code

Read:

1. `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
2. `docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md`
3. `docs/Beastagotchi_Master_Completion_Matrix_v4.7.md`
4. `docs/DEVELOPMENT_WORKFLOW.md`
5. any subsystem specification relevant to your change.

## Architectural expectations

- Keep invasive Pwnagotchi changes to an absolute minimum.
- Prefer Beast Core collectors/adapters and independent services.
- Visual code must not directly execute arbitrary privileged shell commands.
- Privileged mutations belong behind typed, audited Beast Core actions.
- Preserve truthful unavailable/stale states instead of inventing values.
- Keep data sources, widgets, renderers, layouts, themes and animations separable.
- Do not let multiple systems race for framebuffer or touch ownership.
- Optional modules should remain capability-driven and idle when unavailable/not selected.
- Preserve local recovery paths and rollback behavior.
- Do not silently remove planned scope. Update the continuity ledger/matrix when a design decision changes it.

## UI contributions

The 480×320 ADS7846/XPT2046 resistive screen is the fully validated reference platform, not the permanent display ceiling.

For physical UI work:

- use large touch targets;
- separate visual geometry from touch geometry;
- maintain clear information hierarchy;
- avoid forcing deep configuration onto the small TFT;
- support responsive scaling/layout primitives rather than per-resolution forks where practical;
- keep the Beast/Home experience recognizable;
- test off-screen first, then on physical hardware when the change is visually or interactively meaningful.

## Tests

Run at minimum:

```bash
python3 -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
python3 -m compileall -q beastcore beastui beaststudio
bash -n install.sh install_ui.sh install_bridge.sh uninstall.sh validate_v018.sh
```

If your change affects the framebuffer, touch, service lifecycle, Bettercap/Pwnagotchi integration or hardware, state what you tested on real hardware in the pull request.

## Privacy

Never commit or attach:

- credentials/API keys/tokens;
- private configuration;
- raw packet/capture files;
- real SSIDs/BSSIDs/client MAC addresses;
- exact GPS traces/coordinates from private use;
- unsanitized support bundles;
- personal hostnames/device names when avoidable.

Tests should use obviously synthetic identifiers.

## Pull requests

A useful PR explains:

- what problem it solves;
- which subsystem(s) it touches;
- whether it changes persistent data/config formats;
- test results;
- hardware validation performed, if applicable;
- rollback/recovery considerations;
- thermal/resource impact for long-running work;
- continuity/roadmap implications.

## New ideas are welcome

A feature does not need to fit the current milestone to be worth preserving. If it is useful but not ready to implement, add it to an issue or the appropriate roadmap/continuity document rather than forcing it into unrelated code.
