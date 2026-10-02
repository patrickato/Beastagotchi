# Beastagotchi v0.4 Target Validation Report — 2026-09-20

## Result: PASS

The v0.4 target archive validated the Beast Core and the off-screen Beast UI runtime on the actual Raspberry Pi 4 environment without touching the physical framebuffer.

## Core state

- `/health`: `ok=true`, `state=healthy`
- 173 live state keys
- 0 stale keys
- 0 unavailable keys
- Beast Core, Pwnagotchi, Bettercap and gpsd were all active in the captured service state.
- No Beast Core crash or collector exception was present in the captured journal.

## UI runtime

- Target Python: 3.13.5
- Pillow: 11.1.0
- NumPy: 2.5.2
- Classic render: 480×320 RGB
- Black Ice render: 480×320 RGB

The compositor therefore passed the real target interpreter/library/runtime gate at native panel resolution.

## Pwnagotchi bridge

The bridge was live at capture time and continued to deliver:

- Wi-Fi update callbacks
- channel-hop callbacks
- epoch callbacks
- mood callbacks

The sampled bridge state included 10 filtered APs, 9 filtered clients and current channel-hop information. This confirms that the UI handoff can disable only Pwnagotchi's LCD rendering while preserving the engine/bridge path.

## GPS observation

The semantic event capture showed a very short `gps.lock_acquired` → `gps.lock_lost` transition. The acquisition sample had no useful satellite/accuracy payload. This is consistent with a momentary gpsd fix-state wobble and is too noisy for a visual/event system.

v0.5 therefore adds semantic GPS debounce:

- acquire: 3 seconds stable fix
- loss: 5 seconds stable no-fix
- automatic context preserves the previous movement presentation during the short grace interval

This affects presentation/event stability only; raw GPS state remains available.

## Thermal observation

The sampled CPU temperature history ranged approximately 68.2–70.1 °C during the validation window. This is in the current Beast `warm` band and did not indicate a service failure.

## Decision

Gate D off-screen validation passes. The next gate is controlled physical framebuffer ownership using a timed, automatically reversible handoff.
