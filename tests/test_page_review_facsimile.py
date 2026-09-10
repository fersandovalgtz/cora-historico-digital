from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from render_page_review_facsimile import render_page_packet, select_reviewable_rows


def candidate(order: int, page: int, status: str = "matched_headword") -> dict[str, str]:
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_page": str(page),
        "source_printed_page": str(max(1, page - 4)),
        "page_alignment_status": status,
        "source_ocr_line_start": str(order * 10),
        "source_ocr_line_end": str(order * 10 + 1),
        "headword_es_ocr": f"Headword {order}",
        "cora_ocr": f"Cora {order}",
        "raw_span_ocr": f"Headword {order}. — Cora {order}.",
        "separator_type": "em_dash",
        "extraction_confidence": "high",
    }


def create_pdf(path: Path, page_count: int = 3) -> None:
    document = fitz.open()
    for number in range(1, page_count + 1):
        page = document.new_page()
        page.insert_text((72, 72), f"Synthetic source page {number}")
    document.save(path)
    document.close()


class PageReviewFacsimileTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.pdf = self.root / "source.pdf"
        create_pdf(self.pdf)
        self.output = self.root / "review"

    def tearDown(self):
        self.tempdir.cleanup()

    def test_selection_excludes_claimed_and_inferred_candidates(self):
        rows = [
            candidate(1, 1),
            candidate(2, 1, "anchored_same_page"),
            candidate(3, 2, "inferred_sequence"),
            candidate(4, 2),
        ]
        reviewable, inferred = select_reviewable_rows(rows, {"ORT1888-cand-000004"})
        self.assertEqual(
            [row["candidate_id"] for row in reviewable],
            ["ORT1888-cand-000001", "ORT1888-cand-000002"],
        )
        self.assertEqual(inferred, ["ORT1888-cand-000003"])

    def test_unknown_alignment_status_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported bulk-review alignment status"):
            select_reviewable_rows([candidate(1, 1, "future_status")], set())

    def test_packet_renders_each_review_page_once_and_stays_machine_only(self):
        rows = [
            candidate(1, 1),
            candidate(2, 1, "anchored_same_page"),
            candidate(3, 2, "inferred_sequence"),
            candidate(4, 2),
            candidate(5, 3),
        ]
        manifest = render_page_packet(
            rows,
            self.pdf,
            self.output,
            claimed_ids={"ORT1888-cand-000005"},
            dpi=96,
        )

        self.assertFalse(manifest["human_verified"])
        self.assertTrue(manifest["facsimile_required"])
        self.assertTrue(manifest["machine_generated"])
        self.assertEqual(
            manifest["reviewable_alignment_statuses"],
            ["anchored_same_page", "matched_headword"],
        )
        self.assertEqual(manifest["candidate_total"], 5)
        self.assertEqual(manifest["already_reconciled_candidate_total"], 1)
        self.assertEqual(manifest["reviewable_candidate_total"], 3)
        self.assertEqual(manifest["excluded_inferred_candidate_total"], 1)
        self.assertEqual(manifest["excluded_inferred_candidate_ids"], ["ORT1888-cand-000003"])
        self.assertEqual(manifest["review_page_total"], 2)
        self.assertEqual([page["source_pdf_page"] for page in manifest["pages"]], [1, 2])
        self.assertEqual(manifest["pages"][0]["candidate_count"], 2)
        self.assertEqual(manifest["pages"][1]["candidate_count"], 1)
        for page in manifest["pages"]:
            self.assertTrue((self.output / page["path"]).is_file())
        self.assertTrue((self.output / "page_review_manifest.json").is_file())

    def test_unknown_claimed_candidate_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "absent from inventory"):
            render_page_packet(
                [candidate(1, 1)],
                self.pdf,
                self.output,
                claimed_ids={"ORT1888-cand-999999"},
            )

    def test_invalid_page_reference_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "document has 3 pages"):
            render_page_packet([candidate(1, 4)], self.pdf, self.output)

    def test_missing_pdf_fails_closed(self):
        with self.assertRaisesRegex(FileNotFoundError, "missing source PDF"):
            render_page_packet([candidate(1, 1)], self.root / "missing.pdf", self.output)

    def test_low_resolution_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "dpi must be at least 72"):
            render_page_packet([candidate(1, 1)], self.pdf, self.output, dpi=71)


if __name__ == "__main__":
    unittest.main()
