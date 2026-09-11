# Release candidate `0.1.0`

Este directorio contiene controles de integridad para preparar la primera release científica de Cora Histórico Digital. **No implica que `0.1.0` haya sido publicada.** Mientras no exista un tag/release explícito, `CITATION.cff` y CodeMeta permanecen en `0.1.0-dev`.

## Alcance del manifiesto

`manifest.json` y `SHA256SUMS` se generan automáticamente con `scripts/build_release_manifest.py`. Cubren todos los archivos versionados bajo:

- `data/`;
- `reports/`;
- `schemas/`.

Se excluye deliberadamente `data/source/original/`: los binarios fuente externos no forman parte de la release y se verifican por separado mediante `data/source/source_lock.json`.

El manifiesto no incluye fecha de generación ni SHA de commit para que sea determinista respecto del conjunto de artefactos. El tag/commit de una release publicada proporciona la identidad de la versión de código.

## Gates antes de publicar

Una publicación `0.1.0` sólo debe realizarse después de que:

1. `qa` pase completo;
2. `bootstrap-corpus` reconstruya desde el testimonio bloqueado por checksum;
3. TEI Lex-0 valide contra el Relax NG oficial 0.9.5 fijado por SHA-256;
4. CLDF Dictionary pase `pycldf` / `cldf validate`;
5. el manifiesto y `SHA256SUMS` se regeneren y verifiquen sin diferencias;
6. `CITATION.cff`, `codemeta.json`, changelog y versión de release se actualicen de forma coordinada;
7. sólo entonces se cree un tag/release y, si se decide archivar en un repositorio con DOI, se incorpore el DOI real después de su asignación.

No debe inventarse ni reservarse en los metadatos un DOI no emitido.
