from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_inferred_review_batch import build_batch, machine_observations, render_markdown


def candidate(order: int, status: str, page: int, headword: str, raw: str, separator: str = "em_dash") -> dict[str, str]:
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_pdf_page": str(page),
        "source_printed_page": str(page - 4),
        "page_alignment_status": status,
        "headword_es_ocr": headword,
        "cora_ocr": "X",
        "raw_span_ocr": raw,
        "separator_type": separator,
        "extraction_confidence": "medium",
        "source_ocr_line_start": "10",
        "source_ocr_line_end": "11",
    }


class InferredReviewBatchTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.pages = Path(self.tempdir.name)
        (self.pages / "page-030.txt").write_text("26\nApresurarse.—Viyéta.\nmu-*n\n", encoding="utf-8")
        (self.pages / "page-031.txt").write_text("mu-*n\n27\nApresuramiento.—Viyéfcat.\n", encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_batch_contains_only_inferred_candidates(self):
        rows = [
            candidate(1, "matched_headword", 30, "Apresurarse", "Apresurarse.—Viyéta."),
            candidate(2, "inferred_sequence", 30, "mu", "mu-*n | 27", "hyphen_variant"),
            candidate(3, "matched_headword", 31, "Apresuramiento", "Apresuramiento.—Viyéfcat."),
        ]
        batch = build_batch(rows, self.pages, context_lines=2)
        self.assertEqual(batch["case_count"], 1)
        case = batch["cases"][0]
        self.assertEqual(case["candidate_id"], "ORT1888-cand-000002")
        self.assertFalse(case["human_verified"])
        self.assertTrue(case["facsimile_required"])
        self.assertEqual(case["previous_direct_anchor"]["candidate_id"], "ORT1888-cand-000001")
        self.assertEqual(case["next_direct_anchor"]["candidate_id"], "ORT1888-cand-000003")
        self.assertEqual([item["source_pdf_page"] for item in case["page_evidence"]], [30, 31])

    def test_machine_observations_are_descriptive_not_decisions(self):
        target = candidate(2, "inferred_sequence", 30, "f^y", "f^y-^rziiix | 53", "hyphen_variant")
        previous = candidate(1, "matched_headword", 30, "Gato", "Gato.—Miston.")
        following = candidate(3, "matched_headword", 31, "Gavilán", "Gavilán.—Hucuritze.")
        observations = machine_observations(target, previous, following)
        self.assertIn("symbolic_headword", observations)
        self.assertIn("non_em_dash_separator", observations)
        self.assertIn("raw_span_contains_page_number", observations)
        self.assertIn("between_direct_anchors_on_different_pages", observations)
        self.assertNotIn("reject_false_boundary", observations)

    def test_markdown_preserves_pending_human_decision(self):
        rows = [
            candidate(1, "matched_headword", 30, "A", "A.—X."),
            candidate(2, "inferred_sequence", 30, "mu", "mu-*n | 27", "hyphen_variant"),
            candidate(3, "matched_headword", 31, "B", "B.—Y."),
        ]
        markdown = render_markdown(build_batch(rows, self.pages, context_lines=1))
        self.assertIn("human_verified=false", markdown)
        self.assertIn("Decisión humana:** pendiente", markdown)
        self.assertIn("facsímil requerido: sí", markdown)

    def test_empty_inferred_set_is_valid(self):
        rows = [candidate(1, "matched_headword", 30, "Mar", "Mar.—Vaac.")]
        batch = build_batch(rows, self.pages, context_lines=1)
        self.assertEqual(batch["case_count"], 0)
        self.assertEqual(batch["cases"], [])

    def test_missing_page_evidence_fails_closed(self):
        rows = [candidate(1, "inferred_sequence", 99, "I", "I. — X")]
        with self.assertRaisesRegex(FileNotFoundError, "missing page evidence"):
            build_batch(rows, self.pages, context_lines=1)


if __name__ == "__main__":
    unittest.main()
