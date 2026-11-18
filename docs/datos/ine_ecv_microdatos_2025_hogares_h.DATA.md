# esudb25h.csv — diccionario de datos
<!-- datadict: size=20674115 mtime=1776765196 rows=29369 stride=1 sep='coma' seed=42 generated=2026-11-18 07:58 UTC -->

- Filas: 29369 · Columnas: 156 · Tamano: 19.7 MB
- Separador: coma · perfilado sobre las 29369 filas · semilla 42
- Origen: INE, Encuesta de Condiciones de Vida 2025, microdatos transversales base 2013, datos detallados del hogar (ECV_Th), version CSV con comas; dentro de `ine_ecv_microdatos_2025_2026-11-18/` (descomprimido de `ine_ecv_microdatos_2025_2026-11-18.zip`). Significado de cada variable: disenos de registro `disreg_ecv25/dr_ECV_CM_*_2025.xlsx` y `dr_ECV_SM_*_2025.json` de la misma carpeta; la columna «Descripcion» copia la de la hoja «Diseño» del xlsx (entre paréntesis, el módulo donde empieza un bloque); los códigos de cada variable están en sus hojas «Tablas*»

## Columnas
| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |
|---|---|---|---|---|---|
| HB010 | int | 0.0 | 1 | 2025..2025 (media 2025) | Año de la encuesta (INFORMACIÓN BÁSICA) |
| HB020 | str | 0.0 | 1 | top: ES (100%) | País |
| HB030 | int | 0.0 | >=50 | 1..37500 (media 17607.5) | Identificación transversal del hogar |
| HB050 | int | 0.0 | 5 | 2..6 (media 4.3392) | Mes de la entrevista al hogar |
| HB050_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HB050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HB060 | int | 0.0 | 1 | 2025..2025 (media 2025) | Año de la entrevista al hogar |
| HB060_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HB060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HB070 | mixto | 0.0 | >=50 | alta cardinalidad | Identificación personal del informante |
| HB070_F | int | 0.0 | 2 | -1..1 (media 0.938438) | Variable que indica si HB070 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HB080 | int | 0.0 | >=50 | 101..3.75e+06 (media 1.76075e+06) | Identificación de la primera persona responsable de la vivienda |
| HB080_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HB080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HB100 | mixto | 0.0 | >=50 | alta cardinalidad | Número de minutos empleados en cumplimentar el cuestionario sobre el hogar |
| HB100_F | int | 0.0 | 2 | -1..1 (media 0.935851) | Variable que indica si HB100 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HB120 | int | 0.0 | 12 | 1..13 (media 2.43107) | Número de miembros del hogar |
| HB120_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HB120 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HY020 | float | 0.0 | >=50 | -28024.3..522875 (media 39896.3) | Renta disponible total del hogar en el año anterior al de encuesta (nota: esta variable contiene las rentas percibidas de esquemas privados de pensiones) (RENTA
(incluye varios apartados)) |
| HY020_F | int | 0.0 | 3 | 11..51 (media 21.4209) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY022 | float | 0.0 | >=50 | -28024.3..522875 (media 37312) | Renta disponible total del hogar antes de transferencias sociales excepto prestaciones por jubilación y por supervivencia en el año anterior al de encuesta |
| HY022_F | int | 0.0 | 3 | 11..51 (media 21.4021) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY023 | float | 0.0 | >=50 | -34757.4..511364 (media 28186.4) | Renta disponible total del hogar antes de transferencias sociales incluidas prestaciones por jubilación y por supervivencia en el año anterior al de encuesta |
| HY023_F | int | 0.0 | 3 | 11..51 (media 21.3432) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY030N | float | 0.0 | >=50 | 0..22395.7 (media 6601.95) | Alquiler imputado (El alquiler imputado se aplica a los hogares que no pagan un alquiler completo por ser propietarios o por ocupar una vivienda alquilada a un precio inferior al de mercado o a título gratuito. El valor que se imputa es el equivalente al alquiler que se pagaría en el mercado por una vivienda similar a la ocupada, menos cualquier alquiler realmente abonado). (RENTA:
SERIE DE VARIABLES DE RENTA NETAS) |
| HY030N_F | int | 0.0 | 1 | 56..56 (media 56) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY040N | float | 0.0 | >=50 | 0..49956 (media 1011.11) | Renta neta procedente del alquiler de una propiedad o terreno en el año anterior al de encuesta |
| HY040N_F | int | 0.0 | 3 | 11..51 (media 12.7348) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY050N | float | 0.0 | >=50 | 0..42000 (media 154.828) | Ayuda por familia/hijos en el año anterior al de la enc |
| HY050N_F | int | 0.0 | 2 | 11..51 (media 11.1239) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY060N | float | 0.0 | >=50 | 0..50227.3 (media 233.243) | Ingresos por asistencia social en el año anterior al de encuesta |
| HY060N_F | int | 0.0 | 3 | 11..51 (media 11.4992) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY070N | float | 0.0 | >=50 | 0..13200 (media 38.729) | Ayuda para vivienda en el año anterior al de encuesta |
| HY070N_F | int | 0.0 | 2 | 11..51 (media 11.1253) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY080N | float | 0.0 | >=50 | 0..51012 (media 173.86) | Transferencias periódicas monetarias percibidas de otros hogares en el año anterior al de encuesta |
| HY080N_F | int | 0.0 | 2 | 16..56 (media 16.094) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY081N | float | 0.0 | >=50 | 0..51012 (media 114.495) | Transferencias periódicas monetarias percibidas de otros hogares en el año anterior al de encuesta (pensiones alimenticias a hijos o compensatorias a cónyuges) |
| HY081N_F | int | 0.0 | 2 | 16..56 (media 16.0518) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY090N | float | 0.0 | >=50 | 0..69678.6 (media 806.119) | Intereses, dividendos y ganancias netos de inversiones de capital en empresas no constituidas en sociedad en el año anterior al de encuesta |
| HY090N_F | int | 0.0 | 3 | 11..51 (media 20.8137) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY100N | float | 0.0 | >=50 | 0..18197.5 (media 606.861) | Intereses pagados del préstamo para la compra de la vivienda principal, en el año anterior al de encuesta |
| HY100N_F | int | 0.0 | 2 | 11..51 (media 12.155) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY110N | float | 0.0 | >=50 | 0..18000 (media 23.5455) | Renta neta percibida por los menores de 16 años en el año anterior al de encuesta |
| HY110N_F | int | 0.0 | 2 | 11..51 (media 11.0259) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY120N | float | 0.0 | >=50 | 0..17944 (media 356.585) | Impuesto sobre el patrimonio en el año anterior al de la encuesta |
| HY120N_F | int | 0.0 | 2 | 11..51 (media 11.0191) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY130N | float | 0.0 | >=50 | 0..25400 (media 285.547) | Transferencias periódicas monetarias abonadas a otros hogares en el año anterior al de encuesta |
| HY130N_F | int | 0.0 | 2 | 16..56 (media 16.1961) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY131N | float | 0.0 | >=50 | 0..24000 (media 164.656) | Transferencias periódicas monetarias abonadas a otros hogares en el año anterior al de encuesta (pensiones alimenticias a hijos o compensatorias a cónyuges) |
| HY131N_F | int | 0.0 | 2 | 16..56 (media 16.0913) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY145N | float | 0.0 | >=50 | -16855.8..49080.1 (media -72.8505) | Devoluciones/ingresos complementarios por ajustes En impuestos en el año anterior al de encuesta (declaración del IRPF) |
| HY145N_F | int | 0.0 | 2 | 11..21 (media 19.7708) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY170N | float | 0.0 | >=50 | 0..4570 (media 34.7508) | Autoconsumo en el año anterior al de encuesta |
| HY170N_F | int | 0.0 | 2 | 16..56 (media 16.0054) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY010 | float | 0.0 | >=50 | -27862.4..780425 (media 49942.4) | Renta bruta total del hogar en el año anterior al de encuesta (RENTA:
SERIE DE VARIABLES DE RENTA BRUTAS) |
| HY010_F | int | 0.0 | 4 | 15..55 (media 25.221) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY040G | float | 0.0 | >=50 | 0..65562.8 (media 1092.16) | Renta bruta procedente del alquiler de una propiedad o terreno en el año anterior al de encuesta |
| HY040G_F | int | 0.0 | 3 | 15..55 (media 16.7348) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY050G | float | 0.0 | >=50 | 0..42000 (media 155.511) | Ayuda por familia/hijos en el año anterior al de encuesta |
| HY050G_F | int | 0.0 | 3 | 15..55 (media 15.1505) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY060G | float | 0.0 | >=50 | 0..50227.3 (media 233.277) | Ingresos por asistencia social en el año anterior al de encuesta |
| HY060G_F | int | 0.0 | 3 | 15..55 (media 15.4992) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY070G | float | 0.0 | >=50 | 0..13200 (media 38.729) | Ayuda para vivienda en el año anterior al de encuesta |
| HY070G_F | int | 0.0 | 2 | 15..55 (media 15.1253) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY080G | float | 0.0 | >=50 | 0..51012 (media 173.86) | Transferencias periódicas monetarias percibidas de otros hogares en el año anterior al de encuesta |
| HY080G_F | int | 0.0 | 2 | 16..56 (media 16.094) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY081G | float | 0.0 | >=50 | 0..51012 (media 114.495) | Transferencias periódicas monetarias percibidas de otros hogares en el año anterior al de encuesta (pensiones alimenticias a hijos o compensatorias a cónyuges) |
| HY081G_F | int | 0.0 | 2 | 16..56 (media 16.0518) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY090G | float | 0.0 | >=50 | 0..87510.5 (media 983.875) | Intereses, dividendos y ganancias brutos de inversiones de capital en empresas no constituidas en sociedad en el año anterior al de encuesta |
| HY090G_F | int | 0.0 | 3 | 15..55 (media 24.8137) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY100G | float | 0.0 | >=50 | 0..18197.5 (media 606.861) | Intereses pagados del préstamo para la compra de la vivienda principal, en el año anterior al de encuesta |
| HY100G_F | int | 0.0 | 2 | 11..51 (media 12.155) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY110G | float | 0.0 | >=50 | 0..19800 (media 23.6695) | Renta bruta percibida por los menores de 16 años en el año anterior al de encuesta |
| HY110G_F | int | 0.0 | 2 | 15..55 (media 15.0259) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY120G | float | 0.0 | >=50 | 0..17944 (media 356.585) | Impuesto sobre el patrimonio en el año anterior al de encuesta. A partir de ECV2021 se incluye en esta variable el Impuesto sobre Bienes Inmuebles de la vivienda principal, cuando el régimen de tenencia sea en propiedad. |
| HY120G_F | int | 0.0 | 2 | 11..51 (media 11.0191) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY130G | float | 0.0 | >=50 | 0..25400 (media 285.547) | Transferencias periódicas monetarias abonadas a otros hogares en el año anterior al de encuesta |
| HY130G_F | int | 0.0 | 2 | 16..56 (media 16.1961) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY131G | float | 0.0 | >=50 | 0..24000 (media 164.656) | Transferencias periódicas monetarias abonadas a otros hogares en el año anterior al de encuesta (pensiones alimenticias a hijos o compensatorias a cónyuges) |
| HY131G_F | int | 0.0 | 2 | 16..56 (media 16.0913) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HY140G | float | 0.0 | >=50 | -10147.5..343507 (media 9403.92) | Impuesto sobre la renta y cotizaciones sociales |
| HY140G_F | int | 0.0 | 4 | 15..55 (media 25.221) | Variable que indica información complementaria (fuente y tipo de información recogida) |
| HS011 | mixto | 0.0 | 4 | top:   (58%), 3 (38%), 2 (3%) | ¿Se han producido retrasos en el pago de la hipoteca o del alquiler del hogar en los últimos 12 meses? (EXCLUSIÓN SOCIAL) |
| HS011_F | int | 0.0 | 3 | -2..1 (media -0.731452) | Variable que indica si HS011 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS021 | mixto | 0.0 | 4 | top: 3 (92%), 2 (5%), 1 (2%) | ¿Se han producido retrasos en el pago de las facturas |
| HS021_F | int | 0.0 | 3 | -2..1 (media 0.978106) | Variable que indica si HS021 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS022 | int | 0.0 | 2 | 1..2 (media 1.89697) | ¿Se benefició el hogar de algún bono social para hacer frente a gastos de electricidad, calefacción, gas, etc.? |
| HS022_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HS022 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS031 | mixto | 0.0 | 4 | top:   (73%), 3 (23%), 2 (3%) | ¿Se han producido retrasos en el pago de compras aplazadas o de otros préstamos (deudas no relacionadas con la vivienda principal) en los últimos 12 meses? |
| HS031_F | int | 0.0 | 3 | -2..1 (media -1.19684) | Variable que indica si HS031 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS040 | mixto | 0.0 | 3 | top: 1 (70%), 2 (30%),   (0%) | ¿Puede el hogar permitirse ir de vacaciones fuera de casa, al menos una semana al año? |
| HS040_F | int | 0.0 | 2 | -1..1 (media 0.997004) | Variable que indica si HS040 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS050 | mixto | 0.0 | 3 | top: 1 (95%), 2 (5%),   (0%) | ¿Puede el hogar permitirse una comida de carne, pollo o pescado (o equivalentes para los vegetarianos) al menos cada dos días? |
| HS050_F | int | 0.0 | 2 | -1..1 (media 0.999591) | Variable que indica si HS050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS060 | mixto | 0.0 | 3 | top: 1 (67%), 2 (33%),   (0%) | ¿Tiene el hogar capacidad para afrontar gastos imprevistos? |
| HS060_F | int | 0.0 | 2 | -1..1 (media 0.998298) | Variable que indica si HS060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS090 | mixto | 0.0 | 4 | top: 1 (72%), 3 (22%), 2 (5%) | ¿Tiene el hogar ordenador? |
| HS090_F | int | 0.0 | 2 | -1..1 (media 0.999047) | Variable que indica si HS090 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS110 | mixto | 0.0 | 4 | top: 1 (80%), 3 (15%), 2 (5%) | ¿Tiene el hogar coche? |
| HS110_F | int | 0.0 | 2 | -1..1 (media 0.999115) | Variable que indica si HS110 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS120 | mixto | 0.0 | 7 | top: 4 (31%), 3 (23%), 5 (23%) | Capacidad del hogar para llegar a fin de mes |
| HS120_F | int | 0.0 | 2 | -1..1 (media 0.996595) | Variable que indica si HS120 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS150 | mixto | 0.0 | 4 | top:   (76%), 2 (13%), 1 (10%) | Los desembolsos por compras a plazos o por devolución de préstamos no relacionados con la vivienda principal suponen para el hogar: |
| HS150_F | int | 0.0 | 3 | -2..1 (media -1.26977) | Variable que indica si HS150 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HD080 | mixto | 0.0 | 4 | top: 1 (67%), 2 (25%), 3 (9%) | ¿El hogar podría sustituir los muebles estropeados o viejos? (EL HOGAR PUEDE O NO:
REEMPLAZAR MUEBLES) |
| HD080_F | int | 0.0 | 2 | -1..1 (media 0.99891) | Variable que indica si HD080 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH010 | mixto | 0.0 | 5 | top: 4 (47%), 3 (19%), 1 (18%) | Tipo de vivienda (VIVIENDA) |
| HH010_F | int | 0.0 | 2 | -1..1 (media 0.995642) | Variable que indica si HH010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH021 | int | 0.0 | 5 | 1..5 (media 1.85641) | Régimen de tenencia: 1 propiedad sin hipoteca, 2 propiedad con hipoteca, 3 alquiler o realquiler a precio de mercado, 4 a precio inferior al de mercado, 5 cesión gratuita |
| HH021_F | int | 0.0 | 1 | 1..1 (media 1) | Variable que indica si HH021 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH030 | mixto | 0.0 | 11 | top: 5 (34%), 4 (22%), 6 (17%) | Número de habitaciones de la vivienda |
| HH030_F | int | 0.0 | 2 | -1..1 (media 0.993531) | Variable que indica si HH030 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH050 | mixto | 0.0 | 3 | top: 1 (85%), 2 (15%),   (0%) | ¿Puede el hogar permitirse mantener la vivienda con una temperatura adecuada durante los meses de invierno? |
| HH050_F | int | 0.0 | 2 | -1..1 (media 0.997957) | Variable que indica si HH050 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH060 | mixto | 0.0 | >=50 | alta cardinalidad | Alquiler actual por la vivienda ocupada |
| HH060_F | int | 0.0 | 3 | -2..1 (media -1.53253) | Variable que indica si HH060 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HH070 | mixto | 0.0 | >=50 | alta cardinalidad | Gastos de la vivienda: Alquiler (si la vivienda se encuentra en régimen de alquiler), intereses de la hipoteca (para viviendas en propiedad con pagos pendientes) y otros gastos asociados (comunidad, agua, electricidad, gas, etc.) |
| HH070_F | int | 0.0 | 2 | -1..1 (media 0.992782) | Variable que indica si HH070 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HI010 | mixto | 0.0 | 4 | top: 2 (73%), 1 (16%), 3 (11%) | ¿Se ha producido un cambio en los ingresos del hogar en los últimos 12 meses? (ENDEUDAMIENTO EXCESIVO) |
| HI010_F | int | 0.0 | 2 | -1..1 (media 0.996527) | Variable que indica si HI010 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HI020 | mixto | 0.0 | 8 | top:   (85%), 1 (6%), 6 (3%) | ¿Cuál ha sido el motivo principal del aumento de los ingresos? |
| HI020_F | int | 0.0 | 3 | -2..1 (media -1.53778) | Variable que indica si HI020 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HI030 | mixto | 0.0 | 10 | top:   (89%), 4 (3%), 9 (3%) | ¿Cuál ha sido el motivo principal de la disminución de los ingresos? |
| HI030_F | int | 0.0 | 3 | -2..1 (media -1.6671) | Variable que indica si HI030 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HI040 | mixto | 0.0 | 4 | top: 2 (64%), 1 (13%),   (13%) | Pensando en los ingresos de su hogar, ¿qué espera que pase en los próximos 12 meses? |
| HI040_F | int | 0.0 | 2 | -1..1 (media 0.749191) | Variable que indica si HI040 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| cuotahip | mixto | 0.0 | >=50 | alta cardinalidad | Cuota hipotecaria mensual (importe del último recibo mensual del préstamo solicitado para la compra de la vivienda principal). Incluye amortización e intereses (VARIABLES COMPLEMENTARIAS) |
| cuotahip_F | int | 0.0 | 2 | -2..1 (media -1.27413) | Variable que indica si CUOTAHIP está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HX040 | int | 0.0 | 12 | 1..13 (media 2.43107) | Número de miembros del hogar |
| HX060 | mixto | 0.0 | 15 | top: 7 (17%), 8 (12%), 12 (11%) | Tipo de hogar (1) |
| HX240 | float | 0.0 | 37 | 1..5.8 (media 1.65499) | Unidades de consumo. Escala OCDE modificada. Número: 1-50 (2) |
| vhRentaa | float | 0.0 | >=50 | -28024.3..522875 (media 39896.3) | Renta disponible total del hogar en el año anterior al de la entrevista (nota: esta variable contiene las rentas percibidas de esquemas privados de pensiones). Variable utilizada en los indicadores armonizados de pobreza |
| vhRentaAIa | float | 0.0 | >=50 | -23333.8..528587 (media 45891.4) | Renta disponible total del hogar en el año anterior al de la entrevista, incluyendo el alquiler imputado (nota: esta variable contiene las rentas percibidas de esquemas privados de pensiones). Asimismo se deducen de los ingresos totales del hogar los intereses de los préstamos solicitados para la compra de la vivienda principal. |
| vhPobreza | int | 0.0 | 2 | 0..1 (media 0.170282) | Hogar en riesgo de pobreza. Umbral de pobreza: es el 60% de la mediana de los ingresos anuales -vhRentaa- por unidad de consumo (escala OCDE modificada), tomando la distribución de personas. Los ingresos por unidad de consumo se obtienen dividiendo los ingresos totales del hogar entre el número de unidades de consumo |
| vhMATDEP | int | 0.0 | 2 | 0..1 (media 0.0662263) | Hogar en carencia material severa. Son los hogares con carencia en al menos cuatro conceptos de una lista de nueve. Los conceptos considerados son: No puede permitirse ir de vacaciones al menos una semana al año No puede permitirse una comida de carne, pollo o pescado al menos cada dos días No puede permitirse mantener la vivienda con una temperatura adecuada No tiene capacidad para afrontar gastos imprevistos Ha tenido retrasos en el pago de gastos relacionados con la vivienda principal (hipoteca o alquiler, recibos de gas, comunidad...) o en compras a plazos en los últimos 12 meses No puede permitirse disponer de un automóvil No puede permitirse disponer de teléfono No puede permitirse disponer de un televisor en color No puede permitirse disponer de una lavadora A partir de ECV2021 se dejan de recoger los conceptos 'No puede permitirse disponer de un teléfono', ' No puede permitirse disponer de un televisor en color', y ' No puede permitirse disponer de una lavadora', asumiéndose que el hogar no tiene carencia en esos conceptos. |
| HS200 | mixto | 0.0 | 4 | top: 3 (58%), 2 (31%), 1 (8%) | Carga financiera de la asistencia médica (MÓDULO: SALUD) |
| HS200_F | int | 0.0 | 3 | -2..1 (media 0.912459) | Variable que indica si HS200 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS210 | mixto | 0.0 | 4 | top: 2 (38%),   (23%), 3 (20%) | Carga financiera de la asistencia dental |
| HS210_F | int | 0.0 | 3 | -2..1 (media 0.305867) | Variable que indica si HS210 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HS220 | mixto | 0.0 | 4 | top: 2 (49%), 3 (39%), 1 (7%) | Carga financiera de los medicamentos |
| HS220_F | int | 0.0 | 3 | -2..1 (media 0.853247) | Variable que indica si HS220 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HC006 | mixto | 0.0 | 9 | top: 4 (29%), 3 (27%), 5 (19%) | Año de construcción de la vivienda (MÓDULO: ENERGÍA Y MEDIOAMBIENTE
Vivienda) |
| HC006_F | int | 0.0 | 2 | -1..1 (media 0.889884) | Variable que indica si HC006 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HC003A | mixto | 0.0 | 7 | top: 5 (45%), 4 (33%), 1 (13%) | Mejoras en el aislamiento térmico o en el sistema de calefacción de la vivienda o del edificio |
| HC003A_F | int | 0.0 | 3 | -2..1 (media 0.941912) | Variable que indica si HC003A está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE07 | mixto | 0.0 | 6 | top:   (78%), 2 (17%), 5 (3%) | Razón principal por la que no se ha mejorado la eficiencia energética |
| HEE07_F | int | 0.0 | 3 | -2..1 (media -1.32041) | Variable que indica si HEE07 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE01 | mixto | 0.0 | 5 | top: 1 (66%), 2 (24%), 3 (6%) | Distancia a pie desde su casa hasta el espacio verde público más cercano (MÓDULO: ENERGÍA Y MEDIOAMBIENTE
Entorno) |
| HEE01_F | int | 0.0 | 2 | -1..1 (media 0.99285) | Variable que indica si HEE01 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE09 | mixto | 0.0 | 4 | top: 1 (81%), 2 (11%), 3 (8%) | ¿Se reciclan las botellas de plástico? |
| HEE09_F | int | 0.0 | 2 | -1..1 (media 0.996118) | Variable que indica si HEE09 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE11 | mixto | 0.0 | 11 | top: 1 (45%), 2 (27%), 0 (20%) | Número de vehículos de los que dispone el hogar de uso regular como medio de transporte personal (MÓDULO: ENERGÍA Y MEDIOAMBIENTE
Transporte) |
| HEE11_F | int | 0.0 | 2 | -1..1 (media 0.975689) | Variable que indica si HEE11 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE13 | mixto | 0.0 | >=50 | alta cardinalidad | Antigüedad del vehículo más nuevo (o del único) |
| HEE13_F | int | 0.0 | 3 | -2..1 (media 0.370425) | Variable que indica si HEE13 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE14 | mixto | 0.0 | >=50 | alta cardinalidad | Antigüedad del vehículo más viejo |
| HEE14_F | int | 0.0 | 3 | -2..1 (media -0.975689) | Variable que indica si HEE14 está completa, falta o simplemente no es aplicable en el registro en cuestión |
| HEE12 | mixto | 0.0 | 7 | top: 1 (40%), 2 (32%),   (21%) | Tipo de combustible que utiliza el vehículo más nuevo (o el único) |
| HEE12_F | int | 0.0 | 3 | -2..1 (media 0.383704) | Variable que indica si HEE12 está completa, falta o simplemente no es aplicable en el registro en cuestión |

