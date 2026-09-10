#!/usr/bin/env python3
"""Extract explicit Spanish–Cora numeral pairs as machine candidates.

This deliberately models only lines with an explicit pair separator. Productive
rules and explanatory prose remain in the raw appendix and are not silently
converted into lexical records.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from audit_source_coverage import FULL_OCR, locate_partition_ranges, norm_key
from lexicon_text import clean_headword_boundary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data/appendices/numeral_pair_candidates.csv"
DEFAULT_JSONL = ROOT / "data/appendices/numeral_pair_candidates.jsonl"
DEFAULT_REPORT = ROOT / "reports/numeral_pair_extraction.json"

SOURCE_WITNESS_ID = "ORTEGA1888-TEPIC-IA"
APPENDIX_ID = "numerals_appendix"
ID_PREFIX = "ORT1888-numcand-"
REVIEW_STATUS = "unreviewed_machine_pair_candidate"

CONSTRUCTION_GENERAL = "general_cardinal"
CONSTRUCTION_FREQUENCY = "frequency_expression"
CONSTRUCTION_ANIMATE = "animate_cardinal"
CONSTRUCTION_TYPES = {
    CONSTRUCTION_GENERAL,
    CONSTRUCTION_FREQUENCY,
    CONSTRUCTION_ANIMATE,
}

FREQUENCY_MARKER = "Para decir una vez, dos veces"
ANIMATE_MARKER = "Para decir dos hombres, tres hombres"

FIELDS = [
    "candidate_id",
    "order",
    "source_witness_id",
    "appendix_id",
    "source_ocr_line_start",
    "source_ocr_line_end",
    "expression_es_ocr",
    "cora_ocr",
    "raw_line_ocr",
    "separator_type",
    "construction_type_machine",
    "pair_extraction_confidence",
    "review_status",
    "human_verified",
]


def collapsed(text: str) -> str:
    return " ".join(text.split()).strip()


def split_explicit_pair(line: str) -> tuple[str, str, str] | None:
    """Return left/right pair only for conservative explicit separator forms."""
    raw = collapsed(line)
    if not raw:
        return None

    if "—" in raw:
        left, right = raw.split("—", 1)
        expression = clean_headword_boundary(left)
        right = right.strip()
        if expression and right and any(char.isalpha() for char in expression) and any(
            char.isalpha() for char in right
        ):
            return expression, right, "em_dash"

    double_hyphen = re.match(r"^(?P<a>.{1,80}?)[.]?\s*--+\s*(?P<b>\S.*)$", raw)
    if double_hyphen:
        expression = clean_headword_boundary(double_hyphen.group("a"))
        right = double_hyphen.group("b").strip()
        if expression and right and any(char.isalpha() for char in expression) and any(
            char.isalpha() for char in right
        ):
            return expression, right, "double_hyphen"

    # Locked-source OCR form on the animate-cardinal line: ``Tres'.-sMahi...``.
    dotted_hyphen = re.match(r"^(?P<a>.{1,40}?)\.\s*-\s*(?P<b>[sS]\S.*)$", raw)
    if dotted_hyphen:
        expression = clean_headword_boundary(dotted_hyphen.group("a"))
        right = dotted_hyphen.group("b").strip()
        if expression and right:
            return expression, right, "ocr_dotted_hyphen"

    return None


def extract_candidates(lines: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    ranges = locate_partition_ranges(lines)
    start, end = ranges[APPENDIX_ID]
    section = CONSTRUCTION_GENERAL
    rows: list[dict[str, Any]] = []
    nonblank = 0

    for index in range(start, end):
        original = lines[index]
        raw = collapsed(original)
        if not raw:
            continue
        nonblank += 1
        key = norm_key(raw)
        if norm_key(FREQUENCY_MARKER) in key:
            section = CONSTRUCTION_FREQUENCY
            continue
        if norm_key(ANIMATE_MARKER) in key:
            section = CONSTRUCTION_ANIMATE
            continue

        pair = split_explicit_pair(original)
        if pair is None:
            continue
        expression, cora, separator = pair
        confidence = "high" if separator == "em_dash" else "medium"
        rows.append(
            {
                "candidate_id": f"{ID_PREFIX}{len(rows) + 1:06d}",
                "order": len(rows) + 1,
                "source_witness_id": SOURCE_WITNESS_ID,
                "appendix_id": APPENDIX_ID,
                "source_ocr_line_start": index + 1,
                "source_ocr_line_end": index + 1,
                "expression_es_ocr": expression,
                "cora_ocr": cora,
                "raw_line_ocr": original,
                "separator_type": separator,
                "construction_type_machine": section,
                "pair_extraction_confidence": confidence,
                "review_status": REVIEW_STATUS,
                "human_verified": False,
            }
        )

    return rows, {
        "appendix_line_total": end - start,
        "nonblank_line_total": nonblank,
        "explicit_pair_line_total": len(rows),
        "nonpair_nonblank_line_total": nonblank - len(rows),
    }


def validate_candidates(rows: list[dict[str, Any]], lines: list[str]) -> None:
    ranges = locate_partition_ranges(lines)
    appendix_start, appendix_end = ranges[APPENDIX_ID]
    first_line = appendix_start + 1
    last_line = appendix_end
    seen_lines: set[int] = set()

    for expected_order, row in enumerate(rows, start=1):
        expected_id = f"{ID_PREFIX}{expected_order:06d}"
        if row.get("candidate_id") != expected_id:
            raise ValueError(
                f"numeral candidate ID sequence mismatch: expected {expected_id}, got {row.get('candidate_id')!r}"
            )
        if row.get("order") != expected_order:
            raise ValueError(f"{expected_id} has non-sequential order {row.get('order')!r}")
        if row.get("source_witness_id") != SOURCE_WITNESS_ID:
            raise ValueError(f"{expected_id} has unexpected source_witness_id")
        if row.get("appendix_id") != APPENDIX_ID:
            raise ValueError(f"{expected_id} has unexpected appendix_id")
        if row.get("human_verified") is not False:
            raise ValueError(f"{expected_id} must remain human_verified=false")
        if row.get("review_status") != REVIEW_STATUS:
            raise ValueError(f"{expected_id} has unexpected review_status")
        if row.get("construction_type_machine") not in CONSTRUCTION_TYPES:
            raise ValueError(f"{expected_id} has unsupported construction type")
        start = row.get("source_ocr_line_start")
        end = row.get("source_ocr_line_end")
        if type(start) is not int or type(end) is not int or start != end:
            raise ValueError(f"{expected_id} must reference exactly one OCR source line")
        if start < first_line or start > last_line:
            raise ValueError(f"{expected_id} points outside the numeral appendix: line {start}")
        if start in seen_lines:
            raise ValueError(f"multiple numeral candidates point to OCR line {start}")
        seen_lines.add(start)
        if not str(row.get("expression_es_ocr", "")).strip() or not str(row.get("cora_ocr", "")).strip():
            raise ValueError(f"{expected_id} has an empty pair side")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            serialized["human_verified"] = "false"
            writer.writerow(serialized)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_report(rows: list[dict[str, Any]], metrics: dict[str, int]) -> dict[str, Any]:
    return {
        "artifact_type": "numeral_pair_machine_extraction",
        "source_witness_id": SOURCE_WITNESS_ID,
        "appendix_id": APPENDIX_ID,
        "machine_generated": True,
        "human_verified": False,
        "scope": "explicit_spanish_cora_pair_lines_only",
        "candidate_namespace": f"{ID_PREFIX}######",
        "candidate_total": len(rows),
        "counts_by_construction_type": dict(
            sorted(Counter(row["construction_type_machine"] for row in rows).items())
        ),
        "counts_by_separator_type": dict(
            sorted(Counter(row["separator_type"] for row in rows).items())
        ),
        **metrics,
        "unmodeled_context_retained": True,
        "appendix_fully_structured": False,
        "method_note": (
            "Only explicit Spanish–Cora pair lines are represented as machine candidates. "
            "Explanatory prose, productive counting rules, and other non-pair content remain in "
            "data/appendices/numerals_ocr.txt and require a separate structural model."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-ocr", type=Path, default=FULL_OCR)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--jsonl-output", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    lines = args.full_ocr.read_text(encoding="utf-8").splitlines()
    rows, metrics = extract_candidates(lines)
    validate_candidates(rows, lines)
    write_csv(args.csv_output, rows)
    write_jsonl(args.jsonl_output, rows)
    report = build_report(rows, metrics)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"extracted {len(rows)} numeral pair candidates; "
        f"{metrics['nonpair_nonblank_line_total']} non-pair nonblank lines remain contextual"
    )


if __name__ == "__main__":
    main()
