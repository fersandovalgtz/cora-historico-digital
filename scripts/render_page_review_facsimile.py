#!/usr/bin/env python3
"""Render full-page facsimile evidence for scalable phase-2 human review.

Only unreconciled candidates with conservative, non-inferred page alignment are
included. The output remains machine evidence (`human_verified=false`); no human
decision is created by this script.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import fitz

from render_inferred_facsimile import render_png, sha256_file
from validate_reconciliation_decisions import DECISIONS, iter_records, load_candidates, validate_collection

DEFAULT_CANDIDATES = Path("data/lexicon/candidates.csv")
DEFAULT_PDF = Path("data/source/original/ortega_cora_1888_ia.pdf")
DEFAULT_OUTPUT_DIR = Path("artifacts/phase2_page_review")
BULK_REVIEWABLE_STATUSES = {"matched_headword", "anchored_same_page"}
INFERRED_STATUS = "inferred_sequence"


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def load_candidate_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def claimed_candidate_ids(decisions: list[dict[str, Any]]) -> set[str]:
    return {
        candidate_id
        for decision in decisions
        for candidate_id in decision["candidate_ids"]
    }


def compact_candidate(row: dict[str, str]) -> dict[str, Any]:
    printed_page = as_int(row.get("source_printed_page"))
    return {
        "candidate_id": row.get("candidate_id", ""),
        "order": as_int(row.get("order")),
        "source_pdf_page": as_int(row.get("source_pdf_page")),
        "source_printed_page": printed_page if printed_page > 0 else None,
        "page_alignment_status": row.get("page_alignment_status", ""),
        "headword_es_ocr": row.get("headword_es_ocr", ""),
        "cora_ocr": row.get("cora_ocr", ""),
        "raw_span_ocr": row.get("raw_span_ocr", ""),
        "separator_type": row.get("separator_type", ""),
        "extraction_confidence": row.get("extraction_confidence", ""),
        "source_ocr_line_start": as_int(row.get("source_ocr_line_start")),
        "source_ocr_line_end": as_int(row.get("source_ocr_line_end")),
    }


def select_reviewable_rows(
    rows: list[dict[str, str]], claimed_ids: set[str]
) -> tuple[list[dict[str, str]], list[str]]:
    reviewable: list[dict[str, str]] = []
    inferred: list[str] = []
    for row in sorted(rows, key=lambda item: as_int(item.get("order"), 10**9)):
        candidate_id = row.get("candidate_id", "")
        if candidate_id in claimed_ids:
            continue
        status = row.get("page_alignment_status", "")
        if status == INFERRED_STATUS:
            inferred.append(candidate_id)
            continue
        if status not in BULK_REVIEWABLE_STATUSES:
            raise ValueError(
                f"candidate {candidate_id!r} has unsupported bulk-review alignment status {status!r}"
            )
        reviewable.append(row)
    return reviewable, inferred


def render_page_packet(
    rows: list[dict[str, str]],
    pdf_path: Path,
    output_dir: Path,
    claimed_ids: set[str] | None = None,
    dpi: int = 120,
) -> dict[str, Any]:
    if dpi < 72:
        raise ValueError("dpi must be at least 72")
    if not pdf_path.is_file():
        raise FileNotFoundError(f"missing source PDF: {pdf_path}")

    claimed_ids = claimed_ids or set()
    known_ids = {row.get("candidate_id", "") for row in rows}
    unknown_claimed = sorted(claimed_ids - known_ids)
    if unknown_claimed:
        raise ValueError("claimed candidate IDs are absent from inventory: " + ", ".join(unknown_claimed))

    reviewable, excluded_inferred = select_reviewable_rows(rows, claimed_ids)
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in reviewable:
        page = as_int(row.get("source_pdf_page"))
        if page < 1:
            raise ValueError(f"candidate {row.get('candidate_id')!r} has invalid source_pdf_page")
        grouped[page].append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(pdf_path)
    page_records: list[dict[str, Any]] = []

    try:
        for page_number in sorted(grouped):
            if page_number > document.page_count:
                raise ValueError(
                    f"candidate references PDF page {page_number}, but document has {document.page_count} pages"
                )
            relative = Path("pages") / f"page-{page_number:03d}-full.png"
            render_png(document.load_page(page_number - 1), output_dir / relative, dpi)
            page_rows = grouped[page_number]
            printed_pages = sorted(
                {
                    value
                    for value in (as_int(row.get("source_printed_page")) for row in page_rows)
                    if value > 0
                }
            )
            page_records.append(
                {
                    "source_pdf_page": page_number,
                    "source_printed_pages": printed_pages,
                    "path": relative.as_posix(),
                    "candidate_count": len(page_rows),
                    "candidates": [compact_candidate(row) for row in page_rows],
                }
            )
    finally:
        document.close()

    manifest = {
        "artifact_type": "facsimile_page_review_packet",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_sha256": sha256_file(pdf_path),
        "machine_generated": True,
        "human_verified": False,
        "facsimile_required": True,
        "reviewable_alignment_statuses": sorted(BULK_REVIEWABLE_STATUSES),
        "render_dpi": dpi,
        "candidate_total": len(rows),
        "already_reconciled_candidate_total": len(claimed_ids),
        "reviewable_candidate_total": len(reviewable),
        "excluded_inferred_candidate_total": len(excluded_inferred),
        "excluded_inferred_candidate_ids": excluded_inferred,
        "review_page_total": len(page_records),
        "pages": page_records,
        "method_note": (
            "This packet groups unreconciled matched_headword and anchored_same_page candidates "
            "by physical PDF page for human inspection. Inferred or unknown alignment states never "
            "enter bulk review. Page images and metadata are machine-generated evidence; no "
            "candidate is human-verified until a reviewer explicitly records a decision."
        ),
    }
    (output_dir / "page_review_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=120)
    args = parser.parse_args()

    candidate_map = load_candidates(args.candidates)
    decisions = validate_collection(iter_records(args.decisions_dir), candidate_map)
    manifest = render_page_packet(
        load_candidate_rows(args.candidates),
        args.pdf,
        args.output_dir,
        claimed_ids=claimed_candidate_ids(decisions),
        dpi=args.dpi,
    )
    print(
        f"rendered {manifest['review_page_total']} review pages for "
        f"{manifest['reviewable_candidate_total']} unreconciled candidates; "
        f"excluded {manifest['excluded_inferred_candidate_total']} inferred cases"
    )


if __name__ == "__main__":
    main()
