# ¿Me sobra?

**Lo que te queda de tu sueldo, municipio a municipio, después del alquiler, el abono y el tiempo.**
Lemas alternativos: «Tu sueldo, después de Madrid» · «Cuánto te cuesta de verdad vivir donde vives».

Propuesta para DataMad 2026 · versión de 11 de noviembre de 2026 · resultado de 10 rondas de entrevista.
Nace de fusionar dos ideas previas: la 1 (*Salario que sobra*) y la 9 (*alquiler frente a renta*), esta última reformulada como **esfuerzo** y no como legalidad.

> Las marcas **(verificar)** señalan datos o cifras que todavía no se han comprobado en la fuente primaria. Todo lo demás se comprobó el 11 de noviembre de 2026 contra las API o las páginas oficiales.

## Cómo leer esta ficha

Esta ficha **describe y enmarca la idea** para saber cómo afrontarla. **No es una especificación de desarrollo.** Los métodos, herramientas, fuentes y fechas que aparecen son el **punto de partida** que salió de la entrevista: lo que hoy parece mejor con lo que sabemos. Si al desarrollar aparece algo mejor, un dato que no existe o un resultado que obliga a cambiar de rumbo, se cambia.

Para distinguir lo que define la idea de lo que es solo una forma de llevarla a cabo:

**Lo que define la idea (si cambia esto, es otra idea):**
1. **La cuenta completa.** Lo que sobra del sueldo después de vivienda, transporte, gastos básicos y tiempo, no solo el precio del alquiler.
2. **Dos miradas sobre la misma cuenta.** La de quien busca dónde vivir y la de quien decide las ayudas.
3. **Esfuerzo, no legalidad.** Se mide qué parte de la renta se va en vivienda; no se juzga si un alquiler es legal.
4. **Datos abiertos y públicos**, con el catálogo regional en el centro y el portal del Ayuntamiento como complemento.
5. **Honestidad con los límites del dato.** Lo estimado se marca, la incertidumbre se muestra y los supuestos se declaran.
6. **Una decisión que cambia**, no solo un mapa bonito: el impacto se intenta medir.

**Lo que es enfoque de partida (puede cambiar con el desarrollo):** el modelo concreto de imputación o predicción, la forma de calcular los tiempos, los umbrales y parámetros, los perfiles de hogar, los escenarios, las herramientas, la arquitectura, el reparto del equipo, el calendario y el guion.

**Lo que está abierto:** todo lo marcado como **(verificar)** y la lista de la sección 16, más los titulares, que dependen de lo que digan los datos.

---

## 1. La idea en 30 segundos

Un joven que busca piso en la Comunidad de Madrid compara alquileres, pero casi nunca hace la cuenta completa: lo que paga de alquiler, lo que paga de transporte, lo que gasta en lo básico y las horas que pierde en ir a trabajar. Un piso 200 € más barato a 70 minutos puede salir más caro que uno más cerca.

**¿Me sobra?** hace esa cuenta. El usuario mete su sueldo, dónde trabaja y cuántos días va a la oficina, y ve en un mapa cuánto dinero le queda a final de mes en cada municipio (y en cada barrio de Madrid capital).

La misma cuenta, agregada, sirve a la **Administración** para ver dónde se concentran los hogares que dedican demasiado a vivienda y para simular cómo cambiarían las ayudas, en especial el Bono Alquiler Joven, si tuvieran en cuenta el coste del transporte.

## 2. El problema

- **El alquiler se compara sin su coste asociado.** El precio de un piso no incluye el abono, el tiempo de viaje ni la diferencia de gastos según el tipo de hogar.
- **Las ayudas miden solo la renta.** El Bono Alquiler Joven fija requisitos de renta y de precio máximo de alquiler, pero no mira cuánto cuesta desplazarse desde ese piso hasta el trabajo.
- **La demanda de ayuda supera mucho a la que se concede.** En la convocatoria de 2022 del Bono Alquiler Joven en la Comunidad hubo 51.735 solicitudes y 11.477 aceptadas, un 22 % (catálogo regional, conjunto `spacm_bono_alquiler_joven_2022`). El dato es de 2022 y cuenta solicitudes, no personas.
- **El precio del transporte depende de una ayuda temporal.** En 2026 los abonos tienen un descuento del 50 % que depende de que sigan las ayudas estatales; sin ellas, el precio se duplica (prensa, **verificar** en el BOCM de 31 de diciembre de 2025).
- **Madrid no limita el alquiler por ley.** Ningún municipio de la Comunidad figura como zona tensionada en el BOE (septiembre de 2026), y la Comunidad no aplica el mecanismo aunque el Tribunal Constitucional avaló la ley en febrero de 2026. Por eso esta propuesta no habla de alquileres «ilegales» ni de «precio de referencia», sino de **esfuerzo**: qué parte de la renta se va en vivienda.

