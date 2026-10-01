# Beastagotchi Architecture Contract Review — Part 6: Content, Storage & Distribution

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** current v0.19 source, completed Structure Deep Dive, Parts 1-5 Architecture Contract Review,
owner small-card/open-ecosystem guidance, Pack/Depot/Collection work, Recovery/Provisioner direction.

---

# 1. Purpose

Beastagotchi is intended to support a very large long-term ecosystem:

- Experiences;
- faces;
- motion/choreography;
- apps;
- Packs;
- Procedures;
- Doctor knowledge;
- progression content;
- compatibility metadata;
- hardware/provider definitions;
- optional media;
- community content;
- future Monstergotchi content;
- owner-created content.

That ecosystem must not force every Pi to:

- download everything;
- keep everything installed;
- keep everything enabled;
- keep everything resident in RAM;
- keep external storage mounted;
- require cloud/network access;
- require a large SD card;
- confuse discovery with trust or activation.

The stable direction is:

> **Large universe. Small active working set.**

and:

> **A complete Beastagotchi does not mean every optional byte is present.**

This Part defines the contracts that keep that true as the project grows.

---

# 2. Five independent content-state axes

Do not collapse content state into one boolean such as "installed".

Every content object may have independent state across at least these axes.

## Presence

Where the bytes/definition currently exist.

Examples:
- remote catalog only;
- source available;
- downloaded/staged;
- installed locally;
- cached locally;
- pinned locally;
- unavailable/source missing.

## Selection

Whether the owner or a Profile/Collection currently wants it.

Examples:
- not selected;
- selected for this device;
- selected for this Beast;
- selected for a Trip/Offline Set;
- selected by a Distribution Profile.

Selection does not imply immediate activation.

## Retention

How strongly Beast should preserve local availability.

Examples:
- reproducible cache;
- ordinary installed;
- pinned;
- active-required;
- irreplaceable owner-created;
- protected system fallback.

## Runtime residency

Whether it currently consumes active resources.

Examples:
- cold;
- indexed metadata only;
- compiled;
- decoded/warm cache;
- active;
- resident/pinned for current Surface;
- dormant.

## Trust

What authority the object possesses.

Examples:
- catalog metadata;
- unverified import;
- verified declarative content;
- project/trusted content;
- trusted executable extension;
- core/system.

These axes are intentionally independent.

Examples:

- a Pack may be **installed + selected + cold + declarative**;
- a remote face may be **catalog-only + selected + not yet present**;
- an active Experience may be **installed + pinned + resident + verified declarative**;
- an owner-created local Scene may be **installed + pinned + customized**;
- an executable plugin may be **installed but disabled/dormant**.

**Invariant:** no code may infer runtime activity or authority solely from "installed".

---

# 3. Content identity

Every durable content object needs a stable identity independent of filesystem path.

Candidate common identity fields:

- namespaced object id;
- object type;
- definition/content version;
- schema version;
- source/provenance;
- content hash where byte-addressable;
- license/redistribution metadata where known;
- compatibility constraints;
- trust class;
- optional component/variant id;
- optional parent Pack/source id.

Filesystem location is storage metadata, not identity.

A path may change without changing object identity.

A remote source URL may change without changing object identity when provenance confirms equivalence.

---

# 4. Content Store

Introduce one logical **Content Store** contract.

This does not require one physical directory.

The Content Store owns metadata and resolution for content objects across storage pools.

It answers:

- what content is known?
- what content is present?
- where are its bytes?
- is the local copy verified?
- what selected/retention state applies?
- what dependencies/components does it need?
- is the active-required subset locally safe?
- what may be evicted?
- what can be reacquired?
- what source/provenance produced this copy?
- what storage cost does it represent?

The Content Store does **not** itself:

- activate executable authority;
- bypass Action/Transaction;
- decide progression rewards;
- render Scenes;
- silently fetch arbitrary remote content;
- mutate OS/package state.

