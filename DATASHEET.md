# Datasheet del corpus

## Identidad

**Cora Histórico Digital (CHD)** es un corpus histórico-digital reproducible, actualmente publicado como **v0.1.0**, para estudiar un testimonio histórico de la lengua cora/náayeri preservando forma documental, procedencia, incertidumbre y separación entre evidencia fuente y transformación computacional.

## Motivación

Crear una infraestructura científica auditable para investigación en historia de la lexicografía, lingüística misionera, humanidades digitales y métodos computacionales aplicados a lenguas de bajos recursos, sin presentar resultados automáticos como validación filológica humana ni como descripción normativa del náayeri contemporáneo.

## Fuente histórica

La obra de referencia fue impresa originalmente en **México en 1732** como *Vocabulario en lengua castellana y cora. Dispuesto por el P. Joseph de Ortega, de la Compañia de Jesus*, de **José de Ortega**, por los **Herederos de la Viuda de Francisco Rodríguez Lupercio**.

CHD trabaja reproduciblemente sobre una **reimpresión de Tepic de 1888**, *Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano*, impresa por **Antonio Lagaspi**. El ejemplar digital canónico pertenece a la **John Carter Brown Library** y se distribuye mediante Internet Archive como `vocabulariodelas00orte` (`ark:/13960/t2t44qw20`). El registro institucional consigna procedencia de **Nicolás León** mediante ex libris.

Por tanto, CHD distingue explícitamente:

1. obra histórica original de 1732;
2. testimonio/reimpresión de 1888;
3. ejemplar físico de la John Carter Brown Library;
4. digitalización y objetos descargables de Internet Archive;
5. OCR, segmentaciones y derivados computacionales de CHD.

## Composición

El testimonio procesado incluye preliminares, vocabulario castellano→cora, numerales y notas finales sobre verbos y partículas. El cuerpo alfabético produce 2,140 candidatos computacionales; la capa machine-only vigente conserva 2,137 artículos aceptados, 2 artefactos rechazados y 1 candidato incierto. Los apéndices se mantienen como capas documentales separadas.

## Procesamiento

CHD usa OCR de Internet Archive y texto extraíble del PDF para segmentación y alineación. Los objetos digitales de origen se verifican mediante SHA-256 antes de generar derivados. La resolución es **machine-only**: los candidatos con evidencia reproducible suficiente reciben un artículo máquina; los demás permanecen explícitamente inciertos o rechazados por reglas documentadas. El pipeline no moderniza silenciosamente las formas históricas.

La capa alfabética se proyecta además a **TEI Lex-0 0.9.5** y **CLDF Dictionary**, con validación automática e invariantes de procedencia.

## Usos adecuados

Historia de la lexicografía y lingüística misionera; humanidades digitales; corpus históricos; investigación sobre reproducibilidad; docencia; análisis computacional de fuentes históricas y exploración metodológica en contextos de lenguas de bajos recursos.

## Usos no respaldados

No es un diccionario normativo contemporáneo, una edición crítica humana, una traducción validada, una fuente única para identificación dialectal moderna, un sustituto de trabajo comunitario ni una autoridad para corregir o estandarizar el náayeri actual.

## Límites epistemológicos

Los estados `machine_accepted`, `machine_uncertain` y `machine_rejected` expresan autoridad computacional, no consenso lingüístico. `human_verified=false` documenta que la validación humana no forma parte del repositorio; no identifica una tarea pendiente. Las estadísticas deben distinguir siempre OCR, candidatos, artículos máquina, apéndices y casos residuales.

## Procedencia y citación

La cadena completa está documentada en `PROVENANCE.md` y `data/source/source_manifest.json`. Los trabajos que utilicen CHD deben citar la release/versión consultada y, cuando el argumento dependa de material histórico, el testimonio de Ortega de 1888. Para cuestiones de historia editorial debe citarse también la impresión original de 1732.

Mientras no exista un DOI emitido por un archivador externo, CHD no declara uno. La referencia estable actual es la GitHub Release `v0.1.0`.
