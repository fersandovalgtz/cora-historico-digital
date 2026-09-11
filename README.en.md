# Cora Histórico Digital

Cora Histórico Digital (CHD) is a reproducible **machine-only historical corpus** built around José de Ortega's Cora vocabulary through the 1888 Tepic reprint of the 1732 work.

The repository preserves the source witness, OCR, provenance and uncertainty as separate layers. It contains no human-review stage and does not claim human philological or linguistic validation.

Current baseline: 5,388 OCR lines; 2,140 machine candidates in the alphabetical vocabulary body; 2,131 direct page matches; 6 conservative same-page anchors; and 3 `inferred_sequence` candidates. Machine resolution yields **2,137 `machine_accepted` articles, 2 `machine_rejected` segmentation artifacts, and 1 `machine_uncertain` candidate**.

The numeral appendix has a separate machine-only representation of **27 explicit Spanish–Cora pairs**. The irregular-verbs/particles appendix has **22 paragraph-scale documentary records** linked one-to-one to the navigation inventory: 4 imperative examples, 5 expression examples, 3 particle descriptions, 3 explanatory-prose units, 2 form clusters, 1 irregular-verb description and 4 OCR-noise units. These are reproducible documentary classes, not normalized linguistic analyses.

The alphabetical layer now has two validated, reproducible interoperability views. **TEI Lex-0 0.9.5** contains 2,137 accepted entries while retaining the 3 residual candidates as non-promoted evidence and validates against the pinned official Relax NG schema. **CLDF Dictionary** contains 2,137 `EntryTable` rows and 2,137 one-to-one `SenseTable` rows preserving the complete Cora OCR strings, while the 3 non-accepted candidates remain in a separate documentary CSVW table. Neither view replaces the canonical CHD machine records.

```bash
make ingest
make validate
make source-coverage
make appendix-machine-inventory
make numeral-machine-lexicon
make irregular-particles-machine
make machine-corpus
make tei-lex0
make cldf-dictionary
```

Source binaries are downloaded from Internet Archive and checked against pinned SHA-256 values before derived data are rebuilt. The TEI schema is likewise checksum-pinned, and the generated TEI and CLDF datasets must pass their formal validators before bootstrap can commit derived artifacts.

The next scientific phase is the **citable scientific release**: freeze the `0.1.0` contracts, run release QA, create an artifact manifest and checksums, add stable citation metadata, and prepare an archived DOI-bearing release. Additional interoperability formats should only be added when they provide a concrete scientific benefit without distorting the heterogeneous historical source models.

CHD is not a normative dictionary of contemporary Náayeri and should not be described as a human critical edition. In the CLDF view, one SenseTable row per article is a documentary representation of the complete OCR equivalent, not a claim that every historical article has exactly one linguistic sense. Code is MIT; original project metadata and derived annotations are CC BY 4.0 unless otherwise stated.
