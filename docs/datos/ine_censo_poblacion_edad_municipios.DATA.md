# ine_censo_poblacion_edad_municipios_2026-11-15.csv — diccionario de datos
<!-- datadict: size=895553731 mtime=1794740200 rows=12523050 stride=63 sep='punto y coma' seed=42 generated=2026-11-15 10:57 UTC -->

- Filas: 12523050 · Columnas: 7 · Tamano: 854.1 MB
- Separador: punto y coma · perfilado sobre 198779 de 12523050 filas (1 de cada 63) · semilla 42
- Origen: INE, Censo anual de población, tabla 68542 «Población por sexo y edad (año a año)» por municipios; fila de data/README.md «Población por edad (INE, t=68542)»

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Total Nacional | str | 0.0 | 1 | top: Total Nacional (100%) | Constante: «Total Nacional» |
| Provincias | str | 0.0 | >=50 | alta cardinalidad | Código y nombre de la provincia; vacío en las filas del total nacional |
| Municipios | str | 0.6 | >=50 | alta cardinalidad | Código INE (5 cifras) y nombre en la misma celda; vacío en las filas de provincia y de total |
| Sexo | str | 0.0 | 3 | top: Hombres (34%), Mujeres (34%), Tota… | Hombres, Mujeres o Total |
| Edad | str | 0.0 | >=50 | alta cardinalidad | «Todas las edades» o edad simple («18 años», «100 y más años»): 102 valores |
| Periodo | int | 0.0 | 5 | 2021..2025 (media 2023) | Año de referencia, a 1-1 (2021 a 2025) |
| Total | mixto | 0.0 | >=50 | alta cardinalidad | Personas, con punto de miles; puede venir vacío o «.» sin dato |

## Primeras filas
| Total Nacional | Provincias | Municipios | Sexo | Edad | Periodo | Total |
|---|---|---|---|---|---|---|
| Total Nacional |  |  | Hombres | Todas las edades | 2025 | 24.090.369 |
| Total Nacional |  |  | Hombres | Todas las edades | 2024 | 23.826.871 |
| Total Nacional |  |  | Hombres | Todas las edades | 2023 | 23.565.593 |
| Total Nacional |  |  | Hombres | Todas las edades | 2022 | 23.288.747 |
| Total Nacional |  |  | Hombres | Todas las edades | 2021 | 23.248.611 |

## Muestra aleatoria
| Total Nacional | Provincias | Municipios | Sexo | Edad | Periodo | Total |
|---|---|---|---|---|---|---|
| Total Nacional | 34 Palencia | 34904 Pernía, La | Total | 0 años | 2024 | 2 |
| Total Nacional | 08 Barcelona | 08067 Centelles | Mujeres | 89 años | 2022 | 17 |
| Total Nacional | 09 Burgos | 09043 Barrios de Bureba, Los | Total | 41 años | 2022 | 0 |
| Total Nacional | 40 Segovia | 40136 Muñoveros | Total | 81 años | 2024 | 2 |
| Total Nacional | 16 Cuenca | 16051 Cañaveruelas | Mujeres | 44 años | 2022 | 1 |

## Avisos
- 1 columnas con tipos mezclados: `Total`.
- 1 columnas constantes: `Total Nacional`.

## Notas
- Es nacional: todos los municipios de España, no solo los de Madrid. Filtrar por el código del municipio (28xxx) antes de cargar.
- UTF-8 con BOM: leer con `encoding="utf-8-sig"`.
- La suma de 18 a 35 años de Getafe a 1-1-2025 da 38.462 (control de F0-04).
- Los códigos oficiales, como texto: el código va antes del primer espacio.
