# Propuesta B unificada: «Cerca» (visión del jurado)

Análisis comparado de las dos versiones de la Propuesta B y propuesta de unificación.
Fecha: 14 de noviembre de 2026. Fuentes:
- [Plan de Izan](../izan/plan-propuesta-B.md) (11/11/2026)
- [Ficha de Yeray, «Cerca»](../yeray/plan_propuesta_B_Yeray_Cerca.md) (12/11/2026)

> **Estado: propuesta, no decisión.** Antes de anotarla en `docs/decisiones.md` hay que pasarla por `dm-abogado-del-diablo`. No se ha verificado ninguna marca «(verificar)» de los planes de origen.

## Marco de evaluación

- **Criterios:** uso de la información pública regional, viabilidad y código abierto (oficiales), más el valor económico, social o medioambiental (citado por la URJC y la prensa). Los pesos no están publicados.
- **Jurado relevante:**
  - Alberto Abella: Smart Data Models, APIs, MCP y espacios de datos.
  - Olga Quirós (ASEDIE): economía del dato y reutilización.
- **Tiempo:** congelación de datos el 22 de noviembre y presentación el 26 de noviembre.
- **Criterio de recorte (revisado el 14/11):** el desarrollo lo hacen agentes, así que **el tiempo de desarrollo no recorta el alcance**. Se recorta solo por método (circularidad, indicadores ambiguos), por riesgo ante el jurado (cifras inventadas, demo que se cae) o por límites reales: la fecha de congelación, el tiempo de cálculo, la duración de la presentación y la revisión de cifras.

## Diagnóstico

Las dos versiones comparten **el mismo esqueleto técnico**: sección censal, edificios del Catastro, red de OSM, rejilla de candidatos de 250 m, algoritmo voraz de cobertura máxima, web estática con PMTiles, MCP y dos vistas (ciudadanía y Administración). No compiten, se complementan:
- Izan aporta **el análisis**: un titular que se puede medir y un impacto que se puede demostrar.
- Yeray aporta **el contexto**: una decisión pública real, datos regionales comprobados y personas concretas.

Cada una es débil justo donde la otra es fuerte.

## Propuesta de Izan: vulnerabilidad oculta y dónde intervenir

### A favor
- **Titular medible:** «la media municipal oculta el X % de la desigualdad», con la descomposición de Theil dentro y entre municipios.
- **Impacto demostrable con un contrafactual:** con N servicios, compara priorizar por la media municipal con priorizar por sección, con una curva de población vulnerable cubierta para cada estrategia.
- **Rigor:**
  - sigue el manual de indicadores compuestos de la OCDE y el JRC;
  - prueba la sensibilidad con Monte Carlo e intervalos de ranking;
  - calcula el índice de concentración con bootstrap;
  - no reparte hacia abajo las variables municipales.
- **Necesidad y acceso separados**, sin circularidad; el cruce está en el mapa de «doble penalización».
- **Smart Data Models de forma explícita** y un MCP con herramientas concretas.
- Responde de forma expresa al riesgo de parecerse a *Desiertos de servicios* y cuida el lenguaje para no estigmatizar.

### En contra
- **No hay una decisión pública concreta.** Habla de «la Administración» en general, sin el PIR ni un motivo para hacerlo ahora.
- **Madrid capital como un solo municipio.** Su media no está en el quintil más vulnerable, así que todas sus secciones vulnerables saldrían como «ocultas». El hallazgo sería trivial e inflaría el titular.
- **Poco catálogo regional en el núcleo:** el índice por sección usa datos del INE, que son nacionales. No usa el portal del Ayuntamiento.
- **Datos sin actualizar o que no existen:** cuenta con la renta de «≈2023» cuando ya está publicada la de 2024, y valida con el Atlas de Vulnerabilidad Urbana, que según la ficha de Yeray no tiene versión con el Censo 2021.
- **Acceso más pobre:** una parada cuenta aunque no tenga frecuencia, no incluye farmacias ni servicios sociales y no tiene en cuenta la pendiente.
- **Demasiados extras para la demo:** informe en Quarto, comparar escenarios, exportar y una matriz de unos 16.000 × 60.000 pares.

## Propuesta de Yeray: «Cerca»

