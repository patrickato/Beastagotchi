# Beastagotchi v0.7 Physical Validation Report — 2026-09-20

## Result

**PASS.**

The v0.7 physical archive confirms the six-theme/touch/display platform remains stable on the real Pi while Beast UI owns the LCD and Pwnagotchi continues underneath it.

## Beast Core

Captured `/health`:

- state: healthy
- canonical keys: 231
- live: 231
- stale: 0
- unavailable: 0

## Display / UI

- Beast display ownership was confirmed.
- Saved theme was Matrix.
- Physical framebuffer capture was valid at the expected display.
- Touch calibration remained present.
- No display-ownership rollback was active.

## System snapshot

- CPU temperature: 75.47 C
- CPU usage: ~51%
- memory used: 6.16%
- throttling flags: `0x0`

The system was warm but not throttling. This supports the Resource Governor plan: decorative visual load should be the first thing reduced under thermal pressure.

## Radio / Pwnagotchi

- primary monitor interface remained in monitor mode
- current channel in capture: 6
- Pwnagotchi remained active underneath Beast UI

The display takeover therefore did not break the protected Pwnagotchi/Bettercap radio engine.

## Ethernet / Dock / Power

- Ethernet carrier: true
- Ethernet speed: 1000 Mbps
- Dock state: field
- UPS telemetry: not detected
- external power state: unknown

This is expected until the home Ethernet profile is enrolled and the Waveshare UPS telemetry link is physically available to the Pi.

## Follow-up in v0.8

- UI API/history work moves out of the composition loop.
- Runtime timing separates composition from framebuffer-write time.
- Progression/Beast DNA becomes persistent.
- Lifetime Wi-Fi encounters become durable.
- Spectrum gets switchable renderers.
- Reaction priority prevents cosmetic effects from masking more important events.
