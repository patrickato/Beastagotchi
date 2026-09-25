# Testing and Validation Model

Beastagotchi deliberately separates three levels of validation.

## 1. Source / CI validation

Runs on a normal development machine and proves imports, deterministic logic, parsers, persistence, APIs, render generation and shell syntax without claiming real Pi hardware behavior.

```bash
python3 -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
python3 -m compileall -q beastcore beastui beaststudio
bash -n install.sh install_ui.sh install_bridge.sh remove_bridge.sh uninstall.sh validate_v018.sh tools/v019_physical_acceptance.sh
```

## 2. Target Pi off-screen validation

Runs Beast Core/UI/Studio on the actual Pi/Pwnagotchi environment while leaving the physical display owner unchanged. This validates real collectors, services, callbacks, APIs and off-screen rendering without risking the known-good TFT presentation.

Use the milestone validator appropriate to the runtime baseline (`validate_v018.sh` for v0.18.1).

A target validation archive should be reviewed before physical display ownership is changed.

## 3. Physical interaction gate

Used when a change materially affects what the user sees/touches or when framebuffer/touch ownership changes.

Physical gates evaluate things automated render tests cannot fully prove:

- readability at actual physical size;
- resistive touch hit accuracy;
- navigation feel;
- animation artifacts/Moiré/flicker;
- framebuffer ownership/recovery;
- transition behavior;
- thermal impact over realistic use.

## v0.19 bounded physical package

For the active v0.19 branch, the physical interaction gate is packaged as one
reversible session:

    sudo beast-v019-accept start 15

While using the TFT normally, collect an objective window:

    sudo beast-v019-accept sample 60

Then bundle the session with an explicit ownership decision:

    sudo beast-v019-accept finish observe
    sudo beast-v019-accept finish pass
    sudo beast-v019-accept finish rollback

The generated summary includes render/compose/framebuffer-write timing, changed
rows, bytes written, temperature, CPU/governor state, touch evidence and
Capsule/QR availability. It explicitly does not decide readability, touch feel,
phone-camera scan reliability or overall physical polish for the user.

See `Beastagotchi_v019_Physical_Acceptance_Package.md`.

## Rule

Passing source tests does **not** mean physical hardware is validated. Passing an off-screen Pi test does **not** mean a display/touch change should be enabled automatically.
