#!/usr/bin/env python3
"""Extract explicit Spanish–Cora numeral pairs from the Ortega 1888 appendix.

The extractor is deliberately documentary. It recognizes separator-bearing lines
and the explicit series transitions stated by the source, but it does not
normalize Cora forms, assign modern linguistic analyses, or repair OCR.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = Path("data/appendices/numerals_ocr.txt")
DEFAULT_JSONL = Path("data/appendices/numerals_machine.jsonl")
DEFAULT_CSV = Path("data/appendices/numerals_machine.csv")
DEFAULT_REPORT = Path("reports/numerals_machine.json")
SOURCE_WITNESS_ID = "ORTEGA1888-TEPIC-IA"

SERIES_GENERAL = "general_count"
SERIES_FREQUENCY = "frequency_count"
SERIES_ANIMATE = "animate_count"

FREQUENCY_MARKER = "para decir una vez"
ANIMATE_MARKER = "para decir dos hombres"

HYPHEN_PATTERNS = (
    re.compile(r"^(?P<a>.{1,60}?)[.]?\s*--+\s*(?P<b>\S.*)$"),
    re.compile(r"^(?P<a>.{1,60}?)[.']?\s*-\s*(?P<b>\S.*)$"),
)


def collapse_spaces(text: str) -> str:
    return " ".join(text.split()).strip()


def split_explicit_pair(line: str) -> tuple[str, str, str] | None:
    """Split one OCR line into left/right expressions without correcting either.

    The em dash is the primary separator in the witness. Two conservative ASCII
    hyphen fallbacks cover OCR forms such as ``Dos veces. --Huappoax.`` and
    ``Tres'.-sMahiuzM'ca.``. Ordinary word-final hyphenation cannot match because
    a non-empty right-hand expression is required on the same line.
    """
    raw = line.strip()
    if not raw:
        return None

    if "—" in raw:
        left, right = raw.split("—", 1)
        left = left.strip()
        right = right.strip()
        separator_type = "em_dash"
    else:
        match = None
        for pattern in HYPHEN_PATTERNS:
            match = pattern.match(raw)
            if match:
                break
        if not match:
            return None
        left = match.group("a").strip()
        right = match.group("b").strip()
        separator_type = "hyphen_variant"

    if not left or not right:
        return None
    if not any(char.isalpha() for char in left):
        return None
    if not any(char.isalpha() for char in right):
        return None
    if len(left.split()) > 8:
        return None

    lowered = collapse_spaces(left).casefold()
    if lowered.startswith(("y así", "asi ", "así ", "cuando ", "para decir ")):
        return None

    return left, right, separator_type


def series_for_line(line: str, current: str) -> str:
    lowered = collapse_spaces(line).casefold()
    if lowered.startswith(FREQUENCY_MARKER):
        return SERIES_FREQUENCY
    if lowered.startswith(ANIMATE_MARKER):
        return SERIES_ANIMATE
    return current


def build_records(text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    records: list[dict[str, Any]] = []
    series = SERIES_GENERAL

    for line_number, line in enumerate(lines, start=1):
        series = series_for_line(line, series)
        pair = split_explicit_pair(line)
        if not pair:
            continue
        left, right, separator_type = pair
        record_number = len(records) + 1
        records.append(
            {
                "numeral_id": f"ORT1888-num-{record_number:03d}",
                "order": record_number,
                "source_witness_id": SOURCE_WITNESS_ID,
                "source_path": DEFAULT_SOURCE.as_posix(),
                "source_appendix_line": line_number,
                "semantic_series": series,
                "spanish_expression_ocr": left,
                "cora_expression_ocr": right,
                "raw_line_ocr": line.strip(),
                "separator_type": separator_type,
                "record_status": "machine_extracted_explicit_pair",
                "authority_status": "machine_derived",
                "human_verified": False,
            }
        )

    orders = [record["order"] for record in records]
    if orders != list(range(1, len(records) + 1)):
        raise ValueError("numeral record order is not contiguous")
    ids = [record["numeral_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate numeral IDs")

    series_counts = Counter(record["semantic_series"] for record in records)
    separator_counts = Counter(record["separator_type"] for record in records)
    nonempty_lines = sum(bool(line.strip()) for line in lines)
    report = {
        "artifact_type": "numeral_machine_extraction_report",
        "source_witness_id": SOURCE_WITNESS_ID,
        "source_path": DEFAULT_SOURCE.as_posix(),
        "authority_status": "machine_derived",
        "human_verified": False,
        "source_line_total": len(lines),
        "source_nonempty_line_total": nonempty_lines,
        "explicit_pair_total": len(records),
        "series_counts": dict(sorted(series_counts.items())),
        "separator_counts": dict(sorted(separator_counts.items())),
        "series_policy": {
            SERIES_GENERAL: "default series before any explicit source transition",
            SERIES_FREQUENCY: "begins at the source marker 'Para decir una vez, dos veces, etc. dicen:'",
            SERIES_ANIMATE: "begins at the source marker 'Para decir dos hombres, tres hombres...'",
        },
        "scope_note": (
            "Records represent only explicit separator-bearing Spanish–Cora lines. "
            "Narrative instructions, multiplication rules, page numbers and OCR noise remain "
            "in the preserved source and navigation inventory; no missing form is inferred."
        ),
    }
    return records, report


def write_outputs(
    records: list[dict[str, Any]],
    report: dict[str, Any],
    jsonl_path: Path,
    csv_path: Path,
    report_path: Path,
) -> None:
    for path in (jsonl_path, csv_path, report_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    fields = list(records[0]) if records else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if fields:
            writer.writeheader()
            writer.writerows(records)

    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--csv", dest="csv_path", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    records, report = build_records(args.source.read_text(encoding="utf-8"))
    write_outputs(records, report, args.jsonl, args.csv_path, args.report)
    print(
        f"numeral machine extraction: {report['explicit_pair_total']} explicit pairs; "
        f"series={report['series_counts']}; human_verified=false"
    )


if __name__ == "__main__":
    main()
