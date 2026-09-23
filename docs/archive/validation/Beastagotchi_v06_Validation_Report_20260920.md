# Beastagotchi v0.6 Target Validation Report — 2026-09-20

## Result
PASS for the off-screen/target-runtime gate.

- Beast Core health: healthy
- State keys: 225
- Live: 225
- Stale: 0
- Unavailable: 0
- All six structural themes rendered successfully at 480×320 on the target Pi.
- Collector health: all collectors reported `ok` in the captured state.
- Ethernet: `eth0` up, 1 Gbit/s link, default route active.
- Home Dock profile: not yet enrolled (expected).
- Physical framebuffer was not touched during this validation.

## Hardware findings

### Power / Waveshare UPS Module 3S
- `/dev/i2c-1` exists, so Raspberry Pi I2C is enabled.
- The v0.6 power collector did not see an INA219 at its original probe addresses (0x41/0x40).
- v0.6.1 expands the safe probe set to 0x41, 0x40 and 0x42 because Waveshare variants/examples are found at those addresses.
- If v0.6.1 still reports `not_detected`, treat this as a physical telemetry-wiring issue (SDA/SCL/common ground) rather than a Beast Core failure.
- Dock remains FIELD until external power telemetry is trustworthy and the home network is enrolled.

### USB / capabilities
Present during the validation:
- u-blox 7 GPS (`1546:01a7`)
- USB hub
- framebuffer/display capability
- I2C capability

Not attached during the capture:
- ALFA AWUS036ACM
- RTL-SDR
- TP-Link Wi-Fi adapter
- Edimax Wi-Fi adapter
- ASUS Bluetooth adapter

Those devices therefore remain runtime-enrollment items rather than assumptions.

## System observations
- Pi: Raspberry Pi 4 Model B Rev 1.5
- RAM: ~7.8 GB usable; only ~456 MB used in the captured state (~5.8%).
- CPU: ~35% at capture.
- CPU temperature: 74.5°C; thermal band `warm`; throttle flags `0x0`.
- Root filesystem: ~11.8% used with ~110 GB free.

The thermal number reinforces the Resource Governor plan: cosmetic load should scale down before core radio/GPS/data services are affected.

## v0.6 validator issue
The original target validator attempted to run pytest even though pytest is a development-only dependency. The user patched the validator as instructed; target tests were intentionally skipped while the package had already passed the complete test suite before distribution. v0.6.1 permanently removes that target dependency.
