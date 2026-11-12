# Cerca

**¿Tiene cerca lo que necesita quien más lo necesita? Y si no, ¿dónde conviene ponerlo?**
Lemas alternativos: «Lo que tienes a 15 minutos y lo que te falta» · «Que los servicios lleguen a quien más los necesita».

Propuesta para DataMad 2026 · versión de 12 de noviembre de 2026 · resultado de 7 rondas de entrevista y una ronda de verificación de datos.
Nace de fusionar dos ideas previas: la 10 (*índice de vulnerabilidad territorial municipal*) y la 3 (*ciudad de 15 minutos con equidad por renta*).

> Las marcas **(verificar)** señalan datos o cifras que todavía no se han comprobado en la fuente primaria. Todo lo demás se comprobó el 12 de noviembre de 2026 contra las API de los portales de la Comunidad, del Ayuntamiento y del INE, o contra las páginas oficiales.

## Cómo leer esta ficha

Esta ficha **describe y enmarca la idea** para saber cómo afrontarla. **No es una especificación de desarrollo.** Los métodos, herramientas, umbrales y fuentes que aparecen son el **punto de partida** que salió de la entrevista: lo que hoy parece mejor con lo que sabemos. Si al desarrollar aparece algo mejor, un dato que no existe o un resultado que obliga a cambiar de rumbo, se cambia.

**Lo que define la idea (si cambia esto, es otra idea):**
1. **Vulnerabilidad y cercanía, juntas.** No basta con saber dónde vive la gente vulnerable ni dónde faltan servicios: interesa dónde coinciden las dos cosas.
2. **Dos escalas que se explican entre sí.** Un índice por municipio (y por distrito en la capital) y el acceso a pie por sección censal, que muestra lo que la media municipal esconde.
3. **Diagnosticar, auditar, proponer.** Ver dónde está el problema, comprobar si los recursos públicos llegan allí y proponer dónde actuar.
4. **Personas concretas, no promedios.** El acceso se mide para perfiles con necesidades distintas (mayores, familias, movilidad reducida, población general), con su velocidad real y la pendiente de sus calles.
5. **Datos abiertos y públicos**, con el catálogo regional en el centro y el portal del Ayuntamiento como pieza obligatoria.
6. **Honestidad con los límites del dato.** Lo aproximado se marca, los supuestos se declaran y los datos descartados se explican.
7. **Una decisión que cambia**, no solo un mapa: el reparto del PIR 2027-2031 y la ubicación de servicios.

**Lo que es enfoque de partida (puede cambiar con el desarrollo):** los indicadores concretos, los pesos y umbrales, las velocidades, el método de ubicación, las herramientas y la arquitectura.

**Lo que está abierto:** todo lo marcado como **(verificar)** y la lista de la sección 14.

---

## 1. La idea en 30 segundos

Un índice municipal puede decir que un municipio tiene centro de salud mientras parte de sus vecinos no llegan a él a pie: viven lejos, cuesta arriba o en zonas con poco transporte. La media esconde el hueco.

**Cerca** mide ese hueco. Calcula, desde cada edificio de la Comunidad de Madrid, cuánto se tarda a pie, con pendiente y a la velocidad de cada perfil, en llegar al centro de salud, la farmacia, los servicios sociales, el colegio, una parada con frecuencia o un desfibrilador. Lo cruza con un índice de vulnerabilidad de los 179 municipios y los 21 distritos de la capital.

La misma cuenta, agregada, sirve a la **Administración** para ver si la inversión llega a donde hay más necesidad y para decidir **dónde abrir o ampliar** el siguiente servicio, justo cuando se prepara el PIR 2027-2031.

## 2. El problema

- **Las medias municipales esconden los huecos.** Un municipio puede tener buena renta media y buenos servicios en el centro, y a la vez barrios, urbanizaciones o pedanías donde un mayor no llega a pie a nada. Es el riesgo que la idea 10 ya señalaba de su propio índice.
- **El acceso se mide sin mirar quién lo necesita.** Un centro de salud a 15 minutos no significa lo mismo para alguien de 30 años que para alguien de 80 en una calle con cuestas.
- **La inversión regional se reparte con criterios agregados.** El PIR 2022-2026 (1.000 M€, todos los municipios salvo la capital) usa criterios como la renta per cápita, el paro, la población o la dependencia territorial (Decreto 118/2020, art. 9; **verificar** los pesos), pero no mide el acceso real a los servicios.
- **Lo que existe se queda corto.** El Ayuntamiento tiene su índice de vulnerabilidad por barrio (IGUALA), pero solo para la capital y sin acceso a pie. No hay nada parecido publicado para toda la Comunidad.
- **Es el momento.** El PIR 2027-2031 (unos 1.100 M€) está en tramitación según una orden del BOCM del 14/08/2026. El INE publicó el 19/10/2026 la renta de 2024 por sección censal y el Consorcio de Transportes actualizó sus horarios el 05/11/2026.

