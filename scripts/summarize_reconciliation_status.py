#!/usr/bin/env python3
"""Summarize human reconciliation coverage for phase 2."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from validate_reconciliation_decisions import (
    DECISIONS,
    CANDIDATES,
    iter_records,
    load_candidates,
    validate_collection,
)

DEFAULT_OUTPUT = Path("reports/reconciliation_status.json")


def summarize_status(
    candidates: dict[str, dict[str, str]],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    covered: dict[str, dict[str, Any]] = {}
    action_decisions = Counter()
    action_candidates = Counter()

    for decision in decisions:
        action = str(decision["action"])
        action_decisions[action] += 1
        for candidate_id in decision["candidate_ids"]:
            covered[candidate_id] = decision
            action_candidates[action] += 1

    alignment: dict[str, dict[str, int]] = {}
    alignment_names = sorted(
        {row.get("page_alignment_status", "unknown") or "unknown" for row in candidates.values()}
    )
    for status in alignment_names:
        ids = [
            candidate_id
            for candidate_id, row in candidates.items()
            if (row.get("page_alignment_status", "unknown") or "unknown") == status
        ]
        reconciled = sum(candidate_id in covered for candidate_id in ids)
        alignment[status] = {
            "total": len(ids),
            "reconciled": reconciled,
            "pending": len(ids) - reconciled,
        }

    total = len(candidates)
    covered_count = len(covered)
    pending = total - covered_count
    deferred = action_candidates.get("defer_uncertain", 0)
    coverage_complete = pending == 0
    ready = coverage_complete and deferred == 0
    pending_inferred = [
        candidate_id
        for candidate_id, row in candidates.items()
        if row.get("page_alignment_status") == "inferred_sequence" and candidate_id not in covered
    ]

    return {
        "artifact_type": "human_reconciliation_status",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "candidate_total": total,
        "human_decision_records": len(decisions),
        "candidate_reconciled": covered_count,
        "candidate_pending": pending,
        "candidate_coverage_percent": round((covered_count / total * 100) if total else 100.0, 4),
        "decision_coverage_complete": coverage_complete,
        "deferred_uncertain_candidates": deferred,
        "ready_for_canonicalization": ready,
        "decision_counts_by_action": dict(sorted(action_decisions.items())),
        "candidate_counts_by_action": dict(sorted(action_candidates.items())),
        "coverage_by_page_alignment_status": alignment,
        "pending_inferred_alignment_candidates": pending_inferred,
        "method_note": (
            "Decision coverage is complete only when every machine candidate belongs to exactly one "
            "validated human decision. Canonicalization readiness additionally requires no "
            "defer_uncertain candidates. Merge/split decisions still require downstream article "
            "materialization and do not themselves assign ORT1888-art identifiers."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=CANDIDATES)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    candidates = load_candidates(args.candidates)
    decisions = validate_collection(iter_records(args.decisions_dir), candidates)
    status = summarize_status(candidates, decisions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"reconciliation coverage: {status['candidate_reconciled']}/"
        f"{status['candidate_total']} candidates; "
        f"ready_for_canonicalization={str(status['ready_for_canonicalization']).lower()}"
    )


if __name__ == "__main__":
    main()
