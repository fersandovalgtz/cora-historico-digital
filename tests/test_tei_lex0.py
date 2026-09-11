from __future__ import annotations

import csv
import io
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_tei_lex0 import (
    LEX0_VERSION,
    OBJECT_LANGUAGE,
    SOURCE_WITNESS_URL,
    TARGET_LANGUAGE,
    TEI_NS,
    XML_NS,
    build_tree,
)


Q = lambda name: f"{{{TEI_NS}}}{name}"
XML_ID = f"{{{XML_NS}}}id"
XML_LANG = f"{{{XML_NS}}}lang"


def record(
    *,
    order: int,
    status: str = "machine_accepted",
    article_id: str | None = None,
    candidate_id: str | None = None,
    headword: str = "Abajar algo",
    cora: str = "Acátoa. Nete.",
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
        "page_alignment_status": "matched_headword",
        "extraction_confidence": "high" if status == "machine_accepted" else "low",
        "machine_status": status,
        "machine_rationale": "direct_page_headword_match" if status == "machine_accepted" else "test_residual",
        "authority_status": "machine_derived",
        "release_eligible": "True" if status == "machine_accepted" else "False",
        "human_verified": "False",
    }


class TeiLex0ProjectionTests(unittest.TestCase):
    def test_root_and_language_profile_target_lex0(self):
        tree, report = build_tree([record(order=1)])
        root = tree.getroot()
        self.assertEqual(root.tag, Q("TEI"))
        self.assertEqual(root.attrib["type"], "lex-0")
        self.assertEqual(report["target_lex0_version"], LEX0_VERSION)

        languages = root.findall(f".//{Q('language')}")
        profile = {(lang.attrib["ident"], lang.attrib["role"]) for lang in languages}
        self.assertIn((OBJECT_LANGUAGE, "objectLanguage"), profile)
        self.assertIn((TARGET_LANGUAGE, "targetLanguage"), profile)

    def test_accepted_record_maps_field_for_field_without_normalization(self):
        source = record(
            order=1,
            headword="A., denotando  la persona que padece",
            cora="A., hua.  Vel. otra forma.",
        )
        tree, report = build_tree([source])
        root = tree.getroot()
        entry = root.find(f".//{Q('entry')}")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.attrib[XML_ID], "ORT1888-art-000001")
        self.assertEqual(entry.attrib[XML_LANG], OBJECT_LANGUAGE)
        self.assertEqual(entry.attrib["type"], "mainEntry")
        self.assertEqual(entry.attrib["corresp"], "urn:chd:ORT1888-cand-000001")
        self.assertEqual(entry.attrib["source"], "#ORTEGA1888-TEPIC-IA")

        lemma = entry.find(f"./{Q('form')}/{Q('orth')}")
        translated = entry.find(
            f"./{Q('sense')}/{Q('cit')}[@type='translationEquivalent']/{Q('form')}/{Q('orth')}"
        )
        self.assertEqual(lemma.text, source["headword_es_ocr"])
        self.assertEqual(translated.text, source["cora_ocr"])
        self.assertEqual(
            entry.find(f"./{Q('sense')}/{Q('cit')}").attrib[XML_LANG],
            TARGET_LANGUAGE,
        )
        self.assertEqual(report["entry_total"], 1)
        self.assertEqual(report["residual_total"], 0)

    def test_uncertain_and_rejected_are_not_promoted_to_entries(self):
        records = [
            record(order=1),
            record(order=2, status="machine_uncertain"),
            record(order=3, status="machine_rejected"),
        ]
        tree, report = build_tree(records)
        root = tree.getroot()
        entries = root.findall(f".//{Q('body')}/{Q('entry')}")
        residuals = root.findall(f".//{Q('back')}//{Q('item')}")
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(residuals), 2)
        self.assertEqual(
            [item.attrib[XML_ID] for item in residuals],
            ["ORT1888-cand-000002", "ORT1888-cand-000003"],
        )
        self.assertIn("#machine_uncertain", residuals[0].attrib["ana"])
        self.assertIn("#machine_rejected", residuals[1].attrib["ana"])
        self.assertEqual(report["machine_status_counts"]["machine_accepted"], 1)
        self.assertEqual(report["machine_status_counts"]["machine_uncertain"], 1)
        self.assertEqual(report["machine_status_counts"]["machine_rejected"], 1)

    def test_header_preserves_source_bibliography_and_machine_only_authority(self):
        tree, _ = build_tree([record(order=1)])
        root = tree.getroot()
        bibl = root.find(f".//{Q('biblStruct')}[@{XML_ID}='ORTEGA1888-TEPIC-IA']")
        self.assertIsNotNone(bibl)
        self.assertIn(
            "Vocabulario de las lenguas castellana y cora",
            root.find(f".//{Q('sourceDesc')}//{Q('title')}").text,
        )
        source_ref = root.find(
            f".//{Q('biblStruct')}[@{XML_ID}='ORTEGA1888-TEPIC-IA']/{Q('ref')}"
        )
        self.assertIsNotNone(source_ref)
        self.assertEqual(source_ref.attrib["target"], SOURCE_WITNESS_URL)
        self.assertEqual(source_ref.text, "Internet Archive digital witness")
        self.assertIsNone(root.find(f".//{Q('biblStruct')}/{Q('idno')}"))
        category_ids = {
            category.attrib[XML_ID]
            for category in root.findall(f".//{Q('taxonomy')}/{Q('category')}")
        }
        self.assertTrue(
            {"machine_accepted", "machine_uncertain", "machine_rejected", "machine_derived", "human_unverified"}.issubset(category_ids)
        )

    def test_invalid_source_authority_is_rejected(self):
        source = record(order=1)
        source["human_verified"] = "True"
        with self.assertRaisesRegex(ValueError, "machine-only"):
            build_tree([source])

    def test_noncontiguous_source_order_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not contiguous"):
            build_tree([record(order=1), record(order=3)])

    def test_generated_tree_round_trips_as_well_formed_xml(self):
        tree, _ = build_tree(
            [
                record(order=1, headword="Niño & niña", cora="Forma <OCR> & otra"),
                record(order=2, status="machine_uncertain"),
            ]
        )
        buffer = io.BytesIO()
        tree.write(buffer, encoding="utf-8", xml_declaration=True)
        parsed = ET.fromstring(buffer.getvalue())
        self.assertEqual(parsed.tag, Q("TEI"))


if __name__ == "__main__":
    unittest.main()
