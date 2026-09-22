# Beastagotchi Secrets, Achievements & Seasonal Systems — v0.9

## Purpose

Beastagotchi should reward long-term use, curiosity, exploration and attention without turning RF behavior into a grind. The systems in this document are cosmetic/identity systems layered above Beast Core. They do not change radio attack behavior.

## Achievement rarity

Achievements use six presentation tiers:

- Common
- Uncommon
- Rare
- Epic
- Legendary
- Mythic

Rarity describes how difficult/unusual the unlock is. It is not a gameplay power level.

The catalog is intentionally long-tailed. Example lifetime milestones include 10, 25, 50, 100, 250, 500, 1,000, 2,500, 5,000 and 10,000 lifetime-first AP observations; vendor milestones; GPS-lock milestones; capture/archive milestones; runtime milestones; evolution milestones; hardware milestones; context/mode milestones; theme/customization milestones; seasonal events; and hidden discoveries.

Rewards may include XP, badges, titles, palettes, aura variants, theme fragments, cosmetic face/accessory pieces, effect packs, hidden screens, archive entries, and hints. Achievements do not silently enable intrusive RF actions.

## Rare Moments

Rare Moments are deliberately scarce device events. The target design is roughly 1–4 opportunities per calendar year per Beast, plus separate seasonal/condition-driven secrets.

### Scarcity model

A per-device secret seed is created once. A deterministic HMAC schedule derives the rare windows for each year. The normal UI does not expose the future schedule.

This has an important property: the event exists whether Beast is running or not. If Beast is powered off for the complete window, the event is missed. On the next boot Beast records that the opportunity passed. It does not reschedule the event simply because it was missed.

### Omens

Shortly before a scheduled Rare Moment, subtle vector sigils can fade in and out above all ordinary UI layers. They are intentionally unexplained. They may be nearly transparent, occur in different locations, and vary by rarity/theme.

Omens are not limited to the Rare Moment scheduler. Other future triggers may use the same visual language: seasonal events, unusual hardware combinations, special achievements, exact environmental conditions, or multi-step secrets.

### Witnessing versus merely occurring

Software cannot prove that a human's eyes were physically on the display. Beast therefore distinguishes:

- occurred — the event window ran while Beast was on;
- seen by system — Beast rendered the event;
- witnessed — the user deliberately touched the Rare Moment while it was active.

Only the last category is suitable for a "you actually found this" achievement. v0.9 writes a short-lived acknowledgement from Beast UI to Beast Core when the active Rare Moment is touched.

### Cinematic assets

The v0.9 renderer uses a procedural cinematic placeholder so the scheduling/acknowledgement architecture can be validated without carrying large media assets yet.

The production system is planned to support Rare Cinematic Packs with a manifest and one of several render backends:

1. procedural vector/particle animation;
2. pre-rendered frame pack at native 480×320;
3. animated image/video backend when decode performance has been validated on the physical Pi.

Rare clips may range from a few seconds to tens of seconds. Longer/heavier clips are appropriate precisely because they run extremely infrequently. The Resource Governor will temporarily reserve more CPU/render budget for them while keeping thermal and core-service safety authoritative.

## Secret input systems

Secrets must not conflict with global navigation gestures. In particular, long-press is already a normal Beast control and should not be used as an invisible code sequence.

The future **Cipher Console** is therefore a dedicated app/page. It can switch between input surfaces such as:

- numeric keypad;
- telephone-style dot/pattern grid;
- retro D-pad + A/B + Start/Select controller;
- symbol/rune pad;
- combination dial;
- small logic/pattern puzzles.

Secret sequences can yield achievements, archive entries, cosmetics, rare event previews, theme fragments, lore, or one-off visual events. A classic direction-code easter egg can live safely inside this dedicated surface rather than hijacking ordinary UI gestures.

## Seasonal / calendar / celestial context

v0.9 introduces low-cost ambient state keys for season, local day phase and approximate moon phase. Weather is not guessed; future weather state must come from an online source or physical sensor.

Possible visual uses include:

- spring/summer/autumn/winter ambiance;
- dawn/day/dusk/night lighting;
- moon-phase overlays and achievements;
- solstice/equinox events;
- Halloween/holiday/New Year packs;
- snow, rain, wind, storm and heat effects when backed by real data;
- seasonal Beast accessories;
- seasonal palettes and Matrix rain variants;
- rare seasonal secrets and collectibles.

These systems should be overlays/contexts rather than forcing a complete theme change unless the user chooses that behavior.

## Documentation policy for public GitHub release

The final project should contain both a spoiler-light user manual and an explicit spoiler document. Users who want discovery can avoid the spoiler document; users who want to know that content exists can read it.

Recommended final layout:

- `README.md` — installation, normal use, architecture, controls, customization;
- `docs/ACHIEVEMENTS.md` — public achievement categories, rarity and tracked statistics;
- `docs/SECRETS_AND_EASTER_EGGS.md` — spoiler-heavy triggers, input codes, special conditions, Rare Moment rules and unlocks;
- `docs/THEME_STUDIO.md` — theme/effect customization;
- `docs/DEVELOPMENT.md` — paths, code structure, adding pages/widgets/themes/modules;
- `docs/HARDWARE.md` — supported/known accessories and enrollment;
- `CHANGELOG.md` — release history.

Exact future Rare Moment timestamps are never documented because they are different for each Beast and derived locally.