It is content truth and storage orchestration metadata.

---

# 5. Storage pools

Content may live in multiple pools.

Pool semantics matter more than exact mount paths.

## Core/system pool

Normally the system SD/root filesystem.

Contains:
- Beast runtime;
- essential built-in fallback assets;
- active-required metadata;
- critical local configuration;
- protected local state;
- enough content for a complete baseline experience.

Must remain usable without USB/NAS/cloud.

## Local content pool

Normally system SD or another owner-selected persistent local filesystem.

Contains:
- installed Packs;
- Experiences;
- faces;
- media;
- owner Collections;
- optional content.

## Local cache pool

Reproducible/evictable content.

May share the same physical filesystem as local content while keeping different retention semantics.

## Expansion/library pool

Optional:
- larger SD/secondary partition;
- USB flash;
- USB SSD/HDD;
- another local filesystem.

Useful for larger libraries.

Not mandatory for a complete product.

## Network/library source

Optional owner-controlled sources:
- NAS;
- SMB/NFS/SFTP-style library;
- BenchLink machine;
- paired Beast;
- other future local-network provider.

Network source is not assumed continuously available.

## Remote catalog/source

Optional:
- GitHub Releases;
- project/community indexes;
- future CDN;
- upstream project source.

Remote availability is discovery/acquisition, not runtime authority.

---

# 6. Active-content locality rule

An active Experience/Surface/face/choreography must not unexpectedly break because a removable or
network source disappears.

Before activation, all **active-required** objects must either:

1. exist in a guaranteed local pool; or
2. have a declared valid built-in/local fallback.

For owner-selected content sourced from USB/NAS/remote:

- Beast may copy/materialize the active-required subset locally;
- larger nonessential extras may remain at the external source;
- provenance retains the original source;
- local copy may be pinned while active;
- source loss becomes an observable condition, not a crash.

Example:
A large Experience may keep high-resolution optional cinematics on NAS while its 480x320 active
Scene, fonts, face and required assets are local.

---

# 7. Small-card contract

Common **16 GB and 32 GB microSD cards remain first-class targets**.

Large cards are expansion, not a hidden architectural minimum.

The mandatory runtime/core must remain comparatively small.

Stable rules:

- reserve explicit free-space safety floor;
- do not consume that floor with optional content;
- include transaction/update/restore temporary-space requirements in planning;
- include SQLite/WAL/log/capture growth in reserve calculations;
- measure actual usable bytes from the target installation;
- never equate nominal card size with available content budget;
- active/irreplaceable state is never evicted as cache.

Current size targets remain provisional until measured against the exact reference image.

The contract is the budgeting behavior, not one permanent MB number.

---

# 8. Storage Budget Manager

Introduce a storage-budget service above the Content Store.

It consumes:

- pool sizes/free bytes;
- safety reserve;
- content metadata;
- selected Collections/Profile;
- active/pinned objects;
- temporary transaction requirements;
- owner retention choices;
- source reacquisition availability.

It produces a plan such as:

- bytes to download;
- bytes installed;
- temporary peak bytes;
- bytes freed/evicted;
- post-operation reserve;
- objects that become pinned;
- content that cannot safely fit;
- suggested alternatives.

It does not silently delete owner-created or irreplaceable content.

Eviction candidates must be reproducible and unpinned.

---

# 9. Content size/cost metadata

Where practical, manifests should expose:

- compressed/download bytes;
- installed bytes;
- temporary install peak;
- decoded/runtime memory estimate;
- optional component sizes;
- target/display variants;
- expected cacheability;
- source reacquisition policy.

Unknown estimates remain unknown.

Do not fabricate precision.

Actual observed cost may later supplement declared estimates.

---

# 10. Content-addressed storage

Content-addressed storage is encouraged where useful, not required everywhere.

Good candidates:

- immutable downloaded artifacts;
- media assets;
- Pack payload objects;
- generated deterministic derivatives;
- shared fonts/images;
- release artifacts.

