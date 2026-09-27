# Beastagotchi Capability Expansion — Connectivity / Companion / Home Base Cluster

**Date:** 2026-09-26  
**Status:** active capability-expansion jam; candidate directions, not frozen implementation canon

## 1. Core principle

Beastagotchi should turn networking/connectivity from a set of Linux utilities into a coherent capability family while preserving full owner access to underlying applications and Owner Space.

Use the same layered pattern established elsewhere:

- **Guided** — simple, task-focused Beast experience;
- **Advanced** — deeper controls inside Beast;
- **Full Tool** — launch/use the complete external application;
- **Owner Space** — unrestricted general Linux ownership outside Beast-managed workflows.

## 2. Phone as a first-class companion surface

Potential capabilities:
- responsive WebUI/PWA;
- live Beast status;
- Doctor alerts/approvals;
- notifications;
- upload/download queue;
- file/link/text handoff;
- camera/QR input later;
- local control when on same network;
- secure remote access when explicitly configured;
- show/open exact Beast object from TFT via QR/deep link;
- use phone as a richer interaction surface when TFT would be cramped.

The phone is a companion to the same canonical Beast state, not a second control system.

## 3. Local pairing / trust

Candidate Beast pairing flow:
- discover Beast locally;
- pair with QR/short code;
- establish per-device trust;
- assign permissions/capabilities;
- remember trusted phone/desktop;
- revoke easily;
- no cloud account required for local pairing.

## 4. Local service discovery

Use standard local service discovery (mDNS/DNS-SD-style behavior) so phones/desktops can find Beast and Beast can find owner services without manual IP memorization.

Potential discovered services:
- WebUI/Studio;
- NAS/SMB/NFS endpoints;
- printers;
- media/storage services;
- MQTT broker;
- other Beasts;
- owner-defined Home Base services;
- local documentation/library servers.

## 5. Device / service inventory for owner networks

On authorized/trusted networks, Beast can provide a clean inventory of observed/discovered devices/services:
- host/address/name;
- vendor where determinable;
- known service advertisements;
- first/last seen;
- owner label;
- expected/unknown/new;
- basic availability/latency;
- optional topology relation.

This should prioritize owner-network administration/awareness, not arbitrary third-party intrusion.

## 6. Guided network diagnostics

Task-focused flows can cover:
- Internet unavailable;
- DNS broken;
- gateway unreachable;
- service unreachable;
- high latency/loss;
- Home Base NAS unavailable;
- Beast cannot reach package/docs source;
- phone cannot reach Beast;
- Tailscale/secure remote path unhealthy.

Doctor remains the repair authority; connectivity UI is a user-facing guided doorway.

## 7. Packet capture and analysis

For owner-controlled/authorized interfaces and networks, Beast can support:
- bounded packet capture;
- ring-buffer capture;
- PCAP/PCAPNG import/export;
- protocol summaries;
- flow/timeline visualization;
- DNS/HTTP/TLS metadata analysis where visible;
- troubleshooting-focused filtering;
- handoff to full Wireshark/tcpdump/etc.

Guided example:
`Analyze Capture` -> protocol breakdown / endpoints / timeline / useful explanations.

Full Tool example:
`Open in Wireshark`.

Do not build first-party automation for unauthorized interception, credential theft, stealth, persistence, or exploitation of arbitrary third-party systems.

## 8. Wi-Fi capability separation

Keep separate logical purposes even when they share radios:
- Pwnagotchi/Bettercap radio role;
- owner connectivity role;
- Home Base connectivity;
- local diagnostics;
- optional owner-installed security/lab tools.

Use explicit resource arbitration so managed connectivity and monitor/radio workflows do not silently fight for one adapter.

## 9. Bluetooth / BLE capability family

Potential managed uses:
- discover/pair trusted accessories;
- BLE sensors;
- audio devices;
- keyboards/controllers;
- phone presence/proximity where privacy-appropriate;
- Meshtastic/other supported BLE devices;
- owner-defined BLE providers;
- device health / battery where exposed;
- guided onboarding.

Full Bluetooth tooling remains available outside the guided layer.

## 10. File/link/text handoff

Beast should support easy local movement of ordinary owner data:
- send file to phone/desktop;
- receive file into managed Inbox;
- send/copy text;
- send URL;
- queue for Home Base;
- import Pack/manual/map/config/support artifact;
- export debrief/support bundle/snapshot.

Existing open-source local transfer models such as LocalSend demonstrate cross-platform local/offline file sharing; Beast may integrate or borrow the pattern rather than reinventing every transport.

## 11. Folder synchronization

Potential use of Syncthing-like behavior for owner-selected folders:
- Beast exports;
- manuals/library;
- maps;
- Pack staging;
- backup copies;
- logs/evidence if explicitly selected;
- photos/assets;
- Studio content.

Sync policy should be explicit per folder and direction; not every Beast path becomes a sync folder.

## 12. Home Base as an orchestration context

When trusted network + external power/other configured criteria establish Home Base, Beast can process owner-policy work:
- queued downloads;
- queued uploads;
- NAS sync;
- backup replication/verification;
- map/manual/library updates;
- Global Doctor knowledge exchange;
- update/package staging;
- Pack/content sync;
- support exports;
- cleanup/housekeeping;
- remote-resource acquisition requests;
- optional heavy indexing/build jobs.

Home Base is a context/policy trigger, not a separate scheduler architecture.

## 13. Queued acquisition / delivery

Any subsystem may request a resource for later:
- package;
- driver/helper;
- map region;
- documentation;
- Pack/content;
- dataset;
- model/asset later;
- owner file.

Queue can target:
- next Internet connection;
- Home Base only;
- phone-provided connection;
- manual approval.

After transfer, Beast verifies/sorts/indexes/stages appropriately.

