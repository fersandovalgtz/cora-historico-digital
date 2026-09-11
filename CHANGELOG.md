# Changelog

## `0.1.0-dev` — 2026-09-11

- incorpora una proyección regenerable de la capa alfabética a **TEI Lex-0 0.9.5**;
- proyecta **2,137** registros `machine_accepted` como entradas TEI y conserva **3** candidatos residuales fuera del cuerpo lexicográfico;
- preserva de forma literal IDs, `headword_es_ocr`, `cora_ocr`, procedencia y autoridad machine-only;
- valida la proyección TEI completa con **Jing** contra el Relax NG oficial archivado de TEI Lex-0 0.9.5;
- fija el schema TEI externo por SHA-256 `35e73fef48526634714bdf3d16b924f958fca078a903d0bdc2dd4d7d116d1aaa` para detectar deriva remota;
- obliga a QA y bootstrap a fallar si cambia el schema oficial fijado o si el XML generado deja de validar antes de cualquier commit automático;
- incorpora una segunda proyección regenerable mediante **CLDF Dictionary**;
- genera **2,137 filas `EntryTable`** y **2,137 filas `SenseTable`** uno-a-uno, manteniendo el lema OCR castellano como `spa` y el `cora_ocr` íntegro como descripción `crn`, sin segmentar sentidos ni equivalentes;
- conserva candidato fuente, páginas, líneas OCR, texto bruto, alineación, confianza, racional, autoridad y `human_verified=false` mediante extensiones CHD;
- mantiene los **3 registros residuales** en `residuals.csv`, tabla CSVW documental que no los promueve a entradas;
- valida el dataset CLDF con `pycldf` y `cldf validate` dentro de QA y bootstrap;
- cierra la **fase 4 de interoperabilidad** con dos vistas validadas;
- abre la preparación del release candidate `0.1.0` sin publicar todavía la versión;
- añade `scripts/build_release_manifest.py` para inventariar de forma determinista todos los artefactos versionados de `data/`, `reports/` y `schemas/`, excluyendo binarios externos de `data/source/original/`;
- añade `release/manifest.json` y `release/SHA256SUMS` como derivados de integridad generados por bootstrap;
- incorpora pruebas de determinismo, detección de deriva de inventario/bytes y un workflow `release-candidate` que valida el árbol completo;
- mantiene `CITATION.cff` y CodeMeta en `0.1.0-dev` hasta una decisión explícita de publicación; no se inventa ni registra DOI antes de su emisión real.

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
- estructura el apéndice numeral en **27 pares explícitos** `ORT1888-num-###`, sin normalizar ni completar formas;
- estructura el apéndice de verbos irregulares/partículas en **22 unidades documentales** `ORT1888-irr-###`, enlazadas uno-a-uno con `ORT1888-irrunit-###`;
- distingue de forma reproducible ejemplos imperativos, expresiones, descripciones de partículas, descripción verbal, grupos de formas, prosa explicativa y ruido OCR;
- añade schema, pruebas, QA y regeneración bootstrap para las capas específicas de apéndices;
- elimina interfaces, facsímiles, colas, schemas, workflows y pruebas cuya única finalidad era revisión humana;
- elimina `pymupdf` y simplifica QA/bootstrap para reducir dependencias y costo de ejecución;
- mantiene el checksum lock, auditoría completa del testimonio, trazabilidad y pruebas reproducibles como controles principales de calidad;
- cierra la fase 3 de estructuración de apéndices y deja **interoperabilidad (TEI Lex-0 / evaluación CLDF)** como siguiente fase científica.

## `0.1.0-dev` — 2026-09-09

- inicializa Cora Histórico Digital;
- documenta la distinción obra 1732 / testimonio 1888;
- incorpora pipeline reproducible desde Internet Archive;
- genera OCR y 2,140 candidatos computacionales;
- añade procedencia, política editorial, contratos, CI y documentación FAIR inicial;
- cierra la línea base de ingestión reproducible de fase 1.
