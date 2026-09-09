#!/usr/bin/env python3
"""Render facsimile evidence for candidates that still have inferred page alignment.

The output is an evidence packet, not a reconciliation decision. It renders the
original PDF pages surrounding each unresolved candidate plus targeted page-edge
crops for faster visual inspection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import fitz

DEFAULT_CANDIDATES = Path("data/lexicon/candidates.csv")
DEFAULT_PDF = Path("data/source/original/ortega_cora_1888_ia.pdf")
DEFAULT_OUTPUT_DIR = Path("artifacts/phase2_facsimile_review")


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def nearest_direct(rows: list[dict[str, str]], index: int, step: int) -> dict[str, str] | None:
    cursor = index + step
    while 0 <= cursor < len(rows):
        if rows[cursor].get("page_alignment_status") == "matched_headword":
            return rows[cursor]
        cursor += step
    return None


def compact_candidate(row: dict[str, str] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "candidate_id": row.get("candidate_id", ""),
        "order": as_int(row.get("order")),
        "source_pdf_page": as_int(row.get("source_pdf_page")),
        "source_printed_page": as_int(row.get("source_printed_page")),
        "headword_es_ocr": row.get("headword_es_ocr", ""),
        "raw_span_ocr": row.get("raw_span_ocr", ""),
        "page_alignment_status": row.get("page_alignment_status", ""),
    }


def render_png(page: fitz.Page, path: Path, dpi: int, clip: fitz.Rect | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = page.get_pixmap(dpi=dpi, alpha=False, clip=clip)
    pixmap.save(path)


def render_packet(
    rows: list[dict[str, str]],
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 160,
    crop_fraction: float = 0.35,
) -> dict[str, Any]:
    if dpi < 72:
        raise ValueError("dpi must be at least 72")
    if not 0.1 <= crop_fraction <= 0.5:
        raise ValueError("crop_fraction must be between 0.1 and 0.5")
    if not pdf_path.is_file():
        raise FileNotFoundError(f"missing source PDF: {pdf_path}")

    ordered = sorted(rows, key=lambda row: as_int(row.get("order"), 10**9))
    unresolved: list[tuple[int, dict[str, str], dict[str, str] | None, dict[str, str] | None]] = []
    for index, target in enumerate(ordered):
        if target.get("page_alignment_status") == "inferred_sequence":
            unresolved.append(
                (
                    index,
                    target,
                    nearest_direct(ordered, index, -1),
                    nearest_direct(ordered, index, 1),
                )
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    cases_dir = output_dir / "cases"
    document = fitz.open(pdf_path)

    page_numbers: set[int] = set()
    for _, target, previous_anchor, next_anchor in unresolved:
        for row in (target, previous_anchor, next_anchor):
            if row:
                page = as_int(row.get("source_pdf_page"))
                if page:
                    page_numbers.add(page)

    rendered_full_pages: dict[int, str] = {}
    for page_number in sorted(page_numbers):
        if page_number < 1 or page_number > document.page_count:
            raise ValueError(
                f"candidate references PDF page {page_number}, but document has {document.page_count} pages"
            )
        relative = Path("pages") / f"page-{page_number:03d}-full.png"
        render_png(document.load_page(page_number - 1), output_dir / relative, dpi)
        rendered_full_pages[page_number] = relative.as_posix()

    cases: list[dict[str, Any]] = []
    for _, target, previous_anchor, next_anchor in unresolved:
        candidate_id = target.get("candidate_id", "")
        case_assets: list[dict[str, Any]] = []
        previous_page = as_int(previous_anchor.get("source_pdf_page")) if previous_anchor else 0
        next_page = as_int(next_anchor.get("source_pdf_page")) if next_anchor else 0

        for role, page_number in (("previous_tail", previous_page), ("next_head", next_page)):
            if not page_number:
                continue
            page = document.load_page(page_number - 1)
            rect = page.rect
            if role == "previous_tail":
                clip = fitz.Rect(rect.x0, rect.y1 * (1 - crop_fraction), rect.x1, rect.y1)
            else:
                clip = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1 * crop_fraction)
            relative = Path("cases") / candidate_id / f"page-{page_number:03d}-{role}.png"
            render_png(page, output_dir / relative, dpi, clip=clip)
            case_assets.append(
                {
                    "role": role,
                    "source_pdf_page": page_number,
                    "source_printed_page": page_number - 4,
                    "path": relative.as_posix(),
                }
            )

        involved_pages = sorted(
            {
                page
                for page in (
                    as_int(target.get("source_pdf_page")),
                    previous_page,
                    next_page,
                )
                if page
            }
        )
        cases.append(
            {
                "candidate_id": candidate_id,
                "review_status": "pending_human_reconciliation",
                "human_verified": False,
                "facsimile_required": True,
                "target": compact_candidate(target),
                "previous_direct_anchor": compact_candidate(previous_anchor),
                "next_direct_anchor": compact_candidate(next_anchor),
                "full_page_assets": [rendered_full_pages[page] for page in involved_pages],
                "boundary_crop_assets": case_assets,
            }
        )

    document.close()
    manifest = {
        "artifact_type": "facsimile_review_packet",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "source_pdf_sha256": sha256_file(pdf_path),
        "human_verified": False,
        "facsimile_required": True,
        "render_dpi": dpi,
        "crop_fraction": crop_fraction,
        "case_count": len(cases),
        "rendered_pdf_pages": sorted(page_numbers),
        "cases": cases,
        "method_note": (
            "Rendered page images are visual evidence from the locked source PDF. "
            "They do not constitute a reconciliation decision or human verification."
        ),
    }
    (output_dir / "facsimile_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--crop-fraction", type=float, default=0.35)
    args = parser.parse_args()

    manifest = render_packet(
        load_candidates(args.candidates),
        args.pdf,
        args.output_dir,
        dpi=args.dpi,
        crop_fraction=args.crop_fraction,
    )
    print(
        f"rendered {manifest['case_count']} facsimile review cases across "
        f"{len(manifest['rendered_pdf_pages'])} PDF pages"
    )


if __name__ == "__main__":
    main()
