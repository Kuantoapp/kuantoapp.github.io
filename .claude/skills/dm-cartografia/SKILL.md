---
description: "Prepara y cruza datos geográficos con geopandas y diseña los mapas finales: CRS y reproyección (medir en EPSG:25830 u otro UTM, publicar en 4326 o 3857), uniones por código oficial (INE, sección censal, barrio, distrito), sjoin, distancias, áreas y coropletas de presentación. No hace tablas de paso entre unidades que no coinciden (dm-tablas-de-paso), ni busca patrones (dm-eda-espacial) ni modela (dm-modelado-espacial)."
when_to_use: "Leer un shapefile, GeoJSON o GeoParquet; comprobar o cambiar el CRS; hacer un merge o sjoin por municipio o sección; averiguar por qué una unión pierde zonas; medir distancias a servicios; elegir clasificación, paleta y leyenda de un mapa o un cartograma."
---

# Cartografía y mapas

Base de cualquier análisis espacial: si la unión o el CRS fallan, todo lo que viene después (`dm-eda-espacial`, `dm-modelado-espacial`) es falso.

## Antes de empezar: conectar con el desarrollo del proyecto

Esta skill es general. Qué unidades, fuentes y mapas se usan sale del estado actual del proyecto; no lo supongas ni lo copies de los ejemplos.

1. **Qué unidades y ámbito:** lee `docs/decisiones.md` (unidad territorial, ámbito, mapas previstos) y, si hace falta, la ficha vigente en `ideas/`. Las fichas son borradores: manda lo decidido.
2. **Qué fuentes:** lee `data/README.md`. Cada capa nueva se documenta ahí (URL, año, licencia, CRS original).
3. **Qué hay ya hecho:** busca cargas, CRS fijados y tablas de paso existentes y reutilízalos:
   `grep -rnE "read_file|read_parquet|to_crs|EPSG|25830|sjoin|overlay|codigo_ine|cusec" src notebooks`.
   Si el proyecto ya fija un CRS o un tipo de código, se sigue ese.
4. **Qué falta por decidir:** si la unidad o el año de la cartografía no están claros, pregunta; si supones, escríbelo.

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

Si las unidades no coinciden (código postal, secciones de otro año, barrios, zonas de transporte), el paso entre ellas lo hace `dm-tablas-de-paso`: anidamiento, pesos por población o viviendas, extensivas frente a intensivas y controles.

## Mapas de presentación

- **Tasas o medias**, nunca absolutos: el ojo lee el área.
- **Clasificación** nombrada en la leyenda: cuantiles para comparar posiciones, cortes naturales para grupos homogéneos, intervalos iguales si la unidad tiene sentido propio, **punto medio** si hay un umbral con significado (0, un porcentaje de referencia). Los cuantiles fallan con mucha asimetría o empates; para colas largas, head/tail breaks o logaritmos.
- **Paleta** secuencial para magnitudes, **divergente** con punto medio con significado, cualitativa para categorías sin orden y **ordinal** para categorías con orden. Apta para daltónicos; el rojo, solo para lo que es una alerta.
- **Estimaciones marcadas** (trama o borde) con su intervalo accesible, y diferenciadas las zonas fuera del ámbito del modelo.
- **Cartograma** o símbolos graduados si las zonas grandes y poco pobladas dominan el mapa.
- Leyenda con unidad y método; fuente bajo el mapa; «© OpenStreetMap contributors» si se usa OSM.

Detalle de clasificaciones, paletas y trampas visuales en [mapas-de-presentacion.md](referencia/mapas-de-presentacion.md). Para mapas que sirven para explorar (caja, barajado, Bayes empírico), `dm-eda-espacial`.

## Contrastar cada resultado con lo que debe salir

Después de cada carga, unión, paso entre unidades o medida, compara con lo que es correcto por definición o por la fuente oficial. Si no cuadra, se diagnostica y se corrige **antes de seguir**: una unión que pierde zonas en silencio invalida todo lo posterior.

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Número de zonas tras una unión | El del ámbito oficial (por ejemplo, 179 municipios en la Comunidad de Madrid, 21 distritos en la capital) | Códigos con formato distinto, años de cartografía distintos, ceros perdidos |
| Zonas sin dato y datos sin zona | Ninguno, o cada uno con explicación | Revisar códigos huérfanos uno a uno |
| Total de una variable tras un paso entre unidades | Igual antes y después | Pesos mal calculados |
| Pesos de cada unidad de origen | Suman 1 | Superposición incompleta o geometrías inválidas |
| Suma de áreas | ≈ superficie oficial del ámbito | CRS en grados, geometrías duplicadas o huecos |
| Distancias | Positivas y menores que la extensión del territorio | CRS en grados o coordenadas intercambiadas (latitud y longitud) |
| CRS de cada capa | El esperado y explícito | Reproyectar; nunca asignar a ciegas |
| Geometrías | Válidas (`is_valid`), sin vacías | `make_valid` o revisar la fuente |

En un mapa: compara al menos dos clasificaciones. Si el mensaje cambia mucho con la clasificación, el mapa engaña y hay que decirlo o cambiarlo.

## Al terminar: dejar el trabajo conectado

- Cargas y reproyecciones van a funciones de `src/` reutilizables, con un test de los controles de arriba (recuento de zonas, totales conservados).
- Capas nuevas documentadas en `data/README.md`; zonas excluidas, en `docs/decisiones.md`.
- Antes de dar los datos por buenos o de abrir el PR, pide la revisión de `dm-revisor-espacial`.

## Python

| Tarea | Función |
|---|---|
| Cargar y reproyectar | `geopandas.read_file`, `read_parquet`, `gdf.to_crs(25830)` |
| Unión espacial y vecino más cercano | `geopandas.sjoin`, `sjoin_nearest(..., distance_col="d")` en metros |
| Clasificar | `mapclassify.Quantiles`, `NaturalBreaks`, `EqualInterval`, `HeadTailBreaks` |
| Mapa rápido | `gdf.plot(column=..., scheme="quantiles", legend=True)` |

En R (curso): `sf`, `st_transform`, `st_intersection`, `tmap`.
