from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_reconciliation_queue import score_candidate


BASE = {
    "page_alignment_status": "matched_headword",
    "extraction_confidence": "high",
    "multiple_separator_flag": "false",
    "raw_span_ocr": "Casa. — Calli.",
    "source_ocr_line_start": "10",
    "source_ocr_line_end": "11",
}


class ReconciliationQueueScoringTests(unittest.TestCase):
    def test_direct_match_without_other_risk_is_baseline(self):
        score, reasons = score_candidate(dict(BASE))
        self.assertEqual(score, 0)
        self.assertEqual(reasons, ["baseline_review"])

    def test_inferred_alignment_remains_structural_priority(self):
        candidate = dict(BASE)
        candidate["page_alignment_status"] = "inferred_sequence"
        score, reasons = score_candidate(candidate)
        self.assertEqual(score, 100)
        self.assertIn("page_alignment_inferred", reasons)

    def test_same_page_anchor_has_lower_but_visible_priority(self):
        candidate = dict(BASE)
        candidate["page_alignment_status"] = "anchored_same_page"
        score, reasons = score_candidate(candidate)
        self.assertEqual(score, 20)
        self.assertEqual(reasons, ["page_alignment_anchored_same_page"])


if __name__ == "__main__":
    unittest.main()
