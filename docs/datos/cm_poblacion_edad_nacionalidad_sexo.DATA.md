# cm_poblacion_edad_nacionalidad_sexo_2026-11-15.csv — diccionario de datos
<!-- datadict: size=15573665 mtime=1794740135 rows=189090 stride=1 sep='punto y coma' seed=42 generated=2026-11-15 10:57 UTC -->

- Filas: 189090 · Columnas: 10 · Tamano: 14.9 MB
- Separador: punto y coma · perfilado sobre las 189090 filas · semilla 42
- Origen: Comunidad de Madrid, catálogo de datos abiertos, `poblacion_censada_por_edad_nacionalidad_y_sexo` (Censo anual, INE); fila «Población por edad (catálogo)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Año | int | 0.0 | 5 | 2021..2025 (media 2023) | Año de referencia, a 1-1 (2021 a 2025) |
| Tipo territorio | str | 0.0 | 3 | top: Municipios (94%), Zonas Estadístic… | Municipios, Zonas Estadísticas o Comunidad de Madrid |
| Código territorio | int | 0.5 | >=50 | 1..9036 (media 993.895) | Código del territorio en el catálogo, leído como entero (vacío en la Comunidad) |
| Territorio | str | 0.0 | >=50 | alta cardinalidad | Nombre del territorio |
| Edad | str | 0.0 | 22 | top: Total (5%), De 0-4 años (5%), De 5… | «Total» o grupo de cinco años («De 0-4 años»…): 22 valores |
| Nacionalidad | str | 0.0 | 3 | top: Total (33%), Españoles (33%), Extr… | Total, Españoles o Extranjeros |
| Sexo | str | 0.0 | 3 | top: Total (33%), Hombres (33%), Mujere… | Total, Hombres o Mujeres |
| Valor | int | 0.0 | >=50 | 0..7.11389e+06 (media 4374.42) | Personas |
| Unidad | str | 0.0 | 1 | top: Número (100%) | Constante: «Número» |
| Estado dato | vacia | 100.0 | 0 |  | Vacía |

## Primeras filas
| Año | Tipo territorio | Código territorio | Territorio | Edad | Nacionalidad | Sexo | Valor | Unidad | Estado dato |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | Comunidad de Madrid |  | Comunidad de Madrid | Total | Total | Total | 6726640 | Número |  |
| 2021 | Municipios | 0014 | Acebeda (La) | Total | Total | Total | 55 | Número |  |
| 2021 | Municipios | 0029 | Ajalvir | Total | Total | Total | 4793 | Número |  |
| 2021 | Municipios | 0035 | Alameda del Valle | Total | Total | Total | 248 | Número |  |
| 2021 | Municipios | 0040 | Álamo (El) | Total | Total | Total | 9946 | Número |  |

## Muestra aleatoria
| Año | Tipo territorio | Código territorio | Territorio | Edad | Nacionalidad | Sexo | Valor | Unidad | Estado dato |
|---|---|---|---|---|---|---|---|---|---|
| 2022 | Zonas Estadísticas | 01 | Municipio de Madrid | De 5-9 años | Extranjeros | Total | 19168 | Número |  |
| 2025 | Municipios | 0409 | Ciempozuelos | De 5-9 años | Total | Hombres | 656 | Número |  |
| 2025 | Municipios | 1415 | Sevilla la Nueva | De 45-49 años | Total | Hombres | 511 | Número |  |
| 2021 | Municipios | 1356 | Santa María de la Alameda | De 100 y más años | Extranjeros | Total | 0 | Número |  |
| 2021 | Municipios | 0663 | Griñón | De 75-79 años | Total | Mujeres | 124 | Número |  |

## Avisos
- 1 columnas vacias: `Estado dato`.
- 1 columnas constantes: `Unidad`.

## Notas
- UTF-8 con BOM: leer con `encoding="utf-8-sig"`.
- Control de F0-04: en Getafe, 1-1-2025, los cinco grupos de 15 a 39 años del catálogo coinciden con la suma de edades simples del INE t=68542.