### A favor
- **Explica por qué ahora:** el PIR 2027-2031 está en tramitación, el INE publicó la renta de 2024 y el CRTM actualizó su GTFS. Hay una decisión pública real que esta herramienta puede cambiar.
- **Mucho dato regional, ya comprobado:** identificadores del catálogo de la Comunidad, el portal del Ayuntamiento y la validación con IGUALA.
- **199 zonas, con la capital dividida en sus 21 distritos:** evitan el problema de Madrid y permiten compararse con el índice del Ayuntamiento.
- **Personas concretas:** perfiles, pendiente con la función de Tobler y paradas que solo cuentan si tienen frecuencia. Es un buen gancho para la demo.
- **«Abrir frente a ampliar»:** una alternativa realista que un técnico entiende enseguida.
- **Honestidad con el dato:** documenta lo descartado y el sesgo del Portal del Suelo.
- Explica en qué se diferencia de proyectos ya premiados.

### En contra
- **Alcance amplio:** 4 perfiles, unos 8 servicios, toda la región, pendiente, frecuencia, auditoría, ubicación, validación, MCP y chat. Con desarrollo por agentes no es un problema de construcción, pero sí de tiempo de cálculo y de foco en la presentación.
- **Circularidad:** el acceso entra como una dimensión del índice y luego se usa ese índice para buscar zonas vulnerables sin acceso.
- **No mide lo que la media esconde.** No hay vulnerabilidad por sección, solo acceso, así que «la media esconde el hueco» se queda sin cifra.
- **La auditoría es frágil:**
  - las transferencias de capital mezclan el PIR con fondos estatales y europeos;
  - faltan 2022 y 2023;
  - la «brecha» se puede leer como una acusación, lo que choca con la licencia del CRTM.
- **El indicador de energía es discutible:** un consumo bajo también lo tienen los hogares pequeños, los eficientes y las segundas residencias. Abre un debate para ganar poco.
- **No menciona Smart Data Models**, y Abella está en el jurado.
- **Sensibilidad débil:** se limita a sliders y normalización min-max.

## Propuesta unificada

Se queda con el **relato y los datos de Yeray** y con el **método y el impacto de Izan**.

| Pieza | Decisión | Origen |
|---|---|---|
| Nombre y gancho | «Cerca», ligado al PIR 2027-2031 | Yeray |
| Titular | «La media municipal oculta el X % de la desigualdad» (Theil) | Izan |
| Vulnerabilidad por sección | Renta de 2024 del INE, Padrón y Censo 2021, **separada del acceso** | Izan |
| Índice municipal | Las **199 zonas** con variables del catálogo regional, validado con IGUALA (Spearman) y con la esperanza de vida | Yeray |
| Vulnerabilidad oculta | Secciones del quintil más vulnerable en zonas (municipios o distritos) cuya media no lo está | Izan, con las zonas de Yeray |
| Sensibilidad | Sliders en la web y Monte Carlo en la nota metodológica | Ambos |
| Acceso | Servicios de Yeray (centro de salud, farmacia, servicios sociales, centro de mayores o de día, colegio, zona verde, DEA) y **paradas con frecuencia** | Ambos |
| Perfiles | Los **4 perfiles**: mayores, familias, población general y movilidad reducida, este último con las instalaciones accesibles de la capital | Yeray |
| Pendiente | **Función de Tobler en el núcleo**, con el MDT del IGN y más penalización para la movilidad reducida | Yeray |
| Transporte | Parada con frecuencia + **acceso multimodal por hora** (caminar y transporte) con r5py y el GTFS del CRTM | Ambos |
| Cruce | Mapa de doble penalización y población sin acceso por quintil de renta y por perfil | Izan |
| Ubicación | Algoritmo voraz con los 2 objetivos + «abrir frente a ampliar», marcando el suelo público | Ambos |
| Impacto | **Curva contrafactual frente al reparto real del PIR 2022-2026**, extraído del BOCM: «con el mismo dinero, priorizar por sección habría llegado a X personas vulnerables más». La estrategia municipal teórica queda como segunda referencia | Izan + Yeray |
| Auditoría regional | Necesidad frente al PIR real por municipio (brecha), con las transferencias de capital solo como contraste | Yeray, reforzada |
| Auditoría de la capital | Obras de accesibilidad en aceras (2020, 2021 y 2024) frente a mayores y movilidad reducida sin acceso, y listas de espera de centros de día y residencias | Yeray |
| Evolución | Subíndice de renta 2015-2024 por sección (secciones que mejoran o empeoran) | Izan |
| Validación | Esperanza de vida, Spearman con IGUALA, **prueba temporal** (¿el índice de 2019 anticipaba el paro y el envejecimiento de 2024?) y **tiempos a pie contrastados** con un planificador de rutas en una muestra | Ambos |
| Herramienta técnica | Comparar dos escenarios guardados y exportarlos a CSV o GeoJSON | Izan |
| Informe | Informe de análisis completo y nota metodológica, enlazados desde la web | Izan |
| Apertura | MCP, datos en CSV y GeoParquet con CC BY 4.0 y **propuesta de un esquema nuevo en Smart Data Models** (indicador de acceso y vulnerabilidad), además de reutilizar los existentes | Ambos |
| Lenguaje | «Prioridad de intervención» y huecos de transporte como oportunidades de mejora | Ambos |
| Construcción | Por capas, de modo que siempre haya una demo que funcione | Yeray |

