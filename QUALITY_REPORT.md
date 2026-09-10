# Informe de calidad

La línea `0.1.0-dev` preserva el OCR completo, fija criptográficamente el testimonio digital y reconstruye todos los derivados de manera reproducible.

Estado del cuerpo alfabético: **2,140 candidatos**; **2,131** con `matched_headword`; **6** con `anchored_same_page`; **3** con `inferred_sequence`. Bajo la política actual, los dos primeros estados producen **2,137 artículos `machine_accepted`** y los tres inferidos permanecen `machine_uncertain`.

Riesgos conocidos: separadores deformados por OCR, artículos fusionados, encabezamientos truncados, caracteres espurios, falsas fronteras y diferencias entre OCR ABBYY y texto extraíble del PDF.

La calidad se controla mediante source lock, auditoría de cobertura, invariantes de IDs, tests y CI. Ninguna métrica equivale a validación filológica humana; `human_verified=false` es una declaración permanente de autoridad para estas salidas machine-only.
