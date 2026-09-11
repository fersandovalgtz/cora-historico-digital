# Datos

- `source/`: testimonio, OCR y manifiesto de procedencia.
- `grammar/`: preliminares preservados.
- `lexicon/candidates.*`: hipótesis de segmentación del cuerpo alfabético.
- `lexicon/machine_lexicon.*`: resolución computacional exhaustiva de los candidatos.
- `appendices/*_ocr.txt`: OCR íntegro de los apéndices.
- `appendices/machine_inventory.json`: unidades automáticas de navegación de los apéndices.
- `appendices/numerals_machine.*`: 27 pares explícitos del apéndice numeral.
- `appendices/irregular_particles_machine.*`: 22 unidades documentales estructuradas del apéndice de verbos irregulares/partículas.

Las capas machine-only conservan `human_verified=false` como declaración de autoridad, no como trabajo pendiente. Los derivados específicos de cada apéndice conservan su OCR y su estructura documental sin convertirla en normalización lingüística.
