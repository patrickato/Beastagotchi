# Base Pwnagotchi → Beastagotchi Integration Audit v0.1

Audit target: current Jayofelony Pwnagotchi callback/peer surfaces versus the
v0.19 Beast Bridge and Beast Core.

## Already consumed well

- on_ready → bridge ready/mode
- on_channel_hop → live hop/channel event
- on_wifi_update → filtered AP/client counts
- on_unfiltered_ap_list → unfiltered AP count
- on_epoch → activity/blind/sad/bored/inactive/missed/deauth/assoc/handshake/peer/bond metrics
- on_handshake → durable Beast event
- on_association → durable Beast event
- on_deauthentication → durable Beast event
- on_peer_detected / on_peer_lost → callback path exists
- bored/sad/excited/lonely/sleep/wait moods → Beast-visible mood
- Pwnagotchi config/plugin inventory → safe parsed collector
- session statistics → peer/handshake/deauth/association fallback
- handshake/cache metadata → historical capture namespace
- native face/status bridge → Native Pwnagotchi presentation support

## Underused and now prioritized

### Peer object detail
Before this audit the bridge counted peers but discarded identity/name/RSSI/
channel/encounter/version/face/counter data. v0.19 PeerDex work closes this gap.

### on_rebooting
Callback exists upstream but Beast Bridge does not currently export it.
Add as lifecycle event/state.

### on_internet_available
Useful corroborating signal for connectivity/update/global-interaction readiness.
Beast already has independent route/Internet truth, so treat this as secondary
Pwnagotchi state rather than authority.

### on_free_channel
Can feed passive channel-history/context and future cooperative survey UX.
Do not use it to silently alter radio behavior.

### grateful mood
Current Pwnagotchi emits grateful when peer support offsets negative mood.
Bridge currently misses it. Add to canonical mood set.

### unload/lifecycle
on_unload can make bridge state explicitly unavailable instead of waiting for
staleness timeout.

### Current peer advertisement detail
The local Pwnagotchi's own advertised face/name/version/identity/epoch/uptime
could be surfaced read-only for debugging/peer-protocol diagnostics without
publishing it globally.

## Potential reads that need deliberate adapters

- pwngrid local API peer list for richer current-nearby snapshot/recovery after
  Beast Bridge restart;
- peer first_met/first_seen/prev_seen timestamps;
- Pwnagotchi inbox/grid message surfaces where enabled;
- current Pwnagotchi status/face transitions beyond mood callbacks;
- recovery/session history file for diagnostic continuity;
- strategy/channel statistics where they provide useful read-only telemetry;
- configured personality policy values shown as explanation/context;
- plugin-specific useful telemetry through adapters instead of UI scraping.

## Intentionally not mirrored blindly

- arbitrary Bettercap command execution;
- private keys / pwngrid key material;
- credentials/tokens from config;
- raw plugin secrets;
- every UI refresh callback;
- high-rate duplicate AP lists when Bettercap already provides canonical live data;
- internal implementation state with no user value;
- any write path that would make Beast Core silently control Pwnagotchi behavior.

## Principle

If base Pwnagotchi already knows something useful, Beastagotchi should generally
**consume it once and normalize it**, not re-scan/recompute it independently.
But Pwnagotchi remains the protected engine: read/callback bridges are preferred
over patches, monkey-patching, HTML scraping or competing radio control.
