from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from summarize_reconciliation_queue import risk_tier, summarize


ROWS = [
    {
        "queue_rank": "1",
        "candidate_id": "ORT1888-cand-000017",
        "candidate_order": "17",
        "source_pdf_page": "20",
        "source_printed_page": "16",
        "priority_score": "120",
        "priority_reasons": "page_alignment_inferred;medium_extraction_confidence",
        "page_alignment_status": "inferred_sequence",
        "extraction_confidence": "medium",
        "headword_es_ocr": "Abeja que cuelga el nido como de un hilo",
    },
    {
        "queue_rank": "2",
        "candidate_id": "ORT1888-cand-000018",
        "candidate_order": "18",
        "source_pdf_page": "20",
        "source_printed_page": "16",
        "priority_score": "10",
        "priority_reasons": "ocr_surface_artifact",
        "page_alignment_status": "matched_headword",
        "extraction_confidence": "high",
        "headword_es_ocr": "Abeja que aun no vuela",
    },
]


class ReconciliationSummaryTests(unittest.TestCase):
    def test_risk_tiers_are_stable(self):
        self.assertEqual(risk_tier(100), "critical_structural_review")
        self.assertEqual(risk_tier(50), "high_priority_review")
        self.assertEqual(risk_tier(20), "medium_priority_review")
        self.assertEqual(risk_tier(19), "baseline_review")

    def test_summary_preserves_machine_only_status(self):
        report = summarize(ROWS, top_n=1)
        self.assertFalse(report["human_verified"])
        self.assertEqual(report["total_candidates"], 2)
        self.assertEqual(report["risk_tiers"]["critical_structural_review"], 1)
        self.assertEqual(report["risk_tiers"]["baseline_review"], 1)
        self.assertEqual(report["priority_reason_counts"]["page_alignment_inferred"], 1)
        self.assertEqual(len(report["top_priority_candidates"]), 1)
        self.assertEqual(
            report["top_priority_candidates"][0]["candidate_id"],
            "ORT1888-cand-000017",
        )


if __name__ == "__main__":
    unittest.main()