## 3. Para quién y qué decisión cambia

| Usuario | Pregunta que responde | Decisión que cambia |
|---|---|---|
| **Joven de 18 a 35 años** que busca piso o habitación | «Con mi sueldo y mi trabajo, ¿dónde me sobra más dinero, contando el tiempo?» | Dónde buscar piso; si compensa compartir; cuántos días pedir de teletrabajo |
| **Administración** (Consejería de Vivienda, Consorcio de Transportes, ayuntamientos) | «¿Dónde están los hogares sobrecargados y a quién no llega la ayuda?» | A qué municipios dirigir el Bono; si incluir el transporte en el criterio; qué pasa si se acaba el descuento del abono |

La vista del joven es el gancho de la demo. La vista de la Administración es donde está el impacto, porque es la que puede cambiar una decisión pública.

### Personajes de la demo
1. **Enfermera de 26 años** en un gran hospital (La Paz o el 12 de Octubre), con turnos. Salario público conocido.
2. **Teleoperador de 23 años** con un sueldo cercano al SMI, en un polígono del sur. Es el caso «no llega».
3. **Madre sola de 34 años** con un sueldo administrativo. Es el perfil de mayor sobrecarga.
4. **Pareja de 29 años** con dos sueldos medianos; uno teletrabaja tres días. Enseña el efecto del teletrabajo.

## 4. Cómo funciona para el usuario

1. **Sueldo.** Escribe su sueldo bruto anual (como aparece en una oferta de empleo) o su neto mensual, con un selector. Si escribe el bruto, la herramienta calcula el neto (ver 5.1).
2. **Hogar.** Elige entre cuatro perfiles: vive solo en un piso entero, comparte piso (habitación), pareja con dos sueldos o familia monoparental.
3. **Trabajo.** Elige su lugar de trabajo de una lista de polos de empleo o marca un punto libre en el mapa.
4. **Días presenciales.** De 1 a 5 días a la semana.
5. **Resultado.** Ve un mapa con lo que le sobra al mes en cada municipio, y en cada barrio si mira Madrid capital, más una ficha por zona con el desglose: neto, alquiler, transporte, cesta básica, horas de viaje y su coste.
6. **¿Y si…?** Puede activar escenarios (ver 7) y ver cómo cambia el mapa.

Cada cifra lleva su fuente y, si es estimada, una marca de «estimado» con su intervalo.

## 5. El cálculo, paso a paso

Lo estable es **qué** se cuenta. **Cómo** se calcula cada término es el enfoque de partida y se puede sustituir por algo mejor durante el desarrollo.

El **índice** es una cantidad en euros al mes:

```
sobra = neto − alquiler − transporte − cesta_básica − horas_de_viaje × valor_de_la_hora
```

Se lee sin explicación («te sobran 180 € al mes») y cada término se puede ver por separado. No se fusiona en un índice opaco de 0 a 100.

### 5.1 Neto
- Si el usuario da el bruto anual: bruto − cotizaciones a la Seguridad Social del trabajador − retención de IRPF de 2026 con el tramo autonómico de Madrid, repartido en 12 o 14 pagas según elija.
- El neto calculado se puede corregir a mano si el usuario lo conoce.
- **Control de calidad:** conviene contrastarlo con nóminas reales antes de la demo. Un error fiscal destruye la credibilidad de todo lo demás.

### 5.2 Alquiler
**Fuente base: alquiler de contratos declarados**, no precios de anuncios.
- **Municipios:** SERPAVI del Ministerio de Vivienda (alquiler medio por municipio y sección censal, a partir de datos tributarios). **Es la pieza crítica:** hasta ahora solo se ha visto en visores y la descarga en bloque no está confirmada (ver 12).
- **Madrid capital:** alquiler medio mensual por código postal del catálogo regional (`1934258`, 2023 y 2024, solo códigos con más de 200 viviendas alquiladas), llevado a barrio con una tabla de paso de código postal a barrio.
- **Actualización a 2026:** se aplica la variación del IPC de alquiler del catálogo regional (`1934665`).
- **Lectura:** como el dato sale de contratos ya firmados, muchos de ellos antiguos, **va por debajo del precio que se encuentra hoy**. Por eso se presenta como **suelo**: lo que sobra será, como mucho, lo que dice la herramienta.

