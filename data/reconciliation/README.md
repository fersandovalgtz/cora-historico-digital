# Reconciliación

Este directorio contiene derivados y decisiones de la fase 2.

`review_queue.csv` se genera con `python scripts/build_reconciliation_queue.py`. Es una cola de priorización producida por máquina y, por tanto, conserva `human_verified=false`.

Las decisiones humanas de reconciliación deben almacenarse como registros separados que cumplan `schemas/reconciliation-decision.schema.json`. No se debe editar `data/lexicon/candidates.csv` para simular una corrección humana ni sobrescribir OCR de fuente.

La cola puede regenerarse en cualquier momento a partir de `data/lexicon/candidates.csv`; las decisiones humanas, en cambio, son evidencia editorial y deben conservar su procedencia.
