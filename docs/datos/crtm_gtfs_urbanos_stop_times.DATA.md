# stop_times.txt — diccionario de datos
<!-- datadict: size=38381848 mtime=1793889165 rows=490571 stride=3 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 490571 · Columnas: 9 · Tamano: 36.6 MB
- Separador: coma · perfilado sobre 163524 de 490571 filas (1 de cada 3) · semilla 42
- Origen: GTFS de Autobuses Urbanos del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| trip_id | str | 0.0 | >=50 | alta cardinalidad | Viaje; enlaza con trips.txt |
| arrival_time | str | 0.0 | >=50 | alta cardinalidad | Hora de llegada HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| departure_time | str | 0.0 | >=50 | alta cardinalidad | Hora de salida HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| stop_id | str | 0.0 | >=50 | alta cardinalidad | Parada; enlaza con stops.txt |
| stop_sequence | int | 0.0 | >=50 | 0..1703 (media 20.0465) | Orden de la parada dentro del viaje (creciente) |
| stop_headsign | vacia | 100.0 | 0 |  | Rótulo de destino en esa parada |
| pickup_type | vacia | 100.0 | 0 |  | Tipo de subida; vacío = 0, servicio regular |
| drop_off_type | vacia | 100.0 | 0 |  | Tipo de bajada; vacío = 0, servicio regular |
| shape_dist_traveled | vacia | 100.0 | 0 |  | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| 9010101_9__1__013_-9__1__013__1_00:15:0… | 00:15:00 | 00:15:00 | par_8_09568 | 0 |  |  |  |  |
| 9010101_9__1__013_-9__1__013__1_00:15:0… | 00:15:00 | 00:15:00 | par_8_21327 | 1 |  |  |  |  |
| 9010101_9__1__013_-9__1__013__1_00:15:0… | 00:15:00 | 00:15:00 | par_8_09572 | 2 |  |  |  |  |
| 9010101_9__1__013_-9__1__013__1_00:15:0… | 00:15:00 | 00:15:00 | par_8_09576 | 3 |  |  |  |  |
| 9010101_9__1__013_-9__1__013__1_00:15:0… | 00:15:00 | 00:15:00 | par_8_09640 | 4 |  |  |  |  |

## Muestra aleatoria
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| 146126_9__10__005_-2145654 | 11:34:00 | 11:34:00 | par_8_07041 | 3 |  |  |  |  |
| 9999_9__4__014_-9__4__014__3_16:45:00_1… | 16:45:00 | 16:45:00 | par_8_11642 | 34 |  |  |  |  |
| 9999_9__1_A_148_-9__1_A_148__2_11:00:00… | 08:29:34 | 08:29:34 | par_8_06891 | 230 |  |  |  |  |
| 146371_9__1_B_005_-2148974 | 18:51:00 | 18:51:00 | par_8_09685 | 25 |  |  |  |  |
| 1533093_9__2__106_-10882600 | 18:05:21 | 18:05:21 | par_8_07828 | 13 |  |  |  |  |

## Avisos
- 4 columnas vacias: `stop_headsign`, `pickup_type`, `drop_off_type`, `shape_dist_traveled`.

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
