#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v03-validation
ARCHIVE=/home/pi/beast-core-validation-v03.tar.gz
rm -rf "$OUT"
mkdir -p "$OUT"

curl -s http://127.0.0.1:8090/health > "$OUT/health.json" || true
curl -s 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json" || true
curl -s 'http://127.0.0.1:8090/state?meta=1' > "$OUT/state_meta.json" || true
curl -s 'http://127.0.0.1:8090/events?limit=100' > "$OUT/events.json" || true
curl -s 'http://127.0.0.1:8090/history?key=system.temp.cpu_c&limit=20' > "$OUT/history_temp.json" || true
systemctl status beast-core pwnagotchi bettercap gpsd --no-pager > "$OUT/services.txt" 2>&1 || true
journalctl -u beast-core --no-pager -n 200 > "$OUT/beast-core-journal.txt" 2>&1 || true
journalctl -u pwnagotchi --no-pager -n 120 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true
if [[ -r /run/beastagotchi/pwnagotchi_bridge.json ]]; then
  cp /run/beastagotchi/pwnagotchi_bridge.json "$OUT/pwnagotchi_bridge.json"
else
  echo '{"missing":true}' > "$OUT/pwnagotchi_bridge.json"
fi

python3 - <<'PY' > "$OUT/websocket_test.txt" 2>&1 || true
import socket,base64,os,json
s=socket.create_connection(('127.0.0.1',8090),timeout=3)
key=base64.b64encode(os.urandom(16)).decode()
req=(f'GET /ws HTTP/1.1\r\nHost: 127.0.0.1:8090\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
s.sendall(req.encode())
b=b''
while b'\r\n\r\n' not in b: b+=s.recv(4096)
head,rest=b.split(b'\r\n\r\n',1)
print(head.decode(errors='replace').splitlines()[0])
def exact(n):
    global rest
    out=rest[:n]; rest=rest[n:]
    while len(out)<n:
        x=s.recv(n-len(out))
        if not x: raise EOFError
        out+=x
    return out
h=exact(2); n=h[1]&127
if n==126: n=int.from_bytes(exact(2),'big')
elif n==127: n=int.from_bytes(exact(8),'big')
payload=exact(n)
obj=json.loads(payload)
print('first_type=',obj.get('type'))
print('state_keys=',len(obj.get('state',{})))
s.close()
PY

tar -czf "$ARCHIVE" -C /tmp beast-v03-validation
if id pi >/dev/null 2>&1; then chown pi:pi "$ARCHIVE"; fi
chmod 0644 "$ARCHIVE"
echo "$ARCHIVE"
