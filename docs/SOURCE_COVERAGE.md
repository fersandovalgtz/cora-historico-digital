# Cobertura del testimonio Ortega 1888

El OCR completo se divide en cuatro intervalos contiguos y no superpuestos: preliminares, cuerpo alfabético, apéndice numeral y apéndice de verbos irregulares/partículas. `scripts/audit_source_coverage.py` exige que las particiones derivadas reproduzcan exactamente el intervalo correspondiente del OCR completo.

Los **2,140 `ORT1888-cand-######`** corresponden únicamente al cuerpo alfabético. Los apéndices no se fuerzan a ese modelo: conservan OCR completo y unidades machine-only independientes `ORT1888-numunit-###` y `ORT1888-irrunit-###`.

`make source-coverage` falla ante marcadores ausentes, fronteras desordenadas, deriva de una partición, discontinuidad de cobertura, candidatos fuera del cuerpo alfabético u orden no contiguo.

La auditoría es mecánica (`machine_generated=true`, `human_verified=false`). El repositorio no contiene etapa de revisión humana. La capa de resolución puede publicar incertidumbre explícita sin alterar ni borrar el testimonio fuente.