## 3. Para quién y qué decisión cambia

| Usuario | Pregunta que responde | Decisión que cambia |
|---|---|---|
| **Ciudadanía y prensa** | «¿Qué tengo a 15 minutos y qué me falta?» · «¿Recibe mi municipio lo que necesita?» | Dónde reclamar un servicio; qué contar (y con qué datos) sobre el reparto |
| **Personal técnico de la Comunidad** (Administración Local, por el PIR; Familia y Servicios Sociales) | «¿Dónde se juntan vulnerabilidad y falta de acceso?» · «Con presupuesto para N centros, ¿dónde cubren a más personas?» | Criterios del PIR 2027-2031; dónde abrir o ampliar centros de salud, de día o sociales |

La vista ciudadana es el gancho de la demo. La vista técnica es donde está el impacto, porque es la que puede cambiar una decisión pública.

## 4. Cómo funciona para el usuario

**Vista ciudadana «Cerca»:**
1. **Dónde.** Busca su dirección o pincha en el mapa.
2. **Quién.** Elige un perfil: mayor de 65, familia con niños, movilidad reducida o población general.
3. **Resultado.** Ve qué servicios tiene a 15 minutos a pie y cuáles no, cuánto tarda a cada uno y si la parada más cercana tiene frecuencia de verdad.
4. **Contexto.** Ve la posición de su municipio o distrito en el índice y qué dimensiones pesan más.

**Vista técnica:**
1. **Índice.** Un mapa de las 199 zonas con sliders para cambiar los pesos.
2. **Auditoría.** Necesidad frente a recursos recibidos, con la «brecha» por municipio.
3. **¿Dónde actuar?** Elige un tipo de servicio y un número N de centros, y compara «abrir nuevos» con «ampliar existentes».

Cada cifra lleva su fuente y, si es una aproximación, una marca y una explicación.

## 5. El cálculo, paso a paso

Lo estable es **qué** se mide. **Cómo** se calcula cada pieza es el enfoque de partida y se puede sustituir por algo mejor durante el desarrollo.

### 5.1 Las dos escalas y cómo se conectan

- **Escala regional:** un índice para **199 zonas**, que son los 179 municipios con Madrid capital dividida en sus 21 distritos. Se divide la capital porque, como un solo municipio, aplastaría la escala, y porque así se puede comparar con IGUALA.
- **Escala urbana:** el acceso a pie por **sección censal** (la unidad estadística mínima del INE, de unos 1.000 a 2.500 habitantes) en **toda la Comunidad**, unas 4.500 secciones (**verificar** la cifra exacta). En la capital se suma la capa del Ayuntamiento.
- **Conexión:** el acceso por sección se agrega a municipio o distrito y entra en el índice como una dimensión más. El detalle por sección explica por qué cada zona puntúa como puntúa.

```
Sección censal (acceso a pie por perfil) ──agrega──▶ Municipio o distrito (índice de 199 zonas)
        │                                                     │
        └──────────── detalle que explica el índice ◀─────────┘
                               │
               Auditoría (¿llegan los recursos?) ──▶ Propuesta (¿dónde actuar?)
```

### 5.2 El índice de vulnerabilidad

Tiene cuatro dimensiones. Las tres primeras recogen la idea 10 y la cuarta trae la idea 3.

| Dimensión | Indicador de partida | Por qué |
|---|---|---|
| Económica | Paro registrado sobre la población de 16 a 64 años | Es el único dato de empleo fiable por municipio; se queda a esa escala |
| Económica | Renta media por persona (ADRH del INE, 2024) | El mismo método para municipios, distritos y secciones, así que las 199 zonas son comparables |
| Salud y cuidados | Personas con discapacidad reconocida sobre la población | El mejor dato municipal de necesidad de cuidados (solo desde 2023) |
| Salud y cuidados | Grado de envejecimiento | Más mayores, más dependencia de los servicios cercanos |
| Salud y cuidados | Proporción de dependencia demográfica | Peso de los menores y los mayores frente a la población en edad de trabajar. **No** es la dependencia de la ley, que solo existe a nivel regional |
| Vivienda | % de viviendas vacías (Censo 2021, por consumo eléctrico) | Señal de abandono o de un parque desajustado |
| Vivienda | % de hogares en alquiler | Más exposición al coste de la vivienda |
| Vivienda (peso ½) | % de viviendas ocupadas con consumo eléctrico anómalamente bajo | Aproximación a la pobreza energética escondida (ver 5.3) |
| Acceso | % de población de cada perfil sin un servicio básico a 15 minutos | Viene de la escala urbana (5.4) y une las dos ideas |

