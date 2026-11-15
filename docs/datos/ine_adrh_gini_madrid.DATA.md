# ine_adrh_gini_madrid_2026-11-15.csv — diccionario de datos
<!-- datadict: size=11464631 mtime=1794740124 rows=100220 stride=1 sep='punto y coma' seed=42 generated=2026-11-15 10:57 UTC -->

- Filas: 100220 · Columnas: 6 · Tamano: 10.9 MB
- Separador: punto y coma · perfilado sobre las 100220 filas · semilla 42
- Origen: INE, ADRH, tabla 37727 «Índice de Gini y distribución de la renta» de la provincia de Madrid; fila «Gini y P80/P20 (INE, t=37727)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Municipios | str | 0.0 | >=50 | alta cardinalidad | Código INE del municipio (5 cifras) seguido del nombre, en la misma celda |
| Distritos | str | 3.6 | >=50 | alta cardinalidad | Código del distrito (7 cifras) y nombre; vacío en las filas de municipio |
| Secciones | str | 8.5 | >=50 | alta cardinalidad | Código de la sección (10 cifras) y nombre; vacío en las filas de municipio y de distrito |
| Índice de Gini y Distribución de la ren… | str | 0.0 | 2 | top: Índice de Gini (50%), Distribución… | Indicador (2): Índice de Gini y distribución de la renta P80/P20 |
| Periodo | int | 0.0 | 10 | 2015..2024 (media 2019.5) | Año de referencia (2015 a 2024) |
| Total | str | 3.2 | >=50 | alta cardinalidad | Valor en formato español (coma decimal); «.» = sin dato |

## Primeras filas
| Municipios | Distritos | Secciones | Índice de Gini y Distribución de la ren… | Periodo | Total |
|---|---|---|---|---|---|
| 28001 Acebeda, La |  |  | Índice de Gini | 2024 | . |
| 28001 Acebeda, La |  |  | Índice de Gini | 2023 | . |
| 28001 Acebeda, La |  |  | Índice de Gini | 2022 | . |
| 28001 Acebeda, La |  |  | Índice de Gini | 2021 | . |
| 28001 Acebeda, La |  |  | Índice de Gini | 2020 | . |

## Muestra aleatoria
| Municipios | Distritos | Secciones | Índice de Gini y Distribución de la ren… | Periodo | Total |
|---|---|---|---|---|---|
| 28058 Fuenlabrada | 2805808 Fuenlabrada distrito 08 | 2805808007 Fuenlabrada sección 08007 | Distribución de la renta P80/P20 | 2023 | 1,9 |
| 28074 Leganés | 2807401 Leganés distrito 01 | 2807401002 Leganés sección 01002 | Distribución de la renta P80/P20 | 2023 | 2,4 |
| 28079 Madrid | 2807902 Madrid distrito 02 | 2807902064 Madrid sección 02064 | Distribución de la renta P80/P20 | 2023 | 2,9 |
| 28079 Madrid | 2807913 Madrid distrito 13 | 2807913157 Madrid sección 13157 | Distribución de la renta P80/P20 | 2023 | 2,6 |
| 28079 Madrid | 2807912 Madrid distrito 12 | 2807912006 Madrid sección 12006 | Distribución de la renta P80/P20 | 2018 | 2,2 |

## Avisos
- 1 columnas con numeros en formato espanol (coma decimal o punto de miles): `Total`.

## Notas
(Escribe aqui lo que no sale del script; se conserva al regenerar.)
