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
| artículos `machine_accepted` esperados | **2,137** |
| candidatos `machine_uncertain` esperados | **3** |
| revisión humana dentro del repo | **no existe** |

Los 2,140 candidatos representan exclusivamente el cuerpo alfabético. Numerales y verbos/partículas se preservan completos como OCR y tienen inventarios machine-only separados.

## Arquitectura de evidencia

```text
testimonio digital bloqueado por checksum
        ↓
OCR bruto preservado
        ↓
ORT1888-cand-######
        ↓
resolución computacional reproducible
        ├─ machine_accepted → ORT1888-art-######
        ├─ machine_uncertain → candidato preservado, sin artículo
        └─ machine_rejected → candidato preservado como artefacto documentado
        ↓
derivados interoperables y releases citables
```

Un caso incierto es un resultado válido. La arquitectura prefiere conservar incertidumbre antes que fabricar completitud.

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
make machine-corpus
```

`qa` ejecuta pruebas, cobertura documental e invariantes de la capa máquina. `bootstrap-corpus` reconstruye y versiona únicamente derivados reproducibles; ya no genera facsímiles, formularios ni colas para revisión humana.

## Datos principales

- `data/source/ocr/`: OCR completo y extracción textual por página.
- `data/source/source_manifest.json`: procedencia y hashes.
- `data/lexicon/candidates.csv` / `.jsonl`: hipótesis de segmentación fuente.
- `data/lexicon/machine_lexicon.csv` / `.jsonl`: capa machine-only derivada.
- `data/appendices/machine_inventory.json`: unidades de navegación automática de los apéndices.
- `reports/machine_resolution.json`: conteos, incertidumbre y política de IDs.
- `reports/source_coverage.json`: auditoría de conservación completa del testimonio.

## Autoridad y límites

`machine_accepted`, `machine_uncertain` y `machine_rejected` son estados computacionales. `human_verified=false` funciona sólo como declaración epistemológica; no es una cola de trabajo ni una condición futura del pipeline.

CHD no es un diccionario normativo del náayeri contemporáneo, no asigna automáticamente identidad dialectal moderna y no convierte categorías coloniales de la fuente en taxonomías actuales.

## Ruta científica

La siguiente meta es estabilizar la capa machine-only, estructurar automáticamente los apéndices con modelos propios y preparar una release citable con incertidumbre explícita. TEI Lex-0, CLDF u otras proyecciones podrán generarse como vistas derivadas sin sustituir el objeto histórico.

## Licencias y citación

Código: MIT. Metadatos, anotaciones y derivados originales: CC BY 4.0 salvo indicación contraria. La obra histórica es de dominio público; CHD no reclama autoría sobre la digitalización institucional. Mientras el proyecto permanezca en `0.1.0-dev`, cite el testimonio y el commit utilizado; el DOI se añadirá cuando exista una release archivada.
