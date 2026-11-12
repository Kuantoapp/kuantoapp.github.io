# Indicadores y umbrales: SMI, IPREM, IMV, RMI, pobreza, sobrecarga, alquiler y salarios

Investigado el 12/11/2026 en BOE, INE (API Tempus), Eurostat y seg-social.es. **Antes de usar un valor, comprueba que la norma o la publicación citada sigue siendo la vigente o la última**; si cambia el año, este fichero se rehace.

**Contenido:** 1. Salario mínimo interprofesional (SMI) · 2. IPREM 2026 · 3. Ingreso Mínimo Vital (IMV) 2026 · 4. Renta Mínima de Inserción (RMI) de la Comunidad de Madrid 2026 · 5. Umbral de riesgo de pobreza, escala de equivalencia y AROPE (INE, ECV) · 6. Sobrecarga del coste de la vivienda · 7. Alquiler: IRAV, SERPAVI y zonas tensionadas · 8. Salarios del INE · Resumen de cambios importantes de 2026

Fecha de consulta: 12-11-2026. Ámbito: España y Comunidad de Madrid.

Estados usados:
- **VERIFICADO**: leído en la fuente primaria (BOE, INE o su API, Eurostat o su API, seg-social.es).
- **VERIFICADO (indirecto)**: comprobado por cálculo o por coherencia con otra cifra oficial, sin leer el texto literal.
- **NO VERIFICADO**: solo aparece en prensa o en webs secundarias, o no se encontró la fuente primaria. Se indica qué se encontró.

APIs usadas, reutilizables al implementar:
- INE Tempus: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{id}?nult=N` (JSON).
- Eurostat: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?geo=ES&...` (JSON-stat 2.0).

---

## 1. Salario mínimo interprofesional (SMI)

| Concepto | 2026 | 2025 | Unidad | Fuente | Estado |
|---|---|---|---|---|---|
| SMI diario | 40,70 | 39,47 | €/día | RD 126/2026 art. 1 / RD 87/2025 art. 1 | VERIFICADO |
| SMI mensual | 1.221 | 1.184 | €/mes, 14 pagas | RD 126/2026 art. 1 / RD 87/2025 art. 1 | VERIFICADO |
| SMI anual (mínimo de comparación) | 17.094 | 16.576 | €/año | RD 126/2026 art. 3.1 / RD 87/2025 art. 3.1 | VERIFICADO |
| Eventuales y temporeros (≤120 días) | 57,82 | 56,08 | € por jornada legal | art. 4.1 | VERIFICADO |
| Empleo de hogar por horas | 9,55 | 9,26 | €/hora | art. 4.2 | VERIFICADO |
| Subida | +3,1 % | — | % | preámbulo RD 126/2026 | VERIFICADO |

- **2026:** Real Decreto 126/2026, de 18 de febrero. BOE núm. 44, de 19-02-2026, **BOE-A-2026-3815**. Entró en vigor el 20-02-2026, con efectos económicos desde el **1-01-2026** (disposición final tercera). https://www.boe.es/eli/es/rd/2026/02/18/126/con
- **2025:** Real Decreto 87/2025, de 11 de febrero. BOE núm. 37, de 12-02-2025, **BOE-A-2025-2576**. Efectos desde el 1-01-2025; hoy con vigencia agotada. https://www.boe.es/eli/es/rd/2025/02/11/87/con
- Al implementar: anual = mensual × 14 (1.221 × 14 = 17.094). El mensual prorrateado en 12 pagas sería 1.424,50 €; es un cálculo propio, no una cifra de la norma.
- Contexto (NO VERIFICADO en el BOE, solo en prensa): un real decreto-ley anterior que prorrogaba el SMI de 2025 no fue convalidado el 27-01-2026. Ese mismo día se publicó el RDL 5/2026 sobre la tributación del SMI.

## 2. IPREM 2026

