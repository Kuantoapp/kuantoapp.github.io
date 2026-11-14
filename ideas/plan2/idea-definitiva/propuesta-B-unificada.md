# Cerca

**¿Tiene cerca lo que necesita quien más lo necesita? Y si no, ¿dónde conviene ponerlo?**
Titular de la propuesta: «La media municipal oculta a las personas que más lejos están de los servicios».

Propuesta B unificada para DataMad 2026 · versión de 14 de noviembre de 2026.
Une el [plan de Izan](../izan/plan-propuesta-B.md) (*vulnerabilidad oculta y dónde intervenir*, 11/11/2026) y la [ficha de Yeray](../yeray/plan_propuesta_B_Yeray_Cerca.md) (*Cerca*, 12/11/2026). Las dos nacen de fusionar la idea 10 (*índice de vulnerabilidad territorial municipal*) y la idea 3 (*ciudad de 15 minutos con equidad por renta*).

> **Estado: propuesta, no decisión.** La primera revisión de `dm-abogado-del-diablo` (14/11/2026) dio NO APTO; esta versión aplica sus correcciones (Anexo B.4) y falta repetir la revisión antes de anotarla en `docs/decisiones.md`. Las marcas **(verificar)** señalan datos o cifras que no se han comprobado en la fuente primaria; vienen de los planes de origen y esta ficha no ha comprobado ninguna.

## Cómo leer esta ficha

Esta ficha **describe y enmarca la idea** para saber cómo afrontarla. **No es una especificación de desarrollo.** Los métodos, herramientas, umbrales y fuentes que aparecen son el **punto de partida**: lo que hoy parece mejor con lo que sabemos. Si al desarrollar aparece algo mejor, un dato que no existe o un resultado que obliga a cambiar de rumbo, se cambia y se anota en el registro de decisiones (Anexo B).

**Lo que define la idea (si cambia esto, es otra idea):**
1. **Necesidad y cercanía, juntas pero separadas.** Interesa dónde coinciden la vulnerabilidad y la falta de acceso a pie, y para verlo se miden por separado: la necesidad no incluye el acceso.
2. **La media esconde.** La misma necesidad, medida por sección censal y agregada a la zona, muestra cuánta vulnerabilidad queda oculta en zonas que, en la media, parecen sanas.
3. **Personas concretas, no promedios.** El acceso se mide desde donde vive la gente y para perfiles con necesidades distintas.
4. **Diagnosticar, proponer y medir el valor del detalle.** Ver dónde está el problema, proponer dónde actuar y medir cuántas personas vulnerables se dejan de alcanzar cuando se prioriza con la media de la zona en lugar de con la sección.
5. **Una decisión real y actual:** el PIR 2027-2031 y la ubicación de servicios públicos.
6. **Datos abiertos y públicos**, con el catálogo regional en el centro y el portal del Ayuntamiento como pieza obligatoria.
7. **Honestidad con los límites del dato:** lo aproximado se marca, los supuestos se declaran y lo descartado se explica.

**Lo que es enfoque de partida (puede cambiar con el desarrollo):** los indicadores concretos, los pesos, los umbrales y velocidades, el método de ubicación, las referencias con las que se mide el valor, las herramientas y la arquitectura.

**Lo que está abierto:** todo lo marcado como **(verificar)** y la lista de la sección 15.

**Criterio de alcance.** El desarrollo lo hacen agentes, así que el tiempo de desarrollo no recorta el alcance. Una pieza se queda fuera solo por método, por riesgo ante el jurado o por límites reales: la congelación de datos del 22 de noviembre, el tiempo de cálculo, la duración de la presentación y la revisión de las cifras.

---

## 1. La idea en 30 segundos

Un índice municipal puede decir que un municipio está bien mientras parte de sus vecinos viven en secciones pobres, envejecidas y lejos de todo. La media esconde el hueco.

**Cerca** mide ese hueco en dos pasos:
- **Necesidad:** un índice de vulnerabilidad por sección censal en toda la Comunidad de Madrid, que muestra qué parte de la vulnerabilidad queda escondida dentro de municipios y distritos que en la media parecen sanos.
- **Cercanía:** desde cada edificio residencial, cuánto se tarda a pie, con pendiente y a la velocidad de cada perfil, en llegar al centro de salud, la farmacia, los servicios sociales, el colegio, una parada con frecuencia o un desfibrilador.

Donde coinciden mucha necesidad y poca cercanía está la **prioridad de intervención**. Sobre esa base, la herramienta propone **dónde abrir o ampliar** el siguiente servicio y mide cuántas personas vulnerables más se alcanzan priorizando por sección que priorizando por la media de la zona. Justo cuando se prepara el PIR 2027-2031.

## 2. El problema

- **Las medias esconden los huecos.** Un municipio puede tener buena renta media y buenos servicios en el centro y, a la vez, barrios, urbanizaciones o pedanías donde un mayor no llega a pie a nada. Es el riesgo que la idea 10 ya señalaba de su propio índice: priorizar con la media municipal no ve a esas personas.
- **El acceso se mide sin mirar quién lo necesita.** Un centro de salud a 15 minutos no significa lo mismo para alguien de 30 años que para alguien de 80 en una calle con cuestas. Y una parada sin autobuses en hora punta no da acceso aunque esté en la puerta.
- **La inversión regional se reparte con criterios agregados.** El PIR 2022-2026 es un fondo de cooperación de 1.000 M€. De ellos, unos 650 M€ se asignan por municipio en su Plan de Actuación (BOCM de 22/10/2021) a los 178 municipios salvo la capital, con un mínimo por municipio; el resto no se asigna por municipio (**verificar** las cifras). El reparto usa criterios municipales como la renta, el paro, la población o la dependencia territorial (Decreto 118/2020), con pesos que no se publican, y cada ayuntamiento propone sus obras. Nada de eso mide el acceso real a los servicios ni lo que pasa dentro de cada municipio.
- **Lo que existe se queda corto.** El Ayuntamiento tiene su índice de vulnerabilidad por barrio (IGUALA), pero solo para la capital y sin acceso a pie. No hay nada parecido publicado para toda la Comunidad.
- **Riesgo de repetir lo ya premiado.** *Desiertos de servicios* ganó la primera edición de DataMad. Un mapa de acceso a servicios sin más la repetiría; por eso la idea se apoya en lo que la media oculta, en los perfiles y en una decisión medible.

## 3. Por qué ahora

- El **PIR 2027-2031** (unos 1.100 M€) está en tramitación según una orden del BOCM del 14/08/2026.
- El **INE publicó el 19/10/2026** la renta de 2024 por sección censal.
- El **Consorcio de Transportes actualizó sus horarios** (GTFS) el 05/11/2026.

Hay una decisión pública abierta, con datos recién publicados para tomarla mejor.

## 4. Para quién y qué decisión cambia

| Usuario | Pregunta que responde | Decisión que cambia |
|---|---|---|
| **Ciudadanía y prensa** | «¿Qué tengo a 15 minutos y qué me falta?» · «¿Cómo está mi zona frente a mi municipio?» | Dónde reclamar un servicio; qué contar, y con qué datos, sobre el reparto |
| **Personal técnico de la Comunidad** (Administración Local, por el PIR; Familia y Servicios Sociales; Sanidad) | «¿Dónde se juntan vulnerabilidad y falta de acceso?» · «Con N centros, ¿dónde llegan a más personas vulnerables?» · «¿Recibe cada municipio en proporción a su necesidad?» | Un criterio adicional para el Plan de Actuación del PIR 2027-2031; dónde abrir o ampliar centros de salud, sociales o de día; dónde mejorar la frecuencia del transporte |
| **Personal técnico municipal** | «¿Qué secciones de mi municipio están peor y qué les falta?» | Qué obras proponer al PIR, con un informe por municipio |

La vista ciudadana es el gancho de la demo. La vista técnica es donde está el impacto, porque es la que puede cambiar una decisión pública.

### 4.1 Quién decide cada servicio

Cada servicio lo decide una administración distinta, con su propio instrumento. La herramienta propone dónde actuar, pero cada propuesta va dirigida a quien la puede tomar:

