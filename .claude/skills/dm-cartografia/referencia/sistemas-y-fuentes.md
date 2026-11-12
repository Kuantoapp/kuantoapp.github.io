# Sistemas de referencia, formatos y fuentes

Basado en el tema 2 del curso (SIG y cartografía) y en el tema 3 (identificadores).

## Códigos EPSG que aparecen en España

| EPSG | Qué es | Unidades | Uso en el proyecto |
|---|---|---|---|
| **25830** | ETRS89 / UTM huso 30N | metros | **Medir** en la península: distancias, buffers, áreas, W por distancia |
| 25829 / 25831 | ETRS89 / UTM husos 29 y 31 | metros | Galicia y Cataluña o Baleares; no para Madrid |
| 4258 | ETRS89 geográficas | grados | Muchas descargas del CNIG y del IGN vienen así |
| **4326** | WGS84 geográficas (Google Earth, GPS) | grados | Guardar e intercambiar; entrada de MapLibre |
| 3857 | Web Mercator (Google Maps, OSM, Bing) | metros **distorsionados** | Solo para teselas web; nunca para medir |
| 32630 | WGS84 / UTM huso 30N | metros | Casi idéntico a 25830 pero **no** igual: no los mezcles sin reproyectar |

- Un CRS es un datum (el elipsoide que se ajusta a la Tierra, por ejemplo ETRS89 o WGS84) más una proyección (paso al plano, por ejemplo UTM) y unas unidades. Toda proyección distorsiona algo: área (equivalentes), forma (conformes) o distancia.
- **Por qué no medir en grados:** un grado de latitud son unos 111 km, pero un grado de longitud son 111,321 km × cos(latitud). En Madrid (≈ 40,4° N) son unos 85 km. Una distancia «en grados» mezcla dos escalas distintas.
- Si necesitas distancia entre puntos en geográficas sin reproyectar, usa la fórmula del arco sobre la esfera (radio medio 6.371 km), no la euclídea. En el proyecto, mejor reproyectar a 25830.
- Referencias para consultar un código: spatialreference.org y la documentación de PROJ.

## Formatos

- **Vectorial** (puntos, líneas, polígonos con atributos): municipios, barrios, secciones, paradas. **Ráster** (rejilla de celdas): elevación, usos del suelo, población en rejilla.
- **Shapefile** son varios ficheros que viajan juntos: `.shp` (geometrías), `.shx` (índice), `.dbf` (atributos) y `.prj` (CRS). Si falta `.prj`, el CRS es desconocido y no se puede adivinar.
- En el proyecto, guarda las capas procesadas en **GeoParquet** (rápido, conserva el CRS y los tipos) y sirve el mapa con **PMTiles**.
- Lectura: `geopandas` para vectorial; `rasterio` para ráster.

## Dónde está la cartografía oficial

| Fuente | Qué ofrece |
|---|---|
| **INE** | Cartografía de secciones censales por año (la sección cambia: usa la del mismo año que el dato) |
| **CNIG**, centro de descargas | Límites municipales, nomenclátor de municipios y entidades de población, Atlas Nacional |
| **CartoCiudad** (IGN) | Callejero, portales y códigos postales: base para geocodificar y para tablas de paso (comprobar licencia y cobertura) |
| **datos.madrid.es** | Barrios y distritos de Madrid capital |
| **datos.comunidad.madrid** | Zonificación de transporte y capas regionales |
| **Eurostat GISCO** | NUTS y unidades administrativas europeas |

El nivel de detalle depende de la escala: para un mapa regional sobran geometrías de alta resolución. Simplifica (`gdf.simplify`) antes de generar teselas, pero mide siempre con la geometría original.

## Identificadores oficiales

- Municipio: código INE de 5 dígitos (2 de provincia + 3 de municipio; Madrid es `28079`).
- Sección censal: 10 dígitos (municipio + distrito + sección).
- Siempre como **texto**, con ceros a la izquierda.
- Los nombres cambian, llevan artículos pospuestos y tildes distintas. El código no.
