# Beastagotchi — Creature Ideas, Opinions & Code Findings

**From:** Claude (independent review)
**Date:** 2026-09-26
**Status:** proposals for the owner to accept, defer or retire under the no-silent-scope-loss rule. Nothing here changes runtime code.

## Scope and baselines

What I read:

- `main` (runtime v0.18.1): README, ROADMAP, Design & Architecture Bible, Continuity Ledger, Completion Matrices v4.4–v4.7, the Adaptive Behavior, Secrets/Achievements, Rare Cinematic and Expeditions specs, the Hardware/Power/Dock, Companion, Beast Packs and Update Manager specs, and the `beastcore`, `beastui` and `pwnagotchi_plugin` code.
- The plugin prototype branch in `patrickato/test-plugins` (`claude/happy-newton-60zxt8`), so these ideas don't duplicate the existing plugins.
- The newest v0.19 branch, `openai/v019-architecture-foundation-tranche1` at `0abb0af`. I re-checked every finding and idea against it. Where v0.19 already covers an idea, the idea is marked accordingly.

Status labels used below:

- **New**: not found in `main`, the v0.19 branch or the plugin backlog.
- **Extends**: builds on something already reserved or partly built; the gap is stated.
- **Covered in v0.19**: already exists on the v0.19 branch; kept here only so the record is complete.

## My overall read

The field-computer half of Beastagotchi is very mature: honest live data, operations, recovery, theming, and now roster, lineage, heritage and Capsules on v0.19. The creature half is still the thinnest part at runtime. The Beast mirrors the device's current state, but it doesn't *want* anything, *remember* anything, or behave differently from anyone else's Beast. v0.19 has added the identity structure for individuality (seed traits, temperament, lineages). The next step is to make that structure drive behaviour. Most of the ideas below target that gap, using data Beast Core already collects.

---

## Part 1 — Code findings

All of these reproduce on both `main` and the v0.19 branch (`0abb0af`). `personality.py` is identical on both. Reproduce with:

```bash
python3 collaboration/claude/tools/personality_mood_sim.py            # this checkout
python3 collaboration/claude/tools/personality_mood_sim.py /path/to/other/tree
```

The script runs the real `PersonalityEngine` and progression curve against simulated state. It touches no device, database or service.

### F1. The mood is effectively stuck on two states

- `ExpeditionEngine._ensure_active()` always creates an expedition if none is active, and `tick()` always publishes `expedition.active = True` (`beastcore/expeditions.py:56`, `:180`). So the `exp` check in `beastcore/personality.py:41` and `:43` is always true while Core runs.
- With the u-blox attached and no fix (normal indoors), `gps.state` is `connected_no_fix`, so the cascade stops at `gps-searching` (`personality.py:41`).
- Otherwise it stops at `hunting` (`personality.py:43`) whenever `quiet < 45`. `quiet` resets on **any** change in `wifi.ap_count` (`personality.py:21`), not on anything new. Bettercap's AP list naturally drifts as APs age in and out of range.

Simulated share of moods over one hour:

| Scenario | Result |
|---|---|
| Indoors, GPS plugged in, no fix (day or night) | `gps-searching` 100% |
| AP count changes about every 20 s (GPS fixed or absent) | `hunting` 93.7%, `curious` 6.3% |
| AP count perfectly static, night | `sleepy` 83%, `idle` 13%, other 4% |

Curious, bored, sleepy and idle effectively only appear if the AP count never moves, which doesn't happen in practice. This is the main reason the Beast feels static. Idea 1 is the proposed fix.

**Smallest interim patch** (if the full needs system is further off):

- Key "quiet" on *new* BSSIDs (session-new or lifetime-first), not on count changes.
- Gate `gps-searching` and `hunting` on an expedition the user actually started, or on motion, rather than on the always-true auto expedition.

### F2. GPS confidence bonus never applies

`personality.py:54` awards +10 confidence when `gps_state == 'locked'`. The GPS collector only ever emits `'fixed'`, `'connected_no_fix'` or `'unavailable'` (`beastcore/collectors/gps.py:72`). This is a one-word fix.

### F3. Uptime dominates XP

`progression.py` awards 1 XP per 600 s of runtime (`:457` on `main`, `:562` on v0.19). Add the runtime achievement bonuses and the level achievement bonuses that follow from them, and a Beast left powered 24/7 reaches:

- **55,670 XP → level 86 (Apex) after one year without going anywhere.**

