# Fuente y derivados

El testimonio de trabajo es `ORTEGA1888-TEPIC-IA`, reimpresión de Tepic de 1888 de la obra impresa originalmente en México en 1732. Los binarios de fuente no se almacenan en Git: `scripts/ingest_ortega1888.py` los descarga desde Internet Archive, registra URLs y SHA-256 en `source_manifest.json`, genera el OCR por página y después pueden eliminarse sin perder reproducibilidad.
