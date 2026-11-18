# esudb25r.csv — diccionario de datos
<!-- datadict: size=9266625 mtime=1776424146 rows=71398 stride=1 sep='coma' seed=42 generated=2026-11-18 07:58 UTC -->

- Filas: 71398 · Columnas: 46 · Tamano: 8.8 MB
- Separador: coma · perfilado sobre las 71398 filas · semilla 42
- Origen: INE, Encuesta de Condiciones de Vida 2025, microdatos transversales base 2013, datos basicos de la persona (ECV_Tr), version CSV con comas; dentro de `ine_ecv_microdatos_2025_2026-11-18/` (descomprimido de `ine_ecv_microdatos_2025_2026-11-18.zip`). Significado de cada variable: disenos de registro `disreg_ecv25/dr_ECV_CM_*_2025.xlsx` y `dr_ECV_SM_*_2025.json` de la misma carpeta; la columna «Descripcion» copia la de la hoja «Diseño» del xlsx (entre paréntesis, el módulo donde empieza un bloque); los códigos de cada variable están en sus hojas «Tablas*»

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| RB010 | int | 0.0 | 1 | 2025..2025 (media 2025) | Año de la encuesta (INFORMACIÓN BÁSICA) |
| RB020 | str | 0.0 | 1 | top: ES (100%) | País |
| RB030 | int | 0.0 | >=50 | 101..3.75001e+06 (media 1.76251e+06) | Identificador transversal de la persona Se compone del identificador del hogar, DB030, y el nº de orden, a dos dígitos, de la persona dentro del hogar |
| RB050 | float | 0.0 | >=50 | 13.1006..10103.1 (media 682.123) | Factor de ponderación transversal |
| RB050_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB080 | int | 0.0 | >=50 | 1939..2025 (media 1979.54) | Año de nacimiento |
| RB080_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB081 | int | 0.0 | >=50 | -1..85 (media 44.4626) | Edad a 31 de diciembre del año anterior al de la encuesta |
| RB081_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB081 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB082 | int | 0.0 | >=50 | -1..86 (media 44.7802) | Edad en la fecha de la entrevista |
| RB082_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB082 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB090 | int | 0.0 | 2 | 1..2 (media 1.51597) | Sexo |
| RB090_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB090 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB200 | mixto | 0.0 | 3 | top: 1 (98%), 2 (2%),   (0%) | Situación respecto a la residencia en el hogar |
| RB200_F | int | 0.0 | 2 | -1..1 (media 0.994426) | Variable que indica si RB200 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB211 | mixto | 0.0 | 8 | top: 1 (43%), 5 (22%), 3 (18%) | ¿Cuál de las siguientes fue su situación en la actividad en la actualidad? |
| RB211_F | int | 0.0 | 2 | -1..1 (media 0.99563) | Variable que indica si RB211 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB220 | mixto | 0.0 | >=50 | alta cardinalidad | Identificador del padre |
| RB220_F | int | 0.0 | 2 | -2..1 (media -1.24893) | Variable que indica si RB220 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB230 | mixto | 0.0 | >=50 | alta cardinalidad | Identificador de la madre |
| RB230_F | int | 0.0 | 2 | -2..1 (media -1.07527) | Variable que indica si RB230 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB240 | mixto | 0.0 | >=50 | alta cardinalidad | Identificador del cónyuge o pareja |
| RB240_F | int | 0.0 | 2 | -2..1 (media -0.530799) | Variable que indica si RB240 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB280 | int | 0.0 | 3 | 1..3 (media 1.20027) | Pais de nacimiento |
| RB280_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB280 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RB290 | int | 0.0 | 3 | 1..3 (media 1.11205) | Nacionalidad |
| RB290_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si RB290 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL010 | mixto | 0.0 | 47 | top:   (96%), 25 (1%), 0 (1%) | Número de horas en una semana normal que ha sido cuidado o ha asistido a centros de educación preescolar o infantil (CUIDADO DE NIÑOS) |
| RL010_F | int | 0.0 | 2 | -2..1 (media -1.87605) | Variable que indica si RL010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL020 | mixto | 0.0 | 37 | top:   (93%), 25 (2%), 30 (1%) | Número de horas en una semana normal que ha sido cuidado en centros de educación obligatoria (primaria o secundaria) |
| RL020_F | int | 0.0 | 2 | -2..1 (media -1.79483) | Variable que indica si RL020 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL030 | mixto | 0.0 | 23 | top:   (90%), 0 (9%), 5 (0%) | Número de horas en una semana normal que ha sido cuidado en centros de cuidado de niños fuera del horario escolar (antes o después del horario escolar aunque sea dentro del mismo centro) |
| RL030_F | int | 0.0 | 2 | -2..1 (media -1.69071) | Variable que indica si RL030 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL040 | mixto | 0.0 | 18 | top:   (89%), 0 (11%), 2 (0%) | Número de horas en una semana normal que ha sido cuidado en otros centros de cuidado de niños |
| RL040_F | int | 0.0 | 2 | -2..1 (media -1.67087) | Variable que indica si RL040 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL050 | mixto | 0.0 | 19 | top:   (89%), 0 (11%), 1 (0%) | Número de horas en una semana normal que ha sido cuidado por cuidadores profesionales remunerados en casa del niño o del cuidador (niñeras, asistentas, etc.) |
| RL050_F | int | 0.0 | 2 | -2..1 (media -1.67087) | Variable que indica si RL050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL060 | mixto | 0.0 | 38 | top:   (89%), 0 (10%), 10 (0%) | Número de horas en una semana normal que ha sido sido cuidado por otras personas sin remunerar (abuelos, otros miembros que no sean los padres, otros parientes, amigos, vecinos etc.) |
| RL060_F | int | 0.0 | 2 | -2..1 (media -1.67087) | Variable que indica si RL060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| RL070 | mixto | 0.0 | >=50 | alta cardinalidad | Peso transversal para los niños (para el cuidado de niños) |
| RL070_F | int | 0.0 | 2 | -2..1 (media -1.67087) | Variable que indica si RL070 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| vrLOWJOB | int | 0.0 | 3 | 0..9 (media 2.68495) | Personas en hogares sin empleo o con baja intensidad en el empleo (estrategia Europa 2020) (1) (VARIABLES DERIVADAS) |
| vrEU2020 | int | 0.0 | 2 | 0..1 (media 0.219782) | Personas en riesgo de pobreza o exclusión social (estrategia Europa 2020). (2) |
| vrMATSOCDEP | mixto | 0.0 | 3 | top: 0 (92%), 1 (7%),   (1%) | Personas en carencia material y social severa (3) |
| vrLOWJOB_nuevo | int | 0.0 | 3 | 0..9 (media 2.15793) | Personas en hogares sin empleo o con baja intensidad en el empleo (objetivo Europa 2030) (4) |
| vrEU2030_nuevo | int | 0.0 | 2 | 0..1 (media 0.221547) | Personas en riesgo de pobreza o exclusión social (objetivo Europa 2030). (5) |