## Primeras filas (primeras 15 de 156 columnas)
| HB010 | HB020 | HB030 | HB050 | HB050_F | HB060 | HB060_F | HB070 | HB070_F | HB080 | HB080_F | HB100 | HB100_F | HB120 | HB120_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 1 | 4 | 1 | 2025 | 1 | 101 | 1 | 101 | 1 | 22 | 1 | 1 | 1 |
| 2025 | ES | 2 | 3 | 1 | 2025 | 1 | 201 | 1 | 201 | 1 | 37 | 1 | 2 | 1 |
| 2025 | ES | 3 | 6 | 1 | 2025 | 1 | 301 | 1 | 302 | 1 | 8 | 1 | 2 | 1 |
| 2025 | ES | 4 | 4 | 1 | 2025 | 1 | 401 | 1 | 401 | 1 | 15 | 1 | 2 | 1 |
| 2025 | ES | 5 | 5 | 1 | 2025 | 1 | 501 | 1 | 501 | 1 | 10 | 1 | 5 | 1 |

## Muestra aleatoria (primeras 15 de 156 columnas)
| HB010 | HB020 | HB030 | HB050 | HB050_F | HB060 | HB060_F | HB070 | HB070_F | HB080 | HB080_F | HB100 | HB100_F | HB120 | HB120_F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | ES | 20835 | 5 | 1 | 2025 | 1 | 2083501 | 1 | 2083501 | 1 | 12 | 1 | 1 | 1 |
| 2025 | ES | 28018 | 5 | 1 | 2025 | 1 | 2801801 | 1 | 2801801 | 1 | 15 | 1 | 5 | 1 |
| 2025 | ES | 6168 | 4 | 1 | 2025 | 1 | 616801 | 1 | 616802 | 1 | 13 | 1 | 4 | 1 |
| 2025 | ES | 23161 | 3 | 1 | 2025 | 1 | 2316101 | 1 | 2316101 | 1 | 16 | 1 | 1 | 1 |
| 2025 | ES | 17317 | 4 | 1 | 2025 | 1 | 1731701 | 1 | 1731701 | 1 | 14 | 1 | 2 | 1 |

## Avisos
- 36 columnas con tipos mezclados: `HB070`, `HB100`, `HS011`, `HS021`, `HS031`, `HS040`, `HS050`, `HS060` y 28 mas.
- 10 columnas constantes: `HB010`, `HB020`, `HB050_F`, `HB060`, `HB060_F`, `HB080_F`, `HB120_F`, `HY030N_F` y 2 mas.

## Notas
- Cada columna con sufijo `_F` es la bandera de calidad de la variable sin sufijo.
- Region de residencia (`DB040`, p. ej. ES30 = Madrid) esta en el fichero D (`ECV_Td_2025/CSV/esudb25d.csv`, 1 MB); se une con `HB030` (hogar) de H.
