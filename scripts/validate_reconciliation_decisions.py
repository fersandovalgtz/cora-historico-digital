#!/usr/bin/env python3
"""Validate phase-2 human reconciliation decisions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path

CANDIDATES = Path("data/lexicon/candidates.csv")
DECISIONS = Path("data/reconciliation/decisions")
DECISION_RE = re.compile(r"^ORT1888-rec-[0-9]{6}$")
CANDIDATE_RE = re.compile(r"^ORT1888-cand-[0-9]{6}$")
WITNESS = "ORTEGA1888-TEPIC-IA"
ACTIONS = {
    "accept_boundary",
    "merge_candidates",
    "split_candidate",
    "reject_false_boundary",
    "defer_uncertain",
}
REQUIRED = {
    "decision_id", "source_witness_id", "candidate_ids", "action",
    "source_pdf_pages", "reviewer", "reviewed_at", "rationale",
    "human_verified",
}
ALLOWED = REQUIRED | {"source_printed_pages", "proposed_spans", "evidence_note"}


def error(message: str) -> None:
    raise ValueError(message)


def load_candidates(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        cid = row.get("candidate_id", "")
        if not CANDIDATE_RE.fullmatch(cid):
            error(f"invalid candidate_id in {path}: {cid!r}")
        if cid in result:
            error(f"duplicate candidate_id in {path}: {cid}")
        result[cid] = row
    return result


def validate_pages(value: object, field: str, allow_empty: bool = False) -> list[int]:
    if not isinstance(value, list) or (not value and not allow_empty):
        error(f"{field} must be a {'possibly empty' if allow_empty else 'non-empty'} list")
    if any(type(item) is not int or item < 1 for item in value):
        error(f"{field} must contain positive integers")
    if len(set(value)) != len(value):
        error(f"{field} must not contain duplicates")
    return value


def validate_datetime(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        error("reviewed_at must be a non-empty ISO 8601 string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        error(f"reviewed_at is invalid: {value!r}")
    if parsed.tzinfo is None:
        error("reviewed_at must include a UTC offset or Z")


def validate_record(record: dict, candidates: dict[str, dict[str, str]]) -> str:
    missing = REQUIRED - set(record)
    extra = set(record) - ALLOWED
    if missing:
        error(f"missing keys: {', '.join(sorted(missing))}")
    if extra:
        error(f"unexpected keys: {', '.join(sorted(extra))}")

    did = record["decision_id"]
    if not isinstance(did, str) or not DECISION_RE.fullmatch(did):
        error(f"invalid decision_id: {did!r}")
    if record["source_witness_id"] != WITNESS:
        error(f"source_witness_id must be {WITNESS}")

    ids = record["candidate_ids"]
    if not isinstance(ids, list) or not ids:
        error("candidate_ids must be a non-empty list")
    if any(not isinstance(cid, str) or not CANDIDATE_RE.fullmatch(cid) for cid in ids):
        error("candidate_ids contains an invalid identifier")
    if len(set(ids)) != len(ids):
        error("candidate_ids must not contain duplicates")
    unknown = [cid for cid in ids if cid not in candidates]
    if unknown:
        error(f"unknown candidate_ids: {', '.join(unknown)}")

    action = record["action"]
    if action not in ACTIONS:
        error(f"invalid action: {action!r}")
    if action == "merge_candidates" and len(ids) < 2:
        error("merge_candidates requires at least two candidate_ids")
    if action == "split_candidate" and len(ids) != 1:
        error("split_candidate requires exactly one candidate_id")
    if action in {"accept_boundary", "reject_false_boundary", "defer_uncertain"} and len(ids) != 1:
        error(f"{action} requires exactly one candidate_id")

    pages = validate_pages(record["source_pdf_pages"], "source_pdf_pages")
    if "source_printed_pages" in record:
        validate_pages(record["source_printed_pages"], "source_printed_pages", allow_empty=True)
    candidate_pages = {
        int(candidates[cid]["source_pdf_page"])
        for cid in ids if candidates[cid].get("source_pdf_page", "").isdigit()
    }
    missing_pages = candidate_pages - set(pages)
    if missing_pages:
        error(f"source_pdf_pages omits candidate pages: {sorted(missing_pages)}")

    spans = record.get("proposed_spans")
    if spans is not None:
        if not isinstance(spans, list):
            error("proposed_spans must be a list")
        for pos, span in enumerate(spans, 1):
            if not isinstance(span, dict) or set(span) != {"source_ocr_line_start", "source_ocr_line_end"}:
                error(f"proposed_spans[{pos}] has invalid keys")
            start, end = span["source_ocr_line_start"], span["source_ocr_line_end"]
            if type(start) is not int or type(end) is not int or start < 1 or end < start:
                error(f"proposed_spans[{pos}] has invalid line bounds")
    if action == "split_candidate" and (not spans or len(spans) < 2):
        error("split_candidate requires at least two proposed_spans")

    for field in ("reviewer", "rationale"):
        if not isinstance(record[field], str) or not record[field].strip():
            error(f"{field} must be a non-empty string")
    if "evidence_note" in record and not isinstance(record["evidence_note"], str):
        error("evidence_note must be a string")
    validate_datetime(record["reviewed_at"])
    if record["human_verified"] is not True:
        error("human_verified must be the JSON boolean true")
    return did


def iter_records(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            error(f"{path} must contain one JSON object")
        yield str(path), payload
    for path in sorted(directory.glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                error(f"{path}:{line_number} must contain one JSON object")
            yield f"{path}:{line_number}", payload


def validate_collection(records, candidates: dict[str, dict[str, str]]) -> list[dict]:
    """Validate a decision set and prohibit contradictory candidate ownership."""
    seen_decisions: dict[str, str] = {}
    claimed_candidates: dict[str, tuple[str, str]] = {}
    validated: list[dict] = []

    for location, record in records:
        did = validate_record(record, candidates)
        if did in seen_decisions:
            error(
                f"duplicate reconciliation decision_id {did}: "
                f"{seen_decisions[did]} and {location}"
            )
        seen_decisions[did] = location

        for candidate_id in record["candidate_ids"]:
            if candidate_id in claimed_candidates:
                previous_did, previous_location = claimed_candidates[candidate_id]
                error(
                    f"candidate {candidate_id} is reconciled more than once: "
                    f"{previous_did} at {previous_location} and {did} at {location}"
                )
            claimed_candidates[candidate_id] = (did, location)
        validated.append(record)

    return validated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=CANDIDATES)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS)
    args = parser.parse_args()

    try:
        candidates = load_candidates(args.candidates)
        decisions = validate_collection(iter_records(args.decisions_dir), candidates)
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid reconciliation decision set: {exc}") from exc

    covered = sum(len(record["candidate_ids"]) for record in decisions)
    print(
        f"validated {len(decisions)} reconciliation decisions covering {covered} "
        f"of {len(candidates)} machine candidates"
    )


if __name__ == "__main__":
    main()
