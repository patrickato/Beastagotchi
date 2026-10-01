# Beastagotchi Toolbelt Priority Order

**Date:** 2026-09-26
**Status:** owner-accepted ordering for planning. Exact implementation details remain discussable at the point they are designed/built.

The owner accepted the following 1–15 order and requested that detailed input be asked for only when materially needed so brainstorming can continue without constant confirmation.

1. **Owner Space / managed-boundary model**
2. **Transaction/history evidence**
3. **System Graph substrate**
4. **Device Passport / canonical inventory**
5. **“What Changed?” data capture**
6. **One Doctor with extensible condition knowledge**
7. **Radio Workspace**
8. **Power Detective**
9. **Storage Workspace**
10. **Display/radio diagnostic condition packs**
11. **Hardware Bench**
12. **Sensor Onboarding**
13. **Field RF Journal**
14. **Hardware-expanded Beast senses / expression**
15. **BenchLink**

## Interpretation

This is a planning/architecture order, not a mandate that each item become a separate visible app or ship as a standalone release feature.

- Foundation items should shape contracts/data capture early even when polished UI arrives later.
- One Doctor remains the only diagnostic product; display/radio/etc. are diagnostic domains/condition packs.
- System Graph is the shared substrate for topology, capability, pipeline, and resource-claim views.
- Workspaces should contain Instruments, Tools, and Procedures rather than multiplying top-level mini-apps.
- Input from the owner should be requested when a genuine product, UX, policy, end-state, or irreversible architecture decision needs it, not for every low-level implementation choice.
