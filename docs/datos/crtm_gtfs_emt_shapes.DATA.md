# shapes.txt — diccionario de datos
<!-- datadict: size=10389959 mtime=1793343642 rows=193350 stride=1 sep='coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 193350 · Columnas: 5 · Tamano: 9.9 MB
- Separador: coma · perfilado sobre las 193350 filas · semilla 42
- Origen: GTFS de la EMT del CRTM; su fila en data/README.md. Columnas según la Referencia GTFS Schedule (gtfs.org/schedule/reference)

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| shape_id | str | 0.0 | >=50 | alta cardinalidad | Trazado; enlaza con shapes.txt |
| shape_pt_lat | float | 0.0 | >=50 | 40.3319..40.5367 (media 40.428) | Latitud WGS84 del punto del trazado |
| shape_pt_lon | float | 0.0 | >=50 | -3.84771..-3.54103 (media -3.68207) | Longitud WGS84 del punto del trazado |
| shape_pt_sequence | int | 0.0 | >=50 | 1..910 (media 239.422) | Orden del punto dentro del trazado |
| shape_dist_traveled | int | 0.0 | >=50 | 0..24705 (media 5443.22) | Distancia recorrida desde el inicio del trazado; el feed no declara la unidad |

## Primeras filas
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 001_A | 40.438381323037554 | -3.717924512095068 | 1 | 0 |
| 001_A | 40.438100065141491 | -3.717829769387604 | 2 | 30 |
| 001_A | 40.437880066994232 | -3.717869767493253 | 3 | 55 |
| 001_A | 40.437740067147871 | -3.717889766628850 | 4 | 70 |
| 001_A | 40.436710069011568 | -3.718069755299971 | 5 | 186 |

## Muestra aleatoria
| shape_id | shape_pt_lat | shape_pt_lon | shape_pt_sequence | shape_dist_traveled |
|---|---|---|---|---|
| 175_B | 40.507749979961886 | -3.691070121896662 | 218 | 4577 |
| 032_A | 40.407690267705597 | -3.646289609052037 | 321 | 7172 |
| 040_A | 40.432660122638474 | -3.696559749653086 | 42 | 1007 |
| 501_A | 40.485800032371152 | -3.660520046032969 | 419 | 10508 |
| 074_B | 40.429990085440686 | -3.721049683869298 | 328 | 8542 |

## Notas
- No se redistribuye en bruto (licencia del CRTM); solo se publican tiempos derivados.
- Comprobado el 2026-11-15: el `calendar.txt` de Metro va del 2025-05-27 al 2026-05-27 y no cubre noviembre de 2026; las otras cinco redes empiezan entre el 27 y el 30 de octubre de 2026.
