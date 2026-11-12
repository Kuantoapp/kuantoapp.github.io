# Mapas para explorar (no para presentar)

Los mapas de presentación están en la skill `dm-cartografia`. Estos sirven para **descubrir** patrones y atípicos.

- **Mapa de caja (box map):** seis clases, los cuartiles más los atípicos inferiores y superiores (bisagra de 1,5 o 3 veces el rango intercuartílico). Es el mejor primer mapa para ver valores extremos (Chasco, 2025, con ejemplos de Madrid).
- **Mapa de percentiles** (1, 10, 50, 90, 99) y **mapa de desviaciones típicas:** alternativas para ver colas.
- **Mapa barajado:** el mismo mapa con los valores permutados al azar entre zonas. Si el real «parece» igual de agrupado, no hay patrón visual. Es la intuición detrás del test de permutaciones de la I de Moran.
- **Tasas de zonas con poca población** (municipios pequeños, zonas rurales): son inestables y dominan los extremos. **Bayes empírico**, global o espacial, acerca cada tasa a la media, más cuanto menor es su población. Explora con la tasa suavizada y guarda la cruda.
- **Variables discretas** (zona tarifaria, tipo de municipio): mapa de valores únicos y **mapa de co-localización** para ver dónde coinciden categorías de dos variables.
- **Mapas condicionales:** se divide una variable condicionante en intervalos y se dibuja un mapa de la variable de interés para cada uno. Muestra relaciones antes de modelizar.
- **Correlograma espacial:** la I de Moran para órdenes de vecindad o distancias crecientes. Indica hasta dónde llega la dependencia, y sirve para elegir el tamaño de bloque de la validación en `dm-modelado-espacial`.
