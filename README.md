# Cora Histórico Digital

**Cora Histórico Digital (CHD)** es un corpus histórico-digital reproducible para estudiar testimonios históricos de la lengua cora/náayeri sin confundir obra histórica, testimonio bibliográfico, digitalización institucional, OCR, segmentación, inferencia computacional e interpretación lingüística.

[![CI](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml/badge.svg)](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/fersandovalgtz/cora-historico-digital)](https://github.com/fersandovalgtz/cora-historico-digital/releases/tag/v0.1.0)

> **Estado científico: `v0.1.0`, release pública, machine-only.** El repositorio no contiene una etapa de revisión humana. Ninguna salida se presenta como validación filológica o lingüística humana, diccionario normativo contemporáneo ni edición crítica.

## Origen histórico y testimonio utilizado

CHD parte de una obra lexicográfica atribuida al jesuita **José de Ortega (1700–1768)**. La obra fue impresa por primera vez en **México en 1732** con el título *Vocabulario en lengua castellana y cora. Dispuesto por el P. Joseph de Ortega, de la Compañia de Jesus*, por **los herederos de la Viuda de Francisco Rodríguez Lupercio**.

El corpus **no transcribe directamente un ejemplar digital de la impresión de 1732**. Su testimonio de trabajo es la **reimpresión de Tepic de 1888**, titulada *Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano*, publicada por la **Imprenta de Antonio Lagaspi**.

El ejemplar digital canónico utilizado por CHD pertenece a la **John Carter Brown Library** y se consulta mediante Internet Archive con el identificador [`vocabulariodelas00orte`](https://archive.org/details/vocabulariodelas00orte) y ARK `ark:/13960/t2t44qw20`. El registro de Internet Archive documenta además la procedencia del ejemplar mediante ex libris de **Nicolás León (1859–1929)** y señala que la copia de la John Carter Brown Library es imperfecta y carece aparentemente del título de cubierta.

La relación documental se modela explícitamente así:

```text
ORTEGA1732
obra histórica impresa en México
        ↓ tradición/reimpresión
ORTEGA1888-TEPIC
reimpresión de Tepic, Imprenta de Antonio Lagaspi
        ↓ ejemplar conservado
John Carter Brown Library
procedencia documentada: Nicolás León
        ↓ digitalización institucional / acceso
Internet Archive: vocabulariodelas00orte
        ↓ descarga bloqueada por SHA-256
OCR y texto extraíble
        ↓
Cora Histórico Digital
candidatos → resolución machine-only → vistas interoperables
```

Esta distinción entre **obra (1732)**, **testimonio utilizado (1888)**, **ejemplar físico**, **objeto digital** y **derivados computacionales** es parte del contrato científico del repositorio. Véanse [`PROVENANCE.md`](PROVENANCE.md), [`DATASHEET.md`](DATASHEET.md) y [`data/source/source_manifest.json`](data/source/source_manifest.json).

### Referencias históricas principales

- Ortega, José de. *Vocabulario en lengua castellana y cora. Dispuesto por el P. Joseph de Ortega, de la Compañia de Jesus*. México: Herederos de la Viuda de Francisco Rodríguez Lupercio, 1732.
- Ortega, José de. *Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano*. Tepic: Imprenta de Antonio Lagaspi, 1888.
- Testimonio digital canónico: John Carter Brown Library / Internet Archive, `vocabulariodelas00orte`.

## Estado actual

| Dimensión | Estado |
|---|---:|
| versión publicada | **0.1.0** |
| páginas físicas procesadas del PDF | **98** |
| líneas OCR preservadas | **5,388** |
| candidatos del cuerpo alfabético | **2,140** |
| `matched_headword` | **2,131** |
| `anchored_same_page` | **6** |
| `inferred_sequence` | **3** |
| artículos `machine_accepted` | **2,137** |
| artefactos `machine_rejected` | **2** |
| candidatos `machine_uncertain` | **1** |
| pares explícitos del apéndice numeral | **27** |
| unidades estructuradas de verbos/partículas | **22** |
| entradas TEI Lex-0 validadas | **2,137 + 3 residuales** |
| filas CLDF Dictionary | **2,137 entradas + 2,137 sentidos + 3 residuales** |
| revisión humana dentro del repo | **no existe** |

Los 2,140 candidatos representan exclusivamente el cuerpo alfabético. La resolución machine-only conserva todos como evidencia fuente: 2,137 se promueven a artículos, dos se identifican como artefactos de segmentación de cabecera/pre-folio y uno permanece incierto.

El apéndice numeral cuenta además con **27 pares explícitos** estructurados: 22 de cuenta general, 3 de frecuencia y 2 de conteo animado. El apéndice de verbos irregulares/partículas se representa mediante **22 unidades documentales machine-only** ligadas uno-a-uno a su inventario de navegación: 4 ejemplos imperativos, 5 ejemplos de expresión, 3 descripciones de partículas, 3 bloques de prosa explicativa, 2 grupos de formas, 1 descripción de verbo irregular y 4 unidades de ruido OCR. Esta tipificación describe señales documentales; no normaliza formas ni pretende análisis gramatical moderno.

La capa alfabética dispone de dos vistas interoperables regenerables y validadas. **TEI Lex-0 0.9.5** conserva 2,137 entradas y los 3 residuales como evidencia no promovida; el XML pasa el Relax NG oficial fijado por checksum. **CLDF Dictionary** conserva las mismas 2,137 entradas como `EntryTable` y una fila `SenseTable` por artículo con el `cora_ocr` íntegro, mientras los 3 residuales permanecen en una tabla CSVW documental separada. Ambas vistas preservan la autoridad machine-only y no sustituyen los objetos internos.

## Arquitectura de evidencia

```text
testimonio digital bloqueado por checksum
        ↓
OCR bruto preservado
        ├─ cuerpo alfabético → ORT1888-cand-###### → resolución máquina
        │                       ├─ machine_accepted → ORT1888-art-######
        │                       ├─ machine_uncertain
        │                       └─ machine_rejected
        └─ apéndices
             ├─ numerales → ORT1888-num-###
             └─ verbos/partículas → ORT1888-irr-###
                    ├─ imperative_example
                    ├─ expression_example
                    ├─ particle_description
                    ├─ irregular_verb_description
                    ├─ form_cluster
                    ├─ explanatory_prose
                    └─ ocr_noise
        ↓
vistas derivadas validadas
        ├─ TEI Lex-0 0.9.5
        └─ CLDF Dictionary
        ↓
release científica citable v0.1.0
```

Un caso incierto o rechazado sigue siendo evidencia trazable. La arquitectura prefiere conservar incertidumbre y artefactos fuente antes que fabricar completitud o borrar errores de segmentación.

## Reglas de resolución máquina

Los estados del cuerpo alfabético no dependen de juicio humano ni de listas de excepciones por ID. Las coincidencias directas y los anclajes conservadores de misma página producen `machine_accepted`. Una regla estructural adicional detecta ruido OCR situado antes del folio de la página siguiente sólo cuando el candidato es `hyphen_variant`, de baja confianza, queda entre dos anclas directas de páginas consecutivas y su propio span contiene como segmento aislado el número impreso siguiente. Esa regla identifica dos falsos candidatos sin alterar el OCR fuente.

El extractor numeral trabaja únicamente sobre líneas con pares explícitos separados por marcas documentales reconocibles. No asigna valores numéricos normalizados ni corrige grafías OCR; `general_count`, `frequency_count` y `animate_count` reflejan transiciones expresamente anunciadas por la fuente.

El estructurador de verbos irregulares/partículas opera a escala de párrafo OCR. Usa señales superficiales reproducibles —marcadores imperativos, separadores, menciones de `partícula`, marcos narrativos y rasgos de ruido— para tipificar cada unidad. Conserva el texto OCR íntegro, su span de líneas y su enlace `ORT1888-irrunit-###`; no extrae una gramática corregida ni convierte estas categorías documentales en autoridad lingüística.

## Reproducibilidad

Los binarios fuente no se versionan. El pipeline descarga PDF y DjVu TXT desde Internet Archive, verifica SHA-256 contra `data/source/source_lock.json`, reconstruye derivados y falla ante deriva de la fuente. TEI Lex-0 se valida contra el Relax NG oficial 0.9.5, también fijado por SHA-256, y CLDF se valida con `pycldf` / `cldf validate` antes de que bootstrap pueda versionar derivados.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make ingest
make validate
make source-coverage
make appendix-machine-inventory
make numeral-machine-lexicon
make irregular-particles-machine
make machine-corpus
make tei-lex0
make cldf-dictionary
```

`qa` ejecuta pruebas, cobertura documental, invariantes de todas las capas máquina y validación de ambas vistas interoperables. `bootstrap-corpus` reconstruye y versiona únicamente derivados reproducibles; no genera facsímiles, formularios ni colas para revisión humana.

## Datos principales

- `data/source/ocr/`: OCR completo y extracción textual por página.
- `data/source/source_manifest.json`: procedencia, particiones y hashes.
- `data/source/source_lock.json`: bloqueo criptográfico de los objetos digitales de origen.
- `data/lexicon/candidates.csv` / `.jsonl`: hipótesis de segmentación fuente.
- `data/lexicon/machine_lexicon.csv` / `.jsonl`: capa machine-only derivada.
- `data/appendices/machine_inventory.json`: navegación automática íntegra de los apéndices.
- `data/appendices/numerals_machine.csv` / `.jsonl`: 27 pares explícitos del apéndice numeral.
- `data/appendices/irregular_particles_machine.csv` / `.jsonl`: 22 unidades estructuradas del apéndice de verbos/partículas.
- `data/interoperability/ortega1888_tei_lex0.xml`: proyección TEI Lex-0 0.9.5 validada.
- `data/interoperability/cldf/Dictionary-metadata.json`: metadata de la proyección CLDF Dictionary.
- `data/interoperability/cldf/entries.csv`: 2,137 entradas aceptadas.
- `data/interoperability/cldf/senses.csv`: 2,137 descripciones Cora/Náayeri no segmentadas.
- `data/interoperability/cldf/languages.csv`: lenguas `spa` y `crn`.
- `data/interoperability/cldf/residuals.csv`: 3 candidatos no promovidos, conservados como evidencia.
- `data/interoperability/cldf/sources.bib`: referencias bibliográficas de la obra de 1732 y del testimonio de 1888.
- `reports/numerals_machine.json`: métricas y política de extracción numeral.
- `reports/irregular_particles_machine.json`: cobertura y distribución de tipos del apéndice gramatical.
- `reports/machine_resolution.json`: conteos, incertidumbre, rechazos y política de IDs.
- `reports/source_coverage.json`: auditoría de conservación completa del testimonio.
- `reports/tei_lex0.json`: contrato y métricas de la proyección TEI.
- `reports/cldf_dictionary.json`: contrato, métricas y validación de la proyección CLDF.

## Autoridad y límites

`machine_accepted`, `machine_uncertain`, `machine_rejected` y los tipos documentales de apéndice son estados computacionales. `human_verified=false` funciona sólo como declaración epistemológica; no es una cola de trabajo ni una condición futura del pipeline.

CHD no es un diccionario normativo del náayeri contemporáneo, no asigna automáticamente identidad dialectal moderna y no convierte categorías coloniales de la fuente en taxonomías actuales. En CLDF, una fila de `SenseTable` por artículo es una representación documental del equivalente OCR completo, no una afirmación de que cada artículo posea lingüísticamente un único sentido.

## Release científica

La versión pública actual es **[`v0.1.0`](https://github.com/fersandovalgtz/cora-historico-digital/releases/tag/v0.1.0)**, publicada el **11 de septiembre de 2026**. La release fija un snapshot científico reproducible e incluye manifiesto de integridad y `SHA256SUMS`.

El siguiente paso de preservación es el depósito en un archivador externo y el registro de un **DOI real** cuando sea emitido. El repositorio no anticipa ni inventa identificadores persistentes. La etiqueta `v0.1.0` permanece como snapshot científico; cualquier actualización posterior de metadatos en `main` no reescribe retroactivamente ese tag.

Nuevos formatos, normalizaciones o integraciones sólo se justificarán si añaden valor científico concreto. La prioridad es explotar el activo ya estable mediante citación, reutilización docente e institucional, investigación, curación/consultoría y colaboraciones financiadas, evitando elevar innecesariamente el costo marginal del proyecto.

## Licencias y citación

- Código: **MIT**.
- Metadatos, anotaciones y derivados originales de CHD: **CC BY 4.0**, salvo indicación contraria.
- La obra histórica se encuentra en dominio público; CHD no reclama autoría ni propiedad sobre la digitalización institucional de la John Carter Brown Library / Internet Archive.

Para citar CHD antes de que exista DOI, use la versión y la URL de la release:

> Sandoval Gutiérrez, Fernando. 2026. *Cora Histórico Digital*. Version 0.1.0. Dataset/corpus histórico-digital. GitHub. https://github.com/fersandovalgtz/cora-historico-digital/releases/tag/v0.1.0

Cuando el uso dependa de las formas históricas, cite además el testimonio de Ortega de 1888 y, cuando corresponda al argumento histórico-bibliográfico, la edición original de 1732. `CITATION.cff` contiene los metadatos del proyecto; `data/interoperability/cldf/sources.bib` contiene las referencias de la fuente histórica.