**Corrector de oferta.** Para no quedarse solo en el suelo:
- Se calcula un **factor de brecha** por zona = precio de oferta / alquiler de contrato actualizado.
- El precio de oferta sale de un **muestreo puntual** de anuncios. El equipo está dispuesto a hacer scraping para impresionar, pero las condiciones de uso de Idealista y Fotocasa lo prohíben y ha habido pleitos. Por eso **solo se publica el factor agregado** por zona, nunca anuncios ni precios individuales, y se documenta el método.
- Se busca además una fuente municipal legal con precio de oferta. La serie de Idealista por barrio que se creía publicada por el Ayuntamiento **no se ha encontrado** en datos.madrid.es.
- En el mapa, el corrector da una **banda**: «te sobran entre X (con precio de contrato) e Y (con precio de anuncio)».

**Habitación (perfil compartido).** No hay dato oficial abierto del precio de una habitación. Se estima como alquiler del piso ÷ número de dormitorios, más un recargo por habitación calibrado con la muestra de oferta de habitaciones.

**Pareja y monoparental.** Se usa el alquiler de un piso de tamaño adecuado al hogar (superficie media del SERPAVI y del panel municipal).

### 5.3 Transporte
- **Tarifas 2026 por zona** (A, B1, B2, B3, C1, C2): del BOCM de 31 de diciembre de 2025. El conjunto de tarifas del catálogo regional (`1919188`) **no sirve** porque solo trae la Corona Mínima y la Máxima.
- **Zona necesaria:** la más exterior entre la del origen y la del destino.
- **Título más barato:** según los días presenciales, se elige entre abono mensual y billetes de 10 viajes. Si el usuario tiene menos de 26 años, se aplica el abono joven (10 € con descuento, 20 € sin él, **verificar**).
- **Precios de prensa a confirmar:** joven 10 €, B1 38,20 €, B2 43,20 €, B3/C1/C2 49,20 €.

### 5.4 Cesta básica
- Gasto en alimentación y suministros (luz, agua, gas) por tipo de hogar, de la Encuesta de Presupuestos Familiares (INE) para la Comunidad de Madrid, sin incluir el alquiler para no contarlo dos veces.
- Sin este término, la frase «no llega» engañaría: alguien a quien le sobran 300 € después del alquiler puede no llegar a fin de mes.

### 5.5 Tiempo de viaje y su valor
- **Cálculo (una forma de hacerlo):** con los GTFS del CRTM (Metro, Metro Ligero, Cercanías, interurbanos, EMT y urbanos) y la red peatonal de OpenStreetMap, con r5py o OpenTripPlanner. Salida un martes laborable a las 8:00, tiempo puerta a puerta. Origen: centro de población de cada municipio o barrio (ponderado por secciones censales).
- **Destinos:**
  - **Polos de empleo**, obtenidos de los datos de movilidad del MITMA: las zonas que más viajes de casa al trabajo reciben en un día laborable tipo. Así los polos salen del dato y no de una lista hecha a mano.
  - **Destino libre:** el usuario marca cualquier punto y se calcula en vivo. Solo se enseña en la demo si funciona de forma fiable; si el servicio cae, se usa el polo más cercano.
- **Horas al mes** = tiempo de ida y vuelta × días presenciales × 4,33.
- **Valor de la hora:** 50 % del salario por hora del usuario, siguiendo la convención de las guías de evaluación de proyectos de transporte, que valoran el tiempo de viaje no laboral entre el 40 % y el 50 % del salario (**verificar** la cita exacta). Hay un **control deslizante** y un **aviso** visible de que poner precio al tiempo es una convención discutible. Si alguien no quiere monetizarlo, puede ver las horas aparte.

### 5.6 Municipios sin dato de alquiler
Muchos municipios pequeños, sobre todo en la corona C, no tienen alquiler publicado. En vez de dejar huecos justo donde los jóvenes buscan barato:
- Se **estima** el alquiler con un modelo que usa renta (ADRH del INE), valor catastral, precio de compraventa (Notariado), tiempo a los polos de empleo y población.
- **Modelo de partida:** LightGBM con validación cruzada espacial (las particiones son zonas, no filas al azar, para que no se cuele información de los vecinos) e intervalos por **predicción conformal**, que garantizan la cobertura declarada. Se compara siempre con un modelo de referencia simple para demostrar que aporta algo.
- Los municipios estimados aparecen marcados como **«estimado»**, con su intervalo.

## 6. La vista de la Administración