**Cálculo:**
- Cada indicador se normaliza entre 0 y 1 sobre las 199 zonas, de forma que más alto signifique más vulnerable.
- **Pesos iguales** por dimensión e iguales dentro de cada dimensión; la energía lleva medio peso.
- Se descartaron los pesos estadísticos (PCA), porque son difíciles de explicar a un jurado y a un responsable político, y los criterios del PIR, porque sus pesos no son públicos.
- En la web, unos **sliders** permiten probar otros pesos. Con ellos casi gratis, se muestra cuánto cambian las 20 zonas más vulnerables al moverlos (sensibilidad).

**Lo que no entra en el índice:**
- **Esperanza de vida:** solo existe para los municipios de más de 100.000 habitantes y los distritos, así que se usa para validar (8.1).
- **Valor tasado de la vivienda:** solo existe para los municipios de más de 25.000 habitantes; se muestra como contexto.
- **Energía total facturada:** mezcla la industria con los hogares.

**Madrid capital en distritos.** Los datos regionales tratan a Madrid como un único municipio. Para los distritos se usa el panel de indicadores del Ayuntamiento, que trae por distrito el paro, la discapacidad, el envejecimiento, la dependencia, la renta y la esperanza de vida. Las viviendas vacías y el alquiler se calculan sumando las secciones del INE de cada distrito. Las diferencias de fecha o de definición se recogen en una tabla de equivalencias.

### 5.3 La energía

La idea 10 incluía la energía:
- Primero se descartó la **energía total facturada**, porque mezcla la industria con los hogares.
- Después se buscó un dato abierto de **consumo doméstico**. Datadis es privado. Barcelona publica el suyo y Madrid no. El bono social solo existe a nivel regional.
- Finalmente apareció en el catálogo regional el **Censo 2021 de viviendas por tramo de consumo eléctrico**.

Entra con **peso bajo**. El indicador es el porcentaje de viviendas ocupadas con un consumo anómalamente bajo, como aproximación a la *pobreza energética escondida*: hogares que consumen menos de lo que necesitan (concepto de la Estrategia Nacional contra la Pobreza Energética, **verificar** la cita). Los hogares pequeños o eficientes también consumen poco, así que se corrige por el tamaño medio del hogar, se avisa en la web y se enseña el ranking con y sin el indicador. El umbral de «consumo bajo» está abierto.

### 5.4 El acceso a pie

**Qué es tener acceso:** llegar a pie en **15 minutos** desde el propio edificio, a la velocidad de cada perfil y con la pendiente real.

| Perfil | Velocidad de partida | Servicios que importan |
|---|---|---|
| Mayores de 65 | Unos 3 km/h | Centro de salud, farmacia, servicios sociales, centro de mayores o de día, parada con frecuencia, desfibrilador |
| Familias con niños | Unos 4 km/h | Colegio, centro de salud con pediatría, zona verde, parada con frecuencia |
| Población general | Unos 4,8 km/h | Todos, con resultados por **quintil de renta** (la medición original de la idea 3) |
| Movilidad reducida | Unos 2,5 km/h y más penalización por pendiente | Como mayores, más instalaciones accesibles (en la capital) |

**Cómo se calcula (una forma de hacerlo):**
- **Desde dónde:** desde los **edificios residenciales del Catastro**, cada uno ponderado por su número de viviendas. La población de cada sección, por edad, se reparte entre sus edificios. Medir desde el centro de la sección engañaría en las secciones rurales, que pueden medir varios kilómetros.
- **Por dónde:** la red de calles de OpenStreetMap. En el medio rural se asume que toda la red es transitable y se dice.
- **Pendiente:** con el modelo de elevación del IGN se calcula la pendiente de cada tramo. La **función de Tobler**, una fórmula clásica que reduce la velocidad al caminar según la pendiente, ajusta el tiempo de cada tramo, con más penalización para la movilidad reducida.
- **Transporte:** una parada solo cuenta si tiene **frecuencia suficiente**, por ejemplo 4 o más salidas por hora entre las 7 y las 9 de un día laborable, calculado con el GTFS del Consorcio. Una parada sin servicio real no da acceso. Si da tiempo, se amplía a viajes que combinan caminar y transporte.
- **Herramientas candidatas:** pandana u OSMnx para la red a pie, r5py para la parte multimodal.

**Qué produce:**
- Para cada sección, perfil y servicio, el % de población con acceso y el tiempo típico de llegada.
- De ahí salen la **dimensión de acceso** del índice y la **equidad por renta**: el % sin acceso por quintil de renta de la sección, que se puede seguir año a año.
- También un indicador de **soledad** (hogares unipersonales) para ponderar la necesidad.

## 6. La vista de la Administración

### 6.1 Auditoría: ¿llegan los recursos a donde hace falta?

