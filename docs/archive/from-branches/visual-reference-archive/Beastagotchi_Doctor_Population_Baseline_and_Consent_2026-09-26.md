# Beastagotchi Doctor Population Baseline & Consent

**Date:** 2026-09-26  
**Status:** active design candidate; preserve for Doctor/Global/Home Base reconciliation

## Core refinement

The collective Doctor network should not learn only from failures and repairs. A privacy-safe **population baseline** can also be valuable because hardware, drivers, sensors, configurations, package combinations and peripheral revisions vary widely.

The useful question is not only:

> "Who had this problem and what fixed it?"

but also:

> **"What does normal look like across comparable Beast/Pwnagotchi systems?"**

This can strengthen anomaly detection, hardware qualification, compatibility matching, sensor normalization and regression detection.

## Baseline contribution examples

Potentially useful normalized facts, subject to policy and minimization:

- Pi/board family and revision;
- architecture;
- kernel/firmware generation;
- driver/module versions;
- installed hardware/peripheral IDs;
- display/controller family;
- storage/controller family;
- radio chipset/interface capabilities;
- sensor model/revision and normalized capability metadata;
- Pwnagotchi/Bettercap/Beast versions;
- plugin/provider/package versions;
- selected configuration fingerprints;
- capability availability/health state;
- known-good operational fingerprints;
- broad performance/compatibility envelopes where useful.

Do not upload raw secrets, credentials, private keys, capture content, raw SSIDs/BSSIDs, private peer identities, precise location/history, owner filenames/doc contents or other sensitive/private content by default.

## Consent tiers

Suggested policy distinction:

### Base / default-share candidate
Only coarse, normalized, privacy-safe technical facts that materially improve compatibility/diagnostic value. This still requires a product-level privacy decision before becoming default behavior.

### Opt-in enhanced technical sharing
More detailed hardware/configuration/sensor facts that may improve matching but increase fingerprintability.

### Per-case explicit approval
Sensitive or unusually specific evidence that could help diagnose an uncommon issue but should never be globally shared automatically.

### Never-share class
Secrets, credentials, private keys/tokens, raw private content and other information with no justified diagnostic/public value.

## Why population data matters

Potential uses:

- detect that a supposedly healthy value is unusual compared with matching hardware;
- identify board/peripheral revisions with elevated failure rates;
- learn which driver/kernel pairings are stable;
- identify sensor-specific offsets/quirks without pretending every sensor is identical;
- recognize common successful configuration combinations;
- detect regressions after an update;
- rank fixes by success on truly comparable machines;
- improve guided setup defaults;
- qualify new hardware/provider combinations;
- pre-cache relevant knowledge at Home Base.

## Matching principle

Population statistics must remain explainable.

Instead of one opaque similarity percentage, retain dimensions such as:
- hardware exact/close/different;
- kernel exact/compatible/different generation;
- driver exact/near/different;
- Pwnagotchi/Beast branch/version;
- peripheral/sensor exact family/revision;
- relevant config fingerprint;
- symptom/failure class;
- environmental/context differences where safely and meaningfully represented.

## Privacy caution

A sufficiently detailed hardware/software fingerprint can itself become identifying. Therefore privacy must be evaluated at the **combination** level, not only field-by-field.

Use minimization, bucketing, hashing/pseudonymization where appropriate, and avoid exposing a stable real-person identity. A Doctor can contribute useful fleet evidence without the Global service knowing who the owner is.

## Home Base implication

Home Base can become the preferred sync point for:
- contributing new sanitized baseline deltas;
- contributing resolved-case outcomes;
- pulling relevant fleet statistics/knowledge;
- receiving compatibility/regression advisories;
- caching fixes, manuals, datasets and Procedures relevant to this Beast's installed hardware/software.

## Principle

> **Failures teach the fleet what breaks. Healthy systems teach the fleet what normal looks like.**
