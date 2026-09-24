# Beastagotchi Plugin Operations v0.2

## Key point

`main.custom_plugin_repos` tells Pwnagotchi where plugin repositories are. `pwnagotchi plugins update` refreshes/discovers repository contents. Installation remains per plugin with `pwnagotchi plugins install <name>`, followed by plugin-specific configuration and enablement.

The user's current Pwnagotchi configuration already contains the six standard repository URLs supplied by the current Jayofelony defaults, so there is no need to duplicate those URLs simply to use their plugins.

## Why Beast should not blindly install everything

Third-party plugins can require different Python/apt dependencies, expect different Pwnagotchi versions, overlap in responsibilities, manipulate the display, or assume particular radios/GPS/battery hardware. Beast therefore treats repository availability separately from installation and enablement.

## Beast managed states

AVAILABLE -> STAGED -> INSTALLED -> ENABLED

## Planned one-tap workflow

1. Refresh repositories.
2. Build catalog.
3. Compare plugin against Beast compatibility registry.
4. Show dependencies and conflicts.
5. Snapshot Pwnagotchi config.
6. Install plugin.
7. Create/update a dedicated `/etc/pwnagotchi/conf.d/80-beast-<plugin>.toml` fragment.
8. Leave disabled unless the user explicitly enables it.
9. On enable, validate TOML/dependencies/hardware.
10. Restart Pwnagotchi only if necessary.
11. Watch health and automatically offer rollback on failure.

## Config source of truth

Beast should learn plugin config from a curated schema, plugin-supplied metadata when available, and reviewed documentation/code. Arbitrary plugins do not have a universal machine-readable configuration format, so a repo URL alone cannot reliably produce correct config for every plugin.

## v0.19 dependency/capability evolution

Plugin operations are now subordinate to the shared Dependency & Capability
Resolver architecture documented in
`Beastagotchi_Dependency_Capability_Resolver_v0.1.md`.

Before a future install/enable action, Beast should be able to show:

- what the plugin provides;
- mandatory/optional requirements;
- missing software/services/hardware/config/credentials;
- provider overlap;
- conflicts;
- data-egress class;
- reverse `used_by` impact;
- whether Beast can fix a blocker automatically, transactionally, only with
  guidance, or not at all.

The current v0.19 implementation has begun cataloging this metadata but does not
yet install missing dependencies or arbitrate providers.

For the user's reference Pi 4, maintain a complete versioned superset BOM while
keeping the actual installed/runtime set feature-driven. See
`Beastagotchi_Reference_Build_BOM_Strategy_v0.1.md`.