### 6.1 Sobrecarga: cuántos hogares dedican demasiado a vivienda
- **Definición:** un hogar está sobrecargado si el alquiler supera el 30 % de su renta, y en sobrecarga grave si supera el 40 % (umbral de Eurostat).
- **Renta:** Atlas de Distribución de Renta de los Hogares (ADRH) del INE, año 2024, publicado el 19 de octubre de 2026, por municipio, distrito y sección censal.
- **Método propuesto:** el INE publica la media pero no la distribución completa. Por cada sección se ajusta una distribución log-normal de la renta usando la media, el Gini y el cociente P80/P20, y con ella se calcula qué porcentaje de hogares quedaría por encima del 30 % y del 40 %. Para validar el ajuste se comprueba que reproduce el porcentaje de población por debajo del 60 % de la mediana, que el INE también publica.
- **Supuesto que hay que declarar:** el ADRH describe a todos los hogares, pero los que alquilan suelen tener menos renta que los propietarios. Se corrige con la proporción de hogares en alquiler por zona (Censo 2021, **verificar** el nivel territorial) y con la diferencia de renta entre inquilinos y propietarios de la Encuesta de Condiciones de Vida del INE. Sin esa corrección, la sobrecarga saldría infravalorada.
- **Relación con el simulador:** el simulador trabaja con el sueldo de una persona; la vista de la Administración trabaja con la renta de los hogares. Son dos lecturas de la misma cuenta: una individual y otra agregada.

### 6.2 Decisiones que permite
1. **Focalizar el Bono Alquiler Joven.** Mapa de la sobrecarga de los jóvenes frente a las solicitudes, aceptaciones y rechazos del Bono por municipio. Marca los municipios con mucha sobrecarga y poca ayuda.
2. **Criterio con transporte.** Simula un criterio de elegibilidad que cuente alquiler más transporte, no solo la renta. Resultado: cuántos jóvenes entrarían o saldrían de la ayuda por municipio y cuánto costaría. Las reglas del Bono de referencia (Real Decreto 42/2022: 18 a 35 años, ingresos hasta 3 veces el IPREM, alquiler máximo de 600 € o 300 € por habitación, ampliable por la comunidad, y ayuda de 250 € al mes) se **verifican** contra la convocatoria vigente antes de usarlas.
3. **Fin del descuento del abono.** Para cada municipio: euros al mes que se pierden y hogares que pasan a estar sobrecargados si el descuento del 50 % desaparece.

## 7. Escenarios y predicción

### 7.1 Escenarios «¿y si…?»
Son el núcleo de la parte prospectiva, porque responden a decisiones concretas:
- Se acaba el descuento del 50 % del abono.
- El alquiler sube un X % (control deslizante).
- El usuario cumple 27 años y pierde el abono joven.
- Cambia el número de días presenciales.

### 7.2 Predicción
Con pocos años de datos, toda predicción se presenta **siempre con intervalo**.
- **Alquiler a 12 meses** por municipio, con el IPC de alquiler y el precio de compraventa del Notariado como indicador adelantado.
- **Salario sobrante dentro de un año**, combinando la predicción del alquiler con la evolución de los salarios.
- **Sobrecarga futura** por municipio, para la vista de la Administración.
- **Imputación espacial** de los municipios sin dato (ver 5.6). Es la predicción mejor validada y se presenta como tal.

## 8. Qué esperamos encontrar

Hay dos tesis complementarias. Las confirma o las descarta el dato, no al revés:
1. **«Vivir lejos no compensa».** El ahorro en alquiler se lo comen el transporte y el tiempo.
2. **«Ningún sueldo típico llega».** Con sueldos de referencia (deciles del INE por edad, SMI y salarios por ocupación), en muchos municipios no sobra nada después de los gastos básicos.

**Si la primera no se cumple en todas partes** (por ejemplo, en ejes del sur con Cercanías puede compensar), el titular pasa a ser **«Dónde sí compensa vivir lejos y dónde no»**, explicado por la red de transporte. Un resultado matizado da más credibilidad ante un jurado técnico.

**Primer indicio** (MITMA, un solo día, el 15 de octubre de 2025, sin validar). Entre los residentes de la Comunidad que van de casa al trabajo o al estudio:
- **Menores de 25 años:** recorren 9,4 km de media en zonas de renta de 10.000 a 15.000 €, frente a 8,6 km en zonas de más de 15.000 €.
- **De 25 a 45 años:** 8,1 km frente a 7,0 km.
- **Más de 10 km:** los hace el 29 % de las zonas de renta menor, frente al 24 %.

