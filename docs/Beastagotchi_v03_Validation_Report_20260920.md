# Beastagotchi v0.3 Live Validation Report — 2026-09-20

## Result

**PASS.** Beast Core v0.3 and the Pwnagotchi Beast Bridge both operated successfully on the target Raspberry Pi 4.

## Verified on hardware

- Beast Core HTTP health endpoint reported `healthy`.
- 159 canonical/state-health keys were live; 0 stale and 0 unavailable at collection time.
- WebSocket handshake succeeded and delivered a `hello` frame containing 159 state keys.
- Pwnagotchi Beast Bridge loaded under Pwnagotchi 2.9.5.9 and delivered real callbacks:
  - `loaded`
  - `epoch`
  - `ready`
  - `mood(waiting)`
- Epoch callback schema matched the expected 2.9.5.9 fields (`active_for_epochs`, `blind_for_epochs`, `num_deauths`, `num_associations`, `num_handshakes`, peer/bond fields, etc.).
- Bettercap live AP/client state remained available while the bridge was enabled.
- `wlan0mon` remained in monitor mode and was observed on 5 GHz channel 108 during validation.
- gpsd was reachable. GPS had no fix at validation time, correctly represented as `connected_no_fix`.
- Context engine correctly fell back to `PWN` with low-confidence/unknown motion when no GPS speed fix existed.
- SQLite time-series history returned real CPU temperature samples.
- Beast Core remained a disabled-on-boot service during the test; Pwnagotchi and Bettercap remained active.

## Findings folded into v0.4

1. **GPS stale-field correction.** A previous `gps.hdop` value remained present while the current fix was lost. v0.4 explicitly clears fix-derived GPS values when they are not current.
2. **Event-volume correction.** High-frequency `state.changed` events were dominating the in-memory/event history and were being durably stored. v0.4 keeps state patches live for UI streaming but no longer stores them as durable timeline events; the API can filter transient events.
3. **Semantic event layer.** v0.4 derives meaningful low-volume events such as GPS lock transitions, context changes, thermal-band changes, health changes, and session-unique AP discovery batches.
4. **UI gate is now unblocked.** The verified local API and canonical state model are stable enough for the first real Beast UI compositor skeleton.

## Target observations from this sample

- CPU temperature: about 68.65 °C.
- CPU total load at sample: about 30.9%.
- RAM used: about 5.6%.
- Bettercap live sample: 8 APs / 2 clients.
- Pwnagotchi bridge: available and event-driven.
- Core health: healthy.

These values are observations from this validation window only, not permanent expectations or thresholds.
