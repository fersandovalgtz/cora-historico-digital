from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from page_alignment import anchor_inferred_same_page, short_headword_exact_line_match


def row(status: str, page: int) -> dict:
    return {
        "page_alignment_status": status,
        "source_pdf_page": page,
    }


class ShortHeadwordMatchingTests(unittest.TestCase):
    def test_matches_mar_as_explicit_entry(self):
        page = "63\nMar.—Vaac.\nMarcar.—Huaoiterit."
        self.assertTrue(short_headword_exact_line_match(page, "Mar"))

    def test_matches_no_as_explicit_entry(self):
        page = "Ninguno.—Busca nadie.\nNo.—-Ehé, capu cañó, canui.\nNo ha mucho.—Aucheámo."
        self.assertTrue(short_headword_exact_line_match(page, "No"))

    def test_rejects_single_letter_noise(self):
        page = "I.\n—\nNteanhtealía"
        self.assertFalse(short_headword_exact_line_match(page, "I"))

    def test_rejects_symbolic_ocr_fragment(self):
        page = "f^y-^rziiix\n53"
        self.assertFalse(short_headword_exact_line_match(page, "f^y"))

    def test_rejects_plain_hyphen_fragment(self):
        page = "mu-*n\n27"
        self.assertFalse(short_headword_exact_line_match(page, "mu"))

    def test_rejects_midline_occurrence(self):
        page = "Busca No.—Ehé."
        self.assertFalse(short_headword_exact_line_match(page, "No"))


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
