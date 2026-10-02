# Security and Privacy

Beastagotchi handles device/network telemetry and may contain private configuration. Do not attach raw captures, credentials, GPS coordinates, SSIDs/BSSIDs/client identifiers or private config to public issues.

Use sanitized Beast support bundles for bug reports. Review every archive before publishing it.

Privileged mutations belong behind Beast Core's typed Action Broker. New UI code should not execute arbitrary root shell commands.

## Physical acceptance archives

`beast-v019-accept` deliberately records a curated physical/runtime state subset
and config hashes rather than raw Pwnagotchi configuration or whole canonical
state.

However, framebuffer screenshots preserve whatever was visibly displayed. A
capture taken while Networks, Map, Capture detail, or another sensitive view is
open may contain identifiers or location visible on the TFT.

Treat physical acceptance archives as private diagnostic material by default.
Review/sanitize screenshots before attaching them to a public issue.