| Servicio | Quién decide | Instrumento |
|---|---|---|
| Servicios sociales, centros de mayores y de día, desfibriladores públicos, accesibilidad de calles, consultorios locales | Ayuntamientos, con financiación regional | **PIR** (obras que propone cada ayuntamiento) y presupuestos municipales |
| Centros de salud | Comunidad (Sanidad) | Planificación de atención primaria por zonas básicas de salud |
| Colegios públicos | Comunidad (Educación), con suelo municipal | Planificación educativa |
| Farmacias | Comunidad, por concurso | Planificación farmacéutica (ratios y distancias legales); la herramienta solo diagnostica |
| Frecuencia del transporte | Consorcio de Transportes | Planificación de la oferta |

El PIR se relaciona solo con la primera fila. Para el resto, la herramienta es un diagnóstico para quien planifica.

## 5. Cómo funciona para el usuario

Una sola web con dos pestañas que comparten mapa, datos y código. En la demo se pasa de una a otra sin cortes.

### 5.1 Pestaña ciudadana: «¿qué tengo cerca?»
1. **Dónde.** Pincha en el mapa, busca su calle en un buscador que funciona sin conexión o usa la geolocalización del navegador. La dirección nunca sale del navegador.
2. **Quién.** Elige un perfil: mayor de 65, familia con niños, movilidad reducida o población general.
3. **Resultado.** Ve qué servicios tiene a 15 minutos a pie y cuáles no, cuánto tarda a cada uno y si la parada más cercana tiene frecuencia de verdad.
4. **Contexto.** Ve cómo está su sección frente a su municipio o distrito y frente a la Comunidad, en percentiles, y un aviso si su zona es de «prioridad de intervención oculta».

Esta pestaña **no muestra rankings de secciones**, para no señalar barrios.

### 5.2 Pestaña técnica: «¿dónde actuar?»
1. **Capas:** necesidad por sección con su incertidumbre, vulnerabilidad oculta, acceso por servicio y perfil, doble penalización, índice de las 199 zonas y evolución de la renta 2015-2024.
2. **Índice de zonas:** mapa de las 199 zonas con sliders para cambiar los pesos y ver qué zonas cambian de prioridad.
3. **Auditoría:** necesidad frente a lo que recibió cada municipio del PIR 2022-2026 y, en la capital, frente a las obras de accesibilidad y las listas de espera.
4. **Simulador:** elige un servicio, un perfil y un objetivo; coloca un centro a mano (pincha y ve cuántas personas vulnerables gana acceso) o pide «sugerir N ubicaciones». Compara abrir centros nuevos con ampliar los existentes.
5. **Valor:** métricas en vivo y la curva que compara priorizar por sección con priorizar por la media de la zona o solo por población.
6. **Trabajo técnico:** rankings completos de secciones y zonas, dos escenarios guardados lado a lado y exportación a CSV o GeoJSON.

Cada cifra lleva su fuente y, si es una aproximación, una marca y una explicación.

## 6. El cálculo, paso a paso

Lo estable es **qué** se mide y **cómo encajan** las piezas. **Cómo** se calcula cada una es el enfoque de partida.

### 6.1 Las piezas y cómo encajan

```
Necesidad por sección ──agrega──▶ Necesidad media de la zona ──▶ Vulnerabilidad oculta (6.3)
        │
        ├──cruza con── Acceso a pie por perfil (6.5) ──▶ Doble penalización (6.6)
        │                                                        │
        │                                       Dónde actuar (6.7) ──▶ Valor del detalle por sección (6.8)
        │
Índice de las 199 zonas (6.4) ── contexto · auditoría del PIR (6.9) · validación
```

- **Sección censal:** la unidad estadística mínima del INE, de unos 1.000 a 2.500 habitantes. Hay unas 4.500 en la Comunidad (**verificar** la cifra exacta). Es la escala del detalle.
- **Zona:** los 179 municipios, con Madrid capital dividida en sus 21 distritos, en total **199 zonas**. Se divide la capital porque, como un solo municipio, aplastaría la escala y convertiría en «ocultas» todas sus secciones vulnerables. Además, así se puede comparar con IGUALA.

### 6.2 La necesidad por sección

Un índice de vulnerabilidad para cada sección, con datos que existen a esa escala:

| Variable | Fuente | Año |
|---|---|---|
| Renta por persona y por unidad de consumo; % con ingresos por debajo del 60 % de la mediana; Gini | INE, Atlas de Distribución de Renta (ADRH) | 2024 |
| Peso de las prestaciones por desempleo en los ingresos (aproxima el paro, que no existe por sección) | INE, ADRH | 2024 |
| Peso de las pensiones en los ingresos | INE, ADRH | 2024 |
| % de mayores de 65 y de 80; hogares unipersonales; tamaño del hogar | INE, ADRH (tabla 31105) y Padrón por sección | 2024–2025 |
| % de extranjeros | INE, Padrón por sección | 2025 |
| Nivel de estudios y régimen de tenencia | INE, Censo 2021 | 2021 |

**Cálculo de partida** (manual de indicadores compuestos de la OCDE y el JRC):
1. Tasas por habitante.
2. Recorte de extremos (*winsorize*) entre los percentiles 1 y 99, para que unas pocas secciones raras no dominen.
3. Normalización con z-score, que pone todas las variables en la misma escala.
4. Media aritmética con pesos iguales.

**Robustez.** No hay unos pesos «verdaderos», así que se repite el cálculo miles de veces con pesos al azar (Monte Carlo con pesos Dirichlet) y con agregación geométrica en lugar de aritmética. De ahí sale, para cada sección, un intervalo de su posición en el ranking. Una sección es **«vulnerable robusta»** si está en el quintil más vulnerable de la región en la mayoría de las simulaciones. Las correlaciones y un PCA se usan solo para detectar variables redundantes, no para fijar pesos.

**Variables delicadas.** El % de extranjeros se presenta como variable de composición, no como causa, y se publica el índice con y sin ella para que no se lea como un estigma. Cada variable va con su año: la renta de 2024 y el Censo de 2021 cambian despacio a escala de sección, y se declara como limitación.

**Secciones que cambian entre años.** Se fija una cartografía de referencia y se pasan los datos de otros años con la tabla de equivalencias del INE. Las secciones que no casan se cuentan y se declaran.

### 6.3 La vulnerabilidad oculta

Se usa **el mismo índice a dos escalas**, para que la comparación sea limpia:
- El índice de cada sección se agrega a su zona con la media ponderada por población.
- Los quintiles se calculan **ponderados por población**, tanto el de secciones como el de zonas: el quintil más vulnerable es el 20 % de la población, no el 20 % de las unidades.
- **Vulnerabilidad oculta** = secciones vulnerables robustas situadas en zonas cuya media, con su intervalo de Monte Carlo, no está en el quintil más vulnerable. Son las personas que una política basada en la media no ve.

Para cuantificarlo:
- **Descomposición de las diferencias.** La varianza del índice por sección se parte exactamente en una parte *entre* zonas y otra *dentro* de cada zona. Da el titular: «el X % de las diferencias de vulnerabilidad entre secciones está dentro de los municipios». Como contraste, el **índice de Theil** de la renta media por sección, que se descompone igual. Se dice «entre secciones» porque son medias de sección, no rentas de personas.
- **Población vulnerable en zonas «sanas»** y ranking de zonas con más dispersión interna.

**El tamaño de la zona.** Una zona con una sola sección no puede ocultar nada, y una con cientos casi seguro oculta algo. Para que lo oculto no sea solo un efecto del tamaño:
- los resultados se dan también por tramos de tamaño de zona (número de secciones);
- se compara con una **referencia nula**: se reparten las secciones al azar entre zonas del mismo tamaño muchas veces y se mira cuánta vulnerabilidad «oculta» saldría solo por azar. Lo que importa es cuánto supera el dato real a esa referencia.

### 6.4 El índice de las 199 zonas

Es la **vista municipal**, la escala a la que hoy se reparte la inversión regional. No reproduce los criterios del PIR (renta, paro, población, medio ambiente, patrimonio, ingresos, inmigración, entidades singulares y dependencia territorial, con pesos no publicados): es un índice de necesidad social con datos abiertos. Sirve de contexto, de medida de necesidad para la auditoría (6.9) y de pieza que se valida con IGUALA y con el índice por sección (8.1).