Apunta a la primera tesis, pero no es un resultado: falta repetirlo con un mes completo, por distrito y teniendo en cuenta dónde está el empleo.

**Sueldos de referencia:**
- **Deciles de salario del INE** por edad (Encuesta de Estructura Salarial y EPA): permiten decir «el joven mediano de 25 a 34 años».
- **IRPF por municipio** de la Agencia Tributaria: el sueldo de quien ya vive en cada sitio, para la vista de la Administración (**verificar** el último año).
- **Salarios por ocupación del INE:** dan cifras reconocibles para los personajes.

## 9. Validación e impacto

### 9.1 ¿El índice mide lo que dice? (validación externa)
Si el mapa de sobrecarga es correcto, debería ir en la misma dirección que señales independientes:
- **Desahucios por la Ley de Arrendamientos Urbanos** por distrito (panel municipal): más sobrecarga, más desahucios.
- **Vivienda como problema principal** por distrito (Encuesta de Calidad de Vida del Ayuntamiento).
- **Vulnerabilidad territorial** (índice IGUALA del Ayuntamiento).
- **Rechazos del Bono Alquiler Joven** por municipio frente a la sobrecarga estimada.

Se informa de la correlación y su signo, también cuando no sale la esperada.

### 9.2 ¿El dato es fiable? (validación del dato)
- Error del modelo de imputación en validación cruzada espacial.
- Tamaño de la brecha entre oferta y contrato y error del corrector.
- Cobertura real de los intervalos conformales.

### 9.3 ¿Cambia decisiones? (impacto medido)
En los concursos revisados, casi ningún ganador mide su impacto. Esta propuesta lo intenta con dos piezas:
- **Simulación del Bono** (6.2): cuántos jóvenes y cuánto dinero cambiarían de grupo con un criterio que incluya el transporte.
- **Test con usuarios antes y después** con 15 a 30 jóvenes, reclutados en aulas de la URJC y la UCM, en la red del equipo y en organismos de juventud. Primero dicen dónde buscarían piso y cuánto creen que les sobraría; después usan la herramienta y responden de nuevo.
  - **Métricas fijadas antes del test:** porcentaje que cambia la zona donde buscaría piso · diferencia entre lo que creían que les sobraría y lo que calcula la herramienta · usabilidad con el cuestionario estándar SUS.
  - **Ética:** consentimiento informado, sin datos personales identificables (RGPD).

## 10. IA y apertura

- **API abierta** con el índice y sus componentes.
- **Servidor MCP público:** cualquier asistente puede preguntar «¿dónde me sobra más con 24.000 € trabajando en Getafe?» y recibir una respuesta con cifras calculadas y su fuente. Encaja con la formación oficial de DataMad (APIs, MCP y espacios de datos; IA aplicada a datos abiertos).
- **Asistente conversacional** dentro de la web, solo si pasa una puerta de calidad. El principio es que nunca invente una cifra; los números concretos de la prueba son una referencia:
  - Batería de 50 preguntas de los personajes, incluidas trampas fuera de alcance.
  - El 100 % de las cifras sale de herramientas del MCP, nunca del modelo, y el 100 % de las respuestas cita su fuente.
  - Rechaza bien lo que no puede contestar y avisa de que es una IA (artículo 50 del Reglamento de IA).
  - **Un solo fallo numérico y no sale en la demo.** La API y el MCP siguen.
- **Entregables abiertos:**
  - El índice como conjunto de datos por municipio y barrio (CSV y GeoParquet, metadatos DCAT-AP, CC BY 4.0), listo para proponerlo al catálogo regional o a datos.gob.es.
  - Repositorio con licencia MIT que regenera todo con un comando desde las fuentes oficiales, con pruebas del cálculo de bruto a neto y del índice.
  - Nota metodológica de 2 o 3 páginas con supuestos, límites y validación.

## 11. Encaje con los criterios de DataMad

| Criterio | Cómo lo cumple |
|---|---|
| **Uso de la información pública regional** (oficial) | El núcleo usa el catálogo regional: Bono Alquiler Joven, alquiler por código postal, IPC de alquiler, valor catastral de referencia, afiliados por residencia y zonificación de transporte. Lo completan el portal del Ayuntamiento (zoom a barrio, validación) y fuentes nacionales abiertas (INE, MITMA, CRTM, SERPAVI). |
| **Viabilidad** (oficial) | Pipeline reproducible, frontend con respaldo estático que funciona sin servidor, calendario con datos congelados y ensayo con URL pública. Las piezas con riesgo (destino libre, asistente) tienen alternativa. |
| **Código abierto** (oficial) | Repositorio MIT, librerías abiertas (MapLibre, DuckDB, LightGBM, r5py), conjunto de datos CC BY 4.0, API y MCP públicos. |
| **Valor económico, social o medioambiental** (citado por la URJC y la prensa) | Decisión pública concreta (focalizar el Bono, criterio con transporte, fin del descuento), impacto medido con un test antes y después, y validación externa. |

