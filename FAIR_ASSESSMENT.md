# Autoevaluación FAIR

**Findable.** CHD dispone de repositorio público, release versionada `v0.1.0`, `CITATION.cff`, CodeMeta, metadatos bibliográficos de la obra y del testimonio, identificador estable del objeto fuente en Internet Archive y documentación explícita de procedencia. La mejora principal aún pendiente es el depósito en un archivador externo con identificador persistente/DOI. No se registra ni anticipa un DOI hasta que exista realmente.

**Accessible.** Los derivados se distribuyen en formatos abiertos y la release pública fija un snapshot científico reproducible. El facsímil permanece accesible mediante John Carter Brown Library / Internet Archive; el testimonio de trabajo se descarga reproduciblemente y se verifica por checksum. Los binarios fuente externos no se redistribuyen como si fueran producción propia de CHD.

**Interoperable.** CSV, JSONL y JSON Schema conviven con dos vistas derivadas formalmente validadas del cuerpo alfabético: **TEI Lex-0 0.9.5** y **CLDF Dictionary**. TEI se valida contra el Relax NG oficial fijado por checksum; CLDF se valida mediante `pycldf` / `cldf validate`. Ninguna vista sustituye los modelos internos ni promueve los tres candidatos residuales a entradas válidas.

**Reusable.** Licencias, procedencia, autoridad computacional, incertidumbre explícita, source lock, auditorías, pipeline reproducible, manifiesto de release y checksums SHA-256 acompañan a los datos. `human_verified=false` describe la naturaleza machine-only de la capa; no representa una tarea pendiente ni una deficiencia que deba resolverse para una release computacional.

## Trazabilidad bibliográfica

La reutilización distingue la obra original de **1732**, la reimpresión/testimonio de **1888**, el ejemplar de la **John Carter Brown Library**, el objeto digital de **Internet Archive** y los derivados modernos de CHD. Esta separación evita atribuir al proyecto la digitalización institucional o presentar la reimpresión de 1888 como si fuera físicamente la impresión de 1732.

## CARE y límites de uso

La evaluación FAIR no sustituye consideraciones **CARE** ni autoriza usos normativos, comunitarios o sociolingüísticos que el corpus histórico no respalda. La apertura técnica de un testimonio histórico no convierte automáticamente sus categorías coloniales o misioneras en descripciones contemporáneas legítimas de comunidades, identidades o variedades lingüísticas.

## Pendiente verificable

El único salto infraestructural importante pendiente para preservación/citación es un depósito externo con DOI real. Ese paso debe ampliar persistencia y descubribilidad, no reabrir el corpus ni añadir trabajo manual permanente.
