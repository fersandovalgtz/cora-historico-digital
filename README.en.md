# Cora Histórico Digital

Cora Histórico Digital (CHD) is a reproducible **machine-only historical corpus** built around José de Ortega's Cora vocabulary through the 1888 Tepic reprint of the 1732 work.

The repository preserves the source witness, OCR, provenance and uncertainty as separate layers. It contains no human-review stage and does not claim human philological or linguistic validation.

Current baseline: 5,388 OCR lines; 2,140 machine candidates in the alphabetical vocabulary body; 2,131 direct page matches; 6 conservative same-page anchors; and 3 `inferred_sequence` candidates. Machine resolution currently yields **2,137 `machine_accepted` articles, 2 `machine_rejected` segmentation artifacts, and 1 `machine_uncertain` candidate**.

The two rejected candidates match a narrow structural rule for page-top OCR noise: a low-confidence `hyphen_variant` candidate is bracketed by direct matches on consecutive pages and its own OCR span contains the next printed folio number as a standalone segment. Rejected source candidates are retained rather than deleted. The remaining ambiguous candidate is kept explicitly uncertain.

```bash
make ingest
make validate
make source-coverage
make appendix-machine-inventory
make machine-corpus
```

Source binaries are downloaded from Internet Archive and checked against pinned SHA-256 values before derived data are rebuilt. Numerals and the irregular-verbs/particles appendix are retained in full and receive separate machine navigation inventories rather than being forced into the alphabetical candidate model.

CHD is not a normative dictionary of contemporary Náayeri and should not be described as a human critical edition. Code is MIT; original project metadata and derived annotations are CC BY 4.0 unless otherwise stated.
