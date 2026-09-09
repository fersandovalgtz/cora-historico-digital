# Informe de calidad inicial

La ingestión `0.1.0-dev` preserva el OCR bruto, registra hashes de la fuente descargada y genera derivados de manera reproducible.

El extractor produce **2,140 candidatos** y alinea automáticamente **2,105** con una página física del PDF mediante coincidencia normalizada del encabezamiento. **35** mantienen alineación secuencial inferida.

Riesgos conocidos: separadores perdidos o deformados por OCR, artículos fusionados, encabezamientos truncados, caracteres espurios, falsas fronteras y diferencias entre OCR ABBYY y texto extraíble del PDF.

Ninguna de estas métricas equivale a validación filológica. `human_verified` permanece en `false` para todos los candidatos.
