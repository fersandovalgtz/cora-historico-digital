from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from page_alignment import anchor_inferred_same_page


def row(status: str, page: int) -> dict:
    return {
        "page_alignment_status": status,
        "source_pdf_page": page,
    }


class PageAlignmentAnchoringTests(unittest.TestCase):
    def test_anchors_between_direct_matches_on_same_assigned_page(self):
        rows = [
            row("matched_headword", 30),
            row("inferred_sequence", 30),
            row("matched_headword", 30),
        ]
        self.assertEqual(anchor_inferred_same_page(rows), 1)
        self.assertEqual(rows[1]["page_alignment_status"], "anchored_same_page")
        self.assertEqual(rows[1]["source_pdf_page"], 30)

    def test_does_not_anchor_across_page_boundary(self):
        rows = [
            row("matched_headword", 30),
            row("inferred_sequence", 30),
            row("matched_headword", 31),
        ]
        self.assertEqual(anchor_inferred_same_page(rows), 0)
        self.assertEqual(rows[1]["page_alignment_status"], "inferred_sequence")

    def test_does_not_change_mismatched_assigned_page(self):
        rows = [
            row("matched_headword", 30),
            row("inferred_sequence", 29),
            row("matched_headword", 30),
        ]
        self.assertEqual(anchor_inferred_same_page(rows), 0)
        self.assertEqual(rows[1]["source_pdf_page"], 29)

    def test_newly_anchored_rows_are_not_reused_as_direct_anchors(self):
        rows = [
            row("matched_headword", 40),
            row("inferred_sequence", 40),
            row("inferred_sequence", 40),
            row("matched_headword", 40),
        ]
        self.assertEqual(anchor_inferred_same_page(rows), 2)
        self.assertEqual(
            [item["page_alignment_status"] for item in rows],
            ["matched_headword", "anchored_same_page", "anchored_same_page", "matched_headword"],
        )

    def test_is_idempotent(self):
        rows = [
            row("matched_headword", 50),
            row("inferred_sequence", 50),
            row("matched_headword", 50),
        ]
        self.assertEqual(anchor_inferred_same_page(rows), 1)
        self.assertEqual(anchor_inferred_same_page(rows), 0)


if __name__ == "__main__":
    unittest.main()