| Dimensión | Indicador de partida | Por qué |
|---|---|---|
| Económica | Paro registrado sobre la población de 16 a 64 años | Único dato de empleo fiable por municipio |
| Económica | Renta media por persona (ADRH 2024) | El mismo método para municipios, distritos y secciones |
| Salud y cuidados | Personas con discapacidad reconocida sobre la población | Mejor dato municipal de necesidad de cuidados (desde 2023) |
| Salud y cuidados | Grado de envejecimiento | Más mayores, más dependencia de los servicios cercanos |
| Salud y cuidados | Proporción de dependencia **demográfica** | Peso de menores y mayores frente a la población en edad de trabajar; **no** es la dependencia de la ley, que solo existe a nivel regional |
| Vivienda | % de viviendas vacías (Censo 2021) | Señal de abandono o de un parque desajustado |
| Vivienda | % de hogares en alquiler | Más exposición al coste de la vivienda |

- **Cálculo:** cada indicador se normaliza entre 0 y 1 sobre las 199 zonas, con más alto = más vulnerable; pesos iguales por dimensión e iguales dentro de cada una. En la web, los **sliders** permiten probar otros pesos y muestran cuánto cambian las 20 zonas más vulnerables.
- **Madrid capital:** para los distritos se usa el panel de indicadores del Ayuntamiento (paro, discapacidad, envejecimiento, dependencia, renta). Las viviendas vacías y el alquiler se calculan sumando las secciones del INE de cada distrito. Las diferencias de fecha o de definición se recogen en una tabla de equivalencias.
- **Relación con la necesidad por sección:** los dos índices **no se cruzan directamente**, porque usan variables distintas y mezclarlos confundiría lo que oculta la media con lo que se mide distinto. La vulnerabilidad oculta se calcula siempre con el índice por sección (6.3).
- **Lo que no entra:** la esperanza de vida (solo existe para municipios de más de 100.000 habitantes y distritos; se usa para validar), el valor tasado de la vivienda (solo para más de 25.000 habitantes; contexto), la energía total facturada (mezcla la industria con los hogares) y el consumo eléctrico bajo (ver 6.4.1).

#### 6.4.1 La energía, como contexto

El Censo 2021 publica las viviendas por tramo de consumo eléctrico. El % de viviendas ocupadas con consumo anómalamente bajo aproxima la **pobreza energética escondida**: hogares que consumen menos de lo que necesitan (concepto de la Estrategia Nacional contra la Pobreza Energética, **verificar** la cita). Pero los hogares pequeños, los eficientes y las segundas residencias también consumen poco. Por eso **no entra en el índice**: se muestra como capa de contexto, corregida por el tamaño medio del hogar, con el ranking de zonas con y sin ella. El umbral de «consumo bajo» está abierto.

### 6.5 El acceso a pie

**Qué es tener acceso:** llegar a un servicio dentro del umbral de tiempo, desde el propio edificio, a la velocidad de cada perfil y con la pendiente real.

| Perfil | Velocidad de partida | Servicios que importan |
|---|---|---|
| Mayores de 65 | Unos 3 km/h (alternativa: 3,5 km/h) | Centro de salud, farmacia, servicios sociales, centro de mayores o de día, parada con frecuencia, desfibrilador |
| Familias con niños | Unos 4 km/h | Colegio, centro de salud con pediatría, zona verde, parada con frecuencia |
| Población general | Unos 4,8 km/h | Todos, con resultados por **quintil de renta** (la medición original de la idea 3) |
| Movilidad reducida | Unos 2,5 km/h y más penalización por pendiente | Como mayores, más instalaciones accesibles (en la capital) |

**Umbrales de partida:**

| Servicio | Urbano e intermedio | Rural |
|---|---|---|
| Desfibrilador de acceso público | 3–4 min a pie (unos 300 m) | Igual |
| Parada con frecuencia | 5 min a pie | 10 min a pie |
| Colegio, centro de salud y demás | 15 min a pie | 15 min a pie, informando además del tiempo en coche |

El tipo de territorio (urbano, intermedio, rural) sale de la clasificación DEGURBA por municipio. En la web se pueden probar otros umbrales (10, 15 o 20 minutos).

**Cómo se calcula (una forma de hacerlo):**
- **Desde dónde:** desde los **edificios residenciales del Catastro**, cada uno con su número de viviendas. La población de cada sección, por edad, se reparte entre sus edificios en proporción a las viviendas. Medir desde el centro de la sección engañaría en las secciones rurales, que miden kilómetros. En zonas rurales sin buen dato de edificios, la rejilla de 1 km del INE sirve de respaldo. Para el cálculo, los edificios se agrupan en puntos de origen de unos 100 m.
- **Por dónde:** la red de calles de OpenStreetMap. En el medio rural se asume que toda la red es transitable y se dice.
- **Pendiente:** con el modelo digital del terreno del IGN se calcula la pendiente de cada tramo. La **función de Tobler**, una fórmula clásica que reduce la velocidad al caminar según la pendiente, ajusta el tiempo de cada tramo, con más penalización para la movilidad reducida.
- **Transporte:** una parada solo cuenta si tiene **frecuencia suficiente**, por ejemplo 4 o más salidas por hora entre las 7 y las 9 de un día laborable, según el GTFS del Consorcio. Además se calcula el **acceso combinando caminar y transporte según la hora**, para responder a «¿y si no puedo ir andando?».
- **Herramientas candidatas:** pandana u OSMnx para la red a pie, r5py para la parte multimodal.
- **Sin modelos de capacidad** (como 2SFCA): no hay datos abiertos de cupos ni plazas por centro.

**El centro que corresponde, no el más cercano.** A cada vecino le corresponde el centro de salud de su zona básica de salud, que puede no ser el más cercano. Si la zonificación sanitaria está publicada en abierto (**verificar**), el acceso al centro de salud se mide al centro asignado; si no, al más cercano, y se declara. Lo mismo con los colegios, donde la cercanía es solo uno de los criterios de admisión.

**Qué produce:**
- Para cada punto de origen, perfil y servicio, el tiempo al servicio que corresponde (o al más cercano) y si cumple el umbral.
- Agregado a sección y a zona: el % de población de cada perfil sin acceso.
- La **equidad del acceso**: el % sin acceso por quintil de renta y por edad, con un **índice de concentración** (mide si la falta de acceso se acumula en los más pobres) y su intervalo de confianza por *bootstrap*. Sirve de línea base para seguirla cada año.

### 6.6 La doble penalización

El cruce central: secciones **vulnerables robustas y sin acceso** a uno o varios servicios, para cada perfil. Es el mapa principal de la propuesta. Se cuenta además cuántas de esas secciones están en zonas que la media no señala, que es donde se juntan los dos hallazgos.

### 6.7 Dónde actuar

**Candidatos de partida, en dos escenarios:**
- **Abrir uno nuevo:** una rejilla de unos 250 m sobre suelo urbano, marcando si hay suelo público dotacional cerca (Portal del Suelo). Pinchar en el mapa se ajusta a la celda más cercana.
- **Ampliar uno existente:** los equipamientos actuales, por ejemplo añadir atención social a un centro de mayores. Suele ser más barato y más rápido.

Cada propuesta se etiqueta con quién la puede tomar (tabla de 4.1). Las de servicios municipales son candidatas a obras del PIR; las de centros de salud y colegios, un diagnóstico para la planificación de la Comunidad. Las farmacias no se ubican: su apertura sigue la planificación farmacéutica, así que para ellas la herramienta solo diagnostica.

**Dos objetivos, a elegir:**
1. **Ponderado:** cada persona sin acceso cuenta según la puntuación de vulnerabilidad de su sección.
2. **Personas vulnerables:** solo cuenta la población del quintil más vulnerable. Da frases como «N personas vulnerables más con acceso».

**Método:** un algoritmo **voraz de cobertura máxima**. Elige primero el sitio que da acceso a más demanda que hoy no lo tiene, luego el siguiente, y así hasta N. Para este tipo de problema, el voraz garantiza al menos el 63 % del óptimo. La ganancia se calcula por punto de origen, no por sección: solo cuenta la población que hoy no tiene acceso.

