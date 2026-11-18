# esudb25p.csv — diccionario de datos
<!-- datadict: size=49201887 mtime=1776424146 rows=60825 stride=1 sep='coma' seed=42 generated=2026-11-18 07:58 UTC -->

- Filas: 60825 · Columnas: 253 · Tamano: 46.9 MB
- Separador: coma · perfilado sobre las 60825 filas · semilla 42
- Origen: INE, Encuesta de Condiciones de Vida 2025, microdatos transversales base 2013, datos detallados de los adultos (ECV_Tp), version CSV con comas; dentro de `ine_ecv_microdatos_2025_2026-11-18/` (descomprimido de `ine_ecv_microdatos_2025_2026-11-18.zip`). Significado de cada variable: disenos de registro `disreg_ecv25/dr_ECV_CM_*_2025.xlsx` y `dr_ECV_SM_*_2025.json` de la misma carpeta; la columna «Descripcion» copia la de la hoja «Diseño» del xlsx (entre paréntesis, el módulo donde empieza un bloque); los códigos de cada variable están en sus hojas «Tablas*»

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| PB010 | int | 0.0 | 1 | 2025..2025 (media 2025) | Año de la encuesta (INFORMACIÓN BÁSICA) |
| PB020 | str | 0.0 | 1 | top: ES (100%) | País |
| PB030 | int | 0.0 | >=50 | 101..3.75001e+06 (media 1.76195e+06) | Identificación transversal de la persona Se compone del identificador del hogar, HB030 y el nº de orden, a dos dígitos, de la persona dentro del hogar |
| PB040 | float | 0.0 | >=50 | 0..10163.1 (media 688.42) | Factor de ponderación personal transversal (todos los miembros del hogar de 16 años o más) |
| PB040_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si PB040 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB100 | mixto | 0.0 | 6 | top: 5 (31%), 4 (30%), 3 (22%) | Mes de la entrevista |
| PB100_F | int | 0.0 | 2 | -1..1 (media 0.978002) | Variable que indica si PB100 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB110 | int | 0.0 | 1 | 2025..2025 (media 2025) | Año de la entrevista |
| PB110_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si PB110 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB120 | mixto | 0.0 | >=50 | alta cardinalidad | Número de minutos empleados en cumplimentar el cuestionario |
| PB120_F | int | 0.0 | 2 | -1..1 (media 0.91635) | Variable que indica si PB120 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB140 | int | 0.0 | >=50 | 1939..2008 (media 1973.28) | Año de nacimiento |
| PB140_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si PB140 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB150 | int | 0.0 | 2 | 1..2 (media 1.52067) | Sexo |
| PB150_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si PB150 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB160 | mixto | 0.0 | >=50 | alta cardinalidad | Identificación del padre |
| PB160_F | int | 0.0 | 2 | -2..1 (media -1.5598) | Variable que indica si PB160 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB170 | mixto | 0.0 | >=50 | alta cardinalidad | Identificación de la madre |
| PB170_F | int | 0.0 | 2 | -2..1 (media -1.41307) | Variable que indica si PB170 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB180 | mixto | 0.0 | >=50 | alta cardinalidad | Identificación del cónyuge/pareja |
| PB180_F | int | 0.0 | 2 | -2..1 (media -0.275413) | Variable que indica si PB180 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB190 | mixto | 0.0 | 6 | top: 2 (51%), 1 (33%), 4 (7%) | Estado civil |
| PB190_F | int | 0.0 | 2 | -1..1 (media 0.976424) | Variable que indica si PB190 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB200 | mixto | 0.0 | 4 | top: 1 (52%), 3 (42%), 2 (5%) | Cónyuge o pareja de hecho |
| PB200_F | int | 0.0 | 2 | -1..1 (media 0.97626) | Variable que indica si PB200 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB205 | mixto | 0.0 | 3 | top: 1 (57%), 2 (42%),   (1%) | Con pareja viviendo en el mismo hogar |
| PB205_F | int | 0.0 | 2 | -1..1 (media 0.977937) | Variable que indica si PB205 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB230 | mixto | 0.0 | 4 | top: 1 (86%), 3 (10%), 2 (3%) | País de nacimiento del padre |
| PB230_F | int | 0.0 | 2 | -1..1 (media 0.977246) | Variable que indica si PB230 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PB240 | mixto | 0.0 | 4 | top: 1 (86%), 3 (10%), 2 (3%) | País de nacimiento de la madre |
| PB240_F | int | 0.0 | 2 | -1..1 (media 0.977246) | Variable que indica si PB240 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PE010 | mixto | 0.0 | 3 | top: 2 (87%), 1 (12%),   (1%) | ¿Está cursando actualmente algún tipo de estudios o de formación? (EDUCACIÓN, INCLUIDO EL NIVEL MÁS ALTO DE FORMACION ALCANZADO) |
| PE010_F | int | 0.0 | 2 | -1..1 (media 0.977312) | Variable que indica si PE010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PE021 | mixto | 0.0 | 9 | top:   (88%), 50 (7%), 34 (2%) | Nivel de los estudios que está realizando |
| PE021_F | int | 0.0 | 3 | -2..1 (media -1.64672) | Variable que indica si PE021 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PE041 | mixto | 0.0 | 11 | top: 500 (35%), 200 (22%), 100 (11%) | Nivel de los estudios terminados |
| PE041_F | int | 0.0 | 2 | -1..1 (media 0.976424) | Variable que indica si PE041 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL032 | mixto | 0.0 | 8 | top: 1 (51%), 3 (20%), 5 (9%) | Situación en relación con la actividad definida por el interesado (DATOS LABORALES BÁSICOS SOBRE LA SITUACIÓN LABORAL ACTUAL Y SOBRE EL TRABAJO PRINCIPAL ACTUAL (INCLUIDA INFORMACIÓN SOBRE EL ÚLTIMO TRABAJO PRINCIPAL EN EL CASO DE NO TRABAJAR EN LA ACTUALIDAD)) |
| PL032_F | int | 0.0 | 2 | -1..1 (media 0.993292) | Variable que indica si PL032 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL016 | mixto | 0.0 | 4 | top:   (51%), 3 (34%), 1 (12%) | ¿Ha trabajado alguna vez? |
| PL016_F | int | 0.0 | 3 | -2..1 (media -0.53432) | Variable que indica si PL016 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL040A | mixto | 0.0 | 5 | top:   (50%), 3 (43%), 2 (5%) | Situación profesional (último empleo principal) |
| PL040A_F | int | 0.0 | 3 | -2..1 (media -0.4885) | Variable que indica si PL040A está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL040B | mixto | 0.0 | 5 | top:   (67%), 3 (28%), 2 (3%) | Situación profesional (empleo principal actual) |
| PL040B_F | int | 0.0 | 3 | -2..1 (media -0.994821) | Variable que indica si PL040B está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL051A | mixto | 0.0 | 42 | top:   (50%), 52 (4%), 23 (4%) | Ocupación del empleo principal actual. Se proporciona según la clasificación internacional (ISCO08). |
| PL051A_F | int | 0.0 | 3 | -2..1 (media -0.489059) | Variable que indica si PL051A está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL051B | mixto | 0.0 | 42 | top:   (67%), 52 (3%), 91 (3%) | Ocupación del último empleo principal. Se proporciona según la clasificación internacional (ISCO08). |
| PL051B_F | int | 0.0 | 3 | -2..1 (media -0.996695) | Variable que indica si PL051B está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL060 | mixto | 0.0 | >=50 | alta cardinalidad | Número de horas trabajadas normalmente por semana en el trabajo principal |
| PL060_F | int | 0.0 | 4 | -6..1 (media -0.512569) | Variable que indica si PL060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL073 | mixto | 0.0 | 14 | top: 0 (58%), 12 (35%),   (1%) | Número de meses en que trabajó como asalariado a tiempo completo durante el período de referencia de la renta |
| PL073_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL073 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL074 | mixto | 0.0 | 14 | top: 0 (91%), 12 (6%),   (1%) | Número de meses en que trabajó como asalariado a tiempo parcial durante el período de referencia de la renta |
| PL074_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL074 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL075 | mixto | 0.0 | 14 | top: 0 (92%), 12 (6%),   (1%) | Número de meses en que trabajó por cuenta propia a tiempo completo durante el período de referencia de la renta |
| PL075_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL075 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL076 | mixto | 0.0 | 14 | top: 0 (98%),   (1%), 12 (1%) | Número de meses en que trabajó por cuenta propia a tiempo parcial durante el período de referencia de la renta |
| PL076_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL076 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL080 | mixto | 0.0 | 14 | top: 0 (88%), 12 (5%),   (1%) | Número de meses en situación de desempleo durante el período de referencia de la renta |
| PL080_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL085 | mixto | 0.0 | 14 | top: 0 (80%), 12 (18%),   (1%) | Número de meses jubilado durante el período de referencia de la renta |
| PL085_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL085 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL086 | mixto | 0.0 | 14 | top: 0 (96%), 12 (3%),   (1%) | Número de meses incapacitado permanente para trabajar durante el período de referencia de la renta |
| PL086_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL086 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL087 | mixto | 0.0 | 14 | top: 0 (89%), 12 (8%),   (1%) | Número de meses en los que ha estudiado durante el período de referencia de la renta |
| PL087_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL087 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL089 | mixto | 0.0 | 14 | top: 0 (91%), 12 (8%),   (1%) | Número de meses dedicado a las labores del hogar, cuidado de niños, etc. durante el período de referencia de la renta |
| PL089_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL089 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL090 | mixto | 0.0 | 14 | top: 0 (98%),   (1%), 12 (1%) | Número de meses en otra clase de inactividad económica durante el período de referencia de la renta |
| PL090_F | int | 0.0 | 2 | -1..1 (media 0.976194) | Variable que indica si PL090 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL100 | mixto | 0.0 | 29 | top:   (98%), 10 (0%), 20 (0%) | Número total de horas normalmente trabajadas en el segundo puesto de trabajo, tercero, etc. |
| PL100_F | int | 0.0 | 4 | -4..1 (media -2.93261) | Variable que indica si PL100 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL111AA | str | 0.0 | 22 | top:   (50%), g (7%), c (7%) | Actividad del establecimiento del que depende (empleo principal actual) |
| PL111AA_F | int | 0.0 | 3 | -2..1 (media -0.489322) | Variable que indica si PL111A está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL111BA | str | 0.0 | 22 | top:   (75%), c (4%), g (4%) | Actividad del establecimiento del que dependía (último empleo principal) |
| PL111BA_F | int | 0.0 | 3 | -2..1 (media -1.24878) | Variable que indica si PL111B está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL141 | mixto | 0.0 | 5 | top:   (58%), 21 (37%), 11 (5%) | Tipo de contrato (duración) |
| PL141_F | int | 0.0 | 3 | -2..1 (media -0.730308) | Variable que indica si PL141 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL145 | mixto | 0.0 | 3 | top:   (50%), 1 (43%), 2 (7%) | Tipo de contrato (duración) |
| PL145_F | int | 0.0 | 3 | -2..1 (media -0.488204) | Variable que indica si PL145 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL150 | mixto | 0.0 | 3 | top:   (58%), 2 (32%), 1 (11%) | ¿Supervisa/supervisaba o coordina/coordinaba el trabajo de algún empleado de la empresa u organismo en el que trabaja/trabajaba ? |
| PL150_F | int | 0.0 | 3 | -2..1 (media -0.726691) | Variable que indica si PL150 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL200 | mixto | 0.0 | >=50 | alta cardinalidad | Número de años pasados en trabajo remunerado |
| PL200_F | int | 0.0 | 3 | -2..1 (media 0.485771) | Variable que indica si PL200 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211A | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (10%) | Actividad principal en Enero |
| PL211A_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211A está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211B | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (10%) | Actividad principal en Febrero |
| PL211B_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211B está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211C | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (10%) | Actividad principal en Marzo |
| PL211C_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211C está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211D | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (9%) | Actividad principal en Abril |
| PL211D_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211D está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211E | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (9%) | Actividad principal en Mayo |
| PL211E_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211E está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211F | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (9%) | Actividad principal en Junio |
| PL211F_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211F está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211G | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (9%) | Actividad principal en Julio |
| PL211G_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211G está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211H | mixto | 0.0 | 11 | top: 1 (38%), 7 (18%), 6 (9%) | Actividad principal en Agosto |
| PL211H_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211H está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211I | mixto | 0.0 | 11 | top: 1 (38%), 7 (19%), 6 (9%) | Actividad principal en Septiembre |
| PL211I_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211I está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211J | mixto | 0.0 | 11 | top: 1 (38%), 7 (19%), 6 (9%) | Actividad principal en Octubre |
| PL211J_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211J está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211K | mixto | 0.0 | 11 | top: 1 (37%), 7 (19%), 6 (9%) | Actividad principal en Noviembre |
| PL211K_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211K está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL211L | mixto | 0.0 | 11 | top: 1 (37%), 7 (19%), 6 (9%) | Actividad principal en Diciembre |
| PL211L_F | int | 0.0 | 2 | -1..1 (media 0.976095) | Variable que indica si PL211L está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PL271 | mixto | 0.0 | >=50 | alta cardinalidad | Durante los últimos 5 años, número de meses en situación de parado |
| PL271_F | int | 0.0 | 3 | -2..1 (media 0.619137) | Variable que indica si PL271 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH010 | mixto | 0.0 | 6 | top: 2 (53%), 3 (22%), 1 (16%) | Estado general de salud (SALUD) |
| PH010_F | int | 0.0 | 2 | -1..1 (media 0.974879) | Variable que indica si PH010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH020 | mixto | 0.0 | 3 | top: 2 (61%), 1 (37%),   (1%) | ¿Tiene alguna enfermedad o problema de salud crónicos? |
| PH020_F | int | 0.0 | 2 | -1..1 (media 0.97409) | Variable que indica si PH020 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH030 | mixto | 0.0 | 4 | top: 3 (77%), 2 (16%), 1 (4%) | Durante al menos los últimos 6 meses, ¿en qué medida se ha visto limitado debido a un problema de salud para realizar las actividades que la gente habitualmente hace? |
| PH030_F | int | 0.0 | 2 | -1..1 (media 0.93746) | Variable que indica si PH030 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH040 | mixto | 0.0 | 3 | top: 2 (66%),   (31%), 1 (3%) | ¿Durante los últimos 12 meses, hubo alguna ocasión en la que realmente necesitó consultar a un médico (excepto dentista) pero no lo hizo? |
| PH040_F | int | 0.0 | 3 | -2..1 (media 0.0864776) | Variable que indica si PH040 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH050 | mixto | 0.0 | 9 | top:   (97%), 2 (2%), 8 (1%) | Motivo principal para no consultar a un médico (excepto dentista) |
| PH050_F | int | 0.0 | 3 | -2..1 (media -1.91903) | Variable que indica si PH050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH060 | mixto | 0.0 | 3 | top: 2 (48%),   (47%), 1 (4%) | ¿Durante los últimos 12 meses, hubo alguna ocasión en la que realmente necesitó consultar a un dentista pero no lo hizo? |
| PH060_F | int | 0.0 | 3 | -2..1 (media -0.403321) | Variable que indica si PH060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH070 | mixto | 0.0 | 9 | top:   (96%), 1 (3%), 8 (0%) | Motivo principal para no consultar a un dentista |
| PH070_F | int | 0.0 | 3 | -2..1 (media -1.86981) | Variable que indica si PH070 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PY010N | float | 0.0 | >=50 | 0..289248 (media 11390.9) | Renta neta monetaria o cuasi monetaria del asalariado en el año anterior al de encuesta (RENTA. SERIE DE RENTA PERSONAL NETA A ESCALA DE LOS COMPONENTES) |
| PY010N_F | int | 0.0 | 3 | 11..51 (media 20.5048) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY020N | float | 0.0 | >=50 | 0..27531.6 (media 114.677) | Renta neta no monetaria del asalariado en el año anterior al de encuesta |
| PY020N_F | int | 0.0 | 3 | 11..51 (media 19.3607) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY021N | float | 0.0 | >=50 | 0..23819.3 (media 23.3547) | Renta neta no monetaria del asalariado en el año anterior al de encuesta (coche de empresa) |
| PY021N_F | int | 0.0 | 3 | 11..51 (media 19.3152) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY035N | float | 0.0 | >=50 | 0..45000 (media 82.5064) | Aportaciones a planes de pensiones privados individuales en el año anterior al de encuesta |
| PY035N_F | int | 0.0 | 3 | 16..79 (media 16.9139) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY050N | float | 0.0 | >=50 | -36891.7..214538 (media 1332.7) | Beneficios o pérdidas monetarios netos de trabajadores por cuenta propia (incluidos derechos de propiedad intelectual) en el año anterior al de encuesta |
| PY050N_F | int | 0.0 | 5 | 11..55 (media 19.2238) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY080N | float | 0.0 | >=50 | 0..85457.3 (media 164.855) | Rentas netas percibidas de esquemas privados de pensiones (distintos de los incluidos en SEEPROS) en el año anterior al de encuesta |
| PY080N_F | int | 0.0 | 3 | 11..51 (media 19.3109) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY090N | float | 0.0 | >=50 | 0..144984 (media 490.099) | Prestaciones por desempleo (netas) en el año anterior al de encuesta |
| PY090N_F | int | 0.0 | 3 | 11..51 (media 19.2769) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY100N | float | 0.0 | >=50 | 0..93007.1 (media 3715.6) | Prestaciones por jubilación (netas) en el año anterior al de encuesta |
| PY100N_F | int | 0.0 | 3 | 11..51 (media 20.9637) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY110N | float | 0.0 | >=50 | 0..42325.5 (media 690.639) | Prestaciones por supervivencia (netas) en el año anterior al de encuesta |
| PY110N_F | int | 0.0 | 3 | 11..51 (media 20.9303) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY120N | float | 0.0 | >=50 | 0..27718.3 (media 85.3111) | Prestaciones por enfermedad (netas) en el año anterior al de encuesta |
| PY120N_F | int | 0.0 | 3 | 11..51 (media 19.3234) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY130N | float | 0.0 | >=50 | 0..58331.6 (media 425.689) | Prestaciones por invalidez (netas) en el año anterior al de encuesta |
| PY130N_F | int | 0.0 | 3 | 11..51 (media 20.9245) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY140N | float | 0.0 | >=50 | 0..16200 (media 40.6602) | Ayuda para estudios en el año anterior al de encuesta |
| PY140N_F | int | 0.0 | 3 | 11..79 (media 11.8926) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY010G | float | 0.0 | >=50 | 0..517586 (media 14806.6) | Renta bruta monetaria o cuasi monetaria del asalariado en el año anterior al de encuesta (RENTA.SERIE DE RENTA PERSONAL BRUTA A ESCALA DE LOS COMPONENTES) |
| PY010G_F | int | 0.0 | 4 | 15..55 (media 24.5356) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY020G | float | 0.0 | >=50 | 0..37163.7 (media 131.225) | Renta bruta no monetaria del asalariado en el año anterior al de encuesta |
| PY020G_F | int | 0.0 | 4 | 15..55 (media 23.3611) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY021G | float | 0.0 | >=50 | 0..29166.6 (media 27.0312) | Renta bruta no monetaria del asalariado en el año anterior al de encuesta |
| PY021G_F | int | 0.0 | 3 | 15..55 (media 23.3152) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY030G | float | 0.0 | >=50 | 0..85387.2 (media 4048.92) | Cotizaciones sociales a cargo del empleador en el año anterior al de encuesta |
| PY030G_F | int | 0.0 | 2 | 55..79 (media 55.264) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY035G | float | 0.0 | >=50 | 0..45000 (media 82.5064) | Aportaciones a planes de pensiones privados individuales en el año anterior al de encuesta |
| PY035G_F | int | 0.0 | 3 | 16..79 (media 16.9139) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY050G | float | 0.0 | >=50 | -29554.4..233496 (media 1739.43) | Beneficios o pérdidas monetarios brutos de trabajadores por cuenta propia (incluidos derechos de propiedad intelectual) en el año anterior al de encuesta |
| PY050G_F | int | 0.0 | 3 | 15..55 (media 23.1935) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY080G | float | 0.0 | >=50 | 0..131473 (media 177.474) | Rentas brutas percibidas de esquemas privados de pensiones (distintos de los incluidos en SEEPROS) en el año anterior al de encuesta |
| PY080G_F | int | 0.0 | 4 | 15..55 (media 23.3113) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY090G | float | 0.0 | >=50 | 0..147224 (media 510.545) | Prestaciones por desempleo (brutas) en el año anterior al de encuesta |
| PY090G_F | int | 0.0 | 4 | 15..55 (media 23.2773) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY100G | float | 0.0 | >=50 | 0..105607 (media 4245.99) | Prestaciones por jubilación (brutas) en el año anterior al de encuesta |
| PY100G_F | int | 0.0 | 3 | 15..55 (media 24.9637) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY110G | float | 0.0 | >=50 | 0..54994.3 (media 735.64) | Prestaciones por supervivencia (brutas) en el año anterior al de encuesta |
| PY110G_F | int | 0.0 | 3 | 15..55 (media 24.9303) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY120G | float | 0.0 | >=50 | 0..35113.7 (media 89.0848) | Prestaciones por enfermedad (brutas) en el año anterior al de encuesta |
| PY120G_F | int | 0.0 | 3 | 15..55 (media 23.3234) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY130G | float | 0.0 | >=50 | 0..58331.6 (media 437.676) | Prestaciones por invalidez (brutas) en el año anterior al de encuesta |
| PY130G_F | int | 0.0 | 3 | 15..55 (media 24.9245) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PY140G | float | 0.0 | >=50 | 0..16200 (media 40.7156) | Ayuda para estudios en el año anterior al de la encuesta |
| PY140G_F | int | 0.0 | 3 | 15..79 (media 15.8486) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| PD020 | mixto | 0.0 | 4 | top: 1 (89%), 2 (7%), 3 (2%) | ¿Sustituye las ropas estropeadas por otras nuevas (que no sean de segunda mano)? (PRIVACIÓN MATERIAL
y OTRAS) |
| PD020_F | int | 0.0 | 2 | -1..1 (media 0.977674) | Variable que indica si PD020 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PD030 | mixto | 0.0 | 4 | top: 1 (95%), 2 (3%), 3 (1%) | ¿Tiene dos pares de zapatos, (o un par adecuado para cualquier época del año)? |
| PD030_F | int | 0.0 | 2 | -1..1 (media 0.977707) | Variable que indica si PD030 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PD050 | mixto | 0.0 | 4 | top: 1 (81%), 3 (10%), 2 (8%) | ¿Se reúne con amigos y/o familiares para comer o tomar algo al menos una vez al mes? |
| PD050_F | int | 0.0 | 2 | -1..1 (media 0.976819) | Variable que indica si PD050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PD060 | mixto | 0.0 | 4 | top: 1 (60%), 3 (27%), 2 (12%) | ¿Participa regularmente en actividades de ocio tales como deportes, cine, conciertos etc.? |
| PD060_F | int | 0.0 | 2 | -1..1 (media 0.976621) | Variable que indica si PD060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PD070 | mixto | 0.0 | 4 | top: 1 (69%), 3 (16%), 2 (13%) | ¿Gasta una pequeña cantidad de dinero en usted mismo cada semana? |
| PD070_F | int | 0.0 | 2 | -1..1 (media 0.976621) | Variable que indica si PD070 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PD080 | mixto | 0.0 | 4 | top: 1 (92%), 3 (6%), 2 (1%) | ¿Dispone de conexión a internet (fija o móvil) para uso personal en el hogar? |
| PD080_F | int | 0.0 | 2 | -1..1 (media 0.977575) | Variable que indica si PD080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PW010 | mixto | 0.0 | 12 | top: 8 (27%), 7 (21%), 9 (11%) | Grado de satisfacción global con su vida en la actualidad (escala del 0 al 10) |
| PW010_F | int | 0.0 | 2 | -1..1 (media 0.942491) | Variable que indica si PW010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PW191 | mixto | 0.0 | 12 | top: 7 (19%), 5 (18%), 8 (17%) | Grado de confianza en la mayor parte de las personas (escala del 0 al 10) |
| PW191_F | int | 0.0 | 2 | -1..1 (media 0.940288) | Variable que indica si PW191 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH080 | mixto | 0.0 | 6 | top: 1 (42%), 2 (41%), 3 (10%) | Número de visitas al dentista u ortadoncista (MÓDULO: SALUD) |
| PH080_F | int | 0.0 | 2 | -1..1 (media 0.964324) | Variable que indica si PH080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH090 | mixto | 0.0 | 6 | top: 2 (39%), 3 (25%), 1 (18%) | Número de visitas al médico general o médico de familia |
| PH090_F | int | 0.0 | 2 | -1..1 (media 0.960871) | Variable que indica si PH090 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH100 | mixto | 0.0 | 6 | top: 1 (39%), 2 (35%), 3 (16%) | Número de visitas al médico especialista |
| PH100_F | int | 0.0 | 2 | -1..1 (media 0.961956) | Variable que indica si PH100 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH110 | mixto | 0.0 | 26 | top: 24 (11%), 23 (9%), 25 (9%) | Indice de masa corporal (16-40) |
| PH110_F | int | 0.0 | 2 | -1..1 (media 0.896424) | Variable que indica si PH110 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH122 | mixto | 0.0 | 5 | top:   (50%), 1 (21%), 2 (14%) | Tipo de actividad física en el trabajo |
| PH122_F | int | 0.0 | 3 | -2..1 (media -0.497904) | Variable que indica si PH122 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH132 | mixto | 0.0 | 7 | top: 4 (28%), 6 (22%), 2 (20%) | Frecuencia de actividad física |
| PH132_F | int | 0.0 | 2 | -1..1 (media 0.963962) | Variable que indica si PH132 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH142 | mixto | 0.0 | 7 | top: 2 (37%), 1 (26%), 4 (16%) | Frecuencia del consumo de fruta |
| PH142_F | int | 0.0 | 2 | -1..1 (media 0.962351) | Variable que indica si PH142 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH152 | mixto | 0.0 | 7 | top: 2 (34%), 3 (24%), 4 (24%) | Frecuencia del consumo de verduras |
| PH152_F | int | 0.0 | 2 | -1..1 (media 0.9612) | Variable que indica si PH152 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH101 | mixto | 0.0 | 5 | top: 1 (72%), 2 (23%), 3 (3%) | Dificultad para ver |
| PH101_F | int | 0.0 | 2 | -1..1 (media 0.964258) | Variable que indica si PH101 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH111 | mixto | 0.0 | 5 | top: 1 (84%), 2 (12%), 3 (2%) | Dificultad para oír |
| PH111_F | int | 0.0 | 2 | -1..1 (media 0.964159) | Variable que indica si PH111 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH121 | mixto | 0.0 | 5 | top: 1 (78%), 2 (14%), 3 (5%) | Dificultad para caminar |
| PH121_F | int | 0.0 | 2 | -1..1 (media 0.963798) | Variable que indica si PH121 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH131 | mixto | 0.0 | 5 | top: 1 (77%), 2 (17%), 3 (3%) | Dificultad para recordar o concentrarse |
| PH131_F | int | 0.0 | 2 | -1..1 (media 0.963732) | Variable que indica si PH131 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH141 | mixto | 0.0 | 5 | top: 1 (91%), 2 (5%),   (2%) | Dificultad para el cuidado personal |
| PH141_F | int | 0.0 | 2 | -1..1 (media 0.964028) | Variable que indica si PH141 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH151 | mixto | 0.0 | 5 | top: 1 (94%), 2 (3%),   (2%) | Dificultad paea comunicarse |
| PH151_F | int | 0.0 | 2 | -1..1 (media 0.964225) | Variable que indica si PH151 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH171 | mixto | 0.0 | 6 | top: 5 (77%), 1 (15%), 2 (3%) | Frecuencia de consumo de tabaco |
| PH171_F | int | 0.0 | 2 | -1..1 (media 0.963042) | Variable que indica si PH171 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PH180 | mixto | 0.0 | 6 | top: 5 (32%), 2 (24%), 3 (20%) | Frecuencia de consumo de bebidas alcohólicas |
| PH180_F | int | 0.0 | 2 | -1..1 (media 0.962022) | Variable que indica si PH180 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PW201 | mixto | 0.0 | 12 | top: 8 (21%), 7 (17%), 10 (15%) | Grado de satisfacción con los espacios verdes públicos de la zona en la que vive (escala del 0 al 10) (MÓDULO: ENERGÍA Y MEDIOAMBIENTE) |
| PW201_F | int | 0.0 | 2 | -1..1 (media 0.940156) | Variable que indica si PW201 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE08 | mixto | 0.0 | 3 | top: 2 (89%), 1 (9%),   (2%) | ¿Su vivienda sufrió daños por feómenos meteorológicos extremos u otras causas climáticas adversas? |
| PEE08_F | int | 0.0 | 2 | -1..1 (media 0.962877) | Variable que indica si PEE08 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE10 | mixto | 0.0 | 5 | top: 2 (60%), 1 (33%), 3 (4%) | Frecuencia de consumo de carne, aves o pescado |
| PEE10_F | int | 0.0 | 2 | -1..1 (media 0.961463) | Variable que indica si PEE10 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE20 | mixto | 0.0 | 4 | top: 2 (55%), 1 (26%), 3 (17%) | ¿Ha intentado reparar su teléfono móvil cuando se le ha roto? |
| PEE20_F | int | 0.0 | 2 | -1..1 (media 0.959819) | Variable que indica si PEE20 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE21 | mixto | 0.0 | 7 | top: 1 (51%), 5 (16%), 3 (15%) | ¿Qué hizo con su teléfono móvil cuando lo sustituyó o dejó de utilizarlo? |
| PEE21_F | int | 0.0 | 2 | -1..1 (media 0.954361) | Variable que indica si PEE21 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE03 | mixto | 0.0 | 4 | top:   (42%), 1 (40%), 2 (16%) | ¿Puede llegar a su trabajo, escuela o universidad en una hora desde su vivienda en transporte público, bicicleta o caminando? |
| PEE03_F | int | 0.0 | 3 | -2..1 (media -0.251574) | Variable que indica si PEE03 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE04 | mixto | 0.0 | 7 | top: 1 (55%), 2 (22%), 5 (16%) | Medio de transporte utilizado con más frecuencia |
| PEE04_F | int | 0.0 | 2 | -1..1 (media 0.951237) | Variable que indica si PEE04 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE05 | mixto | 0.0 | 7 | top: 5 (34%), 2 (20%), 6 (18%) | Segundo medio de transporte utilizado con más frecuencia |
| PEE05_F | int | 0.0 | 3 | -2..1 (media 0.897624) | Variable que indica si PEE05 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE15 | mixto | 0.0 | 5 | top: 4 (68%), 1 (15%), 2 (9%) | Número de vuelos particulares y de negocios realizados dentro de Europa |
| PEE15_F | int | 0.0 | 2 | -1..1 (media 0.938249) | Variable que indica si PEE15 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE16 | mixto | 0.0 | 5 | top: 4 (87%), 1 (7%),   (4%) | Número de vuelos particulares y de negocios realizados fuera de Europa |
| PEE16_F | int | 0.0 | 2 | -1..1 (media 0.927859) | Variable que indica si PEE16 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PEE17 | mixto | 0.0 | 37 | top: 0 (45%), 2 (9%), 1 (9%) | Número de horas que dedica a conducir un coche no eléctrico en una semana normal |
| PEE17_F | int | 0.0 | 2 | -1..1 (media 0.883009) | Variable que indica si PEE17 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| PMG1 | mixto | 0.0 | 6 | top: 5 (92%), 1 (5%),   (2%) | ¿Ha tenido en algún momento dificultades para acceder a una vivienda? (MÓDULO: DIFICULTADES DE ACCESO A LA VIVIENDA) |
| PMG2 | mixto | 0.0 | 9 | top:   (94%), 7 (3%), 8 (1%) | ¿Cuál fue la razón principal de esas dificultades para acceder a una vivienda? |
| PMG3 | mixto | 0.0 | 3 | top:   (86%), 6 (12%), 1 (2%) | En los últimos 12 meses, ¿ha tenido dificultades en el pago del recibo del alquiler de su vivienda principal debido a dificultades económicas? |
| PMG4 | mixto | 0.0 | 3 | top: 1 (95%), 6 (3%),   (1%) | Hace 12 meses, ¿residía en la misma vivienda que en la actualidad? |
| PMG5 | mixto | 0.0 | 3 | top: 6 (89%), 1 (6%),   (5%) | En los últimos 12 meses, ¿ha buscado activamente un alojamiento distinto a aquel en el que reside actualmente? |
| PMG6 | mixto | 0.0 | 7 | top:   (94%), 1 (4%), 6 (1%) | ¿Cuál es la razón principal por la que no se cambió de vivienda? |
| PMG7 | mixto | 0.0 | 7 | top:   (97%), 6 (2%), 4 (0%) | ¿Cuál es la razón principal por la que se cambió de vivienda? |
| PMG8 | mixto | 0.0 | 8 | top:   (86%), 1 (7%), 2 (3%) | ¿Cuál es la razón principal por la que en la actualidad convive con su padre/madre? (solo para personas entre 17 y 34 años que conviven con alguno de sus progenitores) |

