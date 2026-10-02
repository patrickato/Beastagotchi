# Beastagotchi Peer Social / Lineage Layer — Architecture v0.1

## Foundation inherited from Pwnagotchi

Current Jayofelony Pwnagotchi already exposes a useful local peer substrate:

- nearby Pwnagotchi units advertise presence through pwngrid-peer;
- peer identity/fingerprint, name, face, RSSI, channel and encounter count are available;
- first-seen / repeated encounters are tracked;
- plugins receive peer-detected and peer-lost callbacks;
- peer presence influences current Pwnagotchi mood/bond state.

Beastagotchi should consume this substrate through Beast Bridge/adapters rather
than replacing or patching pwngrid-peer.

## Important compatibility rule

A nearby device does **not** need Beastagotchi installed for our Beastagotchi to
notice that it is a Pwnagotchi.

Therefore Beastagotchi may record:
- plain Pwnagotchi encounters;
- repeated-friend/bond milestones;
- peer proximity/RSSI;
- first-met/last-seen history;
- encounter achievements;
- Beast-specific XP/collection events derived locally from seeing a peer.

The remote peer may remain completely stock/Jayofelony and know nothing about
Beastagotchi.

## Two levels of interaction

### Level 1 — Pwnagotchi-compatible encounter

Requires:
- local device: Beastagotchi;
- remote device: any compatible Pwnagotchi advertising through pwngrid-peer.

Possible Beast-side behavior:
- add the peer to a persistent PeerDex / social encounter log;
- award first-meeting or reunion XP/achievements;
- let the active Beast react socially;
- track recurring friendships/bond;
- attach encounters to Expeditions and Memory Vault;
- trigger harmless visual/audio/rare-event presentation.

This layer is one-sided from Beastagotchi's perspective. The remote Pwnagotchi
does not need Beast code.

### Level 2 — Beast-to-Beast encounter

Requires:
- both devices running Beastagotchi or another implementation of the compatible
  Beast peer extension.

Beast peers may exchange a small privacy-safe capability/identity descriptor on
top of the normal Pwnagotchi identity.

Potential shared fields:
- Beast public ID;
- active creature public name/lineage;
- creature kind: Beast/Monster;
- generation;
- public level/evolution stage;
- approved cosmetic lineage traits;
- public achievements/titles explicitly safe to advertise;
- Beast protocol version/capabilities;
- optional Lineage Capsule availability.

Must never advertise:
- capture contents;
- Wi-Fi target history;
- credentials/secrets;
- private logs;
- exact GPS history/location;
- device configuration secrets;
- owner identity unless explicitly opted in.

## Social progression

A stock Pwnagotchi encounter can matter locally to Beastagotchi.

Examples:
- First Pwnagotchi Encounter
- Familiar Face — encounter same fingerprint 5 times
- Old Friend — 25 encounters
- Social Butterfly — meet N distinct Pwnagotchi peers
- Expedition Companion — meet a peer during an Expedition
- Reunion — encounter a peer again after a long absence

These should use diminishing/capped XP so two devices sitting beside each other
cannot farm unlimited progression.

## Cross-device lineage / Monster synthesis

Two physical devices do **not** need to remain beside each other while a Monster
is created.

The proposed flow is:

1. Two Beastagotchi-capable peers meet, or users intentionally choose exchange.
2. Each device creates a privacy-safe Lineage Capsule for an eligible local Beast.
3. Capsule exchange occurs through an approved local transport.
4. Each receiving device verifies the capsule and stores only lineage-safe data.
5. Local Lineage Synthesis may use:
   - one local Beast + one imported remote lineage capsule; or
   - another future rule explicitly enabled by the user.
6. The resulting Monster belongs to the local device and has its own local save.

Possible transports, in increasing order of complexity:
- QR code;
- file export/import;
- local WebUI transfer;
- direct Beast peer exchange over nearby networking;
- Bluetooth/BLE where practical;
- Meshtastic/LoRa metadata exchange later.

No cloud server is required.

## Does both sides need Beastagotchi?

For ordinary peer encounters: **no**.

For two-way Beast-specific social data, shared Beast achievements, lineage
capsules or automatic cross-device synthesis: **yes, both sides need a compatible
Beast peer extension**.

This can be Beastagotchi itself or a future compatible implementation of the
published Beast peer protocol.

## Pwnagotchi peer identity as bridge

The existing pwngrid identity/fingerprint is useful as a low-level encounter
identifier. Beastagotchi should not replace it.

Preferred relationship:

```
pwngrid peer fingerprint
       ↓
Pwnagotchi peer encounter
       ↓
Beast peer record
       ↓
optional Beast public identity/capability extension
       ↓
social progression / Lineage Capsule / community features
```

This preserves interoperability with ordinary Pwnagotchi units.

## Future cooperative possibilities

Because current Jayofelony Pwnagotchi no longer uses the old AI cooperation
model, Beast-specific cooperation should be explicit and conservative.

Safe future ideas include:
- show which channels nearby Beast peers are currently observing;
- voluntarily partition passive survey work between consenting Beast peers;
- merge only non-sensitive aggregate field observations;
- coordinated Expedition presence;
- proximity-based team achievements;
- temporary group/party mode;
- peer-to-peer Pack/Experience recommendations;
- local event/rare synchronization;
- Beast Bus / Meshtastic group presence.

Any future radio-task coordination must remain opt-in, transparent, bounded and
must not silently change Pwnagotchi's protected core behavior.

## Resource policy

Peer social state is event-driven and tiny. It should not require a constant
heavy network daemon beyond the existing Pwnagotchi peer substrate. Long-term
peer history belongs in SQLite; only active nearby peers remain in memory.

## Implementation sequence

1. Beast Bridge publishes Pwnagotchi peer_detected / peer_lost into canonical state.
2. Add persistent Beast peer encounter table keyed by pwngrid fingerprint.
3. Add PeerDex / friend/bond summaries.
4. Add capped first-meeting/reunion social XP.
5. Add Beast UI peer encounter presentation.
6. Define Beast peer-extension descriptor and privacy schema.
7. Implement explicit opt-in Beast-to-Beast descriptor exchange.
8. Implement Lineage Capsule export/import.
9. Add optional local peer capsule exchange.
10. Add remote-lineage synthesis rules only after local roster/synthesis is mature.
11. Later evaluate group/party/cooperative survey features.

