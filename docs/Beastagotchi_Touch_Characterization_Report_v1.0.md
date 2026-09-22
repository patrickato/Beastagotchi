# Beastagotchi Touch Characterization Report v1.0

Date: 2026-09-20
Hardware: ADS7846/XPT2046-class resistive touchscreen, 480×320
Dataset: 3 complete stylus passes + 3 complete finger passes from Beastagotchi Touch Lab v1.0

## Executive result

The repeated dataset is strong enough to change Beastagotchi's touch design from assumption-based to measured behavior.

The panel is a **single-contact resistive touchscreen**. Linux exposes `ABS_X`, `ABS_Y`, and `ABS_PRESSURE`; no multitouch axes are present. Multi-finger gestures should therefore not be used.

The current legacy affine calibration is substantially misaligned. Across all 75 precise stylus targets it has a pooled median error of about **25.1 px**, with a systematic bias of roughly **+6.5 px X / -20.0 px Y**. A new pooled affine fit reduces median residual error to about **2.0 px**, p95 to about **4.7 px**, and max residual to about **9.2 px**.

A quadratic transform was also tested. It improved pooled median residual only from about **2.02 px to 1.97 px**, which is too small to justify the extra complexity. Beastagotchi should retain a simple affine mapper.

## Recommended affine transform

Derived from all 75 stylus targets across the three independent passes:

```json
{
  "x": [
    0.0000443930936,
    0.129245084,
    -32.4635492
  ],
  "y": [
    -0.0855381318,
    -0.000242859772,
    331.630625
  ]
}
```

This is a candidate for a reversible physical validation before becoming the active calibration.

## Calibration comparison

| Model | Median error | Mean error | p95 | Max |
|---|---:|---:|---:|---:|
| Existing legacy affine | 25.10 px | 24.38 px | 33.92 px | 39.67 px |
| New pooled affine | 2.02 px | 2.30 px | 4.68 px | 9.21 px |
| New pooled quadratic | 1.97 px | 2.28 px | 4.60 px | 9.09 px |

Conclusion: use the new affine calibration; do not add nonlinear mapping.

## Finger targeting results

Finger interaction is naturally much less precise than stylus interaction. The useful question is therefore not only calibration accuracy, but how large Beastagotchi's touch targets must be.

Using the new affine mapping, all first finger attempts were replayed against hypothetical square targets of different sizes. Approximate first-attempt containment was:

| Square target | All first attempts | Ignoring obvious very-low-pressure transients (pressure <20) |
|---|---:|---:|
| 36 px | 45% | 45% |
| 44 px | 65% | 67% |
| 48 px | 72% | 75% |
| 52 px | 77% | 80% |
| 56 px | 82% | 85% |
| 60 px | 82% | 85% |
| 64 px | 85% | 89% |
| 72 px | 92% | 96% |
| 80 px | 92% | 96% |

These values include deliberate natural finger input rather than stylus-like precision and therefore are the correct basis for everyday UI design.

### Touch-size policy for Beastagotchi

Recommended design rules:

- **<44 px:** avoid for direct finger controls.
- **48–52 px:** absolute minimum for secondary actions when space is constrained.
- **56–64 px:** preferred ordinary control size.
- **72+ px:** primary actions, important selectors, high-confidence controls.
- Keep visible controls clean, but use larger invisible hit boxes wherever neighboring controls do not overlap.
- Avoid stacking four or more 27–35 px touch rows on the physical screen; use paging/cards/detail screens instead.

This explains why large footer arrows became reliable while small Theme Studio steppers remained difficult.

## Finger targeting behavior

After accurate mapping, natural finger taps showed a median offset of several pixels rightward and roughly 10–16 px downward from the visual target center. This is normal human/pad behavior on a small resistive screen and should be handled by generous hit boxes rather than corrupting the physical calibration.

The accurate stylus calibration should remain the coordinate truth. Finger-friendliness should be solved at the UI control/hit-target layer.

## Pressure findings

The pressure axis is real and useful, but overlapping enough that it must not be required for ordinary navigation.

Across the controlled stylus pressure prompts, non-zero samples were approximately:

| Prompt | Median pressure | Typical observation |
|---|---:|---|
| Light | ~125 | broadest variation |
| Normal | ~139 | fairly repeatable |
| Firm | ~149.5 | distinguishable but overlaps normal |

Finger sessions showed much higher overall median pressure values (roughly 178–201 in the three passes), but pressure depends on contact area, location, and technique.

Recommended use:

- Do **not** use pressure for required navigation or ordinary buttons.
- It may be used as a confidence signal to reject extremely weak transient samples.
- It is suitable for diagnostics, drawing tools, experiments, and optional/secret interactions.
- If used for secrets, thresholds should be user-calibrated/adaptive rather than hard-coded globally.

## Gesture findings

The panel supports only one contact at a time, but the synchronized gesture engine is viable for taps, long presses and one-finger swipes.

The third natural-finger pass correctly classified the full horizontal/vertical swipe set and all long presses. Earlier passes show a learning/technique effect and reinforce the need for explicit UI cues rather than complex gesture-only navigation.

Recommended policy:

- Keep arrows/buttons as first-class navigation.
- Keep swipes as convenient shortcuts, not the sole route to important actions.
- Do not design multi-finger secrets or gestures.
- A dedicated Cipher Console is a much better place for secret sequences.

## Architecture consequences

1. Preserve a mathematically accurate affine calibration.
2. Add a user-interface touch-size policy and reusable large-control components.
3. Theme Library should use large cards/paging rather than precision scrolling.
4. Theme Studio should show at most a small number of large editable rows per physical page.
5. Achievements, Plugin Manager, Hardware Studio, Cipher Console, Map controls and configuration pages should all inherit the same touch-size policy.
6. Pressure becomes an optional capability registered by the Hardware/Capability layer, not a navigation dependency.
7. Keep Touch Lab as a permanent diagnostic/developer utility and document recalibration in the final master README.

## Recommended next physical gate

A reversible calibration validation should apply the pooled affine transform without deleting the current calibration. The test should compare:

- corner/edge targeting,
- footer navigation,
- Theme Library cards,
- Theme Studio controls,
- ordinary finger taps,
- stylus targets,
- swipe classification.

If it feels correct, the new affine transform becomes Beastagotchi's active calibration. The prior transform remains recoverable.
