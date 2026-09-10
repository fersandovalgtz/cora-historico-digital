#!/usr/bin/env python3
"""Build the machine-only lexical layer from Ortega 1888 candidates.

This step never claims human verification. It promotes candidates with sufficient
reproducible alignment evidence to stable machine article IDs and preserves
residual ambiguous candidates explicitly as machine_uncertain.
"""
from __future__ import annotations

import argparse
import csv
import json
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


def as_int(value: object) -> int:
    return int(str(value).strip())


def resolve_candidate(row: dict[str, str]) -> dict[str, Any]:
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
    records = [resolve_candidate(row) for row in ordered]
    orders = [record["order"] for record in records]
    if orders != list(range(1, len(records) + 1)):
        raise ValueError("candidate order must be contiguous 1..N")
    candidate_ids = [record["candidate_id"] for record in records]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("duplicate candidate IDs")
    article_ids = [record["article_id"] for record in records if record["article_id"]]
    if len(article_ids) != len(set(article_ids)):
        raise ValueError("duplicate article IDs")
    status_counts = Counter(record["machine_status"] for record in records)
    alignment_counts = Counter(record["page_alignment_status"] for record in records)
    uncertain = [record["candidate_id"] for record in records if record["machine_status"] == "machine_uncertain"]
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
        "release_policy": "A machine-only release may retain machine_uncertain candidates. Only machine_accepted records receive stable ORT1888-art IDs; uncertainty is preserved rather than guessed.",
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
    print(f"machine corpus: {report['machine_article_total']} accepted articles; {report['machine_uncertain_total']} uncertain candidates; human_verified=false")


if __name__ == "__main__":
    main()
