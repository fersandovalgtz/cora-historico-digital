#!/usr/bin/env python3
"""Build the machine-only lexical layer from Ortega 1888 candidates.

This step never claims human verification. It promotes candidates with sufficient
reproducible alignment evidence to stable machine article IDs, rejects narrowly
defined OCR boundary artifacts, and preserves residual ambiguity explicitly as
``machine_uncertain``.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_CANDIDATES = Path("data/lexicon/candidates.csv")
DEFAULT_JSONL = Path("data/lexicon/machine_lexicon.jsonl")
DEFAULT_CSV = Path("data/lexicon/machine_lexicon.csv")
DEFAULT_REPORT = Path("reports/machine_resolution.json")

ACCEPTED_ALIGNMENTS = {
    "matched_headword": "direct_page_headword_match",
    "anchored_same_page": "same_page_anchor_support",
}
KNOWN_ALIGNMENTS = set(ACCEPTED_ALIGNMENTS) | {"inferred_sequence"}
DIRECT_ALIGNMENT = "matched_headword"


def as_int(value: object) -> int:
    return int(str(value).strip())


def raw_span_has_standalone_page_number(raw_span: str, page_number: int) -> bool:
    """Return true only for a standalone OCR span segment equal to the folio number.

    Candidate spans join non-empty OCR lines with `` | ``. Requiring an entire
    segment to equal the expected next printed page avoids matching ordinary
    numerals embedded in lexical content.
    """
    return any(part.strip() == str(page_number) for part in raw_span.split("|"))


def is_prefolio_boundary_noise(
    row: dict[str, str],
    previous_row: dict[str, str] | None,
    next_row: dict[str, str] | None,
) -> bool:
    """Detect a narrow class of false candidates caused by page-top OCR noise.

    The rule is intentionally structural rather than linguistic. A candidate is
    rejected only when all of the following hold:

    * its page alignment is unresolved (``inferred_sequence``);
    * it came from the weak hyphen-variant extractor with low confidence;
    * the nearest source-order neighbours are direct page matches;
    * the previous direct match is on the candidate's assigned PDF page;
    * the next direct match is exactly one PDF page later; and
    * the candidate OCR span itself contains, as a standalone line, the printed
      number of that next page.

    This encodes the observed pattern ``page-top noise → folio number → first
    genuine entry`` without hard-coding candidate IDs or lexical forms.
    """
    if row.get("page_alignment_status") != "inferred_sequence":
        return False
    if row.get("separator_type") != "hyphen_variant":
        return False
    if row.get("extraction_confidence") != "low":
        return False
    if previous_row is None or next_row is None:
        return False
    if previous_row.get("page_alignment_status") != DIRECT_ALIGNMENT:
        return False
    if next_row.get("page_alignment_status") != DIRECT_ALIGNMENT:
        return False

    candidate_pdf = as_int(row["source_pdf_page"])
    previous_pdf = as_int(previous_row["source_pdf_page"])
    next_pdf = as_int(next_row["source_pdf_page"])
    next_printed = as_int(next_row["source_printed_page"])

    if previous_pdf != candidate_pdf:
        return False
    if next_pdf != candidate_pdf + 1:
        return False
    if next_printed != next_pdf - 4:
        return False
    return raw_span_has_standalone_page_number(row.get("raw_span_ocr", ""), next_printed)


def resolve_candidate(
    row: dict[str, str],
    previous_row: dict[str, str] | None = None,
    next_row: dict[str, str] | None = None,
) -> dict[str, Any]:
    alignment = row.get("page_alignment_status", "")
    if alignment not in KNOWN_ALIGNMENTS:
        raise ValueError(f"unknown page_alignment_status for {row.get('candidate_id')}: {alignment}")
    order = as_int(row["order"])
    candidate_id = row["candidate_id"]
    expected_id = f"ORT1888-cand-{order:06d}"
    if candidate_id != expected_id:
        raise ValueError(f"candidate/order mismatch: {candidate_id} != {expected_id}")

    if alignment in ACCEPTED_ALIGNMENTS:
        machine_status = "machine_accepted"
        article_id: str | None = f"ORT1888-art-{order:06d}"
        rationale = ACCEPTED_ALIGNMENTS[alignment]
        release_eligible = True
    elif is_prefolio_boundary_noise(row, previous_row, next_row):
        machine_status = "machine_rejected"
        article_id = None
        rationale = "prefolio_noise_between_consecutive_direct_page_anchors"
        release_eligible = False
    else:
        machine_status = "machine_uncertain"
        article_id = None
        rationale = "page_alignment_unresolved"
        release_eligible = False

    return {
        "article_id": article_id,
        "candidate_id": candidate_id,
        "order": order,
        "source_witness_id": row["source_witness_id"],
        "source_pdf_page": as_int(row["source_pdf_page"]),
        "source_printed_page": as_int(row["source_printed_page"]),
        "source_ocr_line_start": as_int(row["source_ocr_line_start"]),
        "source_ocr_line_end": as_int(row["source_ocr_line_end"]),
        "headword_es_ocr": row["headword_es_ocr"],
        "cora_ocr": row["cora_ocr"],
        "raw_span_ocr": row["raw_span_ocr"],
        "separator_type": row["separator_type"],
        "page_alignment_status": alignment,
        "extraction_confidence": row["extraction_confidence"],
        "machine_status": machine_status,
        "machine_rationale": rationale,
        "authority_status": "machine_derived",
        "release_eligible": release_eligible,
        "human_verified": False,
    }


def build_machine_corpus(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: as_int(row["order"]))
    orders = [as_int(row["order"]) for row in ordered]
    if orders != list(range(1, len(ordered) + 1)):
        raise ValueError("candidate order must be contiguous 1..N")

    candidate_ids = [row["candidate_id"] for row in ordered]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("duplicate candidate IDs")

    records: list[dict[str, Any]] = []
    for index, row in enumerate(ordered):
        previous_row = ordered[index - 1] if index > 0 else None
        next_row = ordered[index + 1] if index + 1 < len(ordered) else None
        records.append(resolve_candidate(row, previous_row, next_row))

    article_ids = [record["article_id"] for record in records if record["article_id"]]
    if len(article_ids) != len(set(article_ids)):
        raise ValueError("duplicate article IDs")

    status_counts = Counter(record["machine_status"] for record in records)
    alignment_counts = Counter(record["page_alignment_status"] for record in records)
    uncertain = [record["candidate_id"] for record in records if record["machine_status"] == "machine_uncertain"]
    rejected = [record["candidate_id"] for record in records if record["machine_status"] == "machine_rejected"]
    report = {
        "artifact_type": "machine_resolution_report",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "authority_status": "machine_derived",
        "human_verified": False,
        "candidate_total": len(records),
        "machine_article_total": status_counts.get("machine_accepted", 0),
        "machine_uncertain_total": status_counts.get("machine_uncertain", 0),
        "machine_rejected_total": status_counts.get("machine_rejected", 0),
        "machine_status_counts": dict(sorted(status_counts.items())),
        "page_alignment_counts": dict(sorted(alignment_counts.items())),
        "machine_uncertain_candidate_ids": uncertain,
        "machine_rejected_candidate_ids": rejected,
        "release_policy": "A machine-only release may retain machine_uncertain and machine_rejected source candidates. Only machine_accepted records receive stable ORT1888-art IDs; uncertainty is preserved and rejected segmentation artifacts remain traceable rather than deleted.",
        "id_policy": "Accepted article IDs reuse the six-digit numeric suffix of their source candidate. This prevents renumbering when another candidate later changes machine status.",
    }
    return records, report


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_outputs(records: list[dict[str, Any]], report: dict[str, Any], jsonl: Path, csv_path: Path, report_path: Path) -> None:
    for path in (jsonl, csv_path, report_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    fields = list(records[0]) if records else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if fields:
            writer.writeheader()
            writer.writerows(records)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--csv", dest="csv_path", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    records, report = build_machine_corpus(load_candidates(args.candidates))
    write_outputs(records, report, args.jsonl, args.csv_path, args.report)
    print(
        "machine corpus: "
        f"{report['machine_article_total']} accepted articles; "
        f"{report['machine_rejected_total']} rejected segmentation artifacts; "
        f"{report['machine_uncertain_total']} uncertain candidates; "
        "human_verified=false"
    )


if __name__ == "__main__":
    main()
