# Cora Histórico Digital

**Cora Histórico Digital (CHD)** es una infraestructura de investigación para convertir testimonios históricos de la lengua cora en objetos digitales **trazables, versionados, citables y reproducibles**, sin confundir OCR, segmentación computacional, reconstrucción editorial e interpretación lingüística.

La implementación inicial trabaja con el *Vocabulario de las lenguas castellana y cora* de José de Ortega a partir de la **reimpresión de Tepic de 1888**, que reproduce la obra impresa originalmente en México en **1732**. El testimonio digital de trabajo corresponde al ejemplar de John Carter Brown Library difundido por Internet Archive con identificador `vocabulariodelas00orte`.

[![CI](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml/badge.svg)](https://github.com/fersandovalgtz/cora-historico-digital/actions/workflows/qa.yml)

> **Estado científico: `0.1.0-dev`.** El corpus actual es un inventario computacional inicial. No se afirma validación filológica o lingüística humana independiente.

## Fuente y distinción obra/testimonio

CHD mantiene separados dos niveles documentales:

- **obra histórica:** José de Ortega, *Vocabulario en lengua castellana y cora*, México, 1732;
- **testimonio utilizado:** *Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano*, Tepic, Imprenta de Antonio Lagaspi, 1888.

La ficha de Open Library/Internet Archive señala que el vocabulario español-cora ocupa las páginas impresas **15–90**. En el PDF digital de 98 páginas, la página impresa 15 corresponde a la página física 19.

## Estado de la ingestión

| Dimensión | Estado `0.1.0-dev` |
|---|---:|
| páginas físicas del PDF | **98** |
| candidatos computacionales | **2,140** |
| candidatos con alineación automática de página | **2,105** |
| alineaciones secuenciales inferidas | **35** |
| revisión humana independiente | **0** |

Los **2,140 candidatos no equivalen todavía a 2,140 entradas históricas**. El OCR contiene pérdidas de separadores, cortes de línea, caracteres espurios y posibles fusiones de artículos; el censo definitivo requiere reconciliación contra página.

## Arquitectura de evidencia

```text
testimonio digital / facsímil
        ↓
OCR bruto preservado
        ↓
segmentación computacional de candidatos
        ↓
reconciliación contra evidencia de página
        ↓
artículos lexicográficos canónicos
        ↓
capas editoriales, procedencia e incertidumbre
        ↓
derivados reproducibles: CSV · JSONL · TEI Lex-0 · CLDF, cuando proceda
```

Tres reglas gobiernan el corpus: la fuente no se sobrescribe; la procedencia acompaña a cada transformación; la autoridad de una capa está tipada.

## Reproducibilidad

Los archivos binarios de fuente **no se versionan en Git**. El pipeline los descarga desde Internet Archive, registra URLs y SHA-256, produce el OCR y el inventario de candidatos y elimina los binarios antes de confirmar los derivados.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make ingest
make validate
```

La acción `bootstrap-corpus` ejecuta el mismo proceso en GitHub Actions.

## Datos

- `data/source/ocr/`: OCR completo y extracción por página;
- `data/source/source_manifest.json`: procedencia y hashes del testimonio descargado;
- `data/grammar/`: preliminares y advertencias lingüísticas del testimonio;
- `data/lexicon/candidates.csv` y `.jsonl`: inventario provisional;
- `data/appendices/`: numerales y materiales finales;
- `schemas/`: contratos de datos iniciales;
- `reports/`: métricas de ingestión reproducibles.

## Variedad histórica

Ortega distingue tres “ramos” del idioma y declara haber dispuesto el vocabulario según el habla de los **Ateacari**, vinculada por él con las orillas del río de Jesús María. CHD conserva esa afirmación como evidencia histórica del autor y **no asigna automáticamente una variedad o identificador lingüístico contemporáneo** a ese testimonio.

## Ruta científica

La prioridad siguiente es reconciliar los 2,140 candidatos contra las páginas del testimonio, detectar omisiones y fusiones, fijar artículos canónicos con identificadores persistentes `ORT1888-art-######` y solo después producir TEI Lex-0, CLDF u otras proyecciones interoperables.

## Licencias

Código: MIT. Metadatos, anotaciones y derivados originales de CHD: CC BY 4.0 salvo indicación contraria. El texto histórico es de dominio público; CHD no reclama autoría sobre la obra ni sobre la digitalización institucional.

## Citación

Mientras el proyecto permanezca en `0.1.0-dev`, cite el testimonio histórico y el commit utilizado. `CITATION.cff` fija la forma provisional de citar el repositorio; el DOI se incorporará al publicar una release archivada.
