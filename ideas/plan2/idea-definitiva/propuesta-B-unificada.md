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
- **El alcance no cabe en el plazo:** 4 perfiles, unos 8 servicios, toda la región, pendiente, frecuencia, auditoría, ubicación, validación, MCP y chat, con 8 días hasta la congelación de datos.
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
| Acceso | Servicios de Yeray (centro de salud, farmacia, servicios sociales, colegio, DEA), **paradas con frecuencia** y 2 velocidades (general y mayores) | Ambos |
| Cruce | Mapa de doble penalización y población sin acceso por quintil de renta | Izan |
| Ubicación | Algoritmo voraz con los 2 objetivos + «abrir frente a ampliar», marcando el suelo público | Ambos |
| Impacto | **Curva contrafactual** de la estrategia municipal frente a la de sección, presentada como criterio para el PIR | Izan + Yeray |
| Apertura | MCP, Smart Data Models y datos en CSV y GeoParquet con CC BY 4.0 | Ambos |
| Lenguaje | «Prioridad de intervención» y huecos de transporte como oportunidades de mejora | Ambos |
| Construcción | Por capas, de modo que siempre haya una demo que funcione | Yeray |

### Ampliaciones, solo si sobra tiempo
- Pendiente con la función de Tobler.
- Auditoría de transferencias de capital, como un gráfico con advertencias en la nota metodológica, nunca en la demo.

### Se descarta
- Chat dentro de la web.
- Perfil de movilidad reducida.
- Indicador de energía en el índice (como mucho, de contexto).
- Obras de aceras y listas de espera.
- Transporte multimodal.
- Comparar y exportar escenarios.
- Informe en Quarto (basta con la nota metodológica).
- Atlas de Vulnerabilidad Urbana como validación.

### Qué gana ante el jurado
- **Datos regionales:** el índice de las 199 zonas, los servicios y el GTFS salen del catálogo regional y el portal del Ayuntamiento, no solo del contexto.
- **Viabilidad:** alcance recortado, construcción por capas y una demo estática que no se cae.
- **Código abierto e interoperabilidad:** licencias libres, Smart Data Models y MCP.
- **Valor social:** una decisión real y actual (el PIR) y un impacto simulado contra una línea base.
- **Rigor defendible:** necesidad y acceso separados, sensibilidad y validación externa.

### Riesgos que siguen
- **La estrategia municipal del contrafactual** hay que definirla de forma justa, imitando cómo se reparte hoy el PIR por municipio. Si no, se verá como un rival hecho a medida.
- **El tamaño de la matriz de r5py** está sin probar.
- **Los indicadores de distrito del Ayuntamiento** no son idénticos a los municipales.
- **El alcance** sigue siendo grande para 8 días.

## Pendientes antes de cerrar la decisión
- [ ] Pasar esta propuesta por `dm-abogado-del-diablo`.
- [ ] Definir la estrategia municipal del contrafactual a partir de los criterios del PIR (Decreto 118/2020).
- [ ] Probar r5py en un municipio metropolitano: tiempo de cálculo y tamaño del fichero.
- [ ] Resolver las marcas «(verificar)» que afectan a piezas que se quedan: número de secciones, identificador de la tabla de renta del ADRH, licencia del Catastro INSPIRE, vigencia del GTFS de metro y coordenadas de `atencion_social_registro_centros`.
- [ ] Confirmar con la organización los pesos de los criterios y el formato de entrega.
- [ ] Anotar la idea elegida en `docs/decisiones.md`.
