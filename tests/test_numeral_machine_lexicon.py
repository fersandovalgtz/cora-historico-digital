from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_numeral_machine_lexicon import (
    SERIES_ANIMATE,
    SERIES_FREQUENCY,
    SERIES_GENERAL,
    build_records,
    split_explicit_pair,
)


class NumeralMachineLexiconTests(unittest.TestCase):
    def test_em_dash_pair_preserves_ocr_sides(self):
        pair = split_explicit_pair("Veinte  y  una.  —  Ceitevi  apoan. cenut.")
        self.assertEqual(
            pair,
            ("Veinte  y  una.", "Ceitevi  apoan. cenut.", "em_dash"),
        )

    def test_double_hyphen_variant_is_supported(self):
        self.assertEqual(
            split_explicit_pair("Dos veces. --Huappoax."),
            ("Dos veces", "Huappoax.", "hyphen_variant"),
        )

    def test_single_hyphen_variant_preserves_left_ocr(self):
        self.assertEqual(
            split_explicit_pair("Tres'.-sMahiuzM'ca."),
            ("Tres'", "sMahiuzM'ca.", "hyphen_variant"),
        )

    def test_word_final_hyphenation_is_not_a_pair(self):
        self.assertIsNone(split_explicit_pair("cosas que paresen innu-"))

    def test_narrative_line_is_not_promoted(self):
        self.assertIsNone(
            split_explicit_pair("Para decir una vez, dos veces, etc. dicen:")
        )

    def test_explicit_source_markers_change_series(self):
        text = """Cuenta para contar todo lo numerable.
Una. — Ceaut.
Para decir una vez, dos veces, etc. dicen:
Una vez. — Cevix.
Para decir dos hombres, tres hombres, ú otra cualquiera cosa animada, se dice:
Dos. — Mahuahpoa.
"""
        records, report = build_records(text)
        self.assertEqual(
            [record["semantic_series"] for record in records],
            [SERIES_GENERAL, SERIES_FREQUENCY, SERIES_ANIMATE],
        )
        self.assertEqual(
            report["series_counts"],
            {SERIES_ANIMATE: 1, SERIES_FREQUENCY: 1, SERIES_GENERAL: 1},
        )

    def test_record_ids_are_stable_and_contiguous(self):
        records, _ = build_records("Una. — Ceaut.\nDos. — Huahpoa.\n")
        self.assertEqual(
            [record["numeral_id"] for record in records],
            ["ORT1888-num-001", "ORT1888-num-002"],
        )
        self.assertEqual([record["order"] for record in records], [1, 2])

    def test_source_line_and_raw_ocr_are_preserved(self):
        records, _ = build_records("Intro\n\nUna. — Ceaut.\n")
        self.assertEqual(records[0]["source_appendix_line"], 3)
        self.assertEqual(records[0]["raw_line_ocr"], "Una. — Ceaut.")

    def test_every_record_remains_machine_only(self):
        records, report = build_records("Una. — Ceaut.\nDos. — Huahpoa.\n")
        self.assertFalse(report["human_verified"])
        for record in records:
            self.assertEqual(record["record_status"], "machine_extracted_explicit_pair")
            self.assertEqual(record["authority_status"], "machine_derived")
            self.assertFalse(record["human_verified"])


if __name__ == "__main__":
    unittest.main()
