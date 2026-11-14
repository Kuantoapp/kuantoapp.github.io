# stop_times.txt — diccionario de datos
<!-- datadict: size=115248523 mtime=1793889142 rows=1474880 stride=8 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 1474880 · Columnas: 9 · Tamano: 109.9 MB
- Separador: coma · perfilado sobre 184360 de 1474880 filas (1 de cada 8) · semilla 42
- Origen: GTFS de Autobuses Interurbanos del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| trip_id | str | 0.0 | >=50 | alta cardinalidad | Viaje; enlaza con trips.txt |
| arrival_time | str | 0.0 | >=50 | alta cardinalidad | Hora de llegada HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| departure_time | str | 0.0 | >=50 | alta cardinalidad | Hora de salida HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| stop_id | str | 0.0 | >=50 | alta cardinalidad | Parada; enlaza con stops.txt |
| stop_sequence | int | 0.0 | >=50 | 0..643 (media 15.5699) | Orden de la parada dentro del viaje (creciente) |
| stop_headsign | vacia | 100.0 | 0 |  | Rótulo de destino en esa parada |
| pickup_type | vacia | 100.0 | 0 |  | Tipo de subida; vacío = 0, servicio regular |
| drop_off_type | vacia | 100.0 | 0 |  | Tipo de bajada; vacío = 0, servicio regular |
| shape_dist_traveled | vacia | 100.0 | 0 |  | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| 942101_8__421___-8__421____1_05:40:00_2… | 05:40:00 | 05:40:00 | par_8_08042 | 0 |  |  |  |  |
| 942101_8__421___-8__421____1_05:40:00_2… | 05:40:24 | 05:40:24 | par_8_08053 | 1 |  |  |  |  |
| 942101_8__421___-8__421____1_05:40:00_2… | 05:41:07 | 05:41:07 | par_8_08041 | 2 |  |  |  |  |
| 942101_8__421___-8__421____1_05:40:00_2… | 05:41:38 | 05:41:38 | par_8_08043 | 3 |  |  |  |  |
| 942101_8__421___-8__421____1_05:40:00_2… | 05:42:22 | 05:42:22 | par_8_08046 | 4 |  |  |  |  |

## Muestra aleatoria
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| 427_8__538___-8__538____1_22:15:00_1_-_… | 22:42:29 | 22:42:29 | par_8_11840 | 13 |  |  |  |  |
| 9999_8_N_202___-8_N_202____2_05:30:00_1… | 01:30:48 | 01:30:48 | par_8_06940 | 47 |  |  |  |  |
| 1553286_8__282___-11013745 | 13:23:08 | 13:23:08 | par_8_12523 | 15 |  |  |  |  |
| 5003_8__481___-8__481____1_07:12:00_2_-… | 01:00:00 | 01:00:00 | par_8_07937 | 4 |  |  |  |  |
| 1550920_8__461___-11002971 | 21:35:00 | 21:35:00 | par_8_15800 | 0 |  |  |  |  |

## Avisos
- 4 columnas vacias: `stop_headsign`, `pickup_type`, `drop_off_type`, `shape_dist_traveled`.

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