**Precálculo:** los tiempos reales por la red de cada candidato a cada punto de origen se calculan en Python y se guardan solo los pares dentro del umbral. Estimación de partida: unos 16.000 candidatos por unos 60.000 puntos de origen, en ficheros por servicio y perfil que la web carga bajo demanda (**verificar** el tamaño real en una prueba). Si no cabe en una web estática, la alternativa es la distancia en línea recta calculada en el navegador, declarándolo.

### 6.8 El valor: cuánto se pierde priorizando con la media

Es la prueba de que la idea mejora una decisión, no solo un mapa. No se compara con un rival inventado: se mide **el valor de la información**. El método de ubicación es siempre el mismo (el voraz de 6.7, con el mismo N y los mismos candidatos) y solo cambia lo que se sabe de la necesidad:
- **(a) Solo población:** se ignora la necesidad y se cubre a quien más gente sin acceso tiene cerca.
- **(b) Media de la zona:** cada persona recibe la puntuación media de su municipio o distrito. Es lo que se puede hacer hoy con datos municipales.
- **(c) Sección:** cada persona recibe la puntuación de su sección. Es lo que propone Cerca.

Las tres se evalúan con la misma medida: personas vulnerables (según la sección) que ganan acceso.
- **Resultado:** una curva de personas vulnerables alcanzadas frente a N para cada nivel de información.
- **Lectura honesta:** (c) gana por definición, porque usa la información con la que se evalúa. Lo que importa es **cuánto**: la distancia entre (b) y (c) es la tesis «la media esconde» convertida en cifra («con los mismos N centros, priorizar con la media deja fuera a X personas vulnerables»). Si la distancia es pequeña, también es un resultado y se dice.
- **Ventaja:** funciona igual en la capital (con distritos) y en el resto de la región, y no depende de cómo se reparte el PIR.
- Se dice «llegaría», no «ha llegado»: ninguna estimación se presenta como impacto medido.

### 6.9 La auditoría: ¿recibe cada municipio en proporción a su necesidad?

- **Escala regional.** Se compara la necesidad con la asignación por municipio del PIR 2022-2026, por habitante, tomada de la tabla del Plan de Actuación (BOCM de 22/10/2021), que reparte unos 650 M€ entre los 178 municipios (**verificar**). Es contexto descriptivo, no una prueba de que el PIR esté mal hecho: el PIR tiene un mínimo por municipio, parte va a gasto corriente y cada ayuntamiento elige sus obras.
  - La **brecha** es la posición en el ranking de necesidad menos la posición en el ranking de asignación: una brecha grande y positiva señala mucha necesidad con poca asignación. Se presenta con un diagrama de dispersión y un mapa.
  - La necesidad se mide con el índice de las 199 zonas y, como contraste, con el índice por sección agregado a cada municipio.
  - Las **altas** del PIR publicadas en el BOCM, si da tiempo a extraerlas, son una capa opcional sobre **en qué** se gastó, no sobre cuánto recibió cada municipio.
  - Las **transferencias de capital** y el **gasto municipal en protección social** de los presupuestos liquidados quedan como contraste, sabiendo que mezclan fuentes y que les faltan 2022 y 2023 (y 2022 al gasto social).
- **Escala de la capital.**
  - Las **obras de accesibilidad en aceras** (2020, 2021 y 2024) por distrito, frente a los mayores y las personas con movilidad reducida sin acceso.
  - Los equipamientos por habitante y las **listas de espera** de centros de día y residencias, que el Ayuntamiento publica a diario.
- **Tono:** dónde actuar, no a quién culpar. Los huecos de transporte se presentan como oportunidades de mejora, también por la licencia del CRTM (sección 13).

### 6.10 La evolución en el tiempo

La accesibilidad es una foto actual; la serie está en la necesidad. Con las variables del ADRH que tienen serie desde 2015 se calcula un **subíndice de renta 2015-2024** por sección y se señalan las secciones que han mejorado o empeorado. No se mezcla con el índice completo.

## 7. Escenarios «¿y si…?»

Responden a decisiones concretas y son la parte que más se presta a la demo en directo:
- **Pesos distintos** en el índice de zonas: ¿qué zonas cambian de prioridad?
- **N centros nuevos o ampliados** de un tipo de servicio: ¿a cuántas personas vulnerables más se llega?
- **Abrir frente a ampliar:** ¿qué cubre cada opción?
- **Otro perfil u otro umbral** (10, 15 o 20 minutos): ¿cómo cambia el mapa?
- **Más frecuencia en una línea:** ¿cuántas paradas pasan a dar acceso? (**verificar** si es viable con el GTFS).

No hay capa predictiva.

## 8. Validación

### 8.1 ¿El índice mide lo que dice? (validación externa)
- **Esperanza de vida:** un índice de vulnerabilidad bien hecho debería ir en dirección contraria. Hay unos 31 puntos de comparación: los municipios de más de 100.000 habitantes y los 21 distritos.
- **Concordancia con IGUALA:** el ranking de los 21 distritos se compara con el del Ayuntamiento mediante la **correlación de Spearman**, que mide si dos rankings ordenan igual. El índice por sección se compara además, por solapamiento espacial, con el índice por barrios del Ayuntamiento. Si no coinciden, se explica por qué.
- **Prueba temporal:** ¿el índice con datos de 2019 anticipaba el empeoramiento del paro o del envejecimiento hasta 2024? Se hace sin la discapacidad, que solo existe desde 2023.
- **Fuera de la capital:** casi toda la validación anterior está en Madrid (21 de los 31 puntos de esperanza de vida, e IGUALA entera), que no entra en el PIR. Para el resto de la región se compara el índice por sección agregado a cada municipio con el índice de las 199 zonas en los 178 municipios (Spearman). Los dos índices usan variables distintas, así que si ordenan parecido es una señal de que miden lo mismo (validez convergente), sin mezclarlos.

Se informa de cada correlación y su signo, también cuando no sale la esperada.

### 8.2 ¿El dato es fiable?
- **Sensibilidad:** intervalos de ranking del Monte Carlo (sección) y sliders (zonas).
- **Tiempos a pie contrastados** con un planificador de rutas conocido en una muestra de trayectos.
- **Cobertura de los cruces:** secciones que no casan entre versiones, edificios sin viviendas y centros sin coordenadas, contados y declarados.
- **Pruebas de referencia:** Python genera casos con resultado conocido (cobertura, voraz, índice de concentración) y la web tiene que reproducirlos.

## 9. Lenguaje y estigma

- En la interfaz se habla de **«prioridad de intervención»**, no de «barrio vulnerable».
- Se muestra la incertidumbre (intervalo de ranking) junto a cada posición.
- La pestaña ciudadana no muestra rankings de secciones; los rankings completos están en la pestaña técnica y en el informe, así que se pueden enseñar en la presentación.
- En una web estática no hay control de acceso: la separación entre pestañas es de diseño, no de seguridad. No es un problema, porque todo deriva de datos abiertos.

## 10. IA y apertura

- **Servidor MCP** (el protocolo con el que un asistente de IA usa herramientas externas, visto en la formación de DataMad). Lee las mismas tablas precalculadas y siempre calcula lo mismo. Herramientas de partida:
  - `acceso_desde(lat, lon, perfil)`;
  - `indicadores_seccion(codigo)`;
  - `vulnerabilidad_oculta(zona)`;
  - `sugerir_ubicaciones(servicio, n, objetivo)`.

  Cualquier asistente puede preguntar «¿qué le falta a un mayor en tal sección?» y recibir cifras calculadas con su fuente. En la demo se usa desde Claude.
- **Smart Data Models:** se reutilizan los modelos existentes de puntos de servicio y los de *UrbanMobility* para GTFS, publicados en NGSI-LD. Para el indicador de acceso y vulnerabilidad por sección se parte del modelo existente más cercano y, si no basta, se **propone una extensión o un esquema nuevo**, explicando qué le falta al existente. Clave de cruce: código INE de sección y de municipio más el año.
- **Datos abiertos:** los resultados por sección y zona se publican en CSV y GeoParquet con CC BY 4.0, para consultarlos por URL o proponerlos al catálogo regional.
- **Entregables:** web publicada, repositorio con licencia libre que regenera todo desde las fuentes oficiales, conjunto de datos, informe de análisis y nota metodológica con supuestos, límites y validación.

