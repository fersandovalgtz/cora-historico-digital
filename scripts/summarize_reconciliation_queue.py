#!/usr/bin/env python3
"""Summarize a machine-generated phase-2 reconciliation review queue."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

DEFAULT_INPUT = Path("data/reconciliation/review_queue.csv")
DEFAULT_OUTPUT = Path("reports/reconciliation_queue_summary.json")


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def risk_tier(score: int) -> str:
    if score >= 100:
        return "critical_structural_review"
    if score >= 50:
        return "high_priority_review"
    if score >= 20:
        return "medium_priority_review"
    return "baseline_review"


def summarize(rows: list[dict[str, str]], top_n: int = 25) -> dict:
    scores = Counter()
    reasons = Counter()
    tiers = Counter()
    alignment = Counter()
    confidence = Counter()
    pages = Counter()

    for row in rows:
        score = as_int(row.get("priority_score"))
        scores[str(score)] += 1
        tiers[risk_tier(score)] += 1
        alignment[row.get("page_alignment_status", "")] += 1
        confidence[row.get("extraction_confidence", "")] += 1
        page = row.get("source_pdf_page", "")
        if page:
            pages[page] += 1
        for reason in filter(None, row.get("priority_reasons", "").split(";")):
            reasons[reason] += 1

    top = []
    for row in rows[:top_n]:
        top.append(
            {
                "queue_rank": as_int(row.get("queue_rank")),
                "candidate_id": row.get("candidate_id", ""),
                "candidate_order": as_int(row.get("candidate_order")),
                "source_pdf_page": as_int(row.get("source_pdf_page")),
                "source_printed_page": as_int(row.get("source_printed_page")),
                "priority_score": as_int(row.get("priority_score")),
                "priority_reasons": list(filter(None, row.get("priority_reasons", "").split(";"))),
                "headword_es_ocr": row.get("headword_es_ocr", ""),
            }
        )

    return {
        "artifact_type": "machine_reconciliation_queue_summary",
        "human_verified": False,
        "total_candidates": len(rows),
        "risk_tiers": dict(sorted(tiers.items())),
        "priority_score_distribution": dict(
            sorted(scores.items(), key=lambda item: int(item[0]), reverse=True)
        ),
        "priority_reason_counts": dict(sorted(reasons.items())),
        "page_alignment_status_counts": dict(sorted(alignment.items())),
        "extraction_confidence_counts": dict(sorted(confidence.items())),
        "source_pdf_page_counts": dict(sorted(pages.items(), key=lambda item: as_int(item[0]))),
        "top_priority_candidates": top,
        "method_note": (
            "This report summarizes machine triage only. Scores and tiers are review-order aids, "
            "not philological or linguistic decisions."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-n", type=int, default=25)
    args = parser.parse_args()
    if args.top_n < 0:
        raise SystemExit("--top-n must be zero or greater")

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"review queue is empty: {args.input}")

    report = summarize(rows, top_n=args.top_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"summarized {len(rows)} review items to {args.output}")


if __name__ == "__main__":
    main()