| Concepto | Valor | Unidad | Cuándo se usa | Estado |
|---|---|---|---|---|
| IPREM diario | 20,00 | €/día | — | VERIFICADO (texto 2023 + prórroga) |
| IPREM mensual | 600,00 | €/mes | — | ídem |
| IPREM anual, 12 pagas | 7.200,00 | €/año | Por defecto, y cuando la norma que sustituyó el SMI por el IPREM excluye expresamente las pagas extra | ídem |
| IPREM anual, 14 pagas | 8.400,00 | €/año | Cuando la norma se refería al "SMI en cómputo anual" y no excluye las pagas extra (sustitución del RDL 3/2004) | ídem |

- **Norma que lo fija:** Ley 31/2022, de 23 de diciembre, de PGE para 2023, **disposición adicional nonagésima**, letras a) a d). **BOE-A-2022-22128**. https://www.boe.es/buscar/act.php?id=BOE-A-2022-22128
- **Prórroga presupuestaria:** no hay PGE para 2026. El preámbulo del Real Decreto-ley 3/2026, de 3 de febrero (**BOE-A-2026-2548**, BOE de 04-02-2026), dice que "la falta de aprobación de la Ley de Presupuestos Generales del Estado para el año 2026 determina la prórroga automática" de la Ley 31/2022 (art. 134.4 de la Constitución). https://www.boe.es/eli/es/rdl/2026/02/03/3/con
- **Estado:** las cuantías están VERIFICADAS en la DA 90ª. Que sigan vigentes en 2026 por la prórroga es una interpretación jurídica estándar que confirman las webs secundarias. **NO** encontré ninguna norma de 2026 que fije el IPREM de forma expresa. Tampoco encontré PGE 2026 aprobados a noviembre de 2026 (búsqueda en prensa, sin rastro en el BOE).

## 3. Ingreso Mínimo Vital (IMV) 2026

Base legal: Ley 19/2021, de 20 de diciembre, art. 13. La renta garantizada individual es el 100 % del importe anual de la pensión no contributiva (PNC). La PNC de 2026 es de **8.803,20 €/año** (RDL 3/2026, **art. 2.5**, BOE-A-2026-2548, VERIFICADO). La revalorización general de pensiones de 2026 es del **2,7 %** (art. 2.1).

Cuantías publicadas por la Seguridad Social, en euros, para "2026": https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/65850d68-8d06-4645-bde7-05374ee42ac7 (VERIFICADO)

| Unidad de convivencia | Anual | Mensual (÷12) | Coeficiente sobre la base |
|---|---|---|---|
| 1 adulto | 8.803,20 | 733,60 | 1,0 |
| 1A+1M o 2A | 11.444,16 | 953,68 | 1,3 |
| 1A+2M, 2A+1M o 3A | 14.085,12 | 1.173,76 | 1,6 |
| 1A+3M, 2A+2M, 3A+1M o 4A | 16.726,08 | 1.393,84 | 1,9 |
| Otros (máximo) | 19.367,04 | 1.613,92 | 2,2 |

- **Escala (VERIFICADO indirecto):** +0,3 de la base por cada miembro adicional, con tope de 2,2. Todas las cifras de la tabla cuadran con 8.803,20 × coeficiente.
- **Complemento monoparental:** +22 % de la base (1.936,70 €/año). Ejemplos: 1A+1M = 13.380,84; 1A+2M = 16.021,80; 1A+3M = 18.662,76; 1A+4 o más M = 21.303,72 €/año. VERIFICADO (seg-social). El redondeo de la Seguridad Social difiere en 0,02 € del cálculo exacto.
- **Complemento por discapacidad:** +22 % de la base si algún miembro tiene un grado de discapacidad ≥ 65 %. VERIFICADO (seg-social).
- **Complemento de ayuda para la infancia (CAPI)**, por menor, según la edad cumplida el 1 de enero: <3 años, **115 €/mes**; 3–6 años, **80,50 €/mes**; 6–18 años, **57,50 €/mes**. VERIFICADO (seg-social). No localicé el precepto de 2026 que lo fija: la página cita la Ley 19/2021 sin artículo concreto.
- Fórmula: **prestación = renta garantizada − rentas computables del hogar** (art. 10 Ley 19/2021, según fuentes secundarias). No contrasté el artículo literal.
- NO VERIFICADO: la "subida del 11,4 %" del IMV en 2026 que cita la prensa. No leí la cifra oficial de 2025 para comprobarla.

## 4. Renta Mínima de Inserción (RMI) de la Comunidad de Madrid 2026

