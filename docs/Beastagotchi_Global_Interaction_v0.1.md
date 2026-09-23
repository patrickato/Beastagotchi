# Global Interaction — Beastagotchi architecture v0.1

Global Interaction is an **optional social/community surface** in Beast Studio.
Beastagotchi must remain fully useful offline and without an account.

## What it can become

The WebUI may eventually expose a Global tab with:

- public Beast/Monster profiles intentionally published by owners;
- world/community activity feed using coarse, privacy-safe metadata;
- community Experience/Theme/Face/Animation/Board/Lineage discovery;
- public achievement/trophy showcases;
- opt-in friend/follow/favorite lists;
- Lineage Capsule exchange;
- global/community challenges;
- seasonal events;
- community rarity discoveries;
- Pack/Experience recommendations;
- optional meetup/event discovery;
- public Hall of Legends entries;
- anonymous aggregate statistics such as active lineages or achievement rarity.

## Privacy boundary

Default state: **OFF**.

Global Interaction must never upload by default:
- captured handshakes;
- SSIDs/BSSIDs/client addresses;
- credentials/tokens;
- precise GPS or travel history;
- private logs;
- local files;
- plugin secrets;
- owner identity;
- full Pwnagotchi peer history.

Possible public fields are explicit allow-list selections:
- public Beast ID / display name;
- active creature public name;
- lineage/kind/generation;
- level/evolution stage if owner enables it;
- selected public titles/achievements;
- sanitized Experience/appearance identifiers;
- Lineage Capsule descriptor;
- coarse country/region only if the owner separately enables it.

## Architecture recommendation

Do not make Beast Core itself depend on a social cloud.

Preferred layering:

Beast Core / local DB
→ privacy sanitizer + explicit publish profile
→ Global Interaction connector
→ community service

The connector can be disabled/uninstalled while all local features continue.

Use outbound HTTPS/WebSocket through the management/Internet route, never the
monitor interface. Queue bounded outbound events and retry with backoff.

## Identity

Keep identities distinct:

1. pwngrid fingerprint = local Pwnagotchi encounter identity;
2. Beast public identity = opt-in social identity;
3. owner/account identity = optional service concern, not required by Core;
4. lineage capsule identity = signed/verified portable ancestry object.

Never expose the raw pwngrid fingerprint globally by default.

## Global versus nearby

Nearby Pwnagotchi encounter:
- works offline;
- works with ordinary Pwnagotchi;
- uses pwngrid identity locally.

Nearby Beast encounter:
- adds optional Beast descriptor/capsule exchange.

Global interaction:
- does not require physical proximity;
- requires Internet or another intentional relay;
- should exchange only owner-approved public/sanitized data.

## First implementation gates

1. build local PeerDex first;
2. create public-profile sanitizer/schema;
3. add Global Interaction page in Beast Studio showing disabled/local-only state;
4. define connector interface so backend provider can change later;
5. support import/export of Lineage Capsules before automatic remote exchange;
6. prototype community directory against a test/local server;
7. add authentication only if actually needed;
8. add abuse/report/block/rate-limit controls before public deployment;
9. conduct explicit privacy/security review before default community release.

