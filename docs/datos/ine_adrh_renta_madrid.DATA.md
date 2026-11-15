# ine_adrh_renta_madrid_2026-11-15.csv — diccionario de datos
<!-- datadict: size=37419631 mtime=1794740121 rows=300660 stride=2 sep='punto y coma' seed=42 generated=2026-11-15 10:57 UTC -->

- Filas: 300660 · Columnas: 6 · Tamano: 35.7 MB
- Separador: punto y coma · perfilado sobre 150330 de 300660 filas (1 de cada 2) · semilla 42
- Origen: INE, ADRH, tabla 31097 «Indicadores de renta media y mediana» de la provincia de Madrid; fila «Renta ADRH (INE, t=31097)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Municipios | str | 0.0 | >=50 | alta cardinalidad | Código INE del municipio (5 cifras) seguido del nombre, en la misma celda |
| Distritos | str | 3.6 | >=50 | alta cardinalidad | Código del distrito (7 cifras) y nombre; vacío en las filas de municipio |
| Secciones | str | 8.5 | >=50 | alta cardinalidad | Código de la sección (10 cifras) y nombre; vacío en las filas de municipio y de distrito |
| Indicadores de renta media y mediana | str | 0.0 | 6 | top: Renta neta media por persona (17%)… | Indicador (6): renta neta media por persona y por hogar, media y mediana por unidad de consumo, y renta bruta media por persona y por hogar |
| Periodo | int | 0.0 | 5 | 2016..2024 (media 2020) | Año de referencia (2015 a 2024) |
| Total | mixto | 3.0 | >=50 | alta cardinalidad | Euros, con punto de miles; «.» = sin dato (secreto estadístico) |

## Primeras filas
| Municipios | Distritos | Secciones | Indicadores de renta media y mediana | Periodo | Total |
|---|---|---|---|---|---|
| 28001 Acebeda, La |  |  | Renta neta media por persona | 2024 | 17.216 |
| 28001 Acebeda, La |  |  | Renta neta media por persona | 2023 | 16.893 |
| 28001 Acebeda, La |  |  | Renta neta media por persona | 2022 | 15.715 |
| 28001 Acebeda, La |  |  | Renta neta media por persona | 2021 | 15.245 |
| 28001 Acebeda, La |  |  | Renta neta media por persona | 2020 | 13.999 |

## Muestra aleatoria
| Municipios | Distritos | Secciones | Indicadores de renta media y mediana | Periodo | Total |
|---|---|---|---|---|---|
| 28113 Pinto | 2811302 Pinto distrito 02 | 2811302016 Pinto sección 02016 | Renta neta media por persona | 2020 |  |
| 28049 Coslada | 2804904 Coslada distrito 04 | 2804904002 Coslada sección 04002 | Renta neta media por persona | 2022 | 12.646 |
| 28065 Getafe | 2806502 Getafe distrito 02 | 2806502003 Getafe sección 02003 | Renta neta media por persona | 2022 | 12.127 |
| 28167 Velilla de San Antonio | 2816701 Velilla de San Antonio distrito… | 2816701004 Velilla de San Antonio secci… | Renta bruta media por hogar | 2020 | 52.057 |
| 28079 Madrid | 2807905 Madrid distrito 05 | 2807905101 Madrid sección 05101 | Mediana de la renta por unidad de consu… | 2022 | 36.050 |

## Avisos
- 1 columnas con tipos mezclados: `Total`.

## Notas
(Escribe aqui lo que no sale del script; se conserva al regenerar.)
