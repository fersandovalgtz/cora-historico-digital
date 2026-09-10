# Fase 2 — banco de revisión humana por página

El banco de revisión por página reduce el costo operativo de revisar miles de límites candidatos sin convertir señales automáticas en decisiones humanas. Su unidad de inspección es la **página física del facsímil**, pero su unidad de decisión sigue siendo el **candidato individual**.

## Qué entra al banco

`render_page_review_facsimile.py` parte del inventario vigente y del conjunto validado de decisiones humanas. Incluye únicamente candidatos que:

- todavía no pertenecen a una decisión de reconciliación;
- tienen una página física válida;
- no conservan `page_alignment_status=inferred_sequence`.

Los candidatos `inferred_sequence` permanecen en el paquete especializado `phase2-facsimile-review`, porque una frontera entre páginas requiere comparar recortes y anclas vecinas y puede terminar en aceptación, rechazo, fusión, división o diferimiento.

Los candidatos `matched_headword` y `anchored_same_page` sí pueden presentarse en el banco general. La diferencia de estatus sigue visible para el revisor; ninguno se considera correcto por anticipado.

## Artefacto facsimilar

El renderizador descarga únicamente durante `bootstrap-corpus` el PDF bloqueado por checksum, genera una imagen completa por cada página que contenga candidatos pendientes y escribe `page_review_manifest.json`. El manifiesto conserva:

- SHA-256 del PDF fuente;
- página física e impresa;
- IDs y orden de candidatos;
- guía castellana y forma cora procedentes del OCR;
- span OCR crudo;
- estatus de alineación y confianza de extracción;
- candidatos ya reconciliados excluidos;
- candidatos inferidos excluidos.

El manifiesto declara `machine_generated=true`, `human_verified=false` y `facsimile_required=true`.

## Interfaz de revisión

`build_page_review_sheet.py` produce un HTML autocontenido que referencia las imágenes del mismo artefacto. El banco comienza con **todos los candidatos desmarcados y deshabilitados**.

Para habilitar los candidatos de una página, la persona revisora debe:

1. inspeccionar visualmente la página completa;
2. marcar la confirmación expresa de inspección personal;
3. seleccionar sólo los límites que efectivamente reconoce como artículos independientes.

Después puede exportar decisiones de esa página o de todas las páginas ya revisadas. Cada línea exportada es un registro independiente compatible con el contrato de reconciliación y contiene `human_verified=true` porque la interfaz sólo llega a esa construcción después de la confirmación humana explícita.

## Alcance deliberadamente limitado

La interfaz masiva sólo genera `accept_boundary`. No genera automáticamente:

- `reject_false_boundary`;
- `merge_candidates`;
- `split_candidate`;
- `defer_uncertain`.

Si un candidato no puede aceptarse con seguridad como límite independiente, se deja sin seleccionar y se resuelve después mediante el flujo individual o especializado. Esto evita que la eficiencia operativa diluya la calidad filológica.

## IDs y decisiones existentes

Los candidatos que ya aparecen en `data/reconciliation/decisions/` no se presentan nuevamente. Los IDs sugeridos `ORT1888-rec-######` se asignan evitando los números ya utilizados, pero sólo se vuelven decisiones reales cuando la persona guarda el JSONL y éste se incorpora posteriormente al directorio de decisiones.

La validación final sigue siendo obligatoria:

```bash
python scripts/validate_reconciliation_decisions.py
python scripts/summarize_reconciliation_status.py
```

## Ejecución

Con el PDF fuente disponible en su ruta de trabajo:

```bash
make render-page-review-facsimile
make page-review-sheet
```

En CI, `bootstrap-corpus` construye y publica el artefacto `phase2-page-review`, y elimina después los binarios fuente antes de cualquier commit. Las imágenes y el HTML de revisión no se versionan en el repositorio.

## Principio epistemológico

Agrupar candidatos por página es una optimización de interfaz, no una inferencia editorial. La confirmación de una página tampoco acepta automáticamente sus entradas: cada candidato debe quedar marcado de forma explícita antes de ser exportado como decisión humana.
