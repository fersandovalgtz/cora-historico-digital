#!/usr/bin/env python3
"""Build exhaustive machine review inventories for the two lexical appendices.

The inventories preserve every non-empty OCR paragraph as a review unit. They do
not claim lexicographic boundaries, corrected readings, translations, or human
verification. Stable unit IDs are local to each appendix and do not alter the
ORT1888-cand namespace used by the alphabetical vocabulary body.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_NUMERALS = Path("data/appendices/numerals_ocr.txt")
DEFAULT_IRREGULAR = Path("data/appendices/irregular_verbs_particles_ocr.txt")
DEFAULT_OUTPUT = Path("data/appendices/review_inventory.json")
DEFAULT_REPORT = Path("reports/appendix_review_inventory.json")

DASH_RE = re.compile(r"(?:—|--+|\^—|r—|\.\s*—)")
PAGE_OR_NOISE_RE = re.compile(r"^(?:\d{1,3}|[■mI]+|wm)$", re.IGNORECASE)


def split_paragraphs(text: str) -> list[str]:
    """Return non-empty OCR paragraphs without normalizing their internal text."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return [block.strip() for block in re.split(r"\n\s*\n+", normalized) if block.strip()]


def classify_unit(text: str) -> tuple[str, list[str]]:
    """Assign a descriptive machine class; never an editorial action."""
    compact = " ".join(text.split())
    observations: list[str] = []

    if PAGE_OR_NOISE_RE.fullmatch(compact):
        return "page_marker_or_ocr_noise", ["machine_noise_like"]

    if DASH_RE.search(compact):
        observations.append("contains_equivalence_separator_like_mark")
        if compact.count("—") + compact.count("--") >= 2:
            observations.append("contains_multiple_separator_like_marks")
        return "entry_or_example_like", observations

    lowered = compact.casefold()
    instruction_starts = (
        "cuenta para ", "y así ", "así ", "cuando ", "para decir ",
        "por último ", "el verbo ", "preguntando ", "dice uno", "llamo yo",
    )
    if lowered.startswith(instruction_starts):
        return "narrative_or_grammatical_instruction", ["prose_instruction_like"]

    if " es partícula" in lowered or " partícula " in lowered:
        return "particle_description_like", ["mentions_particle"]

    return "unclassified_text_unit", ["requires_human_structural_review"]


def build_units(text: str, prefix: str, appendix_id: str) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    paragraphs = split_paragraphs(text)
    for index, paragraph in enumerate(paragraphs, start=1):
        machine_class, observations = classify_unit(paragraph)
        units.append(
            {
                "unit_id": f"ORT1888-{prefix}-{index:03d}",
                "appendix_id": appendix_id,
                "order": index,
                "raw_text_ocr": paragraph,
                "machine_classification": machine_class,
                "machine_observations": observations,
                "review_status": "pending_human_structural_review",
                "human_verified": False,
            }
        )
    return units


def build_inventory(numerals_text: str, irregular_text: str) -> dict[str, Any]:
    numeral_units = build_units(numerals_text, "numunit", "numerals_appendix")
    irregular_units = build_units(irregular_text, "irrunit", "irregular_verbs_particles_appendix")
    all_units = numeral_units + irregular_units
    return {
        "artifact_type": "appendix_machine_review_inventory",
        "source_witness_id": "ORTEGA1888-TEPIC-IA",
        "machine_generated": True,
        "human_verified": False,
        "unit_semantics": (
            "OCR paragraph review units only; unit boundaries are navigation aids, not canonical "
            "lexicographic or grammatical boundaries."
        ),
        "id_policy": (
            "ORT1888-numunit-### and ORT1888-irrunit-### are appendix-local machine review IDs; "
            "they do not modify or extend ORT1888-cand-######."
        ),
        "appendices": [
            {
                "appendix_id": "numerals_appendix",
                "source_path": "data/appendices/numerals_ocr.txt",
                "unit_count": len(numeral_units),
                "units": numeral_units,
            },
            {
                "appendix_id": "irregular_verbs_particles_appendix",
                "source_path": "data/appendices/irregular_verbs_particles_ocr.txt",
                "unit_count": len(irregular_units),
                "units": irregular_units,
            },
        ],
        "total_unit_count": len(all_units),
        "all_units_pending_human_review": all(
            unit["review_status"] == "pending_human_structural_review" and not unit["human_verified"]
            for unit in all_units
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numerals", type=Path, default=DEFAULT_NUMERALS)
    parser.add_argument("--irregular", type=Path, default=DEFAULT_IRREGULAR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    inventory = build_inventory(
        args.numerals.read_text(encoding="utf-8"),
        args.irregular.read_text(encoding="utf-8"),
    )
    payload = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    for path in (args.output, args.report):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(
        "wrote appendix review inventory: "
        f"{inventory['total_unit_count']} OCR paragraph units; human_verified=false"
    )


if __name__ == "__main__":
    main()
