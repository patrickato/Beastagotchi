# Archived documentation from consolidated branches

This tree preserves design, architecture, and cross-AI collaboration
documents that lived only on branches before the v0.19 consolidation
(2026-09-30). They are kept here so nothing is lost and everything is
searchable in the repo. **Treat these as reference/history, not the
current source of truth** — the current specs live directly under
`docs/`. Promote any of these to a top-level `docs/` file if it becomes
canonical.

Every original branch is also preserved intact as a git tag
`archive/<branch-name>` (including rendered reference images, which were
not copied here to keep the tree lean). Recover a full branch with:

    git checkout archive/<branch-name>

## Sources

- **visual-reference-archive/** — from `openai/v019-visual-reference-archive`.
  The largest set: the 11-part Architecture Contract Review, capability-
  expansion cluster designs, AI Doctor architecture direction, canonical
  architecture contracts, cross-layer "jam" batches and visual direction.
- **claude-visual-review/** — from `claude/beastagotchi-visual-review-2026-09-27`.
  Independent visual review request/response not already in the set above.
- **claude-foundation-review/** — from `claude/beastagotchi-foundation-review-2026-09-25`.
  Foundation review request/response and a visual north-star reference.
- **claude-doctor-crosspollination/** — from `claude/pwnagotchi-doctor-crosspollination`.
  Note on cross-pollinating a Pwnagotchi "Doctor" plugin idea.
- **claude-creature-ideas/** — from `claude/clever-cori-fq74wu`.
  Creature ideas, opinions and code findings.

Byte-identical duplicates across sources were removed, preferring the
`visual-reference-archive` copy.
