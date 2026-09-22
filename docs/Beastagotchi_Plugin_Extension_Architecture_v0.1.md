# Beastagotchi Plugin & Extension Architecture v0.1

Beastagotchi distinguishes three extension classes:

1. **Pwnagotchi plugins** — remain in Pwnagotchi and use its callback system.
2. **Beast modules/apps** — run beside Pwnagotchi under Beast Core.
3. **Adapters** — translate data/events from an existing Pwnagotchi plugin or external service into canonical Beast state/events.

## Pwnagotchi plugin lifecycle

Planned Beast states are:

`AVAILABLE -> STAGED -> INSTALLED -> ENABLED`

Known/trusted plugins may remain installed with `enabled = false` so activation is quick. Unreviewed plugin code stays staged until compatibility and dependencies are checked.

The installation target is `/etc/pwnagotchi/custom-plugins/`. Plugin-specific Beast-managed configuration should use separate TOML drop-ins under `/etc/pwnagotchi/conf.d/` instead of growing a single monolithic `config.toml`.

Beast Core v0.6 begins exposing an enriched read-only plugin inventory including configured/enabled status, custom-plugin presence, custom plugin directory and available config drop-ins. Mutation/config UI comes after the action broker and rollback system are complete.

## Safety requirements before plugin writes are enabled

Before Beast is allowed to enable/install/configure plugins from the touchscreen, the action path will provide:

- configuration snapshot
- TOML syntax validation
- dependency check
- compatibility fingerprint
- explicit restart requirements
- post-change health observation
- automatic rollback on failure
- change history

Display drawing from legacy plugins will not be allowed to compete with Beast UI. Useful plugin data should flow through a Beast adapter and be rendered by the active Beast theme/layout.
