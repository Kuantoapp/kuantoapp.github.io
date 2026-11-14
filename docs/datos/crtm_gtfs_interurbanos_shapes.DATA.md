# shapes.txt — diccionario de datos
<!-- datadict: size=201804195 mtime=1793889127 rows=2492179 stride=13 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 2492179 · Columnas: 5 · Tamano: 192.5 MB
- Separador: coma · perfilado sobre 191707 de 2492179 filas (1 de cada 13) · semilla 42
- Origen: GTFS de Autobuses Interurbanos del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| shape_id | str | 0.0 | >=50 | alta cardinalidad | Trazado; enlaza con shapes.txt |
| shape_pt_lat | float | 0.0 | >=50 | 39.6035..41.1313 (media 40.4578) | Latitud WGS84 del punto del trazado |
| shape_pt_lon | float | 0.0 | >=50 | -4.58104..-2.76363 (media -3.74679) | Longitud WGS84 del punto del trazado |
| shape_pt_sequence | int | 0.0 | >=50 | 1e+06..8.5e+07 (media 1.47084e+07) | Orden del punto dentro del trazado |
| shape_dist_traveled | float | 0.0 | >=50 | 0..36154.6 (media 2214.68) | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 8_N_401____1_-_IT_1 | 40.4073614671415 | -3.69354648474132 | 1000001 | 0 |
| 8_N_401____1_-_IT_1 | 40.4073614671203 | -3.6935464882767 | 1000002 | 0.0000003 |
| 8_N_401____1_-_IT_1 | 40.4070677171055 | -3.6938051696221 | 1000003 | 0.039307484533 |
| 8_N_401____1_-_IT_1 | 40.4058665998297 | -3.69488298018591 | 1000004 | 0.240295496586 |
| 8_N_401____1_-_IT_1 | 40.4048498552236 | -3.69582086893663 | 1000005 | 0.579383579245 |

## Muestra aleatoria
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 8__541____2_-_IT_1 | 40.3610453207768 | -3.74736641935568 | 26000417 | 8588.49342733172 |
| 8__669_A___1_-_IT_1 | 40.6068326435817 | -4.11952316905127 | 5000073 | 81.133983489971 |
| 8__191____1_cu_IT_2 | 40.8483426572069 | -3.61617075449078 | 27000080 | 6325.13275685232 |
| 8__631____1_r._IT_2 | 40.5685289144181 | -4.01226953556088 | 15000062 | 6445.11043060284 |
| 8__231____2_-_IT_1 | 40.4430456103328 | -3.36881822280182 | 7000011 | 26.068324455854 |

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