Benefits:
- deduplication;
- integrity verification;
- safe cache reuse;
- source-independent identity;
- transactional staging.

Do not force every mutable owner file or SQLite object into CAS semantics.

Human-editable project/config files may remain conventional files.

---

# 11. Pack versus component versus object

A Pack is a **delivery/organization envelope**.

It may contain one or more components/objects.

Examples:
- Experience definitions;
- faces;
- assets;
- choreography;
- Procedures;
- Doctor knowledge;
- progression definitions;
- optional media;
- declarative Surfaces.

A Pack may be:

- intentionally indivisible and small; or
- componentized where meaningful.

Do not require artificial component splitting merely for architecture purity.

Optional components are valuable when size or hardware/display differences justify them.

Examples:
- high-resolution media;
- alternate sound bundle;
- language bundle;
- large cinematic set;
- target-specific assets.

---

# 12. Collection

A **Collection** is an owner selection, not a package.

Examples:

- My Faces;
- My Experiences;
- Camping Trip;
- Offline Field Set;
- Minimal Set;
- Full Local Set;
- Favorite Cinematics;
- Recovery/Support Tools.

A Collection may reference objects from many Packs/sources.

A Collection does not:

- duplicate those objects by definition;
- confer trust;
- grant executable authority;
- imply all content is currently resident.

Collections are useful inputs to the Storage Budget Manager and Provisioner.

---

# 13. Distribution Profile / Device BOM

A **Distribution Profile/BOM** is different from a Collection.

Collection:
> what optional content/capability selection the owner wants.

Device BOM:
> what full reproducible platform composition this device is expected to have.

BOM may include:

- upstream Pwnagotchi distribution/version/hash;
- Beast version/build;
- component versions;
- Python/runtime;
- OS package requirements;
- display/touch profile;
- plugins/providers;
- selected Packs;
- Collection references;
- storage profile;
- schema/migration levels;
- validation suite;
- known-good fingerprint.

One Device BOM may reference one or more Collections.

---

# 14. Depot

Depot is the discovery/catalog layer.

Depot may answer:

- what exists?
- what source provides it?
- what metadata/version/license is known?
- what compatibility applies?
- what is installed/selected/available?
- what dependencies/providers are required?
- what size/cost is expected?

Depot must keep these distinct:

- catalog entry;
- source trust;
- downloaded artifact;
- verified content;
- installed content;
- active content.

A listing in Depot is **not approval to execute**.

---

# 15. Content Source adapters

Acquisition is mediated by typed Content Source adapters.

Examples:

- GitHub Release;
- local file/import;
- USB/SD library;
- NAS/SFTP/local server;
- future project CDN;
- paired-device/local transfer;
- Capsule/file transport where appropriate.

A source adapter provides:

- discovery/acquisition;
- source metadata;
- integrity/provenance evidence;
- resumability where useful;
- size evidence;
- licensing/source URL evidence.

A source adapter does not activate content.

New executable source adapters require trusted extension authority.

Catalog metadata cannot supply arbitrary downloader code.

---

# 16. Offline-first rule

Cloud/network access is optional.

Core Beast functions, identity, progression, Doctor essentials, active presentation and owner state
must remain useful offline.

Offline preparation should be a first-class Procedure:

**PREPARE DEVICE FOR OFFLINE USE**

Possible plan:

1. select destination Collection/Profile;
2. resolve dependencies;
3. identify remote-only required objects;
4. calculate storage budget;
5. acquire/verify objects;
6. pin active/essential subset;
7. validate providers/content;
8. create summary/report;
9. optionally create backup/known-good checkpoint.

No cloud account is required for normal operation.

---

# 17. Activation is separate from acquisition

Canonical flow:

    discover
      ->
    select
      ->
    plan
      ->
    acquire
      ->
    verify
      ->
    install/register
      ->
    activate
      ->
    observe/verify
      ->
    retain or rollback