## Primeras filas (primeras 15 de 253 columnas)
| PB010 | PB020 | PB030 | PB040 | PB040_F | PB100 | PB100_F | PB110 | PB110_F | PB120 | PB120_F | PB140 | PB140_F | PB150 | PB150_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 101 | 628.74024 | 1 | 4 | 1 | 2025 | 1 | 30 | 1 | 1948 | 1 | 2 | 1 |
| 2025 | ES | 201 | 284.14572 | 1 | 3 | 1 | 2025 | 1 | 16 | 1 | 1973 | 1 | 1 | 1 |
| 2025 | ES | 202 | 283.2434 | 1 | 3 | 1 | 2025 | 1 | 11 | 1 | 1974 | 1 | 2 | 1 |
| 2025 | ES | 301 | 727.51987 | 1 | 6 | 1 | 2025 | 1 | 5 | 1 | 1954 | 1 | 2 | 1 |
| 2025 | ES | 302 | 721.0198 | 1 | 6 | 1 | 2025 | 1 | 11 | 1 | 1950 | 1 | 1 | 1 |

## Muestra aleatoria (primeras 15 de 253 columnas)
| PB010 | PB020 | PB030 | PB040 | PB040_F | PB100 | PB100_F | PB110 | PB110_F | PB120 | PB120_F | PB140 | PB140_F | PB150 | PB150_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 990901 | 354.55983 | 1 | 4 | 1 | 2025 | 1 | 15 | 1 | 1962 | 1 | 2 | 1 |
| 2025 | ES | 1239101 | 870.57506 | 1 | 5 | 1 | 2025 | 1 | 21 | 1 | 1976 | 1 | 2 | 1 |
| 2025 | ES | 1629402 | 3404.74903 | 1 | 4 | 1 | 2025 | 1 | 6 | 1 | 1999 | 1 | 2 | 1 |
| 2025 | ES | 3676003 | 458.69153 | 1 | 4 | 1 | 2025 | 1 | 82 | 1 | 1994 | 1 | 1 | 1 |
| 2025 | ES | 3428501 | 233.91557 | 1 | 4 | 1 | 2025 | 1 | 13 | 1 | 1948 | 1 | 1 | 1 |

## Avisos
- 98 columnas con tipos mezclados: `PB100`, `PB120`, `PB160`, `PB170`, `PB180`, `PB190`, `PB200`, `PB205` y 90 mas.
- 7 columnas constantes: `PB010`, `PB020`, `PB040_F`, `PB110`, `PB110_F`, `PB140_F`, `PB150_F`.

## Notas
- Cada columna con sufijo `_F` es la bandera de calidad de la variable sin sufijo.
- Region de residencia (`DB040`, p. ej. ES30 = Madrid) esta en el fichero D (`ECV_Td_2025/CSV/esudb25d.csv`, 1 MB); se une con `HB030` (hogar) de H.
