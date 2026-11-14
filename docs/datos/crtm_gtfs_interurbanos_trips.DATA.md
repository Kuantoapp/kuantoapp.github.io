# trips.txt — diccionario de datos
<!-- datadict: size=8761805 mtime=1793889108 rows=58470 stride=1 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 58470 · Columnas: 9 · Tamano: 8.4 MB
- Separador: coma · perfilado sobre las 58470 filas · semilla 42
- Origen: GTFS de Autobuses Interurbanos del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| route_id | str | 0.0 | >=50 | alta cardinalidad | Línea; enlaza con routes.txt |
| service_id | str | 0.0 | >=50 | alta cardinalidad | Calendario; enlaza con calendar.txt y calendar_dates.txt |
| trip_id | str | 0.0 | >=50 | alta cardinalidad | Viaje; enlaza con trips.txt |
| trip_headsign | str | 0.0 | >=50 | alta cardinalidad | Rótulo de destino del viaje |
| trip_short_name | str | 0.0 | >=50 | alta cardinalidad | Nombre corto del viaje para el público |
| direction_id | int | 0.0 | 2 | 0..1 (media 0.496032) | Sentido del viaje (0 o 1) |
| block_id | vacia | 100.0 | 0 |  | Bloque de viajes consecutivos con el mismo vehículo |
| shape_id | str | 0.0 | >=50 | alta cardinalidad | Trazado; enlaza con shapes.txt |
| wheelchair_accessible | int | 0.0 | 1 | 0..0 (media 0) | Accesible en silla de ruedas (0 sin dato, 1 sí, 2 no) |

## Primeras filas
| route_id | service_id | trip_id | trip_headsign | trip_short_name | direction_id | block_id | shape_id | wheelchair_accessible |
|---|---|---|---|---|---|---|---|---|
| 8__421___ | 942101_8__421___ | 942101_8__421___-8__421____1_05:40:00_2… | PºDELICIAS-PLAZA DE LEGAZPI | 421 MADRID (Legazpi) | 1 |  | 8__421____2_-_IT_1 | 0 |
| 8__421___ | 942101_8__421___ | 942101_8__421___-8__421____1_06:30:00_1… | SUR-POLIDEPORTIVO | 421 PINTO | 0 |  | 8__421____1_-_IT_1 | 0 |
| 8__421___ | 942101_8__421___ | 942101_8__421___-8__421____1_07:15:00_2… | PºDELICIAS-PLAZA DE LEGAZPI | 421 MADRID (Legazpi) | 1 |  | 8__421____2_-_IT_1 | 0 |
| 8__421___ | 942101_8__421___ | 942101_8__421___-8__421____1_08:10:00_1… | SUR-POLIDEPORTIVO | 421 PINTO | 0 |  | 8__421____1_-_IT_1 | 0 |
| 8__421___ | 942101_8__421___ | 942101_8__421___-8__421____1_09:00:00_2… | PºDELICIAS-PLAZA DE LEGAZPI | 421 MADRID (Legazpi) | 1 |  | 8__421____2_-_IT_1 | 0 |

## Muestra aleatoria
| route_id | service_id | trip_id | trip_headsign | trip_short_name | direction_id | block_id | shape_id | wheelchair_accessible |
|---|---|---|---|---|---|---|---|---|
| 8__461___ | 1551063_8__461___ | 1551063_8__461___-11003139 | AV.RONDA-CARMEN CONDE | 461 PARLA | 0 |  | 8__461____1_-_IT_1 | 0 |
| 8__611___ | 1552080_8__611___ | 1552080_8__611___-11008794 | CTRA.M618-PUERTA PRINCIPAL CAMPAMENTO | 611 HOYO DE MANZANARES | 0 |  | 8__611____1_-_IT_1 | 0 |
| 8__681___ | 1557469_8__681___ | 1557469_8__681___-11046969 | CTRA.M619-CLUB DEPORTIVO GUADARRAMA | 681 ALPEDRETE | 0 |  | 8__681____1_-_IT_1 | 0 |
| 8__513___ | 54_8__513___ | 54_8__513___-8__513____2_08:15:00_2_-__… | PºEXTREMADURA-CUATRO VIENTOS | 513 MADRID (Cuatro Vientos) | 1 |  | 8__513____2_-_IT_1 | 0 |
| 8__336___ | 337T27_8__336___ | 337T27_8__336___-8__337____1_09:05:00_2… | FUENTE CARRANTONA-HACIENDA DE PAVONES | MADRID (Pavones)-MORATA DE TAJUÑA | 1 |  | 8__336____2_-_IT_1 | 0 |

## Avisos
- 1 columnas vacias: `block_id`.
- 1 columnas constantes: `wheelchair_accessible`.

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
