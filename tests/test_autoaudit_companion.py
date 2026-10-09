"""Source-level guardrail tests for the optional AutoAudit companion."""
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.autoaudit.runner import load_config, scan


class AutoAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inbox = self.root / "inbox"
        self.inbox.mkdir()
        self.config = {
            "inbox": str(self.inbox), "workdir": str(self.root / "work"),
            "approved_bssids": frozenset({"001122334455"}),
            "auto_run_hashcat": False, "settle_seconds": 1,
        }
        self.capture = self.inbox / "test.pcapng"
        self.capture.write_bytes(bytes.fromhex("0a0d0d0a") + b"\x00" * 48)
        old = time.time() - 120
        os.utime(self.capture, (old, old))

    def _line(self, ap):
        return "WPA*02*" + ("aa" * 16) + "*" + ap + "*66778899aabb*74657374*" + ("00" * 32) + "*" + ("dd" * 32) + "*02\n"

    def test_empty_scope_rejected(self):
        path = self.root / "config.json"
        path.write_text(json.dumps({
            "inbox": "inbox", "workdir": "work", "approved_bssids": [],
            "acknowledged_authorized": True}))
        with self.assertRaises(ValueError):
            load_config(path)

    def test_missing_acknowledgment_rejected(self):
        path = self.root / "config.json"
        path.write_text(json.dumps({
            "inbox": "inbox", "workdir": "work",
            "approved_bssids": ["00:11:22:33:44:55"]}))
        with self.assertRaises(ValueError):
            load_config(path)

    def test_unapproved_never_emitted_or_dispatched(self):
        def fake(cmd, **kwargs):
            self.assertEqual(cmd[0], "hcxpcapngtool")
            Path(cmd[cmd.index("-o") + 1]).write_text(self._line("ffffffffffff"))
            return SimpleNamespace(returncode=0)

        self.config["auto_run_hashcat"] = True
        self.config["wordlist"] = str(self.root / "words.txt")
        (self.root / "words.txt").write_text("labexample\n")
        with patch("tools.autoaudit.runner.subprocess.run", side_effect=fake) as mock:
            state = scan(self.config)
            self.assertEqual(mock.call_count, 1)
        self.assertEqual(state["counts"].get("not_approved"), 1)
        self.assertEqual(list((self.root / "work" / "approved").iterdir()), [])

    def test_mixed_capture_exports_only_approved_candidate(self):
        def fake(cmd, **kwargs):
            Path(cmd[cmd.index("-o") + 1]).write_text(
                self._line("ffffffffffff") + self._line("001122334455"))
            return SimpleNamespace(returncode=0)

        with patch("tools.autoaudit.runner.subprocess.run", side_effect=fake) as mock:
            state = scan(self.config)
            self.assertEqual(mock.call_count, 1)
        self.assertEqual(state["counts"].get("verified"), 1)
        outputs = list((self.root / "work" / "approved").glob("*.hc22000"))
        self.assertEqual(len(outputs), 1)
        contents = outputs[0].read_text()
        self.assertIn("001122334455", contents)
        self.assertNotIn("ffffffffffff", contents)
        with patch("tools.autoaudit.runner.subprocess.run") as mock:
            scan(self.config)
            mock.assert_not_called()  # unchanged capture is deduplicated

    def test_recent_capture_not_processed(self):
        os.utime(self.capture, None)
        with patch("tools.autoaudit.runner.subprocess.run") as mock:
            state = scan(self.config)
            mock.assert_not_called()
        self.assertEqual(state["counts"], {})

    def test_wrong_capture_magic_not_processed(self):
        self.capture.write_bytes(b"NONE" + b"x" * 50)
        old = time.time() - 120
        os.utime(self.capture, (old, old))
        with patch("tools.autoaudit.runner.subprocess.run") as mock:
            state = scan(self.config)
            mock.assert_not_called()
        self.assertEqual(state["counts"], {})


if __name__ == "__main__":
    unittest.main()
