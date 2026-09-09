from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lexicon_text import clean_headword_boundary


class HeadwordBoundaryCleaningTests(unittest.TestCase):
    def test_preserves_final_r_in_short_noun(self):
        self.assertEqual(clean_headword_boundary("Mar. "), "Mar")

    def test_preserves_final_r_in_infinitive(self):
        self.assertEqual(clean_headword_boundary("Negociar.—"), "Negociar")

    def test_preserves_final_r_after_legacy_spelling(self):
        self.assertEqual(clean_headword_boundary("Oyr. —"), "Oyr")

    def test_removes_only_boundary_punctuation(self):
        self.assertEqual(clean_headword_boundary("Casa .,:;^-"), "Casa")

    def test_does_not_strip_other_final_letters(self):
        self.assertEqual(clean_headword_boundary("Abeja."), "Abeja")


if __name__ == "__main__":
    unittest.main()
