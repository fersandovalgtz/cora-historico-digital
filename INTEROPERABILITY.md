# Interoperabilidad

## Principio

Las salidas interoperables de Cora Histórico Digital son **vistas derivadas**. No sustituyen `data/lexicon/machine_lexicon.*`, los modelos específicos de apéndices ni el OCR fuente. Toda proyección debe conservar IDs, procedencia, autoridad computacional e incertidumbre sin corregir silenciosamente la fuente.

## TEI Lex-0

La primera proyección apunta a **TEI Lex-0 0.9.5**. El cuerpo alfabético se modela como vocabulario castellano → cora/náayeri:

- lengua objeto de las entradas: `es`;
- lengua de los equivalentes: `crn` (Cora / Náayeri, ISO 639-3);
- cada `machine_accepted` se proyecta como `<entry type="mainEntry">` y conserva su `ORT1888-art-######` como `xml:id`;
- `headword_es_ocr` se conserva como `<form type="lemma"><orth>…</orth></form>`;
- `cora_ocr` se conserva íntegro, sin segmentación ni normalización, dentro de `<cit type="translationEquivalent" xml:lang="crn">`;
- `machine_uncertain` y `machine_rejected` **no se promueven a entradas**. Se conservan como residuales documentales en el `back` de la vista;
- el encabezado identifica el testimonio Ortega 1888, la licencia de los derivados y el carácter machine-only de la proyección.

Esta primera subfase comprueba XML bien formado, cobertura, estabilidad de IDs y fidelidad campo-a-campo. La validación contra el schema oficial completo de TEI Lex-0 se tratará como un control adicional antes de declarar cerrada la fase de interoperabilidad.

## CLDF

CLDF permanece en evaluación. No se generará una tabla CLDF hasta definir qué componente representa con menor pérdida un vocabulario histórico español–cora y cómo conservar las capas de OCR, autoridad e incertidumbre sin forzar el corpus a un modelo sin correspondencia documental.
