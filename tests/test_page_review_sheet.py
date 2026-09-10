from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_page_review_sheet import render_sheet, validate_manifest


def manifest() -> dict:
    return {
        "artifact_type": "facsimile_page_review_packet",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_sha256": "abc123",
        "machine_generated": True,
        "human_verified": False,
        "facsimile_required": True,
        "render_dpi": 120,
        "candidate_total": 3,
        "already_reconciled_candidate_total": 0,
        "reviewable_candidate_total": 2,
        "excluded_inferred_candidate_total": 1,
        "excluded_inferred_candidate_ids": ["ORT1888-cand-000003"],
        "review_page_total": 1,
        "pages": [
            {
                "source_pdf_page": 19,
                "source_printed_pages": [15],
                "path": "pages/page-019-full.png",
                "candidate_count": 2,
                "candidates": [
                    {
                        "candidate_id": "ORT1888-cand-000001",
                        "order": 1,
                        "source_pdf_page": 19,
                        "source_printed_page": 15,
                        "page_alignment_status": "matched_headword",
                        "headword_es_ocr": "A < B",
                        "cora_ocr": "Cora & forma",
                        "raw_span_ocr": "A < B. — Cora & forma.",
                        "separator_type": "em_dash",
                        "extraction_confidence": "high",
                        "source_ocr_line_start": 10,
                        "source_ocr_line_end": 11,
                    },
                    {
                        "candidate_id": "ORT1888-cand-000002",
                        "order": 2,
                        "source_pdf_page": 19,
                        "source_printed_page": 15,
                        "page_alignment_status": "anchored_same_page",
                        "headword_es_ocr": "Abajar",
                        "cora_ocr": "Acátoa",
                        "raw_span_ocr": "Abajar. — Acátoa.",
                        "separator_type": "em_dash",
                        "extraction_confidence": "medium",
                        "source_ocr_line_start": 12,
                        "source_ocr_line_end": 13,
                    },
                ],
            }
        ],
        "method_note": "Synthetic manifest.",
    }


class PageReviewSheetTests(unittest.TestCase):
    def test_manifest_accepts_noninferred_review_candidates(self):
        candidates = validate_manifest(manifest())
        self.assertEqual(
            [candidate["candidate_id"] for candidate in candidates],
            ["ORT1888-cand-000001", "ORT1888-cand-000002"],
        )

    def test_inferred_candidate_is_rejected_from_bulk_review(self):
        payload = manifest()
        payload["pages"][0]["candidates"][1]["page_alignment_status"] = "inferred_sequence"
        with self.assertRaisesRegex(ValueError, "must not enter bulk page review"):
            validate_manifest(payload)

    def test_duplicate_candidate_is_rejected(self):
        payload = manifest()
        payload["pages"][0]["candidates"][1]["candidate_id"] = "ORT1888-cand-000001"
        with self.assertRaisesRegex(ValueError, "duplicate review candidate"):
            validate_manifest(payload)

    def test_sheet_starts_with_all_candidate_inputs_disabled_and_unchecked(self):
        rendered = render_sheet(
            manifest(),
            ["ORT1888-rec-000001", "ORT1888-rec-000002"],
        )
        self.assertEqual(rendered.count('class="candidate-check" type="checkbox"'), 2)
        self.assertEqual(rendered.count('class="candidate-check" type="checkbox" data-candidate='), 2)
        self.assertEqual(rendered.count('disabled aria-label="Aceptar'), 2)
        self.assertNotIn('type="checkbox" checked', rendered)
        self.assertIn('class="select-all" disabled', rendered)

    def test_sheet_requires_reviewer_and_page_confirmation_before_decision(self):
        rendered = render_sheet(
            manifest(),
            ["ORT1888-rec-000001", "ORT1888-rec-000002"],
        )
        reviewer_guard = "if (!reviewer) throw new Error('Escriba el nombre de la persona revisora.')"
        page_guard = "if (!confirmed) throw new Error('Confirme primero la inspección personal de esta página.')"
        human_flag = "human_verified: true"
        self.assertIn(reviewer_guard, rendered)
        self.assertIn(page_guard, rendered)
        self.assertIn(human_flag, rendered)
        self.assertLess(rendered.index(reviewer_guard), rendered.index(human_flag))
        self.assertLess(rendered.index(page_guard), rendered.index(human_flag))
        self.assertIn("action: 'accept_boundary'", rendered)
        self.assertNotIn("action: 'merge_candidates'", rendered)
        self.assertNotIn("action: 'split_candidate'", rendered)
        self.assertNotIn("action: 'reject_false_boundary'", rendered)
        self.assertNotIn("action: 'defer_uncertain'", rendered)

    def test_sheet_escapes_ocr_text(self):
        rendered = render_sheet(
            manifest(),
            ["ORT1888-rec-000001", "ORT1888-rec-000002"],
        )
        self.assertIn("A &lt; B", rendered)
        self.assertIn("Cora &amp; forma", rendered)
        self.assertNotIn("<strong>A < B</strong>", rendered)

    def test_suggested_decision_ids_must_match_candidate_count_and_be_unique(self):
        with self.assertRaisesRegex(ValueError, "count does not match"):
            render_sheet(manifest(), ["ORT1888-rec-000001"])
        with self.assertRaisesRegex(ValueError, "must be unique"):
            render_sheet(
                manifest(),
                ["ORT1888-rec-000001", "ORT1888-rec-000001"],
            )

    def test_manifest_count_mismatch_fails_closed(self):
        payload = manifest()
        payload["reviewable_candidate_total"] = 3
        with self.assertRaisesRegex(ValueError, "reviewable_candidate_total"):
            validate_manifest(payload)


if __name__ == "__main__":
    unittest.main()