## 11. Encaje con los criterios de DataMad

| Criterio | Cómo lo cumple |
|---|---|
| **Uso de la información pública regional** (oficial) | El núcleo usa el catálogo regional (paro, discapacidad, envejecimiento, dependencia, Censo 2021, centros sanitarios, farmacias, centros sociales y educativos, desfibriladores, GTFS del Consorcio, presupuestos) y el Plan de Actuación del PIR. Lo completan el portal del Ayuntamiento (distritos, IGUALA, servicios municipales, aceras, listas de espera) y fuentes nacionales abiertas (INE, Catastro, IGN, OSM) |
| **Viabilidad** (oficial) | Fuentes identificadas una a una, con su identificador y lo pendiente de comprobar marcado; web sin servidor, pipeline reproducible y construcción por capas que siempre deja una demo funcionando (sección 14) |
| **Código abierto** (oficial) | Repositorio con licencia libre, librerías abiertas, datos CC BY 4.0, MCP y un esquema propuesto a Smart Data Models |
| **Valor económico, social o medioambiental** (citado por la URJC y la prensa) | Responde a una decisión real y actual (el PIR 2027-2031), propone dónde actuar, dirigido a quien puede decidirlo, y mide cuántas personas vulnerables se dejan fuera al priorizar con la media |

**Jurado relevante:** Alberto Abella (Smart Data Models, APIs, MCP y espacios de datos) y Olga Quirós (ASEDIE: economía del dato y reutilización).

**En qué se diferencia de proyectos ya premiados:**
- *Desiertos de servicios* (primera edición de DataMad) mapea el acceso; Cerca lo cruza con la necesidad por sección, muestra lo que oculta la media y propone dónde actuar.
- *Ciudades de quince minutos para la infancia* (UPCT, Madrid 2025) mide un solo colectivo.
- *Rampa* y *AccesibiliMad* (Madrid 2025) calculan rutas accesibles o miran servicios por zona, sin cruzarlos con la vulnerabilidad ni con la inversión.
- *Flowcation* (GovHack 2025) trabaja la equidad del acceso, pero no propone dónde actuar.

## 12. Datos

### 12.1 Catálogo regional (datos.comunidad.madrid, CKAN, CC BY 4.0) · obligatorio
| Conjunto | Qué aporta | Límite |
|---|---|---|
| `302038` | Paro registrado por municipio | Dato a 31 de marzo; 2006–2026 |
| `irpf_indicador_renta` | Renta disponible bruta municipal | 2015–2024; alternativa al ADRH |
| `personas_discapacidad_por_tipo_y_sexo` | Discapacidad reconocida por municipio | Solo 2023–2025 |
| `grado_envejecimiento_por_edad` | Envejecimiento por municipio | 1996–2025 |
| `1930729` | Proporción de dependencia demográfica | No es la dependencia de la ley |
| `censo_2021_viviendas_por_consumo_electrico` | Viviendas vacías y por tramo de consumo | Solo 2021 |
| `censo_2021_porcentaje_viviendas_familiares_por_tenencia` | % en propiedad, alquiler y otros | Solo 2021 |
| `centros_servicios_establecimientos_sanitarios` | 422 centros públicos de atención primaria (272 centros de salud y 150 consultorios), 414 con coordenadas; 311 con pediatría | Una fila por centro y servicio; coordenadas UTM |
| `oficinas_farmacia` | 2.957 farmacias con coordenadas | Coordenadas UTM |
| `atencion_social_registro_centros` | Centros de atención social | **Verificar** las coordenadas |
| `centros_educativos` | Centros educativos | Filtrar por nivel y titularidad |
| `desfibriladores` | Unos 13.700 desfibriladores | Excluye el ámbito sanitario; separar los de acceso público |
| GTFS del CRTM (6 redes) | Paradas, líneas y horarios | Metro del 30/05/2025; los demás, del 05/11/2026 |
| `presu_liq_ingresos`, `presu_liq_gastos` | Transferencias de capital y gasto social por municipio | Faltan 2022–2023 (transferencias) y 2022 (gasto social) |
| `esperanza_vida_municipios_mayores_100000_hab_por_sexo` | Validación | Solo unos 10 municipios |
| `parcelas_portal_suelo` | Marca de suelo público | 527 parcelas en 49 municipios, unas 40 dotacionales |

### 12.2 Portal del Ayuntamiento (datos.madrid.es, CKAN, CC BY 4.0) · capa de la capital y validación
| Conjunto | Qué aporta |
|---|---|
| `300087-0-indicadores-distritos` | Indicadores por distrito y barrio (2019–2026): paro, discapacidad, envejecimiento, dependencia, renta, esperanza de vida |
| `200076-0-padron` | Padrón mensual por sección, edad y sexo |
| `300577-0-iguala-vulnerabilidad`, `300301-0-ranking-vulnerabilidad` | Índice de vulnerabilidad del Ayuntamiento, para validar |
| `201544-0-centros-salud`, `209094-0-centros-servicios-sociales`, `200337-0-centros-mayores`, `200342-0-centros-dia`, `202311-0-colegios-publicos` | Servicios municipales con coordenadas |
| `900023-0-emt-paradas-autobus`, `208327-0-transporte-bicicletas-bicimad` | Transporte de la capital |
| `202162-0-instalaciones-accesibles-municip` | Instalaciones accesibles, para el perfil de movilidad reducida |
| `300714-0`, `300608-0`, `300625-0` | Obras de accesibilidad en aceras de 2024, 2021 y 2020 |
| `300620`, `300621`, `300622`, `300623` | Listas de espera diarias de residencias y centros de día |
| `300153-0-zonas-verdes-inventario` | Zonas verdes |

### 12.3 Fuentes nacionales y otras
| Fuente | Qué aporta | Estado |
|---|---|---|
| **INE, ADRH 2024** | Renta e indicadores demográficos por sección, distrito y municipio (tabla 31105); serie desde 2015 | Publicado el 19/10/2026; **verificar** el id de la tabla de renta |
| **INE, Padrón continuo por sección** | Edad y nacionalidad | **Verificar** el último año publicado |
| **INE, Censo 2021 por sección** | Estudios y tenencia | Solo 2021 |
| **INE, cartografía y tabla de equivalencias de secciones** | Geometrías y paso entre años | **Verificar** la tabla de equivalencias |
| **Catastro INSPIRE, edificios** | Cada edificio con su número de viviendas y su uso; 179 ficheros | Madrid usa el código 28900 en el Catastro y 28079 en el INE; **verificar** la licencia |
| **IGN/CNIG, modelo digital del terreno** | Elevación para la pendiente | Por descargar |
| **OpenStreetMap** (Geofabrik) | Red peatonal | ODbL: citar «© OpenStreetMap contributors» |
| **BOCM, Plan de Actuación del PIR 2022-2026** (22/10/2021) | Asignación por municipio en una sola tabla | **Verificar** las cifras (unos 650 M€ de 1.000 M€, 178 municipios) |
| **BOCM, altas del PIR 2022-2026** | En qué se gastó cada municipio | Opcional; repartidas en muchas órdenes |
| **Zonificación sanitaria** (zonas básicas de salud) | Centro de salud asignado a cada vecino | **Verificar** si está publicada en abierto |
| **DEGURBA** | Tipo de territorio por municipio | Disponible |
| **CartoCiudad o Catastro, callejero** | Buscador de calles sin conexión | **Verificar** la licencia y el tamaño |

### 12.4 Descartados
- `1003254` (% de viviendas vacías): es de 2001.
- `energia_electrica_facturada`: mezcla la industria con los hogares.
- `1914361` (dependencia de la ley) y `1932366` (bono social): solo existen a nivel regional.
- Atlas de Vulnerabilidad Urbana del Ministerio: no hay versión con el Censo 2021.
- Portal del Suelo como lista de candidatos: sesgado hacia municipios ricos (ver Anexo B).

## 13. Arquitectura (propuesta)

