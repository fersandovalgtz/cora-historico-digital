#!/usr/bin/env python3
"""Build a conservative TEI Lex-0 projection of the Ortega 1888 machine corpus.

The internal CHD records remain canonical. This script projects machine-accepted
alphabetical records as Spanish entries with Cora/Náayeri translation equivalents
and preserves machine-uncertain / machine-rejected records as residual documentary
items in TEI back matter. It never normalizes OCR or promotes residual records.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

DEFAULT_SOURCE = Path("data/lexicon/machine_lexicon.csv")
DEFAULT_OUTPUT = Path("data/interoperability/ortega1888_tei_lex0.xml")
DEFAULT_REPORT = Path("reports/tei_lex0.json")

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
LEX0_VERSION = "0.9.5"
OBJECT_LANGUAGE = "es"
TARGET_LANGUAGE = "crn"
SOURCE_WITNESS_ID = "ORTEGA1888-TEPIC-IA"
SOURCE_WITNESS_URL = "https://archive.org/details/vocabulariodelas00orte"

ET.register_namespace("", TEI_NS)


def q(name: str) -> str:
    return f"{{{TEI_NS}}}{name}"


def xml_attr(name: str) -> str:
    return f"{{{XML_NS}}}{name}"


def text_element(parent: ET.Element, name: str, text: str, **attrs: str) -> ET.Element:
    elem = ET.SubElement(parent, q(name), attrs)
    elem.text = text
    return elem


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
        raise ValueError("TEI projection requires machine-only source records")


def add_taxonomy(encoding_desc: ET.Element) -> None:
    class_decl = ET.SubElement(encoding_desc, q("classDecl"))
    taxonomy = ET.SubElement(class_decl, q("taxonomy"), {xml_attr("id"): "chdMachineAuthority"})
    categories = (
        ("machine_accepted", "Machine-accepted lexical record."),
        ("machine_uncertain", "Machine-uncertain source candidate; not promoted to a lexical entry."),
        ("machine_rejected", "Machine-rejected segmentation artifact; retained as source evidence."),
        ("machine_derived", "Computationally derived authority; no human validation claimed."),
        ("human_unverified", "No human philological or linguistic verification is represented."),
    )
    for category_id, description in categories:
        category = ET.SubElement(taxonomy, q("category"), {xml_attr("id"): category_id})
        cat_desc = ET.SubElement(category, q("catDesc"))
        text_element(cat_desc, "term", description)


def add_header(root: ET.Element, accepted_count: int, residual_count: int) -> None:
    header = ET.SubElement(root, q("teiHeader"))
    file_desc = ET.SubElement(header, q("fileDesc"))
    title_stmt = ET.SubElement(file_desc, q("titleStmt"))
    text_element(title_stmt, "title", "Cora Histórico Digital — Ortega 1888 TEI Lex-0 projection")
    resp_stmt = ET.SubElement(title_stmt, q("respStmt"))
    text_element(resp_stmt, "resp", "Machine-only historical-digital corpus and TEI Lex-0 projection")
    text_element(resp_stmt, "name", "Cora Histórico Digital")
    edition_stmt = ET.SubElement(file_desc, q("editionStmt"))
    text_element(edition_stmt, "edition", f"TEI Lex-0 {LEX0_VERSION} projection")
    extent = ET.SubElement(file_desc, q("extent"))
    text_element(extent, "measure", f"{accepted_count} machine-accepted lexical entries", unit="entry", quantity=str(accepted_count))
    text_element(extent, "measure", f"{residual_count} residual machine candidates", unit="candidate", quantity=str(residual_count))
    publication_stmt = ET.SubElement(file_desc, q("publicationStmt"))
    text_element(publication_stmt, "publisher", "Cora Histórico Digital")
    availability = ET.SubElement(publication_stmt, q("availability"))
    text_element(availability, "licence", "Original project metadata and derived annotations: CC BY 4.0. Historical source: public domain.", target="https://creativecommons.org/licenses/by/4.0/")
    source_desc = ET.SubElement(file_desc, q("sourceDesc"))
    list_bibl = ET.SubElement(source_desc, q("listBibl"), {"type": "dictionaries"})
    bibl_struct = ET.SubElement(list_bibl, q("biblStruct"), {xml_attr("id"): SOURCE_WITNESS_ID})
    monogr = ET.SubElement(bibl_struct, q("monogr"))
    author = ET.SubElement(monogr, q("author"))
    text_element(author, "persName", "José de Ortega")
    text_element(monogr, "title", "Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano")
    imprint = ET.SubElement(monogr, q("imprint"))
    text_element(imprint, "pubPlace", "Tepic")
    text_element(imprint, "publisher", "Imprenta de Antonio Lagaspi")
    text_element(imprint, "date", "1888", when="1888")
    text_element(bibl_struct, "ref", "Internet Archive digital witness", type="source", target=SOURCE_WITNESS_URL)
    encoding_desc = ET.SubElement(header, q("encodingDesc"))
    project_desc = ET.SubElement(encoding_desc, q("projectDesc"))
    text_element(project_desc, "p", "This TEI document is a derived machine-only view of Cora Histórico Digital. Internal CHD data remain canonical; OCR is preserved without silent correction or linguistic normalization.")
    editorial_decl = ET.SubElement(encoding_desc, q("editorialDecl"))
    text_element(editorial_decl, "p", "Only machine_accepted alphabetical records are projected as lexical entries. machine_uncertain and machine_rejected candidates are retained as residual documentary items in back matter and are never promoted to entries.")
    add_taxonomy(encoding_desc)
    profile_desc = ET.SubElement(header, q("profileDesc"))
    lang_usage = ET.SubElement(profile_desc, q("langUsage"))
    text_element(lang_usage, "language", "Spanish", ident=OBJECT_LANGUAGE, role="objectLanguage")
    text_element(lang_usage, "language", "Cora / Náayeri (El Nayar Cora)", ident=TARGET_LANGUAGE, role="targetLanguage")
    revision_desc = ET.SubElement(header, q("revisionDesc"))
    text_element(revision_desc, "change", f"Initial CHD projection targeting TEI Lex-0 {LEX0_VERSION}.", when="2026-09-11")


def add_entry(body: ET.Element, record: dict[str, str]) -> None:
    article_id = record["article_id"]
    candidate_id = record["candidate_id"]
    if not article_id:
        raise ValueError(f"accepted record {candidate_id} lacks article_id")
    entry = ET.SubElement(body, q("entry"), {xml_attr("id"): article_id, xml_attr("lang"): OBJECT_LANGUAGE, "type": "mainEntry", "ana": "#machine_accepted #machine_derived #human_unverified", "source": f"#{SOURCE_WITNESS_ID}", "corresp": f"urn:chd:{candidate_id}", "n": record["source_printed_page"]})
    form = ET.SubElement(entry, q("form"), {"type": "lemma"})
    text_element(form, "orth", record["headword_es_ocr"])
    sense = ET.SubElement(entry, q("sense"), {xml_attr("id"): f"{article_id}-s1"})
    cit = ET.SubElement(sense, q("cit"), {"type": "translationEquivalent", xml_attr("lang"): TARGET_LANGUAGE})
    translated_form = ET.SubElement(cit, q("form"), {"type": "lemma"})
    text_element(translated_form, "orth", record["cora_ocr"])
    provenance = (f"candidate_id={candidate_id}; pdf_page={record['source_pdf_page']}; printed_page={record['source_printed_page']}; ocr_lines={record['source_ocr_line_start']}-{record['source_ocr_line_end']}; separator={record['separator_type']}; alignment={record['page_alignment_status']}; confidence={record['extraction_confidence']}; rationale={record['machine_rationale']}")
    text_element(entry, "note", provenance, type="chdProvenance")


def add_residual(back: ET.Element, record: dict[str, str]) -> None:
    status = record["machine_status"]
    item = ET.SubElement(back, q("item"), {xml_attr("id"): record["candidate_id"], "ana": f"#{status} #machine_derived #human_unverified", "source": f"#{SOURCE_WITNESS_ID}", "n": record["source_printed_page"]})
    item.text = record["raw_span_ocr"]


def build_tree(records: list[dict[str, str]]) -> tuple[ET.ElementTree, dict[str, object]]:
    assert_source_contract(records)
    status_counts = Counter(record["machine_status"] for record in records)
    accepted = [record for record in records if record["machine_status"] == "machine_accepted"]
    residual = [record for record in records if record["machine_status"] != "machine_accepted"]
    root = ET.Element(q("TEI"), {"type": "lex-0"})
    add_header(root, len(accepted), len(residual))
    text = ET.SubElement(root, q("text"))
    body = ET.SubElement(text, q("body"))
    for record in accepted:
        add_entry(body, record)
    if residual:
        back = ET.SubElement(text, q("back"))
        div = ET.SubElement(back, q("div"), {"type": "chdMachineResiduals"})
        text_element(div, "head", "Residual machine candidates not promoted to lexical entries")
        residual_list = ET.SubElement(div, q("list"))
        for record in residual:
            add_residual(residual_list, record)
    report: dict[str, object] = {
        "artifact_type": "tei_lex0_projection_report",
        "tei_namespace": TEI_NS,
        "tei_root_type": "lex-0",
        "target_lex0_version": LEX0_VERSION,
        "source_witness_id": SOURCE_WITNESS_ID,
        "source_path": DEFAULT_SOURCE.as_posix(),
        "object_language": OBJECT_LANGUAGE,
        "target_language": TARGET_LANGUAGE,
        "source_record_total": len(records),
        "entry_total": len(accepted),
        "residual_total": len(residual),
        "machine_status_counts": dict(sorted(status_counts.items())),
        "authority_status": "machine_derived",
        "human_verified": False,
        "projection_policy": "machine_accepted records become TEI Lex-0 entries; machine_uncertain and machine_rejected records remain residual documentary items in back matter.",
        "normalization_policy": "headword_es_ocr and cora_ocr are emitted verbatim; no OCR correction, equivalent splitting, modern dialect assignment, or grammatical normalization occurs.",
        "validation_scope": "This subphase checks XML well-formedness, source coverage, ID stability and field fidelity. Full validation against the official TEI Lex-0 schema remains a separate gate before phase 4 closes.",
    }
    return ET.ElementTree(root), report


def indent_tree(tree: ET.ElementTree) -> None:
    try:
        ET.indent(tree, space="  ")
    except AttributeError:
        pass


def write_outputs(tree: ET.ElementTree, report: dict[str, object], output: Path, report_path: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    indent_tree(tree)
    tree.write(output, encoding="utf-8", xml_declaration=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    records = read_records(args.source)
    tree, report = build_tree(records)
    write_outputs(tree, report, args.output, args.report)
    print(f"TEI Lex-0 projection: {report['entry_total']} entries; {report['residual_total']} residual candidates; target={LEX0_VERSION}")


if __name__ == "__main__":
    main()
