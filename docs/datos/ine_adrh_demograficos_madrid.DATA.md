# ine_adrh_demograficos_madrid_2026-11-15.csv — diccionario de datos
<!-- datadict: size=42576727 mtime=1794699791 rows=350770 stride=2 sep='punto y coma' seed=42 generated=2026-11-14 23:47 UTC -->

- Filas: 350770 · Columnas: 6 · Tamano: 40.6 MB
- Separador: punto y coma · perfilado sobre 175385 de 350770 filas (1 de cada 2) · semilla 42
- Origen: INE, Atlas de Distribución de Renta de los Hogares (ADRH), tabla 31105 «Indicadores demográficos» de Madrid; fila «Población por sección (INE, ADRH)» de data/README.md

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| Municipios | str | 0.0 | >=50 | alta cardinalidad | Código INE del municipio (5 cifras) seguido del nombre, en la misma celda |
| Distritos | str | 3.6 | >=50 | alta cardinalidad | Código del distrito censal (7 cifras) y nombre; vacío en las filas de municipio |
| Secciones | str | 8.5 | >=50 | alta cardinalidad | Código de la sección censal (10 cifras) y nombre; vacío en las filas de municipio y de distrito |
| Indicadores demográficos | str | 0.0 | 7 | top: Edad media de la población (14%), … | Indicador (7): población, edad media, % menores de 18, % 65 y más, tamaño medio del hogar, % hogares unipersonales, % población española |
| Periodo | int | 0.0 | 5 | 2016..2024 (media 2020) | Año de referencia (2015 a 2024) |
| Total | mixto | 3.0 | >=50 | alta cardinalidad | Valor del indicador en formato español (punto de miles, coma decimal); «.» = sin dato |

## Primeras filas
| Municipios | Distritos | Secciones | Indicadores demográficos | Periodo | Total |
|---|---|---|---|---|---|
| 28001 Acebeda, La |  |  | Edad media de la población | 2024 | 59,9 |
| 28001 Acebeda, La |  |  | Edad media de la población | 2023 | 59,8 |
| 28001 Acebeda, La |  |  | Edad media de la población | 2022 | 62,2 |
| 28001 Acebeda, La |  |  | Edad media de la población | 2021 | 59,2 |
| 28001 Acebeda, La |  |  | Edad media de la población | 2020 | 59,5 |

## Muestra aleatoria
| Municipios | Distritos | Secciones | Indicadores demográficos | Periodo | Total |
|---|---|---|---|---|---|
| 28079 Madrid | 2807919 Madrid distrito 19 | 2807919044 Madrid sección 19044 | Porcentaje de población española | 2020 | 88,3 |
| 28045 Colmenar Viejo | 2804501 Colmenar Viejo distrito 01 | 2804501022 Colmenar Viejo sección 01022 | Porcentaje de hogares unipersonales | 2022 | 11,7 |
| 28058 Fuenlabrada | 2805804 Fuenlabrada distrito 04 | 2805804006 Fuenlabrada sección 04006 | Porcentaje de población de 65 y más años | 2022 | 14,7 |
| 28106 Parla | 2810601 Parla distrito 01 | 2810601022 Parla sección 01022 | Tamaño medio del hogar | 2020 | 3,1 |
| 28079 Madrid | 2807903 Madrid distrito 03 | 2807903059 Madrid sección 03059 | Tamaño medio del hogar | 2022 | 2,3 |

## Avisos
- 1 columnas con tipos mezclados: `Total`.
- 1 columnas con numeros en formato espanol (coma decimal o punto de miles): `Total`.

## Notas
- El fichero viene en UTF-8 con BOM, aunque el servidor declara ISO-8859-15: leer con `encoding="utf-8-sig"`.
- Mezcla filas de municipio, distrito y sección: filtrar por `Secciones` no vacía para el nivel de sección.
- La tabla lista 4.586 secciones (todas las de 2015 a 2024); en 2024 tienen «Población» 4.518, las mismas que el seccionado del INE a 1-1-2025, y su suma (6.995.318) coincide con la de los municipios (comprobado el 2026-11-15 sobre el fichero completo).
- `Periodo` sale con 5 años (2016 a 2024, pares) por el muestreo 1 de cada 2 sobre bloques ordenados; la tabla tiene de 2015 a 2024 (INE, Tabla.htm?t=31105).
- Los códigos oficiales, como texto: el código va antes del primer espacio.