- **Escala regional.** Se compara el índice con dos medidas abiertas, ambas por habitante: las **transferencias de capital recibidas** (dinero de inversión de otras administraciones, PIR incluido) y el **gasto municipal en protección y promoción social**.
- **Brecha.** La **brecha** es la posición en el ranking de necesidad menos la posición en el ranking de recursos. Una brecha grande y positiva señala mucha necesidad con pocos recursos. Se presenta con un diagrama de dispersión y un mapa.
- **Límites.** Las transferencias de capital mezclan el PIR con fondos estatales y europeos. Además, al catálogo **le faltan 2022 y 2023** (y al gasto social, 2022). Por eso se compara la media de 2017–2021 (el PIR anterior) con 2024. Sacar las cifras exactas del PIR 2022-2026 del BOCM sería la mejora más valiosa.
- **Escala urbana (capital).**
  - Las **obras de accesibilidad en aceras** (2020, 2021 y 2024) por distrito, frente a los mayores y las personas con movilidad reducida sin acceso.
  - Los equipamientos por habitante y las **listas de espera** de centros de día y residencias, que el Ayuntamiento publica a diario.

### 6.2 Propuesta: ¿dónde actuar?

Se usa un algoritmo **voraz de cobertura máxima**. Elige primero el sitio que da acceso a más personas vulnerables sin acceso, luego el siguiente, y así hasta N. Se calculan dos escenarios y se comparan:
- **A · Abrir uno nuevo:** candidatos en una rejilla de unos 250 m sobre suelo urbano, marcando si hay suelo público dotacional cerca.
- **B · Ampliar uno existente:** candidatos entre los equipamientos actuales, por ejemplo añadir atención social a un centro de mayores. Suele ser más barato y más rápido.

El resultado es una frase del tipo «con N centros cubres a X personas vulnerables más; abriendo cubres esto y ampliando cubres esto otro».

**Cómo evolucionó esta decisión.** Al principio se eligieron como candidatas las parcelas públicas del **Portal del Suelo**. Al revisarlas resultaron ser 527 parcelas en solo 49 municipios, casi todas residenciales o industriales en venta, con unas 40 dotacionales, y concentradas en municipios ricos (Majadahonda, Pozuelo). Como lista habrían sesgado el resultado, así que quedan solo como marca de suelo disponible.

### 6.3 Decisiones que permite
1. **Criterio para el PIR 2027-2031.** Un reparto que tenga en cuenta la vulnerabilidad y el acceso, comparado con el reparto actual.
2. **Dónde abrir o ampliar** centros de salud, de día o sociales, con las personas que cubre cada opción.
3. **Dónde mejorar la frecuencia del transporte** para que las paradas existentes den acceso de verdad, presentado como mejora y no como crítica (ver 12).

## 7. Escenarios «¿y si…?»

Responden a decisiones concretas y son la parte que más se presta a la demo en directo:
- **Pesos distintos** en el índice (sliders): ¿qué zonas cambian de prioridad?
- **N centros nuevos o ampliados** de un tipo de servicio: ¿a cuántas personas vulnerables más se cubre?
- **Abrir frente a ampliar:** ¿qué cubre cada opción?
- **Otro perfil u otro umbral** (10, 15 o 20 minutos): ¿cómo cambia el mapa?
- **Más frecuencia en una línea:** ¿cuántas paradas pasan a dar acceso? (ampliación, **verificar** si es viable).

No hay capa predictiva. Queda fuera del alcance.

## 8. Validación e impacto

### 8.1 ¿El índice mide lo que dice? (validación externa)
- **Esperanza de vida:** un índice de vulnerabilidad bien hecho debería ir en la dirección contraria a la esperanza de vida. Hay unos 31 puntos de comparación: los municipios de más de 100.000 habitantes y los 21 distritos.
- **Concordancia con IGUALA:** se compara nuestro ranking de los 21 distritos con el del Ayuntamiento mediante la **correlación de Spearman**, que mide si dos rankings ordenan igual. Si no coinciden, se explica por qué (por ejemplo, porque nuestro índice incluye el acceso).
- **Prueba temporal:** se comprueba si el índice con datos de 2019 anticipaba el empeoramiento del paro o el envejecimiento hasta 2024. Se hace sin la discapacidad, que solo existe desde 2023.

Se informa de la correlación y su signo, también cuando no sale la esperada.

### 8.2 ¿El dato es fiable? (validación del dato)
- **Sensibilidad del ranking** a los pesos y al indicador de energía.
- **Comprobación del tiempo a pie** en una muestra de rutas contra un planificador de rutas conocido (**propuesta**).
- **Cobertura de los cruces:** secciones que no casan entre versiones, edificios sin viviendas y centros sin coordenadas, contados y declarados.