For scale: level 30 = 9,841 XP, level 50 = 22,779, level 100 = 70,182.

This conflicts with the Adaptive Behavior spec's own rule that XP should reward varied use rather than repetition. **Opinion:** award time XP only for *field* time (`dock.docked` is false), or cap it per day. Keep total uptime for the runtime achievements and records, where longevity belongs.

### F4. Data that arrives and is discarded

- **Satellites:** gpsd's SKY message carries every satellite's PRN, elevation, azimuth, signal strength and whether it's used in the fix. `beastcore/collectors/gps.py:90` only counts them. This is the input for idea 11.
- **Peers (fixed in v0.19):** on `main`, `beast_bridge.py:83` only incremented a counter. The v0.19 branch now forwards identity, name, version, face, RSSI, channel and encounters (`_peer_data`) into a persistent PeerDex. Nothing more is needed here.

### F5. Temperament exists but doesn't affect behaviour yet (v0.19)

`beastcore/heritage.py` derives `TEMPERAMENT_AXES = (curiosity, social, focus, boldness, nocturnal)` and uses them for Monster synthesis inheritance. `PersonalityEngine` doesn't read them, so two Beasts with opposite temperaments behave identically. Idea 2 closes this gap.

---

## Part 2 — Ideas

### The creature: make it want, remember and differ

#### 1. Needs instead of a fixed mood cascade — **New** (fixes F1)

Replace the if-chain with 4–5 persisted needs (0–100) that build up and fade over hours, each fed by real data:

- **Curiosity hunger:** rises with time since a first-ever discovery (lifetime-new AP, vendor, place or map cell). Satisfied only by novelty, so repeated sightings of the same networks can't fake it.
- **Restlessness:** today's GPS distance compared with this Beast's own baseline ("walkies").
- **Loneliness:** time since the last PeerDex encounter.
- **Tiredness:** thermal and throttle history, plus battery state.

Mood becomes the result of needs plus recent events, with hysteresis and expression cooldowns so it doesn't flicker. Pwnagotchi's own epoch counters, which the bridge already exports (`blind`, `bored`, `sad`, `missed`), feed in as additional signals. A long `blind` streak is also a useful radio-health tell.

**Opinion:** neglect should make the Beast sulky or sleepy, never damaged. Needs are persisted to survive restarts, but fade gently while powered off.

#### 2. Temperament drives behaviour — **Extends** `heritage.py`

The seed-derived temperament axes already exist (F5). Let them shift the needs system:

- **curiosity:** how fast curiosity hunger rises;
- **social:** how much peers matter;
- **nocturnal:** when sleepiness sets in;
- **boldness:** how it reacts to heat or faults;
- **focus:** how long it stays on one expression.

Two Beasts in the same room then behave differently at no runtime cost. An optional babble-voice pitch (Animal Crossing style) can come from the same seed if a speaker is fitted.

#### 3. Evolution shaped by how you raise it — **Extends** Lineages

Lineage on v0.19 is a chosen species/archetype. The idea is to add *form variation within a lineage* that depends on how the Beast was actually raised, using data Core already stores:

- mostly walking → a "Strider" form;
- mostly driving → "Roadrunner";
- mostly docked → "Sentinel";
- mostly nocturnal → "Nocturne";
- mostly 5 GHz → "Highband".

This is Tamagotchi/Digimon-style care-dependent evolution. It gives face-pack authors a clear contract: lineage × stage × form.

#### 4. The Beast is the status display (body-language contract) — **New** (fits v0.19)

The Pack SDK allows declared breathing and bob motion, and the fidelity pass treats breathing and blinking as decorative. The proposal is to bind these animation channels to canonical keys, and require every face/animation profile to honour them:

| Channel | Driven by |
|---|---|
| breathing rate | `system.cpu.total` |
| flush / colour temperature | `system.temp.cpu_c` / thermal band |
| posture | `health.core.state` |
| eyes looking up at the sky | GPS searching |
| ear twitch | new discoveries / channel hops |
| stamina | battery |

Profiles still decide *how* each channel looks. The contract only fixes *what* it means. **Opinion:** this is the strongest lever for the v0.19 acceptance criterion, "core status readable at arm's length". Home can drop most of its identical metric boxes because the creature itself carries the status.

#### 5. Petting and an owner bond — **New**

A slow back-and-forth rub on the face (two or more direction reversals inside the face hitbox) can't be mistaken for a page swipe, which is fast and one-way. Touch Lab data can tune the thresholds. The Beast leans in and purrs. Petting, witnessed Rare Moments and being carried on Expeditions build a bond meter with the owner, the owner-side counterpart of Pwnagotchi's peer bonds.

