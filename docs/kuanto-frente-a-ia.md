# Kuanto frente a preguntar a una IA

Hicimos la prueba que haría cualquiera antes de buscar piso: preguntar a un asistente de IA dónde le conviene vivir de alquiler. Aquí está qué se preguntó, cuánto se separan las respuestas de la cuenta de Kuanto y qué aporta cada cosa.

- [En corto](#en-corto)
- [Cómo se hizo](#cómo-se-hizo)
- [Métricas de error](#métricas-de-error)
- [Diferencias sin un dato de referencia](#diferencias-sin-un-dato-de-referencia)
- [Conclusiones](#conclusiones)
- [Kuanto y la IA juntos, con MCP](#kuanto-y-la-ia-juntos-con-mcp)

## En corto

| Métrica | Gemini | ChatGPT |
|---|---|---|
| Error medio del sueldo neto mensual | 2,1 % | 3,9 % |
| Municipios puestos en una zona tarifaria que no es | 1 | 1 |
| Diferencia media con Kuanto en el tiempo de viaje (estimado) | 21,3 min menos | 11,0 min menos |

Son cuatro respuestas, una por asistente y perfil: sirve para ilustrar, no para medir cómo se comporta cada asistente en general. Fuente: las tablas de este documento.

## Cómo se hizo

El 25-11-2026 se pasó cada pregunta una sola vez, en un chat nuevo.

| Asistente | Plan | Sesión | Modelo |
|---|---|---|---|
| Gemini | Gratuito | Sin iniciar | Selector en modo automático |
| ChatGPT | Gratuito | Sin iniciar | El que sirve por defecto; no se anotó la versión |

**Perfil A, sola con el salario mínimo:**

> Hola, tengo 30 años, vivo sola y cobro el salario mínimo, 17.094 € brutos al año. Trabajo en Getafe de lunes a viernes y voy en transporte público. Quiero irme de alquiler a un piso para mí sola en la Comunidad de Madrid. ¿Dónde me conviene vivir para que me sobre más dinero a final de mes sin pasarme horas en el transporte? Dime unas cuantas zonas con lo que me costaría el alquiler, el abono, la comida y los gastos básicos, y cuánto me quedaría.

**Perfil B, madre sola con un hijo:**

> Hola, soy madre soltera, tengo 34 años y un hijo. Trabajo de administrativa en Getafe, de lunes a viernes, y gano 25.290 € brutos al año. Voy en transporte público. Busco un piso de alquiler en la Comunidad de Madrid para los dos. ¿Qué zonas me recomiendas para que me llegue el dinero y no tarde mucho en ir al trabajo? Dime unas cuantas zonas con el alquiler, el transporte, la comida y los gastos básicos, y lo que me sobraría al mes.

Son dos de los [seis perfiles precalculados](https://kuantoapp.github.io/saber-mas.html#perfiles) de la web, con Getafe como lugar de trabajo.

| Asistente | Fuentes que dijo usar, perfil A | Perfil B |
|---|---|---|
| Gemini | Avansel, Engel & Völkers y TaxFix | Ninguna |
| ChatGPT | Alquilómetro, Grupo de Empleo, calculadoras de neto, CRTM y Ayuntamiento de Getafe | Alquilómetro, CRTM y Comunidad de Madrid |

La cuenta de Kuanto sale de `mesobra.mcp_servidor.ranking_zonas` sobre `app/datos/` (la misma que usan la web y el asistente MCP), con destino `28065` (Getafe), 5 días, transporte público y los valores por defecto: piso de 69 m² y tarifas de 2026.

## Métricas de error

Solo se llama error a lo que tiene una respuesta fijada por una norma o una tarifa oficial.

### Sueldo neto

Referencia: el neto de Kuanto, que aplica el IRPF y las cotizaciones de 2026 citados a su BOE y se comprueba con casos de la AEAT en `tests/test_neto.py`. Es el neto del año entre 12, y el error se calcula antes de redondear. Cuando el asistente dio un intervalo, se toma su punto medio. Fuente: `app/datos/netos.json`; estimado.

| Perfil | Asistente | Dijo (€/mes) | Kuanto (€/mes) | Error mensual | Error anual |
|---|---|---|---|---|---|
| A | Gemini | 1.285 a 1.310 | 1.332 | −34 € (−2,6 %) | −413 € |
| A | ChatGPT | 1.288 | 1.332 | −44 € (−3,3 %) | −527 € |
| B | Gemini | 1.680 a 1.720 | 1.727 | −27 € (−1,5 %) | −319 € |
| B | ChatGPT | 1.650 (de 1.600 a 1.700) | 1.727 | −77 € (−4,4 %) | −919 € |

Los cuatro netos se quedan por debajo. En el perfil B hay que matizar: la pregunta no decía la edad del hijo y Kuanto supone entre 3 y 24 años, contrato indefinido y declaración individual (fuente: `src/mesobra/neto.py`).

### Zona tarifaria y precio del abono

Los precios de los abonos que citaron los dos asistentes coinciden con los oficiales (Abono 30 días: B1 38,20 €, B2 43,20 €, B3 49,20 €, interzonal B1-B2 28,70 €; fuente: BOCM-20251231-2). Los fallos están en a qué zona pertenece cada municipio y en qué título hace falta:

| Fallo | Quién | Correcto |
|---|---|---|
| Fuenlabrada en la zona B1 | Gemini, perfil A | B2 (fuente: `app/datos/zonas.geojson`) |
| Humanes de Madrid con abono de la zona B2 | ChatGPT, perfil B | B3 (fuente: `app/datos/zonas.geojson`) |
| Abono B2 de 43,20 € para ir de Parla o Fuenlabrada a Getafe | ChatGPT en los dos perfiles y Gemini en el A | El interzonal B1-B2, 28,70 €, basta si no se entra en la zona A (fuente: BOCM-20251231-2) |

Gemini dio a Fuenlabrada un título distinto en cada perfil.

## Diferencias sin un dato de referencia

Aquí no hay un valor oficial, así que se mide cuánto se separa cada respuesta de la estimación de Kuanto, sin decir quién acierta.

### Tiempo de ida a Getafe, en minutos

Punto medio del intervalo de cada respuesta. Kuanto: de puerta a puerta, entre puntos representativos de cada municipio, con los horarios del CRTM (fuente: `app/datos/tiempos.json`; estimado).

| Desde | Kuanto | Gemini A | ChatGPT A | Gemini B | ChatGPT B |
|---|---|---|---|---|---|
| Getafe | 19 | 7,5 | 15 | 10 | 17,5 |
| Leganés | 38 | 15 | 22,5 | 10 | 22,5 |
| Fuenlabrada | 36 | 15 | 32,5 | 12,5 | 27,5 |
| Parla | 41 | 12,5 | 15 | 15 | 27,5 |
| Diferencia media | — | −21,0 | −12,3 | −21,6 | −9,8 |

Los 16 pares quedan por debajo de Kuanto. Una explicación probable, sin comprobar, es que los asistentes cuentan sobre todo el trayecto en tren o metro y no el camino hasta la estación.

### Alquiler y dinero que sobra, en euros al mes

El alquiler no se puede puntuar como error. Kuanto parte de contratos declarados a Hacienda, ajustados a contrato nuevo, y [conviene leerlo como un suelo](preguntas-frecuentes.md#el-alquiler-de-mi-zona-me-parece-bajo-está-mal); los asistentes parecen acercarse a precios de anuncio. Además, el tamaño de piso no es el mismo. Fuente de Kuanto: `app/datos/alquiler.json` y la consulta de arriba; estimado.

| Zona | Alquiler Kuanto | Alquiler Gemini, B | Alquiler ChatGPT, B |
|---|---|---|---|
| Parla | 712 | 825 | 800 a 950 |
| Fuenlabrada | 775 | 875 | 850 a 1.000 |
| Leganés | 820 | 960 | 900 a 1.050 |
| Getafe | 896 | 950 | 950 a 1.100 |

| Perfil y zona | Sobra según Kuanto | Según Gemini | Según ChatGPT |
|---|---|---|---|
| A, Parla | 182 | 175 a 245 | 35 |
| A, Leganés | 82 | 110 a 180 | −10 |
| A, Getafe | 6 | 80 a 150 | −35 |
| B, Parla | 454 | 336 | 150 |
| B, Leganés | 354 | 192 | 50 |
| B, Getafe | 278 | 202 | 0 |

Para la misma persona y zona hay hasta unos 300 € al mes de diferencia (fuente: la tabla anterior; estimado). Cada cuenta supone un alquiler, una cesta y un piso distintos.

## Conclusiones

**Lo que los asistentes hacen bien.** Citan bien los precios de los abonos, avisan de que sus cifras son orientativas, sugieren barrios, habitaciones y ayudas, y hacen preguntas para afinar. Las zonas que proponen son en buena parte las que salen en Kuanto si se limita el viaje a 30 horas al mes: Parla, Fuenlabrada, Leganés y Getafe (fuente: la consulta de arriba; estimado).

**Lo que aporta Kuanto.**

- **Se puede comprobar.** Cada cifra tiene su fuente y las estimaciones van marcadas ([trazabilidad](trazabilidad.md)). Los asistentes suman sus tablas, pero no se puede saber de dónde sale cada importe.
- **Fuentes oficiales.** SERPAVI, INE, BOE, BOCM y CRTM. Los asistentes mezclaron fuentes oficiales con portales y calculadoras privadas ([datos y fuentes](datos-y-fuentes.md)).
- **Misma entrada, mismo resultado.** Es un cálculo, no un texto generado. En esta prueba no se repitieron preguntas, así que no medimos cuánto cambia un asistente de una vez a otra.
- **Compara todas las zonas con datos.** En estos perfiles da cifra en 99 de las 199 zonas y enseña las horas junto al dinero; los asistentes miraron entre 4 y 6 (fuente: la consulta de arriba y las respuestas de la prueba).
- **Privacidad.** En la web, el sueldo y la situación familiar no salen del navegador. Para preguntar a un asistente hay que contárselos a su proveedor.

**Dónde Kuanto se queda corto.** El alquiler es un suelo, usa 69 m² por defecto también para quien vive sola, las zonas donde más sobra pueden quedar a unas 70 horas de viaje al mes y no propone barrios dentro de un municipio ni ayudas a medida (fuente: la consulta de arriba y la [nota metodológica](https://kuantoapp.github.io/metodologia.html#titulo-limites); estimado).

## Kuanto y la IA juntos, con MCP

No hay que elegir. El [asistente MCP](reproducir.md#5-asistente-mcp) permite preguntar en lenguaje normal a una IA y que las cifras salgan de Kuanto:

- La IA entiende la pregunta, repregunta y explica.
- Kuanto calcula, y cada respuesta lleva unidades, año del dato, fuentes y supuestos.
- El servidor pide a la IA que no estime ni complete cifras, que dé las horas junto al dinero y que marque lo estimado (fuente: `src/mesobra/mcp_servidor.py`). Es una instrucción, no una garantía.

**Matiz sobre la privacidad.** El servidor MCP funciona en tu equipo y no usa la red, pero la conversación va a donde esté el modelo. Con Claude, ChatGPT, Gemini u otro asistente en la nube, el sueldo y lo que cuentes de tu hogar llegan a su proveedor. Para que no salgan del equipo hace falta un modelo local. Si no quieres compartirlos, usa la web.

En esta prueba no se midió un asistente conectado a Kuanto por MCP.
