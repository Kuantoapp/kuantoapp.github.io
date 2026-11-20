# ine_ipc_clases_nacional_2026-11-19.csv — diccionario de datos
<!-- datadict: size=9720003 mtime=1795103493 rows=129928 stride=1 sep='punto y coma' seed=42 generated=2026-11-19 15:54 UTC -->

- Filas: 129928 · Columnas: 4 · Tamano: 9.3 MB
- Separador: punto y coma · perfilado sobre las 129928 filas · semilla 42
- Origen: INE, IPC base 2025 nacional por clases ECOICOP v2, tabla 76127, mensual; fila «IPC nacional por clases (INE, t=76127)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Clases  ECOICOP ver.2 | str | 0.0 | >=50 | alta cardinalidad | Clase del IPC con código (dos espacios en el nombre de la columna; algunos nombres llevan espacio final). La cesta usa «04.4.1 Suministro de agua» |
| Tipo de dato | str | 0.0 | 4 | top: Índice (25%), Variación mensual (2… | Índice, variación mensual, variación anual o variación en lo que va de año |
| Periodo | str | 0.0 | >=50 | alta cardinalidad | Mes, con formato AAAAMmm (2026M10) |
| Total | str | 24.4 | >=50 | alta cardinalidad | Valor en formato español (coma decimal); vacío sin dato (series que empiezan después) |

## Primeras filas
| Clases  ECOICOP ver.2 | Tipo de dato | Periodo | Total |
|---|---|---|---|
| Índice general | Índice | 2026M10 | 105,651 |
| Índice general | Índice | 2026M09 | 104,978 |
| Índice general | Índice | 2026M08 | 104,638 |
| Índice general | Índice | 2026M07 | 103,899 |
| Índice general | Índice | 2026M06 | 103,598 |

## Muestra aleatoria
| Clases  ECOICOP ver.2 | Tipo de dato | Periodo | Total |
|---|---|---|---|
| 13.3.0 Protección social | Variación anual | 2009M12 |  |
| 02.1.9 Otras bebidas alcohólicas  | Índice | 2016M07 |  |
| 04.1.2 Otros alquileres | Variación en lo que va de año | 2022M09 | 1,9 |
| 06.3.2 Servicios de cuidados de larga d… | Índice | 2017M07 |  |
| 06.2.1 Servicios de cuidados preventivo… | Variación anual | 2024M06 |  |

## Avisos
- 1 columnas con numeros en formato espanol (coma decimal o punto de miles): `Total`.

## Notas
(Escribe aqui lo que no sale del script; se conserva al regenerar.)
