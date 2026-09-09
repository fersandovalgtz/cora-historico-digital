# Alineación conservadora de guías cortas

La alineación directa general usa una clave normalizada de cuatro o más caracteres para evitar falsos positivos por subcadenas breves. Sin embargo, algunas guías castellanas legítimas de dos o tres letras quedan fuera de esa regla.

Para esos casos se admite una segunda ruta estricta sólo cuando concurren todas estas condiciones: la guía tiene entre dos y tres letras, contiene únicamente caracteres alfabéticos, el candidato fue extraído mediante raya tipográfica (`em_dash`) y la misma guía aparece al inicio de una línea del texto extraído de la página seguida inmediatamente por puntuación opcional y una raya tipográfica.

La regla no se aplica a entradas de una sola letra, fragmentos con símbolos OCR ni separadores por guion. Tampoco busca la guía como subcadena en cualquier posición. Su propósito es recuperar evidencia directa de página sin ampliar de forma insegura el emparejamiento de cadenas cortas.
