# stop_times.txt — diccionario de datos
<!-- datadict: size=99872729 mtime=1793343642 rows=2231790 stride=12 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 2231790 · Columnas: 9 · Tamano: 95.2 MB
- Separador: coma · perfilado sobre 185983 de 2231790 filas (1 de cada 12) · semilla 42
- Origen: GTFS de la EMT del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| trip_id | str | 0.0 | >=50 | alta cardinalidad | Viaje; enlaza con trips.txt |
| arrival_time | str | 0.0 | >=50 | alta cardinalidad | Hora de llegada HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| departure_time | str | 0.0 | >=50 | alta cardinalidad | Hora de salida HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| stop_id | int | 0.0 | >=50 | 2..51327 (media 3639.79) | Parada; enlaza con stops.txt |
| stop_sequence | int | 0.0 | 47 | 1..47 (media 15.086) | Orden de la parada dentro del viaje (creciente) |
| stop_headsign | vacia | 100.0 | 0 |  | Rótulo de destino en esa parada |
| pickup_type | vacia | 100.0 | 0 |  | Tipo de subida; vacío = 0, servicio regular |
| drop_off_type | vacia | 100.0 | 0 |  | Tipo de bajada; vacío = 0, servicio regular |
| shape_dist_traveled | int | 0.0 | >=50 | 0..23455 (media 4814.64) | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| FE0010011 | 07:00:00 | 07:00:00 | 4514 | 1 |  |  |  | 0 |
| FE0010011 | 07:01:40 | 07:01:40 | 4022 | 2 |  |  |  | 295 |
| FE0010011 | 07:02:44 | 07:02:44 | 3687 | 3 |  |  |  | 485 |
| FE0010011 | 07:04:17 | 07:04:17 | 737 | 4 |  |  |  | 759 |
| FE0010011 | 07:05:45 | 07:05:45 | 735 | 5 |  |  |  | 1019 |

## Muestra aleatoria
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | stop_headsign | pickup_type | drop_off_type | shape_dist_traveled |
|---|---|---|---|---|---|---|---|---|
| LA1330067 | 12:22:24 | 12:22:24 | 3688 | 9 |  |  |  | 2201 |
| LA02100517 | 21:51:05 | 21:51:05 | 1226 | 26 |  |  |  | 6996 |
| FE02600518 | 21:22:37 | 21:22:37 | 2212 | 10 |  |  |  | 3372 |
| LA1500096 | 14:56:58 | 14:56:58 | 102 | 19 |  |  |  | 5461 |
| LA04700814 | 21:24:05 | 21:24:05 | 1158 | 34 |  |  |  | 9475 |

## Avisos
- 3 columnas vacias: `stop_headsign`, `pickup_type`, `drop_off_type`.

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
