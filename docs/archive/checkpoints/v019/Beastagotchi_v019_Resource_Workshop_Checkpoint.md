# Beastagotchi v0.19 — Resource / Workshop Checkpoint

## Purpose
This checkpoint advances Beastagotchi without locking the final visual language.

The project now exposes the resource/thermal and presentation-ownership data that
already existed inside Beast Core through the Beast Studio Operations surface.

## Added
- Curated `/platform-bundle` resource snapshot.
- Per-process Beast/platform CPU and RSS visibility.
- Beast UI render/composition/framebuffer-write cost visibility.
- CPU temperature, system CPU/RAM/load, Pi clock and throttle visibility.
- Resource Governor state, budget, FPS cap and reason visibility.
- Presentation desired/active owner, availability and conflicts visible in Studio.
- Theme Manager install/enabled/managed-handoff truth visible in Studio.
- Black Box incident summaries visible beside services/backups/tasks.
- Presentation handoff executor remains deliberately locked.

## Design rule
Resource management is measurement-first. Beast should remove duplicated polling,
inactive render loops and unnecessary background work before it reduces visible
experience. Thermal/load shedding remains an exceptional safety mechanism.

## Visual direction
The final UI style is intentionally unresolved. Current renders are exploration,
not a commitment. Page/tab/swipe architecture and Beast identity remain protected
while the styling/layout language continues to evolve.

## Next
- Validate this bundle in CI.
- Include it in the next off-screen Pi capture.
- Use real per-process measurements to identify duplicated/background work.
- Add presentation-owner adapters only after Theme Manager/native release/acquire
  semantics are explicit and testable.
- Continue WebUI workshop structure for packages/updates/hardware without forcing
  those controls onto the 480×320 TFT.
