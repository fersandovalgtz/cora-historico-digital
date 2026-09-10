# Evidencia visual para la reconciliación de fronteras

Los candidatos que permanecen con `page_alignment_status=inferred_sequence` requieren cotejo visual contra el testimonio y no deben resolverse únicamente con texto OCR.

`scripts/render_inferred_facsimile.py` utiliza el PDF original descargado y previamente verificado contra `data/source/source_lock.json`. Para cada candidato no resuelto identifica los anclajes directos anterior y posterior, renderiza las páginas físicas implicadas y genera dos recortes orientados a la frontera: el tramo inferior de la página del anclaje anterior (`previous_tail`) y el tramo superior de la página del anclaje siguiente (`next_head`).

El manifiesto `facsimile_manifest.json` conserva el SHA-256 del PDF utilizado, la resolución de render, las páginas producidas y la relación de archivos con cada candidato. Todos los casos mantienen `human_verified=false` y `facsimile_required=true`; disponer de una imagen del facsímil no equivale a haber realizado la revisión humana.

## Hoja de revisión humana

`scripts/build_human_review_sheet.py` genera `review_sheet.html` a partir del manifiesto visual y del lote textual. La hoja es autocontenida: no carga bibliotecas, fuentes ni scripts remotos. Muestra los recortes de frontera, enlaza las páginas completas y conserva visibles las señales automáticas como evidencia no decisoria.

La exportación rápida se limita a `accept_boundary`, `reject_false_boundary` y `defer_uncertain`, porque cada una puede expresarse válidamente sobre un solo candidato. `merge_candidates` y `split_candidate` se muestran como acciones avanzadas, pero no se exportan automáticamente porque necesitan candidatos o spans adicionales.

La hoja no genera un registro con `human_verified=true` hasta que una persona escriba su nombre, elija una acción, proporcione una justificación y marque explícitamente que inspeccionó personalmente el facsímil. Los identificadores de decisión sugeridos se calculan evitando los que ya existan en `data/reconciliation/decisions/`.

## Publicación del paquete

En `main`, el workflow `bootstrap-corpus` construye el paquete antes de eliminar `data/source/original/` y lo publica durante 30 días como artefacto `phase2-facsimile-review`. El paquete incluye `inferred_review_batch.json`, `inferred_review_batch.md`, `facsimile_manifest.json`, las imágenes renderizadas y `review_sheet.html`, de modo que evidencia visual, navegación textual y captura de la decisión humana quedan asociadas a la misma reconstrucción del corpus.

La revisión humana debe registrar su resultado exclusivamente mediante el esquema de decisiones de reconciliación. Las imágenes, observaciones de máquina y la evaluación visual de un sistema automático son evidencia auxiliar, no una decisión editorial humana.