Lo importante es que la demo no dependa de un servidor y que todo sea reproducible y abierto.
- **Pipeline en Python**, sin conexión y reproducible (con DuckDB y su extensión espacial o geopandas): descarga las fuentes, construye las tablas de paso entre secciones, municipios y códigos del Catastro, y calcula los índices con sus intervalos, los tiempos de acceso, las matrices de ubicación, la auditoría, la curva de valor, los polígonos simplificados y el índice de calles.
- **Web estática** con MapLibre y teselas PMTiles, por ejemplo en GitHub Pages, sin peticiones a terceros y con las librerías en el repositorio. El navegador solo consulta, suma, ejecuta el voraz sobre las matrices precalculadas, recalcula el índice de zonas con los sliders (son 199 filas) y pinta. Los ficheros pesados se cargan por municipio bajo demanda.
- **Seguridad:** validación estricta de entradas; ninguna entrada se inserta como HTML.
- **MCP:** un servicio aparte, en Python, que lee las mismas tablas; la web no depende de él.
- **Licencias:**
  - Código MIT. Datos derivados CC BY 4.0; los derivados de OSM, ODbL.
  - **CRTM:** obliga a citarlo como «datos explotados», mostrar «Powered by CRTM» con enlace, conservar la fecha y no insinuar su respaldo. No se republica el GTFS en bruto. Prohíbe «menoscabar su imagen», por eso los huecos de transporte se presentan como oportunidades de mejora.
  - **Verificar** las licencias del Catastro y de CartoCiudad.
- **Privacidad:** solo datos agregados. El reparto de la población entre edificios es una estimación estadística y no se publica por edificio. La dirección o la ubicación del usuario no salen del navegador.

## 14. Cómo afrontarlo

**Orden por capas**, para que siempre haya algo que enseñar:
1. Necesidad por sección, índice de las 199 zonas y su mapa.
2. Vulnerabilidad oculta: descomposición, referencia nula por tamaño y titular.
3. Acceso con un perfil y un servicio, en la capital y en un municipio rural.
4. Los cuatro perfiles, todos los servicios, la pendiente y la frecuencia en toda la Comunidad; doble penalización y equidad por renta.
5. Dónde actuar: abrir y ampliar, con los dos objetivos, y la curva de valor de la información.
6. Auditoría con el Plan de Actuación del PIR.
7. Validación (incluida la de fuera de la capital), evolución 2015-2024 y capa de auditoría de la capital.
8. Acceso multimodal por hora.
9. MCP, Smart Data Models, informe y nota metodológica.

**Qué se congela el 22/11 sí o sí:** ADRH, Padrón y Censo por sección; cartografía y tabla de equivalencias de secciones; edificios del Catastro; red de OSM; los conjuntos de servicios del catálogo regional y del Ayuntamiento; GTFS; los indicadores municipales y de distrito; y el Plan de Actuación del PIR. El modelo del terreno del IGN, si se mantiene la pendiente.

**Qué cae primero si el cálculo no llega a tiempo**, en este orden: el acceso multimodal, la pendiente (se usa velocidad fija por perfil y se declara), los perfiles de movilidad reducida y familias, y por último el cálculo en toda la región (se queda en la capital y una muestra de municipios). El índice por sección, la vulnerabilidad oculta y la curva de valor no caen.

**Relato de la presentación** (orientativo, a cerrar cuando se conozca el formato):
1. El titular: «el X % de las diferencias de vulnerabilidad entre secciones está dentro de los municipios».
2. Un caso concreto: una sección de prioridad oculta vista desde la pestaña ciudadana, con un perfil de mayor y una calle con cuesta.
3. El simulador: sugerir N ubicaciones y la curva «priorizar con la media deja fuera a X personas vulnerables».
4. La parte técnica: datos regionales, Smart Data Models, código abierto y MCP.
5. Los límites, dichos por iniciativa propia.

El producto puede ser grande; el relato tiene que ser estrecho. El resto se enseña si el jurado pregunta.

## 15. Riesgos, límites y verificaciones

### Riesgos y límites
| Riesgo o límite | Mitigación |
|---|---|
| Congelación de datos el 22/11 y tiempo de cálculo (matrices de r5py para toda la región con 4 perfiles, pendiente y multimodal; 179 ficheros del Catastro) | Medir con un municipio de prueba; lanzar pronto el cálculo completo; guardar por municipio y procesar en lotes |
| Duración de la presentación | Relato estrecho (sección 14); capas extra solo si preguntan |
| Muchas cifras que defender | Cada cifra visible pasa por `dm-trazador-cifras`; lo espacial, por `dm-revisor-espacial` |
| Peso de la web estática | Carga por municipio bajo demanda; menos combinaciones en la vista ciudadana si hace falta; alternativa en línea recta |
| La curva de valor gana por definición | Se dice abiertamente; lo que se presenta es la magnitud de la diferencia entre media y sección (6.8) |
| Lo oculto como efecto del tamaño de la zona | Quintiles ponderados por población, resultados por tamaño y referencia nula (6.3) |
| Auditoría del PIR leída como acusación | Es contexto descriptivo; se declaran el mínimo por municipio, el gasto corriente y que cada ayuntamiento elige sus obras (6.9) |
| Propuestas dirigidas a quien no decide | Cada propuesta se etiqueta con su decisor e instrumento (4.1) |
| Centro de salud asignado frente al más cercano | Zonificación sanitaria si está en abierto; si no, se declara (6.5) |
| Indicadores de distrito no idénticos a los municipales | Tabla de equivalencias y marca en los datos aproximados |
| Versiones distintas de las secciones | Tablas de paso; documentar las que no casan |
| Datos de distinta antigüedad (Censo 2021, renta 2024) | Cada variable con su año; se declara como limitación |
| Proxies imperfectos (paro por sección, movilidad reducida) | Avisos visibles y sensibilidad |
| Lectura estigmatizante | Lenguaje de prioridad, incertidumbre visible, sin rankings en la vista ciudadana, índice con y sin extranjeros |
| Lectura de la auditoría como ataque | Tono de mejora: dónde actuar, no a quién culpar |
| GTFS de metro de mayo de 2025 | Comprobar que su calendario siga vigente; si no, frecuencia estimada y marcada |

### Verificaciones pendientes
- [x] Pasar esta ficha por `dm-abogado-del-diablo` (14/11: NO APTO; correcciones aplicadas en esta versión, ver B.3). Repetir la revisión sobre esta versión.
- [ ] Plan de Actuación del PIR 2022-2026 como fuente (`dm-verificador-fuentes`) y las cifras de 1.000 y 650 M€ (`dm-trazador-cifras`).
- [ ] Zonificación sanitaria (zonas básicas de salud) en abierto.
- [ ] Prueba de r5py en un municipio metropolitano, con pendiente y multimodal: tiempo de cálculo, tamaño de los ficheros y si r5py admite la pendiente (si no, pandana u OSMnx con los tiempos de Tobler).
- [ ] Ninguna fuente está descargada todavía: empezar por la lista de lo que se congela sí o sí (sección 14).
- [ ] Id de la tabla de renta del ADRH por sección (API del INE, operación 353) y último año del Padrón por sección.
- [ ] Tabla de equivalencias de secciones del INE entre años y número exacto de secciones.
- [ ] Licencias del Catastro INSPIRE y de CartoCiudad; tamaño del índice de calles.
- [ ] Coordenadas de `atencion_social_registro_centros`.
- [ ] Vigencia del calendario del GTFS de metro.
- [ ] Umbral de «consumo eléctrico anómalamente bajo» y cita de la Estrategia Nacional contra la Pobreza Energética.
- [ ] Esquemas existentes de Smart Data Models antes de proponer uno nuevo (carpeta `pysmartdatamodels/` del repositorio de la organización).
- [ ] Índice por barrios del Ayuntamiento: geometrías para la concordancia por solapamiento.
- [ ] Confirmar con la organización los pesos de los criterios, el formato de entrega y la duración de la presentación.
- [ ] Anotar la idea elegida en `docs/decisiones.md`.

---

## Anexo A: origen de la ficha

Las dos versiones compartían el esqueleto técnico (sección censal, edificios del Catastro, red de OSM, rejilla de candidatos, voraz de cobertura máxima, web estática, MCP y dos vistas) y se complementaban:

| | Plan de Izan | Ficha de Yeray («Cerca») |
|---|---|---|
| **Aportó** | Necesidad por sección separada del acceso; vulnerabilidad oculta con Theil; robustez con Monte Carlo; índice de concentración; curva contrafactual; Smart Data Models; lenguaje sin estigma; pruebas de referencia | Decisión real (PIR 2027-2031) y por qué ahora; 199 zonas con la capital en distritos; datos regionales y del Ayuntamiento comprobados; perfiles, pendiente y frecuencia; abrir frente a ampliar; auditoría; validación con IGUALA y prueba temporal |
| **Flojeaba en** | Sin decisión pública concreta; Madrid como un solo municipio (hallazgo trivial); poco dato regional en el núcleo; datos sin actualizar (renta ≈2023, Atlas de Vulnerabilidad Urbana); paradas sin frecuencia | Acceso dentro del índice (circularidad); sin necesidad por sección, así que «la media esconde» se quedaba sin cifra; auditoría frágil (transferencias de capital); energía ambigua; sin Smart Data Models; sensibilidad débil |

La comparación completa, desde la visión del jurado, está en el historial de este fichero (PR #50 y #52).

## Anexo B: registro de decisiones

Recoge lo que se acordó como punto de partida en cada momento. No es un compromiso cerrado: si el desarrollo lo pide, se revisa y se anota aquí.

### B.1 Entrevista de la ficha «Cerca» (Yeray, 12/11/2026)

| Ronda | Pregunta | Respuesta | Alternativas descartadas | Estado en esta ficha |
|---|---|---|---|---|
| 0 | Requisitos | Solo datos abiertos; usar al menos el portal del Ayuntamiento; buscar fuentes más allá del documento de contexto | — | Se mantiene |
| 1 | Fusión de las ideas 10 y 3 | Dos escalas conectadas | Solo escala urbana · el acceso como componente único | Se mantiene |
| 1 | Decisión que mejorar | Ubicar servicios + auditoría, en secuencia | Solo el PIR · solo ubicar | Se mantiene, con la curva de valor de la información y la auditoría con el Plan de Actuación del PIR |
| 1 | Servicios | Salud, cuidados y social, educación, transporte y desfibriladores | — | Se mantiene |
| 1 | Población | Varios perfiles | Un único perfil | Se mantiene |
| 2 | Alcance urbano | Toda la Comunidad + capa del Ayuntamiento | Solo la capital · la capital y dos pilotos | Se mantiene |
| 2 | Perfiles | Mayores, familias, población general y movilidad reducida | — | Se mantiene |
| 2 | Cómo ubicar | Cobertura en las parcelas del Portal del Suelo | Ranking de huecos · optimización completa | Cambiado en la ronda 3 |
| 2 | Pesos | Iguales + sliders | PCA · criterios del PIR | Se mantiene en zonas; en secciones se añade Monte Carlo |
| 3 | Candidatos, tras ver el sesgo del Portal del Suelo (527 parcelas en 49 municipios, unas 40 dotacionales, concentradas en municipios ricos) | Abrir en zona óptima con marca de suelo y ampliar equipamientos | Solo uno de los dos | Se mantiene |
| 3 | Madrid capital en el índice | 21 distritos, validados con IGUALA | Un solo municipio · fuera | Se mantiene |
| 3 | Energía | Buscar una fuente doméstica; si no hay, fuera | Incluir la energía total | Ver ronda 7 |
| 3 | Entregable | Web estática + datos abiertos; IA si da tiempo | Streamlit · web + asistente desde el principio | Se mantiene |
| 4 | Reparto actual | Presupuestos liquidados; PIR del BOCM si da tiempo | Solo presupuestos · solo el BOCM | **Cambia:** la base es la tabla del Plan de Actuación del PIR; las altas del BOCM, opcionales; los presupuestos, contraste (B.3) |
| 4 | Validación | Esperanza de vida, IGUALA, prueba temporal | — | Se mantiene, más sensibilidad y tiempos contrastados |
| 4 | Acceso en el índice | Sí, como dimensión | Matriz 2×2 separada · ambas | **Cambia:** separado, por circularidad (B.3) |
| 4 | Usuario | Ciudadanía y prensa + personal técnico de la Comunidad | Personal técnico municipal | **Cambia:** se añade el personal técnico municipal, que es quien propone las obras del PIR (B.3) |
| 5 | Desde dónde medir | Edificios del Catastro | Centroide de la sección · rejilla | Se mantiene |
| 5 | Transporte | Parada con frecuencia; multimodal si es viable | Solo la parada | Se mantiene, con el multimodal dentro |
| 5 | Pendiente | Tobler; las aceras pasan a la auditoría | Velocidad fija | Se mantiene |
| 5 | Forma de la IA | MCP + chat sencillo | Explicaciones generadas · sin IA | **Cambia:** solo MCP (B.3) |
| 6 | Mínimo imprescindible | Todo, afrontado por capas | — | Se mantiene |
| 6 | Nombre | Cerca | «¿Llega?» · «Mapa de la Equidad» | Se mantiene |
| 7 | Energía, tras encontrar el Censo 2021 | Entra con peso bajo | Solo contexto | **Cambia:** solo contexto (B.3) |

### B.2 Fases del plan de Izan (11/11/2026)

| Fase | Decisión | Estado en esta ficha |
|---|---|---|
| 1. Enfoque | Eje «vulnerabilidad oculta + dónde intervenir», para no repetir *Desiertos de servicios* | Se mantiene como núcleo |
| 1. Enfoque | Métrica de acceso por quintil de renta y por edad | Se mantiene |
| 1. Enfoque | Accesibilidad en transporte por hora (GTFS) como ampliación | **Cambia:** entra en el alcance |
| 1. Enfoque | Dos vistas (Administración y ciudadanía) | Se mantiene |
| 2. Datos | Necesidad por sección con ADRH, Padrón y Censo; % de extranjeros con sensibilidad | Se mantiene, con la renta de 2024 |
| 2. Datos | Índice municipal solo con variables de cobertura completa; energía fuera | Se mantiene, ampliado a 199 zonas con vivienda |
| 2. Datos | Puntos de origen en edificios del Catastro; rejilla de 1 km de respaldo | Se mantiene |
| 3. Modelo | Mismo índice a dos escalas; el índice municipal solo como contexto, sin cruce directo | Se mantiene |
| 3. Modelo | OCDE/JRC: winsorize, z-score, media con pesos iguales, Monte Carlo | Se mantiene en secciones |
| 3. Modelo | Umbrales por servicio y territorio (DEGURBA); 4,8 y 3,5 km/h | Se mantiene, con los 4 perfiles de Yeray |
| 3. Modelo | Voraz con dos objetivos, ganancia por punto de origen, rejilla de 250 m | Se mantiene, más «ampliar» |
| 4. Análisis | Theil, índice de concentración, doble penalización | Se mantiene; la descomposición principal pasa a ser la del índice, con Theil de contraste y referencia nula por tamaño (B.3) |
| 4. Análisis | Contrafactual frente a la estrategia municipal | **Cambia:** valor de la información con el mismo voraz (población, media de la zona o sección) (B.3) |
| 4. Análisis | Validación con el Atlas de Vulnerabilidad Urbana | **Cambia:** fuera, no existe con el Censo 2021 |
| 4. Análisis | Evolución 2015-2023 | Se mantiene, hasta 2024 |
| 5. Herramienta | Web estática, pruebas de referencia Python→JS, Quarto, MCP, Smart Data Models, comparar y exportar | Se mantiene |

### B.3 Decisiones de la unificación (14/11/2026)

| Decisión | Motivo |
|---|---|
| Unir las dos versiones con el relato y los datos de Yeray y el método de Izan | Cada una era fuerte donde la otra flojeaba (Anexo A) |
| Zonas = 179 municipios con la capital en 21 distritos | Con Madrid como un solo municipio, todas sus secciones vulnerables salían «ocultas» y el titular se inflaba |
| El acceso no entra en el índice de necesidad | Si entra, buscar «vulnerables sin acceso» es circular |
| La energía queda como contexto | El consumo bajo también lo tienen hogares pequeños, eficientes y segundas residencias |
| Sin chat en la web; la IA se demuestra con el MCP | El chat exige un servidor con una clave, rompe la web estática y puede inventar una cifra en directo |
| El tiempo de desarrollo no recorta el alcance | El desarrollo lo hacen agentes; solo recortan el método, el riesgo y los límites reales |
| Vuelven al alcance los 4 perfiles, la pendiente, el multimodal, la auditoría de la capital, las dos series, el contraste de tiempos, comparar y exportar, el informe y el esquema de Smart Data Models | Se habían recortado solo por tiempo |
| ~~La curva de valor se compara con el reparto real del PIR 2022-2026~~ | Sustituida tras la revisión de `dm-abogado-del-diablo` (B.4) |

### B.4 Correcciones tras `dm-abogado-del-diablo` (14/11/2026, veredicto NO APTO)

| Decisión | Motivo |
|---|---|
| La curva de valor mide el **valor de la información**: mismo voraz y mismo N, priorizando por población, por la media de la zona o por sección (6.8) | Comparar con el reparto del PIR era tautológico: el voraz maximiza la métrica con la que se puntúa, la regla «repartir como el PIR» era inventada y el PIR es un fondo de cooperación en el que cada ayuntamiento elige sus obras |
| El PIR pasa a la auditoría como contexto descriptivo, con la tabla del Plan de Actuación (BOCM de 22/10/2021) como fuente; las altas del BOCM, opcionales (6.9) | El reparto por municipio está en una sola tabla; las altas están dispersas y dicen en qué se gastó, no cuánto recibió cada municipio. Solo unos 650 M€ de los 1.000 M€ se asignan por municipio (**verificar**) |
| Tabla de quién decide cada servicio y propuestas etiquetadas con su decisor; las farmacias solo se diagnostican (4.1, 6.7) | Centros de salud y colegios los decide la Comunidad; las farmacias, la planificación farmacéutica; el PIR financia obras municipales |
| Centro de salud asignado por zona básica, si la zonificación está en abierto (6.5) | A cada vecino le corresponde su centro, no el más cercano |
| Quintiles ponderados por población, resultados por tamaño de zona y referencia nula; el titular habla de «diferencias entre secciones» y la descomposición principal es la del índice (6.3) | Lo oculto podía ser un efecto del tamaño de la zona, y el Theil de medias por sección no mide «la desigualdad» en general |
| Validación fuera de la capital con el índice de 199 zonas (8.1) | Casi toda la validación estaba en Madrid, que no entra en el PIR |
| El índice de 199 zonas no se presenta como réplica de los criterios del PIR; se quita la referencia «con los criterios del Decreto» y «fuentes comprobadas» pasa a «identificadas» (6.4, 11) | Eran incoherencias internas |
| Lista de lo que se congela sí o sí y orden de lo que cae primero (14) | La mitigación del riesgo de cálculo era genérica |

## Anexo C: glosario

- **ADRH:** Atlas de Distribución de Renta de los Hogares del INE. Renta y datos demográficos por sección censal; la última edición es la de 2024.
- **Sección censal:** la unidad territorial estadística más pequeña del INE, de unos 1.000 a 2.500 habitantes.
- **Zona:** cada una de las 199 unidades del índice regional: los 179 municipios, con Madrid capital dividida en sus 21 distritos.
- **Vulnerabilidad oculta:** secciones vulnerables situadas en zonas cuya media no lo es.
- **Doble penalización:** secciones vulnerables y, a la vez, sin acceso a pie a un servicio.
- **Prioridad de intervención:** término de la interfaz para las zonas donde conviene actuar, en lugar de «barrio vulnerable».
- **Quintil:** cada uno de los cinco grupos del mismo tamaño en que se ordenan las secciones.
- **Índice de Theil:** medida de desigualdad que se puede descomponer exactamente en una parte entre grupos y otra dentro de cada grupo.
- **Índice de concentración:** mide si algo (aquí, la falta de acceso) se acumula en los más pobres; 0 es un reparto igual.
- **Monte Carlo con pesos Dirichlet:** repetir el índice miles de veces con pesos al azar que suman 1, para ver cuánto depende el ranking de los pesos elegidos.
- **Winsorize:** recortar los valores extremos a un percentil para que no dominen.
- **Z-score:** expresar cada valor como distancias a la media en desviaciones típicas.
- **Bootstrap:** remuestrear los datos muchas veces para obtener un intervalo de confianza.
- **Función de Tobler:** fórmula que estima la velocidad al caminar según la pendiente.
- **GTFS:** formato estándar abierto de horarios, paradas y rutas del transporte público.
- **DEGURBA:** clasificación europea de municipios en urbanos, intermedios y rurales.
- **Cobertura máxima (voraz):** método de ubicación que en cada paso elige el sitio que más demanda nueva cubre.
- **Valor de la información:** cuánto mejora una decisión al saber más; aquí, cuántas personas vulnerables más se alcanzan al priorizar por sección en lugar de por la media de la zona, con el mismo método y el mismo número de centros.
- **Referencia nula:** lo que saldría solo por azar; aquí, repartiendo las secciones al azar entre zonas del mismo tamaño.
- **Zona básica de salud:** territorio que atiende cada centro de salud; a cada vecino le corresponde el de su zona.
- **Brecha:** posición en el ranking de necesidad menos posición en el ranking de asignación recibida.
- **Correlación de Spearman:** mide cuánto se parecen dos rankings, de −1 a 1.
- **PIR:** Programa de Inversión Regional de la Comunidad de Madrid; fondo de cooperación con los municipios, salvo la capital, por periodos de cinco años. Su Plan de Actuación fija lo asignado a cada municipio; cada ayuntamiento propone sus obras.
- **IGUALA/IVTA:** sistema del Ayuntamiento de Madrid que calcula el Índice de Vulnerabilidad Territorial Agregado por barrio y distrito.
- **Pobreza energética escondida:** hogares que consumen menos energía de la que necesitan, normalmente por no poder pagarla.
- **MCP (Model Context Protocol):** protocolo abierto para que los asistentes de IA usen herramientas y datos externos de forma controlada.
- **Smart Data Models:** iniciativa de modelos de datos comunes y abiertos para que los datos de distintas fuentes se puedan cruzar.
- **Falacia ecológica:** atribuir a cada persona o barrio la media de su territorio.

## Anexo D: fuentes

- Plan de Izan: [plan-propuesta-B.md](../izan/plan-propuesta-B.md) · Ficha de Yeray: [plan_propuesta_B_Yeray_Cerca.md](../yeray/plan_propuesta_B_Yeray_Cerca.md).
- API del catálogo regional: `https://datos.comunidad.madrid/api/3/action/` · API del Ayuntamiento: `https://datos.madrid.es/api/3/action/` · API del INE: `https://servicios.ine.es/wstempus/js/ES/`.
- [PIR 2022-2026, Portal de Transparencia](https://www.comunidad.madrid/transparencia/node/25379) · [Plan de Actuación del PIR 2022-2026, BOCM 22/10/2021](https://www.comunidad.madrid/transparencia/sites/default/files/plan/document/bocm211022_pir2022-2026.pdf) · [Decreto 118/2020](https://www.comunidad.madrid/transparencia/sites/default/files/plan/document/bocm-pir_2021_2025.pdf) · [BOCM 14/08/2026 (PIR 2027-2031)](https://bocm.es/boletin/CM_Orden_BOCM/2026/08/14/BOCM-20260814-12.PDF) · [Anuncio del nuevo PIR](https://www.comunidad.madrid/node/118920)
- [IGUALA/IVTA en datos.gob.es](https://datos.gob.es/catalogo/l01280796-iguala-indice-de-vulnerabilidad-territorial-agregado-del-ayuntamiento-de-madrid)
- [INE ADRH 2024](https://ine.es/dyngs/Prensa/ADRH2024.htm)
- [Licencia de datos del CRTM](https://www.crtm.es/licencia-de-uso/) · [GTFS del CRTM en Mobility Database](https://mobilitydatabase.org/feeds/gtfs/mdb-2720)
- Catastro INSPIRE, edificios: `https://www.catastro.hacienda.gob.es/INSPIRE/buildings/ES.SDGC.BU.atom.xml`
