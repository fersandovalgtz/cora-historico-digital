# Hoja de ruta

## Fase 1 — ingestión reproducible — completada
Fuente, OCR, checksum lock, particiones, candidatos, alineación de páginas, schemas, CI y auditoría completa del testimonio.

## Fase 2 — resolución computacional — activa
Construir una capa exhaustiva sobre los 2,140 candidatos. Los casos con evidencia reproducible suficiente pasan a `machine_accepted`; los residuales permanecen `machine_uncertain`; futuras reglas podrán producir `machine_rejected` sin borrar el candidato fuente.

Criterio de salida: cobertura computacional del 100 % de candidatos con estado explícito. **No existe criterio de revisión humana.**

## Fase 3 — estructuración machine-only de apéndices
Pasar de unidades OCR de navegación a representaciones específicas para numerales y verbos/partículas sin forzarlas al modelo del vocabulario alfabético.

## Fase 4 — interoperabilidad
Generar TEI Lex-0 y evaluar CLDF como vistas derivadas, conservando procedencia, autoridad computacional e incertidumbre.

## Fase 5 — release científica
Congelar contratos, ejecutar QA, publicar release archivada, DOI, citación estable, informe técnico-académico y sitio público de consulta. Una release puede contener `machine_uncertain` si queda declarado.

## Regla de inversión
El desarrollo adicional debe reutilizar la infraestructura histórico-digital existente y mantener bajo costo marginal. Integraciones o productos comerciales específicos sólo se priorizan ante una ruta verificable a evidencia académica, colaboración financiada, docencia reutilizable, consultoría, servicio gestionado u otra captura legítima de valor.