## 12. Datos

### 12.1 Catálogo regional (datos.comunidad.madrid, CKAN, CC BY 4.0) · obligatorio
| Conjunto | Qué aporta | Límite |
|---|---|---|
| `spacm_bono_alquiler_joven_2022` | Solicitudes, aceptadas y rechazadas por municipio (51.735 / 11.477 / 22 %) | Solo 2022; 3.352 solicitudes sin municipio |
| `1934258`, `1934261` | Alquiler medio mensual y días alquilados por código postal | Solo Madrid capital, 2023–2024, códigos con más de 200 viviendas |
| `1934246` | Alquiler, m², rentabilidad y valor de referencia | Solo el total de la Comunidad |
| `valor_referencia_viviendas_arrendadas_…_mas_20000` | Valor catastral de referencia (no es alquiler) | 38 municipios con valor en 2024 |
| `1934665` y anteriores | IPC de alquiler | Índice, no nivel de precio |
| `1919188` | Tarifas 2007–2024 | Solo Corona Mínima y Máxima: no sirve para las zonas |
| `1916304` | Renta neta media (Base 2013) | Nivel territorial por confirmar |
| `afiliados_por_residencia_*` | Afiliados por municipio de residencia (edad, contrato, jornada) | Por residencia, no por lugar de trabajo |
| `zt84`, `resultados-edm2018` | Zonas de transporte y Encuesta Domiciliaria de Movilidad 2018 | Datos de 2018 |

### 12.2 Portal del Ayuntamiento (datos.madrid.es, CKAN, CC BY 4.0) · zoom a barrio y validación
| Conjunto | Qué aporta |
|---|---|
| `300087-0-indicadores-distritos` | Renta neta media por hogar por barrio 2016–2023 (en 2023, Puente de Vallecas 32.666 € frente a Chamartín 79.274 €) · renta por persona por barrio · valor catastral residencial · superficie media en compraventa · desahucios por la LAU · hogares monoparentales · paro |
| `300438-0-hogares-tamano` | Hogares por tamaño y composición por sección censal |
| `300431-0-personas-viven-solas` | Personas que viven solas por edad y barrio |
| `300588-0-estudio-panel-hogares` | Panel de Hogares (revisar si pregunta por el gasto en vivienda) |
| `319934-0-encuesta-calidad-de-vida-resultados` | La vivienda como problema percibido |
| `300577-0-iguala-vulnerabilidad`, `300301-0-ranking-vulnerabilidad` | Vulnerabilidad territorial |
| `300526-0-promociones-viviendas-emvs` | Vivienda pública municipal por distrito y año |
| `900030-0-emt-autobus-gtfs`, `900031-0-emt-autobus-api` | Red de EMT |
| `300496-0-barrios-madrid` | Geometría de los barrios |

### 12.3 Fuentes nacionales y otras
| Fuente | Qué aporta | Estado |
|---|---|---|
| **INE ADRH 2024** | Renta por hogar y persona, Gini, P80/P20, % por debajo del 60 % de la mediana, % de renta salarial; por municipio, distrito y sección | Publicado el 19 de octubre de 2026 |
| **SERPAVI (Ministerio de Vivienda)** | Alquiler de contratos por municipio y sección | **Descarga en bloque sin confirmar** |
| **INE IPVA** | Índice de alquiler por municipio y por distrito de las capitales | Último año 2024 |
| **MITMA, movilidad con telefonía** | Viajes diarios de casa al trabajo por municipio y distrito, con distancia, tramo de renta del origen (<10, 10–15, >15 mil €), edad y sexo | CC BY 4.0. Ficheros diarios hasta octubre de 2025 como mínimo |
| **CRTM** | GTFS de las seis redes | **Licencia sin confirmar** |
| **BOCM 31/12/2025** | Tarifas 2026 por zona | Pendiente de leer la tabla |
| **INE EPF** | Gasto en alimentación y suministros por tipo de hogar | Por descargar |
| **INE, salarios** | Deciles por edad y salarios por ocupación | Por descargar |
| **Agencia Tributaria** | IRPF por municipio | Verificar último año |
| **Notariado** | Precio de compraventa por municipio y código postal | El equipo tiene acceso a la API; **licencia pendiente** |
| **OpenStreetMap** | Red peatonal para el cálculo de rutas | ODbL: citar «© OpenStreetMap contributors» |