| Concepto | 2026 | Unidad | Fuente | Estado |
|---|---|---|---|---|
| Prestación mensual básica | **469,93** | €/mes (12 pagas, sin pagas extra) | Ley 6/2025 CM, **art. 58.a** | VERIFICADO |
| Complemento por el primer miembro adicional | **117,48** | €/mes | art. 58.b | VERIFICADO |
| Complemento por cada miembro siguiente | **75,11** | €/mes | art. 58.c | VERIFICADO |
| Tope máximo | SMI | €/mes | art. 58 → art. 10.4 Ley 15/2001 | VERIFICADO |

- **Norma:** Ley 6/2025, de 23 de diciembre, de Presupuestos Generales de la Comunidad de Madrid para el año 2026. Se publicó en el BOCM el 29-12-2025 y en el BOE núm. 38 de 12-02-2026, **BOE-A-2026-3218**. Efectos desde el 1-01-2026. https://www.boe.es/boe/dias/2026/02/12/pdfs/BOE-A-2026-3218.pdf
- **Marco:** Ley 15/2001, de 27 de diciembre, de RMI (BOE-A-2002-4378), art. 10. La cuantía es la básica más un complemento variable según el número de miembros, se fija cada año en la ley de presupuestos y se le restan los ingresos mensuales de la unidad de convivencia. El reglamento es el Decreto 126/2014. https://www.boe.es/buscar/act.php?id=BOE-A-2002-4378
- **Relación con el IMV:** la RMI es **subsidiaria y complementaria** (art. 4 Ley 15/2001) de las pensiones y prestaciones públicas. El IMV cuenta como ingreso y se descuenta del importe de la RMI (art. 10.3). El texto consolidado de la Ley 15/2001 no menciona el IMV de forma expresa. Que en la práctica se exija pedir antes el IMV es NO VERIFICADO.
- Comparación (cálculo propio): para un adulto solo, la RMI (469,93 €/mes) es el 64 % del IMV (733,60 €/mes). Como el IMV se descuenta, quien cobra el IMV completo no recibe RMI.
- Sede de la Comunidad de Madrid (plazo permanente): https://sede.comunidad.madrid/prestacion-social/renta-minima-insercion/tramitar. Su documento de cuantías es de 2022 y está desactualizado; no usarlo.

## 5. Umbral de riesgo de pobreza, escala de equivalencia y AROPE (INE, ECV)

**Última ECV publicada:** ECV **2025**, resultados definitivos, publicada el **5-02-2026**. Los ingresos se refieren a **2024**. La ECV 2026 (ingresos de 2025) **no está publicada** a 12-11-2026: las tablas del INE se actualizaron por última vez el 5-02-2026. Nota de prensa: https://www.ine.es/dyngs/Prensa/es/ECV2025.htm

### Umbral (60 % de la mediana de la renta por unidad de consumo). Tabla INE 9964 (VERIFICADO vía API)

| Hogar | ECV 2025 (ingresos 2024) | ECV 2024 (ingresos 2023) | Con alquiler imputado 2025 |
|---|---|---|---|
| 1 persona | **12.220,4 €/año** | 11.584,4 | 14.093,3 |
| 2 adultos + 2 menores de 14 | **25.662,8 €/año** | 24.327,2 | 29.595,9 |

- Fuente: INE, tabla 9964 "Umbral de riesgo de pobreza (valores ilustrativos)". https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/9964
- El Instituto de Estadística de Extremadura da 12.220,35 € a partir de los microdatos del INE.
- **Comunidad de Madrid:** el INE **no publica umbral autonómico**; solo el nacional. Un umbral propio de Madrid habría que calcularlo con los microdatos (60 % de la mediana regional). NO PUBLICADO.

### Escala OCDE modificada
- 1 para el primer adulto, 0,5 para cada persona de 14 o más años y 0,3 para cada menor de 14.
- **VERIFICADO (indirecto):** 12.220,4 × (1 + 0,5 + 0,3 + 0,3) = 12.220,4 × 2,1 = 25.662,84, que coincide con la tabla 9964.
- El texto metodológico literal del INE no se leyó en la consulta del 12/11/2026.

