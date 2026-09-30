# Beastagotchi Independent Visual Review Brief

Date: 2026-09-27
Audience: independent AI/design reviewer (Claude or equivalent)
Status: Review brief only. Reviewer is advisory, not authoritative, and should not merge implementation changes unless explicitly asked.

## Mission

Perform an independent visual/product critique of Beastagotchi v0.19's five Experiences and propose concrete improvements that preserve the project's architecture, truth model, Pwnagotchi foundation, 480×320 TFT constraints, and owner-approved product philosophy.

## Read first

At minimum review these repository documents:
- docs/Beastagotchi_New_Chat_Continuation_Checkpoint_2026-09-27.md
- docs/Beastagotchi_Canonical_Architecture_Contracts_2026-09-27.md
- docs/Beastagotchi_PostReconciliation_Build_Order_and_Roadmap_2026-09-27.md
- docs/Beastagotchi_Visual_Direction_Synthesis_v2_2026-09-27.md

Also inspect current v0.19 renderer code and visual proof artifacts for:
- Atlas
- Forge
- Observatory
- Habitat
- Monolith

## Non-negotiables

- Raspberry Pi 4 / Pi Zero 2 W class hardware matters.
- Primary TFT target is 480×320 at 3.5 inches with touch.
- Real/live data only where represented as real. Unknown must stay unknown.
- Pwnagotchi/Bettercap remain protected engines and independently usable.
- Beast is full but not cluttered.
- No generic same-layout-five-colors theming.
- Five Experiences should be genuinely different visual/interaction grammars built on one shared truth model.
- Creature, Doctor, and Broad AI are distinct systems/roles.
- Creature must not gate core capabilities.
- WebUI can be richer but TFT must remain a complete first-class interface.
- Guided simplicity must never fake or conceal the expert truth underneath.

## Current concern

Recent render explorations repeatedly drifted toward attractive marketing-board imagery, fantasy companion UI, or generic dashboards. The owner explicitly has not approved any current render as final. The goal is not another pretty concept board; the goal is a coherent, implementable 480×320 product language.

## Questions to answer

1. Which current visual ideas are genuinely strong and should survive?
2. Which are generic, overdesigned, too game-like, too decorative, or unsuitable for 480×320?
3. What should the shared Beast visual grammar be across all Experiences?
4. What should be unique to Atlas, Forge, Observatory, Habitat, and Monolith?
5. What information hierarchy works on a real 3.5-inch TFT at arm's length?
6. How can the creature remain meaningful without turning Beast into a pet game?
7. How can security/radio/system truth remain immediately accessible without turning every page into a dashboard?
8. How should touch navigation work consistently without making all five Experiences look identical?
9. What should the minimum coherent screen family be for owner visual approval?
10. Identify any 'holy shit, that's obviously better' visual or interaction ideas that fit the project and are realistically implementable.

## Desired output

Produce a review document, not code, containing:
- strongest 10 observations;
- retain / modify / reject table for major current visual motifs;
- proposed shared design system primitives;
- one concise design DNA section per Experience;
- suggested 480×320 page family for each Experience;
- three highest-value implementation changes;
- any unresolved owner decisions that truly need owner input.

Do not assume the owner wants to approve tiny implementation details. Make recommendations decisively and reserve questions for genuine product choices.
