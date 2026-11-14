# shapes.txt — diccionario de datos
<!-- datadict: size=19914283 mtime=1793889155 rows=244574 stride=2 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 244574 · Columnas: 5 · Tamano: 19.0 MB
- Separador: coma · perfilado sobre 122287 de 244574 filas (1 de cada 2) · semilla 42
- Origen: GTFS de Autobuses Urbanos del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| shape_id | str | 0.0 | >=50 | alta cardinalidad | Trazado; enlaza con shapes.txt |
| shape_pt_lat | float | 0.0 | >=50 | 40.0203..40.7668 (media 40.4395) | Latitud WGS84 del punto del trazado |
| shape_pt_lon | float | 0.0 | >=50 | -4.15277..-3.3177 (media -3.70955) | Longitud WGS84 del punto del trazado |
| shape_pt_sequence | int | 0.0 | >=50 | 1e+06..8.50001e+07 (media 1.57349e+07) | Orden del punto dentro del trazado |
| shape_dist_traveled | float | 0.0 | >=50 | 0..2555.05 (media 169.756) | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 9__1__013__1_-_IT_1 | 40.0345269585562 | -3.61783386984079 | 1000001 | 0 |
| 9__1__013__1_-_IT_1 | 40.0345387269612 | -3.6177601951994 | 1000002 | 0.006420176462 |
| 9__1__013__1_-_IT_1 | 40.0345337380432 | -3.61772391145079 | 1000003 | 0.015985203044 |
| 9__1__013__1_-_IT_1 | 40.0345261086463 | -3.61769687395839 | 1000004 | 0.028007578737 |
| 9__1__013__1_-_IT_1 | 40.0345171603552 | -3.61767403824246 | 1000005 | 0.042216842367 |

## Muestra aleatoria
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 9__8__134__1_-_IT_1 | 40.6189280958329 | -3.61863503958927 | 17000005 | 55.478909501663 |
| 9__1_A_148__1_-_IT_1 | 40.4517222863773 | -3.47145841888902 | 22000051 | 106.506338235483 |
| 9__3__148__2_pe_IT_2 | 40.4449422674726 | -3.48592521267993 | 2000019 | 69.98859094058 |
| 9__2__007__1_-_IT_1 | 40.3515979466647 | -3.83715534838829 | 28000037 | 114.868989753177 |
| 9__4__068__2_s._IT_2 | 40.6741595316026 | -4.09101714291297 | 18000036 | 307.905306258156 |

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
