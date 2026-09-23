# Beast Depot Browser — v0.19 local catalog milestone

Beast Studio now has a real Depot browsing surface backed by persistent catalog
files under `/var/lib/beastagotchi/depot/catalogs/`.

This milestone intentionally separates **discovery** from **trust/acquisition**.

Implemented:
- authenticated catalog JSON import in Beast Studio;
- 1 MiB bounded catalog uploads;
- schema normalization before persistence;
- invalid-entry isolation;
- multiple persistent catalogs;
- combined browser with search and Pack-type filtering;
- local installed/staged Pack comparison by stable Pack ID;
- duplicate-ID conflict reporting across catalogs;
- source repository metadata display;
- explicit `grants_trust=false` and `installs_packs=false` behavior.

Not enabled yet:
- background remote catalog refresh;
- click-to-trust a source;
- click-to-download/acquire a Pack;
- automatic conflict resolution between duplicate catalog entries.

Those later actions must use the existing TrustedSourcePolicy, SHA-256 verified
download staging, Pack intake, transaction and rollback boundaries rather than
letting the browser become a privileged installer.
