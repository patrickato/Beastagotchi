#!/usr/bin/env bash
cat <<'TXT'
BEASTAGOTCHI PATH QUICK REFERENCE

Core runtime:       /opt/beast-core/beastcore/
UI runtime:         /opt/beast-ui/beastui/
Themes:             /opt/beast-ui/themes/
Touch config:       /opt/beast-ui/config/touch.json
UI tools:           /opt/beast-ui/bin/
Core config:        /etc/beastagotchi/core.toml
Persistent state:   /var/lib/beastagotchi/
Beast database:      /var/lib/beastagotchi/beast.db
Progression profile: /var/lib/beastagotchi/profile.json
UI preferences:      /var/lib/beastagotchi/ui/preferences.json
Rare history:        /var/lib/beastagotchi/secrets/rare_history.json
Secrets/spoilers:    /usr/local/share/beastagotchi/SPOILERS_SECRETS_AND_ACHIEVEMENTS.md
Pwnagotchi config:  /etc/pwnagotchi/config.toml
Pwn plugin dir:     /etc/pwnagotchi/custom-plugins/
Pwn config dropins: /etc/pwnagotchi/conf.d/
Master docs:        /usr/local/share/beastagotchi/BEASTAGOTCHI_MASTER_README.md

Services:
  beast-core.service
  beast-ui.service
  pwnagotchi.service

Useful:
  curl -s http://127.0.0.1:8090/health | python3 -m json.tool
  curl -s http://127.0.0.1:8090/encounters?limit=20 | python3 -m json.tool
  curl -s http://127.0.0.1:8090/achievements | python3 -m json.tool
  systemctl status beast-core beast-ui pwnagotchi
  journalctl -u beast-ui -f
  sudo /opt/beast-ui/bin/display_status.sh
TXT
