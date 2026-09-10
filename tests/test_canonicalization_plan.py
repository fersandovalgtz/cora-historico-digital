from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from plan_canonicalization import build_plan


def candidate(order: int, start: int | None = None, end: int | None = None) -> dict[str, str]:
    start = start if start is not None else order * 10
    end = end if end is not None else start + 4
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_page": str(20 + order),
        "source_printed_page": str(16 + order),
        "page_alignment_status": "matched_headword",
        "source_ocr_line_start": str(start),
        "source_ocr_line_end": str(end),
    }


def decision(number: int, action: str, candidate_ids: list[str], **extra):
    record = {
        "decision_id": f"ORT1888-rec-{number:06d}",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "action": action,
        "candidate_ids": candidate_ids,
        "source_pdf_pages": [21, 22, 23, 24, 25, 26],
        "reviewer": "Human Reviewer",
        "reviewed_at": "2026-09-09T18:00:00-06:00",
        "rationale": "Synthetic human-reviewed test fixture.",
        "human_verified": True,
    }
    record.update(extra)
    return record


class CanonicalizationPlanTests(unittest.TestCase):
    def test_plan_materializes_accept_merge_split_and_reject(self):
        candidates = {
            row["candidate_id"]: row
            for row in [
                candidate(1),
                candidate(2),
                candidate(3),
                candidate(4, 40, 49),
                candidate(5),
            ]
        }
        decisions = [
            decision(1, "accept_boundary", ["ORT1888-cand-000001"]),
            decision(2, "merge_candidates", ["ORT1888-cand-000002", "ORT1888-cand-000003"]),
            decision(
                3,
                "split_candidate",
                ["ORT1888-cand-000004"],
                proposed_spans=[
                    {"source_ocr_line_start": 46, "source_ocr_line_end": 49},
                    {"source_ocr_line_start": 40, "source_ocr_line_end": 45},
                ],
            ),
            decision(4, "reject_false_boundary", ["ORT1888-cand-000005"]),
        ]

        plan = build_plan(candidates, decisions)

        self.assertTrue(plan["ready_for_canonicalization"])
        self.assertTrue(plan["derived_from_human_verified_decisions"])
        self.assertEqual(plan["planned_article_total"], 4)
        self.assertEqual(plan["excluded_candidate_total"], 1)
        self.assertEqual(
            [article["article_id"] for article in plan["articles"]],
            [
                "ORT1888-art-000001",
                "ORT1888-art-000002",
                "ORT1888-art-000003",
                "ORT1888-art-000004",
            ],
        )
        self.assertEqual(
            [article["source_type"] for article in plan["articles"]],
            ["accepted_candidate", "merged_candidates", "candidate_span", "candidate_span"],
        )
        self.assertEqual(plan["articles"][2]["source_ocr_span"]["source_ocr_line_start"], 40)
        self.assertEqual(plan["articles"][3]["source_ocr_span"]["source_ocr_line_start"], 46)
        self.assertEqual(
            plan["excluded_candidates"][0]["candidate_id"], "ORT1888-cand-000005"
        )

    def test_plan_is_deterministic_when_decisions_arrive_out_of_order(self):
        candidates = {
            row["candidate_id"]: row for row in [candidate(1), candidate(2), candidate(3)]
        }
        decisions = [
            decision(3, "accept_boundary", ["ORT1888-cand-000003"]),
            decision(1, "accept_boundary", ["ORT1888-cand-000001"]),
            decision(2, "accept_boundary", ["ORT1888-cand-000002"]),
        ]
        plan = build_plan(candidates, decisions)
        self.assertEqual(
            [article["source_candidate_ids"][0] for article in plan["articles"]],
            [
                "ORT1888-cand-000001",
                "ORT1888-cand-000002",
                "ORT1888-cand-000003",
            ],
        )

    def test_incomplete_human_coverage_blocks_plan(self):
        candidates = {row["candidate_id"]: row for row in [candidate(1), candidate(2)]}
        decisions = [decision(1, "accept_boundary", ["ORT1888-cand-000001"])]
        with self.assertRaisesRegex(ValueError, "1 candidates lack human decisions"):
            build_plan(candidates, decisions)

    def test_defer_uncertain_blocks_plan(self):
        row = candidate(1)
        candidates = {row["candidate_id"]: row}
        decisions = [decision(1, "defer_uncertain", [row["candidate_id"]])]
        with self.assertRaisesRegex(ValueError, "1 candidates are defer_uncertain"):
            build_plan(candidates, decisions)

    def test_noncontiguous_merge_blocks_plan(self):
        candidates = {
            row["candidate_id"]: row for row in [candidate(1), candidate(2), candidate(3)]
        }
        decisions = [
            decision(1, "merge_candidates", ["ORT1888-cand-000001", "ORT1888-cand-000003"]),
            decision(2, "reject_false_boundary", ["ORT1888-cand-000002"]),
        ]
        with self.assertRaisesRegex(ValueError, "contiguous candidate orders"):
            build_plan(candidates, decisions)

    def test_split_spans_must_be_nonoverlapping_and_inside_candidate(self):
        row = candidate(1, 100, 110)
        candidates = {row["candidate_id"]: row}
        overlapping = [
            decision(
                1,
                "split_candidate",
                [row["candidate_id"]],
                proposed_spans=[
                    {"source_ocr_line_start": 100, "source_ocr_line_end": 105},
                    {"source_ocr_line_start": 105, "source_ocr_line_end": 110},
                ],
            )
        ]
        with self.assertRaisesRegex(ValueError, "split spans overlap"):
            build_plan(candidates, overlapping)

        outside = [
            decision(
                2,
                "split_candidate",
                [row["candidate_id"]],
                proposed_spans=[
                    {"source_ocr_line_start": 99, "source_ocr_line_end": 100},
                    {"source_ocr_line_start": 101, "source_ocr_line_end": 110},
                ],
            )
        ]
        with self.assertRaisesRegex(ValueError, "falls outside"):
            build_plan(candidates, outside)

    def test_duplicate_candidate_order_blocks_deterministic_ids(self):
        first = candidate(1)
        second = candidate(2)
        second["order"] = "1"
        candidates = {first["candidate_id"]: first, second["candidate_id"]: second}
        decisions = [
            decision(1, "accept_boundary", [first["candidate_id"]]),
            decision(2, "accept_boundary", [second["candidate_id"]]),
        ]
        with self.assertRaisesRegex(ValueError, "candidate order 1 is duplicated"):
            build_plan(candidates, decisions)

    def test_build_plan_rejects_nonhuman_decision_even_when_called_directly(self):
        row = candidate(1)
        candidates = {row["candidate_id"]: row}
        record = decision(1, "accept_boundary", [row["candidate_id"]])
        record["human_verified"] = False
        with self.assertRaisesRegex(ValueError, "human_verified must be the JSON boolean true"):
            build_plan(candidates, [record])


if __name__ == "__main__":
    unittest.main()
