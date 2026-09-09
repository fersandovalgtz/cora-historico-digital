# Evidencia visual para la reconciliación de fronteras

Los candidatos que permanecen con `page_alignment_status=inferred_sequence` requieren cotejo visual contra el testimonio y no deben resolverse únicamente con texto OCR.

`scripts/render_inferred_facsimile.py` utiliza el PDF original descargado y previamente verificado contra `data/source/source_lock.json`. Para cada candidato no resuelto identifica los anclajes directos anterior y posterior, renderiza las páginas físicas implicadas y genera dos recortes orientados a la frontera: el tramo inferior de la página del anclaje anterior (`previous_tail`) y el tramo superior de la página del anclaje siguiente (`next_head`).

El manifiesto `facsimile_manifest.json` conserva el SHA-256 del PDF utilizado, la resolución de render, las páginas producidas y la relación de archivos con cada candidato. Todos los casos mantienen `human_verified=false` y `facsimile_required=true`; disponer de una imagen del facsímil no equivale a haber realizado la revisión humana.

En `main`, el workflow `bootstrap-corpus` construye el paquete antes de eliminar `data/source/original/` y lo publica durante 30 días como artefacto `phase2-facsimile-review`. El paquete incluye además `inferred_review_batch.json` e `inferred_review_batch.md`, de modo que la evidencia visual y la navegación textual quedan asociadas a la misma reconstrucción del corpus.

La revisión humana debe registrar su resultado exclusivamente mediante el esquema de decisiones de reconciliación. Las imágenes y observaciones de máquina son evidencia auxiliar, no una decisión editorial.
