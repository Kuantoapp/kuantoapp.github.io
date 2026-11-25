# Verificaciones: renta, tenencia, sobrecarga y Bono Alquiler Joven

> Las afirmaciones sobre renta, vivienda y el Bono Alquiler Joven de la ficha de la idea, comprobadas con el INE, Eurostat, el catálogo de la Comunidad de Madrid y el BOCM antes de construir nada. Es una de las verificaciones de Kuanto; qué significa cada estado y el resto están en el [índice](README.md).

Resuelve las marcas «(verificar)» de la sección 16 de la [ficha](../../ideas/plan1/idea-definitiva/propuesta-A-unificada.md) que pide la issue F0-04 ([#67](https://github.com/Kuantoapp/kuantoapp.github.io/issues/67)), en el orden de la issue. No cambia la ficha: lo aplica F1-16 ([#84](https://github.com/Kuantoapp/kuantoapp.github.io/issues/84)).

- **Fecha de consulta:** 2026-11-14, la misma en todas las filas.
- **Método:** skill `dm-verificacion-fuentes`. Tres agentes `dm-verificador-fuentes` leyeron al publicador original. Después, la sesión principal volvió a leer en bruto, con `curl` y `python`, cada cifra y cada estructura que se cita aquí. No se ha descargado nada en `data/`.
- **Estados:** VERIFICADO (coincide entera); FALSO (el publicador la contradice, entera o en parte; el valor correcto va en «texto corregido»); NO VERIFICADO (no se encontró publicada donde debería estar, o no se pudo leer).
- API del catálogo regional: `https://datos.comunidad.madrid/catalogo/api/3/action/package_show?id=<id>` redirige a `https://datos.comunidad.madrid/api/action/package_show?id=<id>`. Respondió sin bloqueos, así que no hizo falta el plan B.

## 1. Bono Alquiler Joven 2022: cifras y motivo de los rechazos

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 1a | 51.735 solicitudes, 11.477 aceptadas, un 22 % (§2, §12.1) | VERIFICADO | CSV del dataset `spacm_bono_alquiler_joven_2022` ([ficha CKAN](https://datos.comunidad.madrid/catalogo/dataset/spacm_bono_alquiler_joven_2022), `metadata_modified` 2026-02-03, CC BY 4.0). Sumado en bruto: 160 filas; 51.735 solicitudes, 11.477 aceptadas y 40.258 rechazadas; aceptadas + rechazadas = solicitudes en todas las filas; 22,18 % | «51.735 solicitudes, 11.477 aceptadas (22,2 %) y 40.258 rechazadas» | Ninguna |
| 1b | «3.352 solicitudes sin municipio» (§12.1) | VERIFICADO | Última fila del CSV: `Otro;-;3352;0;3352`. Notas de la ficha CKAN: son solicitantes que, «en lugar de aportar un contrato de alquiler de un inmueble localizado en un municipio concreto», dijeron que podían firmarlo y no lo presentaron | «3.352 solicitudes "Otro", sin contrato de un inmueble concreto; ninguna aceptada» | F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)): esa fila sale del cruce por municipio. Sin ella, la tasa de aceptación es del 23,7 % |
| 1c | El dataset permite saber por qué se rechazó (§2: «no sabemos por qué se rechazó el resto») | FALSO | El CSV y el JSON del dataset solo tienen 5 campos: `municipio_nombre;municipio;solicitudes;aceptadas;rechazadas`. Ni la ficha CKAN ni sus notas dicen nada del motivo | «El dataset da rechazadas por municipio, sin motivo» | F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)): `rechazadas` es un total y no se puede leer como «demanda sin crédito» |
| 1d | Los rechazos se deben a falta de presupuesto (hipótesis de la apertura del pitch, §18) | FALSO como causa única | Orden de 1-08-2024, listado definitivo de excluidos ([BOCM-20240816-2](https://www.bocm.es/boletin/CM_Orden_BOCM/2024/08/16/BOCM-20240816-2.PDF), leída en bruto). Excluye «por no reunir los requisitos establecidos» o, cumpliéndolos, «por haber sido declarado agotado el crédito disponible». El agotamiento se declaró por Orden de 6-11-2023 ([BOCM-20231114-19](https://www.bocm.es/boletin/CM_Boletin_BOCM/2023/11/14/27100.PDF), leída en bruto), que además «se cierra el plazo de presentación» de solicitudes. La concesión fue directa, por orden cronológico (referencia de ayudas de vivienda, §2.1). No hay recuento oficial por motivo: la sede ya no enlaza el listado de excluidos de la concesión, solo los de la fase de pago, y la orden de agotamiento no da cifras | «Se aceptó el 22 %; el resto se excluyó por no cumplir requisitos o porque se agotó el crédito (declarado el 6-11-2023, lo que además cerró el plazo de solicitudes). No hay recuento por motivo» | F5-05 ([#111](https://github.com/Kuantoapp/kuantoapp.github.io/issues/111)) y D11: la apertura no puede decir que la demanda supera a la ayuda. Toca el plan B de §18 (abrir con el precio de la hora) o la frase corregida. F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)) presenta los rechazos como una mezcla de motivos |

## 2. Unidades y niveles del ADRH 2024 (INE)

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 2a | Renta neta media por hogar y por persona, media y mediana por unidad de consumo, % bajo el 60 % de la mediana y % de renta salarial (§7.2, §12.3) | VERIFICADO, con dos precisiones | Series de la tabla de Madrid, por ejemplo `DATOS_SERIE/ADRH7226121` en la API del INE: «Renta neta media por hogar», en euros, 2024 = 68.193 €. [Metodología del ADRH](https://www.ine.es/metodologia/metodologia_adrh.pdf), oct-2026, leída en bruto: unidad de consumo con la escala OCDE modificada (1, 0,5 y 0,3); el umbral del 60 % «pasa a calcularse a nivel nacional» desde el ADRH 2023; el porcentaje de salarios es sobre la renta bruta | «… % por debajo del 60 % de la mediana **nacional** por unidad de consumo; % de salarios sobre la renta **bruta**» | F1-13 ([#81](https://github.com/Kuantoapp/kuantoapp.github.io/issues/81)): `renta_hogar` y `renta_uc` del contrato son correctas como están |
| 2b | Gini y P80/P20 se calculan sobre la renta por unidad de consumo de las personas (§7.2) | VERIFICADO, con un matiz | Metodología, leída en bruto. El P80/P20 es «el percentil 80 y el percentil 20 de la distribución de renta por unidad de consumo». Para el Gini, «el 1,5% de los valores más bajos y el 1,5% de los valores más altos se sustituyen» por el valor más próximo | Añadir: «el Gini del INE se calcula con las colas recortadas (1,5 % por lado)» | F3-06 ([#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100)): el σ que da el Gini sale menor que el del P80/P20 por construcción, así que `dif_sigma` no puede leerse por sí sola como un fallo de la log-normal. Hay que tener en cuenta el recorte o compararlo con un σ simulado con el mismo recorte |
| 2c | ADRH 2024 publicado el 19-10-2026 (§7.2) | VERIFICADO | [Nota de prensa ADRH 2024](https://www.ine.es/dyngs/Prensa/ADRH2024.htm): «19 de octubre de 2026». Último año en las series: 2024. Las tablas dicen `Ultima_Modificacion` 15-10-2026, anterior a la publicación | Sin cambios | Ninguna |
| 2d | Por municipio, distrito y sección censal (§7.2, §12.3) | VERIFICADO, con un límite | Serie `ADRH9347787`: «Madrid sección 06023. Dato base. Índice de Gini.», 2024 = 35,9. Metodología: Gini, P80/P20 y fuentes de ingresos «se publican únicamente en» unidades con «al menos 100 residentes» | «… por municipio, distrito y sección; Gini, P80/P20 y fuentes de ingresos, solo en unidades de 100 residentes o más» | F1-13 ([#81](https://github.com/Kuantoapp/kuantoapp.github.io/issues/81)) admite nulos en `gini` y `p80p20`. F3-06 ([#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100)) necesita una regla para las secciones sin Gini |

## 3. Sobrecarga de los inquilinos en la Comunidad de Madrid (control de F3-06)

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 3a | Hay una tasa de sobrecarga para la Comunidad de Madrid (§7.2) | VERIFICADO, para el total de la población | Eurostat `ilc_lvho07_r` («Housing cost overburden rate by NUTS 2 region», actualizado el 20-10-2026), [API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07_r?geo=ES30&geo=ES&lastTimePeriod=3), leída en bruto. ES30: 9,1 % (2023), 11,2 % (2024) y 9,9 % (2025). España: 7,2 % (2025). Sin marcas de estado | «Comunidad de Madrid, 2025: 9,9 % de la población en sobrecarga (Eurostat `ilc_lvho07_r`)» | — |
| 3b | Esa tasa existe para los **inquilinos** de la Comunidad (§7.2, §16) | NO VERIFICADO: no está publicada | Eurostat `ilc_lvho07c` (por régimen de tenencia, [API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07c?geo=ES30&lastTimePeriod=1)) no tiene ningún valor para ES30. Solo da España en 2025: alquiler a precio de mercado 26,8 %, alquiler reducido 8,4 %, total 7,2 %. En las tablas de la ECV del INE (`TABLAS_OPERACION/ECV`) no hay ningún cruce de comunidad autónoma con régimen de tenencia para la sobrecarga | «No hay tasa publicada de sobrecarga de los inquilinos por comunidad. Referencias: Madrid, total de la población (9,9 %), y España, inquilinos a precio de mercado (26,8 %), 2025» | **F3-06 ([#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100)) se queda sin la cifra de control que prevé.** Según el plan (§1), sin cifra de control no se publica y el Bono usa el esfuerzo. La alternativa (comparar la sobrecarga estimada de todos los hogares con el 9,9 % de ES30) la decide el equipo en S3. F3-04 ([#98](https://github.com/Kuantoapp/kuantoapp.github.io/issues/98)) registra `ilc_lvho07_r` en lugar de una tasa de inquilinos |
| 3c | Esa tasa tiene un margen de error publicado (§7.2) | NO VERIFICADO: no está publicado | Los [metadatos de EU-SILC](https://ec.europa.eu/eurostat/cache/metadata/en/ilc_sieusilc.htm) (19-12-2025) remiten los errores de muestreo a los informes de calidad, que solo los dan para los indicadores principales. El INE solo publica coeficientes de variación para el AROPE | Quitar «dentro de su margen de error». Si se usa 3a, poner una tolerancia fijada de antemano, declarada como supuesto | F3-06 ([#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100)): el criterio «fuera del margen» del plan (§1) tiene que fijarse como una tolerancia propia antes de mirar el resultado |

## 4. Régimen de tenencia

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 4a | Censo de edificios y viviendas de la Comunidad, serie `19155xx`, régimen de tenencia por municipio, «dato regional» (§7.2, §12.1) | FALSO: el identificador y el origen | No hay ningún dataset `19155xx` con tenencia. `package_search?q=tenencia` devuelve 25 resultados; el bueno es `censo_2021_viviendas_familiares_por_tenencia`, con fuente «Censo de Población y Vivienda. INE.» (actualizado el 14-06-2024). Leído en bruto: viviendas principales con régimen Propiedad, Alquiler u Otro, para la Comunidad, 178 municipios y 10 zonas estadísticas. No llega a distrito. Madrid capital: 317.766 en alquiler; Comunidad: 525.834 | «`censo_2021_viviendas_familiares_por_tenencia` (catálogo regional; fuente: Censo 2021 del INE): viviendas principales por régimen, por municipio, 2021» | F3-04 ([#98](https://github.com/Kuantoapp/kuantoapp.github.io/issues/98)) usa este identificador. No se puede presentar como fuente regional independiente: es el INE |
| 4b | El Censo 2021 del INE da la tenencia (nivel por verificar) (§7.2, §12.3) | VERIFICADO, por sección censal | [Indicadores por sección del Censo 2021](https://www.ine.es/censos2021/C2021_Indicadores.csv) (30-06-2023, el INE avisa de que son provisionales), cabecera leída en bruto: `ccaa,cpro,cmun,dist,secc,…,t20_1,t20_2,t20_3`. El [diccionario](https://www.ine.es/censos2021/indicadores_seccen_c2021.xlsx), leído en bruto, dice que `t20_2` = «Viviendas en alquiler» (`t20_1` propiedad, `t20_3` otro). Son recuentos, que suman `t19_1` (viviendas principales) | «Censo 2021 (INE): viviendas principales en alquiler por sección censal (`t20_2`, provisional)» | F3-04 ([#98](https://github.com/Kuantoapp/kuantoapp.github.io/issues/98)) y F3-06 ([#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100)): la proporción de inquilinos puede ir por sección, el mismo grano que la sobrecarga, en vez de por municipio. Hay que pasar las secciones de 2021 a las del ADRH 2024 (skill `dm-tablas-de-paso`) |

## 5. IPC de alquiler regional

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 5a | El identificador es `1927681` o `1934665` (§6.2, §12.1) | VERIFICADO: `1934665` | `package_show`: `1934665` es el «Índice de Precios de Consumo. Vivienda en alquiler (Base 2025)»; `1927681` es la misma serie en base 2021, ya sustituida. Medias anuales de 2002 a 2025. Fuente: INE | «`1934665` (IPC de vivienda en alquiler, base 2025, medias anuales hasta 2025)» | — |
| 5b | El dataset regional da el IPC de alquiler **de la Comunidad de Madrid** | FALSO en los metadatos | Los metadatos dicen «Ámbito: Toda España». Cada año trae dos filas sin territorio (`Otros;;;`). Comparado en bruto con la serie INE `IPC297196` («Madrid, Comunidad de. Alquiler de vivienda. Índice.»), cuyas medias anuales son 94,466 (2023) y 97,062 (2024): una fila es la Comunidad y la otra el Nacional (95,548 y 97,643, iguales a las medias Nacionales de la misma tabla), **en orden variable**: Madrid va 1.ª en 2008, 2009, 2013, 2014 y 2016 a 2018, y 2.ª en el resto; en 2025, año base, las dos valen 100 ([#258](https://github.com/Kuantoapp/kuantoapp.github.io/issues/258)) | «Para el factor: serie INE `IPC297196` (tabla 76137, base 2025, Comunidad de Madrid, mensual; oct-2026 = 103,746; variación anual 3,0 %). `1934665` solo sirve identificando cada año la fila que coincide con `IPC297196`» | F2-10 ([#94](https://github.com/Kuantoapp/kuantoapp.github.io/issues/94)): con una fila fija se aplicaría en algunos años el IPC nacional. Lo más seguro es `IPC297196`, que además llega a octubre de 2026 |

## 6. EPF: alimentación y suministros por tipo de hogar en Madrid

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 6a | La EPF da el gasto en alimentación y suministros por tipo de hogar para la Comunidad de Madrid (§12.3) | FALSO: no cruza las tres cosas | Dimensiones leídas en bruto (`GRUPOS_TABLA` del INE): la 73807 cruza tipo de hogar y grupos de gasto, solo para España; la 74000 cruza comunidad y tipo de hogar reducido, con el gasto total; la 73992 cruza comunidad y subgrupo de gasto, sin tipo de hogar. Madrid en 2025 (73992): electricidad, gas y otros combustibles, 806,38 € por unidad de consumo (1.404,59 € por hogar); productos alimenticios, 3.115,68 € por unidad de consumo. No hay un tipo «comparte piso» | «EPF 2025: Madrid por subgrupo y por unidad de consumo; por tipo de hogar, solo España (t=73807)» | F1-14 ([#82](https://github.com/Kuantoapp/kuantoapp.github.io/issues/82)): cesta = gasto de Madrid por unidad de consumo × unidades de consumo OCDE del perfil, marcada como **estimado**. «Comparte» se trata como supuesto |
| 6c | La EPF de Madrid está en el catálogo regional (añadida el 14-11, tras el PR #122) | VERIFICADO | `gasto_por_subgrupo_gasto_3_digitos_coicop_epf_base_2006` (fuente: EPF del INE; CC BY; actualizado el 26-06-2026), CSV leído en bruto: 2016-2025, gasto por hogar, por persona y por unidad de consumo. Sus filas no llevan territorio y los metadatos dicen «Toda España», pero los valores de 2025 son los de Madrid en el INE t=73992: 806,38 € (electricidad, gas y otros combustibles), 3.115,68 € (productos alimenticios) y 188,78 € (bebidas no alcohólicas) por unidad de consumo. `1914699` da además el gasto total por tamaño del hogar (1, 2, 3, 4 o más miembros), hasta 2023 | «EPF 2025 de Madrid por subgrupo y por unidad de consumo: catálogo regional `gasto_por_subgrupo_gasto_3_digitos_coicop_epf_base_2006` (= INE t=73992)» | F1-02 ([#70](https://github.com/Kuantoapp/kuantoapp.github.io/issues/70)) y F1-14 ([#82](https://github.com/Kuantoapp/kuantoapp.github.io/issues/82)) descargan la EPF del catálogo, no del INE |
| 6b | Último año de la EPF | VERIFICADO: 2025 | Serie `EPF526597` (España, alimentos y bebidas no alcohólicas por hogar): 2025 = 5.626,32 €. Tablas modificadas el 25-06-2026 | «EPF 2025» | `anio` = 2025 en `hogares` |

## 7. Renta del catálogo regional `1916304`

| # | Afirmación (ficha) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 7 | `1916304` da la renta neta media con un nivel territorial por confirmar (§12.1) | FALSO como renta por zona | `package_show`: «Renta anual neta media por hogar, persona y unidad de consumo (Base 2013)», fuente: Encuesta de Condiciones de Vida (INE). El CSV, leído en bruto, va de 2009 a 2025 sin territorio. En 2025 da 18.169 € por persona y 27.136 € por unidad de consumo, igual que la fila «Madrid, Comunidad de» de la tabla INE 9947: es **solo la Comunidad entera** | «`1916304`: renta neta media de la ECV, total de la Comunidad de Madrid, 2009-2025 (renta del año anterior a la entrevista)» | F1-13 ([#81](https://github.com/Kuantoapp/kuantoapp.github.io/issues/81)) sigue con el ADRH. `1916304` solo sirve como contraste regional |
| 7b | El catálogo regional publica renta del ADRH por municipio (añadida el 14-11) | VERIFICADO, solo renta bruta per cápita | `irpf_indicador_renta`, «Indicador de Renta Disponible Bruta Municipal. Municipios» (fuente: ADRH del INE; CC BY; actualizado el 20-10-2026), CSV leído en bruto: 2015-2024, Comunidad, municipios y zonas estadísticas; medidas «Total», «Per cápita» y «Porcentaje sobre la media». 2024: Comunidad 24.786 € per cápita, Getafe 20.614 € (83,2 %). No tiene renta neta por hogar ni por unidad de consumo, ni Gini, ni secciones | «`irpf_indicador_renta`: renta disponible bruta per cápita por municipio, 2015-2024 (ADRH)» | F1-13 ([#81](https://github.com/Kuantoapp/kuantoapp.github.io/issues/81)): sirve como control municipal y como cita del catálogo, no como entrada del cálculo |

## 8. Población de 18 a 35 años por municipio

| # | Afirmación (plan) | Estado | Evidencia | Texto corregido | Consecuencia para el plan |
|---|---|---|---|---|---|
| 8a | Hay población por edad y municipio en el catálogo regional | VERIFICADO, en grupos de 5 años | `poblacion_censada_por_edad_nacionalidad_y_sexo` (fuente: Censo anual del INE; CC BY; actualizado el 20-01-2026). `datastore_search` leído en bruto: año 2025 con todos los grupos (por ejemplo, Getafe, 20-24 años: 10.534) | «18–35 ≈ 0,4·(15-19) + (20-34) + 0,2·(35-39), estimado» | F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)): la versión regional obliga a repartir los grupos de los extremos |
| 8b | Hay una alternativa del INE con edad año a año | VERIFICADO: tabla 68542 | Censo anual de población, tabla 68542 «Población por sexo y edad (año a año)», por municipios. Leída en bruto: «Getafe. Dato base. Total. 18 años.», 1-1-2025 = 2.130. Edades de 18 (id 15337) a 35 (id 15354). La tabla 68534, que propuso el verificador, solo tiene municipios de Baleares y Canarias. El Padrón continuo dejó de publicarse con los datos de 2022 | «18–35 = suma exacta de las edades 18 a 35 (INE, t=68542, 1-1-2025)» | F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)): `poblacion_joven` exacta con 68542. Si se prefiere la regional por el criterio del catálogo, se usa 8a marcada como estimada |
| 8c | El catálogo y el INE dan la misma población (añadida el 14-11) | VERIFICADO en Getafe | Getafe, 1-1-2025, total por sexo: los cinco grupos de 15 a 39 años del catálogo (10.569, 10.534, 10.277, 11.091 y 13.051; 55.522 en total) son iguales a la suma de las edades simples del INE t=68542. De 18 a 35 años, el INE da exactamente 38.462; el reparto de 8a da 38.740 (+0,72 %) | «Catálogo e INE son el mismo Censo anual; el reparto de los grupos de los extremos desvía menos del 1 % en Getafe» | F2-05 ([#89](https://github.com/Kuantoapp/kuantoapp.github.io/issues/89)): cualquiera de las dos sirve; el control es que los grupos del catálogo cuadren con el INE |

## Fuente elegida por dato

Aplica la regla de `docs/decisiones.md` del 14-11: si el catálogo regional (datos.comunidad.madrid) tiene el dato, se usa el del catálogo. La fuente original solo se usa si el catálogo no lo tiene, o si la original es más reciente o más detallada. En ese caso se dice qué tenía el catálogo, por qué se toma otra fuente y para qué se usa el dato del catálogo. Lo revisó `dm-abogado-del-diablo` el 14-11-2026, con veredicto APTO CON RESERVAS, ya incorporadas. Todos los controles son comprobaciones que puede repetir un test.

| Dato · issue | Qué tiene el catálogo regional | Fuente de cálculo y por qué | Para qué se usa el del catálogo | Publicador original · último periodo · actualización | Control comprobable |
|---|---|---|---|---|---|
| Bono Alquiler Joven · F2-05 | `spacm_bono_alquiler_joven_2022` | **Catálogo** (es la única fuente). Se excluye la fila «Otro» (3.352 solicitudes sin contrato) | Cálculo y cita | Comunidad de Madrid · convocatoria de 2022 (plazo del 21-09-2022 al 14-11-2023) · ficha del 2026-02-03 | Totales 51.735 / 11.477 / 40.258 (fila 1a) |
| IPC de alquiler · F2-10 | `1934665` (base 2025; sustituye a `1927681`) | **INE `IPC297196`**, porque es más reciente (mensual, hasta oct-2026; el catálogo da medias anuales hasta 2025) y está etiquetado («Madrid, Comunidad de»). El catálogo no dice qué fila es Madrid y sus metadatos dicen «Toda España» (fila 5b): con una fila fija se aplicaría en algunos años el IPC nacional | Cita, y control: en cada año, una de sus dos filas tiene que coincidir (±0,0015) con la media anual de los 12 meses de `IPC297196` | INE · oct-2026 · tabla modificada el 13-11-2026 | 2023: 94,466; 2024: 97,062 (comprobado). El test compara todos los años disponibles |
| Cesta básica (EPF) · F1-14 | `gasto_por_subgrupo_gasto_3_digitos_coicop_epf_base_2006` (Madrid, sin etiqueta de territorio) | **Catálogo**: gasto de Madrid por unidad de consumo × unidades de consumo OCDE del perfil, marcado **estimado** (no hay cruce de Madrid con tipo de hogar). Es un gasto medio, no un mínimo, en euros de 2025 | Cálculo y cita | INE (EPF) · 2025 · catálogo del 26-06-2026 | Igual al INE t=73992: 806,38 / 3.115,68 / 188,78 €/UC (fila 6c) |
| Tenencia por municipio · F2-05, F3-07 | `censo_2021_viviendas_familiares_por_tenencia` | **Catálogo** | Cálculo y cita | INE (Censo 2021) · 2021 · catálogo del 14-06-2024. No hay dato más reciente: el siguiente censo es el de 2031 | Madrid capital 317.766 y Comunidad 525.834 en alquiler (fila 4a) |
| Tenencia por sección · F3-06 | Lo mismo, pero sin bajar de municipio | **INE `C2021_Indicadores.csv` (`t20_2`)**, porque es más detallado: F3-06 calcula por sección. Son datos provisionales y van con una tabla de paso de las secciones de 2021 a las del ADRH 2024 | Control: la suma de las secciones de cada municipio tiene que coincidir con el catálogo, dentro de una tolerancia fijada antes de mirar | INE · 2021 (provisional) · 30-06-2023 | Diccionario `t20_2` = viviendas en alquiler (fila 4b) |
| Inquilinos por debajo del precio de mercado · F3-06 | `1912645` (ECV, hogares por régimen de tenencia) | **Catálogo**: 2025, 22,6 % alquiler a precio de mercado y 4,3 % por debajo, así que el 16 % de los inquilinos no paga precio de mercado. F3-06 lo usa para no aplicar el SERPAVI a todos los inquilinos | Cálculo y cita | INE (ECV) · 2025 · catálogo del 06-02-2026. Las filas no llevan territorio, pero son Madrid | Igual al INE t=9997, «Madrid, Comunidad de», 2025: propiedad 69,1 %; alquiler a precio de mercado 22,6 %; por debajo 4,3 %; cesión 4,0 % (leído en bruto el 14-11) |
| Renta · F1-13 | `irpf_indicador_renta` (renta disponible **bruta** per cápita por municipio, 2015–2024, ADRH) y `1916304` (ECV, solo la Comunidad) | **INE ADRH 2024**, porque es más detallado: sección, distrito, renta neta por hogar y por unidad de consumo, Gini y P80/P20. El catálogo no tiene nada de eso | Cita; control municipal (igualdad si `irpf_indicador_renta` coincide con alguna columna del ADRH, si no, el orden de los municipios); prueba de robustez del Bono; `1916304` como contraste regional | INE · 2024 · publicado el 19-10-2026 (catálogo, 20-10-2026) | Comunidad 24.786 € y Getafe 20.614 € per cápita en 2024 (fila 7b) |
| Población de 18 a 35 años · F2-05 | `poblacion_censada_por_edad_nacionalidad_y_sexo` (grupos de cinco años, 2021–2025) | **INE t=68542**, porque es más detallado (edad año a año): da la suma exacta de 18 a 35 sin repartir los grupos de los extremos, que es donde el reparto falla en los municipios jóvenes. Fecha **1-1-2023**, la más cercana a la mitad del plazo del Bono (21-09-2022 a 14-11-2023), para no dividir solicitudes de 2022 entre jóvenes de 2025 | Cita, y control exacto: la suma de 20 a 34 años del INE tiene que ser igual a 20-24 + 25-29 + 30-34 del catálogo | INE (Censo anual) · 1-1-2025 (hay 2021–2025) · catálogo del 20-01-2026 | Getafe: grupos idénticos; 18–35 = 38.462 (fila 8c) |
| Sobrecarga, control de F3-06 | Nada (y el Instituto de Estadística de la Comunidad tampoco la publica: «Pendiente») | **Microdatos de la ECV 2025 del INE**, cálculo propio y **estimado**: es la única vía que trae a la vez la región y la tenencia. Detalle en «Pendiente» | — | INE (ECV, fichero de uso público) · 2025 (renta de 2024) · fichero del 10-06-2026 | El mismo cálculo reproduce a Eurostat (`ilc_lvho07c`, `ilc_lvho07_r`): España, las cinco tenencias de 2025 (26,8 / 8,4 / 3,4 / 1,9 / 7,2 %) y ES30, total, 9,9 %, a ±0,05 puntos (personas). Lo comprueba `tests/test_sobrecarga_ecv.py` sobre `mesobra.sobrecarga_ecv` ([#260](https://github.com/Kuantoapp/kuantoapp.github.io/issues/260)) |

## Pendiente

- **Decisión para S3, control de F3-06:** no hay tasa publicada de sobrecarga de los inquilinos para Madrid. Comparar con el 9,9 % de ES30 no valida nada: es de personas, incluye a los propietarios y obliga a suponer su sobrecarga, así que el control sería circular. [#129](https://github.com/Kuantoapp/kuantoapp.github.io/issues/129) miró las dos vías que quedaban el **2026-11-16** (dos `dm-verificador-fuentes` y relectura en bruto). **Resultado: hay cifra de control, calculada con los microdatos del INE.** La decisión de usarla es de S3 y va a `docs/decisiones.md`.
  - **Vía 1, Instituto de Estadística de la Comunidad: NO VERIFICADO, no se publica.** Su ECV explota la muestra del INE sin ampliarla: la [nota metodológica](https://web.comunidad.madrid/iestadis/fijas/estructu/sociales/descarga/Metedologia_Encuesta_Condiciones_de_Vida.pdf) dice «consiste en una explotación de los microdatos en el ámbito territorial de la Comunidad de Madrid». Las tablas de hogares ([`175_000004`](https://iestadis.edatos.io/statistical-resources/v1.0/datasets/IECM/175_000004/~latest.json?fields=-data)) y de personas (`175_000013`) se desglosan por régimen de tenencia, «Alquiler o realquiler» incluido, de 2013 a 2025. Leídas en bruto, tienen 71 y 39 medidas: renta, pobreza, carencias y retrasos en el pago. Ninguna es de carga ni de sobrecarga del gasto en vivienda, y ninguna da errores de muestreo.
  - **Vía 2, microdatos de la ECV del INE: VERIFICADO, sirve.** El fichero de uso público de 2025 ([`datos_2025.zip`](https://www.ine.es/ftp/microdatos/ecv/ecv_b2013/datos_2025.zip), del 10-06-2026; también hay de 2023 y 2024) se descarga sin registro. Sus [condiciones](https://ine.es/dyngs/SER/index.htm?cid=1388) piden citar al INE como fuente del dato primario. Según su diseño de registro, trae la región (`DB040`, «ES30» = Comunidad de Madrid), la tenencia (`HH021`: 3 = alquiler a precio de mercado; 4 = a precio inferior), el alquiler (`HH060`), los gastos de la vivienda (`HH070`: alquiler, comunidad, agua, electricidad, gas…), la renta disponible del año anterior (`HY020`), las ayudas a la vivienda (`HY070N`) y los factores de elevación (`DB090` del hogar y `RB050` de la persona). **No trae el estrato (`DB050`) ni la sección (`DB060`).** Muestra de 2025: 2.861 hogares de ES30, de los que **580 son inquilinos** (`HH021` 3 o 4); 562 tienen gasto (18 con `HH070` en blanco).
  - **El cálculo reproduce a Eurostat.** La sobrecarga se calcula con la fórmula de Eurostat, `(HH070·12 − HY070N) / (HY020 − HY070N) > 0,40`, contando como sobrecargados los hogares con denominador ≤ 0, y se pondera por personas. En 2025, con el código del repo (`mesobra.sobrecarga_ecv`, [#260](https://github.com/Kuantoapp/kuantoapp.github.io/issues/260)), da para España: alquiler a precio de mercado 26,8 % (Eurostat: 26,8 %); alquiler reducido o cesión gratuita 8,4 % (8,4 %); propiedad con hipoteca 3,4 % (3,4 %); sin hipoteca 1,9 % (1,9 %); total 7,2 % (7,2 %). Para ES30 da 9,9 % en 2025 (9,9 %). El cálculo de #190, fuera del repo, daba 26,4 % y 9,8 %, y además 9,1 % en 2023 (9,1 %) y 11,2 % en 2024 (11,2 %). Dos cosas salen del cuadre y no del diseño de registro: `HH070` es mensual, y la categoría «reducido» de Eurostat incluye la cesión gratuita. Con el mismo código (`hogares(carpeta, anio)`, [#274](https://github.com/Kuantoapp/kuantoapp.github.io/issues/274)), ES30 da 9,06 % en 2023 (Eurostat: 9,1 %) y 11,16 % en 2024 (11,2 %), dentro de ±0,05 puntos: la regla es la misma en los tres años, y lo vigila `tests/test_sobrecarga_ecv.py`.
  - **Cifra de control, con la definición de F3-06 (estimado).** Porcentaje de hogares inquilinos de la Comunidad de Madrid (`HH021` 3 o 4, ponderados con `DB090`):

    | ECV (renta del año anterior) | Hogares en la muestra | Gasto de vivienda > 40 % de la renta | Error estándar | Alquiler > 30 % de la renta | Error estándar |
    |---|---|---|---|---|---|
    | **2025** | 580 (562 con gasto) | **36,0 %** | 2,7 | **41,4 %** | 2,7 |
    | 2024 | 631 (614 con gasto) | 37,6 % | 2,5 | 44,0 % | 2,6 |
    | 2023 | 536 (526 con gasto) | 31,0 % | 2,4 | 35,5 % | 2,5 |
    | 2023 a 2025 juntas | 1.747 (1.702 con gasto) | 35,0 % | 1,5 | 40,5 % | 1,5 |

    Las cuatro filas salen de `mesobra.sobrecarga_ecv.control_f306` ([#260](https://github.com/Kuantoapp/kuantoapp.github.io/issues/260), [#274](https://github.com/Kuantoapp/kuantoapp.github.io/issues/274)), (la fila de las tres juntas, con `pd.concat` de los tres años antes de llamarla; lo comprueba `test_control_tres_anios_juntos`), con la misma regla en todos los años: los hogares con renta ≤ 0 cuentan como sobrecargados. Las cifras anteriores de #190 (calculadas fuera del repo, sin esa regla) eran 2024: 37,1 % y 43,5 %; 2023: 30,7 % y 35,2 %; juntas: 34,6 % y 40,0 %; y 2025: 35,9 %. Dejando fuera los hogares con renta ≤ 0 se recuperan las del gasto (30,7 %, 37,1 % y 35,9 %), así que la diferencia es solo esa regla. Hay 3 hogares con renta ≤ 0 en 2023, 4 en 2024 y 1 en 2025 (un autónomo con pérdidas en 2024, `HY020` = −2.501 €). Las filas de 2023 y 2024 no cambian el control de F3-06, que sigue siendo 2025. Las tres juntas no son hogares independientes (panel rotatorio, ver «Margen de error»), por eso no se usan como control.

    **Estabilidad entre años.** Con la regla de Eurostat el gasto sobre el 40 % de la renta es 31,0 % (2023), 37,6 % (2024) y 36,0 % (2025). El salto de 2023 a 2024 es de 6,5 puntos y el error estándar de la diferencia, si fueran muestras independientes, es √(2,4² + 2,5²) = 3,5: unos 1,9 errores estándar, sin el efecto de diseño (el panel rotatorio los correlaciona un poco). 2024 y 2025 distan 1,6 puntos. La cifra de 2025 es del nivel de la de 2024 y por encima de la de 2023, y el intervalo de tolerancia de S3 (28,6 % a 43,4 %) incluye las tres.

    **Los 18 hogares sin gasto (2025, estimado).** `HH070` falta en 18 de los 580 inquilinos de ES30 (un 2,4 % del peso), y `HH060` falta en esos mismos 18; la renta (`HY020`) la tienen todos. No son iguales a los otros 562: solo el 49,6 % paga alquiler a precio de mercado (`HH021` = 3) frente al 84,8 %, y los de precio inferior sobrecargan menos (27,9 % frente a 37,5 %). Su renta es parecida: media de 39.550 € (36.552 € los otros) y mediana de 29.940 € (31.494 €). El tamaño del hogar es el mismo (1,77 y 1,78 unidades de consumo). Acotando la tasa con los 18 todos sin sobrecarga o todos sobrecargados, el gasto sobre el 40 % queda entre **35,1 % y 37,5 %** (36,0 % con los 562). Como son pocos y el 36,0 % queda dentro de la cota, la cifra de control no cambia; si se asignara a esos hogares la tasa de los de precio inferior (27,9 %) la cifra bajaría a unos 35,8 %.

    Solo a precio de mercado, en 2025: 37,5 % (459 hogares con gasto de 468); a precio inferior: 27,9 % (103 de 112). Descontar las ayudas a la vivienda apenas cambia la tasa (35,5 % en 2025). Se toma 2025 porque su renta es la de 2024, el mismo año que el ADRH 2024 de F3-06.
  - **Margen de error (supuesto).** Sin estrato ni sección en el fichero, el error estándar se calcula por linealización tomando el hogar como unidad, y sale igual que el binomial con el tamaño efectivo de Kish. No recoge el efecto de conglomerado, así que se multiplica por √2 (efecto de diseño 2). Con 580 inquilinos en 408 secciones (metodología de la ECV, cuadro II), hay 1,4 por sección y el efecto es 1 + 1,4ρ: el factor 2 equivale a ρ ≈ 0,7, muy por encima de lo habitual. Agrupar 2023 a 2025 no da hogares independientes, porque la ECV es un panel rotatorio y `DB030` no identifica al hogar entre años; por eso no se usa como control.
  - **Tolerancia propuesta para S3, fijada antes de que F3-06 tenga resultado:** 36,0 ± 1,96 × 2,66 × √2 (y 41,4 ± 1,96 × 2,73 × √2 para el alquiler). **F3-06 pasa si el rango de su sobrecarga agregada a la Comunidad (alquiler y suministros por encima del 40 %, σ del Gini a σ del P80/P20) toca el intervalo [28,6 %; 43,4 %]**, y el del alquiler por encima del 30 % toca [33,9 %; 49,0 %]. Antes de #260 eran [28,5; 43,3] y [33,8; 48,9]; se movieron 0,1 puntos por la regla de la renta ≤ 0, no por ningún resultado de F3-06. Con ±7,4 puntos, el intervalo solo detecta errores gruesos. Si no lo toca, se aplica la señal de corte de [#100](https://github.com/Kuantoapp/kuantoapp.github.io/issues/100): no se publica y el Bono usa el esfuerzo.
  - **Lo que la tolerancia no cubre**, y que hay que decir junto al resultado: la renta es la de la ECV (`HY020`), que el INE construye combinando lo que dice el hogar con registros administrativos de la AEAT, la Seguridad Social y las haciendas forales de Navarra, Bizkaia y Gipuzkoa (metodología mixta desde la ECV de 2013), y no la renta del ADRH (verificado el 2026-11-23, [ficha metodológica de la ECV](https://ine.es/dynt3/metadatos/es/RespuestaDatos.htm?oe=30453), apartados 13.1, 15.1 y 18.3: «metodología mixta combinando la información proporcionada por el informante con los registros administrativos de la Agencia Estatal de Administración Tributaria, la Seguridad Social…»; en Álava no se usaron los ficheros tributarios (apartado 15.1), que no afecta a Madrid); el gasto es el que declara el hogar (`HH070`, que incluye la comunidad), no el SERPAVI P25–P75 más la cesta de la EPF; el gasto es de 2025 y el SERPAVI, de 2024; y quedan fuera 18 de los 580 hogares, por no tener gasto declarado (con ellos, la tasa quedaría entre 35,1 % y 37,5 %, dentro de la tolerancia). Esas diferencias están medidas en la viñeta siguiente.
  - **Entradas de F3-06 frente a la ECV ([#193](https://github.com/Kuantoapp/kuantoapp.github.io/issues/193), 2026-11-18, estimado).** Medidas antes de que F3-06 tenga resultado, para saber hacia dónde se desviará. ECV 2025, inquilinos de ES30 (`HH021` 3 o 4, ponderados con `DB090`); para el alquiler, solo los de mercado (`HH021` = 3, 459 hogares con dato), porque F3-06 aplica el SERPAVI solo a ellos. Diferencia = (F3-06 − ECV) / ECV. El efecto es el cambio de la cifra de control (36,0 %) si se multiplica esa entrada de cada hogar de la ECV por el cociente F3-06/ECV.

    | Entrada | ECV 2025 | Lo que usa F3-06 | Diferencia | Efecto en la sobrecarga |
    |---|---|---|---|---|
    | Renta por hogar, media | 36.624 € (`HY020`) | 36.416 € (ADRH: 51.976 € × 0,701) | −0,6 % | ruido (ver abajo) |
    | Renta por hogar, mediana | 31.379 € | 36.416 € (la misma media) | +16,1 % | no aplica (ver abajo) |
    | Renta por unidad de consumo, media de las personas | 19.781 € (`HY020/HX240`) | 20.425 € (ADRH: 29.153 € × 0,701) | +3,3 % | −0,8 puntos |
    | Alquiler de mercado, P25 | 600 €/mes (`HH060`) | 679 €/mes | +13,1 % | +6,5 puntos |
    | Alquiler de mercado, mediana | 775 €/mes | 789 €/mes | +1,8 % | +2,1 puntos |
    | Alquiler de mercado, P75 | 1.029 €/mes | 992 €/mes | −3,7 % | −0,7 puntos |
    | Alquiler de mercado, media | 862 €/mes | 879 €/mes | +2,0 % | — |
    | Suministros, mediana por hogar | 151 €/mes (`HH070 − HH060`) | 122 €/mes (cesta: 81,08 €/UC·mes × `HX240`) | −19,5 % | −1,2 puntos |

    Fuentes. ECV: microdatos de la ECV 2025 del INE (`ine_ecv_microdatos_2025_2026-11-18.zip`, `mesobra.sobrecarga_ecv.hogares`). Renta de F3-06: ADRH 2024 del INE (`mesobra.renta.renta`). Alquiler: SERPAVI 2024 del MIVAU, cuantía mensual (`mesobra.alquiler.alquiler_seccion`), con los inquilinos del Censo 2021 del INE por sección (`t20_2`, `ine_c2021_indicadores_seccion_2026-11-18.csv`). Suministros: cesta de la EPF 2025 (`mesobra.hogares.cesta_uc`: electricidad, gas, otros combustibles y agua).

    F3-06 todavía no existe, así que su lado de la tabla se construye con estos supuestos:
    - **Renta.** El ADRH no trae la Comunidad: es la media de los 179 municipios ponderada por hogares (población ÷ tamaño medio del hogar) y, por unidad de consumo, por población. Se ajusta a los inquilinos con `r / (p·r + 1 − p)` = 0,701, donde `r` = 0,650 es el cociente de renta por unidad de consumo entre inquilinos y propietarios de la ECV (19.781,17 € frente a 30.432,15 €) y `p` = 0,2065 es la parte de viviendas principales en alquiler del Censo 2021 (`t20_2 / t19_1`).
    - **Alquiler.** En cada sección, F3-06 integra el alquiler entre el P25 y el P75 del SERPAVI. Aquí se toma uniforme en ese tramo y se mezclan las secciones con el peso de sus inquilinos del Censo 2021, del mismo seccionado (4.416 secciones; el 2,0 % de los inquilinos cae en secciones sin dato y queda fuera). Los cuantiles de la tabla son los de esa mezcla. Promediar los percentiles de las secciones da otra cosa: 716, 861 y 1.041 €/mes, es decir, +19,4 %, +11,1 % y +1,1 % frente a la ECV.
    - **Efecto.** Es un orden de magnitud: un factor único para todos los hogares no reproduce el cambio de forma de la distribución. Además, la tasa da saltos cerca del 40 %: cinco hogares tienen un gasto entre el 39,97 % y el 39,998 % de su renta y pesan cerca del 1 % del total. Con factores a menos del 1 % de la unidad, el efecto es ruido: la renta media (−0,6 %) mueve la tasa +1,6 puntos solo por ese escalón.

    Lectura:
    - **Renta: casa.** Por unidad de consumo, que es como trabaja F3-06, el ADRH ajustado queda un 3,3 % por encima de la ECV y bajaría la sobrecarga en torno a 1 punto. Por hogar casa al 0,6 %, pero por compensación: el ADRH de todos los hogares supera a la ECV un 9,7 % (51.976 € frente a 47.375 €; ADRH frente a ECV, de fuente, cobertura y método distintos, aunque la ECV también usa registros de la AEAT; la causa de la diferencia no está medida), y el ajuste a inquilinos, con la `p` del Censo 2021 (20,7 %) y un cociente de unidad de consumo aplicado al hogar, lo baja más de lo que dice la ECV.
    - **La mediana pasa del 15 % (+16,1 %), pero no es una diferencia de entradas.** Compara la media del ADRH con la mediana de la ECV; en la ECV, la media es 1,17 veces la mediana. Es un aviso para F3-06: la log-normal tiene que fijar la **media** con el ADRH. Si tomara esa media como renta típica, la sobrecarga bajaría unos 7,7 puntos (al 28,3 %), en el borde de la tolerancia.
    - **Alquiler: el centro casa y la parte barata no.** La mediana y la media de lo que integra F3-06 quedan a un 2 % de la ECV; el P25, un 13,1 % por encima, y el P75, un 3,7 % por debajo. Integrar solo entre el P25 y el P75 de cada sección deja fuera los alquileres baratos que sí declara la ECV. Dirección: **más sobrecarga**, de +2 puntos (mediana) a +6,5 puntos (si todo se moviera como el P25). No es por el año: con el IPC de alquiler de Madrid (media de 2025 ÷ media de 2024 = 1,030), el SERPAVI de 2024 se alejaría más. Causas posibles, sin cuantificar: el SERPAVI solo recoge vivienda colectiva y contratos declarados en el IRPF; la ECV, cualquier alquiler declarado en la entrevista.
    - **Suministros: pasa del 15 % (−19,5 %).** `HH070` incluye la comunidad y la cesta de F3-06 no. Si se le suman los gastos comunitarios de la EPF (04.4, 600,38 €/UC·año), la cesta pasa a 197 €/mes (+30,2 %); la ECV queda entre las dos. Dirección: **menos sobrecarga**, unos −1,2 puntos.
    - **Todo junto:** con la media de lo que integra F3-06 (+2,0 %), la renta y los suministros, la sobrecarga baja de 0,8 a 1,5 puntos (35,1 % con la renta por hogar; 34,5 % por unidad de consumo). Con los extremos del alquiler va de −1,9 puntos (factor del P75) a +6,9 (factor del P25). Todo queda dentro de [28,6 %; 43,4 %]: las entradas, por sí solas, no sacan a F3-06 de la tolerancia. El riesgo está en la cola barata del alquiler, que empuja hacia arriba, y en usar la media como mediana, que empuja hacia abajo.

    Segunda vía:
    - El script reproduce primero la cifra de control: `control_f306` da 36,0 %, y la tasa con todos los factores a 1, también.
    - El cociente `r` sale de los microdatos: la renta por unidad de consumo de inquilinos, propiedad con hipoteca, sin hipoteca y total coincide al céntimo con el IECM `175_000004` (19.781,17; 31.108,81; 29.941,95 y 27.136,20 €).
    - El ADRH agregado desde las 4.518 secciones da 51.142 € por hogar y 28.834 € por unidad de consumo (−1,6 % y −1,1 % frente a los municipios).
    - El SERPAVI agregado desde los municipios (pesos `t20_2` por municipio) da P25 664, mediana 814 y P75 1.048 €/mes. Dentro de un municipio el reparto es más ancho que dentro de una sección, así que su P25 es más bajo; queda entre la ECV y la media de los percentiles de sección.
    - El Censo 2021 suma 525.755 inquilinos en la provincia y 317.766 en Madrid, igual que en #98.
  - **Periodicidad de `HH060`: VERIFICADO, es mensual** (`dm-verificador-fuentes` y relectura en bruto del PDF, 2026-11-18). INE, [Cuestionario de Hogar de la ECV 2025](https://www.ine.es/metodologia/t25/ecv_hog25.pdf), p. 5, pregunta HC2, de la que salen `HH060` y `HH070`: «¿Cuál ha sido el importe del alquiler de esta vivienda en el último mes?», con la casilla «Importe mensual del alquiler». Segunda vía: la mediana de `HH060` de mercado (775 €) es del orden del SERPAVI mensual (789 €), no doce veces mayor. Así que el alquiler por encima del 30 % (`HH060·12`) está bien construido. Matiz: HC2 pide incluir las ayudas al alquiler aunque se paguen directamente al arrendador, y excluir, si se puede, la comunidad y el agua; `HH060` es el alquiler antes de ayudas.
  - **Script de #193** (desde la raíz del repo, con `PYTHONPATH=src` y los microdatos descomprimidos como dice `data/README.md`):
    <details><summary>entradas_f306.py</summary>

    ```python
    # ruff: noqa: T201, C408, RUF015 -- script de un solo uso fuera del repo (#193), su salida es el resultado
    """#193: entradas de F3-06 frente a la ECV 2025 de los inquilinos de Madrid (ES30). Estimado."""

    import numpy as np
    import pandas as pd

    from mesobra import alquiler, hogares, renta
    from mesobra import sobrecarga_ecv as ecv

    RAW = ecv.RAIZ / "data/raw"


    def wq(x, w, q):
        """Cuantil ponderado (interpolación sobre el peso acumulado en el punto medio)."""
        o = np.argsort(x.to_numpy())
        x, w = x.to_numpy()[o], w.to_numpy()[o]
        c = (np.cumsum(w) - w / 2) / w.sum()
        return np.interp(q, c, x)


    def pct(f3, e):
        return 100 * (f3 - e) / e


    h = ecv.hogares()
    print("control", ecv.control_f306(h).tasa.round(2).to_dict())
    m = h[h.DB040 == ecv.MADRID]
    inq = m[m.HH021.isin(ecv.INQUILINOS)]
    mer = inq[
        (inq.HH021 == 3) & inq.HH060.notna()
    ]  # HH060 y HH070 faltan juntos en 18 hogares

    # --- Censo 2021: inquilinos (t20_2) y viviendas principales (t19_1) por sección, provincia 28
    c = pd.read_csv(RAW / "ine_c2021_indicadores_seccion_2026-11-18.csv", dtype=str)
    c = c[c.cpro.astype(int) == 28]
    c["seccion_id"] = (
        c.cpro.str.zfill(2)
        + c.cmun.str.zfill(3)
        + c.dist.str.zfill(2)
        + c.secc.str.zfill(3)
    )
    for k in ("t19_1", "t20_2"):
        c[k] = pd.to_numeric(c[k])
    print(
        "censo t20_2 prov 28",
        c.t20_2.sum(),
        "Madrid",
        c[c.seccion_id.str[:5] == "28079"].t20_2.sum(),
    )
    ok = c.t20_2.notna() & c.t19_1.notna()
    p = c[ok].t20_2.sum() / c[ok].t19_1.sum()
    print(f"p (alquiler/principales, Censo 2021) {p:.4f}")

    # --- 1. Renta
    r_uc = lambda d: np.average(d.HY020 / d.HX240, weights=d.peso_personas)
    prop = m[m.HH021.isin((1, 2))]
    print(
        "IECM UC inq/hip/sin/total",
        round(r_uc(inq), 2),
        round(r_uc(m[m.HH021 == 2]), 2),
        round(r_uc(m[m.HH021 == 1]), 2),
        round(r_uc(m), 2),
    )
    r = r_uc(inq) / r_uc(prop)
    print(f"r (UC inquilinos/propietarios) {r:.4f}  propietarios UC {r_uc(prop):.2f}")
    aj = r / (p * r + 1 - p)

    t = renta.renta()
    t = t[t.anio == 2024]
    mun = t[(t.nivel == "zona") & (t.unidad_id.str.len() == 5)].dropna(
        subset=["renta_hogar", "tam_hogar"]
    )
    sec = t[t.nivel == "seccion"].dropna(subset=["renta_hogar", "tam_hogar", "poblacion"])
    for nom, d in (("municipios", mun), ("secciones", sec)):
        hog = d.poblacion / d.tam_hogar
        print(
            f"ADRH Comunidad desde {nom} ({len(d)}): hogar {np.average(d.renta_hogar, weights=hog):.0f}"
            f"  uc {np.average(d.renta_uc.fillna(0), weights=d.poblacion * d.renta_uc.notna()):.0f}"
        )
    hog = mun.poblacion / mun.tam_hogar
    adrh_h = np.average(mun.renta_hogar, weights=hog)
    mu = mun.dropna(subset=["renta_uc"])
    adrh_uc = np.average(mu.renta_uc, weights=mu.poblacion)

    e_media = np.average(inq.HY020, weights=inq.DB090)
    e_med = wq(inq.HY020, inq.DB090, 0.5)
    e_todos = np.average(m.HY020, weights=m.DB090)
    sin_neg = inq[inq.HY020 > 0]
    print(
        f"ECV inquilinos HY020 media {e_media:.0f} mediana {e_med:.0f} (sin renta<=0: media "
        f"{np.average(sin_neg.HY020, weights=sin_neg.DB090):.0f}); todos ES30 media {e_todos:.0f}"
    )
    print(
        f"ADRH hogar {adrh_h:.0f} vs ECV todos {e_todos:.0f}: {pct(adrh_h, e_todos):+.1f} %"
    )
    f3_h = adrh_h * aj
    print(
        f"F3-06 renta hogar inquilinos {f3_h:.0f} (ajuste {aj:.4f}) vs media {pct(f3_h, e_media):+.1f} %"
        f" vs mediana {pct(f3_h, e_med):+.1f} %"
    )
    e_uc = r_uc(inq)
    e_uc_todos = r_uc(m)
    f3_uc = adrh_uc * aj
    print(
        f"ADRH uc {adrh_uc:.0f} vs ECV uc todos {e_uc_todos:.0f}: {pct(adrh_uc, e_uc_todos):+.1f} %"
    )
    print(
        f"F3-06 renta UC inquilinos {f3_uc:.0f} vs ECV {e_uc:.0f}: {pct(f3_uc, e_uc):+.1f} %"
    )

    # --- 2. Alquiler (mercado, HH021 = 3)
    e_alq = {q: wq(mer.HH060, mer.DB090, q) for q in (0.25, 0.5, 0.75)}
    print(
        "ECV HH060 mercado P25/P50/P75",
        {k: round(v) for k, v in e_alq.items()},
        "media",
        round(np.average(mer.HH060, weights=mer.DB090)),
        "n",
        mer.HH060.notna().sum(),
    )
    hojas = alquiler.leer_serpavi()
    s = alquiler.alquiler_seccion(hojas)
    s = s[s.anio == 2024].merge(c[["seccion_id", "t20_2"]], on="seccion_id", how="left")
    print("secciones SERPAVI 2024", len(s), "sin censo", s.t20_2.isna().sum())
    con = s.dropna(subset=["cuantia_p50", "t20_2"])
    fuera = 1 - con.t20_2.sum() / c.t20_2.sum()
    print(f"inquilinos del Censo fuera del agregado {100 * fuera:.1f} %")
    z = alquiler.alquiler_zona(hojas)
    z = z[(z.anio == 2024) & (z.zona_id.str.len() == 5)]
    cm = c.groupby(c.seccion_id.str[:5]).t20_2.sum().rename("t20_2")
    z = z.merge(cm, left_on="zona_id", right_index=True).dropna(subset=["cuantia_p50"])
    ipc = alquiler.leer_ipc()
    anual = ipc.groupby(ipc.index.str[:4]).mean()
    k_ipc = anual["2025"] / anual["2024"]
    print(f"IPC alquiler Madrid media 2025/2024 {k_ipc:.4f}")
    f3_alq = {}
    for q, col in ((0.25, "cuantia_p25"), (0.5, "cuantia_p50"), (0.75, "cuantia_p75")):
        sec_m = np.average(con[col], weights=con.t20_2)
        mun_m = np.average(z[col], weights=z.t20_2)
        sec_med = wq(con[col], con.t20_2, 0.5)
        f3_alq[q] = sec_m
        print(
            f"SERPAVI {col}: secciones {sec_m:.0f} (mediana ponderada {sec_med:.0f}), municipios {mun_m:.0f}"
            f" | vs ECV P{int(q * 100)} {pct(sec_m, e_alq[q]):+.1f} %, con IPC 2025 "
            f"{pct(sec_m * k_ipc, e_alq[q]):+.1f} %"
        )
    # Lo que integra F3-06: en cada sección, alquiler uniforme entre P25 y P75, mezclado con t20_2
    u = np.linspace(0, 1, 101)
    mezcla = pd.Series(
        (
            con.cuantia_p25.to_numpy()[:, None]
            + np.outer(con.cuantia_p75 - con.cuantia_p25, u)
        ).ravel()
    )
    w_mezcla = pd.Series(np.repeat(con.t20_2.to_numpy() / len(u), len(u)))
    f3_mez = {q: wq(mezcla, w_mezcla, q) for q in (0.25, 0.5, 0.75)}
    for q, v in f3_mez.items():
        print(
            f"mezcla F3-06 P{int(q * 100)} {v:.0f} vs ECV {e_alq[q]:.0f}: {pct(v, e_alq[q]):+.1f} %"
        )
    print(
        f"mezcla media {np.average(mezcla, weights=w_mezcla):.0f} vs ECV media "
        f"{np.average(mer.HH060, weights=mer.DB090):.0f}"
    )

    # --- 3. Suministros
    s_ecv = inq.HH070 - inq.HH060
    okk = s_ecv.notna()
    e_sum = wq(s_ecv[okk], inq.DB090[okk], 0.5)
    cesta = hogares.cesta_uc()
    f3_sum_h = cesta["suministros"] * inq.HX240[okk]
    f3_sum = wq(f3_sum_h, inq.DB090[okk], 0.5)
    comunidad = 600.38 / 12  # EPF 2025, 04.4 gastos comunitarios, €/UC·año (hogares.py)
    f3_sum_com = wq(f3_sum_h + comunidad * inq.HX240[okk], inq.DB090[okk], 0.5)
    print(f"cesta suministros €/UC·mes {cesta['suministros']:.2f}")
    print(
        f"suministros mediana ECV {e_sum:.0f} (n {okk.sum()}, mercado {wq((mer.HH070 - mer.HH060).dropna(), mer.DB090[mer.HH070.notna()], 0.5):.0f})"
        f" vs EPF {f3_sum:.0f}: {pct(f3_sum, e_sum):+.1f} %; con comunidad {f3_sum_com:.0f}: {pct(f3_sum_com, e_sum):+.1f} %"
    )
    print(
        "ECV HH070-HH060 P25/P75",
        round(wq(s_ecv[okk], inq.DB090[okk], 0.25)),
        round(wq(s_ecv[okk], inq.DB090[okk], 0.75)),
        "ceros",
        round(100 * np.average(s_ecv[okk] <= 0, weights=inq.DB090[okk]), 1),
        "%",
    )


    # --- 4. Sensibilidad de la sobrecarga (> 40 %) a cada factor, orden de magnitud
    def tasa(k_renta=1.0, k_alq=1.0, k_sum=1.0):
        y = ecv._supera(
            (
                inq.HH060 * np.where(inq.HH021 == 3, k_alq, 1)
                + (inq.HH070 - inq.HH060) * k_sum
            )
            * 12,
            inq.HY020 * k_renta,
            0.40,
        )
        return ecv.tasa(y, inq.DB090)[0]


    base = tasa()
    print(f"base {base:.2f}")
    k_alq = {q: f3_alq[q] / e_alq[q] for q in f3_alq}
    fac = {
        "renta (media)": dict(k_renta=f3_h / e_media),
        "renta (mediana)": dict(k_renta=f3_h / e_med),
        "renta UC": dict(k_renta=f3_uc / e_uc),
        "alquiler P25": dict(k_alq=k_alq[0.25]),
        "alquiler P50": dict(k_alq=k_alq[0.5]),
        "alquiler P75": dict(k_alq=k_alq[0.75]),
        "suministros": dict(k_sum=f3_sum / e_sum),
        "suministros+comunidad": dict(k_sum=f3_sum_com / e_sum),
    }
    for nom, kw in fac.items():
        print(
            f"  {nom:22s} k={list(kw.values())[0]:.3f} -> {tasa(**kw):.1f} ({tasa(**kw) - base:+.1f} pp)"
        )
    for kr, nom in ((f3_h / e_media, "media"), (f3_uc / e_uc, "UC")):
        for q in (0.25, 0.75):
            v = tasa(k_renta=kr, k_alq=k_alq[q], k_sum=f3_sum / e_sum)
            print(
                f"  todo junto (renta {nom}, alquiler P{int(q * 100)}) -> {v:.1f} ({v - base:+.1f} pp)"
            )
    for q in (0.25, 0.5, 0.75):
        v = tasa(k_alq=f3_mez[q] / e_alq[q])
        print(
            f"  alquiler mezcla P{int(q * 100)} k={f3_mez[q] / e_alq[q]:.3f} -> {v:.1f} ({v - base:+.1f} pp)"
        )
    k_mez = np.average(mezcla, weights=w_mezcla) / np.average(mer.HH060, weights=mer.DB090)
    for kr, nom in ((f3_h / e_media, "media"), (f3_uc / e_uc, "UC")):
        v = tasa(k_renta=kr, k_alq=k_mez, k_sum=f3_sum / e_sum)
        print(
            f"  todo junto (renta {nom}, alquiler media mezcla k={k_mez:.3f}) -> {v:.1f} ({v - base:+.1f} pp)"
        )
    ```

    </details>
  - **El método de F3-06 con entradas de la ECV ([#194](https://github.com/Kuantoapp/kuantoapp.github.io/issues/194), estimado).** Separa el error del método del de las entradas: se aplica `mesobra.sobrecarga.prob_supera` a la Comunidad entera, como si fuera una sola sección, con entradas sacadas de los mismos microdatos con los que se cuenta la tasa directa. **Lo único que cambia entre los dos lados es la forma del cálculo:** log-normales integradas frente a recuento hogar a hogar.
    - **Qué prueba y qué no.** Prueba la forma log-normal **a escala de la Comunidad**: una sola distribución para 562 hogares, con el ρ medido a esa misma escala. F3-06 aplica el método **dentro de cada sección**, con σ del ADRH y el ρ regional como supuesto. Pasar no demuestra que el método valga en cada sección, y fallar no demuestra que falle en cada una. Lo que sí dice es si la forma, con entradas exactas, ya se desvía por sí sola, y de qué pieza sale la desviación.
    - **Regla, fijada el 2026-11-20 antes de ejecutar el método.** El método vale si la diferencia entre su tasa y la directa, **sin redondear**, no supera **3,7 puntos en valor absoluto con cada una de las dos σ** (la del Gini y la del P80/P20; cuenta la peor). Se da también el punto medio, que es lo que mira la regla de #100. 3,7 es la mitad del semiancho de la tolerancia de #129 (7,4): el método no puede consumir más de la mitad del margen. Es una propuesta y se confirma en S3. **No es una regla a ciegas:** la prueba rápida del abogado del diablo en #100 (nota del 19-11 en #194) ya dio +3,7 y +5,9 puntos con entradas parecidas, y la regla se eligió sabiéndolo. **Zona gris:** si el intervalo al 95 % del bootstrap de la diferencia de la peor σ contiene ±3,7, el veredicto se da, pero como no concluyente frente al ruido de muestreo de las entradas (con 562 hogares la media, el Gini y los cuartiles varían de una muestra a otra, así que la diferencia no está libre de muestreo).
    - **Qué decide.** F3-06 ya no se publicó (señal de corte del 18-11). Si el método no vale, cualquier versión futura de F3-06 tiene que cambiar la forma (la pieza que señale la descomposición) antes de volver a compararse con #129, aunque su agregado cayera en [28,6 %; 43,4 %]. Si vale, la desviación de #100 es de las entradas (ADRH, SERPAVI, UC), como ya apuntaba su diagnóstico.
    - **Medida de la regla:** hogares cuyo alquiler más la cesta de suministros (`HH060·12 + s·HX240·12`) supera el 40 % de `HY020`. Es la misma medida que estima F3-06, no la cifra de control: `HH070` incluye la comunidad y gastos que el modelo no tiene, y compararlas mezclaría definición y método. `s` = 81,08 €/UC·mes, la cesta de la EPF 2025 sin actualizar por IPC (`hogares.cesta_uc` con factores 1), porque la renta y el alquiler de la ECV 2025 son de 2024 y la cesta actual (83,95, con IPC hasta 2026-10) añadiría unos 2,9 €/UC·mes que la tasa directa no tiene. La cesta es la misma en los dos lados, así que su año no cambia la diferencia más que por el nivel. **Medida secundaria**, sin regla: alquiler (`HH060·12`) por encima del 30 % de `HY020`, cuya tasa directa es la cifra de control de 41,4 %.
    - **Población:** inquilinos de ES30 (`HH021` 3 o 4) con `HH060` y `HY020` declarados, ponderados con `DB090`. Los mismos hogares dan las entradas del método y la tasa directa.
    - **Entradas del método**, todas de esa población completa (también los hogares con renta ≤ 0 o alquiler 0, como la media del ADRH incluye a todos) y con `DB090`:
      - Renta por UC (`HY020/HX240`): media sin recortar; Gini winsorizado al 1,5 % por cola (los extremos se sustituyen, no se quitan), como el del ADRH, porque `sigma_gini` invierte un Gini winsorizado; P80/P20 (sin recortar: el recorte no mueve esos cuantiles). De ahí `sigma_gini` y `sigma_p80p20`.
      - Alquiler (`HH060`): P25 y P75, convertidos en la log-normal igual que `sobrecarga.alquiler_2025`.
      - UC del hogar: la media de `HX240` de los inquilinos, como la UC común de cada sección de F3-06. Usar una UC común en lugar de la de cada hogar es parte del método y entra en su error. Que F3-06 la saque del tamaño medio de todos los hogares de la sección es error de entradas y aquí no cuenta.
      - ρ: el de `sobrecarga.parametros_ecv` (0,279), que excluye renta ≤ 0 y alquiler 0 porque usa logaritmos; la misma definición que usa F3-06.
      - Pesos de hogares (`DB090`), porque la tasa directa cuenta hogares. El ADRH da el Gini de personas; con pesos de personas va solo como sensibilidad: es error de entradas.
    - **Tasa directa:** `sobrecarga_ecv._supera` con la regla de Eurostat (renta ≤ 0 cuenta como sobrecargado) y `sobrecarga_ecv.tasa`. La log-normal no admite renta ≤ 0 ni alquiler 0: se cuenta lo que pesan y se repite todo sin ellos (entradas y tasa directa), pero el veredicto se da con ellos.
    - **Comprobaciones previstas**, para que la diferencia sea solo del método:
      - De punta a punta con datos sintéticos (test sin microdatos): hogares log-normales con ρ conocido y la misma UC, pasados por el mismo código de entradas, método y tasa directa; la diferencia tiene que salir cerca de 0.
      - La función de la tasa directa reproduce el 41,4 % con `s = 0` y el 30 %, y `control_f306` sigue en 36,0 %.
      - `prob_supera` coincide con un Monte Carlo de las mismas log-normales (< 0,1 puntos).
      - Cambiar la definición del cuantil ponderado (punto medio o escalón) mueve menos de 0,1 puntos.
      - Bootstrap de hogares (500 réplicas): intervalo de la diferencia para la zona gris.
    - **Descomposición**, una pieza cada vez sobre la tasa directa: (a) renta empírica de cada hogar con el alquiler log-normal condicionado a ella; (b) alquiler empírico de cada hogar con la renta log-normal condicionada a él; (c) la UC común en lugar de la de cada hogar, con todo lo demás empírico. Más los cuantiles P10, P50 y P90 empíricos frente a los de cada log-normal.
    - **Resultado (2026-11-20, estimado).** Fuente de todas las cifras: microdatos de la ECV 2025 del INE (`ine_ecv_microdatos_2025_2026-11-18.zip`) y cesta de la EPF 2025 (`hogares.cesta_uc` con factores 1: 81,08 €/UC·mes); cálculo de `test_metodo_con_entradas_de_la_ecv` y del script de abajo. 562 de los 580 inquilinos tienen alquiler y renta; uno tiene renta ≤ 0 (0,12 % del peso) y ninguno alquiler 0.

      Entradas: renta media por UC 21.893 €; Gini winsorizado 30,93, de donde σ = 0,579; P80/P20 2,669, de donde σ = 0,583; alquiler P25 572 y P75 1.000 €/mes (μ = 6,629; σ = 0,414); UC media 1,784; ρ = 0,279.

      | Medida | Tasa directa | Método, σ del Gini | Método, σ del P80/P20 | Diferencia | Punto medio |
      |---|---|---|---|---|---|
      | Alquiler y suministros > 40 % (regla) | 34,44 % | 37,31 % | 37,54 % | +2,87 y **+3,10** | +2,98 |
      | Alquiler > 30 % | 41,45 % | 44,31 % | 44,49 % | +2,86 y +3,05 | +2,95 |

      **Veredicto: la regla no rechaza el método (3,10 ≤ 3,7), pero el resultado no es concluyente (zona gris).** El intervalo al 95 % del bootstrap de la diferencia contiene 3,7: [−0,79; 6,80] con la σ del Gini y [−2,69; 7,72] con la del P80/P20 (error estándar 1,95 y 2,66). Con 562 hogares, la prueba no distingue un error del método de +3 puntos de uno de +6. Tampoco tenía potencia para concluir que vale: con ese error estándar, el intervalo solo quedaría entero por debajo de 3,7 si la diferencia estimada fuera menor que unos −1,5 puntos. El bootstrap remuestrea hogares sin el diseño de la encuesta (el fichero no trae estrato ni sección), así que el intervalo real es, si acaso, más ancho.

      **Pasa en parte por compensación** (descomposición, 40 %; los efectos no se suman):

      | Variante (cambia una pieza; UC común en las tres) | σ del Gini | σ del P80/P20 |
      |---|---|---|
      | (c) Todo empírico | 31,07 % | 31,07 % |
      | (a) Renta empírica, alquiler log-normal | 36,54 % | 36,57 % |
      | (b) Alquiler empírico, renta log-normal | 37,04 % | 37,27 % |
      | Método (las dos log-normales) | 37,31 % | 37,54 % |

      Usar una UC común (1,784) en lugar de la de cada hogar **baja** la tasa 3,4 puntos (de 34,44 a 31,07 %). Sobre esa base, cualquiera de las dos log-normales la **sube** de 5,5 a 6,2 puntos, y juntas, 6,2 a 6,5. El error neto de +3 es la resta de dos errores de signo contrario y mayor tamaño. Con el 30 % pasa lo mismo: 39,02 % con la UC común, 43,6 a 43,8 % con una log-normal. En (a) y (b), la variable empírica se tipifica con los parámetros de su log-normal para condicionar la otra; así la marginal de la otra no es exactamente log-normal. Condicionar por rangos (cópula gaussiana) daría otra cifra, y la conclusión no depende de ello: el tamaño de la subida es aproximado.

      De dónde sale la subida, con los cuantiles (P10, P50 y P90):
      - **Renta:** la log-normal da 8.814, 18.514 y 38.886 € (σ del Gini) frente a 8.051, 19.414 y 39.096 € empíricos. Con la media fija, la log-normal deja la mediana un 4,6 % por debajo de la real: más hogares cerca del umbral. Es el mismo mecanismo que el diagnóstico de #100 encontró en las secciones.
      - **Alquiler:** la log-normal da 445, 756 y 1.286 €/mes frente a 400, 750 y 1.307 € empíricos. La cola barata real es más baja que la que dibuja la log-normal ajustada a P25 y P75.

      Comprobaciones:
      - El lado directo reproduce las cifras de control: `control_f306` da 36,0 % (criterio de la issue; el 35,9 % era antes de #260) y la función de la tasa directa, con `s = 0` y el 30 %, da lo mismo que `alquiler_30` (41,45 %).
      - Con datos sintéticos log-normales, el proceso completo devuelve la σ verdadera (±0,01) y la tasa directa (±0,3 puntos) (`test_metodo_igual_a_directa_si_los_datos_son_log_normales`).
      - `prob_supera` frente a un Monte Carlo de 2·10⁶ extracciones con estas entradas: `prob_supera` da 37,312 y 37,538 %; el Monte Carlo, 37,308 y 37,539 %.
      - ρ recalculado a mano: 0,278724, igual que `parametros_ecv`.
      - Sin el hogar de renta ≤ 0 (entradas, ρ y tasa directa recalculados): diferencia +2,77 y +3,08. El veredicto no cambia.
      - **Cuantil ponderado en escalón** en lugar del punto medio: 37,30 y 37,67 %, es decir, −0,01 y +0,13 puntos. **Pasa de la cota prevista de 0,1** con la σ del P80/P20; la diferencia quedaría en 3,23, aún por debajo de 3,7.
      - **Sensibilidad, error de entradas:** con pesos de personas, como el Gini del ADRH, σ = 0,588 y 0,586 y el método da 37,78 y 37,66 % (+0,47 y +0,12 puntos frente a su σ con pesos de hogares).
      - **Empates en el cuantil (nota del 2026-11-20, #333).** Hay 263 alquileres repetidos (nueve hogares declaran 1.000 €), y el P75 cae en ese bloque. El cuantil del punto medio depende del orden en que quedan los empates, y `np.argsort` sin `kind="stable"` los ordena distinto según la plataforma: en un Mac arm64 (Python 3.14.8, numpy 2.5.5, scipy 1.18.1, pandas 3.1.1, mismo zip) daba P75 1.000,79 € y el método 37,34 y 37,56 % en vez de 37,31 y 37,54 %. Las dos cifras eran correctas para sus entradas (`prob_supera` coincide con `scipy.integrate.quad` a 1e-8 y con un Monte Carlo de 4·10⁶ extracciones). `_cuantil` ordena ahora de forma estable; así sale el P75 de 1.000 € de arriba y todas las cifras de esta sección, salvo dos que también dependían del orden y se han corregido: el P90 empírico del alquiler (1.307 €, antes 1.309) y el intervalo del bootstrap (antes [−0,77; 6,79] y [−2,70; 7,70]). Con los empates agregados en un solo punto, una definición que no depende del orden y que no es la que se fijó antes de ejecutar, el P75 sería 1.002,83 € y el método daría 37,41 y 37,63 % (diferencias +2,96 y +3,19): el veredicto no cambia.

      Lectura:
      - **A escala de la Comunidad, con entradas exactas, el método se desvía +3 puntos (intervalo [−2,7; 7,7]), en el mismo sentido que #100.** #100 sacó 47,2 % (con la misma cesta de 81,08); frente a la tasa directa de la misma medida (34,44 %), son +12,8 puntos, y frente al control con `HH070` (36,0 %), +11,2: 1,6 puntos de esa distancia son de definición. Esta prueba **no permite repartir** los +12,8 entre método y entradas en las secciones: allí la UC común no tiene por qué compensar igual, y el sesgo de la forma por sí sola es de +5,5 a +6,5 puntos. Con el error de esta prueba (+3), las entradas (renta del ADRH, SERPAVI y UC) pesarían más que el método, como apuntó el diagnóstico de #100; con el de la forma sola (+6,5), los dos pesarían casi lo mismo.
      - **La forma sí sesga hacia arriba** de 5,5 a 6,5 puntos, por la mediana de la renta y la cola barata del alquiler. Ese sesgo queda tapado aquí por la UC común. En una sección, la UC del modelo sale del tamaño medio del hogar de la sección y no hay garantía de que compense igual. Una versión futura de F3-06 debería probar la renta con una forma de cola más pesada a la izquierda o integrar por tipo de hogar antes de fiarse del +3.
      - La tasa directa con el mismo coste es 34,44 %, no el 33,6 % de la prueba rápida de #100. Esa prueba se hizo fuera del repo y no se puede saber qué la separa.
      - **Cesta:** se fijó la de 2025 sin IPC (81,08) en los dos lados. **No se han rehecho** las cifras de F3-06 del 18-11 (47,0–47,3 %) con la cesta de 2026 (83,95): este cambio no toca `sobrecarga.py` ni sus datos procesados.

      <details><summary>metodo_194.py</summary>

      Desde la raíz del repo, con los microdatos descomprimidos como dice `data/README.md`: `python metodo_194.py .`. Reutiliza las funciones del test.

      ```python
      # ruff: noqa: T201 -- script de un solo uso (#194), su salida es el resultado
      """#194: el método de F3-06 con entradas de la ECV 2025 frente a la tasa directa. Estimado."""

      import sys
      from pathlib import Path

      import numpy as np
      import pandas as pd
      from scipy.stats import norm

      RAIZ = Path(sys.argv[1])
      sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "tests")]

      from test_sobrecarga_ecv import (
          _cuantil,
          _directa,
          _entradas,
          _gini_winsorizado,
          _inquilinos,
          _metodo,
      )

      from mesobra import hogares as cesta_mod
      from mesobra import sobrecarga as s
      from mesobra import sobrecarga_ecv as ecv

      f = pd.Series(
          1.0, index=sorted({g for c in cesta_mod.CONCEPTOS.values() for _, g in c.values()})
      )
      f.attrs["ipc_hasta"] = "2025-12"
      cesta_mod.factores_ipc = lambda _c: f
      CESTA = cesta_mod.cesta_uc()["suministros"]
      print(f"cesta 2025 sin IPC: {CESTA:.4f} €/UC·mes")

      h = ecv.hogares()
      par = s.parametros_ecv(h)
      RHO = par["rho"]
      q = _inquilinos(h)
      todos = h[(h.DB040 == ecv.MADRID) & h.HH021.isin(ecv.INQUILINOS)]
      print(f"inquilinos ES30 {len(todos)}, con HH060 y HY020 {len(q)}; rho {RHO:.4f}")
      borde = (q.HY020 <= 0) | (q.HH060 <= 0)
      print(
          f"renta<=0: {(q.HY020 <= 0).sum()}, alquiler 0: {(q.HH060 <= 0).sum()}, "
          f"peso {100 * q.DB090[borde].sum() / q.DB090.sum():.2f} %"
      )

      # comprobaciones del lado directo
      print("control_f306:", ecv.control_f306(h)["tasa"].round(2).to_dict())
      print(
          f"directa s=0 k=0,30: {_directa(q, 0.0, 0.30):.3f}  alquiler_30: {ecv.tasa(ecv.alquiler_30(q), q.DB090)[0]:.3f}"
      )


      def rho_de(d):
          ok = d[(d.HH060 > 0) & (d.HY020 > 0)]
          c = np.cov(np.log(ok.HH060), np.log(ok.HY020 / ok.HX240), aweights=ok.DB090)
          return c[0, 1] / np.sqrt(c[0, 0] * c[1, 1])


      print(f"rho recalculado {rho_de(q):.6f} frente a parametros_ecv {RHO:.6f}")

      sec, sig = _entradas(q, CESTA)
      r = q.HY020 / q.HX240
      print("entradas:", sec.round(4).to_dict("records")[0], "sigmas", sig.round(4))
      print(
          f"  Gini wins {100 * _gini_winsorizado(r, q.DB090):.2f}; P80/P20 "
          f"{np.divide(*_cuantil(r, q.DB090, [0.8, 0.2])):.4f}; alquiler P25/P75 {_cuantil(q.HH060, q.DB090, [0.25, 0.75])}"
      )


      def resultado(d, rho, etiqueta):
          for nombre, cesta, k in (
              ("40 % con cesta", CESTA, 0.40),
              ("30 % alquiler", 0.0, 0.30),
          ):
              m = _metodo(d, cesta, k, rho)
              di = _directa(d, cesta, k)
              print(
                  f"{etiqueta} {nombre}: directa {di:.3f}; método σGini {m[0]:.3f} σP80 {m[1]:.3f}; "
                  f"dif {m[0] - di:+.3f} {m[1] - di:+.3f}; medio {m.mean() - di:+.3f}"
              )


      resultado(q, RHO, "BASE")
      sin = q[~borde]
      resultado(sin, rho_de(sin), "SIN BORDE")

      # sensibilidad: σ con pesos de personas
      w_p = q.peso_personas
      sp = [
          s.sigma_gini(100 * _gini_winsorizado(r, w_p)),
          s.sigma_p80p20(np.divide(*_cuantil(r, w_p, [0.8, 0.2]))),
      ]
      print(
          "σ con pesos de personas:",
          np.round(sp, 4),
          "tasa 40:",
          np.round(100 * s.prob_supera(sec, np.array(sp), RHO, 0.40), 3),
      )


      # sensibilidad: cuantil en escalón
      def escalon(x, w, qs):
          o = np.argsort(x.to_numpy())
          x, w = x.to_numpy()[o], w.to_numpy()[o]
          c = np.cumsum(w) / w.sum()
          return np.array([x[np.searchsorted(c, p)] for p in np.atleast_1d(qs)])


      p20, p80 = escalon(r, q.DB090, [0.2, 0.8])
      a25, a75 = np.log(escalon(q.HH060, q.DB090, [0.25, 0.75]))
      sec_e = sec.assign(mu_a=(a25 + a75) / 2, sigma_a=(a75 - a25) / (2 * norm.ppf(0.75)))
      sig_e = np.array([sig[0], s.sigma_p80p20(p80 / p20)])
      print(
          "cuantil en escalón, tasa 40:",
          np.round(100 * s.prob_supera(sec_e, sig_e, RHO, 0.40), 3),
      )

      # Monte Carlo con los parámetros reales
      g = np.random.default_rng(3)
      z, e = g.standard_normal((2, 2_000_000))
      for j, sg in enumerate(sig):
          mlog = np.log(sec.m_media[0]) - sg**2 / 2
          renta = np.exp(mlog + sg * (RHO * z + np.sqrt(1 - RHO**2) * e))
          coste = 12 * (np.exp(sec.mu_a[0] + sec.sigma_a[0] * z) / sec.uc[0] + CESTA)
          mc = 100 * (coste > 0.40 * renta).mean()
          print(
              f"MC σ{j}: {mc:.3f} frente a {100 * s.prob_supera(sec, np.array([sg]), RHO, 0.40)[0]:.3f}"
          )


      # descomposición (40 %, con cesta), una pieza cada vez
      def descomp(d, rho, k=0.40, cesta=CESTA):
          sec, sig = _entradas(d, cesta)
          ub, mu_a, sa, m = sec.uc[0], sec.mu_a[0], sec.sigma_a[0], sec.m_media[0]
          w = d.DB090.to_numpy()
          r = (d.HY020 / d.HX240).to_numpy()
          a = d.HH060.to_numpy()
          out = {}
          for j, sg in enumerate(sig):
              mlog = np.log(m) - sg**2 / 2
              # (a) renta empírica, alquiler log-normal condicionado a ella
              zr = (np.log(np.where(r > 0, r, 1)) - mlog) / sg
              umbral = ub * (k * r / 12 - cesta)
              pa = 1 - norm.cdf(
                  (np.log(np.where(umbral > 0, umbral, 1)) - mu_a - sa * rho * zr)
                  / (sa * np.sqrt(1 - rho**2))
              )
              pa = np.where((r <= 0) | (umbral <= 0), 1.0, pa)
              # (b) alquiler empírico, renta log-normal condicionada a él (alquiler 0: sin correlación)
              za = np.where(a > 0, (np.log(np.where(a > 0, a, 1)) - mu_a) / sa, 0.0)
              c = 12 * (a / ub + cesta)
              pb = norm.cdf(
                  (np.log(c / k) - mlog - sg * rho * za) / (sg * np.sqrt(1 - rho**2))
              )
              out[f"σ{j}"] = (
                  100 * np.average(pa, weights=w),
                  100 * np.average(pb, weights=w),
              )
          # (c) todo empírico con la UC común
          pc = ecv.tasa(
              ecv._supera(12 * (d.HH060 / ub + cesta), d.HY020 / d.HX240, k), d.DB090
          )[0]
          return out, pc


      out, pc = descomp(q, RHO)
      print(
          "DESCOMPOSICIÓN 40 %: (a) renta empírica / alquiler LN, (b) alquiler empírico / renta LN:",
          {k: np.round(v, 3) for k, v in out.items()},
          f"(c) UC común {pc:.3f}",
      )
      out30, pc30 = descomp(q, RHO, k=0.30, cesta=0.0)
      print(
          "DESCOMPOSICIÓN 30 %:",
          {k: np.round(v, 3) for k, v in out30.items()},
          f"(c) UC común {pc30:.3f}",
      )

      # ajuste de la forma: cuantiles empíricos frente a los de cada log-normal
      for j, sg in enumerate(sig):
          mlog = np.log(sec.m_media[0]) - sg**2 / 2
          print(
              f"renta σ{j}: LN P10/P50/P90",
              np.round(np.exp(mlog + sg * norm.ppf([0.1, 0.5, 0.9]))),
          )
      print("renta empírica P10/P50/P90", np.round(_cuantil(r, q.DB090, [0.1, 0.5, 0.9])))
      print(
          "alquiler LN P10/P50/P90",
          np.round(np.exp(sec.mu_a[0] + sec.sigma_a[0] * norm.ppf([0.1, 0.5, 0.9]))),
      )
      print(
          "alquiler empírico P10/P50/P90",
          np.round(_cuantil(q.HH060, q.DB090, [0.1, 0.5, 0.9])),
      )

      # bootstrap de hogares
      g = np.random.default_rng(194)
      difs = []
      for _ in range(500):
          b = q.iloc[g.integers(0, len(q), len(q))]
          m = _metodo(b, CESTA, 0.40, rho_de(b))
          difs.append(m - _directa(b, CESTA, 0.40))
      difs = np.array(difs)
      print(
          "bootstrap dif 40 %: EE",
          difs.std(0, ddof=1).round(3),
          "IC95 σGini",
          np.percentile(difs[:, 0], [2.5, 97.5]).round(3),
          "σP80",
          np.percentile(difs[:, 1], [2.5, 97.5]).round(3),
      )
      ```

      </details>
  - **Hecho:** la fórmula y la cifra de control están en `src/mesobra/sobrecarga_ecv.py` con tests ([#260](https://github.com/Kuantoapp/kuantoapp.github.io/issues/260)). Los tests comprueban además el reparto por tenencia de ES30 frente al catálogo `1912645` y la renta por unidad de consumo frente al IECM `175_000004`, que coincide al céntimo con `HY020/HX240`: la renta del IECM es la renta disponible **neta** de la ECV.
- **Fallos de metadatos del catálogo:** `1934665`, el dataset de la EPF y `1912645` dicen «Toda España» y sus filas no llevan territorio. La propuesta de corrección al catálogo (N2, plan §1) **se descartó el 2026-11-18** ([#130](https://github.com/Kuantoapp/kuantoapp.github.io/issues/130), cerrada sin hacer; ver `docs/decisiones.md`). El ámbito real de los tres ya está comprobado contra el INE en esta página, así que el proyecto no se fía de esos metadatos.
- **Año de la cesta y del alquiler:** el alquiler se actualiza a octubre de 2026 y la cesta se queda en euros de 2025. Hay que decirlo, o actualizar la cesta con el IPC por grupos. **Lo lleva F1-14 ([#82](https://github.com/Kuantoapp/kuantoapp.github.io/issues/82)), que ya tiene la nota en su cuerpo.**
- **Licencias:** no se releyeron hoy. La del catálogo regional (`license_id: cc-by`) sí aparece en cada `package_show`. Para la del INE y la de Eurostat valen las notas de `.claude/skills/dm-verificacion-fuentes/referencia/licencias.md`; la duda entre CC BY y CC BY-SA del INE se resolvió el 16-11 a favor de CC BY 4.0 ([#147](https://github.com/Kuantoapp/kuantoapp.github.io/issues/147), [verificación](licencia-ine.md)). **Lo llevan F1-02 ([#70](https://github.com/Kuantoapp/kuantoapp.github.io/issues/70)) y F3-04 ([#98](https://github.com/Kuantoapp/kuantoapp.github.io/issues/98)): cada fila de `data/README.md` exige su licencia y el veredicto de `dm-verificador-fuentes`.**
- **Contraste de `1912645` con el INE:** hecho el 14-11 (fila de la tabla «Fuente elegida por dato»).
- **Fichero de la ficha y `data/README.md`:** los cambios los aplican F1-16 ([#84](https://github.com/Kuantoapp/kuantoapp.github.io/issues/84)) y las issues que descarguen cada fuente.
