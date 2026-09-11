#!/usr/bin/env python3
"""Build a conservative CLDF Dictionary projection of the Ortega 1888 machine corpus.

The internal CHD machine corpus remains canonical. Only machine-accepted alphabetical
records become CLDF dictionary entries. Each accepted article maps to exactly one sense
whose Description preserves the complete ``cora_ocr`` string; this intentionally avoids
inventing sense boundaries or splitting historical equivalents. Machine-uncertain and
machine-rejected candidates are retained in a separate CSVW table and are never promoted
to lexical entries.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter
from pathlib import Path

from pycldf import Dictionary, Source, term_uri

DEFAULT_SOURCE = Path("data/lexicon/machine_lexicon.csv")
DEFAULT_OUTPUT_DIR = Path("data/interoperability/cldf")
DEFAULT_REPORT = Path("reports/cldf_dictionary.json")

SOURCE_WITNESS_ID = "ORTEGA1888-TEPIC-IA"
SOURCE_KEY = "Ortega1888"
OBJECT_LANGUAGE_ID = "spa"
TARGET_LANGUAGE_ID = "crn"
TARGET_CLDF_SPEC = "1.3"


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))
    if not records:
        raise ValueError("machine lexicon is empty")
    return records


def assert_source_contract(records: list[dict[str, str]]) -> None:
    orders = [int(record["order"]) for record in records]
    if orders != list(range(1, len(records) + 1)):
        raise ValueError("machine lexicon order is not contiguous")
    if any(record["source_witness_id"] != SOURCE_WITNESS_ID for record in records):
        raise ValueError("unexpected source witness in machine lexicon")
    if any(record["authority_status"] != "machine_derived" for record in records):
        raise ValueError("unexpected authority status in machine lexicon")
    if any(record["human_verified"].casefold() != "false" for record in records):
        raise ValueError("CLDF projection requires machine-only source records")


def source_ref(record: dict[str, str]) -> list[str]:
    page = record["source_printed_page"].strip()
    return [f"{SOURCE_KEY}[{page}]"] if page else [SOURCE_KEY]


def build_rows(records: list[dict[str, str]]) -> tuple[list[dict], list[dict], list[dict]]:
    assert_source_contract(records)
    entries: list[dict] = []
    senses: list[dict] = []
    residuals: list[dict] = []

    for record in records:
        if record["machine_status"] == "machine_accepted":
            article_id = record["article_id"]
            if not article_id:
                raise ValueError(f"accepted record {record['candidate_id']} lacks article_id")
            entries.append(
                {
                    "ID": article_id,
                    "Language_ID": OBJECT_LANGUAGE_ID,
                    "Headword": record["headword_es_ocr"],
                    "Part_Of_Speech": None,
                    "Source": source_ref(record),
                    "CHD_Candidate_ID": record["candidate_id"],
                    "CHD_Source_Witness_ID": record["source_witness_id"],
                    "CHD_Source_PDF_Page": int(record["source_pdf_page"]),
                    "CHD_Source_Printed_Page": record["source_printed_page"],
                    "CHD_Source_OCR_Line_Start": int(record["source_ocr_line_start"]),
                    "CHD_Source_OCR_Line_End": int(record["source_ocr_line_end"]),
                    "CHD_Raw_Span_OCR": record["raw_span_ocr"],
                    "CHD_Separator_Type": record["separator_type"],
                    "CHD_Page_Alignment_Status": record["page_alignment_status"],
                    "CHD_Extraction_Confidence": record["extraction_confidence"],
                    "CHD_Machine_Status": record["machine_status"],
                    "CHD_Machine_Rationale": record["machine_rationale"],
                    "CHD_Authority_Status": record["authority_status"],
                    "CHD_Release_Eligible": record["release_eligible"].casefold() == "true",
                    "CHD_Human_Verified": False,
                }
            )
            senses.append(
                {
                    "ID": f"{article_id}-s1",
                    "Description": record["cora_ocr"],
                    "Entry_ID": article_id,
                    "Description_Language_ID": TARGET_LANGUAGE_ID,
                    "CHD_Candidate_ID": record["candidate_id"],
                    "CHD_Authority_Status": record["authority_status"],
                    "CHD_Human_Verified": False,
                }
            )
        else:
            residuals.append(
                {
                    "ID": record["candidate_id"],
                    "Source": source_ref(record),
                    "Order": int(record["order"]),
                    "Headword_ES_OCR": record["headword_es_ocr"],
                    "Cora_OCR": record["cora_ocr"],
                    "Raw_Span_OCR": record["raw_span_ocr"],
                    "Source_Witness_ID": record["source_witness_id"],
                    "Source_PDF_Page": int(record["source_pdf_page"]),
                    "Source_Printed_Page": record["source_printed_page"],
                    "Source_OCR_Line_Start": int(record["source_ocr_line_start"]),
                    "Source_OCR_Line_End": int(record["source_ocr_line_end"]),
                    "Separator_Type": record["separator_type"],
                    "Page_Alignment_Status": record["page_alignment_status"],
                    "Extraction_Confidence": record["extraction_confidence"],
                    "Machine_Status": record["machine_status"],
                    "Machine_Rationale": record["machine_rationale"],
                    "Authority_Status": record["authority_status"],
                    "Human_Verified": False,
                }
            )

    return entries, senses, residuals


def configure_dataset(output_dir: Path) -> Dictionary:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = Dictionary.in_dir(output_dir)
    dataset.add_component("LanguageTable")
    dataset.add_foreign_key("EntryTable", "Language_ID", "LanguageTable", "ID")

    dataset.add_columns(
        "EntryTable",
        term_uri("source"),
        {"name": "CHD_Candidate_ID", "datatype": "string"},
        {"name": "CHD_Source_Witness_ID", "datatype": "string"},
        {"name": "CHD_Source_PDF_Page", "datatype": "integer"},
        {"name": "CHD_Source_Printed_Page", "datatype": "string"},
        {"name": "CHD_Source_OCR_Line_Start", "datatype": "integer"},
        {"name": "CHD_Source_OCR_Line_End", "datatype": "integer"},
        {"name": "CHD_Raw_Span_OCR", "datatype": "string"},
        {"name": "CHD_Separator_Type", "datatype": "string"},
        {"name": "CHD_Page_Alignment_Status", "datatype": "string"},
        {"name": "CHD_Extraction_Confidence", "datatype": "string"},
        {"name": "CHD_Machine_Status", "datatype": "string"},
        {"name": "CHD_Machine_Rationale", "datatype": "string"},
        {"name": "CHD_Authority_Status", "datatype": "string"},
        {"name": "CHD_Release_Eligible", "datatype": "boolean"},
        {"name": "CHD_Human_Verified", "datatype": "boolean"},
    )
    dataset.add_columns(
        "SenseTable",
        {"name": "Description_Language_ID", "datatype": "string"},
        {"name": "CHD_Candidate_ID", "datatype": "string"},
        {"name": "CHD_Authority_Status", "datatype": "string"},
        {"name": "CHD_Human_Verified", "datatype": "boolean"},
    )
    dataset.add_foreign_key(
        "SenseTable", "Description_Language_ID", "LanguageTable", "ID"
    )

    dataset.add_table(
        "residuals.csv",
        {
            "name": "ID",
            "required": True,
            "datatype": {"base": "string", "format": "[a-zA-Z0-9_\\-]+"},
        },
        term_uri("source"),
        {"name": "Order", "datatype": "integer"},
        {"name": "Headword_ES_OCR", "datatype": "string"},
        {"name": "Cora_OCR", "datatype": "string"},
        {"name": "Raw_Span_OCR", "datatype": "string"},
        {"name": "Source_Witness_ID", "datatype": "string"},
        {"name": "Source_PDF_Page", "datatype": "integer"},
        {"name": "Source_Printed_Page", "datatype": "string"},
        {"name": "Source_OCR_Line_Start", "datatype": "integer"},
        {"name": "Source_OCR_Line_End", "datatype": "integer"},
        {"name": "Separator_Type", "datatype": "string"},
        {"name": "Page_Alignment_Status", "datatype": "string"},
        {"name": "Extraction_Confidence", "datatype": "string"},
        {"name": "Machine_Status", "datatype": "string"},
        {"name": "Machine_Rationale", "datatype": "string"},
        {"name": "Authority_Status", "datatype": "string"},
        {"name": "Human_Verified", "datatype": "boolean"},
        primaryKey="ID",
        description=(
            "Machine-uncertain and machine-rejected CHD candidates retained as documentary "
            "evidence; rows in this table are not CLDF dictionary entries."
        ),
    )

    dataset.properties.update(
        {
            "dc:title": "Cora Histórico Digital — Ortega 1888 CLDF Dictionary projection",
            "dc:creator": "Cora Histórico Digital",
            "dc:license": "https://creativecommons.org/licenses/by/4.0/",
            "dc:identifier": "https://github.com/fersandovalgtz/cora-historico-digital",
            "dc:bibliographicCitation": (
                "Ortega, José de. 1888. Vocabulario de las lenguas castellana y cora. "
                "Reimpresión de Tepic: Imprenta de Antonio Lagaspi. Machine-only CLDF "
                "projection by Cora Histórico Digital."
            ),
            "rdf:ID": "cora-historico-digital-ortega1888",
        }
    )
    dataset.add_sources(
        Source(
            "book",
            SOURCE_KEY,
            author="José de Ortega",
            title=(
                "Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, "
                "por orden del Sr. Gral. D. Leopoldo Romano"
            ),
            year="1888",
            address="Tepic",
            publisher="Imprenta de Antonio Lagaspi",
            url="https://archive.org/details/vocabulariodelas00orte",
        )
    )
    return dataset


def write_dataset(
    records: list[dict[str, str]], output_dir: Path, report_path: Path
) -> dict[str, object]:
    entries, senses, residuals = build_rows(records)
    dataset = configure_dataset(output_dir)
    languages = [
        {"ID": OBJECT_LANGUAGE_ID, "Name": "Spanish", "ISO639P3code": "spa"},
        {
            "ID": TARGET_LANGUAGE_ID,
            "Name": "Cora / Náayeri (El Nayar Cora)",
            "ISO639P3code": "crn",
        },
    ]
    dataset.write(
        EntryTable=entries,
        SenseTable=senses,
        LanguageTable=languages,
        **{"residuals.csv": residuals},
    )

    metadata_path = output_dir / "Dictionary-metadata.json"
    on_disk = Dictionary.from_metadata(metadata_path)
    if not on_disk.validate():
        raise RuntimeError("generated CLDF Dictionary failed pycldf validation")

    status_counts = Counter(record["machine_status"] for record in records)
    report: dict[str, object] = {
        "artifact_type": "cldf_dictionary_projection_report",
        "target_cldf_spec": TARGET_CLDF_SPEC,
        "module": "Dictionary",
        "metadata_path": metadata_path.as_posix(),
        "source_path": DEFAULT_SOURCE.as_posix(),
        "source_witness_id": SOURCE_WITNESS_ID,
        "source_record_total": len(records),
        "entry_total": len(entries),
        "sense_total": len(senses),
        "residual_total": len(residuals),
        "machine_status_counts": dict(sorted(status_counts.items())),
        "entry_language_id": OBJECT_LANGUAGE_ID,
        "sense_description_language_id": TARGET_LANGUAGE_ID,
        "authority_status": "machine_derived",
        "human_verified": False,
        "validation": "pycldf Dataset.validate() passed",
        "projection_policy": (
            "Each machine_accepted article becomes one EntryTable row and exactly one "
            "SenseTable row whose Description is the complete cora_ocr field. No sense or "
            "equivalent splitting occurs. Non-accepted candidates remain in residuals.csv."
        ),
        "normalization_policy": (
            "headword_es_ocr, cora_ocr and raw_span_ocr are preserved without OCR correction, "
            "modern spelling normalization, dialect reassignment or grammatical inference."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    records = read_records(args.source)
    report = write_dataset(records, args.output_dir, args.report)
    print(
        f"CLDF Dictionary projection: {report['entry_total']} entries; "
        f"{report['sense_total']} senses; {report['residual_total']} residual candidates; "
        f"target=CLDF {TARGET_CLDF_SPEC}"
    )


if __name__ == "__main__":
    main()
