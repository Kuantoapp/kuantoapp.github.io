"""Simulación del criterio del Bono Alquiler Joven con transporte en casos tipo (#101, #301, ficha A §7.4).

Para cada perfil de `titulares.PERFILES` y cada municipio con alquiler, dice qué parte de sus ocupados sería
elegible con el criterio que aplica Madrid (`bono_vigente`) y con dos alternativas declaradas
(`alquiler_transporte` y `horas_viaje`), y si lo es el municipio (`elegible` = al menos el 50 % de sus ocupados).
Todo sale de `mesobra.calculo.calcular` (modo `tp`) hacia cada destino de zona de `tiempos.json`, con
`app/datos/tarifas.json` (congelada el 2026-11-23 en #437, escenario `vigente_2026`: descuento del RDL 17/2025, que solo
vale en 2026; 227 días de trabajo al año). Salida: tabla `simulacion` (`contratos.py`). Es una simulación: todas las
filas van `estimado` y ser elegible no es cobrar (decisión 26).

Método de #301 (registro previo en `docs/decisiones.md`, 2026-11-19, fijado antes de ejecutar con los pesos). Se
evalúa cada par (zona de residencia z, destino d) y no la media del municipio: z es elegible para d si cumple edad,
ingresos y (alquiler(z) + T(z, d) + VTT × H(z, d)) ÷ neto > `CORTE`; `alquiler_transporte` es igual con VTT = 0.
T es el transporte al mes del hogar y H las horas de viaje al mes de más frente a la zona ref(d) con menos minutos
hacia d: H = máx(0, horas(z, d) − horas(ref(d), d)), con las horas del propio `calcular`. pct(z) = Σ_d w(z, d) ·
1[elegible(z, d)] × 100 y el del municipio, la mediana de pct entre sus zonas. `bono_vigente` no depende del
destino: su pct es 100 o 0.

Decisiones y sentido de su sesgo:
1. Criterio vigente: RD 42/2022 en la ronda «2024» de Madrid (BOCM-20250110-20, FAQ 2024). Sigue en tramitación
   (BOCM-20260922-16); sin convocatoria del RD 326/2026 en Madrid. Texto completo del Acuerdo en BDNS 805618, doc. 1505247.
2. IPREM «referido a 14 pagas» (Acuerdo, art. 4.4): 8.400 € (DA 90.ª.d Ley 31/2022, BOE-A-2022-22128, fijado «durante
   2023»; sin cambios en el consolidado del 18-11-2026 y vigente por la prórroga automática de los Presupuestos (CE,
   art. 134.4, BOE-A-1978-31229): sin Ley de Presupuestos posterior ni norma consolidada que fije otro IPREM,
   consultado el 24-11-2026).
   El art. 4.4 pide el IPREM del ejercicio de los ingresos (2024 o 2025): el mismo valor. Umbral 3 × IPREM = 25.200 €,
   «iguales o inferiores».
3. Edad de 18 a 35 años incluidos (RD 42/2022, art. 6.1.a, BOE-A-2022-802). Los 5 perfiles (23 a 34) cumplen: sin efecto.
4. Topes (art. 8; Acuerdo CG 26-12-2024, art. 5 y Anexo II, leído en bruto): vivienda 600 € (900 € en 55 municipios) y
   habitación 300 € (450 €), «hasta». `TOPE_900_2024` = `bono.TOPE_900` (ronda 2022) + 26 municipios nuevos.
5. Cuantía: min(250 € × personas beneficiarias, renta) (RD art. 11; Acuerdo, arts. 4.1.d y 8.1): en la pareja de 29
   las dos pueden ser beneficiarias (mismo sueldo, cada una cumple sola); en los demás, una. Sin límites de duración.
6. Se supone que cada perfil cumple el resto de requisitos (fuente regular de ingresos, sin exclusiones del art. 6.2)
   y que garaje, trastero y gastos van en la renta del SERPAVI, sin la valoración del 80, 95 o 75 % de la FAQ p. 12:
   sobreestima los elegibles.
7. Cada parámetro va con su cita, arriba de este módulo (`parametros_2026.py` queda fuera de la issue).
8. «Ingresos» = base imponible general + del ahorro (arts. 48 y 49 LIRPF). Es un supuesto bien fundado, no lo fija el BAJ:
   el Acuerdo solo dice «rentas anuales» e «información del IRPF» (arts. 4.1.d y 4.4), y tampoco aparece en el RD
   42/2022, la Orden 3479/2022, las FAQ 2024 ni el Anexo I. El mismo órgano lo define así en la ayuda hermana del plan:
   «base imponible general y del ahorro» (Orden de 22-10-2025, art. 11, BDNS 864406, doc. 1342309). Lo hacen igual
   Extremadura (DOE 02-07-2026) y Andalucía (BOJA 194/2022). Sin consulta a la Comunidad (decisión de #302).
   Un asalariado sin ahorro tiene solo la base general: bruto − cotización − 2.000 € (art. 19.2.f) − reducción del
   art. 20, como `neto.cuota_irpf`. La medida decide a la pareja y al joven: con la base (24.215 y 21.571 €) entran;
   con el bruto (28.038 y 25.209,48 €; el joven, por 9,48 €), no. La madre (20.323 € de base, 23.875 € de bruto)
   entra con las dos. El bruto es la cota inferior de elegibles (`ingresos="bruto"`), y la pareja y el joven se
   presentan siempre como banda. Sin resolver: cómo se agregan las imputaciones de quien no declara (no afecta a
   ningún perfil).
9. Cuentan solo los ingresos de la persona solicitante, el primer sueldo: Acuerdo, art. 4.1.d, si conviven jóvenes sin
   parentesco de 1.er grado o todos de hasta 35 años y firma el contrato (la pareja de 29); la madre suma su hijo, sin
   ingresos; en habitación, solo la persona arrendataria. El RD suma los de los convivientes: con esa regla la pareja
   queda fuera (sensibilidad `hogar`).
10. Los ingresos son los del «periodo impositivo inmediatamente anterior con plazo de presentación vencido a la
    solicitud» (Acuerdo, art. 4.4, certificado del ACG, BDNS 805618, doc. 1560529; FAQ 2024, pregunta 2). Las fechas
    son inferencia nuestra, la FAQ no las da: 2023 hasta el fin de la campaña del IRPF 2024 (30-6-2025), 2024
    hasta el de 2025 y 2025 después. Cuadra con el motivo de incumplimiento 7.1 de la ronda 2024 («ingresos
    correspondientes al ejercicio 2023»; sede.comunidad.madrid/medias/motivosdeincumplimientocompletobaj2024pdf/
    download, leído por el verificador el 2026-11-23, sin copia en data/raw), porque el plazo abrió el 3-2-2025. Para quien pidió entonces, el ejercicio
    era 2023, con ingresos menores: entrarían al menos los mismos (sin cargar sueldos de 2023). Supuesto: solicitud
    tras la campaña de 2024 (ejercicio 2024; una de hoy, noviembre de 2026, usaría 2025, con el mismo resultado). Se usa 2024: el bruto de 2024 de la pareja, la madre y el joven
    (`sueldos_2024`), no el llevado a 2026 (con el de 2026 la pareja, de 24.215 a 25.769 € de base, pasaría de los
    25.200 € y quedaría fuera por un ajuste de precios, no de ingresos reales). Con 2025 (ETCL ×1,0333, estimado) la
    base de la pareja sería de unos 25.089 €: dentro por 111 €. El SMI usa su sueldo de 2026: está por debajo del
    umbral en los dos años. La enfermera usa la misma fila de la nómina oficial de 2024 (`ENFERMERA_2024`,
    29.098,22 €, BOCM-20240806-11, anexo V, tabla 2.1.a): base de 25.206,84 €, fuera por 6,84 € (con 2026, por
    1.244 €; con 2025, por unos 824 €, bruto de 29.971,80 € sin la subida del 1,5 %, estimado). El margen es
    mínimo, así que el veredicto se da con sus sensibilidades. Hacia fuera: con la cotización de 2024 (MEI del
    trabajador 0,12 % en vez de 0,15 %) la base es de 25.215,57 €; con trienios, noches o guardias, más. El 0,5 %
    adicional de 2024 (RDL 4/2024, art. 6.2; BOCM-20250721-1) no cuenta: se aprobó en julio de 2025 y se imputa a
    2025, cuando es exigible (LIRPF art. 14.1.a; criterio de la AEAT del 15-3-2024 para el 0,5 % de 2023); si
    contara, 25.340,20 € (0,5 % sobre lo vigente a 31-12-2023). Hacia dentro, sin modelar (igual que en los
    demás perfiles): cuotas sindicales o de un colegio de colegiación obligatoria (LIRPF art. 19.2.d; RIRPF
    art. 10: las sindicales sin límite, las colegiales hasta 500 €) que pasaran de 6,84 € al año la dejarían
    dentro, y también el incremento por movilidad (art. 19.2.f) si estaba en paro inscrita y aceptó un puesto que
    exigía cambiar de residencia (ese año y el siguiente). Con el modelo común queda fuera, por la mínima. El neto y el esfuerzo siguen con el bruto de 2026. `ingresos_bruto` (el
    de 2024) también lo usa la regla del art. 301 LGSS junto al SMI y el transporte de 2026: no cambia ningún
    resultado (el salario supera el SMI mensual en 484 € o más y el 20 % del salario es de al menos 341 € al mes).
    La cotización y el art. 20 son los de 2026: en la pareja, la madre y la enfermera el art. 20 es 0 y la
    diferencia es de pocos euros, frente a un margen de 985 a 4.877 € (en la enfermera, unos 9 € que la alejan más
    del umbral).
11. Vivienda de 69 m² para los 5 perfiles; los 3 «solo» se repiten como habitación con el hogar `comparte` (alquiler
    repartido entre `personas_comparten`), aproximación a la renta de una habitación. 69 m² sobreestima la renta de
    quien vive solo: menos entran por el tope. La habitación (un tercio del piso) es una cota inferior de su renta.
    No hay una fuente de precio de habitación que se pueda reutilizar (buscado el 2026-11-23, #302). El catálogo
    regional y datos.madrid.es no tienen precio de habitación, y el SERPAVI y el INE solo cubren vivienda completa.
    Los portales privados (idealista) publican cifras sin metodología y con condiciones no comprobadas (su aviso
    legal dio 403). La cota inferior queda declarada y las cifras de habitación no van al pitch.
12. Alquiler P50 del SERPAVI con `factor_ipc`: suelo del precio (parque de contratos, no oferta nueva); más entran
    por el tope y menos por esfuerzo (sensibilidad con el P75).
13. Las alternativas sustituyen el tope y mantienen edad e ingresos; misma cuantía; son simulados e ilustrativos, no
    una propuesta. Lo que cambia frente a `bono_vigente` sale sobre todo de quitar el tope. En la pareja, la renta es
    la de una persona y el esfuerzo el del hogar: no se compara entre criterios.
14. Corte 45 % (`CORTE`): el índice H+T del CNT (vivienda + transporte, «no más del 45 %» de la renta del hogar = 30 %
    + 15 %; H+T Index Methods, nov. 2022, p. 4); referencia estadounidense, no norma. Con el CNT, exactamente el 45 %
    sigue siendo asequible: solo es elegible si el esfuerzo es mayor que el corte (el registro previo decía ≥; es un
    cambio de frontera, no de parámetro; vale también para los criterios de #296). Es la revisión del 30 % de #296
    (`sobrecarga_30`, #100), que se fijó antes de ver resultados: con el 30 %, el término de horas bastaba para pasar
    el umbral en casi todos los municipios. El 45 % se eligió tras ver esos datos, así que el registro previo de
    #301 se escribió antes de ejecutar con los pesos y se publica la curva de cortes de 25 % a 50 %, con el 30 %
    marcado, y los criterios de #296 como sensibilidad (`simulacion_296`).
15. VTT = 0,325 × coste laboral total por hora de la Comunidad de Madrid (INE, ETCL4391, media de 2025T3–2026T2:
    30,0175 €/h) = 9,76 €/h. 0,325 es el punto medio de la banda 0,25 a 0,40 (7,50 a 12,01 €/h), no un valor de la
    fuente: CE CBA Guide 2014, p. 91 y nota 90 (HEATCO, 30 a 42 %), y Vademécum 2021-2027, p. 55. El coste laboral
    total incluye la parte del empleador (cotizaciones), y el VTT se compara con el neto del hogar: el numerador va
    inflado frente a un valor del tiempo sobre el salario neto, así que sobreestima el esfuerzo y los elegibles de
    `horas_viaje`. Madrid y no la media nacional (ETCL4443, 25,8225 €/h → 8,39 €/h) porque el producto se ofrece en
    las condiciones de DataMad: con la nacional entran menos. Valorar el tiempo de viaje con una fracción del
    salario es un supuesto, no un dato.
16. Pesos w(z, d): matriz de residencia × trabajo del INE (`matriz_trabajo`, ocupados de 2023), destinos de la
    Comunidad con municipio conocido, renormalizados. «No consta» y fuera de la región se excluyen y se declara su
    masa por municipio (se marca si pasa del 25 %): se supone que quienes trabajan fuera o sin municipio conocido
    reparten igual su destino, y quien trabaja en otra provincia puede vivir en el borde (sin comprobar). Las celdas suprimidas (< 5) no
    se imputan: no se distinguen de los ceros y repartir 2,5 a cada par ausente daría a un municipio pequeño más
    ocupados que los reales; los pequeños destinos pierden peso y los grandes lo ganan. El lugar de trabajo puede ser
    la sede de la empresa y no el centro real (sin comprobar): sobrepesa a Madrid y sus distritos centrales.
17. Madrid como destino se reparte entre sus 21 distritos por los ocupados de 2023 del Colectivo Empresarial
    (`matriz_trabajo.leer_cuotas_distritos`, sin «no consta distrito»), igual para todos los orígenes: ignora que
    cada origen trabaja más cerca, e infla las horas de quien vive junto a pocos distritos (más elegibles). Madrid
    como origen usa la fila del municipio en sus 21 distritos: no distingue entre distritos de residencia.
18. Pares sin tiempo (null: más de 120 min o sin ruta) con w > 0: 120 min (`TP_IMPUTADO`), imputación provisional, no
    cota inferior: #311 (cerrada por #350) halló nulos falsos por horarios rotos, y en el `tiempos.json` congelado el
    21-11 (#105) un nulo sigue mezclando más de 120 min, horario que falta en el GTFS y ruido de r5py; el recálculo a
    180 min queda para #161. Con ese `tiempos.json`, los pares (zona con alquiler, destino) imputados pasan de 3.746 a
    4.239 de 11.840 con peso, y las marcas de calidad no cambian: 46 por masa imputada, 1 por masa excluida y 23 por
    pocos ocupados, de 179 municipios (#103). Sensibilidades: 60 y 90 min (nulos falsos, hacia abajo), 180 min (hacia
    arriba) y sin pares imputados. Como `calcular` da con ello transporte y horas, no hace falta código de tarifas
    aparte. Los pares con w = 0 se quedan sin tiempo.
19. ref(d) = la zona con menos minutos observados hacia d, sin los imputados (el mínimo observado, no 0: la diagonal
    d → d es una mediana intrazona y puede no ser la mínima), con desempate por `zona_id`; el log declara los
    destinos cuya ref no es el propio d. H mide el viaje de más frente a la mejor ubicada, que puede no ser asequible:
    sobreestima H si nadie puede vivir allí. H = 0 para la propia ref.
20. `elegible` del municipio = pct ≥ 50 % (`PCT_MINIMO`), la mayoría de sus ocupados; es un convenio de lectura, no
    de la norma. El municipio es la mediana de sus zonas: en Madrid pesa 1 cada distrito, sin ponderar por población,
    y `pct_mediano` de los logs es la mediana entre municipios, que pesan 1 cada uno.
21. Sensibilidad parcial: regla histórica de colocación adecuada del art. 301 LGSS (RDLeg 8/2015, redacción original;
    la sustituyó el 02-03-2023 la Ley 3/2023, que no fija criterios de desplazamiento): ida y vuelta mayor del 25 % de
    la jornada diaria (8 h), coste del desplazamiento mayor del 20 % del salario mensual, o salario menos ese coste
    por debajo del SMI (la norma remite al SMI sin cuantía: se toma el del año simulado, 17.094 €, RD 126/2026,
    art. 3.1, BOE-A-2026-3815). Texto original leído en el BOE el 20-11-2026 (BOE-A-2015-11724, en vigor del
    02-01-2016 al 01-03-2023, https://www.boe.es/buscar/doc.php?id=BOE-A-2015-11724; lo sustituye la DF 4.11 de la
    Ley 3/2023, BOE-A-2023-5365). La norma pide el tiempo mínimo y se usa el mediano de 7:30 a 8:30, que es mayor:
    sobreestima los desplazamientos largos. No aplica el radio de 30 km (fuera de él no rige la presunción de
    adecuación; aplicar las excepciones sin radio subestima los largos) ni el alojamiento. «Salario mensual» = bruto
    del primer sueldo ÷ 12 (`lgss_2015`); con ÷ 14 (`lgss_2015_14`) el umbral baja (SMI, de 285 a 244 €). El coste es
    el de un solo trabajador, T ÷ n.º de sueldos (la pareja, con 5/2 días, subestima el de quien va 5 días). Va a la
    tabla de sensibilidades, no al contrato.
22. Transporte: modo `tp`, 2 viajes al día, tarifas `vigente_2026` (el descuento solo vale en 2026: favorece el
    transporte barato). El de 23 años usa el Abono Joven (hasta 25 años), tarifa plana por corona.
23. Horas trabajadas al mes = `semanas_mes` × 5 × `horas_dia` del perfil por sueldo (8 h; 37,5 h semanales para la enfermera; solo en `simulacion_296`). Pares sin alquiler
    quedan fuera; los municipios sin alquiler o sin pesos no tienen fila.
24. `perfil` = identificador por perfil y tipo de vivienda (`smi_30`, `smi_30_habitacion`...): choca con el enumerado
    de `api_estatica.PERFILES` (#103).
25. `estimado` = True siempre: el alquiler es una mediana estimada, no un contrato.
26. Ser elegible no es cobrar: la concesión va por orden de llegada hasta agotar el crédito. Personas y coste: decisión 34.

Fin del descuento del abono (#102, ficha A §7.5), `fin_descuento`: por municipio, € al mes que pierde un adulto y
un joven (15 a 25 años) si en 2027 no se prorroga el descuento, = coste_mes(`sin_descuento`) −
coste_mes(`vigente_2026`) de la forma v1 de `tarifas.json`, cada escenario con su título más barato.
27. Norma: RDL 17/2025 (BOE-A-2025-26459), art. 8: descuento del 50 % en los títulos joven y del 20 % en los
    demás abonos y 10 viajes del 1-1 al 31-12-2026, sobre la tarifa del 30-11-2025; el art. 11 obliga a la
    Comunidad y a los ayuntamientos a cubrir la pérdida de esos porcentajes que no paga el Estado. Sin prórroga
    para 2027 publicada a 2026-11-21 (ficha del BOE: solo la convalidación, BOE-A-2026-2025). El descuento total
    del abono normal es del 41,8 % frente a la oficial de 2026 (32,70 frente a 56,20 €, BOCM-20251231-2 pág. 66
    y -3 pág. 70); lo que pasa del 20 % lo pone el CRTM voluntariamente. `sin_descuento` quita todo, así que para
    el adulto es la cota superior. La cota inferior es `fin_descuento_rdl` (decisión 32). Para el joven, el 50 %
    es todo el descuento (20,00 → 10,00 €).
28. `sin_descuento` son las tarifas oficiales de 2026 (supuesto S5 de `transporte`): si las de 2027 suben, se
    pierde más.
29. Forma v1: ida y vuelta pasando por la zona A desde la corona del municipio, 5 días y 2 viajes al día, precio
    ordinario, sin ocio. Sobrestima la pérdida de quien trabaja en su corona B o C (interzonal o urbano) y la
    subestima en Cercanías: el abono de Renfe de 20 € (10 € joven; RDL 17/2025, art. 3.2.a) solo existe con
    descuento y la v1 no lo ve.
30. € al mes = media del año: el abono se compra 335/30 veces (`transporte.ABONOS_ANIO`), así que en la corona C2
    la pérdida es 35,20 € por abono (84,40 − 49,20) y 32,76 € de media al mes; el joven, 10,00 € y 9,30 €. Se
    restan los `coste_mes` ya redondeados de `tarifas.json` (18,61 − 9,31; la exacta, 9,31): ±0,01 €, lo mismo
    que ve la app. En B2, 62,43 − 36,32 = 26,11 (empate de 62,425 redondeado hacia arriba, #374).
31. Sin hogares sobrecargados: la tabla `sobrecarga` (F3-06, #100) no se publica (señal de corte, PR #293).
    Filas de `simulacion` con `criterio` = `fin_descuento`, `perfil` = `adulto` o `joven`, `elegible` = pierde
    algo (eur_mes > 0), `pct_ocupados_elegibles` nulo (no aplica) y `estimado` = True.
32. `fin_descuento_rdl`: solo se retira la parte del RDL y el CRTM mantiene la suya. Precio = vigente 2026 + 20 %
    (50 % joven) de la tarifa del 30-11-2025 (art. 8, último párrafo), con el mismo título que `vigente_2026`
    (lo comprueba un test) y la misma media del año. Esa tarifa es la de 1-2-2013 (BOCM-20130130-9, págs. 22-23,
    columna sin descuento; BOCM-20251231-3 pág. 69: «la última actualización de tarifas se produjo en el año
    2013»), salvo el Abono 30 días de C1 y C2, igualado a B3 (82 €) desde el 1-1-2022 (BOCM-20211217-35, pág. 251,
    «UNIFICACIÓN DE LAS TARIFAS DEL ABONO DE LAS ZONAS B3, C1 Y C2»), y el Abono Joven, de 20 € (sin subida en
    2026, misma pág. 69). El 50 % va solo al Abono Joven (art. 8.b: títulos «dirigidos a población joven»); los
    demás títulos, también los de un joven, llevan el 20 %. Contraste: la oficial de 2026 es la de 2025 × 1,03
    redondeada a 0,10 a la baja en todos esos títulos, también con 82 € (84,40). Supone que en 2027 el CRTM
    mantiene su parte en euros, sin tarifa nueva.
33. Sensibilidad de `fin_descuento` por corona con 3 y 5 días × 2 y 4 viajes al día (`fin_coronas`, #378), de la
    forma v1 de `tarifas.json`. No es monótona: con 3 días y 2 viajes C1 pierde 27,69 € y C2 22,32 €, porque con
    descuento C1 usa el 10 viajes (40,41 €) y C2 el abono (45,78 €), y sin él los dos pasan al sencillo (68,10 €).

Escalado a personas y coste (#302, `escalado`; registro previo de `docs/decisiones.md`, 2026-11-23):
34. Orden de magnitud, `estimado`, fuera del contrato `simulacion` y del pitch. techo(m) = A ÷ Σ pob_joven ×
    pob_joven(m) × alquiler_joven(m); con el tope, techo × f, con f acotada por el P50 y el P75 del SERPAVI
    (P75 ≤ tope: 0,75 a 1; solo P50 ≤ tope: 0,5 a 0,75; tope < P50: 0 a 0,5). Coste = personas × min(250 €, renta)
    × 12, junto al crédito de la convocatoria (31,8 millones; ACG, BDNS 805618, doc. 1560529, p. 1), que es lo que
    limita de verdad. A = asalariados de 18 a 35 años con ingresos ≤ 3 × IPREM: el umbral en bruto (la base de
    25.200 € invertida con `base_imponible`) sobre las decilas de la AEAT 2024 (Madrid, decilas nacionales,
    interpolación lineal en el SME del centil y reparto uniforme dentro de la decila), aplicado a los perceptores
    del catálogo regional. `umbral_bruto` aplica la cotización de 2026 a salarios de 2024: con un tipo 0,15 puntos
    menor el umbral sería de 29.044,31 € (mismo centil 61) y A, un 0,16 % menor. Sesgos: A, hacia abajo (el SME anualiza y quien está bajo el SMI no se cuenta); el cruce
    de pob_joven y alquiler_joven, sin signo conocido (incluye a quien vive en el piso alquilado de sus padres, y el
    asalariado se emancipa más; repartir por población sobrepesa a Madrid); f, hacia abajo (el P50 y el P75 de 69 m²
    sobreestiman la renta de un joven, decisión 11). Los municipios con alquiler_joven nulo quedan fuera de la tabla
    y su parte de A se pierde (Σ pob_joven es la de toda la Comunidad). En los no elegibles con el P50 la cuantía es
    250 € (su renta pasa del tope, de al menos 600 €). Sin la vía
    de habitación (su renta es una cota inferior, decisión 11).
"""