## 13. Arquitectura (propuesta)

Lo importante es que la demo no dependa de un único servidor y que todo sea reproducible y abierto. Las herramientas concretas son la opción de partida.

- **Pipeline** en Python con DuckDB: descarga las fuentes, las cruza, calcula el índice, entrena los modelos y precalcula las matrices de tiempos.
- **Backend** FastAPI: API, servidor MCP, destino libre y asistente.
- **Frontend** con MapLibre y teselas PMTiles. Funciona también **en estático** con lo precalculado (por ejemplo, en GitHub Pages) si el backend falla durante la demo.
- **Geometrías:** barrios municipales, distritos del MITMA, secciones del INE y códigos postales no coinciden. Se construyen tablas de paso antes de cruzar nada.

## 14. Equipo y calendario

**Equipo:** 3 científicos de datos. El reparto está por decidir. Nadie tiene perfil de frontend ni de presentación; el frontend se apoya en desarrollo asistido por IA y una persona se reserva desde el 20 de noviembre para el test con usuarios y el relato.

**Bloques de trabajo** (para repartir):
1. **Alquiler y renta:** SERPAVI, catálogo regional, ADRH, corrector de oferta, imputación, sobrecarga, predicción.
2. **Movilidad y coste:** GTFS, MITMA, polos de empleo, matrices de tiempo, tarifas, bruto a neto, cesta básica.
3. **Producto y relato:** frontend, API, MCP, asistente, test con usuarios, validación, presentación.

**Calendario orientativo** (alcance completo y flexible; las únicas fechas fijas son las de la organización):
| Fecha | Hito |
|---|---|
| 12–14 nov | Resolver las verificaciones críticas (SERPAVI, licencias, tarifas). Pipeline de datos funcionando |
| 15–19 nov | Índice, imputación, sobrecarga, matrices de tiempo, primera versión navegable |
| 20 nov | Versión usable para el test |
| 21–23 nov | Test con usuarios |
| 22 nov | **Datos y cálculos congelados** |
| 23 nov | Cifras finales y titulares |
| 24–25 nov | Ensayo con la URL pública; evaluación final del asistente |
| 26 nov | Presentación ante el jurado en la URJC |

## 15. Guion de 5 minutos (borrador)

Combina abrir con un dato y contar el resto con un personaje. Las cifras y los titulares se sustituirán por los que salgan del análisis:
- **0:00** De 51.735 solicitudes del Bono Alquiler Joven en 2022, solo se aceptó el 22 %. Y quien vive de alquiler, ¿cuánto le queda a fin de mes?
- **0:20** La enfermera de 26 años mete su sueldo en directo y aparece el mapa.
- **1:10** Cambia los días de teletrabajo; después se acaba el descuento del abono. El mapa se mueve.
- **2:00** Titulares con datos del MITMA y del INE: dónde compensa vivir lejos y dónde no, y en cuántos municipios no llega un sueldo típico.
- **3:00** Vista de la Administración: simulación del Bono con el transporte en el criterio.
- **4:00** Validación, resultados del test con usuarios y entregables abiertos (conjunto de datos, API, MCP).
- **4:40** Cierre y URL.

## 16. Riesgos y verificaciones

### Riesgos
| Riesgo | Mitigación |
|---|---|
| **SERPAVI sin descarga en bloque** (es el alquiler municipal del núcleo) | Resolverlo el primer día. Alternativas: pedir los datos al Ministerio, usar el visor público de forma documentada, o apoyarse más en la imputación y declararlo |
| Dato de contratos por debajo del precio actual | Presentarlo como suelo y dar la banda con el corrector de oferta |
| Scraping contra las condiciones de uso | Muestreo puntual, solo publicar el factor agregado |
| Licencias del Notariado y del CRTM | Confirmarlas por escrito antes de publicar derivados |
| Error en el cálculo de bruto a neto | Validar con nóminas reales |
| Sobrecarga infravalorada por usar a todos los hogares | Corrección por inquilinos (6.1), declarada como supuesto |
| Intervalos de predicción anchos | Mostrarlos siempre; los escenarios son el núcleo prospectivo |
| Fallo en la demo (destino libre, asistente) | Respaldo estático y puerta de calidad |
| Equipo sin frontend ni relato | Desarrollo asistido por IA; una persona dedicada desde el 20 |
| Datos personales en el test | Consentimiento y anonimato |