### 8.3 ¿Cambia decisiones? (impacto)
En los concursos revisados, casi ningún ganador mide su impacto. Esta propuesta lo enfoca así:
- **Capacidad de priorizar** (la medida de la idea 10): cuántas personas vulnerables sin acceso cubriría un reparto guiado por el índice, frente al reparto real (6.1).
- **Equidad del acceso** (la medida de la idea 3): el % sin acceso por quintil de renta, como línea base para seguir cada año.
- Se dice «cubriría», no «ha cubierto». Ninguna estimación se presenta como impacto medido.

## 9. IA y apertura

- **Datos abiertos como API:** los resultados por sección, municipio y distrito se publican en CSV y GeoParquet, con CC BY 4.0, para consultarlos por URL o proponerlos al catálogo regional.
- **Servidor MCP** (el protocolo con el que un asistente de IA usa herramientas externas, que se vio en la formación de DataMad). Tendría herramientas que siempre calculan lo mismo: consultar el índice, ver el acceso de una zona y ubicar N servicios. Cualquier asistente podría preguntar «¿qué le falta a un mayor en tal sección?» y recibir cifras calculadas con su fuente.
- **Chat dentro de la web**, solo si da tiempo y si nunca inventa una cifra: todas las salen de las herramientas, todas las respuestas citan la fuente y avisa de que es una IA (artículo 50 del Reglamento de IA). Si falla, se queda fuera y la API y el MCP siguen.
- **Entregables abiertos:**
  - Repositorio con licencia libre que regenera todo desde las fuentes oficiales.
  - Conjunto de datos del índice y del acceso.
  - Nota metodológica con supuestos, límites y validación.

## 10. Encaje con los criterios de DataMad

| Criterio | Cómo lo cumple |
|---|---|
| **Uso de la información pública regional** (oficial) | El núcleo usa el catálogo regional: paro, discapacidad, envejecimiento, dependencia, Censo 2021, centros sanitarios, farmacias, centros sociales y educativos, desfibriladores, GTFS del Consorcio y presupuestos municipales. Lo completan el portal del Ayuntamiento (capa de la capital, validación con IGUALA, listas de espera) y fuentes nacionales abiertas (INE, Catastro, IGN, OSM). |
| **Viabilidad** (oficial) | Fuentes comprobadas una a una, web sin servidor, pipeline reproducible y construcción por capas que siempre dejan una demo funcionando (13). |
| **Código abierto** (oficial) | Repositorio con licencia libre, librerías abiertas, conjunto de datos CC BY 4.0, API y MCP. |
| **Valor económico, social o medioambiental** (citado por la URJC y la prensa) | Responde a una decisión real y actual (el PIR 2027-2031), propone dónde actuar y mide su capacidad de priorizar frente al reparto actual. |

**Lecciones de los concursos de referencia que se aplican:** un problema concreto para colectivos claros, el valor en el cruce de fuentes, un resultado que sirve para decidir, un servicio con URL, la IA como capa sobre datos verificables y el impacto comparado con una línea base.

**En qué se diferencia de proyectos ya premiados:**
- *Ciudades de quince minutos para la infancia* (UPCT, Madrid 2025) mide un solo colectivo.
- *Rampa* y *AccesibiliMad* (Madrid 2025) calculan rutas accesibles o miran servicios por zona, sin cruzarlos con la vulnerabilidad ni con el gasto.
- *Flowcation* (GovHack 2025) trabaja la equidad del acceso, pero no propone dónde actuar.

Cerca une vulnerabilidad, acceso con pendiente, auditoría del gasto y propuesta de ubicación, en toda la región y para varios perfiles.

## 11. Datos

### 11.1 Catálogo regional (datos.comunidad.madrid, CKAN, CC BY 4.0) · obligatorio
| Conjunto | Qué aporta | Límite |
|---|---|---|
| `302038` | Paro registrado por municipio | Dato a 31 de marzo; 2006–2026 |
| `irpf_indicador_renta` | Renta disponible bruta municipal | 2015–2024; alternativa al ADRH |
| `personas_discapacidad_por_tipo_y_sexo` | Discapacidad reconocida por municipio | Solo 2023–2025 |
| `grado_envejecimiento_por_edad` | Envejecimiento por municipio | 1996–2025 |
| `1930729` | Proporción de dependencia **demográfica** | No es la dependencia de la ley |
| `censo_2021_viviendas_por_consumo_electrico` | Viviendas vacías y por tramo de consumo doméstico | Solo 2021 |
| `censo_2021_porcentaje_viviendas_familiares_por_tenencia` | % en propiedad, alquiler y otros | Solo 2021 |
| `centros_servicios_establecimientos_sanitarios` | **422 centros públicos de atención primaria** (272 centros de salud y 150 consultorios), 414 con coordenadas, en 176 municipios; 311 con pediatría | Una fila por centro y servicio, hay que eliminar duplicados; coordenadas UTM |
| `oficinas_farmacia` | 2.957 farmacias con coordenadas | Coordenadas UTM |
| `atencion_social_registro_centros` | Centros de atención social | **Verificar** las coordenadas |
| `centros_educativos` | Centros educativos | |
| `desfibriladores` | Unos 13.700 DEA | Excluye el ámbito sanitario |
| GTFS del CRTM (6 redes, enlazadas desde el catálogo) | Paradas, líneas y horarios; capas de accesos y andenes | El de metro es del 30/05/2025; los demás, del 05/11/2026 |
| `presu_liq_ingresos`, `presu_liq_gastos` | Transferencias de capital y gasto social por municipio | Faltan 2022–2023 (transferencias) y 2022 (gasto social) |
| `esperanza_vida_municipios_mayores_100000_hab_por_sexo` | Validación | Solo unos 10 municipios |
| `parcelas_portal_suelo` | Marca de suelo público | 527 parcelas, 49 municipios, unas 40 dotacionales |