Not every content type needs every stage.

Examples:

- inert face: acquire -> verify -> register -> select;
- Experience: acquire -> verify -> register -> compile -> select;
- executable plugin: acquire -> verify -> install -> explicit Action/Transaction activation;
- Doctor knowledge: acquire -> verify -> register; no treatment authority granted by acquisition.

**Invariant:** download/install never silently means enable/run.

---

# 18. Trust and content authority

Content provenance does not equal execution authority.

Examples:

- first-party Pack may be trusted as declarative content;
- external Pack may be schema-valid but untrusted executable code;
- signed artifact may prove publisher identity but still not be authorized to mutate the device;
- Doctor knowledge may be high-confidence evidence without treatment authority.

Trust decisions belong to registration/policy contracts from Parts 2 and 3.

Content Store records trust/provenance; it does not grant it.

---

# 19. Owner-created content

Owner-created content is first-class and must not be treated as disposable cache.

Examples:

- custom Experience;
- custom Scene;
- face;
- Procedure draft;
- owner artwork;
- custom progression/local achievement definition;
- custom Pack;
- local configuration.

Stable rules:

- preserve provenance as owner-created/customized;
- never evict without explicit owner policy;
- include in appropriate backup scope;
- do not require publication;
- do not require a remote source;
- allow export/share separately from local use.

---

# 20. Dependency closure

Installing/selecting content may require a dependency closure across:

- content objects;
- Packs/components;
- Capabilities/providers;
- Python dependencies;
- OS/platform packages;
- hardware;
- versions.

Resolution remains read-only.

If mutation is required:

- content acquisition may use a transaction;
- package/service changes require registered Actions/Transactions;
- hardware absence remains a technical blocker;
- optional fallback may be proposed;
- owner receives a plan before consequential changes.

Do not let a Pack silently install arbitrary OS packages merely because its manifest lists them.

---

# 21. Optional external media and premium content

Large media is optional enrichment.

Examples:

- long cinematics;
- high-resolution art;
- audio packs;
- voice packs;
- large animated sequences.

Every semantically important event must retain a lightweight fallback.

Example:
A Monster reveal may use premium cinematic media when installed.

Without it:
- the reveal still occurs;
- the identity/result is preserved;
- a lightweight Choreography/fallback renders.

Missing optional media must not suppress gameplay/progression truth.

---

# 22. Content retention classes

Working semantic retention classes:

## essential
Required for baseline operation/recovery.

## active_required
Required by current selected runtime state.

## pinned
Owner explicitly wants local availability.

## installed
Local persistent object; ordinary retention.

## cache
Reproducible and evictable.

## external_only
Known/selected but intentionally not materialized locally.

## irreplaceable
Owner-created or otherwise non-reacquirable.

Exact names may evolve; semantics should remain.

---

# 23. Safe eviction

Eviction may target only content whose retention/source semantics permit it.

Before eviction verify:

- not active_required;
- not pinned;
- not irreplaceable;
- source/reacquisition is valid if policy requires;
- dependency graph has no protected consumer;
- resulting free-space change is meaningful.

Eviction should produce Events/provenance where user-visible state changes.

Large automatic cache churn should be avoided.

---

# 24. Backup scope integration

Backup policy distinguishes at least:

## Essential State Backup
Irreplaceable state/config/identity/progression/metadata.

## Full Offline Backup
Essential state plus selected/pinned content necessary to operate without reacquisition.

## Device Clone / Rebuild Manifest
BOM, hashes, source references and owner selections sufficient to reconstruct reproducible content.

Default backup does not need to copy every cache/media object.

Owner-created content is never omitted merely because it resembles Pack content.

---

# 25. Recovery integration

Recovery Vault consumes Content/BOM metadata.

After restore/re-provision it should be able to determine:

