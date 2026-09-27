# Beastagotchi Free-First Backend Options

**Date:** 2026-09-27  
**Status:** implementation candidates; provider selection not frozen

## Goal

Avoid assuming Beastagotchi needs a paid central server to support Global Doctor, public indexes, shared metadata, software catalogs, docs/manifests and selected public assets.

## Strong current candidates

### Cloudflare D1
Useful for compact structured Global Doctor/fleet metadata.
Current free tier (2026-09-27):
- 5 million rows read/day;
- 100,000 rows written/day;
- 5 GB total storage;
- no D1 egress charge.

Good fit for:
- normalized Doctor cases;
- healthy fleet baselines;
- compatibility records;
- software/catalog metadata;
- content indexes;
- lightweight public/global query API.

Caution: daily free-tier read/write limits are enforced; schema/index design must avoid wasteful scans.

### Cloudflare R2
Useful for larger public/static objects.
Current free tier:
- 10 GB-month standard storage;
- 1 million Class A operations/month;
- 10 million Class B operations/month;
- Internet egress free.

Good fit for:
- public docs bundles;
- manifests;
- small map/data packs;
- firmware/resources that licensing permits redistributing;
- exported public artifacts;
- larger immutable Global Doctor support objects if ever needed.

### Cloudflare Workers
Potential API/gateway layer in front of D1/R2 for validation, rate limiting, privacy normalization and schema-controlled uploads/downloads. Exact free-tier/runtime needs should be checked at implementation time.

### Supabase Free
Current free offering includes:
- 2 free projects;
- 500 MB Postgres database/project;
- 1 GB storage;
- 5 GB egress;
- 500,000 Edge Function invocations;
- 2 million realtime messages;
- free projects may pause after inactivity.

Good fit for rapid prototyping because Postgres/Auth/Storage/API are integrated.

Tradeoff vs Cloudflare-first approach:
- easier relational/product development;
- smaller free database/storage allowances;
- free-project pausing/inactivity behavior needs consideration for a public always-on service.

### GitHub Releases
Excellent for public redistributable Beastagotchi assets rather than a query database.
Current GitHub release limits:
- up to 1000 assets/release;
- each asset under 2 GiB;
- GitHub documents no total release-size or bandwidth limit.

Good fit for:
- Beast releases;
- public Pack bundles;
- public manuals/data snapshots;
- static catalog snapshots;
- firmware/assets we are permitted to redistribute.

### GitHub Pages
Free static project-site hosting for public repositories.
Good fit for:
- project docs;
- static catalog browser;
- public schemas;
- help/instructions;
- generated read-only indexes.

Not a database/API replacement by itself.

## Recommended architecture to evaluate first

A composable free-first model:

1. **GitHub** — source of truth for public project code, releases, static docs and distributable public bundles.
2. **Cloudflare D1** — compact structured Global Doctor/fleet/catalog metadata.
3. **Cloudflare R2** — larger public/shared blobs when GitHub Releases is not the right lifecycle.
4. **Cloudflare Worker** — thin validated API in front of D1/R2.
5. **Beast local cache** — each device downloads/indexes only relevant subsets where practical.
6. **Owner-controlled destinations** — private backups/data remain on owner NAS/phone/PC/chosen cloud rather than Beastagotchi central infrastructure by default.

This avoids one giant hosted database and lets the public system scale by keeping Global Doctor records compact and structured rather than uploading raw logs.

## Key architecture rule

Global Doctor should upload normalized facts/outcomes, not indiscriminate machine logs. Large private/user data should not become central-server responsibility by default.

## Status

Do not freeze providers yet. Re-check quotas, terms, expected user count and data model immediately before implementation. The intent is to prove that a useful shared system can begin with free tiers and public hosting instead of requiring owner-funded infrastructure from day one.
