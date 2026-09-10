# Decisiones humanas de reconciliación

Este directorio contiene exclusivamente decisiones editoriales tomadas por una persona durante la fase 2. No almacena candidatos de máquina ni reemplaza el OCR fuente.

Cada decisión debe cumplir `schemas/reconciliation-decision.schema.json` y puede guardarse como un objeto `.json` o como una línea dentro de un archivo `.jsonl`. Los identificadores usan la forma `ORT1888-rec-######`.

Antes de confirmar cambios, ejecute:

```bash
python scripts/validate_reconciliation_decisions.py
python scripts/summarize_reconciliation_status.py
```

El validador comprueba, entre otras invariantes, que los candidatos existan, que las páginas físicas incluyan las páginas de los candidatos implicados, que las acciones de fusión y división tengan la cardinalidad esperada y que `human_verified` sea el booleano JSON `true`. Además, un candidato no puede pertenecer a más de una decisión de reconciliación: mientras el modelo no incluya una relación explícita de sustitución o supersesión, una segunda decisión sobre el mismo candidato se considera contradictoria y hace fallar la validación.

`reports/reconciliation_status.json` registra la cobertura acumulada. `decision_coverage_complete=true` significa que todos los candidatos pertenecen exactamente a una decisión humana válida. `ready_for_canonicalization=true` exige, además, que no quede ningún candidato con `defer_uncertain`.

En `main`, cualquier cambio bajo `data/reconciliation/decisions/**` activa el workflow `reconciliation-status`, que valida el conjunto completo y actualiza el reporte de cobertura sin volver a descargar ni procesar el testimonio fuente.

No se debe crear una decisión con `human_verified=true` a partir de inferencia automática. Esa marca documenta una revisión humana efectivamente realizada contra el testimonio.
