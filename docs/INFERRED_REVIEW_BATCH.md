# Lote de revisión de alineaciones todavía inferidas

`scripts/build_inferred_review_batch.py` prepara un paquete reproducible para los candidatos que continúan con `page_alignment_status=inferred_sequence`.

El paquete no constituye una decisión editorial. Reúne el candidato, los anclajes directos anterior y posterior más próximos, las páginas físicas implicadas y extractos del texto obtenido del PDF. También añade señales descriptivas de máquina, pero conserva `human_verified=false` y `facsimile_required=true` en todos los casos.

Los extractos de texto sirven únicamente para navegación. Antes de registrar una acción de reconciliación debe inspeccionarse el facsímil del testimonio. Las únicas acciones admisibles continúan siendo `accept_boundary`, `merge_candidates`, `split_candidate`, `reject_false_boundary` y `defer_uncertain`.

El lote puede generarse localmente con:

```bash
make inferred-review-batch
```

CI lo publica, junto con la cola general de reconciliación, como `inferred_review_batch.json` e `inferred_review_batch.md` dentro del artefacto `phase2-reconciliation-review`.
