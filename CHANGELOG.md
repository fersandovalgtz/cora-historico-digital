# Changelog

## `0.1.0-dev` — 2026-09-10

- adopta formalmente una arquitectura **machine-only**: el repositorio no contiene ni espera revisión humana;
- sustituye la antigua reconciliación humana por una resolución computacional exhaustiva de los 2,140 candidatos;
- define `machine_accepted`, `machine_uncertain` y `machine_rejected` como estados de autoridad computacional;
- asigna `ORT1888-art-######` sólo a candidatos aceptados, preservando el sufijo del candidato fuente para estabilidad de IDs;
- conserva tres `inferred_sequence` como incertidumbre explícita en lugar de fabricar una decisión;
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
