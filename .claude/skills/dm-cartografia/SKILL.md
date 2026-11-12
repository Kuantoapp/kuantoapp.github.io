---
description: Preparar y cruzar datos geográficos y dibujar mapas finales. CRS y reproyección (EPSG:25830 para medir, 4326 y 3857 para la web), uniones por código oficial (INE, municipal) y spatial joins, tablas de paso entre unidades (código postal, sección censal, barrio, distrito), distancias y áreas, y mapas coropléticos de presentación (clasificación, paleta, leyenda, cartogramas). Úsala al cargar geometrías con geopandas, unir tablas por zona, medir distancias o diseñar un mapa para la app o la presentación. No es para buscar patrones (dm-eda-espacial) ni para modelos (dm-modelado-espacial).
when_to_use: Leer un shapefile, GeoJSON o GeoParquet, comprobar o cambiar el CRS, hacer un merge o sjoin por municipio o sección, pasar datos de código postal a barrio, calcular distancias a servicios, generar teselas, elegir clasificación, colores y leyenda de un coroplético, averiguar por qué una unión pierde zonas.
---

# Cartografía y mapas

Base de cualquier análisis espacial: si la unión o el CRS fallan, todo lo que viene después (`dm-eda-espacial`, `dm-modelado-espacial`) es falso.

**Contexto del proyecto:** qué unidades, fuentes y mapas se usan lo decide el equipo y cambia con el desarrollo. Consúltalo en `docs/decisiones.md` y en `ideas/`; los ejemplos de esta skill son orientativos.

## CRS

- **ETRS89 / UTM 30N, EPSG:25830** (metros) para **medir** en la España peninsular: distancias, buffers, áreas, W por distancia. Fuera de ese huso, el EPSG correspondiente.
- **EPSG:4326** (grados) para guardar, intercambiar y servir a la web (MapLibre o Leaflet reproyectan a Web Mercator, EPSG:3857). Nunca para medir.
- Comprueba `gdf.crs` al cargar cada capa y reproyecta explícitamente. No asumas el CRS de un fichero; un shapefile sin `.prj` no tiene CRS conocido.
- No mezcles 25830 (ETRS89) con 32630 (WGS84 UTM) ni con 4258 sin reproyectar. Tabla de códigos, formatos y fuentes oficiales en [sistemas-y-fuentes.md](referencia/sistemas-y-fuentes.md).

## Identificadores y uniones

- Une por **código oficial**, nunca por nombre: INE de municipio (5 dígitos), sección censal (10 dígitos), códigos municipales de distrito y barrio. «Las Rozas de Madrid» y «Rozas de Madrid, Las» son el mismo municipio para una persona, pero no para un `merge`.
- Códigos como **texto**, con los ceros a la izquierda (`"28079"`, no `28079`).
- Usa el **mismo año** de cartografía que el dato: las secciones censales cambian.

## Tablas de paso

Códigos postales, secciones, barrios, distritos y zonificaciones de transporte no coinciden.

- Los **códigos postales** responden a la logística de Correos, no a un marco estadístico, y su cartografía no es oficial.
- Paso entre unidades: superposición de polígonos con **pesos** (viviendas o población de cada trozo, no área).
- Los pesos de cada origen suman 1 y el total se conserva tras el paso.
- El supuesto se declara en la nota metodológica.

## Mapas de presentación

- **Tasas o medias**, nunca absolutos: el ojo lee el área.
- **Clasificación** nombrada en la leyenda: cuantiles para comparar posiciones, cortes naturales para grupos homogéneos, intervalos iguales si la unidad tiene sentido propio, **punto medio** si hay un umbral con significado (0, un porcentaje de referencia). Los cuantiles fallan con mucha asimetría o empates; para colas largas, head/tail breaks o logaritmos.
- **Paleta** secuencial para magnitudes, **divergente** con punto medio con significado, cualitativa para categorías sin orden y **ordinal** para categorías con orden. Apta para daltónicos; el rojo, solo para lo que es una alerta.
- **Estimaciones marcadas** (trama o borde) con su intervalo accesible, y diferenciadas las zonas fuera del ámbito del modelo.
- **Cartograma** o símbolos graduados si las zonas grandes y poco pobladas dominan el mapa.
- Leyenda con unidad y método; fuente bajo el mapa; «© OpenStreetMap contributors» si se usa OSM.

Detalle de clasificaciones, paletas y trampas visuales en [mapas-de-presentacion.md](referencia/mapas-de-presentacion.md). Para mapas que sirven para explorar (caja, barajado, Bayes empírico), `dm-eda-espacial`.

## Razonar cada resultado

Después de cada carga, unión o paso entre unidades:

1. **Qué dice:** cuántas filas entran, cuántas salen, cuántas zonas quedan sin dato y cuántos datos sin zona.
2. **Si es fiable:** ¿el total de la variable se conserva? ¿Los pesos suman 1? ¿El CRS es el esperado? ¿Las áreas y distancias tienen magnitudes plausibles (un municipio no mide 0,003 ni 3 millones de km²)?
3. **Si es coherente:** el número de zonas coincide con el ámbito (por ejemplo, 179 municipios en la Comunidad de Madrid, 21 distritos en la capital); los códigos huérfanos tienen explicación (cambios de código, zonas sin población).
4. **Qué implica:** corregir antes de seguir. Una unión que pierde zonas en silencio invalida todo lo posterior.
5. **Registrarlo:** supuestos de las tablas de paso y zonas excluidas, en `docs/decisiones.md`.

En un mapa: compara al menos dos clasificaciones. Si el mensaje cambia mucho con la clasificación, el mapa engaña y hay que decirlo o cambiarlo.

## Python

| Tarea | Función |
|---|---|
| Cargar y reproyectar | `geopandas.read_file`, `read_parquet`, `gdf.to_crs(25830)` |
| Unión espacial y vecino más cercano | `geopandas.sjoin`, `sjoin_nearest(..., distance_col="d")` en metros |
| Superposición para tablas de paso | `geopandas.overlay(a, b, how="intersection")` |
| Clasificar | `mapclassify.Quantiles`, `NaturalBreaks`, `EqualInterval`, `HeadTailBreaks` |
| Mapa rápido | `gdf.plot(column=..., scheme="quantiles", legend=True)` |

En R (curso): `sf`, `st_transform`, `st_intersection`, `tmap`.