## Primeras filas (primeras 15 de 46 columnas)
| RB010 | RB020 | RB030 | RB050 | RB050_F | RB080 | RB080_F | RB081 | RB081_F | RB082 | RB082_F | RB090 | RB090_F | RB200 | RB200_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 101 | 623.81237 | 1 | 1948 | 1 | 76 | 1 | 77 | 1 | 2 | 1 | 1 | 1 |
| 2025 | ES | 201 | 279.26707 | 1 | 1973 | 1 | 51 | 1 | 51 | 1 | 1 | 1 | 1 | 1 |
| 2025 | ES | 202 | 279.26707 | 1 | 1974 | 1 | 50 | 1 | 50 | 1 | 2 | 1 | 1 | 1 |
| 2025 | ES | 301 | 719.41894 | 1 | 1954 | 1 | 70 | 1 | 71 | 1 | 2 | 1 | 1 | 1 |
| 2025 | ES | 302 | 719.41894 | 1 | 1950 | 1 | 74 | 1 | 74 | 1 | 1 | 1 | 1 | 1 |

## Muestra aleatoria (primeras 15 de 46 columnas)
| RB010 | RB020 | RB030 | RB050 | RB050_F | RB080 | RB080_F | RB081 | RB081_F | RB082 | RB082_F | RB090 | RB090_F | RB200 | RB200_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 843904 | 1896.39634 | 1 | 2017 | 1 | 7 | 1 | 8 | 1 | 1 | 1 | 1 | 1 |
| 2025 | ES | 1058601 | 669.57499 | 1 | 1973 | 1 | 51 | 1 | 51 | 1 | 2 | 1 | 1 | 1 |
| 2025 | ES | 1378701 | 474.24276 | 1 | 1967 | 1 | 57 | 1 | 58 | 1 | 1 | 1 | 1 | 1 |
| 2025 | ES | 3101301 | 1353.47547 | 1 | 1992 | 1 | 32 | 1 | 32 | 1 | 1 | 1 | 1 | 1 |
| 2025 | ES | 2815001 | 724.05452 | 1 | 1984 | 1 | 40 | 1 | 40 | 1 | 1 | 1 | 1 | 1 |

## Avisos
- 13 columnas con tipos mezclados: `RB200`, `RB211`, `RB220`, `RB230`, `RB240`, `RL010`, `RL020`, `RL030` y 5 mas.
- 9 columnas constantes: `RB010`, `RB020`, `RB050_F`, `RB080_F`, `RB081_F`, `RB082_F`, `RB090_F`, `RB280_F` y 1 mas.

## Notas
- Cada columna con sufijo `_F` es la bandera de calidad de la variable sin sufijo.
- Region de residencia (`DB040`, p. ej. ES30 = Madrid) esta en el fichero D (`ECV_Td_2025/CSV/esudb25d.csv`, 1 MB); se une con `HB030` (hogar) de H.
