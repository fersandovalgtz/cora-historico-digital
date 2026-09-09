# Decisiones humanas de reconciliación

Este directorio contiene exclusivamente decisiones editoriales tomadas por una persona durante la fase 2. No almacena candidatos de máquina ni reemplaza el OCR fuente.

Cada decisión debe cumplir `schemas/reconciliation-decision.schema.json` y puede guardarse como un objeto `.json` o como una línea dentro de un archivo `.jsonl`. Los identificadores usan la forma `ORT1888-rec-######`.

Antes de confirmar cambios, ejecute:

```bash
python scripts/validate_reconciliation_decisions.py
```

El validador comprueba, entre otras invariantes, que los candidatos existan, que las páginas físicas incluyan las páginas de los candidatos implicados, que las acciones de fusión y división tengan la cardinalidad esperada y que `human_verified` sea el booleano JSON `true`.

No se debe crear una decisión con `human_verified=true` a partir de inferencia automática. Esa marca documenta una revisión humana efectivamente realizada contra el testimonio.