### 11.2 Portal del Ayuntamiento (datos.madrid.es, CKAN, CC BY 4.0) · capa de la capital y validación
| Conjunto | Qué aporta |
|---|---|
| `300087-0-indicadores-distritos` | 392 indicadores por distrito y barrio (2019–2026): paro, discapacidad, envejecimiento, dependencia, renta, esperanza de vida 2024 |
| `200076-0-padron` | Padrón mensual por sección, edad y sexo |
| `300577-0-iguala-vulnerabilidad`, `300301-0-ranking-vulnerabilidad` | Índice de vulnerabilidad del Ayuntamiento, para validar |
| `201544-0-centros-salud`, `209094-0-centros-servicios-sociales`, `200337-0-centros-mayores`, `200342-0-centros-dia`, `202311-0-colegios-publicos` | Servicios municipales con coordenadas |
| `900023-0-emt-paradas-autobus`, `208327-0-transporte-bicicletas-bicimad` | Transporte de la capital |
| `202162-0-instalaciones-accesibles-municip` | Instalaciones accesibles, para el perfil de movilidad reducida |
| `300714-0`, `300608-0`, `300625-0` | Obras de accesibilidad en aceras de 2024 (188 actuaciones), 2021 y 2020, para la auditoría |
| `300620`, `300621`, `300622`, `300623` | Listas de espera diarias de residencias y centros de día |
| `300153-0-zonas-verdes-inventario` | Zonas verdes |

### 11.3 Fuentes nacionales y otras
| Fuente | Qué aporta | Estado |
|---|---|---|
| **INE ADRH 2024** | Renta por sección, distrito y municipio (tabla de renta: **verificar** el id) · indicadores demográficos por sección (**tabla 31105**: población, % de menores de 18, % de 65 y más, hogares unipersonales, tamaño del hogar) | Publicado el 19/10/2026; API JSON comprobada |
| **Catastro INSPIRE, edificios** | Cada edificio con su número de viviendas y su uso; 179 ficheros | Comprobado. Madrid usa el código 28900 en el Catastro y 28079 en el INE. Licencia: **verificar** |
| **IGN/CNIG, MDT** | Elevación para la pendiente | Por descargar |
| **OpenStreetMap** (Geofabrik) | Red peatonal | ODbL: citar «© OpenStreetMap contributors» |
| **Licencia del CRTM** | Condiciones de uso del GTFS | Leída (ver 12) |

### 11.4 Descartados
- `1003254` (% de viviendas vacías): es de 2001.
- `energia_electrica_facturada`: mezcla la industria con los hogares.
- `1914361` (dependencia de la ley) y `1932366` (bono social): solo existen a nivel regional.
- Atlas de Vulnerabilidad Urbana del Ministerio: no hay versión con el Censo 2021.
- Portal del Suelo como lista de candidatos: está sesgado (ver 6.2).

## 12. Arquitectura (propuesta)

Lo importante es que la demo no dependa de un servidor y que todo sea reproducible y abierto. Las herramientas concretas son la opción de partida.
- **Pipeline** en Python con DuckDB (y su extensión espacial): descarga las fuentes, las cruza, calcula el acceso, el índice, la auditoría y los escenarios precalculados.
- **Web estática** con MapLibre y teselas PMTiles, por ejemplo en GitHub Pages. El índice se recalcula en el navegador con los sliders, porque son solo 199 filas.
- **Ubicación de N servicios:** precalculada para varios valores de N, o calculada en el navegador si es lo bastante rápida (**verificar**).
- **MCP:** un servicio aparte y opcional, que no condiciona la web.
- **Geometrías:** las secciones del INE, el padrón municipal, el Censo 2021 y los códigos del Catastro no coinciden del todo. Se construyen tablas de paso antes de cruzar nada.
- **Licencias:**
  - Código MIT o Apache 2.0. Datos derivados CC BY 4.0; los derivados de OSM, ODbL.
  - **CRTM:** sus derivados pueden ir con otra licencia. Obliga a citarlo como «datos explotados», mostrar «Powered by CRTM» con enlace, conservar la fecha y no insinuar su respaldo. **No se republica el GTFS en bruto.** Prohíbe «menoscabar su imagen», así que los huecos de transporte se presentan como oportunidades de mejora.
