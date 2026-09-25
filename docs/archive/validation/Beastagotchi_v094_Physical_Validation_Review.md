# Beastagotchi v0.9.4 Physical Validation Review

## Evidence reviewed

- user-supplied `beast-display-validation-v094.tar.gz`
- user-supplied physical video of the four Rare Moment presentations
- user's written notes from the physical test

## Passed observations

- Beast Core health was healthy with 273/273 live keys and no stale/unavailable keys in the captured state.
- Pwnagotchi, Beast Core and Beast UI coexisted during the handoff test.
- touch calibration state remained `restored`; the rejected v0.9.2 affine candidate was not active.
- Native Pwnagotchi source was available at exact 480x320 with configured rotation 180 degrees.
- touch and swipe behavior were reported good overall.
- Native Pwnagotchi stock view and several colored Native faces worked.
- Rare Moment drift/cross/ghost/apparition mechanics rendered and moved successfully in the submitted video.
- Achievement Explorer was usable and progress data was live.

## Matrix finding: transient magenta diagonal lines

The validation snapshot saved Matrix preferences as mixed / dense / fury / green. The captured framebuffer showed vertical green code and no permanent magenta diagonal field.

The event history recorded a thermal transition from hot to critical at 80.34 C, followed by a return to hot at 78.39 C. In v0.9.4, a severe Matrix event used `theme.danger` (pink-red) while the event-reaction bars advanced their X and Y coordinates together every animation tick. This creates exactly the reported temporary diagonal moving magenta pattern and then disappears when the reaction window expires.

Conclusion: this specific magenta diagonal effect was an event-reaction bug / visual-design collision, not evidence that Matrix rain columns were moving diagonally.

## v0.9.5 corrective action

- fixed-X vertical reaction pulses
- stationary danger corner brackets for severe events
- Matrix `REACTIONS` On/Off option
- no additional rain-renderer change until a reaction-isolated physical Matrix video is available

## Achievement input finding

The user described Achievement controls as usable but tight. v0.9.4 used individually enlarged hitboxes; adjacent enlarged regions can overlap on a 480x320 resistive panel. v0.9.5 replaces that screen with explicit non-overlapping touch partitions.
