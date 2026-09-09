from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_reconciliation_decisions import validate_record


CANDIDATES = {
    "ORT1888-cand-000001": {
        "candidate_id": "ORT1888-cand-000001",
        "source_pdf_page": "19",
    },
    "ORT1888-cand-000002": {
        "candidate_id": "ORT1888-cand-000002",
        "source_pdf_page": "20",
    },
}


def valid_record() -> dict:
    return {
        "decision_id": "ORT1888-rec-000001",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "candidate_ids": ["ORT1888-cand-000001"],
        "action": "accept_boundary",
        "source_pdf_pages": [19],
        "reviewer": "Human reviewer",
        "reviewed_at": "2026-09-09T17:00:00-06:00",
        "rationale": "Boundary confirmed against the facsimile.",
        "human_verified": True,
    }


class ReconciliationDecisionValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_decision(self):
        self.assertEqual(
            validate_record(valid_record(), CANDIDATES),
            "ORT1888-rec-000001",
        )

    def test_rejects_machine_style_false_human_flag(self):
        record = valid_record()
        record["human_verified"] = False
        with self.assertRaisesRegex(ValueError, "human_verified"):
            validate_record(record, CANDIDATES)

    def test_rejects_missing_candidate_source_page(self):
        record = valid_record()
        record["source_pdf_pages"] = [18]
        with self.assertRaisesRegex(ValueError, "omits candidate pages"):
            validate_record(record, CANDIDATES)

    def test_merge_requires_multiple_candidates(self):
        record = valid_record()
        record["action"] = "merge_candidates"
        with self.assertRaisesRegex(ValueError, "at least two"):
            validate_record(record, CANDIDATES)

    def test_valid_merge_can_span_multiple_pages(self):
        record = valid_record()
        record["action"] = "merge_candidates"
        record["candidate_ids"] = [
            "ORT1888-cand-000001",
            "ORT1888-cand-000002",
        ]
        record["source_pdf_pages"] = [19, 20]
        self.assertEqual(
            validate_record(record, CANDIDATES),
            "ORT1888-rec-000001",
        )

    def test_split_requires_two_proposed_spans(self):
        record = valid_record()
        record["action"] = "split_candidate"
        record["proposed_spans"] = [
            {"source_ocr_line_start": 547, "source_ocr_line_end": 548}
        ]
        with self.assertRaisesRegex(ValueError, "at least two proposed_spans"):
            validate_record(record, CANDIDATES)

    def test_split_accepts_ordered_positive_spans(self):
        record = valid_record()
        record["action"] = "split_candidate"
        record["proposed_spans"] = [
            {"source_ocr_line_start": 547, "source_ocr_line_end": 547},
            {"source_ocr_line_start": 548, "source_ocr_line_end": 548},
        ]
        self.assertEqual(
            validate_record(record, CANDIDATES),
            "ORT1888-rec-000001",
        )


if __name__ == "__main__":
    unittest.main()