### Indicadores 2025 (ingresos 2024)

| Indicador | España | C. de Madrid | Tabla INE |
|---|---|---|---|
| Tasa de riesgo de pobreza | 19,5 % | 12,7 % | 9963 |
| Tasa de riesgo de pobreza con alquiler imputado | 17,5 % | 12,4 % | 9963 |
| AROPE | 25,7 % | 19,4 % | nota de prensa, tabla por CCAA |
| Carencia material y social severa | 8,1 % | 3,5 %* | ídem |
| Baja intensidad en el empleo | 8,0 % | 8,4 %* | ídem |
| Renta neta media por persona | 15.620 € | 18.169 € | 9947 |
| Renta media por unidad de consumo | 22.943 € | 27.136 € | 9947 |
| Renta neta media por hogar | 38.994 € | 47.375 € | 9949 |

\*Las cifras de Madrid para los componentes salen del texto del PDF de la nota de prensa (fila "Madrid, Comunidad de 19,4 12,7 8,4 3,5"). El orden de esas dos columnas lo deduje de la cabecera; conviene confirmarlo en la tabla 76847/67989.

- **AROPE (Europa 2030):** población que cumple al menos uno de tres criterios: riesgo de pobreza, carencia material y social severa, o baja intensidad en el empleo. Así lo define la nota del INE (VERIFICADO). El detalle operativo de los componentes (7 de 13 conceptos de carencia; intensidad laboral < 20 % en la población de 0 a 64 años) es la definición de Eurostat, que **no leí en la consulta del 12/11/2026: NO VERIFICADO**.
- Otro indicador del INE: tasa de pobreza con umbral fijo en 2008 (tablas 59962 y 59972, actualizadas el 1-10-2026).

## 6. Sobrecarga del coste de la vivienda

### Definición de Eurostat (housing cost overburden rate)
- Porcentaje de población que vive en hogares cuyos **costes totales de vivienda, netos de ayudas a la vivienda, superan el 40 % de la renta disponible**, también neta de ayudas a la vivienda. Glosario: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Housing_cost_overburden_rate (VERIFICADO)
- **Costes incluidos:** alquiler, o intereses de la hipoteca netos de deducciones fiscales en el caso de propietarios; agua, electricidad, gas y calefacción; seguro estructural; servicios obligatorios (alcantarillado, basuras); mantenimiento y reparaciones ordinarias. VERIFICADO (glosario).
- **Ayudas a la vivienda:** el glosario dice "net of housing allowances" en el numerador y en el denominador. Su texto detallado añade que la variable de coste se recoge bruta de ayudas. Fórmula operativa en EU-SILC, deducida y NO VERIFICADA literalmente en la guía metodológica: `(HH070 − HY070G) / (HY020 − HY070G) > 0,40`. Es decir, la ayuda se resta del coste y de la renta.

### Últimos valores (Eurostat, EU-SILC 2025, ingresos de 2024; datasets actualizados en octubre de 2026). VERIFICADO vía API

| Ámbito | 2023 | 2024 | 2025 | Dataset |
|---|---|---|---|---|
| España, total | 8,2 % | 7,8 % | **7,2 %** | ilc_lvho07a |
| UE-27 | 8,8 % | 8,2 % | 7,6 % | ilc_lvho07a |
| Comunidad de Madrid (NUTS2 ES30) | 9,1 % | 11,2 % | **9,9 %** | ilc_lvho07_r |
| España, inquilinos a precio de mercado | — | — | **26,8 %** | ilc_lvho07c |
| España, población en riesgo de pobreza | — | — | 28,3 % | ilc_lvho07a |

- Madrid 2022: 12,2 %.
- **Equivalente en el INE:** el INE es el productor nacional de la ECV/EU-SILC, pero en su catálogo de tablas de la ECV **no encontré** ninguna tabla de "carga de los gastos de la vivienda" con el umbral del 40 % (solo "carga de los gastos sanitarios"). La cifra oficial accesible es la de Eurostat con datos de la ECV.

