# Cartografía, CRS y mapas coropléticos

## Sistema de referencia (CRS)

- Un CRS es un datum (modelo de la Tierra: WGS84, ETRS89…) más una proyección (paso a plano: UTM, Mercator…) y unas unidades.
- **España peninsular: ETRS89 / UTM huso 30N, EPSG:25830**, en metros. Úsalo para distancias, buffers, áreas y W por distancia.
- **EPSG:4326** (grados) para guardar e intercambiar, y para MapLibre (que reproyecta a Web Mercator, EPSG:3857). Nunca para medir.
- Comprueba el CRS de cada capa al cargarla (`gdf.crs`) y reproyecta explícitamente (`to_crs`). No asumas.

## Identificadores

- Une datos y geometrías por **código normalizado**, no por nombre: código INE de municipio (5 dígitos, con ceros a la izquierda), sección censal (10 dígitos), código de distrito y barrio del Ayuntamiento.
- Guarda los códigos como **texto**, para no perder los ceros.
- **Códigos postales**: responden a la logística de Correos, no a un marco estadístico, y su cartografía no es oficial. Pasarlos a barrio o sección exige una tabla de paso con pesos (viviendas o población) y declarar el supuesto.
- Fuentes de cartografía: INE (secciones censales), CNIG (municipios, nomenclátor), datos.madrid.es (barrios), Eurostat GISCO.

## Mapas coropléticos

- Pinta **tasas o medias**, no valores absolutos: el ojo lee el área, y un municipio grande y vacío domina el mapa.
- **Clasificación** (con `mapclassify`):
  - cuantiles: mismo número de zonas por clase; buena para comparar posiciones;
  - Jenks o natural breaks: minimiza la variación dentro de cada clase;
  - intervalos iguales: si la escala tiene sentido propio (euros);
  - desviaciones típicas o punto medio: para variables con un centro (0 € «te sobra / no te sobra»).

  Di cuál usas en la leyenda.
- **Paleta:** secuencial para magnitudes, **divergente** cuando hay un punto medio con significado (por ejemplo, 0 € o el 30 % de sobrecarga). Apta para daltónicos.
- **Prueba del mapa barajado:** el mismo mapa con los valores permutados al azar. Si el real «parece» igual de agrupado, no hay patrón visual.
- Zonas con poca población dan tasas inestables: márcalas o suavízalas.
- **Mapas condicionales:** un mapa por intervalo de otra variable, para ver relaciones.
- **Cartogramas** (contiguos, no contiguos, Dorling): deforman el área según una variable, por ejemplo la población. Útiles para que Madrid capital no quede diminuta frente a la sierra.

## Para la demo

Leyenda con la clasificación y la unidad, marca «estimado» en las zonas imputadas, fuente debajo del mapa y la mención «© OpenStreetMap contributors» si se usa OSM.
