# Modelo de datos y contratos

CHD usa un modelo por capas. Los objetos canónicos futuros conservarán evidencia y autoridad; los productos derivados deberán regenerarse desde esas capas.

```text
fuente / metadatos
        ↓
OCR bruto
        ↓
candidatos de frontera
        ↓
artículos históricos canónicos
        ↓
revisión y procedencia
        ↓
derivados interoperables
```

## `vocabulary-candidate.schema.json`

Modela los candidatos de `0.1.0-dev`: identificador persistente provisional, orden, testimonio, página física e impresa, estado de alineación, líneas OCR, encabezamiento castellano, forma cora OCR, span bruto, tipo de separador, confianza de extracción, estado de revisión y `human_verified`.

## `lexical-article.schema.json`

Reserva el contrato de los futuros artículos reconciliados `ORT1888-art-######`. Un candidato no debe promoverse a artículo únicamente por haber sido extraído por software.

## Identificadores

- candidatos: `ORT1888-cand-######`;
- artículos canónicos futuros: `ORT1888-art-######`.

Los IDs publicados no deben reciclarse para entidades diferentes.
