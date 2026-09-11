# Modelo de datos y contratos

```text
fuente / metadatos
        ↓
OCR bruto
        ├─ cuerpo alfabético → ORT1888-cand → resolución máquina → ORT1888-art / estados residuales
        └─ apéndices → inventarios de navegación → modelos machine-only específicos
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

## Regla para vistas interoperables
TEI Lex-0, CLDF u otros formatos deben generarse como proyecciones derivadas. Ninguna vista interoperable sustituirá los objetos internos ni podrá omitir procedencia, autoridad computacional, estado de incertidumbre o vínculo con el OCR fuente.