- what essential state was restored;
- what local content is present;
- what content is missing but reproducible;
- what selected/pinned objects need reacquisition;
- what source is unavailable;
- what device is customized;
- what cannot be reconstructed automatically.

Doctor explains degraded/missing-content state honestly.

---

# 26. Update integration

Content update uses the same identity/provenance/storage contracts.

Update plan must account for:

- staged new bytes;
- old-version rollback bytes where required;
- temporary peak;
- migration;
- verification;
- active consumer impact.

Do not delete the known-good version before new-version verification when rollback policy requires it.

---

# 27. Licensing / redistribution

Architecture support is not redistribution permission.

For each external component/content source track where practical:

- license;
- upstream source;
- redistribution status;
- attribution/notices;
- acquisition policy.

If redistribution is not permitted or unclear:

- Depot may still describe compatibility;
- Provisioner may acquire from original source where legally/technically appropriate;
- owner may import local copies;
- official Beast distribution should not silently bundle it.

Do not turn availability on GitHub/the Internet into assumed redistribution rights.

---

# 28. Availability and graceful degradation

A missing optional source/content object should produce one of:

- local fallback;
- reduced presentation;
- disabled unavailable option with reason;
- Doctor/Content Store advisory;
- reacquire action.

It should not produce:

- invented data;
- crash loops;
- blank active UI where fallback exists;
- hidden automatic remote fetches;
- silent substitution that changes semantics.

---

# 29. Content observability

Expose compact truth for owner/Doctor/Studio:

- known objects count;
- installed bytes;
- cache bytes;
- pinned bytes;
- active-required bytes;
- pool free/reserve;
- missing selected objects;
- source health;
- verification failures;
- stale catalogs;
- duplicate/dedup savings where available.

Do not make scanning the content universe a permanent expensive loop.

Index/update on bounded triggers/cadence.

---

# 30. Content events

Useful semantic Events may include:

- content.discovered;
- content.acquired;
- content.verified;
- content.installed;
- content.activated;
- content.deactivated;
- content.evicted;
- content.source_lost;
- content.source_restored;
- collection.changed;
- storage.reserve_low;
- storage.plan_blocked.

Event payloads follow privacy/provenance rules.

Do not emit high-frequency noise for every file read.

---

# 31. Content / progression boundary

Availability of progression content does not grant rewards by itself.

Pack/progression definitions register rules/content.

Canonical Progression Engine decides results from truthful Events/State.

Installing:
- an Achievement pack;
- secret content;
- a Rare Moment definition;
- a breeding/synthesis extension;

does not award XP/rarity/lineage outcomes merely because the content exists.

This protects progression provenance while keeping the ecosystem extensible.

---

# 32. Content / presentation boundary

Presentation content may define/decorate:

- Surfaces;
- Scenes;
- Experience DNA;
- faces;
- choreography;
- visual assets.

Presentation cannot invent operational truth.

Scene values must consume registered Signals/State.

Missing Signal remains unavailable/fallback.

A visual Pack may not shadow canonical privacy or mutation authority.

---

# 33. Content / executable extension boundary

Most ecosystem growth should remain declarative.

Executable extensions are justified where genuinely required.

Examples:
- new hardware adapter;
- new protocol/provider;
- new executable Scene primitive;
- new Content Source adapter.

Executable content:

- uses Part 3 trusted registration rules;
- receives bounded handles from Part 2;
- declares resource behavior under Part 5;
- does not receive raw root/Core/DB authority by installation alone.

---

# 34. Content lifecycle state machine

A useful generic object lifecycle:

    catalog_only
       |
    selected
       |
    acquiring
       |
    staged
       |
    verified
       |
    installed/registered
       |
    available
       |
    active
       |
    inactive
       |
    retained / cached / evicted

Terminal/error states may include:

- incompatible;
- verification_failed;
- source_unavailable;
- blocked_storage;
- blocked_dependency;
- retired/deprecated.

Not every object traverses every state.

State must remain inspectable.

---

# 35. Provisioner integration

