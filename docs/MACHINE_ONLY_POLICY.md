# Política machine-only

Desde el 10 de septiembre de 2026, Cora Histórico Digital funciona como un corpus histórico-digital íntegramente computacional. El pipeline no contiene ni espera revisión humana.

La autoridad de cada salida se declara como computacional. Los casos que no puedan resolverse de manera reproducible se conservan como `machine_uncertain`; no bloquean por sí mismos el cierre técnico del corpus y no se presentan como validaciones filológicas o lingüísticas humanas.

## Principios

1. La fuente y el OCR se preservan sin sobrescritura silenciosa.
2. Cada transformación conserva trazabilidad hacia candidato, página y span fuente.
3. `machine_accepted`, `machine_uncertain` y `machine_rejected` describen decisiones computacionales reproducibles.
4. `human_verified=false` puede conservarse como declaración epistemológica, pero no existe una ruta operativa para promover ese campo.
5. Una release computacional puede contener incertidumbre explícita.
6. El proyecto no se describe como edición crítica humana ni como norma del náayeri contemporáneo.

La calidad se sostiene mediante checksum lock de la fuente, auditorías de cobertura, esquemas, invariantes, pruebas unitarias y CI reproducible.
