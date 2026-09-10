from __future__ import annotations
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_machine_corpus import (
    build_machine_corpus,
    is_prefolio_boundary_noise,
    raw_span_has_standalone_page_number,
    resolve_candidate,
)


def candidate(
    order: int,
    alignment: str,
    *,
    pdf_page: int = 20,
    printed_page: int | None = None,
    raw_span: str = "Cabeza. — Tete.",
    separator: str = "em_dash",
    confidence: str = "high",
) -> dict[str, str]:
    if printed_page is None:
        printed_page = pdf_page - 4
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_page": str(pdf_page),
        "source_printed_page": str(printed_page),
        "source_ocr_line_start": str(100 + order),
        "source_ocr_line_end": str(100 + order),
        "headword_es_ocr": "Cabeza",
        "cora_ocr": "Tete",
        "raw_span_ocr": raw_span,
        "separator_type": separator,
        "page_alignment_status": alignment,
        "extraction_confidence": confidence,
    }


class MachineCorpusTests(unittest.TestCase):
    def test_direct_and_anchored_become_machine_articles(self):
        records, report = build_machine_corpus([
            candidate(1, "matched_headword"),
            candidate(2, "anchored_same_page"),
        ])
        self.assertEqual(
            [r["article_id"] for r in records],
            ["ORT1888-art-000001", "ORT1888-art-000002"],
        )
        self.assertTrue(all(r["machine_status"] == "machine_accepted" for r in records))
        self.assertTrue(all(r["human_verified"] is False for r in records))
        self.assertEqual(report["machine_article_total"], 2)

    def test_inferred_without_structural_noise_evidence_remains_uncertain(self):
        record = resolve_candidate(candidate(1, "inferred_sequence"))
        self.assertEqual(record["machine_status"], "machine_uncertain")
        self.assertIsNone(record["article_id"])
        self.assertFalse(record["release_eligible"])

    def test_standalone_page_number_requires_complete_span_segment(self):
        self.assertTrue(raw_span_has_standalone_page_number("noise | 27", 27))
        self.assertFalse(raw_span_has_standalone_page_number("veintisiete 27 cosas", 27))
        self.assertFalse(raw_span_has_standalone_page_number("127", 27))

    def test_prefolio_noise_rule_requires_consecutive_direct_page_anchors(self):
        previous = candidate(1, "matched_headword", pdf_page=30)
        row = candidate(
            2,
            "inferred_sequence",
            pdf_page=30,
            raw_span="mu-*n | 27",
            separator="hyphen_variant",
            confidence="low",
        )
        following = candidate(3, "matched_headword", pdf_page=31)
        self.assertTrue(is_prefolio_boundary_noise(row, previous, following))
        resolved = resolve_candidate(row, previous, following)
        self.assertEqual(resolved["machine_status"], "machine_rejected")
        self.assertEqual(
            resolved["machine_rationale"],
            "prefolio_noise_between_consecutive_direct_page_anchors",
        )
        self.assertIsNone(resolved["article_id"])
        self.assertFalse(resolved["release_eligible"])

    def test_prefolio_rule_does_not_reject_without_next_folio_in_span(self):
        previous = candidate(1, "matched_headword", pdf_page=30)
        row = candidate(
            2,
            "inferred_sequence",
            pdf_page=30,
            raw_span="possible mutilated entry",
            separator="hyphen_variant",
            confidence="low",
        )
        following = candidate(3, "matched_headword", pdf_page=31)
        self.assertFalse(is_prefolio_boundary_noise(row, previous, following))
        self.assertEqual(
            resolve_candidate(row, previous, following)["machine_status"],
            "machine_uncertain",
        )

    def test_prefolio_rule_requires_low_confidence_hyphen_candidate(self):
        previous = candidate(1, "matched_headword", pdf_page=30)
        following = candidate(3, "matched_headword", pdf_page=31)
        for separator, confidence in [("em_dash", "medium"), ("hyphen_variant", "medium")]:
            row = candidate(
                2,
                "inferred_sequence",
                pdf_page=30,
                raw_span="I. — possible content | 27",
                separator=separator,
                confidence=confidence,
            )
            self.assertFalse(is_prefolio_boundary_noise(row, previous, following))

    def test_prefolio_rule_requires_exactly_next_pdf_page(self):
        previous = candidate(1, "matched_headword", pdf_page=30)
        row = candidate(
            2,
            "inferred_sequence",
            pdf_page=30,
            raw_span="noise | 28",
            separator="hyphen_variant",
            confidence="low",
        )
        following = candidate(3, "matched_headword", pdf_page=32)
        self.assertFalse(is_prefolio_boundary_noise(row, previous, following))

    def test_report_separates_rejected_from_uncertain(self):
        rows = [
            candidate(1, "matched_headword", pdf_page=30),
            candidate(
                2,
                "inferred_sequence",
                pdf_page=30,
                raw_span="noise | 27",
                separator="hyphen_variant",
                confidence="low",
            ),
            candidate(3, "matched_headword", pdf_page=31),
            candidate(
                4,
                "inferred_sequence",
                pdf_page=31,
                raw_span="possible entry",
                separator="em_dash",
                confidence="medium",
            ),
        ]
        records, report = build_machine_corpus(rows)
        self.assertEqual(report["machine_article_total"], 2)
        self.assertEqual(report["machine_rejected_total"], 1)
        self.assertEqual(report["machine_uncertain_total"], 1)
        self.assertEqual(report["machine_rejected_candidate_ids"], ["ORT1888-cand-000002"])
        self.assertEqual(report["machine_uncertain_candidate_ids"], ["ORT1888-cand-000004"])
        self.assertEqual(records[1]["machine_status"], "machine_rejected")
        self.assertEqual(records[3]["machine_status"], "machine_uncertain")

    def test_article_id_reuses_candidate_suffix(self):
        self.assertEqual(
            resolve_candidate(candidate(42, "matched_headword"))["article_id"],
            "ORT1888-art-000042",
        )

    def test_unknown_alignment_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown page_alignment_status"):
            resolve_candidate(candidate(1, "invented"))

    def test_candidate_order_mismatch_fails_closed(self):
        row = candidate(1, "matched_headword")
        row["candidate_id"] = "ORT1888-cand-000002"
        with self.assertRaisesRegex(ValueError, "candidate/order mismatch"):
            resolve_candidate(row)

    def test_corpus_requires_contiguous_source_order(self):
        with self.assertRaisesRegex(ValueError, "contiguous"):
            build_machine_corpus([
                candidate(1, "matched_headword"),
                candidate(3, "matched_headword"),
            ])


if __name__ == "__main__":
    unittest.main()