- **Privacidad:** solo datos agregados. El reparto de la población entre edificios es una estimación estadística y no se publica por edificio.

## 13. Cómo afrontarlo

**Orden por capas** (decidido que todo entra en el alcance; se construye así para que siempre haya algo que enseñar):
1. Índice sin acceso y mapa de las 199 zonas.
2. Acceso con un perfil y un servicio, en la capital y en un municipio rural.
3. Los cuatro perfiles y todos los servicios en toda la Comunidad; el acceso entra en el índice.
4. Auditoría.
5. Propuesta de ubicación.
6. Validación.
7. MCP y chat.

## 14. Riesgos y verificaciones

### Riesgos
| Riesgo | Mitigación |
|---|---|
| **Alcance amplio en 14 días** (se decidió que todo entra) | Construir por capas que se puedan enseñar (13) |
| Volumen de cálculo regional (179 ficheros del Catastro, la red de toda la Comunidad) | Empezar por la capital y un municipio rural; guardar resultados por municipio y procesar en lotes |
| Indicadores de distrito no idénticos a los municipales | Tabla de equivalencias y marca en los datos aproximados |
| Versiones distintas de las secciones | Tablas de paso; documentar las que no casan |
| Proxies imperfectos (energía; movilidad reducida aproximada con los mayores o la tasa de discapacidad) | Peso bajo, avisos visibles y sensibilidad |
| El dato municipal oculta desigualdades (riesgo original de la idea 10) | Para eso existe la escala de sección; el paro se queda municipal |
| Huecos en los presupuestos (2022–2023) | Comparar periodos completos; el PIR del BOCM si da tiempo |
| GTFS de metro de mayo de 2025 | Comprobar que su calendario siga vigente; si no, usar paradas con frecuencia estimada |
| Lectura de la auditoría como ataque (licencia del CRTM, relación con la Administración) | Tono de mejora: dónde actuar, no a quién culpar |
| IA que inventa cifras | Solo herramientas que calculan siempre lo mismo; el chat es opcional |

### Verificaciones pendientes
- Id de la tabla de renta del ADRH por sección para Madrid (API del INE, operación 353).
- Vigencia del calendario del GTFS de metro.
- Licencia del Catastro INSPIRE.
- Umbral de «consumo eléctrico anómalamente bajo» y su ajuste por el tamaño del hogar.
- Pesos de los criterios del PIR (Decreto 118/2020) y altas del PIR 2022-2026 en el BOCM.
- Número exacto de secciones de la Comunidad.
- Coordenadas de `atencion_social_registro_centros`.
- Cita de la Estrategia Nacional contra la Pobreza Energética.

---

## Anexo A: registro de las rondas de entrevista

Recoge lo que se acordó como punto de partida en cada ronda. No es un compromiso cerrado: si el desarrollo lo pide, se revisa.

| Ronda | Pregunta | Respuesta del equipo | Alternativas descartadas |
|---|---|---|---|
| 0 | Requisitos | Solo datos abiertos; usar al menos el portal del Ayuntamiento; buscar fuentes más allá del documento de contexto | — |
| 1 | Fusión de las ideas 10 y 3 | Dos escalas conectadas | Solo escala urbana (pierde lo regional) · el acceso como componente único (oculta la explicación) |
| 1 | Decisión que mejorar | Ubicar servicios + auditoría, en secuencia | Solo el PIR · solo ubicar |
| 1 | Servicios | Salud, cuidados y social, educación, transporte y DEA | — |
| 1 | Población | Varios perfiles | Un único perfil |
| 2 | Alcance urbano | Toda la Comunidad + capa del Ayuntamiento en la capital | Solo la capital · la capital y dos pilotos |
| 2 | Perfiles | Los cuatro: mayores, familias, población general, movilidad reducida | — |
| 2 | Cómo ubicar | Cobertura en las parcelas del Portal del Suelo → revisado en la ronda 3 | Ranking de huecos · optimización completa |
| 2 | Pesos | Iguales + sliders | PCA · criterios del PIR |
| 3 | Candidatos, tras ver el sesgo del Portal del Suelo | Ambos: zona óptima con marca de suelo y ampliar equipamientos | Solo uno de los dos |
| 3 | Madrid capital en el índice | 21 distritos, validados con IGUALA | Un solo municipio · fuera |
| 3 | Energía | Buscar una fuente doméstica; si no hay, fuera | Incluir la energía total |
| 3 | Entregable | Web estática + datos abiertos; IA si da tiempo | Streamlit · web + asistente desde el principio |
| 4 | Reparto actual | Presupuestos liquidados; PIR del BOCM si da tiempo | Solo presupuestos · solo el BOCM |
| 4 | Validación | Esperanza de vida, IGUALA, prueba temporal | (La sensibilidad no se eligió; se mantiene por su bajo coste) |
| 4 | Acceso en el índice | Sí, como dimensión | Separado en una matriz de 2×2 · ambas |
| 4 | Usuario | Ciudadanía y prensa + técnico de la Comunidad | Técnico municipal |
| 5 | Desde dónde medir | Edificios del Catastro | Centroide de la sección · rejilla |
| 5 | Transporte | Parada con frecuencia; multimodal si es viable | Solo la parada |
| 5 | Pendiente | Tobler; las aceras de la capital se pidieron para las rutas → pasan a la auditoría por ser un listado de obras | Velocidad fija |
| 5 | Forma de la IA | Servidor MCP + chat sencillo | Explicaciones generadas · sin IA |
| 6 | Mínimo imprescindible | Todo (se afronta por capas) | — |
| 6 | Ubicación de la ficha | `ideas/plan2/yeray/` | — |
| 6 | Nombre | Cerca | «¿Llega?» · «Mapa de la Equidad» |
| 7 | Energía, tras encontrar el Censo 2021 | Entra con peso bajo | Solo contexto |

