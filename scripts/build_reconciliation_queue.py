#!/usr/bin/env python3
"""Build a deterministic human-review queue for phase-2 boundary reconciliation.

The queue is a derived planning artifact. It never mutates machine candidates and it
never promotes a candidate to human-verified status. Priority is based only on
explicit extraction/alignment signals already present in candidates.csv plus a small
set of transparent OCR-surface warnings.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

DEFAULT_INPUT = Path("data/lexicon/candidates.csv")
DEFAULT_OUTPUT = Path("data/reconciliation/review_queue.csv")

OCR_ARTIFACT_RE = re.compile(r"[{}<>^\\]|(?:\b[Il1]{3,}\b)")


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def score_candidate(row: dict[str, str]) -> tuple[int, list[str]]:
    """Return a transparent review-priority score and the reasons that produced it."""
    score = 0
    reasons: list[str] = []

    if row.get("page_alignment_status") == "inferred_sequence":
        score += 100
        reasons.append("page_alignment_inferred")

    confidence = row.get("extraction_confidence", "")
    if confidence == "low":
        score += 40
        reasons.append("low_extraction_confidence")
    elif confidence == "medium":
        score += 20
        reasons.append("medium_extraction_confidence")

    if as_bool(row.get("multiple_separator_flag", "false")):
        score += 30
        reasons.append("multiple_separator")

    raw_span = row.get("raw_span_ocr", "")
    if " | " in raw_span:
        score += 10
        reasons.append("multiline_span")

    if OCR_ARTIFACT_RE.search(raw_span):
        score += 10
        reasons.append("ocr_surface_artifact")

    line_start = as_int(row.get("source_ocr_line_start"))
    line_end = as_int(row.get("source_ocr_line_end"))
    if line_end and line_start and (line_end - line_start) >= 4:
        score += 10
        reasons.append("long_ocr_span")

    if not reasons:
        reasons.append("baseline_review")

    return score, reasons


def build_queue(input_path: Path) -> list[dict[str, str]]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    queue: list[dict[str, str]] = []
    for row in rows:
        score, reasons = score_candidate(row)
        queue.append(
            {
                "candidate_id": row["candidate_id"],
                "candidate_order": str(row.get("order", "")),
                "source_pdf_page": str(row.get("source_pdf_page", "")),
                "source_printed_page": str(row.get("source_printed_page", "")),
                "priority_score": str(score),
                "priority_reasons": ";".join(reasons),
                "page_alignment_status": str(row.get("page_alignment_status", "")),
                "extraction_confidence": str(row.get("extraction_confidence", "")),
                "multiple_separator_flag": str(row.get("multiple_separator_flag", "")),
                "headword_es_ocr": str(row.get("headword_es_ocr", "")),
                "cora_ocr": str(row.get("cora_ocr", "")),
                "raw_span_ocr": str(row.get("raw_span_ocr", "")),
                "review_status": "pending_human_reconciliation",
                "human_verified": "false",
            }
        )

    queue.sort(
        key=lambda item: (
            -as_int(item["priority_score"]),
            as_int(item["candidate_order"], 10**9),
            item["candidate_id"],
        )
    )

    for index, item in enumerate(queue, start=1):
        item["queue_rank"] = str(index)

    return queue


def write_queue(rows: list[dict[str, str]], output_path: Path, limit: int | None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows if limit is None else rows[:limit]
    fieldnames = [
        "queue_rank",
        "candidate_id",
        "candidate_order",
        "source_pdf_page",
        "source_printed_page",
        "priority_score",
        "priority_reasons",
        "page_alignment_status",
        "extraction_confidence",
        "multiple_separator_flag",
        "headword_es_ocr",
        "cora_ocr",
        "raw_span_ocr",
        "review_status",
        "human_verified",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be a positive integer")
    rows = build_queue(args.input)
    write_queue(rows, args.output, args.limit)
    print(f"wrote {min(len(rows), args.limit or len(rows))} review items to {args.output}")


if __name__ == "__main__":
    main()
