from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from render_inferred_facsimile import render_packet


def candidate(order: int, status: str, page: int, headword: str) -> dict[str, str]:
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_pdf_page": str(page),
        "source_printed_page": str(page - 4),
        "page_alignment_status": status,
        "headword_es_ocr": headword,
        "raw_span_ocr": f"{headword} — X",
    }


class FacsimileRenderingTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.pdf = self.root / "source.pdf"
        document = fitz.open()
        for number in range(1, 4):
            page = document.new_page(width=400, height=600)
            page.insert_text((40, 60), f"Synthetic page {number}")
            page.insert_text((40, 540), f"Bottom evidence {number}")
        document.save(self.pdf)
        document.close()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_renders_full_pages_and_boundary_crops(self):
        rows = [
            candidate(1, "matched_headword", 1, "Left"),
            candidate(2, "inferred_sequence", 1, "Noise"),
            candidate(3, "matched_headword", 2, "Right"),
        ]
        output = self.root / "packet"
        manifest = render_packet(rows, self.pdf, output, dpi=72, crop_fraction=0.25)

        self.assertEqual(manifest["case_count"], 1)
        self.assertEqual(manifest["rendered_pdf_pages"], [1, 2])
        self.assertFalse(manifest["human_verified"])
        self.assertTrue(manifest["facsimile_required"])

        case = manifest["cases"][0]
        self.assertEqual(case["candidate_id"], "ORT1888-cand-000002")
        self.assertEqual(
            {asset["role"] for asset in case["boundary_crop_assets"]},
            {"previous_tail", "next_head"},
        )

        for relative in case["full_page_assets"]:
            path = output / relative
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)
        for asset in case["boundary_crop_assets"]:
            path = output / asset["path"]
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)
        self.assertTrue((output / "facsimile_manifest.json").is_file())

    def test_no_unresolved_cases_produces_empty_packet(self):
        rows = [candidate(1, "matched_headword", 1, "Only")]
        output = self.root / "empty"
        manifest = render_packet(rows, self.pdf, output, dpi=72)
        self.assertEqual(manifest["case_count"], 0)
        self.assertEqual(manifest["rendered_pdf_pages"], [])
        self.assertTrue((output / "facsimile_manifest.json").is_file())

    def test_invalid_page_reference_fails_closed(self):
        rows = [candidate(1, "inferred_sequence", 9, "Bad")]
        with self.assertRaisesRegex(ValueError, "document has"):
            render_packet(rows, self.pdf, self.root / "bad", dpi=72)

    def test_missing_pdf_fails_closed(self):
        with self.assertRaisesRegex(FileNotFoundError, "missing source PDF"):
            render_packet([], self.root / "missing.pdf", self.root / "missing", dpi=72)

    def test_rejects_low_dpi(self):
        with self.assertRaisesRegex(ValueError, "dpi"):
            render_packet([], self.pdf, self.root / "lowdpi", dpi=50)


if __name__ == "__main__":
    unittest.main()
