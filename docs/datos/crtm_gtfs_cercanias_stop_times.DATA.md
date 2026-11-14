# stop_times.txt — diccionario de datos
<!-- datadict: size=24247996 mtime=315529200 rows=559207 stride=3 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 559207 · Columnas: 7 · Tamano: 23.1 MB
- Separador: coma · perfilado sobre 186403 de 559207 filas (1 de cada 3) · semilla 42
- Origen: GTFS de Cercanías del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| trip_id | str | 0.0 | >=50 | alta cardinalidad | Viaje; enlaza con trips.txt |
| arrival_time | str | 0.0 | >=50 | alta cardinalidad | Hora de llegada HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| departure_time | str | 0.0 | >=50 | alta cardinalidad | Hora de salida HH:MM:SS del día de servicio (puede pasar de 24:00:00) |
| stop_id | int | 0.0 | >=50 | 10000..98305 (media 36654.4) | Parada; enlaza con stops.txt |
| stop_sequence | int | 0.0 | 41 | 1..41 (media 10.5101) | Orden de la parada dentro del viaje (creciente) |
| pickup_type | vacia | 100.0 | 0 |  | Tipo de subida; vacío = 0, servicio regular |
| drop_off_type | vacia | 100.0 | 0 |  | Tipo de bajada; vacío = 0, servicio regular |

## Primeras filas
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | pickup_type | drop_off_type |
|---|---|---|---|---|---|---|
| 1002V17098C8a | 06:35:00 | 06:36:00 | 10206 | 005 |  |  |
| 1002V17098C8a | 06:41:00 | 06:41:00 | 10205 | 006 |  |  |
| 1002V17098C8a | 06:47:00 | 06:47:00 | 10204 | 007 |  |  |
| 1002V17098C8a | 06:52:00 | 06:56:00 | 10203 | 008 |  |  |
| 1002V21182C10 | 06:52:00 | 06:56:00 | 10203 | 008 |  |  |

## Muestra aleatoria
| trip_id | arrival_time | departure_time | stop_id | stop_sequence | pickup_type | drop_off_type |
|---|---|---|---|---|---|---|
| 1022J21212C10 | 09:46:00 | 09:46:00 | 10007 | 012 |  |  |
| 1005L75867C7 | 20:33:00 | 20:33:00 | 70001 | 009 |  |  |
| 1006M36202C10 | 07:06:00 | 07:06:00 | 10002 | 010 |  |  |
| 1025D75333C10 | 15:15:00 | 15:15:00 | 18003 | 010 |  |  |
| 1011D27067C3 | 18:58:00 | 18:58:00 | 18101 | 011 |  |  |

## Avisos
- 2 columnas vacias: `pickup_type`, `drop_off_type`.

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