import logging
import re
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path
from typing import NamedTuple

import pandas as pd

from mesobra import (
    bono,
    calculo,
    censo2021,
    contratos,
    matriz_trabajo,
    neto,
    parametros_2026,
    titulares,
    transporte,
)

LOG = logging.getLogger(__name__)
PROCESSED = calculo.RAIZ / "data/processed"

# DA 90.ª.d Ley 31/2022 (BOE-A-2022-22128), prorrogada (CE, art. 134.4); 14 pagas por el Acuerdo, art. 4.4.
IPREM = D(8400)
# RD 42/2022, art. 6.1.d (BOE-A-2022-802); Acuerdo, art. 4.1.d: ingresos iguales o inferiores a 3 × IPREM.
UMBRAL_INGRESOS = 3 * IPREM
# RD 42/2022, art. 6.1.a: de 18 a 35 años, ambos incluidos.
EDAD_MIN, EDAD_MAX = 18, 35
# RD 42/2022, art. 11; Acuerdo, art. 8.1: 250 €/mes por persona beneficiaria, sin pasar de la renta.
CUANTIA = D(250)
# RD 42/2022, art. 8; Acuerdo CG 26-12-2024 (BOCM-20250110-20), Anexo II: (tope general, tope en TOPE_900_2024).
TOPES = {"vivienda": (D(600), D(900)), "habitacion": (D(300), D(450))}
CRITERIOS = ("bono_vigente", "alquiler_transporte", "horas_viaje")
CRITERIOS_296 = ("alquiler_transporte_296", "horas_viaje_296")
UMBRAL_296 = 0.30  # corte de `sobrecarga_30` (#100), el de #296
# Registro previo de #301 (docs/decisiones.md, 2026-11-19): INE, ETCL4391 (Comunidad de Madrid, coste laboral total
# por hora, media de 2025T3 a 2026T2) y ETCL4443 (nacional, mismo periodo).
COSTE_LABORAL_HORA_MADRID = 30.0175
COSTE_LABORAL_HORA_NACIONAL = 25.8225
# VTT como proporción del coste laboral: CE CBA Guide 2014 p. 91 (nota 90) y Vademécum 2021-2027 p. 55
# (banda 0,25 a 0,40).
PROPORCION_COMMUTING = 0.325
BANDA_PROPORCION = (0.25, 0.40)
VTT = PROPORCION_COMMUTING * COSTE_LABORAL_HORA_MADRID  # €/h
BANDA_VTT = tuple(p * COSTE_LABORAL_HORA_MADRID for p in BANDA_PROPORCION)
VTT_NACIONAL = PROPORCION_COMMUTING * COSTE_LABORAL_HORA_NACIONAL
CORTE = 0.45  # índice H+T del CNT (30 % de vivienda + 15 % de transporte), H+T Index Methods, nov. 2022, p. 4
PCT_MINIMO = (
    50.0  # % de ocupados elegibles para que lo sea el municipio (registro previo)
)
TP_IMPUTADO = 120  # min, imputación provisional de los pares sin tiempo con flujo (supuesto 18; 180 min en #161)
MASA_EXCLUIDA_MAX = 0.25  # se marca a los municipios con más masa excluida o imputada
POCOS_OCUPADOS = 100  # se marca a los municipios con menos ocupados observados
# Art. 301 LGSS, RDLeg 8/2015, redacción original (BOE-A-2015-11724, en vigor del 02-01-2016 al 01-03-2023):
# ida y vuelta > 25 % de la jornada diaria; coste > 20 % del salario; salario − coste < SMI.
LGSS_TIEMPO, LGSS_COSTE = 0.25, 0.20
# «Salario mensual» = bruto anual ÷ pagas: 12 por defecto; ÷ 14 es la sensibilidad (el umbral baja).
PAGAS_LGSS = {"lgss_2015": 12, "lgss_2015_14": 14}
# Escalado de #302 (decisión 34): AEAT, «Mercado de trabajo y pensiones en las fuentes tributarias» 2024.
DECILAS = bono.RAW / "aeat_asalariados_decilas_edad_madrid_2024_2026-11-23.html"
CENTILAS = bono.RAW / "aeat_recorrido_sme_centilas_2024_2026-11-23.html"
# Catálogo regional, perceptores asalariados por edad (CC BY 4.0).
PERCEPTORES = bono.RAW / "cm_perceptores_asalariados_edad_2026-11-23.csv"
# Certificado del ACG, BDNS 805618, doc. 1560529, p. 1: crédito de la ronda 2024, plurianual 2025-2026.
CREDITO_2024 = 31_800_000
# Registro previo de #302: parte de los contratos bajo el tope según el percentil SERPAVI que lo cumple.
BANDAS_F = {"p75": (0.75, 1.0), "p50": (0.5, 0.75), "sobre": (0.0, 0.5)}
EUR_PERSONA = int(CUANTIA) * 12  # € al año por persona beneficiaria
IDS = (
    "smi_30",
    "teleoperador_23",
    "pareja_mediana",
    "madre_oficina",
    "joven_mediano",
    "enfermera_26",
)

