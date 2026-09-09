# Cora Histórico Digital

**Cora Histórico Digital (CHD)** is a research infrastructure for transforming historical Cora-language witnesses into traceable, versioned and reproducible digital objects while keeping OCR, computational segmentation, editorial reconstruction and linguistic interpretation distinct.

The initial implementation uses José de Ortega's vocabulary through the **1888 Tepic reprint** of the work first printed in Mexico in **1732**. The working digital witness is the John Carter Brown Library copy disseminated by Internet Archive as `vocabulariodelas00orte`.

> **Scientific status: `0.1.0-dev`.** The current dataset is a machine-generated candidate inventory. No independent human philological or linguistic validation is claimed.

The first conservative pass yields **2,140 computational candidates**, of which **2,105** are automatically aligned to a PDF page and **35** retain sequence-inferred alignment. These counts are extraction metrics, not a definitive count of historical dictionary entries.

Source binaries are downloaded reproducibly from Internet Archive and are not committed to Git. Derived OCR, page text, candidate inventories, manifests and reports are versioned. See `PROVENANCE.md`, `EDITORIAL_POLICY.md`, `DATASHEET.md` and `SCHEMA.md`.
