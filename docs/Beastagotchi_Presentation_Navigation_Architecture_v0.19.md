# Beastagotchi Presentation & Navigation Architecture v0.19

## Goal
Preserve the page/tab/swipe experience while allowing Beastagotchi to grow into many apps, themes, profiles and presentation engines without turning the 480×320 display into an administration panel.

## Three layers
1. **Presentation owner** — native Pwnagotchi, Theme Manager or Beast UI owns physical framebuffer/touch through an exclusive broker lease.
2. **Beast primary carousel** — fast field pages. Beast/Home is the default landing page and retains creature, level/growth/evolution/personality presentation.
3. **Apps / Studios / Decks** — deeper tools opened from the carousel, Control Center, search or context. Their number is not artificially capped.

## Reference Beast carousel
The exact final ordering remains UX-testable, but the retained information families are:
- Beast/Home — creature, level/XP/growth, evolution, aura/personality and immediate attention state;
- Recon — current activity/session/environment summary;
- Networks — AP/client/channel encounter state and history;
- Spectrum — channel/RF visualizations appropriate to available radios/services;
- Captures — capture/session records and related status;
- Map — GPS and compatible spatial overlays;
- System — health/power/storage/services/connectivity/attention;
- optional context pages may appear when hardware/capabilities justify them.

Detailed Beast progression/achievement/collection views can open from the Home page instead of forcing every detail into the primary carousel.

## Interaction principles
- Swipe/tab navigation remains available.
- Large touch targets and resistive-touch physical validation remain mandatory for 480×320.
- Critical alerts may overlay or badge pages without permanently stealing the layout.
- Long configuration forms belong primarily in Beast Studio/WebUI.
- Back/home behavior is predictable and globally consistent.
- Every app declares whether it is field-appropriate, WebUI-preferred, large-display-preferred or available everywhere.

## Presentation Broker contract
The current owner holds an exclusive lease until a user/system request initiates handoff:
`REQUEST -> PREPARE_RELEASE -> RELEASED -> ACQUIRE -> HEALTH_CHECK -> COMMIT`.
Failure before commit causes rollback/reacquisition of the previous known-good owner.

A presentation may remain loaded in standby/web-only state without touching framebuffer/input. This is the preferred coexistence model for Korrie71 Theme Manager + Beast Core/UI.
