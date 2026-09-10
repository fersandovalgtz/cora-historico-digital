from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_source_coverage import (
    build_coverage_report,
    locate_partition_ranges,
    render_partition,
    verify_candidate_scope,
)


LINES = [
    "Preliminary title",
    "Preliminary note",
    "A., denotando la persona que padece. — Cora A.",
    "Abajar. — Cora B.",
    "Zumbar la abeja. — Cora Z.",
    "Cuenta para contar todo lo numerable. Una. — Cora one.",
    "Dos. — Cora two.",
    "Por último pondrá aqui algunos verbos irregulares, y algunas partículas.",
    "Arieú. — Example.",
]


def candidate(order: int, start: int, end: int) -> dict[str, str]:
    return {
        "candidate_id": f"ORT1888-cand-{order:06d}",
        "order": str(order),
        "source_ocr_line_start": str(start),
        "source_ocr_line_end": str(end),
    }


class SourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.full = self.root / "full.txt"
        self.full.write_text("\n".join(LINES) + "\n", encoding="utf-8")
        self.ranges = locate_partition_ranges(LINES)
        self.paths = {
            "preliminary_matter": self.root / "preliminary.txt",
            "alphabetical_lexicon_body": self.root / "body.txt",
            "numerals_appendix": self.root / "numerals.txt",
            "irregular_verbs_particles_appendix": self.root / "irregular.txt",
        }
        for partition_id, (start, end) in self.ranges.items():
            self.paths[partition_id].write_text(
                render_partition(LINES, start, end), encoding="utf-8"
            )
        self.candidates = self.root / "candidates.csv"
        with self.candidates.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "candidate_id",
                    "order",
                    "source_ocr_line_start",
                    "source_ocr_line_end",
                ],
            )
            writer.writeheader()
            writer.writerows([candidate(1, 3, 3), candidate(2, 4, 5)])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_ranges_cover_complete_source_without_gaps(self):
        self.assertEqual(
            self.ranges,
            {
                "preliminary_matter": (0, 2),
                "alphabetical_lexicon_body": (2, 5),
                "numerals_appendix": (5, 7),
                "irregular_verbs_particles_appendix": (7, 9),
            },
        )
        ordered = [self.ranges[key] for key in [
            "preliminary_matter",
            "alphabetical_lexicon_body",
            "numerals_appendix",
            "irregular_verbs_particles_appendix",
        ]]
        self.assertEqual(ordered[0][0], 0)
        self.assertEqual(ordered[-1][1], len(LINES))
        self.assertTrue(all(left[1] == right[0] for left, right in zip(ordered, ordered[1:])))

    def test_report_distinguishes_alphabetical_inventory_from_appendices(self):
        report = build_coverage_report(
            self.full,
            self.candidates,
            partition_paths=self.paths,
        )
        self.assertTrue(report["coverage"]["contiguous"])
        self.assertEqual(report["candidate_scope"]["candidate_total"], 2)
        self.assertTrue(report["candidate_scope"]["all_candidates_within_alphabetical_body"])
        self.assertTrue(report["lexical_scope"]["alphabetical_body_structured_as_machine_candidates"])
        self.assertFalse(report["lexical_scope"]["numerals_appendix_structured"])
        self.assertFalse(report["lexical_scope"]["irregular_verbs_particles_appendix_structured"])
        self.assertFalse(report["lexical_scope"]["witness_lexical_content_fully_structured"])
        self.assertFalse(report["human_verified"])
        self.assertEqual(
            [item["line_total"] for item in report["partitions"]], [2, 3, 2, 2]
        )

    def test_partition_file_drift_fails_closed(self):
        self.paths["numerals_appendix"].write_text("corrupted\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "derived partition drift"):
            build_coverage_report(
                self.full,
                self.candidates,
                partition_paths=self.paths,
            )

    def test_missing_boundary_marker_fails_closed(self):
        lines = [line for line in LINES if "Cuenta para contar" not in line]
        with self.assertRaisesRegex(ValueError, "boundary marker not found"):
            locate_partition_ranges(lines)

    def test_candidate_outside_alphabetical_body_fails_closed(self):
        rows = [candidate(1, 6, 6)]
        with self.assertRaisesRegex(ValueError, "escapes alphabetical body"):
            verify_candidate_scope(rows, self.ranges["alphabetical_lexicon_body"])

    def test_candidate_order_must_be_complete_sequence(self):
        rows = [candidate(1, 3, 3), candidate(3, 4, 4)]
        with self.assertRaisesRegex(ValueError, "complete 1..N sequence"):
            verify_candidate_scope(rows, self.ranges["alphabetical_lexicon_body"])

    def test_inverted_candidate_span_fails_closed(self):
        rows = [candidate(1, 5, 4)]
        with self.assertRaisesRegex(ValueError, "inverted OCR line bounds"):
            verify_candidate_scope(rows, self.ranges["alphabetical_lexicon_body"])


if __name__ == "__main__":
    unittest.main()
