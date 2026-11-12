---
description: Análisis exploratorio de datos espaciales (ESDA) del proyecto. Matrices de pesos W, I de Moran global y local (LISA), Getis-Ord, Moran y LISA bivariantes, mapas exploratorios (caja, percentiles, mapa barajado) y tasas suavizadas con Bayes empírico. Úsala al explorar cómo se reparte una variable por municipios, barrios o secciones, al buscar clústeres o atípicos territoriales, o al construir una W.
when_to_use: Ver si la sobrecarga o lo que sobra tiene patrón territorial, localizar clústeres alto-alto para la vista de la Administración, cruzar sobrecarga con ayudas del Bono, revisar tasas de municipios pequeños, elegir la W que luego usará un modelo.
---

# Exploración espacial (ESDA)

Método de la asignatura *Análisis de Datos Espaciales* (UCM), completado con Chasco (2025) y Moura y Fonseca (2020), en Python. Parte del jurado conoce este método: nómbralo bien (W, I de Moran, LISA).

Antes de explorar, los datos tienen que estar unidos por código oficial y en EPSG:25830: ver la skill `dm-cartografia`. Para modelizar después, `dm-modelado-espacial`.

## Flujo

1. **Mapa de caja** de la variable: cuartiles más atípicos (bisagra 1,5). Es el primer mapa: enseña los extremos. Ver [mapas-exploratorios.md](referencia/mapas-exploratorios.md).
2. **Tasas de zonas pequeñas:** si la variable es una tasa y hay municipios con poca población, **suaviza con Bayes empírico** antes de mirar patrones.
3. **Mapa barajado:** el mismo mapa con los valores permutados entre zonas. Si el real no parece más agrupado, no hay patrón visual.
4. **W:** contigüidad reina para polígonos; k vecinos si hay zonas muy desiguales o islas. **Normalizada por filas.** Revisa `w.islands`. Prueba una segunda W y comprueba que las conclusiones se mantienen. Ver [pesos-y-autocorrelacion.md](referencia/pesos-y-autocorrelacion.md).
5. **I de Moran global** con 999 permutaciones y su diagrama de dispersión.
6. **LISA:** clústeres alto-alto, bajo-bajo y atípicos espaciales, solo los significativos. Con muchas zonas, umbral más estricto o FDR. **Gi\*** para puntos calientes y fríos.
7. **Bivariante** cuando la pregunta cruza dos variables: Moran y LISA bivariantes.

## Aplicación a «¿Me sobra?»

| Pregunta | Técnica |
|---|---|
| ¿«Lo que sobra» tiene patrón territorial? | Moran global por municipio; LISA para ver dónde |
| ¿Dónde están los hogares sobrecargados? | LISA de la sobrecarga por sección censal: los alto-alto son las zonas a señalar |
| ¿Dónde hay mucha sobrecarga y poca ayuda? (decisión 6.2.1) | **LISA bivariante** sobrecarga frente a tasa de solicitudes aceptadas del Bono, con tasas suavizadas |
| ¿Hay municipios con valores raros? | Mapa de caja antes de modelizar; revisar si son errores de dato |

## Errores a evitar

- Moran o LISA con W sin normalizar o con islas sin tratar.
- Leer clústeres LISA sin corregir por comparaciones múltiples.
- Tasas de municipios diminutos sin suavizar: dominan los extremos.
- Tratar el LISA bivariante como causal: es exploratorio y no controla la autocorrelación de cada variable.

## Python

| Tarea | Función |
|---|---|
| W reina, k vecinos, distancia | `libpysal.weights.Queen.from_dataframe(gdf)`, `KNN.from_dataframe(gdf, k=5)`, `DistanceBand`; `w.transform = "r"` |
| Retardo espacial | `libpysal.weights.lag_spatial(w, y)` |
| Moran global y local | `esda.Moran(y, w, permutations=999)`, `esda.Moran_Local(y, w)` |
| Getis-Ord local | `esda.G_Local(y, w, star=True)` |
| Bivariante | `esda.Moran_BV(x, y, w)`, `esda.Moran_Local_BV(x, y, w)` |
| Bayes empírico | `esda.smoothing.Empirical_Bayes(eventos, poblacion)`, `Spatial_Empirical_Bayes(eventos, poblacion, w)` |
| Mapa de caja, percentiles | `mapclassify.BoxPlot(y, hinge=1.5)`, `Percentiles` |

En R (curso): `spdep::poly2nb`, `nb2listw(style="W")`, `moran.mc`, `localmoran`, `localG`. Comprueba la firma exacta en la versión instalada.
