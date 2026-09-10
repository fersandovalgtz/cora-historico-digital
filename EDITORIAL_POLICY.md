# Política editorial y de autoridad

CHD es un corpus histórico-digital por capas y **machine-only**. Su objeto es representar de forma auditable un testimonio histórico, no producir un diccionario normativo de cora/náayeri contemporáneo ni una edición crítica humana.

## Autoridad de capas

`source` → evidencia documental preservada.  
`ocr` → lectura automática o heredada.  
`candidate` → hipótesis computacional de segmentación.  
`machine_accepted` → candidato promovido por reglas reproducibles a artículo máquina.  
`machine_uncertain` → evidencia insuficiente; se conserva sin forzar artículo.  
`machine_rejected` → frontera descartada por una regla automática documentada.

`human_verified=false` puede conservarse para declarar explícitamente la ausencia de validación humana, pero no existe una ruta operativa para cambiar ese estado dentro del repositorio.

## Transformaciones

Ninguna transformación sobrescribe silenciosamente evidencia previa. Las formas históricas y OCR se conservan; futuras normalizaciones, lematizaciones o equivalencias modernas viven en campos derivados con procedencia y autoridad explícitas.

Los IDs de artículo reutilizan el sufijo numérico del candidato fuente para evitar renumeraciones masivas cuando cambie un estado computacional.

## Incertidumbre

La incertidumbre no bloquea una release machine-only. Un candidato puede permanecer `machine_uncertain` indefinidamente. Esa condición debe ser visible en reportes, datos y documentación y nunca reinterpretarse como validación filológica.

## Variedad histórica y contexto colonial

Las clasificaciones de Ortega se conservan como afirmaciones históricas de la fuente y no se convierten automáticamente en taxonomía sociolingüística contemporánea. La preservación de categorías misioneras o coloniales no implica su adopción por el proyecto.
