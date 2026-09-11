from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_irregular_particles_machine import (
    TYPE_EXPRESSION,
    TYPE_IMPERATIVE,
    TYPE_NOISE,
    TYPE_PARTICLE,
    build_records,
    classify_record,
    split_paragraphs_with_lines,
)


class IrregularParticlesMachineTests(unittest.TestCase):
    def test_paragraph_split_preserves_source_line_span(self):
        blocks = split_paragraphs_with_lines("Uno\ncontinúa\n\nDos\n")
        self.assertEqual(blocks, [("Uno\ncontinúa", 1, 2), ("Dos", 4, 4)])

    def test_explicit_imperative_marker_is_separate_type(self):
        record_type, observations = classify_record(
            "Imperativo. .— Arixu, Anda ó vete. — Arieú,"
        )
        self.assertEqual(record_type, TYPE_IMPERATIVE)
        self.assertIn("imperative_cue", observations)
        self.assertIn("contains_multiple_separator_like_marks", observations)

    def test_generic_separator_example_is_expression(self):
        record_type, observations = classify_record(
            "Estí a y tu padre? — Necaemaháhua ayaoppa?"
        )
        self.assertEqual(record_type, TYPE_EXPRESSION)
        self.assertIn("contains_question_mark", observations)

    def test_particle_description_is_not_flattened_to_narrative(self):
        record_type, observations = classify_record(
            "Llamo yo a Miguel. Ahe es partícula con que saluda el que entra."
        )
        self.assertEqual(record_type, TYPE_PARTICLE)
        self.assertIn("mentions_particle", observations)

    def test_punctuation_heavy_tail_is_noise(self):
        record_type, _ = classify_record(":•■ .pin/' . -... :::.-v -.«-yt'l")
        self.assertEqual(record_type, TYPE_NOISE)

    def test_build_records_has_stable_one_to_one_navigation_ids(self):
        text = """Por último se incluyen ejemplos.

Imperativo. — Arixu.

Che, es partícula de optativo.

wm
"""
        records, report = build_records(text)
        self.assertEqual(
            [record["irregular_id"] for record in records],
            [
                "ORT1888-irr-001",
                "ORT1888-irr-002",
                "ORT1888-irr-003",
                "ORT1888-irr-004",
            ],
        )
        self.assertEqual(
            [record["source_unit_id"] for record in records],
            [
                "ORT1888-irrunit-001",
                "ORT1888-irrunit-002",
                "ORT1888-irrunit-003",
                "ORT1888-irrunit-004",
            ],
        )
        self.assertEqual(report["record_total"], 4)
        self.assertEqual(report["source_nonempty_paragraph_total"], 4)

    def test_every_record_remains_machine_only(self):
        records, report = build_records("Imperativo. — Arixu.\n\nwm\n")
        self.assertFalse(report["human_verified"])
        for record in records:
            self.assertEqual(
                record["record_status"], "machine_structured_appendix_unit"
            )
            self.assertEqual(record["authority_status"], "machine_derived")
            self.assertFalse(record["human_verified"])


if __name__ == "__main__":
    unittest.main()
