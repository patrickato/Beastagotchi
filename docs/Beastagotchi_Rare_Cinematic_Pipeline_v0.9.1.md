# Beastagotchi Rare Cinematic Pipeline — v0.9.1

Rare Moments are intentionally scarce. Their visual budget can therefore be much higher than the always-on UI, provided they never destabilize Beast Core, Pwnagotchi, GPS, or radio work.

## Three visual tiers

1. **Omen overlay** — lightweight procedural sigils above the live UI. Slow, subtle, ambiguous, and cheap enough to run while everything else continues normally.
2. **Procedural fallback cinematic** — the current v0.9 renderer. This proves scheduling, acknowledgement, rarity, persistence, and full-screen compositing. It is not the final quality target.
3. **Rare Cinematic assets** — short pre-rendered 480×320 sequences built specifically for the TFT. These are the final target for the very rare events.

## Proposed asset budget

The first hardware benchmark should test H.264/MP4 playback at 480×320 and 15, 20, and 24 fps. A 5–10 second Rare/Epic sequence can be visually dense; Legendary can run roughly 18–30 seconds; Mythic is allowed roughly 30–60 seconds. Audio remains optional and must never be required.

The player will be isolated from Beast Core. If decode/render timing falls behind, Beast drops cinematic frames rather than blocking telemetry or radio work. If an asset is missing or unsupported, the procedural fallback plays instead.

## Asset manifest concept

Each cinematic pack should eventually describe:

- id / title / rarity
- duration and preferred fps
- video or frame asset path
- optional theme/color variants
- omen sigil(s)
- conditions / unlock relationship
- whether acknowledgement is required
- fallback procedural style
- checksum/version

## Witness semantics

Beast differentiates:

- **occurred** — the rare window happened while Beast was powered on
- **rendered** — the UI actually rendered the event
- **witnessed** — the user deliberately acknowledged/touched the active event

The system cannot prove a human eye saw pixels without a camera, so `witnessed` is the strongest practical signal. The final UI should preserve this distinction in secret/achievement history.

## Performance rule

Rare cinematics may use a much larger visual budget than normal pages because they are temporary and exceptionally infrequent. Core collectors, Pwnagotchi/Bettercap, storage safety, and thermal protection always have priority over cinematic quality.
