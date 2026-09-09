#!/usr/bin/env python3
"""Checksum locking for reproducible historical-source ingestion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_locked_sources(source_paths: Mapping[str, Path], lock_path: Path) -> dict[str, str]:
    """Verify every declared source against the repository checksum lock.

    Returns the observed hashes when all values match. Any missing source key,
    unexpected key, or checksum drift aborts ingestion before derived data are
    rewritten.
    """
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = payload.get("expected_sha256")
    if not isinstance(expected, dict) or not expected:
        raise ValueError(f"invalid source lock: {lock_path}")

    expected_keys = set(expected)
    actual_keys = set(source_paths)
    if expected_keys != actual_keys:
        missing = sorted(expected_keys - actual_keys)
        unexpected = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(f"missing source keys: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected source keys: {', '.join(unexpected)}")
        raise ValueError("; ".join(details))

    observed: dict[str, str] = {}
    mismatches: list[str] = []
    for key in sorted(expected):
        path = source_paths[key]
        if not path.is_file():
            raise ValueError(f"source file does not exist for {key}: {path}")
        observed[key] = sha256_file(path)
        if observed[key] != expected[key]:
            mismatches.append(
                f"{key}: expected {expected[key]}, observed {observed[key]}"
            )

    if mismatches:
        raise ValueError(
            "source checksum drift detected; review the upstream witness before "
            "updating data/source/source_lock.json: " + "; ".join(mismatches)
        )
    return observed