# Acuerdo CG 26-12-2024, Anexo II: 55 municipios (texto completo en BDNS 805618, doc. 1505247, «Certificado ACG»,
# leído el 2026-11-19; la FAQ 2024 p. 12 da los mismos 55; la ficha de la sede, 54, sin Moraleja de Enmedio).
TOPE_900_2024 = bono.TOPE_900 | {
    "28002": "Ajalvir",
    "28010": "Alpedrete",
    "28013": "Aranjuez",
    "28014": "Arganda del Rey",
    "28023": "Boalo, El",
    "28026": "Brunete",
    "28032": "Camarma de Esteruelas",
    "28040": "Ciempozuelos",
    "28041": "Cobeña",
    "28045": "Colmenar Viejo",
    "28044": "Colmenarejo",
    "28053": "Daganzo de Arriba",
    "28054": "Escorial, El",
    "28059": "Fuente el Saz de Jarama",
    "28068": "Guadarrama",
    "28073": "Humanes de Madrid",
    "28084": "Mejorada del Campo",
    "28089": "Moraleja de Enmedio",
    "28090": "Moralzarzal",
    "28096": "Navalcarnero",
    "28104": "Paracuellos de Jarama",
    "28129": "San Agustín del Guadalix",
    "28131": "San Lorenzo de El Escorial",
    "28132": "San Martín de la Vega",
    "28144": "Soto del Real",
    "28167": "Velilla de San Antonio",
}
# Anexo II del Acuerdo, transcripción literal (con sus erratas «Carmarma» y «Paracuellos del Jarama»).
NOMBRES_ANEXO_II = [
    "Ajalvir",
    "Alcalá de Henares",
    "Alcobendas",
    "Alcorcón",
    "Algete",
    "Alpedrete",
    "Aranjuez",
    "Arganda del Rey",
    "Arroyomolinos",
    "Boadilla del Monte",
    "Boalo, El",
    "Brunete",
    "Carmarma de Esteruelas",
    "Ciempozuelos",
    "Cobeña",
    "Collado Villalba",
    "Colmenar Viejo",
    "Colmenarejo",
    "Coslada",
    "Daganzo de Arriba",
    "Escorial, El",
    "Fuenlabrada",
    "Fuente el Saz de Jarama",
    "Galapagar",
    "Getafe",
    "Guadarrama",
    "Humanes de Madrid",
    "Leganés",
    "Madrid",
    "Majadahonda",
    "Mejorada del Campo",
    "Moraleja de Enmedio",
    "Moralzarzal",
    "Móstoles",
    "Navalcarnero",
    "Paracuellos del Jarama",
    "Parla",
    "Pinto",
    "Pozuelo de Alarcón",
    "Rivas-Vaciamadrid",
    "Rozas de Madrid, Las",
    "San Agustín del Guadalix",
    "San Fernando de Henares",
    "San Lorenzo de El Escorial",
    "San Martín de la Vega",
    "San Sebastián de los Reyes",
    "Soto del Real",
    "Torrejón de Ardoz",
    "Torrelodones",
    "Tres Cantos",
    "Valdemoro",
    "Velilla de San Antonio",
    "Villanueva de la Cañada",
    "Villanueva del Pardillo",
    "Villaviciosa de Odón",
]


