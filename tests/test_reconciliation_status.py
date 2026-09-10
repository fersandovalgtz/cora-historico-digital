from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from summarize_reconciliation_status import summarize_status


CANDIDATES = {
    "ORT1888-cand-000001": {"page_alignment_status": "matched_headword"},
    "ORT1888-cand-000002": {"page_alignment_status": "anchored_same_page"},
    "ORT1888-cand-000003": {"page_alignment_status": "inferred_sequence"},
}


def decision(decision_id: str, candidate_id: str, action: str = "accept_boundary") -> dict:
    return {
        "decision_id": decision_id,
        "candidate_ids": [candidate_id],
        "action": action,
    }


class ReconciliationStatusTests(unittest.TestCase):
    def test_empty_decisions_report_zero_coverage(self):
        status = summarize_status(CANDIDATES, [])
        self.assertEqual(status["candidate_total"], 3)
        self.assertEqual(status["candidate_reconciled"], 0)
        self.assertEqual(status["candidate_pending"], 3)
        self.assertEqual(status["candidate_coverage_percent"], 0.0)
        self.assertFalse(status["decision_coverage_complete"])
        self.assertFalse(status["ready_for_canonicalization"])
        self.assertEqual(
            status["pending_inferred_alignment_candidates"],
            ["ORT1888-cand-000003"],
        )

    def test_complete_terminal_coverage_is_ready(self):
        decisions = [
            decision("ORT1888-rec-000001", "ORT1888-cand-000001"),
            decision("ORT1888-rec-000002", "ORT1888-cand-000002", "reject_false_boundary"),
            decision("ORT1888-rec-000003", "ORT1888-cand-000003"),
        ]
        status = summarize_status(CANDIDATES, decisions)
        self.assertEqual(status["candidate_reconciled"], 3)
        self.assertEqual(status["candidate_pending"], 0)
        self.assertEqual(status["candidate_coverage_percent"], 100.0)
        self.assertTrue(status["decision_coverage_complete"])
        self.assertTrue(status["ready_for_canonicalization"])
        self.assertEqual(status["pending_inferred_alignment_candidates"], [])

    def test_deferred_candidate_blocks_canonicalization_readiness(self):
        decisions = [
            decision("ORT1888-rec-000001", "ORT1888-cand-000001"),
            decision("ORT1888-rec-000002", "ORT1888-cand-000002"),
            decision("ORT1888-rec-000003", "ORT1888-cand-000003", "defer_uncertain"),
        ]
        status = summarize_status(CANDIDATES, decisions)
        self.assertTrue(status["decision_coverage_complete"])
        self.assertFalse(status["ready_for_canonicalization"])
        self.assertEqual(status["deferred_uncertain_candidates"], 1)

    def test_alignment_breakdown_tracks_reconciled_and_pending(self):
        decisions = [decision("ORT1888-rec-000001", "ORT1888-cand-000001")]
        status = summarize_status(CANDIDATES, decisions)
        self.assertEqual(
            status["coverage_by_page_alignment_status"]["matched_headword"],
            {"total": 1, "reconciled": 1, "pending": 0},
        )
        self.assertEqual(
            status["coverage_by_page_alignment_status"]["inferred_sequence"],
            {"total": 1, "reconciled": 0, "pending": 1},
        )

    def test_merge_counts_one_decision_but_multiple_candidates(self):
        merged = {
            "decision_id": "ORT1888-rec-000001",
            "candidate_ids": ["ORT1888-cand-000001", "ORT1888-cand-000002"],
            "action": "merge_candidates",
        }
        status = summarize_status(CANDIDATES, [merged])
        self.assertEqual(status["human_decision_records"], 1)
        self.assertEqual(status["candidate_reconciled"], 2)
        self.assertEqual(status["decision_counts_by_action"]["merge_candidates"], 1)
        self.assertEqual(status["candidate_counts_by_action"]["merge_candidates"], 2)


if __name__ == "__main__":
    unittest.main()
