# Modelo de datos y contratos

```text
fuente / metadatos
        ↓
OCR bruto
        ├─ cuerpo alfabético → ORT1888-cand → resolución máquina → ORT1888-art / estados residuales
        └─ apéndices → inventarios de navegación → modelos machine-only específicos
        ↓
vistas derivadas
        ├─ TEI Lex-0 0.9.5
        └─ CLDF Dictionary
```

## Candidatos
`schemas/vocabulary-candidate.schema.json` modela las hipótesis de segmentación del cuerpo alfabético. `processing_status=machine_candidate`; `human_verified=false` declara autoridad, no una tarea pendiente.

## Capa de resolución alfabética
`schemas/machine-lexicon-record.schema.json` modela todos los candidatos tras la resolución computacional. `machine_status` admite `machine_accepted`, `machine_uncertain` y `machine_rejected`.

Sólo `machine_accepted` recibe `article_id`. El ID conserva el sufijo del candidato fuente: `ORT1888-cand-000042` → `ORT1888-art-000042`. Los huecos son válidos y evitan renumeración si cambia una clasificación.

## Inventarios de apéndices
`ORT1888-numunit-###` y `ORT1888-irrunit-###` son IDs locales de navegación machine-only. Preservan unidades OCR y no extienden ni renumeran `ORT1888-cand-######`.

## Registros numerales
`schemas/numeral-machine-record.schema.json` modela pares explícitos del apéndice numeral. Los IDs `ORT1888-num-###` siguen el orden de aparición de las líneas extraídas y son independientes de `ORT1888-numunit-###`.

Cada registro conserva línea de origen, expresiones OCR castellana y cora, separador observado, serie documental, autoridad y estado machine-only. `semantic_series` admite `general_count`, `frequency_count` y `animate_count`, activadas únicamente por transiciones explícitas del texto fuente.

No se incluye todavía un campo de valor numérico normalizado. Si se añade posteriormente, deberá ser una capa derivada separada y no sustituirá `spanish_expression_ocr` ni `cora_expression_ocr`.

## Registros de verbos irregulares y partículas
`schemas/irregular-particle-machine-record.schema.json` modela el apéndice heterogéneo de verbos irregulares y partículas a escala de párrafo OCR. Los IDs `ORT1888-irr-###` siguen el orden documental y enlazan uno-a-uno con los IDs de navegación `ORT1888-irrunit-###`.

Cada registro conserva `raw_text_ocr`, span de líneas, observaciones superficiales y un `record_type` documental. Los tipos admitidos son `imperative_example`, `expression_example`, `particle_description`, `irregular_verb_description`, `form_cluster`, `explanatory_prose` y `ocr_noise`.

Estos tipos no constituyen una gramática moderna ni una edición crítica. Son clasificaciones computacionales reproducibles para preservar heterogeneidad y permitir proyecciones posteriores sin forzar el apéndice al modelo del vocabulario alfabético.

## Proyección TEI Lex-0
`data/interoperability/ortega1888_tei_lex0.xml` es una vista regenerable orientada a TEI Lex-0 0.9.5. Sólo los registros `machine_accepted` se convierten en `<entry>` y conservan el `article_id` como `xml:id`. El lema castellano y el equivalente cora se emiten literalmente desde `headword_es_ocr` y `cora_ocr`; los tres candidatos no aceptados permanecen en material posterior como evidencia documental.

El documento preserva procedencia y categorías de autoridad mediante referencias y taxonomía internas. Se valida con Jing contra el Relax NG oficial archivado de TEI Lex-0 0.9.5, fijado por SHA-256 `35e73fef48526634714bdf3d16b924f958fca078a903d0bdc2dd4d7d116d1aaa`.

## Proyección CLDF Dictionary
`data/interoperability/cldf/Dictionary-metadata.json` describe una vista CLDF Dictionary regenerable. No se usa `Wordlist` porque el objeto fuente es un vocabulario histórico de entradas y equivalentes, no una lista comparativa de formas por concepto.

Cada `machine_accepted` produce exactamente una fila en `EntryTable`: `ID=article_id`, `Language_ID=spa` y `Headword=headword_es_ocr`. Produce también exactamente una fila en `SenseTable`, con ID `<article_id>-s1`, `Entry_ID=article_id`, `Description=cora_ocr` y `Description_Language_ID=crn`. Esta relación uno-a-uno es documental; no significa que cada artículo tenga lingüísticamente un solo sentido y no autoriza a dividir automáticamente las secuencias OCR.

Las columnas prefijadas `CHD_` conservan candidato fuente, testimonio, páginas, líneas OCR, texto bruto, separación observada, alineación, confianza, racional, autoridad, elegibilidad y `human_verified=false`. `LanguageTable` declara `spa` y `crn`. `sources.bib` registra el testimonio Ortega 1888 y las entradas preservan referencias por página impresa cuando ésta existe.

`residuals.csv` es una tabla CSVW adicional, no una tabla de entradas. Contiene los dos `machine_rejected` y el `machine_uncertain` para mantener incertidumbre y artefactos trazables sin promoverlos a objetos lexicográficos válidos.

La proyección debe pasar `pycldf` / `cldf validate`; QA compara además cada lema y cada descripción Cora contra la capa canónica.

## Regla para vistas interoperables
TEI Lex-0, CLDF u otros formatos se generan como proyecciones derivadas. Ninguna vista interoperable sustituye los objetos internos ni puede omitir procedencia, autoridad computacional, estado de incertidumbre o vínculo con el OCR fuente. Nuevos formatos sólo se añaden si ofrecen interoperabilidad concreta sin forzar los objetos heterogéneos del corpus a un modelo semánticamente falso.