def base_imponible(bruto: float | D) -> D:
    """Base imponible general: bruto − cotización − 2.000 € − reducción del art. 20 (como `neto.cuota_irpf`)."""
    # shortcut: duplica neto.py:86-87 (la issue no deja tocar neto); extraer a neto cuando se pueda tocar.
    bruto = D(str(bruto))
    rnt = max(bruto - neto.cotizacion(bruto), D(0))
    gastos = min(parametros_2026.GASTOS_OTROS, rnt)
    return max(rnt - gastos - neto._reduccion_art20(rnt), D(0))


def tope(municipio_id: str, tipo: str) -> D:
    """Renta máxima subvencionable: `tipo` es `vivienda` o `habitacion`."""
    return TOPES[tipo][municipio_id in TOPE_900_2024]


def requisitos(edad: int, ingresos: D, renta: D, maximo: D | None) -> list[str]:
    """Requisitos que fallan con su artículo; vacía = cumple. `maximo` None = sin tope (criterios alternativos)."""
    f = []
    if not EDAD_MIN <= edad <= EDAD_MAX:
        f.append("edad (RD 42/2022, art. 6.1.a)")
    if ingresos > UMBRAL_INGRESOS:
        f.append("ingresos > 3 × IPREM (RD art. 6.1.d; Acuerdo, art. 4.1.d)")
    if maximo is not None and renta > maximo:
        f.append("renta > tope (RD art. 8; Acuerdo, art. 5 y Anexo II)")
    return f


def _carga(r: dict, criterio: str, vtt: float) -> float:
    """Esfuerzo que se compara con el corte: (renta + T [+ VTT × H]) ÷ neto; en #296, horas de viaje ÷ horas trabajadas."""
    carga = (r["renta"] + r["transporte"]) / r["neto"]
    if criterio == "horas_viaje":
        carga += vtt * r["horas_extra"] / r["neto"]
    elif criterio == "horas_viaje_296":
        carga += r["horas"] / r["horas_trab"]
    return carga


def _colocacion_inadecuada(r: dict, pagas: int) -> bool:
    """Regla histórica del art. 301 LGSS: ida y vuelta > 25 % de la jornada, coste > 20 % del salario mensual o
    salario mensual menos el coste por debajo del SMI mensual."""
    viaje = 2 * r["minutos"] > LGSS_TIEMPO * r["horas_dia"] * 60
    salario, coste = r["ingresos_bruto"] / pagas, r["transporte"] / r["n_sueldos"]
    smi = float(parametros_2026.SMI_ANUAL) / pagas
    return viaje or coste > LGSS_COSTE * salario or salario - coste < smi


