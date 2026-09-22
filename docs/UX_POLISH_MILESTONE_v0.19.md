# Beastagotchi v0.19 — UX / Visual Cohesion Milestone

## Why this milestone exists
External hands-on feedback on the v0.11 friend kit described the UI as unattractive, clunky and not sufficiently user-friendly. The criticism is useful and consistent with the project's own v0.18 renders: the platform architecture has matured faster than the final interaction and visual language.

This milestone deliberately pauses broad surface-area growth long enough to make the existing experience feel intentional.

## Goals
- Establish a production visual system rather than a collection of individually functional screens.
- Create clear information hierarchy for a 480x320 resistive-touch display.
- Reduce persistent chrome, tiny text and repeated outlined-box layouts.
- Make primary actions obvious and secondary details discoverable.
- Use touch targets sized from the measured ADS7846 finger/stylus characterization.
- Keep the Beast/character visible and emotionally useful without obstructing instrumentation.
- Preserve truthful live telemetry while reducing visual noise.
- Give every major theme a genuinely distinct composition, not only palette/effects changes.
- Make navigation predictable: Home, Back, Apps, notifications/context, and page movement should behave consistently.
- Add empty/loading/error/no-capability states that look intentional.

## Deliverables
1. Design tokens: spacing, type scale, corner radii, strokes, emphasis levels, icon sizing, animation timings.
2. Navigation redesign and interaction map.
3. New reference Home/Overview composition.
4. Redesigned Operations Center, Apps, Plugin Manager, System/Diagnostics and Networks pages.
5. Consistent cards, lists, dialogs, confirmations and toast/notification system.
6. Theme-specific component skins with shared interaction grammar.
7. 480x320 physical readability/touch regression.
8. 800x480 responsive Board/Command-Center comparison.
9. A visual acceptance gallery used for future regressions.

## Acceptance criteria
A first-time tester should be able to identify the device state, move between primary areas, open/close an app, understand a warning, and return Home without instructions. Core status must be readable at arm's length; advanced detail can remain one tap deeper.