Provisioner uses:

- Device BOM/Profile;
- Collection;
- Content Store;
- Storage Budget Manager;
- Dependency resolver;
- Transactions;
- Doctor validation.

Provisioner should be able to create:

- Core/Minimal;
- Recommended;
- Full;
- Custom;
- Reference/Development Monster Build;

without creating different incompatible Beast architectures.

A Minimal 16 GB system and a huge reference build are the same platform with different selected
content/capability closure.

---

# 36. Public release artifact discipline

Official project release artifacts should identify:

- exact source/build;
- content/component manifest;
- hashes;
- required dependencies;
- compatibility;
- licenses/notices;
- migration level;
- verification evidence.

The artifact tested is the artifact released.

Do not treat an arbitrary working-tree state as the supported installation definition.

---

# 37. Migration from current v0.19

Incremental path:

1. Define ContentObject/ContentLocation/Retention metadata model.
2. Add Content Store index over current Pack/asset paths without moving bytes yet.
3. Add storage-pool discovery and explicit reserve calculation.
4. Convert Pack/Depot inventory to the five-axis model.
5. Add Collections as owner selections.
6. Add Storage Budget Manager planning.
7. Introduce active-required/pinned locality checks for Experience assets.
8. Add cache eviction only after provenance/reacquisition evidence is reliable.
9. Move large optional media to content-object components progressively.
10. Integrate Provisioner/BOM.
11. Integrate Recovery/backup manifests.
12. Add additional Content Source adapters only as needed.
13. Preserve existing working Pack install/activation flows behind adapters during migration.

No flag-day filesystem rewrite is required.

---

# 38. Content/storage invariants

1. **Known != selected != present != installed != active != resident.**
2. Installed content does not gain execution authority.
3. Active-required content is local or has an explicit usable fallback.
4. External/NAS/cloud storage is optional, never a baseline requirement.
5. Common 16/32 GB cards remain first-class.
6. Optional content cannot consume the protected storage reserve.
7. Irreplaceable owner data is never cache.
8. Reproducible cache is evictable only when retention/dependency policy permits.
9. A source URL/path is not content identity.
10. Catalog presence is not trust.
11. Download success is not verification.
12. Verification is not activation.
13. Pack installation is not plugin/service enablement.
14. Remote availability is not assumed during normal field operation.
15. Missing optional media degrades presentation, not semantic truth.
16. Collections are selections, not packages.
17. Device BOM is reproducibility, not merely content selection.
18. Content Store never grants privileged mutation authority.
19. Storage plans expose temporary peak and post-operation reserve.
20. Owner-created/customized content is preserved and backup-visible.
21. Licensing/redistribution is tracked separately from technical compatibility.
22. Content updates preserve rollback evidence where policy requires it.
23. Progression rewards are not granted merely because content/rules are installed.
24. Presentation content cannot invent live operational state.
25. Most ecosystem content should remain declarative; executable extensions are exceptional/trusted.

---

# 39. Part 6 conclusion

The content/storage system should make Beastagotchi feel effectively unlimited without making the
device itself bloated.

The target experience is:

- browse a huge universe;
- install only what is wanted;
- keep active content locally safe;
- let unused content stay cold;
- use small SD cards comfortably;
- expand onto larger/local/network storage when desired;
- prepare a device for offline use deliberately;
- preserve owner-created state;
- recover/rebuild from provenance;
- keep install/trust/activation distinct.

This contract intentionally supports future growth without choosing one permanent repository host,
one storage device, one Pack granularity or one distribution mechanism.

The next Architecture Contract Review should define the **Beast lifecycle/progression contract**:
identity, Life Ledger, Level/Phase/Form/Rank/Rarity/Mastery/Ascension, provenance/integrity,
Achievements/Rares/Secrets, synthesis/breeding/lineage, reward-depth influence, and how those systems
remain extensible without creating runaway economies or owner-hostile anti-tamper.
