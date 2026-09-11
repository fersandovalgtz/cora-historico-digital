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

## Fase 4 — interoperabilidad — activa

### 4A. TEI Lex-0 — completada
La vista derivada orientada a **TEI Lex-0 0.9.5** proyecta los 2,137 registros `machine_accepted` como entradas castellanas con equivalentes cora/náayeri (`crn`) sin normalizar OCR. Los 3 registros residuales permanecen visibles como evidencia documental y no se promueven a entradas.

La proyección preserva IDs, `headword_es_ocr`, `cora_ocr`, procedencia y autoridad machine-only; se regenera desde las capas internas y valida formalmente con Jing contra el Relax NG oficial archivado de TEI Lex-0 0.9.5. El schema queda fijado por SHA-256 `35e73fef48526634714bdf3d16b924f958fca078a903d0bdc2dd4d7d116d1aaa`; QA y bootstrap deben fallar si cambia el schema o si el XML deja de validar.

### 4B. CLDF Dictionary — activa
Evaluar e implementar una segunda vista derivada mediante el módulo **CLDF Dictionary**, no `Wordlist`. El mapeo base debe usar `EntryTable` y `SenseTable` sin inventar segmentación semántica: cada artículo aceptado conservará su ID estable y su lema OCR castellano, mientras el equivalente cora/náayeri se representará en la capa de sentido únicamente en la medida permitida por el contrato CLDF.

Las extensiones CHD deberán preservar OCR literal, procedencia, páginas, candidato fuente, autoridad `machine_derived` y `human_verified=false`. Los 3 registros residuales no deberán presentarse como entradas lexicográficas válidas; si CLDF no ofrece una representación estándar adecuada, se conservarán en una tabla de extensión documental explícitamente no léxica.

Criterio de salida de fase 4: mantener TEI Lex-0 validado y producir una segunda vista CLDF regenerable y validable sin pérdida de IDs, fuente, autoridad ni incertidumbre.

## Fase 5 — release científica
Congelar contratos, ejecutar QA, publicar release archivada, DOI, citación estable, informe técnico-académico y sitio público de consulta. Una release puede contener `machine_uncertain` si queda declarado.

## Regla de inversión
El desarrollo adicional debe reutilizar la infraestructura histórico-digital existente y mantener bajo costo marginal. Integraciones o productos comerciales específicos sólo se priorizan ante una ruta verificable a evidencia académica, colaboración financiada, docencia reutilizable, consultoría, servicio gestionado u otra captura legítima de valor.
