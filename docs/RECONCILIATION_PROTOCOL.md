# Protocolo de reconciliación de fronteras

## Propósito

La fase 2 de Cora Histórico Digital (CHD) determina si cada frontera detectada por el extractor corresponde efectivamente a un artículo lexicográfico del testimonio de 1888. El objetivo no es modernizar ni normalizar el texto, sino reconciliar la segmentación computacional con la evidencia de página.

La unidad de trabajo inicial sigue siendo el **candidato computacional** `ORT1888-cand-######`. Ningún candidato se convierte por esta sola fase en artículo canónico `ORT1888-art-######`.

## Principio de autoridad

La cola de revisión es una ayuda de priorización generada por máquina. Su puntuación no tiene autoridad filológica ni lingüística. Las decisiones de reconciliación requieren inspección humana del testimonio y se registran por separado con `schemas/reconciliation-decision.schema.json`.

El OCR, `candidates.csv` y los demás objetos de procedencia se conservan sin sobrescritura. Una corrección editorial debe quedar expresada como una nueva capa trazable.

## Orden de revisión

`scripts/build_reconciliation_queue.py` genera una cola determinista a partir de señales ya presentes en el corpus. Se revisan primero los casos con mayor riesgo estructural:

1. alineación de página inferida secuencialmente;
2. confianza de extracción baja o media;
3. múltiples separadores detectados;
4. spans multilínea, especialmente los extensos;
5. artefactos superficiales de OCR que puedan ocultar una frontera.

Los casos sin señales de riesgo también permanecen en la cola como revisión basal. El puntaje sirve únicamente para ordenar trabajo.

## Acciones admisibles

Cada decisión humana utiliza una de las siguientes acciones:

- `accept_boundary`: la frontera propuesta es compatible con la evidencia de página;
- `merge_candidates`: dos o más candidatos forman un solo artículo histórico;
- `split_candidate`: un candidato contiene dos o más artículos que deben separarse;
- `reject_false_boundary`: la frontera computacional no corresponde a un artículo;
- `defer_uncertain`: la evidencia disponible no permite decidir todavía.

`merge_candidates` y `split_candidate` deben especificar los candidatos afectados y, cuando proceda, los spans OCR propuestos. Ninguna de estas acciones autoriza por sí sola normalizaciones ortográficas, morfológicas o semánticas.

## Evidencia mínima

Toda decisión debe registrar:

- identificador de decisión `ORT1888-rec-######`;
- candidato o candidatos involucrados;
- página física del PDF y, cuando esté disponible, página impresa;
- persona revisora;
- fecha y hora de revisión;
- acción tomada;
- justificación breve basada en evidencia observable;
- `human_verified=true` únicamente para la decisión efectivamente realizada por una persona.

La marca `human_verified=true` pertenece al registro de decisión, no retroactivamente al OCR ni al candidato computacional.

## Criterios de frontera

La revisión debe atender, al menos, a la disposición tipográfica, continuidad de líneas, puntuación, separadores, secuencia alfabética, sangrías, cambios de guía castellana y continuidad de la forma cora. Ninguno de estos indicios funciona aisladamente como regla automática.

Cuando el OCR contradiga el facsímil, prevalece el facsímil como evidencia documental. Cuando la lectura del facsímil sea ambigua, debe conservarse la incertidumbre mediante `defer_uncertain` o una nota explícita.

## Producto de la fase 2

La fase se considera suficientemente madura para pasar a artículos canónicos cuando todos los candidatos hayan recibido una decisión o estén explícitamente diferidos, las fusiones y divisiones hayan sido reconciliadas de forma consistente y exista un mapa trazable entre candidatos de máquina y unidades editoriales propuestas.

Solo entonces puede iniciarse la asignación estable de identificadores `ORT1888-art-######` y la modelación lexicográfica de la fase 3.
