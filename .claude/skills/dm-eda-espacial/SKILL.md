---
description: "Explora dónde hay patrón espacial en una variable territorial e interpreta el resultado con la teoría: matriz de pesos W, I de Moran global y local (LISA), Getis-Ord Gi*, Moran bivariante, correlograma, tasas con Bayes empírico, mapa de necesidad frente a recurso por municipio y patrones de puntos (Ripley, kernel). No hace mapas finales (dm-cartografia) ni estima efectos ni predice (dm-modelado-espacial)."
when_to_use: "¿Dónde hay mucha necesidad y poca ayuda (necesidad frente a recurso)?, ¿son fiables las tasas por 1.000 de zonas pequeñas?, ¿hay autocorrelación espacial?, ¿dónde están los clústeres o atípicos?, ¿esta W es razonable?, ¿a qué escala llega el patrón?, ¿es real o un artefacto?, qué significa este Moran."
---

# Exploración espacial (ESDA)

Método de la asignatura *Análisis de Datos Espaciales* (UCM), completado con Chasco (2025), Moura y Fonseca (2020) y Herrera-Gómez, en Python.

## Antes de empezar: conectar con el desarrollo del proyecto

Esta skill es general. Qué variable, unidad y pregunta se exploran sale del estado actual del proyecto; no lo supongas ni lo copies de los ejemplos.

1. **Qué se pregunta:** lee `docs/decisiones.md` (idea elegida, variables, unidad territorial) y, si hace falta, la ficha vigente en `ideas/`. Las fichas son borradores: manda lo decidido.
2. **Con qué datos:** lee `data/README.md` (fuentes, años, cobertura) y comprueba que las capas existen en `data/`.
3. **Qué hay ya hecho:** busca W, cargas y mapas existentes y reutilízalos:
   `grep -rnE "libpysal|weights|Queen|KNN|esda|Moran|mapclassify|pointpats" src notebooks`.
4. **Qué falta por decidir:** si la unidad o la variable no están claras, pregunta; si supones, escríbelo.
5. Requisito previo: datos unidos por código oficial y con el CRS correcto (`dm-cartografia`). Para modelizar después, `dm-modelado-espacial`.

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

## Contrastar cada resultado con la teoría

Un resultado solo se acepta cuando **coincide con lo que la teoría dice que debe salir**, o cuando la diferencia está explicada y comprobada:

1. **Antes de calcular**, escribe qué esperas (por la teoría del fenómeno y por el mapa): ¿agrupamiento positivo?, ¿a qué escala?, ¿dónde?
2. **Calcula** y compara con lo esperado y con los **valores de control** de abajo.
3. **Si no cuadra**, diagnostica con una comprobación concreta (W, islas, atípicos, tasas sin suavizar, unión mal hecha) antes de interpretar.
4. **Ajusta** solo lo que el diagnóstico señala y repite.
5. **Corrobora** por una segunda vía: otra W; Moran frente a Geary; LISA frente a Gi\*; mapa barajado frente al test.
6. **Acepta** solo si cuadra y es estable con esas variantes. Si no, se informa como resultado frágil.
7. **Registra** en `docs/decisiones.md` la W, la escala y lo que el ESDA implica para el modelo.

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Filas de W | Suman 1; ninguna zona sin vecinos sin tratar | W mal construida |
| I de Moran | Comparada con E[I] = −1/(n−1); con W normalizada, entre −1 y 1 aprox. | W o variable mal calculadas |
| Moran frente a Geary | Dirección coherente (I > E[I] ↔ C < 1) | Atípicos o W problemática: revisar antes de concluir |
| Suma de los Moran locales | Proporcional al global | Cálculo local erróneo |
| Tasa suavizada (Bayes empírico) | Entre la tasa cruda y la media global; se mueve más cuanto menor es la población | Población o eventos mal pasados |
| Correlograma | La I suele bajar al aumentar la distancia u orden | Si sube: tendencia o efecto frontera |
| Función L bajo aleatoriedad | ≈ 0, dentro de la envolvente | Ventana o intensidad mal definidas |

Guía completa de lectura y de qué hacer después: [interpretar-resultados.md](referencia/interpretar-resultados.md).

## Al terminar: dejar el trabajo conectado

- La W y las funciones de exploración reutilizables van a `src/`, para que el modelo use **la misma W** que el ESDA.
- Lo que el ESDA implica para el modelo (estructura espacial, escala del patrón, familia de modelo) se anota en `docs/decisiones.md`.
- Antes de dar un patrón por bueno o de abrir el PR, pide la revisión de `dm-revisor-espacial`.

## Errores a evitar

- LISA con FDR y pocas permutaciones: la FDR (Benjamini–Hochberg, `esda.fdr`) solo rechaza si hay k zonas con p ≤ k·α/n, y con un suelo p_min hacen falta al menos ⌈p_min·n/α⌉ zonas en el suelo. p_min = 3/(R+1) con `alternative='two-sided'` y 1/(R+1) con `'directed'` (el valor por defecto de `Moran_Local` en esda 2.10). Elige R para que un municipio aislado pueda salir (p_min < α/n): si no, «todo ns» puede ser un artefacto.
- `esda.Moran.p_sim` es unilateral, en la dirección del estadístico (no depende de `alternative`, que es de `Moran_Local`): para una p bilateral se dobla.
- Bayes empírico global con una zona que concentra la población (la capital): fija la media a priori; se calcula sin ella y se declara.
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