def fallos(
    r: dict, criterio: str, ingresos: str, vtt: float, corte: float
) -> list[str]:
    """Requisitos que fallan en una fila de pares o de municipios con `criterio` (único sitio donde se decide).
    `vtt` en €/h (solo cuenta en `horas_viaje`) y `corte` como fracción del neto. Es elegible solo si el esfuerzo
    supera el corte: el CNT dice «no más del 45 %», así que exactamente el corte sigue siendo asequible."""
    if criterio not in (*CRITERIOS, *CRITERIOS_296, *PAGAS_LGSS):
        raise ValueError(f"criterio desconocido: {criterio!r}")
    renta = D(str(r["renta"]))
    limite = tope(r["municipio_id"], r["tipo"]) if criterio == "bono_vigente" else None
    f = requisitos(r["edad"], D(str(r[ingresos])), renta, limite)
    if criterio in PAGAS_LGSS:
        if not _colocacion_inadecuada(r, PAGAS_LGSS[criterio]):
            f.append("colocación adecuada (art. 301 LGSS, RDLeg 8/2015)")
    elif criterio != "bono_vigente" and _carga(r, criterio, vtt) <= corte:
        f.append(f"esfuerzo <= {corte} (criterio alternativo, {criterio})")
    return f


def variantes() -> list[tuple[str, dict, str, str]]:
    """(id, perfil, hogar, tipo): una por perfil, más la habitación de los que viven solos."""
    salida = []
    for pid, p in zip(IDS, titulares.PERFILES, strict=True):
        salida.append((pid, p, p["perfil"], "vivienda"))
        if p["perfil"] == "solo":
            salida.append((f"{pid}_habitacion", p, "comparte", "habitacion"))
    return salida


def imputar_tiempos(
    api: dict, w: pd.DataFrame, minutos: int = TP_IMPUTADO
) -> tuple[dict, set[tuple[str, str]]]:
    """Copia de `api` con `minutos` (por defecto `TP_IMPUTADO`) en los pares (zona, destino) con w > 0 y `tp` nulo, y esos pares."""
    t = api["tiempos"]
    destinos = [d["destino_id"] for d in t["destinos"]]
    # solo los de zona: `tabla_pares` no usa los demás y su peso se perdería sin aviso
    zonas = {d["destino_id"] for d in t["destinos"] if d["tipo"] == "zona"}
    if faltan := set(w["destino"]) - zonas:
        raise ValueError(
            f"destinos con peso que no están en tiempos.json como zona: {sorted(faltan)[:5]}"
        )
    zona_mun = {
        f["properties"]["zona_id"]: f["properties"]["municipio_id"]
        for f in api["zonas"]["features"]
    }
    flujo = w.groupby("origen")["destino"].agg(set)
    tp, imputados = [list(fila) for fila in t["tp"]], set()
    for i, z in enumerate(t["origenes"]):
        for j, d in enumerate(destinos):
            if tp[i][j] is None and d in flujo.get(zona_mun[z], ()):
                tp[i][j] = minutos
                imputados.add((z, d))
    return api | {"tiempos": t | {"tp": tp}}, imputados


def tabla_pares(
    api: dict, w: pd.DataFrame, imputados: set[tuple[str, str]]
) -> pd.DataFrame:
    """Una fila por (variante, zona con alquiler, destino de zona) con alquiler, transporte, neto, horas, minutos,
    `horas_extra` (H), `imputado` y el peso `w` (0 si el municipio no tiene flujo a ese destino). `api` es la de
    `imputar_tiempos`. ref(d) = la zona con menos minutos observados hacia d, sin los pares imputados (no 0: la
    diagonal d → d es una mediana intrazona), con desempate por `zona_id`. Falla si un par con w > 0 queda sin
    transporte, horas o neto."""
    zona_mun = {
        f["properties"]["zona_id"]: f["properties"]["municipio_id"]
        for f in api["zonas"]["features"]
    }
    t = api["tiempos"]
    destinos = [
        (j, d["destino_id"]) for j, d in enumerate(t["destinos"]) if d["tipo"] == "zona"
    ]
    contrato = calculo.api_precio_contrato(
        api
    )  # el Bono sigue con el precio de contrato (#301, #329)
    filas, refs = [], {}
    for pid, p, hogar, tipo in variantes():
        # ingresos de quien solicita (decisión 9), de todo el hogar (sensibilidad) y bruto (sensibilidad)
        ingresos = p.get("sueldos_2024", p["sueldos"])  # ejercicio 2024 (decisión 10)
        bases = [float(base_imponible(b)) for b, _ in ingresos]
        horas_dia = titulares.horas_dia(p)
        horas_mes = api["tarifas"]["semanas_mes"] * titulares.DIAS_SEMANA * horas_dia
        fijos = {
            "perfil": pid,
            "tipo": tipo,
            "edad": p["edad"],
            "ingresos_base": bases[0],
            "ingresos_bruto": ingresos[0][0],
            "ingresos_hogar": sum(bases),
            "horas_dia": horas_dia,
            "horas_trab": horas_mes * len(p["sueldos"]),
            "n_sueldos": len(p["sueldos"]),
            # la pareja de 29: cada una firma y cumple sola (Acuerdo, art. 4.1.d); habitación: una
            "beneficiarios": len(p["sueldos"]) if tipo == "vivienda" else 1,
        }
        for j, d in destinos:
            entrada = {
                "hogar": {"perfil": hogar, "edad": p["edad"]},
                "sueldos": [
                    {"destino": d, "dias": dias, "modo": "tp", "bruto": bruto}
                    for bruto, dias in p["sueldos"]
                ],
            }
            zonas = calculo.calcular(contrato, entrada)["zonas"]
            con_tiempo = [
                (t["tp"][i][j], z)
                for i, z in enumerate(t["origenes"])
                if t["tp"][i][j] is not None and (z, d) not in imputados
            ]
            refs[d] = min(con_tiempo)[1] if con_tiempo else None
            ref = zonas[refs[d]]["horas"] if con_tiempo else None
            for i, (zona, z) in enumerate(zonas.items()):
                if z["alquiler"] is None:
                    continue
                h = z["horas"]
                filas.append(
                    fijos
                    | {
                        "zona_id": zona,
                        "municipio_id": zona_mun[zona],
                        "destino": d,
                        "minutos": t["tp"][i][j],
                        "alquiler": z["alquiler"],
                        "alquiler_p75": z["alquiler_p75"],
                        "transporte": z["transporte"],
                        "neto": z["neto"],
                        "horas": h,
                        "horas_extra": None if None in (h, ref) else max(0.0, h - ref),
                        "imputado": (zona, d) in imputados,
                    }
                )
    df = pd.DataFrame(filas).merge(
        w.rename(columns={"origen": "municipio_id"}),
        on=["municipio_id", "destino"],
        how="left",
        validate="many_to_one",
    )
    df["w"] = df["w"].fillna(0.0)
    incompletos = df[
        (df["w"] > 0)
        & df[["transporte", "horas", "horas_extra", "neto"]].isna().any(axis=1)
    ]
    if not incompletos.empty:
        raise ValueError(
            f"{len(incompletos)} pares con peso sin transporte, horas o neto"
        )
    LOG.info(
        "pares: %d; con peso: %d; imputados: %d",
        len(df), (df["w"] > 0).sum(), df["imputado"].sum(),
    )  # fmt: skip
    propia = {d: r for d, r in refs.items() if r != d}
    LOG.info(
        "destinos cuya referencia no es el propio destino: %d: %s", len(propia), propia
    )
    return df


MEDIDAS = ("alquiler", "alquiler_p75", "transporte", "horas")
FIJAS = (
    "perfil", "tipo", "edad", "ingresos_base", "ingresos_bruto", "ingresos_hogar", "horas_dia", "horas_trab", "n_sueldos",
    "beneficiarios", "neto", "zona_id", "municipio_id",
)  # fmt: skip


def tabla_zonas(pares: pd.DataFrame) -> pd.DataFrame:
    """Como #296: una fila por (variante, zona) con la mediana entre destinos de zona, sin ponderar y sin los
    pares imputados."""
    completas = pares[~pares["imputado"]].dropna(subset=list(MEDIDAS))
    zonas = completas.groupby(list(FIJAS), as_index=False)[list(MEDIDAS)].median()
    LOG.info(
        "tabla_zonas: descartados %d de %d pares (imputados o sin medida) y %d de %d zonas",
        len(pares) - len(completas), len(pares),
        len(pares.drop_duplicates(["perfil", "zona_id"])) - len(zonas),
        len(pares.drop_duplicates(["perfil", "zona_id"])),
    )  # fmt: skip
    return zonas


def _municipios(zonas: pd.DataFrame, medidas: tuple[str, ...]) -> pd.DataFrame:
    """Mediana de sus zonas por (perfil, municipio)."""
    # las columnas fijas en la clave: si no fueran constantes, saldrían claves repetidas y `validar` fallaría
    claves = [c for c in zonas.columns if c not in MEDIDAS and c != "zona_id"]
    return zonas.groupby(claves, as_index=False)[list(medidas)].median()


class Escenario(NamedTuple):
    """Cómo se mide: ingresos (`base`, `bruto` u `hogar`), columna de alquiler, VTT en €/h y corte (fracción)."""

    ingresos: str = "base"
    alquiler: str = "alquiler"
    vtt: float = VTT
    corte: float = CORTE


