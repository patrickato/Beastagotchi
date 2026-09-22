# Beastagotchi Resource Governor Specification v0.11

## Purpose

Keep Beastagotchi visually rich without allowing optional presentation work to endanger the protected Pwnagotchi/Bettercap/GPS/data path on the Pi 4.

## Modes

| Mode | UI budget | FPS cap | Ambient | Foreground effects | Rare cinematic | History interval |
|---|---:|---:|---|---|---|---:|
| FULL | 100% | 18 | yes | yes | yes | 1.0× |
| GUARDED | 75% | 10 | yes | yes | yes | 1.0× |
| REDUCED | 45% | 6 | yes | no | no | 1.5× |
| SURVIVAL | 20% | 3 | no | no | no | 2.5× |

Escalation is immediate. Recovery is held for 20 seconds by default so a threshold boundary cannot make rendering oscillate every second.

## v0.11 pressure inputs

- CPU temperature: GUARDED at 70 C, REDUCED at 76 C, SURVIVAL at 80 C.
- CPU load: 75 / 90 / 97 percent.
- RAM use: 76 / 86 / 94 percent.
- battery estimate while on battery: 25 / 15 / 7 percent.
- current Raspberry Pi throttle/undervoltage bits force SURVIVAL.

`vcgencmd get_throttled` historical bits are published as history but **do not** force a live restrictive mode after the condition clears.

## Controlled consumers in v0.11

- Beast UI adaptive FPS cap
- temporary theme/background/foreground effect shedding
- high-cost procedural Rare Moment presentation fallback
- time-series sampling interval scaling

Saved Theme Studio options are never overwritten by transient governor decisions.

## Deliberately not governed yet

Pwnagotchi, Bettercap, GPS, bridge callbacks and essential collectors are not stopped/throttled by this first governor. Later modules will declare explicit cost/priority/resource classes before the governor is allowed to manage them.

## Future expansion

Per-module CPU/RAM/I/O/radio/USB/power cost declarations, SD write budgets, dock-vs-field profiles, fan/power telemetry, heavy service admission and benchmark-derived cinematic/SDR policies remain planned.
