---
description: Datos geográficos y mapas del proyecto. Sistemas de referencia (EPSG:25830 para medir, EPSG:4326 para la web), uniones por código oficial INE y municipal, tablas de paso de código postal a barrio o sección, y mapas coropléticos para la demo (clasificación, paleta, leyenda, marca «estimado», cartogramas). Úsala al cargar o cruzar geometrías, calcular distancias o áreas, construir una tabla de paso o dibujar un mapa en la app o en el pitch.
when_to_use: Cargar municipios, barrios o secciones censales, unir una fuente por municipio, pasar el alquiler por código postal a barrio, calcular distancias a polos o servicios, preparar las teselas del mapa, elegir colores y leyenda del coroplético de la demo.
---

# Cartografía y mapas

Base de cualquier análisis espacial del proyecto: si la unión o el CRS fallan, todo lo que viene después (`dm-eda-espacial`, `dm-modelado-espacial`) es falso.

## CRS

- **ETRS89 / UTM 30N, EPSG:25830** (metros) para **medir**: distancias, buffers, áreas, W por distancia.
- **EPSG:4326** (grados) para guardar, intercambiar y servir a MapLibre, que reproyecta a Web Mercator (EPSG:3857). Nunca para medir.
- Comprueba `gdf.crs` al cargar cada capa y reproyecta explícitamente con `gdf.to_crs(25830)`. No asumas el CRS de un fichero; un shapefile sin `.prj` no tiene CRS conocido.
- No mezcles 25830 (ETRS89) con 32630 (WGS84 UTM) ni con 4258 sin reproyectar. Tabla completa, formatos y fuentes oficiales en [sistemas-y-fuentes.md](referencia/sistemas-y-fuentes.md).

## Identificadores y uniones

- Une por **código oficial**, nunca por nombre: INE de municipio (5 dígitos), sección censal (10 dígitos), distrito y barrio del Ayuntamiento. «Las Rozas de Madrid» y «Rozas de Madrid, Las» son el mismo municipio para una persona, pero no para un `merge`.
- Códigos como **texto**, con los ceros a la izquierda (`"28079"`, no `28079`).
- Tras cada unión, cuenta: zonas sin dato, datos sin zona. Lo esperado son 179 municipios y 21 distritos en la capital.
- Fuentes de geometrías: INE (secciones), CNIG (municipios, nomenclátor), datos.madrid.es (barrios), Eurostat GISCO.

## Tablas de paso

Barrios, distritos del MITMA, secciones del INE y códigos postales no coinciden.

- Los **códigos postales** responden a la logística de Correos, no a un marco estadístico, y su cartografía no es oficial.
- Paso de código postal a barrio o sección: superposición de polígonos con **pesos** (viviendas o población de cada trozo, no área).
- Comprueba que los pesos de cada origen suman 1 y que el total se conserva tras el paso.
- Declara el supuesto en la nota metodológica.

## Mapas para la demo

- **Tasas o medias**, nunca absolutos: el ojo lee el área.
- **Clasificación** con `mapclassify`, nombrada en la leyenda:
  - **cuantiles** para comparar posiciones;
  - **Jenks** para grupos naturales;
  - **intervalos iguales** cuando la escala tiene sentido propio (euros);
  - **punto medio** para «te sobra / no te sobra» (0 €) o el umbral del 30 % de sobrecarga.
- **Paleta** secuencial para magnitudes y **divergente** cuando hay un punto medio con significado. Apta para daltónicos.
- **Marca «estimado»** (trama o borde) en las zonas imputadas, con su intervalo en la ficha. Las zonas fuera del área de aplicabilidad del modelo, distinguidas.
- **Cartograma** (contiguo o Dorling) por población si Madrid capital queda diminuta frente a la sierra.
- Leyenda con unidad, fuente bajo el mapa y «© OpenStreetMap contributors» si se usa OSM.

- Las **coronas tarifarias** son ordinales: paleta secuencial por pasos, no cualitativa.
- Cuantiles fallan con variables muy asimétricas o con muchos empates; para colas largas, head/tail breaks o escala logarítmica.

Tabla de clasificaciones, paletas y trampas visuales en [mapas-de-presentacion.md](referencia/mapas-de-presentacion.md). Para mapas que sirven para explorar y no para presentar (caja, barajado, Bayes empírico), ver `dm-eda-espacial`.

## Python

| Tarea | Función |
|---|---|
| Cargar y reproyectar | `geopandas.read_file`, `gdf.to_crs(25830)` |
| Superposición para tablas de paso | `geopandas.overlay(a, b, how="intersection")` |
| Vecino más cercano y distancias | `geopandas.sjoin_nearest(..., distance_col="d")` en EPSG:25830 |
| Clasificar | `mapclassify.Quantiles`, `NaturalBreaks`, `EqualInterval` |
| Mapa rápido | `gdf.plot(column=..., scheme="quantiles", legend=True)` |

En R (curso): `sf`, `st_transform`, `st_intersection`, `tmap`.
