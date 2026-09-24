# Beastagotchi Beast Capsules / Offline Ecosystem — v0.1

**Status:** transport-neutral Capsule codec + lineage export + QR text framing implemented  
**Date:** 2026-09-24

## Product direction

Beastagotchi should support a real **offline/sneakernet ecosystem**, not merely
continue functioning when Internet access disappears.

Portable Beast data should be able to move between devices through several
transports without changing its logical meaning.

A **Beast Capsule** is the portable data object.

Transport is separate.

Examples of transports:
- one QR code;
- animated/multi-frame QR;
- file download/upload;
- USB drive;
- SD card;
- NFC;
- Bluetooth/local direct transfer;
- Beast-to-Beast transport;
- local WebUI/phone.

The same Capsule can therefore survive environments with no Internet and no
shared LAN.

## Initial implemented Capsule

### Lineage Capsule

The first Capsule type is:

`lineage`

It exports a privacy-curated representation of one local creature.

Default payload includes:
- pseudonymous portable creature ID;
- optional creature name;
- Beast/Monster kind;
- lineage identifier;
- generation;
- level;
- stage;
- Hall of Legends flag;
- pseudonymous local parent IDs when known;
- safe appearance traits/mutation when present;
- achievement count.

Achievement IDs are **not** included by default. They can be explicitly included
for later trophy/social workflows.

Not exported:
- local roster IDs;
- raw identity JSON;
- raw preferences;
- counters;
- XP internals;
- captures;
- Wi-Fi/network history;
- credentials/tokens;
- exact GPS/location;
- logs;
- private achievement context.

## Portable public identity

Lineage export creates/uses a separate local Capsule namespace:

`capsulepub-<random>`

A portable creature ID is derived as:

`creature-<hash(capsule namespace | local creature id)>`

This preserves stable identity across repeated Capsule exports from the same
installation while avoiding disclosure of the local SQLite roster ID.

This Capsule namespace is deliberately separate from the optional Global/public
profile identity. Offline sharing should not silently opt a user into Global
publishing.

Future UX should allow namespace rotation with a clear explanation of the
identity consequences.

## BC1 encoding

Implemented module:

`beastcore/capsules.py`

`BeastCapsuleCodec` provides:

- canonical JSON serialization;
- schema/version metadata;
- Capsule ID;
- creation time;
- producer metadata;
- privacy metadata;
- SHA-256 integrity digest;
- zlib compression;
- URL-safe Base64 text encoding;
- bounded decoding/decompression.

Encoded text uses prefix:

`BC1.`

### Integrity is not authenticity

The current SHA-256 digest detects corruption or modification.

It does **not** prove who created the Capsule.

The current envelope therefore explicitly says:

`authenticated: false`

Future signed Capsules may add an identity/signature layer. The UI must never
call an unsigned Capsule "verified owner" or "trusted sender" merely because its
checksum is valid.

## QR framing

The current codec can split a Capsule into bounded QR-ready text frames.

Frame prefix:

`BCQ1`

Each frame contains:
- session ID;
- frame number;
- total frame count;
- per-frame CRC32;
- payload chunk.

Reassembly:
- accepts frames in any order;
- tolerates identical duplicate frames;
- rejects conflicting duplicates;
- rejects mixed Capsule sessions;
- detects frame corruption;
- reports missing frames;
- verifies the reassembled BC1 Capsule.

### What is not implemented yet

The current repository produces **QR-ready text frames**, not QR bitmap images.

No QR rendering dependency was added to the base system.

The current API reports:

`renderer_bundled: false`

A later rendering adapter can turn each text frame into an actual QR image and
cycle them on the TFT/Studio. That should be benchmarked on the target Pi and
should not add a permanent heavy dependency merely to display occasional
Capsules.

Camera/scanner ingestion is also future work.

## Local API

Read-only export:

`GET /capsule/export?type=lineage`

Useful options:
- `beast_id=<local id>`
- `name=0|1`
- `achievements=0|1`
- `appearance=0|1`
- `qr_chars=<bounded frame size>`

Metadata:

`GET /capsule/types`

The export endpoint does not import anything or alter lineage.

## Import boundary

v0.19 Capsule import is **preview-only** at the codec/inspection level.

Decoding a Capsule does not:
- create a Beast;
- modify ancestry;
- award XP;
- grant achievements;
- merge a PeerDex entry;
- enable a Pack;
- run code.

Remote/cross-device lineage import must wait for explicit semantics around:
- duplicate identity;
- ancestry trust;
- signature/authenticity;
- local-vs-remote lineage records;
- synthesis eligibility;
- privacy;
- replay/duplicate attacks;
- owner confirmation.

