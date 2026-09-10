#!/usr/bin/env python3
"""Build a deterministic phase-3 canonicalization plan from human decisions.

The plan is a machine-generated materialization schedule, not a philological
review. It assigns future ORT1888-art identifiers only after every machine
candidate belongs to exactly one validated human decision and no decision is
``defer_uncertain``. It does not yet rewrite lexical text.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from summarize_reconciliation_status import summarize_status
from validate_reconciliation_decisions import (
    CANDIDATES,
    DECISIONS,
    iter_records,
    load_candidates,
    validate_collection,
)

DEFAULT_OUTPUT = Path("data/canonical/canonicalization_plan.json")
ARTICLE_PREFIX = "ORT1888-art-"


def _candidate_order(candidates: dict[str, dict[str, str]], candidate_id: str) -> int:
    try:
        order = int(candidates[candidate_id]["order"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"candidate {candidate_id} has invalid order") from exc
    if order < 1:
        raise ValueError(f"candidate {candidate_id} has invalid order {order}")
    return order


def _validate_unique_orders(candidates: dict[str, dict[str, str]]) -> None:
    owners: dict[int, str] = {}
    for candidate_id in candidates:
        order = _candidate_order(candidates, candidate_id)
        if order in owners:
            raise ValueError(
                f"candidate order {order} is duplicated by {owners[order]} and {candidate_id}"
            )
        owners[order] = candidate_id


def _validate_complete_coverage(
    candidates: dict[str, dict[str, str]], decisions: list[dict[str, Any]]
) -> None:
    claimed: list[str] = [
        candidate_id
        for decision in decisions
        for candidate_id in decision["candidate_ids"]
    ]
    counts = Counter(claimed)
    duplicates = sorted(candidate_id for candidate_id, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(
            "canonicalization blocked: candidates occur in multiple decisions: "
            + ", ".join(duplicates)
        )

    unknown = sorted(set(claimed) - set(candidates))
    if unknown:
        raise ValueError(
            "canonicalization blocked: decisions contain unknown candidates: "
            + ", ".join(unknown)
        )

    missing = sorted(set(candidates) - set(claimed), key=lambda cid: _candidate_order(candidates, cid))
    deferred = sorted(
        candidate_id
        for decision in decisions
        if decision["action"] == "defer_uncertain"
        for candidate_id in decision["candidate_ids"]
    )
    if missing or deferred:
        details = []
        if missing:
            details.append(f"{len(missing)} candidates lack human decisions")
        if deferred:
            details.append(f"{len(deferred)} candidates are defer_uncertain")
        raise ValueError("canonicalization blocked: " + "; ".join(details))


def _validate_merge_contiguity(
    candidates: dict[str, dict[str, str]], decision: dict[str, Any]
) -> list[str]:
    ordered_ids = sorted(
        decision["candidate_ids"], key=lambda cid: _candidate_order(candidates, cid)
    )
    orders = [_candidate_order(candidates, cid) for cid in ordered_ids]
    expected = list(range(orders[0], orders[0] + len(orders)))
    if orders != expected:
        raise ValueError(
            f"{decision['decision_id']} merge_candidates must reference contiguous candidate orders; "
            f"got {orders}"
        )
    return ordered_ids


def _validated_split_spans(
    candidates: dict[str, dict[str, str]], decision: dict[str, Any]
) -> list[dict[str, int]]:
    candidate_id = decision["candidate_ids"][0]
    row = candidates[candidate_id]
    try:
        candidate_start = int(row["source_ocr_line_start"])
        candidate_end = int(row["source_ocr_line_end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"candidate {candidate_id} has invalid OCR line bounds") from exc

    spans = sorted(
        decision.get("proposed_spans") or [],
        key=lambda span: (span["source_ocr_line_start"], span["source_ocr_line_end"]),
    )
    if len(spans) < 2:
        raise ValueError(f"{decision['decision_id']} split_candidate requires at least two spans")

    previous_end = None
    for span in spans:
        start = span["source_ocr_line_start"]
        end = span["source_ocr_line_end"]
        if start < candidate_start or end > candidate_end:
            raise ValueError(
                f"{decision['decision_id']} split span {start}-{end} falls outside "
                f"candidate {candidate_id} OCR bounds {candidate_start}-{candidate_end}"
            )
        if previous_end is not None and start <= previous_end:
            raise ValueError(f"{decision['decision_id']} split spans overlap")
        previous_end = end
    return spans


def _unit(
    *,
    decision: dict[str, Any],
    candidate_ids: list[str],
    source_type: str,
    sort_order: int,
    split_index: int | None = None,
    source_ocr_span: dict[str, int] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "article_id": None,
        "decision_id": decision["decision_id"],
        "decision_action": decision["action"],
        "source_type": source_type,
        "source_candidate_ids": candidate_ids,
        "source_pdf_pages": decision["source_pdf_pages"],
        "sort_order": sort_order,
    }
    if split_index is not None:
        item["split_index"] = split_index
    if source_ocr_span is not None:
        item["source_ocr_span"] = source_ocr_span
    return item


def build_plan(
    candidates: dict[str, dict[str, str]],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a deterministic plan; fail closed unless phase 2 is complete."""
    _validate_unique_orders(candidates)
    _validate_complete_coverage(candidates, decisions)

    status = summarize_status(candidates, decisions)
    if not status["ready_for_canonicalization"]:
        raise ValueError(
            "canonicalization blocked: reconciliation status is not ready_for_canonicalization"
        )

    decisions_in_order = sorted(
        decisions,
        key=lambda decision: (
            min(_candidate_order(candidates, cid) for cid in decision["candidate_ids"]),
            decision["decision_id"],
        ),
    )

    units: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for decision in decisions_in_order:
        action = decision["action"]
        candidate_ids = sorted(
            decision["candidate_ids"], key=lambda cid: _candidate_order(candidates, cid)
        )
        first_order = _candidate_order(candidates, candidate_ids[0])

        if action == "accept_boundary":
            units.append(
                _unit(
                    decision=decision,
                    candidate_ids=candidate_ids,
                    source_type="accepted_candidate",
                    sort_order=first_order,
                )
            )
        elif action == "merge_candidates":
            candidate_ids = _validate_merge_contiguity(candidates, decision)
            units.append(
                _unit(
                    decision=decision,
                    candidate_ids=candidate_ids,
                    source_type="merged_candidates",
                    sort_order=first_order,
                )
            )
        elif action == "split_candidate":
            spans = _validated_split_spans(candidates, decision)
            for split_index, span in enumerate(spans, start=1):
                units.append(
                    _unit(
                        decision=decision,
                        candidate_ids=candidate_ids,
                        source_type="candidate_span",
                        sort_order=first_order,
                        split_index=split_index,
                        source_ocr_span=span,
                    )
                )
        elif action == "reject_false_boundary":
            excluded.append(
                {
                    "decision_id": decision["decision_id"],
                    "candidate_id": candidate_ids[0],
                    "candidate_order": first_order,
                    "reason": "human_rejected_false_boundary",
                }
            )
        elif action == "defer_uncertain":
            raise ValueError(
                f"canonicalization blocked: {decision['decision_id']} is defer_uncertain"
            )
        else:
            raise ValueError(f"unsupported reconciliation action: {action}")

    units.sort(
        key=lambda item: (
            item["sort_order"],
            item.get("split_index", 0),
            item["decision_id"],
        )
    )
    for index, item in enumerate(units, start=1):
        item["article_id"] = f"{ARTICLE_PREFIX}{index:06d}"

    action_counts = Counter(decision["action"] for decision in decisions)
    source_type_counts = Counter(item["source_type"] for item in units)

    return {
        "artifact_type": "canonicalization_plan",
        "project_phase": 3,
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "machine_generated": True,
        "derived_from_human_verified_decisions": True,
        "human_decision_coverage_complete": True,
        "ready_for_canonicalization": True,
        "candidate_total": len(candidates),
        "human_decision_records": len(decisions),
        "planned_article_total": len(units),
        "excluded_candidate_total": len(excluded),
        "decision_counts_by_action": dict(sorted(action_counts.items())),
        "article_counts_by_source_type": dict(sorted(source_type_counts.items())),
        "articles": units,
        "excluded_candidates": sorted(excluded, key=lambda item: item["candidate_order"]),
        "method_note": (
            "This machine-generated plan assigns deterministic future article identifiers from "
            "validated human reconciliation decisions. It does not normalize, correct, translate, "
            "or otherwise rewrite lexical content. Article text materialization is a separate step."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=CANDIDATES)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        candidates = load_candidates(args.candidates)
        decisions = validate_collection(iter_records(args.decisions_dir), candidates)
        plan = build_plan(candidates, decisions)
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot build canonicalization plan: {exc}") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"planned {plan['planned_article_total']} canonical articles from "
        f"{plan['human_decision_records']} human decisions; "
        f"excluded {plan['excluded_candidate_total']} false boundaries"
    )


if __name__ == "__main__":
    main()
