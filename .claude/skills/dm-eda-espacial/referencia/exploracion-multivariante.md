# Exploración antes de modelizar

Basado en Chasco (2025) y en el tema 6 del curso. El ESDA no es solo describir: sirve para **elegir el modelo** que viene después en `dm-modelado-espacial`.

## Qué modelo sugiere cada tipo de variable

| Variable objetivo | Exploración | Familia de modelo espacial |
|---|---|---|
| Continua (precio en €, un saldo) | Histograma, mapa de caja, Moran | Regresión espacial lineal o ML con retardos |
| **Tasa o proporción** (% de hogares que superan un umbral, tasa de aceptación de una ayuda) | Mapa de la tasa cruda, **mapa de exceso de riesgo**, tasa suavizada con Bayes empírico | Modelos para respuestas en [0, 1]: regresión beta o de respuesta fraccional espacial |
| Binaria («le llega / no le llega») | Mapa de valores únicos, co-localización | Logit o probit espacial |
| Recuento (número de solicitudes) | Mapa de la tasa, no del recuento | Poisson o binomial negativa con exposición |
| Serie temporal por zona (varios años) | Caja por año, mapa por año, dispersión con el retardo temporal | Paneles espaciales |

**Mapa de exceso de riesgo:** cociente entre lo observado y lo esperado si toda la región tuviera la tasa media. > 1 = exceso; < 1 = déficit. Por ejemplo, solicitudes de una ayuda observadas frente a las esperadas por la población destinataria.

## Relaciones entre variables

- **Diagrama de dispersión con LOWESS** (regresión local) en lugar de solo la recta: muestra no linealidades y cambios de régimen. Si aparecen, el modelo no debe ser lineal (encaja con Montero et al.).
- **Matriz de diagramas de dispersión** con variables estandarizadas: equivale visualmente a la matriz de correlaciones y ayuda a ver colinealidad entre explicativas.
- **Gráfico de coordenadas paralelas:** cada zona es una línea que cruza un eje por variable. Las líneas que van juntas son grupos de zonas parecidas; las sueltas, atípicos multivariantes. Útil para comparar zonas en varias dimensiones a la vez.
- **Vistas enlazadas:** seleccionar puntos en un gráfico y verlos en el mapa (lo hace GeoDa; en Python, `folium` o `plotly` con selección). Para explorar, no para presentar.

## Atípicos

Un atípico en el mapa de caja puede ser un fenómeno real o un **error de dato**. Antes de quitarlo, mira su origen. Si es un error, se corrige o se excluye y se documenta. Si es real, se queda y se dice.
