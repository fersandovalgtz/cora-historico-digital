# Autoevaluación FAIR inicial

**Findable.** Repositorio público, metadatos bibliográficos, identificador de fuente, `CITATION.cff` y CodeMeta. La principal mejora pendiente es publicar una release archivada con identificador persistente/DOI; no se registra un DOI hasta que exista realmente.

**Accessible.** Los derivados se distribuyen en formatos abiertos; el facsímil permanece accesible en Internet Archive y el testimonio de trabajo se descarga reproduciblemente con verificación de checksum. Los binarios fuente externos no se incluyen en la release del proyecto.

**Interoperable.** CSV, JSONL y JSON Schema conviven con dos vistas derivadas formalmente validadas del cuerpo alfabético: **TEI Lex-0 0.9.5** y **CLDF Dictionary**. TEI se valida contra el Relax NG oficial fijado por checksum; CLDF se valida mediante `pycldf` / `cldf validate`. Ninguna vista sustituye los modelos internos ni promueve los tres candidatos residuales a entradas válidas.

**Reusable.** Licencias, procedencia, autoridad computacional, incertidumbre explícita, source lock, auditorías y pipeline reproducible acompañan a los datos. `human_verified=false` describe la naturaleza machine-only de la capa; no representa una tarea pendiente ni una deficiencia que deba resolverse para una release computacional. El release candidate `0.1.0` añade un manifiesto determinista y checksums SHA-256 de `data/`, `reports/` y `schemas/`.

La evaluación FAIR no sustituye consideraciones CARE ni autoriza usos normativos, comunitarios o sociolingüísticos que el corpus histórico no respalda.
