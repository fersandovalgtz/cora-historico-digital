# Modelo de datos y contratos

```text
fuente / metadatos → OCR bruto → ORT1888-cand → resolución máquina → ORT1888-art / machine_uncertain → derivados
```

## Candidatos
`schemas/vocabulary-candidate.schema.json` modela las hipótesis de segmentación del cuerpo alfabético. `processing_status=machine_candidate`; `human_verified=false` declara autoridad, no una tarea pendiente.

## Capa de resolución
`schemas/machine-lexicon-record.schema.json` modela todos los candidatos tras la resolución computacional. `machine_status` admite `machine_accepted`, `machine_uncertain` y `machine_rejected`.

Sólo `machine_accepted` recibe `article_id`. El ID conserva el sufijo del candidato fuente: `ORT1888-cand-000042` → `ORT1888-art-000042`. Los huecos son válidos y evitan renumeración si cambia una clasificación.

## Apéndices
`ORT1888-numunit-###` y `ORT1888-irrunit-###` son IDs locales de navegación machine-only. No extienden ni renumeran `ORT1888-cand-######`.

Los productos interoperables deben regenerarse desde estas capas y conservar procedencia y autoridad.
