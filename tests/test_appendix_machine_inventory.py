from __future__ import annotations
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_appendix_machine_inventory import build_inventory, build_units, classify_unit, split_paragraphs

class AppendixMachineInventoryTests(unittest.TestCase):
    def test_split_preserves_nonempty_paragraph_text(self):
        self.assertEqual(split_paragraphs("Una. — Cevit.\n\nY así van contando.\n\n89\n"),["Una. — Cevit.","Y así van contando.","89"])
    def test_namespaces_remain_separate(self):
        n=build_units("Una. — Cevit.","numunit","numerals_appendix"); i=build_units("Che, es partícula.","irrunit","irregular_verbs_particles_appendix")
        self.assertEqual(n[0]["unit_id"],"ORT1888-numunit-001"); self.assertEqual(i[0]["unit_id"],"ORT1888-irrunit-001")
    def test_unclassified_never_requests_human_review(self):
        cls, obs=classify_unit("Texto OCR ambiguo")
        self.assertEqual(cls,"unclassified_text_unit"); self.assertEqual(obs,["no_structural_classification"]); self.assertFalse(any("human" in x for x in obs))
    def test_inventory_is_machine_only(self):
        inventory=build_inventory("Una. — Cevit.\n\n89","Por último pondrá aqui algunos verbos irregulares")
        self.assertTrue(inventory["all_units_machine_only"]); self.assertFalse(inventory["human_verified"])
        for appendix in inventory["appendices"]:
            for unit in appendix["units"]:
                self.assertEqual(unit["processing_status"],"machine_classified"); self.assertEqual(unit["authority_status"],"machine_derived"); self.assertFalse(unit["human_verified"])

if __name__ == "__main__": unittest.main()