This is intentionally stricter than simply parsing the data.

## Future Capsule families

### Beast Card / PeerDex Capsule

A compact social calling card:
- public creature identity;
- chosen name;
- lineage/stage;
- selected appearance;
- selected trophies;
- optional capability descriptor.

Scanning can enrich a normal PeerDex encounter without sharing capture history.

### Challenge Capsule

Portable Mission/Challenge definition.

Possible flow:
1. one user creates/selects a challenge;
2. Beast generates Capsule;
3. another Beast imports it offline;
4. canonical mission engine tracks completion;
5. result is recorded in local history.

### Achievement / Trophy Proof Capsule

A privacy-safe signed proof that a specific achievement was earned.

The long-term signature/trust design matters here. A plain self-declared string
must not become authoritative trophy proof.

### Lineage Capsule

Implemented export foundation.

Future use:
- exchange parent lineage identity;
- ancestry graph enrichment;
- offline lineage collaboration;
- later cross-device synthesis rules.

### Configuration Capsule

A selected safe subset of settings/Experience configuration that can be shared
between devices.

Never include secrets by default.

### Pack Reference Capsule

Small Capsule containing:
- Pack identity/version;
- digest;
- optional local file/media reference;
- compatibility metadata.

Large Pack binaries should not be shoved through hundreds of QR frames. A QR can
identify/verify the Pack while USB/SD/file transfer carries the payload.

## Physical relics / printed artifacts

Because Capsules are transport-neutral, QR/NFC objects may become physical
Beastagotchi artifacts.

Examples:
- Beast calling cards;
- lineage cards;
- challenge cards;
- convention/event tokens;
- rare cosmetic relics;
- mission unlocks;
- secret/cipher objects;
- Trophy cabinet artifacts.

Any progression-affecting physical relic must use a canonical, auditable rule.
Scanning arbitrary user data should not directly grant privileged state.

## Witnessed/social achievements

Offline exchange can support richer encounter achievements without requiring a
server.

Example:
- two Beasts meet normally through pwngrid;
- one presents a privacy-safe Beast Card Capsule;
- the receiving Beast associates the richer descriptor with its existing
  encounter record;
- Achievement Engine observes a canonical social event.

The plugin/transport supplies facts. The Achievement Engine grants the trophy.

## Extension ecosystem relationship

A Companion Expansion may advertise:
- Capsule types;
- supported offline transports;
- signals provided/consumed;
- related Beast Apps/Packs;
- related Pwnagotchi plugin.

Example:

**Lineage Exchange Companion**
- Beast Capsule schema/codec;
- Roster/PeerDex adapter;
- QR renderer;
- optional camera scanner;
- trophy/achievement catalog;
- Studio Capsule Workshop;
- optional Pwnagotchi peer bridge.

The user sees one coherent expansion, while the internals remain modular.

## Lightbulb directions

### Animated QR UX

On the 480×320 TFT:
- large QR;
- `FRAME 3 / 8`;
- progress ring/bar;
- pause;
- slower/faster cycle;
- brightness boost while sharing;
- auto-return to prior page.

Receiving phone/Beast can display:
- frames captured;
- missing frame numbers;
- integrity result.

### Air-gap "handshake"

Two isolated Beastagotchis can exchange:
1. Beast Card;
2. challenge;
3. response/proof;

using only their screens/cameras or a phone as a relay.

This may create a useful social system even when neither device joins a network.

### Capsule inbox/outbox

Future Studio:
- Received;
- Created;
- Imported;
- Rejected;
- Expired;
- Shared.

Capsules remain data objects, not hidden executable attachments.

### Capsule Workshop

A Beast App for:
- previewing exactly what will be shared;
- selecting optional fields;
- choosing QR/file/NFC transport;
- inspecting incoming Capsule provenance/integrity;
- exporting a human-readable summary.

### Signed identity

A future device/creature signing key can make signed trophies, Lineage Capsules
and mutual encounter proofs possible.

Key design must account for:
- backup/restore;
- device replacement;
- key rotation;
- clone detection/expectations;
- privacy;
- owner recovery.

Do not bolt signatures on casually.

## Implementation next steps

1. Add actual QR renderer as an optional lightweight adapter/Pack and benchmark
   it on the physical Pi.
2. Add Studio/TFT Capsule preview/share UI.
3. Add scan/import preview without roster mutation.
4. Define signed Capsule identity/authenticity v2.
5. Add PeerDex Beast Card Capsule.
6. Add Challenge Capsule.
7. Define remote-lineage storage separately from local owned Beasts.
8. Only then allow confirmed lineage import/synthesis semantics.
