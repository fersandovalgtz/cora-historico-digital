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

## Contenido retenido y preestructuración de revisión

Los bloques de numerales y de verbos irregulares/partículas forman parte del contenido léxico-gramatical del testimonio y están preservados como OCR. No deben incorporarse a `data/lexicon/candidates.csv` mediante la heurística del cuerpo alfabético, porque su organización interna es distinta y hacerlo desestabilizaría la trazabilidad de la fase 2.

Como paso previo a cualquier segmentación lexicográfica, `scripts/build_appendix_review_inventory.py` transforma **cada párrafo OCR no vacío** en una unidad exhaustiva de navegación para revisión humana. Los IDs `ORT1888-numunit-###` y `ORT1888-irrunit-###` pertenecen exclusivamente a este inventario de máquina y no amplían ni renumeran `ORT1888-cand-######`.

Cada unidad conserva el texto OCR íntegro, el orden dentro de su apéndice, una clasificación automática meramente descriptiva y `human_verified=false`. Las clases pueden señalar, por ejemplo, que un bloque parece contener un separador de equivalencia, prosa instructiva, descripción de partícula o un marcador de página/ruido OCR. Ninguna clase equivale a `accept`, `reject`, `merge`, `split`, corrección de lectura o delimitación canónica.

El inventario se genera con:

```bash
make appendix-review-inventory
```

Los productos reproducibles son `data/appendices/review_inventory.json` y `reports/appendix_review_inventory.json`. El `bootstrap-corpus` los regenera después de reconstruir el testimonio y QA produce además copias temporales para verificar que el constructor funciona sobre las particiones vigentes.

Este paso **no significa que los apéndices ya estén estructurados como léxico canónico**. Su función es hacer auditable y manejable la revisión posterior sin imponer prematuramente una ontología de entrada a materiales heterogéneos.

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
- apéndice numeral: OCR retenido y organizado en unidades de revisión de máquina, pendiente de estructura lexicográfica humana;
- verbos irregulares y partículas: OCR retenido y organizado en unidades de revisión de máquina, pendiente de estructura lexicográfico-gramatical humana;
- contenido léxico del testimonio completamente estructurado: **no**.
