# Fase 3 — planificación de canonicalización

La fase 3 comienza únicamente después de cerrar la reconciliación humana de la fase 2. Su primera salida no es todavía un vocabulario corregido ni un conjunto de artículos lexicográficos finales: es un **plan determinista de materialización** que traduce decisiones humanas válidas a futuras unidades `ORT1888-art-######`.

## Barrera de entrada

`python scripts/plan_canonicalization.py` falla de forma cerrada mientras cualquiera de estas condiciones no se cumpla:

- todos los candidatos de `data/lexicon/candidates.csv` pertenecen exactamente a una decisión humana válida;
- ninguna decisión usa `defer_uncertain`;
- los órdenes de los candidatos son enteros positivos y únicos;
- una decisión `merge_candidates` sólo combina candidatos contiguos en el orden fuente;
- una decisión `split_candidate` propone por lo menos dos spans OCR no superpuestos y contenidos dentro del span OCR del candidato original.

La condición global se corresponde con `ready_for_canonicalization=true` en `reports/reconciliation_status.json`.

## Semántica del plan

El plan se escribe, por defecto, en `data/canonical/canonicalization_plan.json` y cumple `schemas/canonicalization-plan.schema.json`.

Las acciones de fase 2 se proyectan así:

- `accept_boundary` → una unidad `accepted_candidate`;
- `merge_candidates` → una unidad `merged_candidates` que conserva todos los IDs fuente;
- `split_candidate` → una unidad `candidate_span` por cada span humano propuesto, ordenada por línea OCR;
- `reject_false_boundary` → el candidato queda en `excluded_candidates` y no recibe ID de artículo;
- `defer_uncertain` → bloquea por completo la generación del plan.

Los IDs `ORT1888-art-######` se asignan sólo dentro de un plan listo, de forma secuencial y reproducible según el orden de los candidatos fuente. Una división produce IDs consecutivos dentro de la posición original del candidato.

## Alcance epistemológico

El plan es generado por máquina, pero deriva exclusivamente de decisiones que ya pasaron el validador humano (`human_verified=true`). Por ello declara simultáneamente `machine_generated=true` y `derived_from_human_verified_decisions=true`.

El plan **no corrige OCR, no normaliza grafías, no traduce, no decide límites y no construye todavía el texto canónico**. La materialización lexicográfica será un paso posterior y deberá conservar trazabilidad explícita hacia candidatos, decisiones y páginas fuente.

## Uso

```bash
make validate-reconciliation
make reconciliation-status
make canonicalization-plan
```

En el estado basal actual, con cobertura humana incompleta, el tercer comando debe fallar. Ese fallo es intencional y constituye una salvaguarda contra canonicalización prematura.
