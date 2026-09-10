# Hoja de ruta

## Fase 1 — ingestión reproducible — completada
Fuente, OCR, checksum lock, particiones, candidatos, alineación de páginas, schemas, CI y auditoría completa del testimonio.

## Fase 2 — resolución computacional — estabilizada
La capa alfabética cubre el 100 % de los 2,140 candidatos con estado explícito: **2,137 `machine_accepted`**, **2 `machine_rejected`** y **1 `machine_uncertain`**. Los rechazos preservan la evidencia fuente y la incertidumbre residual no bloquea la arquitectura.

Criterio de salida cumplido: cobertura computacional exhaustiva con autoridad tipada. **No existe criterio de revisión humana.** Nuevas reglas sólo se incorporarán cuando generalicen de forma reproducible y estén protegidas por pruebas negativas.

## Fase 3 — estructuración machine-only de apéndices — activa

### 3A. Numerales — completada
El apéndice numeral conserva su inventario OCR íntegro y añade una representación específica de **27 pares explícitos castellano–cora**: 22 de cuenta general, 3 de frecuencia y 2 de conteo animado. Los registros `ORT1888-num-###` no normalizan ni corrigen el OCR.

### 3B. Verbos irregulares y partículas — siguiente
Construir una representación que distinga ejemplos imperativos, expresiones, descripciones de partículas y prosa explicativa sin forzar este material al modelo del vocabulario alfabético.

## Fase 4 — interoperabilidad
Generar TEI Lex-0 y evaluar CLDF como vistas derivadas, conservando procedencia, autoridad computacional e incertidumbre. La representación deberá respetar que cuerpo alfabético, numerales y apéndice gramatical tienen estructuras diferentes.

## Fase 5 — release científica
Congelar contratos, ejecutar QA, publicar release archivada, DOI, citación estable, informe técnico-académico y sitio público de consulta. Una release puede contener `machine_uncertain` si queda declarado.

## Regla de inversión
El desarrollo adicional debe reutilizar la infraestructura histórico-digital existente y mantener bajo costo marginal. Integraciones o productos comerciales específicos sólo se priorizan ante una ruta verificable a evidencia académica, colaboración financiada, docencia reutilizable, consultoría, servicio gestionado u otra captura legítima de valor.
