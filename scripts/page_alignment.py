#!/usr/bin/env python3
"""Conservative helpers for machine page alignment."""

from __future__ import annotations

import re


def short_headword_exact_line_match(page_text: str, headword: str) -> bool:
    """Match a 2–3 letter headword only as an explicit em-dash entry line.

    This narrow rule exists because substring matching is unsafe for very short
    strings. Single-letter strings and strings containing OCR symbols are never
    accepted here. The caller must also require an ``em_dash`` extraction.
    """
    headword = headword.strip()
    if not 2 <= len(headword) <= 3 or not headword.isalpha():
        return False
    pattern = re.compile(
        rf"^\s*{re.escape(headword)}\s*[.,;:]?\s*—",
        flags=re.IGNORECASE,
    )
    return any(pattern.search(line) for line in page_text.splitlines())


def anchor_inferred_same_page(rows: list[dict]) -> int:
    """Reclassify only inferred rows bracketed by direct matches on one page.

    The function never changes a page number. A row is changed from
    ``inferred_sequence`` to ``anchored_same_page`` only when its nearest previous
    and next *direct* ``matched_headword`` anchors share the same PDF page and that
    page is already the inferred row's assigned page. Newly anchored rows are not
    reused as anchors.
    """
    previous_direct: list[int | None] = []
    last_direct: int | None = None
    for index, row in enumerate(rows):
        previous_direct.append(last_direct)
        if row.get("page_alignment_status") == "matched_headword":
            last_direct = index

    next_direct: list[int | None] = [None] * len(rows)
    last_direct = None
    for index in range(len(rows) - 1, -1, -1):
        next_direct[index] = last_direct
        if rows[index].get("page_alignment_status") == "matched_headword":
            last_direct = index

    anchored = 0
    for index, row in enumerate(rows):
        if row.get("page_alignment_status") != "inferred_sequence":
            continue
        left_index = previous_direct[index]
        right_index = next_direct[index]
        if left_index is None or right_index is None:
            continue

        assigned_page = str(row.get("source_pdf_page", "")).strip()
        left_page = str(rows[left_index].get("source_pdf_page", "")).strip()
        right_page = str(rows[right_index].get("source_pdf_page", "")).strip()
        if assigned_page and assigned_page == left_page == right_page:
            row["page_alignment_status"] = "anchored_same_page"
            anchored += 1

    return anchored