### Regla del 30 %
- **Única referencia normativa española encontrada (VERIFICADO):** Ley 12/2023, por el derecho a la vivienda, **art. 18.3.a**. Es uno de los criterios para declarar una zona tensionada: que "la carga media del coste de la hipoteca o del alquiler... más los gastos y suministros básicos, supere el treinta por ciento de los ingresos medios o de la renta media de los hogares". https://www.boe.es/buscar/act.php?id=BOE-A-2023-12203
- **NO VERIFICADO** (no buscado o no encontrado en fuente primaria): el uso del 30 % en el Plan Estatal de Vivienda 2026-2030, en ONU-Hábitat o en el Banco de España. El origen histórico habitual de la regla está en la normativa de vivienda pública de EE. UU. y queda fuera del alcance de esta búsqueda. **No hay ningún indicador oficial de España con umbral del 30 %**: el indicador europeo y estadístico usa el 40 %.

## 7. Alquiler: IRAV, SERPAVI y zonas tensionadas

### IRAV (Índice de Referencia de Arrendamientos de Vivienda, INE)
- **Base legal (corrección):** el IRAV procede de la **disposición adicional undécima de la LAU** (Ley 29/1994), que introdujo la **disposición final primera** de la Ley 12/2023. **No viene de la disposición final sexta.** La DF 6ª de la Ley 12/2023 modificó el art. 46 del RDL 6/2022 (tope temporal del 3 % en 2023). VERIFICADO en el texto consolidado del BOE.
- **Qué es:** el límite de referencia para la actualización anual de la renta de los contratos de vivienda (art. 18 LAU). El INE lo calcula como el mínimo entre la variación anual del IPC, la del IPC subyacente y una media ajustada de ambas. Esa definición metodológica la dan fuentes secundarias: NO VERIFICADA en la metodología del INE. Se publica cada mes desde enero de 2025 (dato de diciembre de 2024).
- **Serie INE, tabla 72975, variación anual (VERIFICADO vía API):** ene-26 2,14; feb-26 2,16; mar-26 2,47; abr-26 2,40; may-26 2,48; jun-26 2,44; jul-26 2,49; ago-26 2,47; **sep-26 2,54 % (último publicado, el 14-10-2026)**. El dato de octubre aún no está publicado a 12-11-2026. https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/72975
- **Cambio de 2026 (VERIFICADO en el BOE):** Real Decreto-ley 29/2026, de 6 de octubre, **BOE-A-2026-20823** (BOE de 7-10-2026, en vigor el 8-10-2026). Su **DF 6ª** limita las actualizaciones anuales hasta el **31-12-2027**:
  - Si la renta supera el límite del sistema de índices de referencia, no cabe ninguna subida.
  - En el resto de casos, se aplica lo pactado y, sin pacto, **como máximo el 2 %**.

  Antes, el Congreso derogó el RDL 8/2026 (tope del 2 %) y los RDL 26/2026 y 27/2026, de 29 de septiembre (BOE-A-2026-20526, acuerdo de 2-10-2026). **NO VERIFICADO:** si el RDL 29/2026 se convalidó (el plazo de 30 días vencía hacia el 6-11-2026). El texto consolidado de la Ley 12/2023 en el BOE seguía mostrando la redacción del RDL 29/2026.
- https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20823

### SERPAVI (sistema estatal de índices de referencia del precio del alquiler)
- Lo regula el art. 17.7 de la Ley 12/2023 y lo gestiona el Ministerio de Vivienda y Agenda Urbana (MIVAU). Última actualización: **Resolución de 16-04-2026, BOE-A-2026-8691** (BOE de 20-04-2026), con metodología de 18-03-2026, por secciones censales. La anterior es BOE-A-2025-7279. Estado: VERIFICADO por los títulos del BOE; no leí el contenido.
- Sus valores solo limitan la renta en zonas tensionadas declaradas, y desde el RDL 29/2026 también la actualización anual.

### Zonas de mercado residencial tensionado (Ley 12/2023, art. 18)
- **Criterios (art. 18.3, VERIFICADO), basta uno:**
  - a) La carga media de la hipoteca o el alquiler, más gastos y suministros básicos, **supera el 30 %** de los ingresos medios o de la renta media de los hogares.
  - b) El precio de compra o de alquiler ha crecido en los 5 años anteriores **al menos 3 puntos porcentuales más** que el IPC acumulado de la comunidad autónoma.
