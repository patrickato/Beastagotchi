#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then echo "Run with sudo: sudo ./install.sh"; exit 1; fi
getent group beastagotchi >/dev/null 2>&1 || groupadd --system beastagotchi
systemctl stop beast-core.service 2>/dev/null || true
install -d -o root -g beastagotchi -m 0750 /var/lib/beastagotchi/support
install -d -m 0755 /opt/beast-core /etc/beastagotchi /var/lib/beastagotchi
rm -rf /opt/beast-core/beastcore
cp -a "$SRC/beastcore" /opt/beast-core/
install -m 0644 "$SRC/config/core.toml" /etc/beastagotchi/core.toml
install -m 0644 "$SRC/systemd/beast-core.service" /etc/systemd/system/beast-core.service
install -m 0755 "$SRC/tools/enroll_home_dock.py" /usr/local/bin/beast-enroll-home
install -m 0755 "$SRC/tools/beast_paths.sh" /usr/local/bin/beast-paths
install -d -m 0755 /usr/local/share/beastagotchi
install -m 0644 "$SRC/docs/BEASTAGOTCHI_MASTER_README_DRAFT.md" /usr/local/share/beastagotchi/BEASTAGOTCHI_MASTER_README.md
install -m 0644 "$SRC/docs/Beastagotchi_Plugin_Operations_v0.2.md" /usr/local/share/beastagotchi/Beastagotchi_Plugin_Operations.md
install -m 0644 "$SRC/docs/Beastagotchi_Secrets_Achievements_Seasonal_Spec_v0.9.md" /usr/local/share/beastagotchi/Beastagotchi_Secrets_Achievements_Seasonal_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Theme_Studio_Spec_v0.10.0.md" /usr/local/share/beastagotchi/Beastagotchi_Theme_Studio_Spec.md
install -m 0644 "$SRC/docs/SPOILERS_SECRETS_AND_ACHIEVEMENTS.md" /usr/local/share/beastagotchi/SPOILERS_SECRETS_AND_ACHIEVEMENTS.md
install -m 0644 "$SRC/docs/Beastagotchi_Rare_Cinematic_Pipeline_v0.9.1.md" /usr/local/share/beastagotchi/Beastagotchi_Rare_Cinematic_Pipeline.md
install -m 0644 "$SRC/docs/Beastagotchi_Touch_Characterization_Report_v1.0.md" /usr/local/share/beastagotchi/Beastagotchi_Touch_Characterization_Report.md
install -m 0644 "$SRC/docs/Beastagotchi_Classic_Identity_and_Korrie71_Integration_v0.9.2.md" /usr/local/share/beastagotchi/Beastagotchi_Classic_Identity_and_Korrie71_Integration.md
install -m 0644 "$SRC/docs/Beastagotchi_Foundation_Roadmap_v2.9.md" /usr/local/share/beastagotchi/Beastagotchi_Foundation_Roadmap.md
install -m 0644 "$SRC/docs/Beastagotchi_Native_Pwnagotchi_Bridge_v0.9.3.md" /usr/local/share/beastagotchi/Beastagotchi_Native_Pwnagotchi_Bridge.md
install -m 0644 "$SRC/docs/Beastagotchi_Master_Completion_Matrix_v4.7.md" /usr/local/share/beastagotchi/Beastagotchi_Master_Completion_Matrix.md
install -m 0644 "$SRC/docs/Beastagotchi_Project_Continuity_Audit_v1.0.md" /usr/local/share/beastagotchi/Beastagotchi_Project_Continuity_Audit.md
install -m 0644 "$SRC/docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md" /usr/local/share/beastagotchi/Beastagotchi_Master_Continuity_Ledger.md
install -m 0644 "$SRC/docs/Beastagotchi_Resource_Governor_Spec_v0.11.md" /usr/local/share/beastagotchi/Beastagotchi_Resource_Governor_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Expeditions_Spec_v0.11.md" /usr/local/share/beastagotchi/Beastagotchi_Expeditions_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Live_Telemetry_Integrity_Spec_v0.13.md" /usr/local/share/beastagotchi/Beastagotchi_Live_Telemetry_Integrity_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Thermal_Efficiency_Strategy_v0.13.md" /usr/local/share/beastagotchi/Beastagotchi_Thermal_Efficiency_Strategy.md
install -m 0644 "$SRC/docs/Beastagotchi_Beast_Studio_Spec_v0.15.md" /usr/local/share/beastagotchi/Beastagotchi_Beast_Studio_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Operations_Knowledge_Spec_v0.16.md" /usr/local/share/beastagotchi/Beastagotchi_Operations_Knowledge_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_Platform_Compatibility_Spec_v0.18.md" /usr/local/share/beastagotchi/Beastagotchi_Platform_Compatibility_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_v017_Source_Validation_Report.md" /usr/local/share/beastagotchi/Beastagotchi_v017_Source_Validation_Report.md
install -m 0644 "$SRC/docs/Beastagotchi_v016_Source_Validation_Report.md" /usr/local/share/beastagotchi/Beastagotchi_v016_Source_Validation_Report.md
install -m 0644 "$SRC/docs/Beastagotchi_v015_Source_Validation_Report_20260921.md" /usr/local/share/beastagotchi/Beastagotchi_v015_Source_Validation_Report.md
install -m 0644 "$SRC/docs/Beastagotchi_Visualization_Studio_Spec_v1.0.md" /usr/local/share/beastagotchi/Beastagotchi_Visualization_Studio_Spec.md
install -m 0644 "$SRC/docs/Beastagotchi_v094_Physical_Validation_Review.md" /usr/local/share/beastagotchi/Beastagotchi_v094_Physical_Validation_Review.md
install -m 0644 "$SRC/docs/Beastagotchi_v095_Physical_Validation_Review.md" /usr/local/share/beastagotchi/Beastagotchi_v095_Physical_Validation_Review.md
systemctl daemon-reload
cat <<'EOF'
Beast Core v0.18.1 Platform / Compatibility milestone installed but NOT enabled or started.
Existing Beast DB is preserved.

Start validation:
  sudo systemctl start beast-core
  sleep 10
  curl -s http://127.0.0.1:8090/health | python3 -m json.tool

Optional read-only Pwnagotchi callback bridge is separate:
  sudo ./install_bridge.sh

No /opt/beastagotchi, /opt/beastagotchi-v1, or /opt/beastagotchi-v1.2 files were modified.
EOF
