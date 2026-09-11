# Cora Histórico Digital

**Cora Histórico Digital (CHD)** es un corpus histórico-digital reproducible para estudiar testimonios históricos de la lengua cora/náayeri sin confundir fuente, OCR, segmentación, inferencia computacional e interpretación lingüística.

La implementación inicial trabaja con el *Vocabulario de las lenguas castellana y cora* de José de Ortega mediante la reimpresión de Tepic de 1888, derivada de la obra impresa en México en 1732. El testimonio digital canónico procede de John Carter Brown Library / Internet Archive (`vocabulariodelas00orte`).

[![CI](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml/badge.svg)](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml)

> **Estado científico: `0.1.0-dev`, machine-only.** El repositorio no tiene etapa de revisión humana. Ninguna salida se presenta como validación filológica o lingüística humana.

## Estado actual

| Dimensión | Estado |
|---|---:|
| páginas físicas del PDF | **98** |
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
| revisión humana dentro del repo | **no existe** |

Los 2,140 candidatos representan exclusivamente el cuerpo alfabético. La resolución machine-only conserva todos como evidencia fuente: 2,137 se promueven a artículos, dos se identifican como artefactos de segmentación de cabecera/pre-folio y uno permanece incierto.

El apéndice numeral cuenta además con **27 pares explícitos** estructurados: 22 de cuenta general, 3 de frecuencia y 2 de conteo animado. El apéndice de verbos irregulares/partículas se representa ahora mediante **22 unidades documentales machine-only** ligadas uno-a-uno a su inventario de navegación: 4 ejemplos imperativos, 5 ejemplos de expresión, 3 descripciones de partículas, 3 bloques de prosa explicativa, 2 grupos de formas, 1 descripción de verbo irregular y 4 unidades de ruido OCR. Esta tipificación describe señales documentales; no normaliza formas ni pretende análisis gramatical moderno.

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
derivados interoperables y releases citables
```

Un caso incierto o rechazado sigue siendo evidencia trazable. La arquitectura prefiere conservar incertidumbre y artefactos fuente antes que fabricar completitud o borrar errores de segmentación.

## Reglas de resolución máquina

Los estados del cuerpo alfabético no dependen de juicio humano ni de listas de excepciones por ID. Las coincidencias directas y los anclajes conservadores de misma página producen `machine_accepted`. Una regla estructural adicional detecta ruido OCR situado antes del folio de la página siguiente sólo cuando el candidato es `hyphen_variant`, de baja confianza, queda entre dos anclas directas de páginas consecutivas y su propio span contiene como segmento aislado el número impreso siguiente. Esa regla identifica dos falsos candidatos sin alterar el OCR fuente.

El extractor numeral trabaja únicamente sobre líneas con pares explícitos separados por marcas documentales reconocibles. No asigna valores numéricos normalizados ni corrige grafías OCR; `general_count`, `frequency_count` y `animate_count` reflejan transiciones expresamente anunciadas por la fuente.

El estructurador de verbos irregulares/partículas opera a escala de párrafo OCR. Usa señales superficiales reproducibles —marcadores imperativos, separadores, menciones de `partícula`, marcos narrativos y rasgos de ruido— para tipificar cada unidad. Conserva el texto OCR íntegro, su span de líneas y su enlace `ORT1888-irrunit-###`; no extrae una gramática corregida ni convierte estas categorías documentales en autoridad lingüística.

## Reproducibilidad

Los binarios fuente no se versionan. El pipeline descarga PDF y DjVu TXT desde Internet Archive, verifica SHA-256 contra `data/source/source_lock.json`, reconstruye derivados y falla ante deriva de la fuente.

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
```

`qa` ejecuta pruebas, cobertura documental e invariantes de todas las capas máquina. `bootstrap-corpus` reconstruye y versiona únicamente derivados reproducibles; no genera facsímiles, formularios ni colas para revisión humana.

## Datos principales

- `data/source/ocr/`: OCR completo y extracción textual por página.
- `data/source/source_manifest.json`: procedencia y hashes.
- `data/lexicon/candidates.csv` / `.jsonl`: hipótesis de segmentación fuente.
- `data/lexicon/machine_lexicon.csv` / `.jsonl`: capa machine-only derivada.
- `data/appendices/machine_inventory.json`: navegación automática íntegra de los apéndices.
- `data/appendices/numerals_machine.csv` / `.jsonl`: 27 pares explícitos del apéndice numeral.
- `data/appendices/irregular_particles_machine.csv` / `.jsonl`: 22 unidades estructuradas del apéndice de verbos/partículas.
- `reports/numerals_machine.json`: métricas y política de extracción numeral.
- `reports/irregular_particles_machine.json`: cobertura y distribución de tipos del apéndice gramatical.
- `reports/machine_resolution.json`: conteos, incertidumbre, rechazos y política de IDs.
- `reports/source_coverage.json`: auditoría de conservación completa del testimonio.

## Autoridad y límites

`machine_accepted`, `machine_uncertain`, `machine_rejected` y los tipos documentales de apéndice son estados computacionales. `human_verified=false` funciona sólo como declaración epistemológica; no es una cola de trabajo ni una condición futura del pipeline.

CHD no es un diccionario normativo del náayeri contemporáneo, no asigna automáticamente identidad dialectal moderna y no convierte categorías coloniales de la fuente en taxonomías actuales.

## Ruta científica

La estructuración machine-only de los dos apéndices está cubierta con modelos específicos y trazables. La siguiente meta es **interoperabilidad**: generar una proyección TEI Lex-0 y evaluar CLDF como vistas derivadas sin sustituir los objetos históricos internos. Después corresponde congelar contratos y preparar una release científica citable y archivada.

## Licencias y citación

Código: MIT. Metadatos, anotaciones y derivados originales: CC BY 4.0 salvo indicación contraria. La obra histórica es de dominio público; CHD no reclama autoría sobre la digitalización institucional. Mientras el proyecto permanezca en `0.1.0-dev`, cite el testimonio y el commit utilizado; el DOI se añadirá cuando exista una release archivada.
