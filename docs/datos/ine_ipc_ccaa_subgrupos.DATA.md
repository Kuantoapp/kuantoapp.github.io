# ine_ipc_ccaa_subgrupos_2026-11-15.csv — diccionario de datos
<!-- datadict: size=92853966 mtime=1794740134 rows=1096640 stride=6 sep='punto y coma' seed=42 generated=2026-11-15 10:57 UTC -->

- Filas: 1096640 · Columnas: 5 · Tamano: 88.6 MB
- Separador: punto y coma · perfilado sobre 182774 de 1096640 filas (1 de cada 6) · semilla 42
- Origen: INE, IPC base 2025 por comunidades autónomas y subgrupos ECOICOP v2, tabla 76137, mensual; fila «IPC por CCAA y subgrupo (INE, t=76137)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Comunidades y Ciudades Autónomas | str | 0.0 | 20 | top: Nacional (5%), 01 Andalucía (5%), … | Código y nombre; «Nacional» y las 19 comunidades y ciudades (Madrid es «13 Madrid, Comunidad de») |
| Subgrupos ECOICOP ver.2 | str | 0.0 | 46 | top: Índice general (2%), 02.1 Bebidas … | Subgrupo del IPC; el alquiler es «04.1 Alquiler de vivienda» (serie IPC297196 en Madrid) |
| Tipo de dato | str | 0.0 | 4 | top: Índice (25%), Variación en lo que … | Índice, variación mensual, variación anual o variación en lo que va de año |
| Periodo | str | 0.0 | >=50 | alta cardinalidad | Mes, con formato AAAAMmm (2026M10) |
| Total | str | 11.3 | >=50 | alta cardinalidad | Valor en formato español (coma decimal); vacío o «.» sin dato |

## Primeras filas
| Comunidades y Ciudades Autónomas | Subgrupos ECOICOP ver.2 | Tipo de dato | Periodo | Total |
|---|---|---|---|---|
| Nacional | Índice general | Índice | 2026M10 | 105,651 |
| Nacional | Índice general | Índice | 2026M09 | 104,978 |
| Nacional | Índice general | Índice | 2026M08 | 104,638 |
| Nacional | Índice general | Índice | 2026M07 | 103,899 |
| Nacional | Índice general | Índice | 2026M06 | 103,598 |

## Muestra aleatoria
| Comunidades y Ciudades Autónomas | Subgrupos ECOICOP ver.2 | Tipo de dato | Periodo | Total |
|---|---|---|---|---|
| 14 Murcia, Región de | 01.2 Bebidas no alcohólicas | Índice | 2025M02 | 99,028 |
| 02 Aragón | 07.2 Utilización de vehículos personales | Variación anual | 2014M12 | -9,9 |
| 03 Asturias, Principado de | 04.5 Electricidad, gas y otros combusti… | Variación anual | 2002M04 | -2,6 |
| 16 País Vasco | Índice general | Índice | 2012M08 | 76,907 |
| 06 Cantabria | 02.1 Bebidas alcohólicas | Índice | 2012M10 | 73,988 |

## Avisos
- 1 columnas con numeros en formato espanol (coma decimal o punto de miles): `Total`.

## Notas
- UTF-8 con BOM: leer con `encoding="utf-8-sig"`.
- Control de F0-04: media de los 12 índices mensuales de 04.1 en Madrid = 94,466 (2023) y 97,062 (2024), iguales a las del catálogo `1934665`.
- Último mes: 2026M10.
