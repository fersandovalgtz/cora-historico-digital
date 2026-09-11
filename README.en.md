# Cora Histórico Digital

Cora Histórico Digital (CHD) is a reproducible **machine-only historical corpus** built around José de Ortega's Cora vocabulary through the 1888 Tepic reprint of the 1732 work.

The repository preserves the source witness, OCR, provenance and uncertainty as separate layers. It contains no human-review stage and does not claim human philological or linguistic validation.

Current baseline: 5,388 OCR lines; 2,140 machine candidates in the alphabetical vocabulary body; 2,131 direct page matches; 6 conservative same-page anchors; and 3 `inferred_sequence` candidates. Machine resolution yields **2,137 `machine_accepted` articles, 2 `machine_rejected` segmentation artifacts, and 1 `machine_uncertain` candidate**.

The numeral appendix has a separate machine-only representation of **27 explicit Spanish–Cora pairs**. The irregular-verbs/particles appendix now has **22 paragraph-scale documentary records** linked one-to-one to the navigation inventory: 4 imperative examples, 5 expression examples, 3 particle descriptions, 3 explanatory-prose units, 2 form clusters, 1 irregular-verb description and 4 OCR-noise units. These are reproducible documentary classes, not normalized linguistic analyses.

```bash
make ingest
make validate
make source-coverage
make appendix-machine-inventory
make numeral-machine-lexicon
make irregular-particles-machine
make machine-corpus
```

Source binaries are downloaded from Internet Archive and checked against pinned SHA-256 values before derived data are rebuilt. The alphabetical body, numerals and irregular-verbs/particles appendix retain distinct internal models because their documentary structures differ.

The next scientific phase is interoperability: generate TEI Lex-0 and evaluate CLDF as derived views while preserving IDs, provenance, authority status and source OCR. A citable archived release follows once those contracts are stable.

CHD is not a normative dictionary of contemporary Náayeri and should not be described as a human critical edition. Code is MIT; original project metadata and derived annotations are CC BY 4.0 unless otherwise stated.