- La declara la comunidad autónoma. El MIVAU publica cada trimestre la relación en el BOE (art. 18.2.d).
- **Comunidad de Madrid:** **no hay ninguna zona declarada**. La resolución del 2.º trimestre de 2026 (Resolución de 24-07-2026, **BOE-A-2026-16532**) no incluye ningún ámbito de Madrid: recoge Asturias, País Vasco, Galicia y otras. Estado: VERIFICADO para esa resolución.
  - NO VERIFICADO: la lista acumulada completa (la web del MIVAU devolvió 403) y la resolución del 3.er trimestre, que la prensa sitúa en el BOE de 3-11-2026 (Sopela, Urduliz y Bergara, en el País Vasco).
  - La prensa recoge que el Gobierno regional ha dicho que no las declarará.

## 8. Salarios del INE

### Encuesta Anual de Estructura Salarial (EAES) 2024
Último año publicado: definitiva, 28-05-2026. https://www.ine.es/dyngs/Prensa/es/EAES2024.htm

| Ganancia bruta anual por trabajador 2024 | España | C. de Madrid |
|---|---|---|
| Media | 29.540,26 € | 34.410,01 € |
| Percentil 10 | 12.018,46 € | 13.728,43 € |
| Cuartil inferior | 17.457,47 € | 18.872,44 € |
| Mediana | 24.497,17 € | 28.037,75 € |
| Cuartil superior | 36.969,61 € | 43.598,00 € |
| Percentil 90 | 52.515,27 € | 63.685,49 € |
| Moda | 16.520,18 € | — |

- Fuente: tabla INE **28191** "Medias y percentiles por sexo y CCAA" (VERIFICADO vía API). La moda sale de la nota de prensa.
- **Por edad:** tabla INE **28189** "Sexo y edad". Media nacional por tramos de 5 años: <20 años, 10.693,93; 20–24, 15.636,05; 25–29, 22.723,25; 30–34, 26.944,39; 35–39, 28.704,89; 40–44, 30.215,05; 45–49, 32.051,12; 50–54, 32.357,60; 55–59, 32.247,58; 60–64, 31.814,39; 65 y más, 31.576,81 €. La tabla 28201 es la otra tabla de sexo y edad (por percentiles).
  - Acceso: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/28189` o INEbase → Mercado laboral → Salarios → EAES.
  - No hay cruce de edad por comunidad autónoma en estas tablas (no lo comprobé a fondo).

### Decil de salarios del empleo principal (EPA)
- Último publicado: **año 2024**, el 14-11-2025, definitivo. https://www.ine.es/dyngs/Prensa/es/dsEPA2024.htm
- Salario medio mensual bruto: 2.385,6 €. Esta cifra viene de prensa que cita al INE: NO VERIFICADA en la tabla.
- La edición de 2025 se espera hacia mediados de noviembre de 2026 y no estaba localizada a 12-11-2026.

---

## Resumen de cambios importantes de 2026
1. **SMI 2026:** 1.221 €/mes (+3,1 %), aprobado tarde por el RD 126/2026 (BOE de 19-02-2026), con efectos retroactivos al 1-01-2026.
2. **IPREM congelado** en 600 €/mes por cuarto año, por la prórroga de los PGE 2023 (sin PGE 2026).
3. **IMV 2026:** 8.803,20 €/año para un adulto, ligado a la PNC (RDL 3/2026, art. 2.5).
4. **RMI Madrid 2026:** básica de 469,93 €/mes (Ley 6/2025 CM, art. 58), muy por debajo del IMV y subsidiaria de él.
5. **ECV 2025 publicada** en febrero de 2026, antes de lo habitual. Umbral para una persona: 12.220,4 €. No hay todavía ECV 2026.
6. **Alquiler:** cadena de reales decretos-leyes (8/2026 derogado; 26 y 27/2026 derogados; 29/2026 en vigor desde 8-10-2026, convalidación sin verificar). Tope del 2 % sin pacto y congelación de las rentas por encima del índice de referencia hasta el 31-12-2027. IRAV de septiembre de 2026: 2,54 %.
7. **Zonas tensionadas:** ninguna en la Comunidad de Madrid.
