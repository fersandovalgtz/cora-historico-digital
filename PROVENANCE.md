# Procedencia

Cora Histórico Digital distingue de forma explícita cinco niveles de procedencia: **obra histórica**, **testimonio bibliográfico**, **ejemplar físico**, **objeto digital** y **derivados computacionales**. Ninguno de esos niveles se trata como equivalente a los demás.

## Cadena de procedencia

```text
ORTEGA1732
obra histórica
        ↓ reimpresión
ORTEGA1888-TEPIC
        ↓ ejemplar conservado
John Carter Brown Library
        ↓ digitalización / distribución
Internet Archive: vocabulariodelas00orte
        ↓ objetos digitales bloqueados por SHA-256
PDF + DjVu TXT
        ↓
OCR/texto preservado → candidatos → resolución machine-only → derivados
```

## Obra histórica de 1732

La obra fue impresa originalmente en **México en 1732** con el título:

> *Vocabulario en lengua castellana y cora. Dispuesto por el P. Joseph de Ortega, de la Compañia de Jesus*.

Autor: **José de Ortega (1700–1768)**.  
Lugar: **México**.  
Impresor/editor: **Herederos de la Viuda de Francisco Rodríguez Lupercio**.  
Año: **1732**.

Este nivel se identifica conceptualmente como `ORTEGA1732`. CHD no afirma trabajar directamente sobre un ejemplar digital de esa impresión.

## Testimonio de trabajo de 1888

La implementación reproducible de CHD se basa en la reimpresión:

> *Vocabulario de las lenguas castellana y cora, reimpresso en Tepic, por orden del Sr. Gral. D. Leopoldo Romano*.

Autor: **José de Ortega**.  
Lugar: **Tepic**.  
Imprenta: **Imprenta de Antonio Lagaspi**.  
Año: **1888**.  
Identificador CHD: `ORTEGA1888-TEPIC-IA`.

La descripción de Internet Archive informa que esta reimpresión deriva de la obra de 1732 y conserva preliminares en español, vocabulario castellano-cora y materiales finales.

## Ejemplar físico y procedencia institucional

El ejemplar digitalizado pertenece a la **John Carter Brown Library**. El registro de Internet Archive consigna:

- signatura JCB: `B888 .O77v`;
- procedencia: **Nicolás León (1859–1929), ex libris/bookplate**;
- nota de ejemplar: copia imperfecta, aparentemente sin título de cubierta;
- referencias catalográficas: Palau y Dulcet y Backer-Sommervogel.

Estas notas describen el ejemplar físico y su historia de custodia; no son inferencias de CHD.

## Objeto digital canónico

- Institución de procedencia: John Carter Brown Library.
- Plataforma de acceso: Internet Archive.
- Identificador: `vocabulariodelas00orte`.
- ARK: `ark:/13960/t2t44qw20`.
- Registro público: <https://archive.org/details/vocabulariodelas00orte>.
- PDF: <https://archive.org/download/vocabulariodelas00orte/vocabulariodelas00orte.pdf>.
- DjVu TXT: <https://archive.org/download/vocabulariodelas00orte/vocabulariodelas00orte_djvu.txt>.

Cada ingestión verifica PDF y DjVu TXT contra `data/source/source_lock.json`. Una diferencia de SHA-256 detiene el pipeline antes de escribir derivados.

## Derivados computacionales

El OCR y el texto extraíble se conservan como evidencia de entrada. La segmentación en candidatos, la alineación de encabezamientos, la resolución `machine_accepted` / `machine_uncertain` / `machine_rejected` y las vistas TEI Lex-0 y CLDF son transformaciones computacionales trazables.

`machine_accepted` no significa cotejo humano ni validación filológica. CHD no contiene una etapa operativa de revisión humana y no corrige silenciosamente el testimonio histórico, el OCR ni las grafías derivadas.

## Regla de citación de la fuente

Cuando un resultado dependa de una forma o pasaje histórico, debe citarse el **testimonio de 1888** utilizado por CHD. Cuando el argumento trate sobre la historia editorial o la primera aparición de la obra, debe citarse además la **impresión de 1732**. La release de CHD se cita por separado como objeto computacional moderno.
