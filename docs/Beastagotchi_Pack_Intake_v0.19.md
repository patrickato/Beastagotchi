# Beast Pack Intake — v0.19 safety foundation

Beastagotchi is intended to grow through optional themes, layouts, faces, apps,
hardware adapters, Mission Packs, data bundles and other downloadable extras.
That ecosystem needs a safe boundary before a public Depot or automatic updater
is allowed to place files onto a device.

## Lifecycle

```
download / local copy
        ↓
/var/lib/beastagotchi/packs/inbox
        ↓
INSPECT
        ↓
VERIFIED
        ↓
/var/lib/beastagotchi/packs/staged/<pack-id>
        ↓
future transactional install
        ↓
installed → enabled / disabled
```

v0.19 implements only the **inspect → verified staging** portion.

## What inspection enforces

- archive must be inside the bounded Beast Pack inbox
- supported intake formats: `.tar.gz`, `.tgz`, `.zip`
- archive-size, unpacked-size and member-count limits
- no absolute paths or `..` traversal
- no symlinks, hardlinks or device nodes
- exactly one root-level pack `manifest.json` (optionally inside one wrapper directory)
- manifest is normalized by the canonical Beast Pack schema
- SHA-256 is recorded
- staging is isolated under the staged-pack registry

## What staging does **not** do

Staging does not:

- execute Python or shell code
- install dependencies
- copy files into live application/plugin directories
- enable a pack
- restart Beast Core, Pwnagotchi or any other service
- mutate the physical display owner
- fetch anything from the network

The Action Broker now understands `pack.inspect` and `pack.stage`, so the
future WebUI/Depot can use audited structured operations instead of arbitrary
shell commands.

## Next gates

Before a public one-click install or auto-update path is enabled, Beastagotchi
still needs:

1. version compatibility checks
2. declared dependency/conflict resolution
3. trusted source/catalog metadata
4. checksum/signature policy
5. pre-install rescue backup
6. transactional install plan
7. service restart plan
8. probation/health observation
9. automatic rollback
10. persistent update/install history

This separation is deliberate: Beast can understand and safely unpack a package
well before it is allowed to trust or activate one.