### Qué vuelve al quitar el plazo de desarrollo
Lo que se había recortado solo por tiempo: el reparto real del PIR desde el BOCM, la pendiente, los 4 perfiles, el multimodal, la capa de auditoría de la capital, las dos series temporales, el contraste de tiempos a pie, comparar y exportar escenarios, el informe completo y el esquema nuevo de Smart Data Models.

**La mayor ganancia es el PIR real.** El contrafactual deja de compararse con una estrategia que definimos nosotros y pasa a compararse con lo que de verdad se hizo. Desaparece el riesgo de rival hecho a medida y la auditoría deja de depender de las transferencias de capital, que mezclan fuentes y les faltan 2022 y 2023. Límite que se declara: el PIR no incluye a Madrid capital y financia inversión en general, no solo centros de servicios.

### Se descarta (por método o por riesgo, no por tiempo)
- **El acceso como dimensión del índice:** crea circularidad; se mantiene separado de la necesidad.
- **El indicador de energía en el índice:** es ambiguo (hogares pequeños, eficientes, segundas residencias); se queda como contexto, con el ranking con y sin él.
- **El chat dentro de la web:** exige un servidor con una clave y rompe la web estática, y puede inventar una cifra en directo. La IA se demuestra con el MCP desde Claude.
- **El Atlas de Vulnerabilidad Urbana como validación:** no existe con el Censo 2021.
- **El Portal del Suelo como lista de candidatos:** está sesgado; solo marca el suelo disponible.

### Qué gana ante el jurado
- **Datos regionales:** el índice de las 199 zonas, los servicios, el GTFS, el PIR del BOCM y la capa del Ayuntamiento forman el núcleo, no solo el contexto.
- **Viabilidad:** construcción por capas y una demo estática que no se cae.
- **Código abierto e interoperabilidad:** licencias libres, MCP y un esquema propuesto a Smart Data Models.
- **Valor social y económico:** una decisión real y actual (el PIR 2027-2031) y un impacto simulado contra el reparto real anterior.
- **Rigor defendible:** necesidad y acceso separados, sensibilidad, validación externa, prueba temporal y tiempos contrastados.

### Límites reales que quedan
- **Fecha de congelación (22/11) y tiempo de cálculo.** Las matrices de r5py para toda la región, con 4 perfiles, pendiente y multimodal, y los 179 ficheros del Catastro son horas de máquina. Hay que medir con un municipio de prueba y lanzar el cálculo completo pronto.
- **Duración de la presentación.** El producto es grande, pero el relato sigue estrecho: titular, un caso concreto, el simulador y la curva frente al PIR real. El resto se enseña solo si el jurado pregunta.
- **Más cifras que defender.** Cada pieza nueva pasa por `dm-trazador-cifras` y, si es espacial, por `dm-revisor-espacial`. El cuello de botella es la revisión, no el desarrollo.
- **Peso de la web estática.** Perfiles × servicios × pendiente multiplican los ficheros precalculados: carga por municipio bajo demanda y, si hace falta, menos combinaciones en la vista ciudadana.
- **Extraer el PIR del BOCM:** las altas vienen en órdenes y anexos en PDF; hay que comprobar que se pueden asignar por municipio y año.
- **Los indicadores de distrito del Ayuntamiento** no son idénticos a los municipales.

## Pendientes antes de cerrar la decisión
- [ ] Pasar esta propuesta por `dm-abogado-del-diablo`.
- [ ] Localizar en el BOCM las altas del PIR 2022-2026 y comprobar que se pueden asignar por municipio e importe.
- [ ] Definir la estrategia municipal teórica (segunda referencia) a partir de los criterios del PIR (Decreto 118/2020).
- [ ] Probar r5py en un municipio metropolitano, con pendiente y multimodal: tiempo de cálculo y tamaño del fichero.
- [ ] Revisar los esquemas existentes de Smart Data Models antes de proponer uno nuevo.
- [ ] Resolver las marcas «(verificar)» que afectan a piezas que se quedan: número de secciones, identificador de la tabla de renta del ADRH, licencia del Catastro INSPIRE, vigencia del GTFS de metro y coordenadas de `atencion_social_registro_centros`.
- [ ] Confirmar con la organización los pesos de los criterios y el formato de entrega.
- [ ] Anotar la idea elegida en `docs/decisiones.md`.
