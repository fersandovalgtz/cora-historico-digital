# Changelog

## `0.1.0-dev` — 2026-09-10

- adopta formalmente una arquitectura **machine-only**: el repositorio no contiene ni espera revisión humana;
- sustituye la antigua reconciliación humana por una resolución computacional exhaustiva de los 2,140 candidatos;
- define `machine_accepted`, `machine_uncertain` y `machine_rejected` como estados de autoridad computacional;
- asigna `ORT1888-art-######` sólo a candidatos aceptados, preservando el sufijo del candidato fuente para estabilidad de IDs;
- mejora la alineación automática hasta **2,131 `matched_headword`**, **6 `anchored_same_page`** y **3 `inferred_sequence`**;
- incorpora una regla estructural de rechazo para ruido OCR pre-folio, sin listas de excepciones ni juicio lingüístico;
- clasifica `ORT1888-cand-000342` y `ORT1888-cand-001106` como `machine_rejected` y conserva `ORT1888-cand-001457` como `machine_uncertain`;
- deja la capa alfabética en **2,137 artículos `machine_accepted` / 2 artefactos `machine_rejected` / 1 candidato `machine_uncertain`**;
- transforma los apéndices de numerales y verbos/partículas en inventarios machine-only separados;
- elimina interfaces, facsímiles, colas, schemas, workflows y pruebas cuya única finalidad era revisión humana;
- elimina `pymupdf` y simplifica QA/bootstrap para reducir dependencias y costo de ejecución;
- mantiene el checksum lock, auditoría completa del testimonio, trazabilidad y pruebas reproducibles como controles principales de calidad.

## `0.1.0-dev` — 2026-09-09

- inicializa Cora Histórico Digital;
- documenta la distinción obra 1732 / testimonio 1888;
- incorpora pipeline reproducible desde Internet Archive;
- genera OCR y 2,140 candidatos computacionales;
- añade procedencia, política editorial, contratos, CI y documentación FAIR inicial;
- cierra la línea base de ingestión reproducible de fase 1.
