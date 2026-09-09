#!/usr/bin/env python3
"""Build an evidence packet for candidates that still lack direct page alignment.

The packet is machine-generated and is not a reconciliation decision. It gathers
nearby direct anchors and page-boundary OCR excerpts so a human reviewer can inspect
the remaining cases against the facsimile with less navigation overhead.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_CANDIDATES = Path("data/lexicon/candidates.csv")
DEFAULT_PAGES_DIR = Path("data/source/ocr/pdf_pages")
DEFAULT_JSON = Path("data/reconciliation/inferred_review_batch.json")
DEFAULT_MARKDOWN = Path("reports/inferred_review_batch.md")

ALLOWED_ACTIONS = [
    "accept_boundary",
    "merge_candidates",
    "split_candidate",
    "reject_false_boundary",
    "defer_uncertain",
]


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def compact_candidate(row: dict[str, str] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "candidate_id": row.get("candidate_id", ""),
        "order": as_int(row.get("order")),
        "source_pdf_page": as_int(row.get("source_pdf_page")),
        "source_printed_page": as_int(row.get("source_printed_page")),
        "page_alignment_status": row.get("page_alignment_status", ""),
        "headword_es_ocr": row.get("headword_es_ocr", ""),
        "cora_ocr": row.get("cora_ocr", ""),
        "raw_span_ocr": row.get("raw_span_ocr", ""),
        "separator_type": row.get("separator_type", ""),
        "extraction_confidence": row.get("extraction_confidence", ""),
        "source_ocr_line_start": as_int(row.get("source_ocr_line_start")),
        "source_ocr_line_end": as_int(row.get("source_ocr_line_end")),
    }


def nearest_direct(rows: list[dict[str, str]], index: int, step: int) -> dict[str, str] | None:
    cursor = index + step
    while 0 <= cursor < len(rows):
        if rows[cursor].get("page_alignment_status") == "matched_headword":
            return rows[cursor]
        cursor += step
    return None


def machine_observations(
    target: dict[str, str],
    previous_anchor: dict[str, str] | None,
    next_anchor: dict[str, str] | None,
) -> list[str]:
    observations: list[str] = []
    headword = target.get("headword_es_ocr", "").strip()
    raw_span = target.get("raw_span_ocr", "")

    if len(headword) == 1:
        observations.append("single_character_headword")
    if headword and not headword.isalpha():
        observations.append("symbolic_headword")
    if target.get("separator_type") != "em_dash":
        observations.append("non_em_dash_separator")
    if any(part.strip().isdigit() for part in raw_span.split("|")):
        observations.append("raw_span_contains_page_number")

    if previous_anchor and next_anchor:
        previous_page = as_int(previous_anchor.get("source_pdf_page"))
        next_page = as_int(next_anchor.get("source_pdf_page"))
        if previous_page != next_page:
            observations.append("between_direct_anchors_on_different_pages")

    return observations or ["no_additional_machine_observation"]


def page_excerpt(path: Path, context_lines: int) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing page evidence: {path}")
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        "path": path.as_posix(),
        "line_count_nonempty": len(lines),
        "head": lines[:context_lines],
        "tail": lines[-context_lines:],
    }


def build_batch(
    rows: list[dict[str, str]],
    pages_dir: Path,
    context_lines: int = 12,
) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: as_int(row.get("order"), 10**9))
    cases: list[dict[str, Any]] = []

    for index, target in enumerate(ordered):
        if target.get("page_alignment_status") != "inferred_sequence":
            continue

        previous_anchor = nearest_direct(ordered, index, -1)
        next_anchor = nearest_direct(ordered, index, 1)
        page_numbers = {
            as_int(target.get("source_pdf_page")),
            as_int(previous_anchor.get("source_pdf_page")) if previous_anchor else 0,
            as_int(next_anchor.get("source_pdf_page")) if next_anchor else 0,
        }
        page_numbers.discard(0)

        evidence = []
        for page_number in sorted(page_numbers):
            path = pages_dir / f"page-{page_number:03d}.txt"
            evidence.append(
                {
                    "source_pdf_page": page_number,
                    "source_printed_page": page_number - 4,
                    "extracted_pdf_text": page_excerpt(path, context_lines),
                }
            )

        cases.append(
            {
                "candidate_id": target.get("candidate_id", ""),
                "review_status": "pending_human_reconciliation",
                "human_verified": False,
                "facsimile_required": True,
                "target": compact_candidate(target),
                "previous_direct_anchor": compact_candidate(previous_anchor),
                "next_direct_anchor": compact_candidate(next_anchor),
                "machine_observations": machine_observations(target, previous_anchor, next_anchor),
                "page_evidence": evidence,
                "allowed_human_actions": ALLOWED_ACTIONS,
            }
        )

    return {
        "artifact_type": "machine_inferred_alignment_review_batch",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "human_verified": False,
        "facsimile_required": True,
        "case_count": len(cases),
        "cases": cases,
        "method_note": (
            "This packet is navigation evidence only. Extracted PDF text and machine observations "
            "must not be treated as facsimile inspection or as a philological decision."
        ),
    }


def render_markdown(batch: dict[str, Any]) -> str:
    lines = [
        "# Lote de cotejo humano — alineaciones todavía inferidas",
        "",
        f"Casos: **{batch['case_count']}**",
        "",
        "**Estado epistemológico:** generado por máquina; `human_verified=false`; "
        "el facsímil es obligatorio antes de registrar una decisión.",
        "",
        batch["method_note"],
        "",
    ]

    for number, case in enumerate(batch["cases"], start=1):
        target = case["target"]
        previous_anchor = case["previous_direct_anchor"]
        next_anchor = case["next_direct_anchor"]
        lines.extend(
            [
                f"## {number}. {case['candidate_id']} — `{target['headword_es_ocr']}`",
                "",
                f"- Estado: `{case['review_status']}`; `human_verified=false`; facsímil requerido: sí.",
                f"- Página asignada: PDF {target['source_pdf_page']} / impresa {target['source_printed_page']}.",
                f"- Span OCR: `{target['raw_span_ocr']}`",
                f"- Observaciones automáticas: {', '.join(case['machine_observations'])}.",
                "",
            ]
        )
        if previous_anchor:
            lines.append(
                f"Anclaje directo anterior: `{previous_anchor['candidate_id']}` — "
                f"{previous_anchor['headword_es_ocr']} (PDF {previous_anchor['source_pdf_page']})."
            )
        if next_anchor:
            lines.append(
                f"Anclaje directo siguiente: `{next_anchor['candidate_id']}` — "
                f"{next_anchor['headword_es_ocr']} (PDF {next_anchor['source_pdf_page']})."
            )
        lines.append("")

        for page in case["page_evidence"]:
            excerpt = page["extracted_pdf_text"]
            lines.extend(
                [
                    f"### PDF {page['source_pdf_page']} / impresa {page['source_printed_page']}",
                    "",
                    "Inicio del texto extraído:",
                    "```text",
                    *excerpt["head"],
                    "```",
                    "",
                    "Final del texto extraído:",
                    "```text",
                    *excerpt["tail"],
                    "```",
                    "",
                ]
            )

        lines.extend(
            [
                "**Decisión humana:** pendiente.",
                "",
                "Acciones admisibles: " + ", ".join(f"`{action}`" for action in case["allowed_human_actions"]) + ".",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--pages-dir", type=Path, default=DEFAULT_PAGES_DIR)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--context-lines", type=int, default=12)
    args = parser.parse_args()
    if args.context_lines < 1:
        raise SystemExit("--context-lines must be positive")

    batch = build_batch(load_candidates(args.candidates), args.pages_dir, args.context_lines)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(batch), encoding="utf-8")
    print(f"wrote {batch['case_count']} inferred-alignment review cases")


if __name__ == "__main__":
    main()
