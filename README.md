# Cora Histórico Digital

**Cora Histórico Digital (CHD)** es un repositorio de investigación para convertir un testimonio histórico de la lengua cora en datos digitales trazables, versionados y reproducibles sin confundir OCR, segmentación computacional, edición filológica e interpretación lingüística.

La implementación inicial trabaja con el *Vocabulario de las lenguas castellana y cora* de José de Ortega a partir del testimonio reimpreso en Tepic en **1888**, que reproduce la obra impresa originalmente en México en **1732**. El testimonio digital de trabajo procede del ejemplar John Carter Brown Library difundido por Internet Archive, identificador `vocabulariodelas00orte` y ARK `ark:/13960/t2t44qw20`.

> **Estado 0.1.0-dev:** inventario computacional inicial. No se afirma validación filológica o lingüística humana independiente.

## Fuente y distinción obra/testimonio

CHD separa dos niveles que no deben colapsarse:

- **obra histórica:** José de Ortega, *Vocabulario en lengua castellana y cora*, México, 1732;
- **testimonio digital utilizado:** reimpresión de Tepic, Imprenta de Antonio Lagaspi, 1888, digitalizada por John Carter Brown Library / Internet Archive.

La catalogación de Internet Archive/Open Library sitúa el vocabulario bilingüe en las páginas impresas **15–90**. En el PDF suministrado para esta ingestión, la página impresa 15 corresponde a la página física 19 del archivo.

## Arquitectura de evidencia

```text
facsimil PDF / testimonio HTML
        ↓
OCR bruto preservado
        ↓
segmentación computacional de candidatos
        ↓
reconciliación contra página y evidencia visible
        ↓
artículos lexicográficos canónicos
        ↓
capas de revisión, procedencia e incertidumbre
        ↓
derivados reproducibles: CSV · JSONL · TEI Lex-0 · CLDF (si procede)
```

Una transformación de formato no eleva por sí misma la autoridad del dato. Un **candidato** no es todavía una entrada histórica canónica.

## Estado de la ingestión inicial

La primera pasada conservadora detectó **2,140 candidatos** en el cuerpo alfabético; **2,105** pudieron alinearse automáticamente con una página física del PDF mediante coincidencia del encabezamiento OCR y **35** conservan alineación secuencial inferida. Todos permanecen como `unreviewed_machine_candidate`; `human_verified = false`.

Estos números describen el rendimiento del extractor, **no** el número definitivo de artículos del vocabulario. El OCR contiene pérdidas de separadores, cortes de línea, caracteres espurios y fusiones de artículos que deberán reconciliarse contra la imagen de página.

## Estructura

- `data/source/original/`: archivos fuente suministrados, preservados sin edición;
- `data/source/ocr/`: OCR completo y extracción por página del PDF;
- `data/grammar/`: preliminares y advertencias gramaticales en OCR bruto;
- `data/lexicon/candidates.csv|jsonl`: inventario computacional provisional;
- `data/appendices/`: sistema numeral y verbos/partículas finales;
- `schemas/`: contratos de datos iniciales;
- `scripts/`: ingestión, validación y consulta;
- `reports/`: métricas reproducibles del procesamiento.

## Reproducibilidad rápida

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make ingest
make validate
```

`make ingest` regenera OCR derivado, candidatos, alineación de páginas e informe de ingestión desde los dos archivos originales conservados en `data/source/original/`.

## Principios editoriales

1. La fuente no se sobrescribe.
2. OCR, candidato, reconstrucción editorial y validación humana son estados distintos.
3. La ortografía histórica no se moderniza silenciosamente.
4. Las variantes y categorías descritas por Ortega se registran primero como afirmaciones del testimonio histórico; no se convierten automáticamente en taxonomía lingüística contemporánea.
5. La incertidumbre se conserva como dato.

## Ruta científica inmediata

La prioridad es reconciliar los comienzos de artículo, corregir fusiones y omisiones del OCR, generar artículos canónicos con spans de página y después exportar proyecciones interoperables. TEI Lex-0 y CLDF serán capas derivadas; ninguna sustituirá el objeto histórico canónico.

## Licencias

Código del proyecto: MIT. Datos y anotaciones creados por CHD: CC BY 4.0, salvo componentes de fuente que conservan su procedencia y régimen propio. La obra histórica es de dominio público; el repositorio no atribuye al proyecto autoría sobre el texto original ni sobre la digitalización institucional.

## Citación

La citación formal del proyecto se fijará al publicar la primera release archivada. Mientras `0.1.0-dev` permanezca en desarrollo, cite el testimonio histórico y el commit utilizado.
