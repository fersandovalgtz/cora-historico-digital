# Informe de calidad

La línea `0.1.0-dev` preserva el OCR completo, fija criptográficamente el testimonio digital y reconstruye todos los derivados de manera reproducible.

Estado del cuerpo alfabético: **2,140 candidatos**; **2,131** con `matched_headword`; **6** con `anchored_same_page`; **3** con `inferred_sequence`. La resolución computacional produce **2,137 artículos `machine_accepted`**, **2 artefactos `machine_rejected`** y **1 candidato `machine_uncertain`**.

Los dos rechazos corresponden a un patrón estructural reproducible de ruido OCR antes del folio de la página siguiente. La regla exige simultáneamente baja confianza, extracción `hyphen_variant`, anclas directas en páginas consecutivas y presencia del número impreso siguiente como segmento aislado del span. Los registros rechazados permanecen íntegros en la capa de candidatos y no se eliminan.

El caso residual no satisface esa regla y conserva `machine_uncertain`; el pipeline prefiere incertidumbre explícita antes que una asignación no respaldada.

Riesgos conocidos: separadores deformados por OCR, artículos fusionados, encabezamientos truncados, caracteres espurios, falsas fronteras, alteraciones del orden de lectura y diferencias entre OCR ABBYY y texto extraíble del PDF.

La calidad se controla mediante source lock, auditoría de cobertura, invariantes de IDs, pruebas negativas de las reglas de resolución y CI. Ninguna métrica equivale a validación filológica humana; `human_verified=false` es una declaración permanente de autoridad para estas salidas machine-only.
