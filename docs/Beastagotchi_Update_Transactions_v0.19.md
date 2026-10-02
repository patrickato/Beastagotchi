# v0.19 Update Transactions — safety model

## Current executable scope

Beastagotchi now has an end-to-end update transaction only for **Beast Packs**.
That scope is intentional.

A Beast Pack update may:

1. discover a newer release from a trusted source;
2. download a bounded release asset;
3. verify SHA-256;
4. copy the verified archive into the bounded Beast Pack inbox;
5. re-inspect it as a Beast Pack;
6. require the manifest ID to match the component being updated;
7. stage it as verified;
8. transactionally install it into the inert installed-pack registry;
9. run a platform probation snapshot;
10. retain the prior installed pack as rollback payload;
11. persist update history.

It still does **not activate the pack** or restart services.

## Why core/platform updates remain staged-only

Beastagotchi itself, Pwnagotchi and Theme Manager have different failure modes.
A safe update adapter for each must know how to create the correct rescue
snapshot, preserve configuration, restart only required services, verify
component-specific health, and restore the previous version without depending
on the failed component.

Therefore `auto_install` currently means:

- Beast Pack: eligible for the inert transactional update path;
- Beastagotchi core: verified stage only until its self-update adapter exists;
- Theme Manager: verified stage only until plugin/config rollback is proven;
- Pwnagotchi platform: requires a dedicated image/platform adapter.

## Probation truth

The shared probation evaluator currently checks Beast Core health, Pwnagotchi,
Bettercap, root read-only state and presentation ownership conflicts.

## Background automation

The policy engine may identify `auto_stage` and `auto_install` candidates while
docked and online, but this milestone still does not run a background mutation
loop. That remains a later opt-in gate after retry/backoff, notification UX and
failure escalation are complete.