### Verificaciones pendientes
- Descarga en bloque del SERPAVI.
- Licencia de los GTFS del CRTM (su página de licencia devolvió error 500).
- Licencia del Notariado, por escrito.
- Tarifas 2026 por zona en el BOCM.
- Reglas vigentes del Bono Alquiler Joven en la Comunidad.
- Cita del valor del tiempo en las guías de evaluación de transporte.
- Mes completo del MITMA, por distrito, para confirmar o descartar el indicio.
- Nivel territorial de la tenencia de vivienda en el Censo 2021 y de la renta del catálogo regional (`1916304`).

---

## Anexo: registro de las 10 rondas de entrevista

Recoge lo que se acordó como punto de partida en cada ronda. No es un compromiso cerrado: si el desarrollo lo pide, se revisa.

| Ronda | Pregunta | Respuesta del equipo |
|---|---|---|
| 1 | Usuario principal | Joven + Administración |
| 1 | Fuente del alquiler | Dato declarado con corrector; el scraping se acepta si hace falta, para impresionar |
| 1 | Encaje de la idea 9 | Como esfuerzo (sobrecarga), sin «referencia» ni «legal» |
| 1 | Capa predictiva | Escenarios y también predicciones |
| 2 | Precio de oferta | Solo como corrector + fuente municipal legal + API del Notariado |
| 2 | Tiempo de viaje | Destino libre (con cautela y asegurando que funcione en la demo) + GTFS + polos de empleo |
| 2 | Perfiles de hogar | Los cuatro: solo, compartido, pareja, monoparental |
| 2 | Equipo | 3–4 personas con perfiles mixtos (luego aclarado: 3 científicos de datos) |
| 3 | Entrada del salario | Bruto y neto con selector |
| 3 | Índice propio | Salario sobrante con tiempo, en euros |
| 3 | Pruebas de impacto | Simulación del Bono, test con usuarios, validación del dato |
| 3 | Titular | Decidir tras los datos; atraen «vivir lejos no compensa» y «ningún sueldo típico llega» |
| 4 | Valor del tiempo | 50 % del salario por hora, control deslizante y aviso sobre la dificultad de monetizar el tiempo |
| 4 | Cobertura | Imputar con modelo y marcar como estimado |
| 4 | Gastos | Añadir cesta básica |
| 4 | Qué predecir | Alquiler a 12 meses, salario sobrante futuro, sobrecarga futura e imputación espacial |
| 5 | Recorte de alcance | Rechazado: con desarrollo asistido por IA el código no es el cuello de botella |
| 5 | IA | API + MCP + asistente, este último solo si está bien calibrado y funciona |
| 5 | Vista de la Administración | Focalizar el Bono, criterio con transporte, fin del descuento del abono |
| 5 | Arquitectura | Atrae el backend; se combina con el respaldo estático |
| 6 | Calendario | Alcance completo y flexible, datos congelados el 22 |
| 6 | Notariado | El equipo ya tiene acceso |
| 6 | Habitaciones | Reparto por dormitorios + calibración con oferta |
| 6 | Reclutamiento del test | Aulas de la URJC y la UCM, red propia, juventud institucional |
| 7 | Portal del Ayuntamiento | Zoom a barrio en Madrid capital |
| 7 | Polos de empleo | Empíricos con el MITMA |
| 7 | Sueldos de referencia | Deciles del INE, IRPF por municipio, salarios por ocupación |
| 7 | Validación externa | Desahucios por la LAU, vivienda como problema, IGUALA, rechazos del Bono |
| 8 | Personajes | Los cuatro |
| 8 | Teletrabajo | Sí, días presenciales |
| 8 | Entregables abiertos | Conjunto de datos, repositorio MIT, nota metodológica, MCP público |
| 8 | Reparto | Por decidir; los tres son científicos de datos |
| 9 | Método de sobrecarga | Distribución ajustada por sección censal |
| 9 | Modelo | Gradient boosting con predicción conformal |
| 9 | Guion | Combinar abrir con el dato y recorrer con el personaje |
| 9 | Puerta del asistente | 50 preguntas, 100 % de cifras exactas |
| 10 | Plan B del titular | «Dónde sí y dónde no», con el resto de tesis como complementarias |
| 10 | Éxito del test | Cambio de decisión, error de estimación, usabilidad (SUS) |
| 10 | Nombre | «¿Me sobra?» con un lema descriptivo |
