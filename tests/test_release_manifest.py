from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_release_manifest import artifact_paths, build_manifest, verify_manifest


class ReleaseManifestTests(unittest.TestCase):
    def make_tree(self, root: Path) -> None:
        files = {
            "data/a.txt": b"alpha\n",
            "data/source/source_lock.json": b"{}\n",
            "data/source/original/source.pdf": b"external binary",
            "reports/z.json": b'{"ok": true}\n',
            "schemas/x.schema.json": b'{"type": "object"}\n',
        }
        for rel, payload in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)

    def test_inventory_is_sorted_and_excludes_downloaded_source_binaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            paths = [p.as_posix() for p in artifact_paths(root)]
            self.assertEqual(paths, sorted(paths))
            self.assertIn("data/source/source_lock.json", paths)
            self.assertNotIn("data/source/original/source.pdf", paths)

    def test_manifest_is_deterministic_and_hashes_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            first = build_manifest(root)
            second = build_manifest(root)
            self.assertEqual(first, second)
            row = next(r for r in first["files"] if r["path"] == "data/a.txt")
            self.assertEqual(row["sha256"], hashlib.sha256(b"alpha\n").hexdigest())
            self.assertEqual(first["release_status"], "candidate")
            self.assertEqual(first["target_version"], "0.1.0")
            verify_manifest(root, first)

    def test_verify_detects_modified_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            manifest = build_manifest(root)
            (root / "reports/z.json").write_text('{"ok": false}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "(size|checksum) mismatch"):
                verify_manifest(root, manifest)

    def test_verify_detects_inventory_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root)
            manifest = build_manifest(root)
            (root / "data/new.txt").write_text("new\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory"):
                verify_manifest(root, manifest)


if __name__ == "__main__":
    unittest.main()
