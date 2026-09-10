from __future__ import annotations
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_machine_corpus import build_machine_corpus, resolve_candidate


def candidate(order: int, alignment: str) -> dict[str, str]:
    return {"candidate_id":f"ORT1888-cand-{order:06d}","order":str(order),"source_witness_id":"ORTEGA1888-TEPIC-IA","source_pdf_page":"20","source_printed_page":"16","source_ocr_line_start":"100","source_ocr_line_end":"101","headword_es_ocr":"Cabeza","cora_ocr":"Tete","raw_span_ocr":"Cabeza. — Tete.","separator_type":"em_dash","page_alignment_status":alignment,"extraction_confidence":"high"}


class MachineCorpusTests(unittest.TestCase):
    def test_direct_and_anchored_become_machine_articles(self):
        records, report = build_machine_corpus([candidate(1,"matched_headword"), candidate(2,"anchored_same_page")])
        self.assertEqual([r["article_id"] for r in records],["ORT1888-art-000001","ORT1888-art-000002"])
        self.assertTrue(all(r["machine_status"] == "machine_accepted" for r in records))
        self.assertTrue(all(r["human_verified"] is False for r in records))
        self.assertEqual(report["machine_article_total"],2)
    def test_inferred_remains_uncertain(self):
        record = resolve_candidate(candidate(1,"inferred_sequence"))
        self.assertEqual(record["machine_status"],"machine_uncertain")
        self.assertIsNone(record["article_id"])
        self.assertFalse(record["release_eligible"])
    def test_article_id_reuses_candidate_suffix(self):
        self.assertEqual(resolve_candidate(candidate(42,"matched_headword"))["article_id"],"ORT1888-art-000042")
    def test_unknown_alignment_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"unknown page_alignment_status"):
            resolve_candidate(candidate(1,"invented"))
    def test_candidate_order_mismatch_fails_closed(self):
        row=candidate(1,"matched_headword"); row["candidate_id"]="ORT1888-cand-000002"
        with self.assertRaisesRegex(ValueError,"candidate/order mismatch"):
            resolve_candidate(row)
    def test_corpus_requires_contiguous_source_order(self):
        with self.assertRaisesRegex(ValueError,"contiguous"):
            build_machine_corpus([candidate(1,"matched_headword"),candidate(3,"matched_headword")])

if __name__ == "__main__": unittest.main()
