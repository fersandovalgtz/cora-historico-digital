# Interoperabilidad

## Principio

Las salidas interoperables de Cora Histórico Digital son **vistas derivadas**. No sustituyen `data/lexicon/machine_lexicon.*`, los modelos específicos de apéndices ni el OCR fuente. Toda proyección debe conservar IDs, procedencia, autoridad computacional e incertidumbre sin corregir silenciosamente la fuente.

La fase de interoperabilidad del cuerpo alfabético se considera cerrada con dos vistas independientes y formalmente validadas: **TEI Lex-0 0.9.5** y **CLDF Dictionary**.

## TEI Lex-0 0.9.5

El cuerpo alfabético se modela como vocabulario castellano → cora/náayeri:

- lengua objeto de las entradas: `es`;
- lengua de los equivalentes: `crn` (Cora / Náayeri, ISO 639-3);
- cada `machine_accepted` se proyecta como `<entry type="mainEntry">` y conserva su `ORT1888-art-######` como `xml:id`;
- `headword_es_ocr` se conserva como `<form type="lemma"><orth>…</orth></form>`;
- `cora_ocr` se conserva íntegro, sin segmentación ni normalización, dentro de `<cit type="translationEquivalent" xml:lang="crn">`;
- `machine_uncertain` y `machine_rejected` **no se promueven a entradas** y permanecen como residuales documentales en el `back`;
- el encabezado identifica el testimonio Ortega 1888, la licencia de los derivados y el carácter machine-only de la proyección.

La proyección contiene **2,137 entradas y 3 residuales**. QA verifica cobertura, IDs y fidelidad campo-a-campo y ejecuta Jing contra el Relax NG oficial archivado de TEI Lex-0 0.9.5. El schema se fija mediante SHA-256 `35e73fef48526634714bdf3d16b924f958fca078a903d0bdc2dd4d7d116d1aaa`; bootstrap repite esta validación antes de poder versionar derivados.

## CLDF Dictionary

La segunda vista utiliza el módulo **Dictionary**, no `Wordlist`, porque el testimonio contiene artículos históricos con equivalentes y no una matriz comparativa de formas por concepto.

- `EntryTable` contiene **2,137 filas**, una por `machine_accepted`;
- `ID` reutiliza `ORT1888-art-######`;
- `Language_ID=spa` y `Headword=headword_es_ocr`;
- `SenseTable` contiene **2,137 filas**, exactamente una por entrada;
- `Description=cora_ocr` y `Description_Language_ID=crn`;
- la relación 1:1 es estrictamente documental: no implica monosemia y evita dividir automáticamente equivalentes históricos;
- `LanguageTable` declara `spa` y `crn`;
- `sources.bib` registra Ortega 1888 y las entradas conservan referencias por página impresa;
- columnas adicionales `CHD_` mantienen candidato fuente, testimonio, páginas, líneas OCR, texto bruto, alineación, confianza, racional computacional, autoridad, elegibilidad y `human_verified=false`;
- los **3 candidatos no aceptados** se conservan en `residuals.csv`, tabla CSVW documental que no forma parte de `EntryTable`.

El generador recarga el dataset escrito y exige `Dataset.validate()`. QA ejecuta además `cldf validate`, compara cada lema y cada descripción Cora con la capa canónica y verifica que ningún residual sea promovido. Bootstrap repite la validación antes de cualquier commit automático.

## Límites de interoperabilidad

Ni TEI ni CLDF convierten CHD en una edición crítica humana, un diccionario normativo contemporáneo o una gramática normalizada. Los apéndices conservan modelos internos distintos y no se exportan por fuerza al modelo del vocabulario alfabético. Cualquier formato adicional deberá justificar una ventaja científica concreta y preservar los mismos contratos de procedencia, autoridad e incertidumbre.
