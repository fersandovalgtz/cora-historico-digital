# Hoja de ruta

## Fase 1 — ingestión reproducible — completada
Fuente, OCR, checksum lock, particiones, candidatos, alineación de páginas, schemas, CI y auditoría completa del testimonio.

## Fase 2 — resolución computacional — estabilizada
La capa alfabética cubre el 100 % de los 2,140 candidatos con estado explícito: **2,137 `machine_accepted`**, **2 `machine_rejected`** y **1 `machine_uncertain`**. Los rechazos preservan la evidencia fuente y la incertidumbre residual no bloquea la arquitectura.

Criterio de salida cumplido: cobertura computacional exhaustiva con autoridad tipada. **No existe criterio de revisión humana.** Nuevas reglas sólo se incorporarán cuando generalicen de forma reproducible y estén protegidas por pruebas negativas.

## Fase 3 — estructuración machine-only de apéndices — completada

### 3A. Numerales — completada
El apéndice numeral conserva su inventario OCR íntegro y añade una representación específica de **27 pares explícitos castellano–cora**: 22 de cuenta general, 3 de frecuencia y 2 de conteo animado. Los registros `ORT1888-num-###` no normalizan ni corrigen el OCR.

### 3B. Verbos irregulares y partículas — completada
El apéndice se representa mediante **22 unidades documentales `ORT1888-irr-###`**, enlazadas uno-a-uno con `ORT1888-irrunit-###`. La tipificación machine-only distingue ejemplos imperativos, expresiones, descripciones de partículas, descripción de verbo irregular, grupos de formas, prosa explicativa y ruido OCR. Cada registro conserva texto OCR y span de líneas; las categorías son documentales, no análisis lingüísticos normalizados.

## Fase 4 — interoperabilidad — completada

### 4A. TEI Lex-0 — completada
La vista derivada orientada a **TEI Lex-0 0.9.5** proyecta los 2,137 registros `machine_accepted` como entradas castellanas con equivalentes cora/náayeri (`crn`) sin normalizar OCR. Los 3 registros residuales permanecen visibles como evidencia documental y no se promueven a entradas.

La proyección preserva IDs, `headword_es_ocr`, `cora_ocr`, procedencia y autoridad machine-only; se regenera desde las capas internas y valida formalmente con Jing contra el Relax NG oficial archivado de TEI Lex-0 0.9.5. El schema queda fijado por SHA-256 `35e73fef48526634714bdf3d16b924f958fca078a903d0bdc2dd4d7d116d1aaa`; QA y bootstrap fallan si cambia el schema o si el XML deja de validar.

### 4B. CLDF Dictionary — completada
La segunda vista derivada usa el módulo **CLDF Dictionary**, no `Wordlist`. Proyecta **2,137 `EntryTable` rows** con lema OCR castellano (`spa`) y **2,137 `SenseTable` rows** uno-a-uno cuya `Description` conserva íntegramente `cora_ocr` y se identifica como `crn`. La relación 1:1 es documental: no divide equivalentes ni infiere polisemia.

Las columnas CHD adicionales preservan candidato fuente, OCR, páginas, líneas, alineación, confianza, racional computacional, autoridad `machine_derived`, elegibilidad y `human_verified=false`. Los **3 candidatos residuales** se conservan en `residuals.csv`, tabla CSVW explícitamente no léxica, y nunca se presentan como entradas. El dataset se regenera desde la capa interna y valida mediante `pycldf` / `cldf validate` en QA y bootstrap.

Criterio de salida cumplido: existen dos vistas interoperables independientes, regenerables y validadas —TEI Lex-0 y CLDF Dictionary— sin pérdida de IDs, fuente, autoridad ni incertidumbre.

## Fase 5 — release científica — activa

### 5A. Release candidate `0.1.0` — activa
Congelar el inventario de artefactos científicos sin publicar todavía la versión. `scripts/build_release_manifest.py` genera un manifiesto determinista y `SHA256SUMS` para todos los archivos versionados bajo `data/`, `reports/` y `schemas/`, excluyendo `data/source/original/`. Un workflow específico verifica inventario y hashes; bootstrap los regenera sólo después de validar corpus, CLDF y TEI.

Durante esta subfase `CITATION.cff` y `codemeta.json` permanecen en `0.1.0-dev`. No se crea tag, GitHub Release ni DOI todavía.

### 5B. Publicación `0.1.0` — pendiente de decisión explícita
Cuando el release candidate quede estable: actualizar coordinadamente versión y fecha en metadatos, ejecutar QA final, crear tag/release archivada y, si se decide usar un repositorio que emita DOI, incorporar únicamente el DOI real después de su asignación. La release puede contener `machine_uncertain` porque su condición queda declarada y preservada.

### 5C. Difusión científica — posterior a la release
Preparar informe técnico-académico, citación definitiva, registro en repositorios/índices pertinentes y sitio público de consulta. Priorizar canales que produzcan evidencia académica, colaboración o reutilización verificable.

## Regla de inversión
El desarrollo adicional debe reutilizar la infraestructura histórico-digital existente y mantener bajo costo marginal. Integraciones o productos comerciales específicos sólo se priorizan ante una ruta verificable a evidencia académica, colaboración financiada, docencia reutilizable, consultoría, servicio gestionado u otra captura legítima de valor.
