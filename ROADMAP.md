# Hoja de ruta

## Fase 1 — ingestión reproducible — línea base `0.1.0-dev` completada

Fuente, procedencia, OCR, separación de secciones, candidatos, alineación de páginas, schemas, CI y documentación científica inicial. La línea base conserva 2,140 candidatos computacionales y no afirma validación humana independiente.

## Fase 2 — reconciliación de fronteras — iniciada

Cotejar los 2,140 candidatos contra las páginas, detectar comienzos omitidos, artículos fusionados y falsas fronteras; documentar cada decisión sin borrar el OCR previo.

La infraestructura de esta fase incluye una cola reproducible de revisión humana, criterios explícitos de priorización, un protocolo de reconciliación y un schema separado para decisiones humanas. La cola no constituye validación filológica ni lingüística.

Criterio de salida: cada candidato debe tener una decisión de reconciliación o un diferimiento explícito y trazable; las fusiones y divisiones deben quedar documentadas antes de asignar identificadores de artículo canónico.

## Fase 3 — artículos canónicos

Fijar `ORT1888-art-######`, spans físicos, guía castellana, formas coras, marcas gramaticales, plurales, ejemplos, remisiones y notas.

## Fase 4 — interoperabilidad

Generar TEI Lex-0 y evaluar CLDF como vistas derivadas, nunca como reemplazo del objeto histórico.

## Fase 5 — release científica

Congelar contratos, ejecutar QA, publicar release archivada, DOI, citación estable, informe técnico-académico y sitio público de consulta.
