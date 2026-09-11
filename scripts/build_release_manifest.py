#!/usr/bin/env python3
"""Build a deterministic manifest for CHD release data artifacts.

The manifest covers versioned files under data/, reports/ and schemas/. Downloaded
source binaries under data/source/original/ are deliberately excluded because they
are external witnesses verified through data/source/source_lock.json and are not
versioned release artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_OUTPUT = Path("release/manifest.json")
DEFAULT_SHA256SUMS = Path("release/SHA256SUMS")
ROOTS = (Path("data"), Path("reports"), Path("schemas"))
EXCLUDED_PREFIXES = (Path("data/source/original"),)
TARGET_VERSION = "0.1.0"
MANIFEST_SCHEMA_VERSION = 1


def is_excluded(path: Path) -> bool:
    return any(path == prefix or prefix in path.parents for prefix in EXCLUDED_PREFIXES)


def artifact_paths(root: Path = Path(".")) -> list[Path]:
    paths: list[Path] = []
    for rel_root in ROOTS:
        base = root / rel_root
        if not base.exists():
            raise FileNotFoundError(f"release root does not exist: {rel_root.as_posix()}")
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(root)
                if not is_excluded(rel):
                    paths.append(rel)
    return sorted(paths, key=lambda p: p.as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path = Path(".")) -> dict[str, object]:
    files = []
    total_bytes = 0
    for rel in artifact_paths(root):
        full = root / rel
        size = full.stat().st_size
        total_bytes += size
        files.append(
            {
                "path": rel.as_posix(),
                "bytes": size,
                "sha256": sha256(full),
            }
        )

    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "project": "Cora Histórico Digital",
        "target_version": TARGET_VERSION,
        "release_status": "candidate",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "artifact_roots": [p.as_posix() for p in ROOTS],
        "excluded_prefixes": [p.as_posix() for p in EXCLUDED_PREFIXES],
        "artifact_count": len(files),
        "total_bytes": total_bytes,
        "hash_algorithm": "sha256",
        "files": files,
    }


def write_outputs(
    manifest: dict[str, object],
    output: Path,
    sha256sums: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    sha256sums.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [f"{row['sha256']}  {row['path']}" for row in manifest["files"]]
    sha256sums.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_manifest(root: Path, manifest: dict[str, object]) -> None:
    expected_paths = [path.as_posix() for path in artifact_paths(root)]
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise ValueError("manifest files must be a list")
    actual_paths = [row["path"] for row in rows]
    if actual_paths != expected_paths:
        raise ValueError("manifest path inventory does not match release roots")
    if manifest.get("artifact_count") != len(rows):
        raise ValueError("manifest artifact_count mismatch")
    if manifest.get("total_bytes") != sum(int(row["bytes"]) for row in rows):
        raise ValueError("manifest total_bytes mismatch")
    for row in rows:
        rel = Path(row["path"])
        full = root / rel
        if full.stat().st_size != int(row["bytes"]):
            raise ValueError(f"size mismatch: {rel.as_posix()}")
        if sha256(full) != row["sha256"]:
            raise ValueError(f"checksum mismatch: {rel.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sha256sums", type=Path, default=DEFAULT_SHA256SUMS)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        manifest = json.loads(args.output.read_text(encoding="utf-8"))
        verify_manifest(args.root, manifest)
        print(f"release manifest verified: {manifest['artifact_count']} artifacts")
        return

    manifest = build_manifest(args.root)
    write_outputs(manifest, args.output, args.sha256sums)
    verify_manifest(args.root, manifest)
    print(
        f"release candidate manifest: {manifest['artifact_count']} artifacts; "
        f"{manifest['total_bytes']} bytes; target={TARGET_VERSION}"
    )


if __name__ == "__main__":
    main()