## 14. Secure remote access

Optional Tailscale-style integration can provide owner-controlled remote access without exposing Beast directly to the public Internet.

Possible uses:
- WebUI/Studio remotely;
- SSH for owner/admin;
- file transfer;
- remote support by explicitly trusted devices;
- reach Home Base services;
- optional subnet/exit-node roles where owner intentionally configures them.

Do not enable routing/gateway roles silently.

## 15. Local network bridge to Home Base services

Beast may integrate with owner infrastructure:
- NAS;
- SMB/NFS shares;
- media/library servers;
- backup target;
- MQTT;
- local Git server;
- local package/cache mirror;
- home automation system;
- printer/service endpoints;
- owner APIs.

Beast should discover/configure these as capabilities where possible rather than hardcoding one vendor.

## 16. MQTT/event bridge

A lightweight MQTT broker/client integration can expose or consume selected Beast events/state for owner automation.

Potential examples:
- publish Beast health/status;
- receive owner-approved automation triggers;
- sensor values;
- Home Base arrival;
- Expedition start/end;
- hardware attach/detach;
- Doctor attention state.

Use explicit topic/permission policy; never publish secrets/raw sensitive data by default.

## 17. Notifications

One shared notification service can route to:
- TFT;
- WebUI;
- phone;
- desktop;
- optional MQTT/webhook/etc.

Notification classes may include:
- Doctor needs approval;
- queued download ready;
- backup failed;
- Expedition/Homecoming complete;
- hardware capability appeared;
- storage/power warning;
- update staged;
- user-defined alerts.

## 18. Phone/computer handoff

Small TFT can hand deeper tasks to richer devices:
- `Open in Studio` QR/deep link;
- open exact Doctor case;
- open exact map/debrief;
- upload file from phone;
- approve repair;
- view raw evidence;
- edit complex configuration.

Desktop/phone can reciprocate with `Show on Beast` / preview where practical.

## 19. KDE Connect-style integrated companion possibilities

Potentially useful patterns include:
- notifications;
- clipboard/text sharing;
- files/links;
- remote commands;
- phone battery/device state;
- remote input/media control where useful.

Whether Beast integrates KDE Connect directly or implements a narrower native companion protocol remains open.

## 20. Full-tool handoff

Preserve unrestricted expert pathways:
- Wireshark/tcpdump;
- network manager tools;
- Bluetooth tools;
- Tailscale client;
- Syncthing UI;
- LocalSend;
- SSH/SFTP;
- owner-selected network utilities.

Guided Beast flows never replace the actual application.

## 21. “Abilities” integration

Connectivity capabilities should appear dynamically:
- Local file transfer — Ready;
- Phone paired — Ready;
- Secure remote access — Available / Configure;
- NAS sync — Ready;
- BLE sensing — hardware/provider dependent;
- Packet analysis — Ready;
- Full Wireshark — installed/not installed;
- MQTT bridge — optional;
- Home Base — configured/not configured.

## 22. Walk-the-line boundary

Beast-managed connectivity may go far on owner-controlled/authorized systems:
- discovery/inventory;
- diagnostics;
- packet capture/analysis;
- service discovery;
- configuration;
- secure remote access;
- file/sync/notification workflows;
- Bluetooth/BLE device integration;
- network/lab education;
- launching full tools.

Beast should not ship purpose-built automated workflows for unauthorized intrusion, credential theft, stealth/persistence, bypassing access controls, or exploitation of arbitrary third-party systems.

The platform may still:
- acknowledge that general Linux/security tooling exists;
- expose generic provider/tool/action integration contracts;
- launch owner-installed full applications where appropriate;
- import/export generic artifacts such as PCAPs;
- document required dependencies/interfaces;
- leave Owner Space open for the owner’s own software.

A policy limitation is not presented as a technical impossibility.

## 23. Potential capability composition examples

- Phone + QR + Doctor => approve/inspect a repair without crowding TFT.
- Home Base + Syncthing/NAS => automatically move owner-approved field artifacts home.
- Tailscale + WebUI => secure owner access to Beast away from home.
- mDNS + capability registry => zero-IP local discovery of Beast/services.
- BLE + Provider framework => paired sensor becomes a new Beast sense.
- PCAP + Guided Software + Wireshark => beginner summary plus full expert analysis.
- MQTT + Sensors + Home Base => bridge Beast observations into owner automation.
- Acquisition Queue + phone tether => resource requested in field can be fulfilled when temporary Internet appears.

## 24. Current ecosystem notes

- Tailscale currently supports Linux subnet-router and exit-node roles, with explicit user/admin opt-in for exit-node use.
- Wireshark supports live capture, multiple interfaces, filters, ring-buffer capture and PCAP/PCAPNG analysis; capture privileges are separated through `dumpcap`.
- Syncthing provides cross-device block-based folder synchronization.
- KDE Connect currently supports cross-device files/links, notifications and configurable remote commands across Linux/Android/Windows/macOS/iOS variants.
- LocalSend currently provides encrypted local-network file transfer across Linux/Android/iOS/Windows/macOS without requiring Internet.
- Mosquitto remains an actively maintained MQTT broker/client ecosystem with current ARM64 packages.

These are examples to evaluate/integrate, not mandatory dependencies.

## 25. Status

Strong directions to carry forward:
- phone as first-class companion;
- secure pairing/trust;
- local discovery;
- guided + full-tool network analysis;
- Home Base orchestration;
- file/sync/acquisition queue;
- secure remote access;
- BLE/provider integration;
- notifications;
- capabilities/Abilities view;
- explicit walk-the-line separation between managed, compatible and Owner Space.

Exact protocols, companion app architecture, storage policy, access-control schema and automatic behaviors remain for later implementation design/reconciliation.