## Anexo B: glosario

- **ADRH:** Atlas de Distribución de Renta de los Hogares del INE. Renta y datos demográficos por sección censal; la última edición es la de 2024.
- **Sección censal:** la unidad territorial estadística más pequeña del INE, de unos 1.000 a 2.500 habitantes.
- **Quintil de renta:** cada uno de los cinco grupos del mismo tamaño en que se ordenan las secciones de menor a mayor renta.
- **PIR:** Programa de Inversión Regional de la Comunidad de Madrid; inversiones en los municipios, salvo la capital, por periodos de cinco años.
- **IGUALA/IVTA:** sistema del Ayuntamiento de Madrid que calcula el Índice de Vulnerabilidad Territorial Agregado por barrio y distrito.
- **GTFS:** formato estándar abierto de horarios, paradas y rutas del transporte público.
- **Función de Tobler:** fórmula que estima la velocidad al caminar según la pendiente.
- **Cobertura máxima (voraz):** método de ubicación que en cada paso elige el sitio que más demanda nueva cubre.
- **Correlación de Spearman:** mide cuánto se parecen dos rankings, de −1 a 1.
- **Pobreza energética escondida:** hogares que consumen menos energía de la que necesitan, normalmente por no poder pagarla.
- **MCP (Model Context Protocol):** protocolo abierto para que los asistentes de IA usen herramientas y datos externos de forma controlada.
- **Falacia ecológica:** atribuir a cada persona o barrio la media de su territorio.

## Anexo C: fuentes

- Documento de contexto del equipo: DataMad 2026, contexto y referencias (criterios, ganadores de referencia, patrones y panorama técnico).
- API del catálogo regional: `https://datos.comunidad.madrid/api/3/action/` · API del Ayuntamiento: `https://datos.madrid.es/api/3/action/` · API del INE: `https://servicios.ine.es/wstempus/js/ES/`.
- [PIR 2022-2026, Portal de Transparencia](https://www.comunidad.madrid/transparencia/node/25379) · [BOCM 14/08/2026 (PIR 2027-2031)](https://bocm.es/boletin/CM_Orden_BOCM/2026/08/14/BOCM-20260814-12.PDF) · [Anuncio del nuevo PIR](https://www.comunidad.madrid/node/118920)
- [IGUALA/IVTA en datos.gob.es](https://datos.gob.es/catalogo/l01280796-iguala-indice-de-vulnerabilidad-territorial-agregado-del-ayuntamiento-de-madrid)
- [INE ADRH 2024](https://ine.es/dyngs/Prensa/ADRH2024.htm)
- [Licencia de datos del CRTM](https://www.crtm.es/licencia-de-uso/) · [GTFS del CRTM en Mobility Database](https://mobilitydatabase.org/feeds/gtfs/mdb-2720)
- Catastro INSPIRE, edificios: `https://www.catastro.hacienda.gob.es/INSPIRE/buildings/ES.SDGC.BU.atom.xml`
- [Consumo eléctrico por código postal (Barcelona, referencia)](https://datos.gob.es/es/catalogo/l01080193-consumo-de-electricidad-mwh-por-codigo-postal-sector-economico-y-tramo-horario) · [Solicitud ciudadana de datos de consumo en viviendas](https://datos.gob.es/es/solicitud-de-datos/historico-de-consumos-mensuales-de-electricidad-en-viviendas)
