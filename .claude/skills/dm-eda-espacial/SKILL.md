---
description: Análisis exploratorio espacial (ESDA) e interpretación de sus resultados. Matriz de pesos W, I de Moran global y local (LISA), Getis-Ord Gi* (hotspots), Moran y LISA bivariantes, correlograma, mapas de caja, tasas suavizadas con Bayes empírico y patrones de puntos (K y L de Ripley, densidad kernel). Úsala para saber si una variable tiene patrón territorial, localizar clústeres o atípicos, construir o elegir una W, analizar ubicaciones de servicios o leer qué significa un Moran o un LISA. No es para mapas finales (dm-cartografia) ni para entrenar modelos (dm-modelado-espacial).
when_to_use: ¿Hay autocorrelación espacial?, ¿dónde están los clústeres alto-alto?, ¿esta W es razonable?, ¿son fiables las tasas de zonas pequeñas?, ¿los servicios están donde está la gente?, ¿a qué escala llega el patrón?, ¿qué modelo pide esta variable?, interpretar una salida de esda o pointpats.
---

# Exploración espacial (ESDA)

Método de la asignatura *Análisis de Datos Espaciales* (UCM), completado con Chasco (2025), Moura y Fonseca (2020) y Herrera-Gómez, en Python.

**Contexto del proyecto:** qué variables y unidades se exploran lo decide el equipo y cambia con el desarrollo. Consúltalo en `docs/decisiones.md` y en `ideas/`; los ejemplos de esta skill son orientativos.

Antes de explorar, los datos tienen que estar unidos por código oficial y con el CRS correcto (`dm-cartografia`). Para modelizar después, `dm-modelado-espacial`.

## Flujo

1. **Mapa de caja** de la variable: cuartiles más atípicos (bisagra 1,5). Revisa si los atípicos son errores de dato. Ver [mapas-exploratorios.md](referencia/mapas-exploratorios.md).
2. **Tasas de zonas pequeñas:** si la variable es una tasa y hay zonas con poca población, **suaviza con Bayes empírico** antes de buscar patrones.
3. **Mapa barajado:** el mismo mapa con los valores permutados entre zonas. Si el real no parece más agrupado, no hay patrón visual.
4. **W exógena:** contigüidad reina para polígonos; k vecinos si hay zonas muy desiguales o islas. **Normalizada por filas.** Revisa las islas. Prueba una segunda W. Ver [pesos-y-autocorrelacion.md](referencia/pesos-y-autocorrelacion.md).
5. **I de Moran global** con 999 permutaciones y su diagrama de dispersión.
6. **LISA** (solo significativos tras corregir comparaciones múltiples) y **Gi\*** para puntos calientes y fríos.
7. **Correlograma:** a qué distancia u orden deja de haber dependencia. Esa escala fija el tamaño de bloque de la validación espacial.
8. **Bivariante** cuando la pregunta cruza dos variables (por ejemplo, necesidad frente a recurso): Moran y LISA bivariantes.
9. **Antes de modelizar:** el tipo de variable decide la familia de modelo (una proporción no es una regresión lineal) y un diagrama con LOWESS dice si la relación es lineal. Ver [exploracion-multivariante.md](referencia/exploracion-multivariante.md).

Si el dato son **ubicaciones** (servicios, paradas, empresas) y no zonas, el método es otro: patrones de puntos, con la población como referencia y no la aleatoriedad completa. Ver [patrones-de-puntos.md](referencia/patrones-de-puntos.md).

## Patrones de uso habituales

| Pregunta | Técnica |
|---|---|
| ¿Esta variable tiene patrón territorial? | Moran global con dos W; LISA para ver dónde |
| ¿Dónde se concentra un problema? | LISA o Gi\*: los clústeres alto-alto son las zonas prioritarias |
| ¿Dónde hay mucha necesidad y poco recurso? | LISA bivariante necesidad frente a recurso, con tasas suavizadas |
| ¿Están los servicios donde está la población? | Intensidad observada frente a la esperada por población (Poisson no homogéneo) |
| ¿Qué tamaño de bloque uso para validar? | Correlograma |

## Razonar cada resultado

Ningún resultado se da por bueno sin estos cinco pasos:

1. **Qué dice:** el valor frente a su referencia (por ejemplo, I frente a E[I]) y su significación.
2. **Si es fiable:** ¿se mantiene con otra W, sin las zonas atípicas, con tasas suavizadas?
3. **Si es coherente:** con la teoría del fenómeno y con los mapas.
4. **Qué implica para lo siguiente:** estructura espacial y validación espacial en el modelo, W elegida, escala, familia de modelo.
5. **Registrarlo** en `docs/decisiones.md`.

Guía de lectura de Moran, LISA, Gi\*, bivariantes, tasas suavizadas, correlograma y funciones K y L: [interpretar-resultados.md](referencia/interpretar-resultados.md).

## Errores a evitar

- Moran o LISA con W sin normalizar, con islas sin tratar o con una W construida con la propia variable.
- Conclusiones que solo se sostienen con una W.
- Clústeres LISA sin corregir por comparaciones múltiples.
- Tasas de zonas diminutas sin suavizar: dominan los extremos.
- Concluir que los servicios «están agrupados» frente a aleatoriedad completa: siguen a la población.
- Tratar el LISA bivariante como causal.
- Quitar atípicos sin mirar si son errores de dato o fenómenos reales.

## Python

| Tarea | Función |
|---|---|
| W reina, k vecinos, distancia | `libpysal.weights.Queen.from_dataframe(gdf)`, `KNN.from_dataframe(gdf, k=5)`, `DistanceBand`; `w.transform = "r"`; `w.islands` |
| Retardo espacial | `libpysal.weights.lag_spatial(w, y)` |
| Moran global y local | `esda.Moran(y, w, permutations=999)`, `esda.Moran_Local(y, w)` |
| Getis-Ord local | `esda.G_Local(y, w, star=True)` |
| Bivariante | `esda.Moran_BV(x, y, w)`, `esda.Moran_Local_BV(x, y, w)` |
| Bayes empírico | `esda.smoothing.Empirical_Bayes(eventos, poblacion)`, `Spatial_Empirical_Bayes(eventos, poblacion, w)` |
| Mapa de caja, percentiles | `mapclassify.BoxPlot(y, hinge=1.5)`, `Percentiles` |
| Patrones de puntos | `pointpats` (`PointPattern`, funciones G, K, L con simulación) |

En R (curso): `spdep::poly2nb`, `nb2listw(style="W")`, `moran.mc`, `localmoran`, `localG`, `spatstat`. Comprueba la firma exacta en la versión instalada.
