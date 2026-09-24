# Installation — Current Pre-1.0 Development Build

Beastagotchi is not yet a one-click production appliance. The current installer intentionally stages components so testers can validate them before the project takes over the physical display.

## Reference environment

The most completely validated target so far is:

- Raspberry Pi 4 Model B, 8 GB
- 64-bit jayofelony Pwnagotchi image / Debian 13 era environment
- Pwnagotchi 2.9.5.9
- Python 3.13
- 480×320 ILI9486 SPI framebuffer (`fb_ili9486`)
- ADS7846/XPT2046-class resistive touch
- local Bettercap and gpsd where available

See `Beastagotchi_Platform_Compatibility_Spec_v0.18.md` for what is proven versus merely designed.

## Safety before installation

- Have SSH access.
- Back up `/etc/pwnagotchi/config.toml` and any custom plugin/config directories you care about.
- Confirm Pwnagotchi and Bettercap are healthy before introducing Beastagotchi.
- Do not perform the physical display handoff until off-screen validation succeeds.

## Beast Core

From a checked-out repository on the Pi:

```bash
sudo ./install.sh
sudo systemctl start beast-core
sleep 10
curl -s http://127.0.0.1:8090/health | python3 -m json.tool
```

The installer preserves the existing Beast SQLite database and does not automatically enable/start the service.

## Optional Pwnagotchi callback bridge

```bash
sudo ./install_bridge.sh
```

This installs/enables the read-only callback bridge configuration but deliberately does **not** restart Pwnagotchi for you. Review the config backup and restart only when ready.

## Beast UI / Studio

```bash
sudo ./install_ui.sh
```

The installer refuses to pretend a missing touch calibration exists and keeps physical UI ownership disabled.

Off-screen smoke test:

```bash
sudo -u pi PYTHONPATH=/opt/beast-ui \
  /opt/.pwn/bin/python3 -m beastui \
  --root /opt/beast-ui \
  --output /tmp/beast-ui-test.png \
  --duration 2
```

## Target validation

For the v0.18.1 baseline:

```bash
sudo ./validate_v018.sh
```

Review the returned validation archive before using the reversible display handoff tools in `display_handoff/`.

For the active v0.19 branch, the UI installer also installs the bounded physical-acceptance harness. After off-screen/source checks are green, the reference-TFT session starts with:

```bash
sudo beast-v019-accept start 15
```

During the physical session, collect a one-minute objective sample while using the TFT:

```bash
sudo beast-v019-accept sample 60
```

Finish with an explicit ownership decision:

```bash
sudo beast-v019-accept finish observe
sudo beast-v019-accept finish pass
sudo beast-v019-accept finish rollback
```

`observe` only bundles evidence; `pass` calls the existing display confirmation path; `rollback` captures evidence then restores Pwnagotchi display ownership. See `Beastagotchi_v019_Physical_Acceptance_Package.md` for the complete gate and evidence boundary.

## Upgrades

Until Update Manager/migrations are finalized, treat upgrades as explicit versioned deployments. Do not use an unattended `git pull && restart` workflow on a field device.
