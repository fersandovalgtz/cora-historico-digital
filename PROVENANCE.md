# Procedencia

## Cadena documental

`ORTEGA1732` (obra impresa) → `ORTEGA1888-TEPIC-IA` (reimpresión/testimonio) → digitalización John Carter Brown Library / Internet Archive → OCR y texto extraíble → candidatos computacionales → futuras capas editoriales.

## Identificador del testimonio

- Internet Archive: `vocabulariodelas00orte`
- PDF: `https://archive.org/download/vocabulariodelas00orte/vocabulariodelas00orte.pdf`
- texto completo/OCR: `https://archive.org/stream/vocabulariodelas00orte/vocabulariodelas00orte_djvu.txt`

Cada ejecución de `scripts/ingest_ortega1888.py` registra los SHA-256 efectivamente descargados en `data/source/source_manifest.json` y `reports/ingest_report.json`.

## Actividad inicial

La ingestión separa preliminares, cuerpo lexicográfico, numerales y materiales finales mediante anclas documentales; genera candidatos a inicio de artículo y alinea encabezamientos con texto extraído del PDF. Una coincidencia automática de encabezamiento no equivale a cotejo visual ni a validación filológica.

No se afirma en `0.1.0-dev` revisión humana independiente, equivalencia lingüística moderna, normalización ortográfica autorizada ni identidad dialectal contemporánea.
