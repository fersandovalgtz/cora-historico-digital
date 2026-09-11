#!/usr/bin/env python3
"""Structure the Ortega 1888 irregular-verbs/particles appendix machine-only.

The source is heterogeneous: short verbal examples, particle descriptions,
narrative explanations and OCR noise coexist on the same final pages. This
module deliberately models paragraph-scale documentary units instead of
forcing them into the alphabetical lexicon or inventing linguistic analyses.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = Path("data/appendices/irregular_verbs_particles_ocr.txt")
DEFAULT_JSONL = Path("data/appendices/irregular_particles_machine.jsonl")
DEFAULT_CSV = Path("data/appendices/irregular_particles_machine.csv")
DEFAULT_REPORT = Path("reports/irregular_particles_machine.json")
SOURCE_WITNESS_ID = "ORTEGA1888-TEPIC-IA"

TYPE_IMPERATIVE = "imperative_example"
TYPE_EXPRESSION = "expression_example"
TYPE_PARTICLE = "particle_description"
TYPE_VERB_DESCRIPTION = "irregular_verb_description"
TYPE_FORM_CLUSTER = "form_cluster"
TYPE_PROSE = "explanatory_prose"
TYPE_NOISE = "ocr_noise"

PAGE_OR_NOISE_RE = re.compile(r"^(?:\d{1,3}|[■mI]+|wm)$", re.IGNORECASE)
IMPERATIVE_START_RE = re.compile(
    r"^(?:imperativo\b|andad\b|soci[eé]gate\b|socegaos\b)",
    re.IGNORECASE,
)
NARRATIVE_STARTS = ("preguntando ", "dice uno:", "llamo yo ")


def collapse_spaces(text: str) -> str:
    return " ".join(text.split()).strip()


def split_paragraphs_with_lines(text: str) -> list[tuple[str, int, int]]:
    """Return non-empty OCR paragraphs with inclusive source line spans."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    blocks: list[tuple[str, int, int]] = []
    current: list[str] = []
    start_line = 0

    for line_number, line in enumerate(lines, start=1):
        if line.strip():
            if not current:
                start_line = line_number
            current.append(line)
            continue
        if current:
            blocks.append(("\n".join(current).strip(), start_line, line_number - 1))
            current = []

    if current:
        blocks.append(("\n".join(current).strip(), start_line, len(lines)))
    return blocks


def classify_record(text: str) -> tuple[str, list[str]]:
    """Classify one paragraph-scale OCR unit using documentary cues only."""
    compact = collapse_spaces(text)
    lowered = compact.casefold()
    observations: list[str] = []
    alpha_count = sum(char.isalpha() for char in compact)
    punctuation_count = sum(
        not char.isalnum() and not char.isspace() for char in compact
    )

    if PAGE_OR_NOISE_RE.fullmatch(compact) or (
        len(compact) <= 60
        and alpha_count <= 8
        and punctuation_count >= alpha_count
    ):
        return TYPE_NOISE, ["machine_noise_like"]

    dash_count = compact.count("—") + compact.count("--")
    if dash_count:
        observations.append("contains_equivalence_separator_like_mark")
        if dash_count > 1:
            observations.append("contains_multiple_separator_like_marks")
    if "partícula" in lowered or "partículas" in lowered:
        observations.append("mentions_particle")
    if "vel." in lowered or " vel " in lowered:
        observations.append("contains_vel_variant_marker")
    if "?" in compact:
        observations.append("contains_question_mark")
    if "quiere decir" in lowered:
        observations.append("contains_metalinguistic_gloss")

    if lowered.startswith("por último "):
        return TYPE_PROSE, observations + ["appendix_intro"]
    if IMPERATIVE_START_RE.match(compact):
        return TYPE_IMPERATIVE, observations + ["imperative_cue"]
    if lowered.startswith("el verbo "):
        return TYPE_VERB_DESCRIPTION, observations + ["explicit_verb_description"]
    if (
        "partícula" in lowered
        or "partículas" in lowered
        or "es señal de admiración" in lowered
    ):
        return TYPE_PARTICLE, observations
    if lowered.startswith(NARRATIVE_STARTS):
        return TYPE_PROSE, observations + ["narrative_frame"]
    if dash_count:
        return TYPE_EXPRESSION, observations
    if len(compact.split()) <= 12:
        return TYPE_FORM_CLUSTER, observations
    return TYPE_PROSE, observations


def build_records(text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    blocks = split_paragraphs_with_lines(text)
    records: list[dict[str, Any]] = []

    for order, (raw_text, start_line, end_line) in enumerate(blocks, start=1):
        record_type, observations = classify_record(raw_text)
        records.append(
            {
                "irregular_id": f"ORT1888-irr-{order:03d}",
                "order": order,
                "source_witness_id": SOURCE_WITNESS_ID,
                "source_path": DEFAULT_SOURCE.as_posix(),
                "source_unit_id": f"ORT1888-irrunit-{order:03d}",
                "source_appendix_start_line": start_line,
                "source_appendix_end_line": end_line,
                "record_type": record_type,
                "raw_text_ocr": raw_text,
                "machine_observations": observations,
                "record_status": "machine_structured_appendix_unit",
                "authority_status": "machine_derived",
                "human_verified": False,
            }
        )

    ids = [record["irregular_id"] for record in records]
    orders = [record["order"] for record in records]
    unit_ids = [record["source_unit_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate irregular/particle IDs")
    if orders != list(range(1, len(records) + 1)):
        raise ValueError("irregular/particle record order is not contiguous")
    if len(unit_ids) != len(set(unit_ids)):
        raise ValueError("duplicate source unit IDs")

    type_counts = Counter(record["record_type"] for record in records)
    source_lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    report = {
        "artifact_type": "irregular_particles_machine_structure_report",
        "source_witness_id": SOURCE_WITNESS_ID,
        "source_path": DEFAULT_SOURCE.as_posix(),
        "authority_status": "machine_derived",
        "human_verified": False,
        "source_line_total": len(source_lines),
        "source_nonempty_paragraph_total": len(blocks),
        "record_total": len(records),
        "record_type_counts": dict(sorted(type_counts.items())),
        "coverage_policy": (
            "Every non-empty OCR paragraph is represented exactly once, including "
            "units classified as OCR noise."
        ),
        "classification_policy": (
            "Record types are documentary machine classifications driven by explicit "
            "surface cues. They are not normalized grammatical analyses, modern "
            "Náayeri descriptions, or human philological judgments."
        ),
        "id_policy": (
            "ORT1888-irr-### follows source paragraph order and links one-to-one to "
            "the existing appendix navigation unit ORT1888-irrunit-###."
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
            for record in records:
                row = dict(record)
                row["machine_observations"] = json.dumps(
                    row["machine_observations"], ensure_ascii=False
                )
                writer.writerow(row)

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
        f"irregular/particle machine structure: {report['record_total']} units; "
        f"types={report['record_type_counts']}; human_verified=false"
    )


if __name__ == "__main__":
    main()
