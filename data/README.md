# Datos

- `source/`: testimonio, OCR y manifiesto de procedencia.
- `grammar/`: preliminares preservados.
- `lexicon/candidates.*`: hipótesis de segmentación del cuerpo alfabético.
- `lexicon/machine_lexicon.*`: resolución computacional exhaustiva de los candidatos.
- `appendices/*_ocr.txt`: OCR íntegro de los apéndices.
- `appendices/machine_inventory.json`: unidades automáticas de navegación de los apéndices.
- `appendices/numerals_machine.*`: 27 pares explícitos del apéndice numeral.
- `appendices/irregular_particles_machine.*`: 22 unidades documentales estructuradas del apéndice de verbos irregulares/partículas.
- `interoperability/ortega1888_tei_lex0.xml`: proyección TEI Lex-0 0.9.5 del cuerpo alfabético, validada contra el Relax NG oficial fijado por checksum.
- `interoperability/cldf/Dictionary-metadata.json`: metadata de la proyección CLDF Dictionary.
- `interoperability/cldf/entries.csv`: 2,137 artículos `machine_accepted` como entradas castellanas (`spa`).
- `interoperability/cldf/senses.csv`: 2,137 filas uno-a-uno que preservan el `cora_ocr` completo como descripción `crn` sin segmentación semántica automática.
- `interoperability/cldf/languages.csv`: declaración de `spa` y `crn`.
- `interoperability/cldf/residuals.csv`: 2 `machine_rejected` y 1 `machine_uncertain`, preservados como evidencia CSVW no léxica.
- `interoperability/cldf/sources.bib`: bibliografía del testimonio Ortega 1888 utilizada por la vista CLDF.

Las capas machine-only conservan `human_verified=false` como declaración de autoridad, no como trabajo pendiente. Los derivados específicos de cada apéndice conservan su OCR y su estructura documental sin convertirla en normalización lingüística. TEI Lex-0 y CLDF Dictionary son vistas regenerables: ninguna sustituye `lexicon/machine_lexicon.*` ni convierte incertidumbre residual en entradas válidas.