#### 6. Hatching as the setup process — **New** (v0.19 / public release)

First launch shows an egg, and the real first-run steps become the ritual:

1. Tap the egg (touch check).
2. Boot POST passes (the egg glows).
3. First GPS lock (the egg warms under the sky; skippable indoors).
4. Name the Beast from a phone in Beast Studio (typing on a 3.5" resistive screen is miserable).

Then it hatches. The plug-and-play first run needed for outside testers becomes the most memorable moment. The egg's pattern can come from the heritage seed. It also gives every Beast a real birthday. Existing and Founder Beasts use their profile creation time.

### Memory

#### 7. Favourite places — **New**

Group Expedition points into places. The Beast recognises returns ("back at the station — visit 14"), and familiar vs new places feed curiosity hunger. Data stays on the device, like the route data it's built from. (The only related hit on v0.19 is "Haunt" as a naming example in `experience_dna.py`, not a feature.)

#### 8. Old friends and the Departed — **New**

`wifi_encounters.seen_sessions` already counts how many separate Core sessions saw each network. Networks seen across many sessions become "familiar". When a long-familiar network stops appearing for several weeks, it moves to a *Departed* list: "the router on the corner, known 211 days". It's cheap, truthful and oddly moving.

#### 9. Dreams and a Dream Journal — **New**

Present the dock-time work already planned (backup, indexing, OUI updates, map prefetch, Expedition replay) as the Beast sleeping and dreaming, with a slow, dimmed replay of the day's route. In the morning it leaves a Dream Journal card in its own voice: "dreamt of 312 networks by the river, tidied 14 old captures, backed myself up." Invisible maintenance becomes something the owner looks forward to seeing.

### Exploring and collecting

#### 10. A map that reveals itself as you explore — **New** (could land in v0.19)

The Map doesn't need to wait for offline tile packs. Render a grid of roughly 150 m cells (geohash-7 is a ready-made grid) that starts dark and is revealed only where the Beast has actually been, with favourite places, routes and discovery density on top.

- It needs no downloads and can't show fake data.
- "New cells revealed" is exactly the novelty-based XP the spec asks for, and it's the natural replacement for time-based XP (F3).
- Real map tiles can become an optional underlay later.

#### 11. Collect the real stars — **New** (uses F4)

Draw the satellites gpsd already reports as a skyplot, the actual sky above the Beast, and make each satellite PRN a collectible. From the UK, the geostationary EGNOS/SBAS satellites sit low in the southern sky, so they're genuinely rare catches. A `gps-searching` Beast can literally look up at the sky it's searching.

#### 12. Pwnagotchi friends list — **Covered in v0.19** (PeerDex)

Originally proposed after finding that the `main` bridge discarded peer identity. The v0.19 PeerDex already implements it.

#### 13. Beast Cards over QR — **Covered in v0.19** (Beast Capsules)

Originally proposed as StreetPass-style card swapping over QR. The Capsule system already covers it, including Beast Cards and physical QR/NFC relics.

### Rituals and community

#### 14. Quests instead of grinding — **Extends** Challenge Capsules

Challenge Capsules are missions users share with each other. The idea here is a *built-in, automatically rotating* daily and weekly set, seeded from the device secret the same way Rare Moments are:

- walk 2 km;
- spot a network on a DFS channel;
- get a lock on 8+ satellites;
- reveal 5 new map cells;
- run a backup;
- have the Beast on for sunrise.

Every objective is passive observation, movement, learning or maintenance. **Opinion:** this is the missing mechanism behind the spec's "varied use over repetition" rule, and it should feed the same mission engine that Challenge Capsules use.

#### 15. World Moments — **Extends** reserved "distributed-world events"

Rare Moments use a private per-device seed. Add a second schedule derived from a *public* seed, so every Beast in the world gets the same event in the same UTC minute, with no server. People who dig through the code will predict it, like an eclipse, and that's part of the fun: "did anyone witness the Serpent last night?"

#### 16. Birthday and "Wrapped" — **New**

On the hatch anniversary: a special animation plus a year-in-review card (distance, favourite places, friends met, Rare Moments witnessed and missed). Make it privacy-safe by construction: no SSIDs, BSSIDs or coordinates, so it can be shared straight away. A natural Capsule type.

### Practical ideas with creature framing

#### 17. Guarding the den — **Extends** reserved defensive awareness annotations

At home (the dock fingerprint already knows), the Beast guards the owner's own networks, using an own-network list like the `own_network_allowlist` plugin's. It growls when:

- the owner's SSID appears from an unknown BSSID or vendor (a possible impersonating AP);
- the owner's AP changes security, for example a router reset leaves it open.

It's passive and defensive, genuinely useful, and a natural guard-dog role.

#### 18. Grooming is maintenance; the Doctor is the vet — **New**

Present hygiene state as care:

- stale backup → "matted coat";
- storage nearly full → "overfed";
- pending updates → "needs a trim";
- open Black Box incident → "limping", with Beast Doctor as the vet.

The pet-care habit gets owners doing the maintenance the operations layer already supports.

#### 19. Beast Academy — **New**

Short lessons built from what's on the air right now: "14 networks share channel 6 — that's co-channel contention", "this 'hidden' network isn't really hidden, here's why". Finishing a lesson unlocks cosmetics. It fits the project's curiosity-and-learning philosophy and makes owners more knowledgeable, not just more active. Lessons can live as Field Library content with live-data hooks.

#### 20. E-ink pet tag — **New** (hardware)

A 2.13" e-paper panel (the original Pwnagotchi display) on the back of the case, showing the Beast's name, level and a sleeping face. E-paper keeps its image with no power, so when the device is off, the Beast is visibly asleep. It needs one of the Pi 4's spare SPI buses, because the TFT and touch controller use SPI0.

### Smaller ones

- **Face editor in Beast Studio** — **New.** A pixel editor for face packs, with a checklist of the canonical expressions and exact-frame preview, to seed community packs.
- **Traces of missed Rare Moments** — **New.** Scorch marks or footprints shown on the next boot after a window was missed. The engine already records misses.
- **NFC treat figurines** — **Covered in v0.19.** Physical QR/NFC relics in the Capsules spec already cover this.

---

## Part 3 — Recommended order

1. **F1 + F2, then idea 1 (needs) with idea 2 (temperament).** This is small, it's the reason the Beast feels static today, and quests, grooming, dreams and bonding all build on it.
2. **Idea 4 (body-language contract)** as part of the v0.19 Home redesign.
3. **Idea 11 (real sky)** and **idea 10 (self-revealing map).** Both use data already arriving, and together they replace time-based XP (F3) with discovery-based XP.

## Ledger-ready lines

Suggested entries for the next Completion Matrix delta. All are `[ ]` planned unless the owner decides otherwise.

```text
- [ ] Fix personality cascade: novelty-keyed quiet timer; gps-searching/hunting not gated on always-on auto expedition (F1)
- [ ] Fix personality GPS confidence check 'locked' -> 'fixed' (F2)
- [ ] Rebalance runtime XP: field time only or daily cap; uptime stays in runtime achievements/records (F3)
- [ ] Parse gpsd SKY satellite array into canonical keys (F4)
- [ ] Persisted needs system (curiosity hunger / restlessness / loneliness / tiredness) replacing mood cascade
- [ ] Heritage temperament axes bias needs and expression behaviour
- [ ] Care-dependent forms within a lineage (Strider / Roadrunner / Sentinel / Nocturne / Highband)
- [ ] Body-language contract: canonical keys -> breathing/flush/posture/gaze/ears/stamina, honoured by all profiles
- [ ] Petting gesture (face-region rub) and owner bond meter
- [ ] Egg / hatching first-run onboarding tied to real setup checks; hatch date = birthday
- [ ] Favourite places (clustered Expedition points) with return recognition
- [ ] Familiar networks and Departed list from seen_sessions/last_seen
- [ ] Dock-time Dreams presentation and morning Dream Journal card
- [ ] Self-revealing exploration map (geohash-7 cells), tiles optional underlay
- [ ] GNSS skyplot habitat sky and satellite PRN collection
- [ ] Rotating seeded daily/weekly Quests on the mission engine
- [ ] World Moments from a public seed (same UTC minute worldwide)
- [ ] Birthday animation and privacy-safe yearly Wrapped card / Capsule
- [ ] Den guarding: own-network impersonation and security-change alerts
- [ ] Grooming presentation of maintenance state; Doctor as vet
- [ ] Beast Academy live-data lessons
- [ ] E-ink pet tag on secondary SPI bus
- [ ] Beast Studio face-pack pixel editor
- [ ] Missed Rare Moment traces on next boot
```
