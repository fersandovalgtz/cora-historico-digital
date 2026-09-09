from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from source_integrity import verify_locked_sources


class SourceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.pdf = self.root / "source.pdf"
        self.text = self.root / "source.txt"
        self.pdf.write_bytes(b"stable pdf witness")
        self.text.write_bytes(b"stable text witness")
        self.lock = self.root / "source_lock.json"
        self.write_lock()

    def tearDown(self):
        self.tempdir.cleanup()

    @staticmethod
    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def write_lock(self):
        self.lock.write_text(
            json.dumps(
                {
                    "expected_sha256": {
                        "pdf": self.digest(b"stable pdf witness"),
                        "djvu_text": self.digest(b"stable text witness"),
                    }
                }
            ),
            encoding="utf-8",
        )

    def test_accepts_exact_locked_sources(self):
        observed = verify_locked_sources(
            {"pdf": self.pdf, "djvu_text": self.text}, self.lock
        )
        self.assertEqual(observed["pdf"], self.digest(b"stable pdf witness"))
        self.assertEqual(observed["djvu_text"], self.digest(b"stable text witness"))

    def test_rejects_checksum_drift(self):
        self.text.write_bytes(b"changed text witness")
        with self.assertRaisesRegex(ValueError, "checksum drift"):
            verify_locked_sources(
                {"pdf": self.pdf, "djvu_text": self.text}, self.lock
            )

    def test_rejects_missing_source_key(self):
        with self.assertRaisesRegex(ValueError, "missing source keys"):
            verify_locked_sources({"pdf": self.pdf}, self.lock)

    def test_rejects_unexpected_source_key(self):
        with self.assertRaisesRegex(ValueError, "unexpected source keys"):
            verify_locked_sources(
                {
                    "pdf": self.pdf,
                    "djvu_text": self.text,
                    "extra": self.text,
                },
                self.lock,
            )

    def test_rejects_missing_file(self):
        self.text.unlink()
        with self.assertRaisesRegex(ValueError, "does not exist"):
            verify_locked_sources(
                {"pdf": self.pdf, "djvu_text": self.text}, self.lock
            )


if __name__ == "__main__":
    unittest.main()