def _ok(t: pd.DataFrame, criterio: str, e: Escenario) -> list[bool]:
    return [
        not fallos(r, criterio, f"ingresos_{e.ingresos}", e.vtt, e.corte)
        for r in t.assign(renta=t[e.alquiler]).to_dict("records")
    ]


def _pct_municipios(
    pares: pd.DataFrame, mun: pd.DataFrame, criterio: str, e: Escenario
) -> list[float]:
    """% de ocupados elegibles de cada fila de `mun`: la mediana de sus zonas, cada una Σ_d w · 1[elegible]."""
    if criterio == "bono_vigente":
        return [100.0 * ok for ok in _ok(mun, criterio, e)]
    p = pares[pares["w"] > 0]
    por = [p["perfil"], p["municipio_id"], p["zona_id"]]
    zona = (p["w"] * _ok(p, criterio, e)).groupby(por).sum() / p["w"].groupby(por).sum()
    pct = 100 * zona.groupby(level=["perfil", "municipio_id"]).median()
    return pct.loc[pd.MultiIndex.from_frame(mun[["perfil", "municipio_id"]])].tolist()


def _filas(
    mun: pd.DataFrame, criterio: str, pct: list[float], e: Escenario
) -> list[tuple]:
    filas = []
    for r, p in zip(mun.to_dict("records"), pct, strict=True):
        ok = p >= PCT_MINIMO
        eur = (
            float(min(CUANTIA * r["beneficiarios"], D(str(r[e.alquiler]))))
            if ok
            else 0.0
        )
        filas.append((r["perfil"], r["municipio_id"], criterio, ok, eur, True, p))
    return filas


