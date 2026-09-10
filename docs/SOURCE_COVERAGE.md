# Cobertura del testimonio Ortega 1888

El testimonio digital de la reimpresión de Tepic de 1888 se conserva completo en OCR, pero **no todo su contenido léxico está todavía estructurado como candidatos lexicográficos**. Esta distinción es obligatoria para interpretar correctamente las cifras del proyecto.

## Particiones canónicas del OCR

La ingestión divide el OCR completo en cuatro intervalos contiguos y no superpuestos:

1. `preliminary_matter` → `data/grammar/preliminary_ocr.txt`;
2. `alphabetical_lexicon_body` → `data/source/ocr/lexicon_body_raw.txt`;
3. `numerals_appendix` → `data/appendices/numerals_ocr.txt`;
4. `irregular_verbs_particles_appendix` → `data/appendices/irregular_verbs_particles_ocr.txt`.

El cuerpo alfabético comienza con la entrada identificada por la fórmula «A., denotando la persona que padece». El apéndice numeral comienza con «Cuenta para contar todo lo numerable». El último bloque comienza con la indicación «Por último pondrá aqui algunos verbos irregulares…».

La separación no descarta texto: los cuatro intervalos cubren la secuencia completa de líneas del OCR. `scripts/audit_source_coverage.py` reconstruye las fronteras desde el OCR completo, vuelve a generar en memoria cada partición y exige igualdad exacta con los archivos derivados.

## Qué significan los 2,140 candidatos

`ORT1888-cand-######` representa actualmente **sólo el cuerpo alfabético del vocabulario**. La ingestión deliberadamente detiene la detección de límites antes del apéndice numeral para no imponer a contenidos heterogéneos la misma estructura de artículo.

Por tanto, la expresión correcta es:

> 2,140 candidatos de artículos del cuerpo alfabético.

No debe describirse esa cifra como «2,140 entradas de todo el testimonio» ni como «léxico completo de Ortega 1888».

## Contenido retenido pero pendiente de estructuración

Los bloques de numerales y de verbos irregulares/partículas forman parte del contenido léxico-gramatical del testimonio y están preservados como OCR. Todavía no tienen un modelo estructurado propio, IDs canónicos ni reconciliación humana.

No deben incorporarse a `data/lexicon/candidates.csv` mediante la heurística del cuerpo alfabético. Hacerlo alteraría el significado del inventario existente y podría desestabilizar la trazabilidad de la fase 2. Su modelado deberá diseñarse como una fase separada, con un esquema adecuado a cada tipo de contenido y sin renumerar los `ORT1888-cand-######` ya existentes.

## Auditoría automática

```bash
make source-coverage
```

El comando genera `reports/source_coverage.json` y falla si detecta cualquiera de estas condiciones:

- falta alguno de los tres marcadores de frontera;
- las fronteras aparecen en un orden inválido;
- un archivo de partición ya no coincide exactamente con su intervalo del OCR completo;
- existe una discontinuidad entre particiones;
- algún candidato del cuerpo alfabético apunta a líneas OCR fuera de ese cuerpo;
- el campo `order` de los candidatos deja de constituir una secuencia completa `1..N`.

La misma auditoría se ejecuta tanto en QA como después de cada reconstrucción del corpus.

## Estado epistemológico

El reporte de cobertura es una comprobación mecánica de conservación, segmentación y alcance. Declara `machine_generated=true` y `human_verified=false`. No valida lecturas, traducciones, límites lexicográficos ni transcripciones.

El estado actual se expresa explícitamente así:

- cuerpo alfabético: estructurado como candidatos de máquina, pendiente de reconciliación humana;
- apéndice numeral: OCR retenido, pendiente de estructuración;
- verbos irregulares y partículas: OCR retenido, pendiente de estructuración;
- contenido léxico del testimonio completamente estructurado: **no**.
