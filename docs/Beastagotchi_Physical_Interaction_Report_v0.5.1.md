# Beastagotchi Physical Interaction Report — v0.5.1

**Source:** second physical 480×320 ADS7846 touchscreen video test.

## What improved

- Footer previous/next controls are materially easier to activate than v0.5.
- Long-press interaction appears reliable in the observed test.
- Vertical quick-drawer gesture/exit behavior appears substantially more reliable.
- Display ownership, orientation, page rendering, and rollback behavior remain usable.

## Remaining defect

Horizontal swipes are still inconsistent. When they do register at the edge of the main carousel, the UI can appear to bounce between page 1 (HOME) and page 8 (SYSTEM), even when the physical swipe direction is intended to be the opposite direction.

## Code-level causes found

1. v0.5.1 sampled a mapped touch point after every individual `ABS_X` or `ABS_Y` event. Linux input devices deliver coherent frames terminated by `SYN_REPORT`; sampling mid-frame can pair a new coordinate on one axis with an older coordinate on the other axis.
2. Swipe direction was derived primarily from endpoint displacement. ADS7846 lift-off wobble/snap can contaminate those endpoints.
3. Main-page swipes used circular modulo navigation, so a misread right-swipe while on HOME immediately jumped to SYSTEM, making the direction error visually dramatic.

## v0.5.2 correction

- Sample coordinates only at `SYN_REPORT` boundaries.
- Require a fresh coordinate pair for the beginning of each new touch.
- Determine swipe direction from the full gesture path trend, with endpoint medians as supporting data.
- Slightly reduce the horizontal threshold and tolerate natural diagonal finger motion.
- Clamp finger swipes at the first/last page; footer arrows remain circular.
- Save bounded volatile gesture traces under `/run/beastagotchi/touch-gestures.jsonl` for exact physical tuning.
- Include swipe direction and delta in the PHYS TEST overlay.

This is an input-layer correction only. The generic engineering visuals remain intentionally unchanged until interaction is considered dependable.
