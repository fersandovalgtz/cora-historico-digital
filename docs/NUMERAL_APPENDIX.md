# Apéndice numeral — capa machine-only

El apéndice numeral de Ortega 1888 contiene pares explícitos castellano–cora, instrucciones de formación, ejemplos, números de página y ruido OCR. CHD mantiene dos representaciones complementarias:

- `data/appendices/machine_inventory.json`: unidades de navegación que preservan todos los párrafos OCR;
- `data/appendices/numerals_machine.csv` y `.jsonl`: sólo líneas donde el testimonio presenta explícitamente dos expresiones separadas por una marca de equivalencia reconocible.

## Regla de extracción

`scripts/build_numeral_machine_lexicon.py` procesa el OCR línea por línea. Acepta el guion largo `—` y dos variantes ASCII estrechas que aparecen en el testimonio. Una línea sólo produce registro si existen expresiones alfabéticas no vacías a ambos lados y el lado castellano es corto. Los guiones de corte de línea, instrucciones narrativas, números de página y ruido aislado no producen registros.

El extractor no corrige OCR ni reconstruye formas ausentes. `spanish_expression_ocr`, `cora_expression_ocr` y `raw_line_ocr` preservan la lectura de entrada.

## Series documentales

La fuente anuncia explícitamente tres contextos. El extractor los modela como:

- `general_count`: serie general desde el comienzo del apéndice;
- `frequency_count`: desde “Para decir una vez, dos veces, etc. dicen:”;
- `animate_count`: desde “Para decir dos hombres, tres hombres...”.

Estas etiquetas describen la organización textual declarada por la fuente. No constituyen un análisis gramatical moderno.

## Identificadores

Los registros usan `ORT1888-num-###` en orden de aparición. Este namespace es independiente de `ORT1888-cand-######`, `ORT1888-art-######` y de las unidades de navegación `ORT1888-numunit-###`.

## Autoridad

Todos los registros son `authority_status=machine_derived`, `record_status=machine_extracted_explicit_pair` y `human_verified=false`. Una extracción explícita no equivale a normalización, traducción validada ni análisis lingüístico contemporáneo.
