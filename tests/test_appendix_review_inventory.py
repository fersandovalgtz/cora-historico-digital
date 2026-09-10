from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_appendix_review_inventory import build_inventory, build_units, classify_unit, split_paragraphs


class AppendixReviewInventoryTests(unittest.TestCase):
    def test_split_paragraphs_preserves_internal_linebreaks(self):
        text = "Uno. — Ceaut.\ncontinuación\n\n89\n\nDos. — Huahpoa.\n"
        self.assertEqual(
            split_paragraphs(text),
            ["Uno. — Ceaut.\ncontinuación", "89", "Dos. — Huahpoa."],
        )

    def test_machine_classification_is_descriptive(self):
        machine_class, observations = classify_unit("Una. — Ceaut.")
        self.assertEqual(machine_class, "entry_or_example_like")
        self.assertIn("contains_equivalence_separator_like_mark", observations)
        self.assertNotIn("accept_boundary", observations)

    def test_page_marker_is_not_promoted_to_entry(self):
        machine_class, observations = classify_unit("89")
        self.assertEqual(machine_class, "page_marker_or_ocr_noise")
        self.assertEqual(observations, ["machine_noise_like"])

    def test_ids_are_separate_from_alphabetical_candidate_namespace(self):
        units = build_units("Una. — Ceaut.\n\nDos. — Huahpoa.", "numunit", "numerals_appendix")
        self.assertEqual([unit["unit_id"] for unit in units], ["ORT1888-numunit-001", "ORT1888-numunit-002"])
        self.assertTrue(all("ORT1888-cand-" not in unit["unit_id"] for unit in units))
        self.assertTrue(all(unit["human_verified"] is False for unit in units))

    def test_inventory_keeps_appendices_separate_and_pending(self):
        inventory = build_inventory(
            "Una. — Ceaut.\n\nY así van contando hasta veinte.",
            "El verbo Arieú, tiene solo dos personas.\n\nChe, es partícula de que se usa.",
        )
        self.assertEqual(len(inventory["appendices"]), 2)
        self.assertEqual(inventory["appendices"][0]["unit_count"], 2)
        self.assertEqual(inventory["appendices"][1]["unit_count"], 2)
        self.assertEqual(inventory["total_unit_count"], 4)
        self.assertFalse(inventory["human_verified"])
        self.assertTrue(inventory["all_units_pending_human_review"])

    def test_narrative_and_particle_descriptions_are_not_entry_claims(self):
        self.assertEqual(
            classify_unit("Y así van contando hasta veinte que dicen:")[0],
            "narrative_or_grammatical_instruction",
        )
        self.assertEqual(
            classify_unit("Che, es partícula de que se usa en los optativos.")[0],
            "particle_description_like",
        )


if __name__ == "__main__":
    unittest.main()
