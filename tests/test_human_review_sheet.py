from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_human_review_sheet import (
    allocate_decision_ids,
    existing_decision_numbers,
    render_sheet,
    validate_manifests,
)


def manifests():
    facsimile = {
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_sha256": "abc123",
        "human_verified": False,
        "facsimile_required": True,
        "case_count": 1,
        "cases": [
            {
                "candidate_id": "ORT1888-cand-000342",
                "target": {
                    "candidate_id": "ORT1888-cand-000342",
                    "source_pdf_page": 30,
                    "source_printed_page": 26,
                    "headword_es_ocr": "mu",
                    "raw_span_ocr": "mu-*n | 27",
                },
                "previous_direct_anchor": {
                    "candidate_id": "ORT1888-cand-000341",
                    "source_pdf_page": 30,
                    "source_printed_page": 26,
                    "headword_es_ocr": "Apresurarse",
                },
                "next_direct_anchor": {
                    "candidate_id": "ORT1888-cand-000343",
                    "source_pdf_page": 31,
                    "source_printed_page": 27,
                    "headword_es_ocr": "Apresuramiento",
                },
                "full_page_assets": [
                    "pages/page-030-full.png",
                    "pages/page-031-full.png",
                ],
                "boundary_crop_assets": [
                    {
                        "role": "previous_tail",
                        "source_pdf_page": 30,
                        "source_printed_page": 26,
                        "path": "cases/ORT1888-cand-000342/page-030-previous_tail.png",
                    },
                    {
                        "role": "next_head",
                        "source_pdf_page": 31,
                        "source_printed_page": 27,
                        "path": "cases/ORT1888-cand-000342/page-031-next_head.png",
                    },
                ],
            }
        ],
    }
    inferred = {
        "human_verified": False,
        "facsimile_required": True,
        "case_count": 1,
        "cases": [
            {
                "candidate_id": "ORT1888-cand-000342",
                "machine_observations": [
                    "non_em_dash_separator",
                    "raw_span_contains_page_number",
                ],
            }
        ],
    }
    return facsimile, inferred


class HumanReviewSheetTests(unittest.TestCase):
    def test_allocates_ids_without_colliding_with_used_numbers(self):
        self.assertEqual(
            allocate_decision_ids(3, {1, 3}),
            ["ORT1888-rec-000002", "ORT1888-rec-000004", "ORT1888-rec-000005"],
        )

    def test_reads_existing_json_and_jsonl_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.json").write_text(
                '{"decision_id":"ORT1888-rec-000004"}', encoding="utf-8"
            )
            (root / "many.jsonl").write_text(
                '{"decision_id":"ORT1888-rec-000009"}\n'
                '{"decision_id":"not-a-decision"}\n',
                encoding="utf-8",
            )
            self.assertEqual(existing_decision_numbers(root), {4, 9})

    def test_manifest_case_lists_must_match(self):
        facsimile, inferred = manifests()
        inferred["cases"][0]["candidate_id"] = "ORT1888-cand-999999"
        with self.assertRaisesRegex(ValueError, "case lists differ"):
            validate_manifests(facsimile, inferred)

    def test_manifest_must_remain_machine_unverified(self):
        facsimile, inferred = manifests()
        facsimile["human_verified"] = True
        with self.assertRaisesRegex(ValueError, "human_verified=false"):
            validate_manifests(facsimile, inferred)

    def test_sheet_contains_visual_evidence_and_guarded_export(self):
        facsimile, inferred = manifests()
        rendered = render_sheet(
            facsimile,
            inferred,
            ["ORT1888-rec-000001"],
        )
        self.assertIn("ORT1888-cand-000342", rendered)
        self.assertIn("page-030-previous_tail.png", rendered)
        self.assertIn("page-031-next_head.png", rendered)
        self.assertIn("non_em_dash_separator", rendered)
        self.assertIn("Confirmo que inspeccioné personalmente", rendered)
        self.assertIn("reject_false_boundary", rendered)
        self.assertIn("defer_uncertain", rendered)
        self.assertIn("merge_candidates", rendered)
        self.assertIn("split_candidate", rendered)
        self.assertIn("human_verified: true", rendered)
        self.assertIn("Escriba el nombre de la persona revisora", rendered)
        self.assertNotIn("<script src=", rendered)
        self.assertNotIn("https://cdn", rendered)

    def test_sheet_escapes_display_text(self):
        facsimile, inferred = manifests()
        facsimile["cases"][0]["target"]["raw_span_ocr"] = "<img src=x onerror=alert(1)>"
        rendered = render_sheet(facsimile, inferred, ["ORT1888-rec-000001"])
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", rendered)
        self.assertNotIn("<img src=x onerror=alert(1)>", rendered)


if __name__ == "__main__":
    unittest.main()
