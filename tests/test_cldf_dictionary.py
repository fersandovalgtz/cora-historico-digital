from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

from pycldf import Dictionary

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_cldf_dictionary import (
    OBJECT_LANGUAGE_ID,
    TARGET_LANGUAGE_ID,
    build_rows,
    write_dataset,
)


def record(
    *,
    order: int,
    status: str = "machine_accepted",
    article_id: str | None = None,
    candidate_id: str | None = None,
    headword: str = "Abajar algo",
    cora: str = "Acátoa. Nete. Acucare. Nete.",
) -> dict[str, str]:
    candidate_id = candidate_id or f"ORT1888-cand-{order:06d}"
    if article_id is None and status == "machine_accepted":
        article_id = f"ORT1888-art-{order:06d}"
    return {
        "article_id": article_id or "",
        "candidate_id": candidate_id,
        "order": str(order),
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_page": "19",
        "source_printed_page": "15",
        "source_ocr_line_start": str(547 + order),
        "source_ocr_line_end": str(548 + order),
        "headword_es_ocr": headword,
        "cora_ocr": cora,
        "raw_span_ocr": f"{headword}. — {cora}",
        "separator_type": "em_dash",
        "page_alignment_status": "matched_headword" if status == "machine_accepted" else "inferred_sequence",
        "extraction_confidence": "high" if status == "machine_accepted" else "low",
        "machine_status": status,
        "machine_rationale": "direct_page_headword_match" if status == "machine_accepted" else "test_residual",
        "authority_status": "machine_derived",
        "release_eligible": "True" if status == "machine_accepted" else "False",
        "human_verified": "False",
    }


class CldfDictionaryProjectionTests(unittest.TestCase):
    def test_accepted_record_maps_to_one_entry_and_one_unsplit_sense(self):
        source = record(
            order=1,
            headword="Abajar algo",
            cora="Acátoa. Nete. Acucare. Nete.",
        )
        entries, senses, residuals = build_rows([source])
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(senses), 1)
        self.assertEqual(residuals, [])
        self.assertEqual(entries[0]["ID"], "ORT1888-art-000001")
        self.assertEqual(entries[0]["Language_ID"], OBJECT_LANGUAGE_ID)
        self.assertEqual(entries[0]["Headword"], source["headword_es_ocr"])
        self.assertEqual(senses[0]["ID"], "ORT1888-art-000001-s1")
        self.assertEqual(senses[0]["Entry_ID"], entries[0]["ID"])
        self.assertEqual(senses[0]["Description_Language_ID"], TARGET_LANGUAGE_ID)
        self.assertEqual(senses[0]["Description"], source["cora_ocr"])

    def test_uncertain_and_rejected_are_residuals_not_entries(self):
        rows = [
            record(order=1),
            record(order=2, status="machine_uncertain", headword="I", cora="Nteanhtealía"),
            record(order=3, status="machine_rejected", headword="mu", cora="*n"),
        ]
        entries, senses, residuals = build_rows(rows)
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(senses), 1)
        self.assertEqual(
            [r["Machine_Status"] for r in residuals],
            ["machine_uncertain", "machine_rejected"],
        )
        self.assertEqual(
            [r["ID"] for r in residuals],
            ["ORT1888-cand-000002", "ORT1888-cand-000003"],
        )

    def test_projection_rejects_human_verified_source(self):
        source = record(order=1)
        source["human_verified"] = "True"
        with self.assertRaisesRegex(ValueError, "machine-only"):
            build_rows([source])

    def test_projection_rejects_noncontiguous_order(self):
        with self.assertRaisesRegex(ValueError, "not contiguous"):
            build_rows([record(order=1), record(order=3)])

    def test_written_dataset_validates_and_preserves_language_roles(self):
        rows = [
            record(order=1),
            record(order=2, status="machine_uncertain", headword="I", cora="Nteanhtealía"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "cldf"
            report_path = root / "report.json"
            report = write_dataset(rows, output_dir, report_path)

            dataset = Dictionary.from_metadata(output_dir / "Dictionary-metadata.json")
            self.assertTrue(dataset.validate())
            self.assertEqual(report["entry_total"], 1)
            self.assertEqual(report["sense_total"], 1)
            self.assertEqual(report["residual_total"], 1)

            with (output_dir / "entries.csv").open(encoding="utf-8", newline="") as handle:
                entries = list(csv.DictReader(handle))
            with (output_dir / "senses.csv").open(encoding="utf-8", newline="") as handle:
                senses = list(csv.DictReader(handle))
            with (output_dir / "languages.csv").open(encoding="utf-8", newline="") as handle:
                languages = list(csv.DictReader(handle))
            with (output_dir / "residuals.csv").open(encoding="utf-8", newline="") as handle:
                residuals = list(csv.DictReader(handle))

            self.assertEqual(entries[0]["Language_ID"], "spa")
            self.assertEqual(senses[0]["Description_Language_ID"], "crn")
            self.assertEqual({r["ID"] for r in languages}, {"spa", "crn"})
            self.assertEqual(residuals[0]["Machine_Status"], "machine_uncertain")
            self.assertEqual(entries[0]["CHD_Human_Verified"].lower(), "false")
            self.assertEqual(senses[0]["CHD_Human_Verified"].lower(), "false")
            self.assertEqual(residuals[0]["Human_Verified"].lower(), "false")

            loaded_report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded_report, report)


if __name__ == "__main__":
    unittest.main()