def _tabla(filas: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(
        filas, columns=list(contratos.CONTRATOS["simulacion"]["columnas"])
    )
    contratos.validar(df, "simulacion")
    return df


def simulacion(
    pares: pd.DataFrame,
    criterios: tuple[str, ...] = CRITERIOS,
    **escenario: str | float,
) -> pd.DataFrame:
    """Tabla `simulacion` por (perfil, municipio, criterio), validada. `escenario`: los campos de `Escenario`."""
    e = Escenario(**escenario)
    con_peso = pares[pares["w"] > 0]["municipio_id"].unique()
    zonas = pares.drop_duplicates(["perfil", "zona_id"])[
        [*FIJAS, "alquiler", "alquiler_p75"]
    ]
    mun = _municipios(
        zonas[zonas["municipio_id"].isin(con_peso)], ("alquiler", "alquiler_p75")
    )
    return _tabla(
        [
            f
            for c in criterios
            for f in _filas(mun, c, _pct_municipios(pares, mun, c, e), e)
        ]
    )


def simulacion_296(zonas: pd.DataFrame) -> pd.DataFrame:
    """Sensibilidad: los criterios de #296 (corte del 30 %, mediana de los destinos sin ponderar) sobre `tabla_zonas`.
    El pct es 100 o 0: no hay ocupados."""
    e = Escenario(corte=UMBRAL_296)
    mun = _municipios(zonas, MEDIDAS)
    return _tabla(
        [
            f
            for c in ("bono_vigente", *CRITERIOS_296)
            for f in _filas(mun, c, [100.0 * ok for ok in _ok(mun, c, e)], e)
        ]
    )


def cambios(df: pd.DataFrame) -> pd.DataFrame:
    """Por perfil y criterio: municipios elegibles, pct mediano de ocupados elegibles y municipios que entran y que
    salen frente a `bono_vigente`."""
    ok = df.pivot(
        index=["perfil", "municipio_id"], columns="criterio", values="elegible"
    ).astype(bool)
    pct = df.groupby(["perfil", "criterio"])["pct_ocupados_elegibles"].median()
    filas = []
    for perfil, g in ok.groupby(level="perfil"):
        for c in g.columns:
            filas.append(
                {
                    "perfil": perfil,
                    "criterio": c,
                    "elegibles": int(g[c].sum()),
                    "pct_mediano": float(pct[(perfil, c)]),
                    "entran": int((~g["bono_vigente"] & g[c]).sum()),
                    "salen": int((g["bono_vigente"] & ~g[c]).sum()),
                }
            )
    return pd.DataFrame(filas)


def curva(pares: pd.DataFrame) -> pd.DataFrame:
    """Municipios elegibles por perfil y criterio con cada corte de 25 % a 50 % (columnas: el corte)."""
    cortes = [round(0.25 + 0.05 * i, 2) for i in range(6)]
    cols = [
        simulacion(pares, ("alquiler_transporte", "horas_viaje"), corte=c)
        .groupby(["criterio", "perfil"])["elegible"]
        .sum()
        .rename(c)
        for c in cortes
    ]
    return pd.concat(cols, axis=1)


def _imputacion(pares: pd.DataFrame) -> pd.DataFrame:
    """Por municipio de residencia: pares (zona, destino) imputados y masa de w en pares imputados (mediana de sus
    zonas, con 0 en las que no tienen ninguno)."""
    una = pares[pares["perfil"] == pares["perfil"].iloc[0]]
    zonas = una.assign(masa=una["w"] * una["imputado"]).groupby(
        ["municipio_id", "zona_id"]
    )
    zonas = zonas.agg(pares=("imputado", "sum"), masa=("masa", "sum"))
    return zonas.groupby(level="municipio_id").agg(
        pares=("pares", "sum"), masa=("masa", "median")
    )


def calidad(
    pares: pd.DataFrame, excluida: pd.Series, observados: pd.Series
) -> pd.DataFrame:
    """Tabla auxiliar por municipio de residencia: masa excluida, masa imputada (nula si no tiene fila en
    `simulacion`), ocupados observados y marcas de poca fiabilidad."""
    c = pd.DataFrame(
        {
            "masa_excluida": excluida,
            "masa_imputada": _imputacion(pares)["masa"],
            "ocupados_observados": observados,
        }
    ).rename_axis("municipio_id")
    c["marca_imputada"] = c["masa_imputada"] > MASA_EXCLUIDA_MAX
    c["marca_excluida"] = c["masa_excluida"] > MASA_EXCLUIDA_MAX
    c["marca_pocos"] = c["ocupados_observados"] < POCOS_OCUPADOS
    return c.reset_index()


# Fin del descuento (decisiones 27 a 31): caso base de la nota del 15-11 de #102
CRITERIO_FIN = "fin_descuento"
DIAS_FIN, VIAJES_FIN = 5, 2
EDADES_FIN = {"adulto": "general", "joven": "joven"}  # perfil → edad de `tarifas.json`
NORMA_DESCUENTO = (
    "RDL 17/2025 (BOE-A-2025-26459), art. 8: 50 % joven y 20 % resto del 1-1 al 31-12-2026, más el "
    "descuento voluntario del CRTM; sin prórroga para 2027 publicada. Si no se prorroga, con las tarifas "
    "oficiales de 2026. Adulto: fin_descuento es la cota superior (quita también la parte del CRTM) y "
    "fin_descuento_rdl la inferior (solo la del RDL). €/mes = media del año (335/30 abonos ÷ 12): por abono, "
    "35,20 € en C2 y 10,00 € el joven"
)
CRITERIO_RDL = "fin_descuento_rdl"
# RDL 17/2025, art. 8.c (abonos y 10 viajes) y 8.b (títulos joven)
PCT_RDL, PCT_RDL_JOVEN = D("0.20"), D("0.50")
# Tarifa del 30-11-2025, precio ordinario (decisión 32): BOCM-20130130-9 págs. 22-23; C1 y C2, BOCM-20211217-35
ABONO_2025 = {"A": D("54.60"), "B1": D("63.70"), "B2": D("72.00")}
ABONO_2025 |= dict.fromkeys(("B3", "C1", "C2"), D("82.00"))
DIEZ_VIAJES_2025 = {"metro_a": D("12.20")}
# interurbano por saltos de corona, como `transporte.DIEZ_VIAJES_INTERURBANO`
DIEZ_VIAJES_INTERURBANO_2025 = [
    D(x) for x in ("8.50", "12.20", "16.10", "23.00", "29.70", "37.40")
]


def _sin_rdl(titulo: str, corona: str) -> D:
    """Coste al mes del título de la v1 si solo se retira el descuento del RDL (decisión 32)."""
    vig, ofi = ("vigente_2026", "ordinario"), ("sin_descuento", "ordinario")
    abono = transporte.ABONOS_ANIO / 12
    if titulo == "Abono Joven":  # sin subida en 2026: la oficial es la del 30-11-2025
        precios, q = (transporte.ABONO_JOVEN[vig], transporte.ABONO_JOVEN[ofi]), abono
    elif titulo == "Abono 30 días":
        precios, q = (transporte.ABONO_30[corona][vig], ABONO_2025[corona]), abono
    elif titulo == "10 viajes":
        cmin, cmax, productos = transporte._partes(
            transporte.clave_v1(corona, VIAJES_FIN)
        )
        if productos != ["metro_a"] and productos != ["interurbano"]:
            raise ValueError(f"10 viajes sin tarifa de 2025 para {productos}")
        hoy = transporte._diez_viajes(productos[0], cmin, cmax)[vig]
        saltos = transporte._i(cmax) - transporte._i(cmin)
        ref = DIEZ_VIAJES_2025.get(productos[0]) or DIEZ_VIAJES_INTERURBANO_2025[saltos]
        precios, q = (hoy, ref), 2 * DIAS_FIN * transporte.SEMANAS_MES / 10
    else:
        raise ValueError(f"título sin tarifa de 2025: {titulo!r}")
    pct = PCT_RDL_JOVEN if titulo == "Abono Joven" else PCT_RDL
    return transporte._redondea((F(precios[0]) + F(pct) * F(precios[1])) * q)


def _tarifa(
    api: dict,
    esc: str,
    edad: str,
    corona: str,
    caso: tuple[int, int] = (DIAS_FIN, VIAJES_FIN),
) -> dict:
    """Entrada de la forma v1 de `tarifas.json` (`titulo`, `coste_mes`); `caso` = (días, viajes al día)."""
    dias, viajes = caso
    return api["tarifas"]["escenarios"][esc][edad][str(viajes)][corona][dias - 1]


def fin_descuento(api: dict) -> pd.DataFrame:
    """Tabla `simulacion` con los € al mes que pierde cada perfil por municipio si se acaba el descuento: todo
    (`fin_descuento`) o solo la parte del RDL (`fin_descuento_rdl`)."""
    coronas = {}
    for f in api["zonas"]["features"]:
        m, c = f["properties"]["municipio_id"], f["properties"]["corona"]
        if coronas.setdefault(m, c) != c:
            raise ValueError(f"municipio {m} en dos coronas: {coronas[m]} y {c}")

    def fila(esc: str, edad: str, corona: str) -> tuple[str, D]:
        f = _tarifa(api, esc, edad, corona)
        return f["titulo"], D(str(f["coste_mes"]))

    filas = []
    for m, corona in sorted(coronas.items()):
        for perfil, edad in EDADES_FIN.items():
            titulo, hoy = fila("vigente_2026", edad, corona)
            for criterio, sin in [
                (CRITERIO_FIN, fila("sin_descuento", edad, corona)[1]),
                (CRITERIO_RDL, _sin_rdl(titulo, corona)),
            ]:
                eur = sin - hoy
                filas.append(
                    (perfil, m, criterio, eur > 0, float(eur), True, float("nan"))
                )
    return _tabla(filas)


def fin_coronas(api: dict) -> pd.DataFrame:
    """Sensibilidad de `fin_descuento` (decisión 33): € al mes por corona, perfil, días (3 y 5) y viajes (2 y 4)."""

    def coste(esc: str, edad: str, corona: str, dias: int, viajes: int) -> D:
        return D(str(_tarifa(api, esc, edad, corona, (dias, viajes))["coste_mes"]))

    return pd.DataFrame(
        [
            (c, perfil, dias, viajes, float(coste("sin_descuento", edad, c, dias, viajes)
                                            - coste("vigente_2026", edad, c, dias, viajes)))
            for c in api["tarifas"]["orden_coronas"]
            for perfil, edad in EDADES_FIN.items()
            for dias in (3, DIAS_FIN)
            for viajes in (VIAJES_FIN, 4)
        ],
        columns=["corona", "perfil", "dias", "viajes_dia", "eur_mes"],
    )  # fmt: skip


def _texto(ruta: Path) -> str:
    return re.sub(
        r"\s+", " ", re.sub(r"<[^>]+>", " ", ruta.read_text(encoding="utf-8"))
    )


def _num(x: str) -> int:
    return int(x.replace(".", ""))


_N = r"(\d{1,3}(?:\.\d{3})*)"


def leer_decilas(ruta: Path = DECILAS) -> pd.DataFrame:
    """Asalariados de Madrid por decila nacional del SME y tramo de edad (AEAT 2024); falla si no cuadra."""
    t = _texto(ruta)
    cols = ["total", "hasta25", "de26a35", "de36a45", "de46a55", "de56a65", "mas65"]
    filas = re.findall(rf"Decil (\d+)(?: Mediana)?{(' ' + _N) * 7}", t)
    total = re.search(rf"Mayor de 65 años Total{(' ' + _N) * 7}", t)
    if [f[0] for f in filas] != [str(i) for i in range(1, 11)] or total is None:
        raise ValueError(f"Se esperaban 10 decilas y la fila Total, y hay {len(filas)}")
    df = pd.DataFrame(
        [[_num(x) for x in f[1:]] for f in filas], columns=cols, index=range(1, 11)
    )
    if (df.sum() != [_num(x) for x in total.groups()]).any():
        raise ValueError(
            f"Las decilas no suman el Total:\n{df.sum()}\n{total.groups()}"
        )
    return df


def leer_centilas(ruta: Path = CENTILAS) -> pd.DataFrame:
    """Centiles del SME (AEAT 2024): n, sme, inf, sup y recorrido; falla si no son los 100 contiguos."""
    filas = re.findall(rf"(?<!\S)(\d{{1,3}}){(' ' + _N) * 5} \d+,\d+%", _texto(ruta))
    df = pd.DataFrame(
        [[_num(x) for x in f] for f in filas],
        columns=["centil", "n", "sme", "inf", "sup", "recorrido"],
    ).set_index("centil")
    contiguos = (df["inf"].iloc[1:].to_numpy() == df["sup"].iloc[:-1].to_numpy()).all()
    if list(df.index) != list(range(1, 101)) or not contiguos:
        raise ValueError(f"Se esperaban 100 centiles contiguos y hay {len(df)}")
    return df


def leer_perceptores(ruta: Path = PERCEPTORES) -> tuple[int, int]:
    """Perceptores asalariados de 18 a 25 y de 26 a 35 años en 2024 (Total sexos y nacionalidades)."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Año"] == "2024")
        & (df["Sexo"] == "Total")
        & (df["Nacionalidad"] == "Total")
    ]
    v = [
        df.loc[
            df["Concepto"].str.startswith(f"Total asalariados de {tramo} años"), "Valor"
        ]
        for tramo in ("18 a 25", "26 a 35")
    ]
    if any(len(x) != 1 for x in v):
        raise ValueError(f"Se esperaba una fila por tramo y hay {[len(x) for x in v]}")
    return int(v[0].iloc[0]), int(v[1].iloc[0])


def umbral_bruto() -> D:
    """Mayor bruto (al céntimo) cuya base imponible no pasa de `UMBRAL_INGRESOS`, por bisección."""
    lo, hi = 0, 10_000_000  # céntimos; base_imponible no decrece con el bruto
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if base_imponible(D(mid) / 100) <= UMBRAL_INGRESOS:
            lo = mid
        else:
            hi = mid - 1
    return D(lo) / 100


def posicion_en_centiles(centilas: pd.DataFrame, umbral: D) -> float:
    """Centiles completos bajo `umbral` más la fracción del que lo contiene (interpolación lineal en el SME)."""
    u = float(umbral)
    c = centilas[(centilas["inf"] <= u) & (u < centilas["sup"])]
    if len(c) != 1:
        raise ValueError(f"El umbral {u} no cae en ningún centil")
    c = c.iloc[0]
    return float(c.name - 1 + (u - c["inf"]) / (c["sup"] - c["inf"]))


def parte_bajo(decilas: pd.Series, pos: float) -> float:
    """Parte de un tramo bajo `pos` centiles: decilas completas y reparto uniforme en la del corte."""
    d, resto = divmod(pos, 10)
    return float(
        (decilas.iloc[: int(d)].sum() + decilas.iloc[int(d)] * resto / 10)
        / decilas.sum()
    )


def asalariados_bajo_umbral(
    decilas: pd.DataFrame, centilas: pd.DataFrame, perceptores: tuple[int, int]
) -> float:
    """A: asalariados de 18 a 35 años con ingresos ≤ 3 × IPREM = Σ parte bajo el umbral × perceptores del tramo."""
    pos = posicion_en_centiles(centilas, umbral_bruto())
    return (
        parte_bajo(decilas["hasta25"], pos) * perceptores[0]
        + parte_bajo(decilas["de26a35"], pos) * perceptores[1]
    )


def escalado(
    df_p50: pd.DataFrame,
    df_p75: pd.DataFrame,
    pob_joven: pd.Series,
    alquiler_joven: pd.Series,
    a: float,
) -> pd.DataFrame:
    """Personas y coste por municipio (decisión 34): techo = A ÷ Σ pob_joven × pob_joven × alquiler_joven.

    `df_p50` y `df_p75`: `simulacion` con `bono_vigente` y `smi_30` con el alquiler P50 y con el P75. Σ pob_joven es
    la de toda la Comunidad: los municipios con `alquiler_joven` nulo (el INE suprime celdas) no reciben fila y su
    parte de A se pierde (subestima). La cuantía de los no elegibles con el P50 es 250 €: su renta pasa del tope,
    que es de al menos 600 €, así que min(250, renta) = 250.
    """
    d = pd.DataFrame({"pob": pob_joven, "alq": alquiler_joven}).dropna()
    m = df_p50.set_index("municipio_id").join(d, how="inner")
    fuera = pob_joven.index.difference(m.index)
    LOG.info(
        "escalado: %d municipios sin fila (sin alquiler_joven, población o fila en `simulacion`): %s; su población joven (cuenta en Σ, su parte de A se pierde): %d",
        len(fuera), sorted(fuera), pob_joven[fuera].sum(),
    )  # fmt: skip
    m["p75"] = df_p75.set_index("municipio_id")["elegible"].reindex(m.index)
    if m["p75"].isna().any():
        raise ValueError(f"sin fila con el P75: {sorted(m.index[m['p75'].isna()])}")
    banda = (
        pd.Series("sobre", index=m.index)
        .mask(m["elegible"], "p50")
        .mask(m["p75"], "p75")
    )
    f = pd.DataFrame(
        banda.map(BANDAS_F).tolist(), index=m.index, columns=["f_min", "f_max"]
    )
    out = f.assign(techo=a / pob_joven.sum() * m["pob"] * m["alq"])
    eur = m["eur_mes"].where(m["elegible"], float(CUANTIA))
    for lado in ("min", "max"):
        out[f"personas_{lado}"] = out["techo"] * out[f"f_{lado}"]
        out[f"coste_{lado}"] = out[f"personas_{lado}"] * eur * 12
    return out.assign(estimado=True).rename_axis("municipio_id").reset_index()


def comprobar_parada(esc: pd.DataFrame, bono_2022: pd.DataFrame) -> None:
    """Criterios de parada del registro: cota superior bajo las aceptadas de 2022 (50 o más) o techo < solicitudes."""
    ace = bono_2022.dropna(subset=["municipio_id"]).set_index("municipio_id")[
        "aceptadas"
    ]
    ace = ace[ace >= 50]
    cota = esc.set_index("municipio_id")["personas_max"].reindex(ace.index).fillna(0)
    bajo = cota[cota < ace]
    techo = esc["techo"].sum()
    if len(bajo) or techo < bono.TOTALES[0]:
        raise RuntimeError(
            f"Criterio de parada de #302: techo {techo:.0f} (solicitudes de 2022: {bono.TOTALES[0]}); "
            f"cota superior bajo las aceptadas de 2022 en {len(bajo)} municipios:\n"
            + pd.DataFrame({"personas_max": cota, "aceptadas": ace})
            .loc[bajo.index]
            .round(0)
            .to_string()
        )


def _log_tabla(titulo: str, t: pd.DataFrame) -> None:
    LOG.info("%s:\n%s", titulo, t.round(3).to_string())


def pares_con_imputacion(
    api: dict, w: pd.DataFrame, minutos: int = TP_IMPUTADO
) -> pd.DataFrame:
    """Tabla de pares de `tabla_pares` con `minutos` imputados a los pares sin tiempo con w > 0 (`imputar_tiempos`)."""
    api_imp, imputados = imputar_tiempos(api, w, minutos)
    return tabla_pares(api_imp, w, imputados)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    api = calculo.leer_api(calculo.RAIZ / "app/datos")
    nombres = {
        f["properties"]["municipio_id"]: f["properties"]["nombre"]
        for f in api["zonas"]["features"]
        if f["properties"]["tipo"] == "municipio"
    } | {"28079": "Madrid"}
    matriz, cuotas = (
        matriz_trabajo.leer_matriz(),
        matriz_trabajo.leer_cuotas_distritos(),
    )
    w, excluida = matriz_trabajo.pesos(matriz, cuotas)
    pares = pares_con_imputacion(api, w)
    df = simulacion(pares)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "simulacion.csv", index=False)
    LOG.info("simulacion.csv: %d filas", len(df))
    df_p50 = df[(df["criterio"] == "bono_vigente") & (df["perfil"] == "smi_30")]
    df_p75 = simulacion(pares, ("bono_vigente",), alquiler="alquiler_p75")
    df_p75 = df_p75[df_p75["perfil"] == "smi_30"]
    a = asalariados_bajo_umbral(leer_decilas(), leer_centilas(), leer_perceptores())
    esc = escalado(
        df_p50,
        df_p75,
        bono.poblacion_joven(bono._edades()),
        censo2021.pct_alquiler_joven(),
        a,
    )
    comprobar_parada(esc, bono.leer_bono())
    esc.to_csv(PROCESSED / "simulacion_escalado.csv", index=False)
    LOG.info(
        "escalado (estimado): A %.0f; Comunidad:\n%s\ncrédito %d €: %.0f personas-año en 2025-2026 (la mitad por año)\n28079:\n%s",
        a, esc[["techo", "personas_min", "personas_max", "coste_min", "coste_max"]].sum().round(0).to_string(),
        CREDITO_2024, CREDITO_2024 / EUR_PERSONA, esc[esc["municipio_id"] == "28079"].round(2).T.to_string(),
    )  # fmt: skip
    fin = fin_descuento(api)
    fin.to_csv(PROCESSED / "simulacion_fin_descuento.csv", index=False)
    _log_tabla(
        f"fin del descuento, €/mes por municipio (estimado; {NORMA_DESCUENTO})",
        fin.groupby(["criterio", "perfil"])["eur_mes"].describe(),
    )
    sens = fin_coronas(api)
    sens.to_csv(PROCESSED / "simulacion_fin_descuento_coronas.csv", index=False)
    _log_tabla(
        f"fin_descuento por corona, días y viajes al día (€/mes, estimado; decisión 33; {NORMA_DESCUENTO})",
        sens.pivot(
            index="corona", columns=["perfil", "dias", "viajes_dia"], values="eur_mes"
        ),
    )
    cal = calidad(pares, excluida, matriz_trabajo.ocupados_observados(matriz))
    cal.to_csv(PROCESSED / "simulacion_calidad.csv", index=False)
    LOG.info(
        "simulacion_calidad.csv: %d municipios; marca_imputada %d, marca_excluida %d, marca_pocos %d",
        len(cal), cal["marca_imputada"].sum(), cal["marca_excluida"].sum(), cal["marca_pocos"].sum(),
    )  # fmt: skip
    sin_fila = set(nombres) - set(df["municipio_id"])
    LOG.info(
        "municipios sin fila (sin alquiler, sin pesos o sin ruta): %d", len(sin_fila)
    )
    alta = excluida[excluida > MASA_EXCLUIDA_MAX]
    LOG.info(
        "masa excluida (otras provincias o «No consta») > %d %%: %s",
        100 * MASA_EXCLUIDA_MAX,
        {nombres.get(m, m): round(float(x), 3) for m, x in alta.items()},
    )
    _log_tabla("masa excluida por municipio", excluida.describe())
    imp = _imputacion(pares)
    LOG.info(
        "imputados a %d min: %d pares; masa de w por municipio de residencia (mediana de sus zonas; media %.4f, máx. %.4f); los 10 mayores:\n%s",
        TP_IMPUTADO, imp["pares"].sum(), imp["masa"].mean(), imp["masa"].max(),
        imp.sort_values("masa", ascending=False).head(10).rename(index=nombres).round(4).to_string(),
    )  # fmt: skip
    _log_tabla(
        "base (corte 0,45, VTT 9,76)", cambios(df).set_index(["perfil", "criterio"])
    )
    _log_tabla("curva de cortes: municipios elegibles", curva(pares))
    uniformes = pd.Series(1 / len(cuotas), index=cuotas.index)
    sensibilidades = {
        "VTT 7,50": simulacion(pares, vtt=BANDA_VTT[0]),
        "VTT 12,01": simulacion(pares, vtt=BANDA_VTT[1]),
        "VTT nacional": simulacion(pares, vtt=VTT_NACIONAL),
        "LGSS 2015 (÷ 12)": simulacion(pares, ("bono_vigente", "lgss_2015")),
        "LGSS 2015 (÷ 14)": simulacion(pares, ("bono_vigente", "lgss_2015_14")),
        "criterios de #296": simulacion_296(tabla_zonas(pares)),
        "ingresos = bruto": simulacion(pares, ingresos="bruto"),
        "regla del RD (suma del hogar)": simulacion(pares, ingresos="hogar"),
        "alquiler P75": simulacion(pares, alquiler="alquiler_p75"),
        "tiempo imputado 60 min": simulacion(pares_con_imputacion(api, w, 60)),
        "tiempo imputado 90 min": simulacion(pares_con_imputacion(api, w, 90)),
        "tiempo imputado 180 min": simulacion(pares_con_imputacion(api, w, 180)),
        "sin pares imputados (w renormalizado)": simulacion(pares[~pares["imputado"]]),
        "cuotas de distrito uniformes": simulacion(
            pares_con_imputacion(api, matriz_trabajo.pesos(matriz, uniformes)[0])
        ),
    }
    for nombre, s in sensibilidades.items():
        _log_tabla(
            f"sensibilidad {nombre}", cambios(s).set_index(["perfil", "criterio"])
        )


if __name__ == "__main__":
    main()
