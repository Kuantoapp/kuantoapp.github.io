# DATAMAD26 · Plan de la Propuesta B: Vulnerabilidad oculta y dónde intervenir (#10 + #3)

Plan de alto nivel resultado de la entrevista por fases.
Última actualización: 11/11/2026 · Final: 26/11/2026 (URJC Vicálvaro).

## Estado de las fases
| Fase | Estado |
|---|---|
| 1. Enfoque y alcance | ✅ Cerrada |
| 2. Datos | ✅ Cerrada (quedan verificaciones prácticas) |
| 3. Modelo (índice + accesibilidad + priorización) | ✅ Cerrada |
| 4. Análisis | ✅ Cerrada |
| 5. Herramienta | ✅ Cerrada |
| 6. Presentación y entrega | 📝 Orientativa (se detallará al final) |

**Plan cerrado el 11/11/2026.** El orden de trabajo, el reparto y las fechas los gestiona el equipo y no forman parte de este documento.

---

## 1. Enfoque y alcance
- **Motivo del enfoque:** el riesgo principal de B es la originalidad. *Desiertos de servicios* ganó la primera edición, y un simple "mapa de acceso a servicios" la repetiría.
- **Eje elegido (2 + 3):**
  - **Vulnerabilidad oculta:** secciones censales vulnerables y sin acceso dentro de municipios que, en la media, parecen sanos. Es lo que una política basada en la media municipal no ve.
  - **Dónde intervenir:** priorizar la ubicación de un nuevo servicio (centro de salud, DEA, colegio, parada) según cuánto reduce la desigualdad de acceso por persona vulnerable (*location-allocation*). Sustituye a la medición "frente al reparto actual de recursos", que no tenía datos.
- **Métrica incluida (1):** población sin acceso por quintil de renta y por edad (si la falta de acceso es regresiva).
- **Ampliación (4):** accesibilidad en transporte público según la hora y la frecuencia (GTFS). Fuera del alcance inicial.
- **Encaje #10 / #3:** el índice municipal es la vista con la que se prioriza hoy; la sección censal es la vista real. No se reparten hacia abajo las variables municipales (no se imputa). Ver la Fase 3 para la definición operativa.
- **Público, con dos vistas:**
  - **Administración:** simulador de dónde intervenir y mapa de vulnerabilidad oculta.
  - **Ciudadanía:** qué tengo a mano desde mi zona y cómo está mi sección frente a mi municipio.
- **Servicios:** sanidad (atención primaria), DEA, colegios y transporte.
- **Territorio:** toda la Comunidad de Madrid, con énfasis en el área metropolitana. Umbrales de acceso distintos según el tipo de territorio (urbano / intermedio / rural).
- **Unidades:** sección censal (≈4.500, a verificar) para el detalle y los 179 municipios para el contexto.

## 2. Datos
### Vulnerabilidad por sección censal
| Variable | Fuente | Último año | Nota |
|---|---|---|---|
| Renta por persona y por unidad de consumo; % con ingresos < 60 % de la mediana; Gini | INE, Atlas de Distribución de Renta | ≈2023 | Serie 2015– |
| Peso de las prestaciones por desempleo en los ingresos | INE, Atlas | ≈2023 | Proxy del paro por sección |
| Peso de las pensiones en los ingresos | INE, Atlas | ≈2023 | |
| % mayores de 65 y de 80, % extranjeros | **INE, Padrón continuo por sección** | 1/1/2025 | Actualiza edad y nacionalidad sin depender del Censo |
| Nivel de estudios, hogares unipersonales de mayores, régimen de tenencia | INE, Censo 2021 | 2021 | Solo existe para ese año |

- **Antigüedad de los datos (en 2026):** cada variable va con su año de referencia. No se actualiza nada con supuestos. La renta (≈2023) y el Censo (2021) son estructurales y cambian despacio a escala de sección; se declara como limitación.
- Las secciones cambian entre años: se fija una cartografía de referencia y se reasignan los datos con la tabla de equivalencias del INE.
- **% extranjeros: se incluye.** Se presenta como variable de composición, no como causa, y se informa del índice con y sin ella (sensibilidad) para evitar que se lea como estigma.

### Índice municipal (#10), solo con variables de cobertura completa
| Variable | Fuente | Decisión |
|---|---|---|
| Paro registrado (tasa) | Comunidad | Entra |
| Discapacidad reconocida (tasa) | Comunidad | Entra |
| Dependencia (tasa) | Comunidad | Entra |
| Renta | INE | Entra |
| Envejecimiento | Padrón | Entra |
| Esperanza de vida (>100k) | Comunidad | Fuera del índice; **validación externa** |
| Valor tasado (>25k) | Comunidad | Fuera |
| Energía facturada | Comunidad | **Fuera** (no tiene una lectura clara) |

### Accesibilidad
| Componente | Fuente | Estado / riesgo |
|---|---|---|
| Atención primaria | Comunidad | **Verificar a mano**: existencia y coordenadas; geocodificar si solo hay dirección |
| DEA | Comunidad | **Verificar a mano**; separar los de acceso público |
| Colegios | Comunidad | **Verificar a mano**; filtrar por nivel y titularidad |
| Paradas | GTFS del CRTM (localizado en A) | Disponible |
| Red peatonal y viaria | OpenStreetMap + r5py | Se reutiliza lo de A |
| Geometrías de sección | INE | Disponible |
| Tipo de territorio | DEGURBA por municipio | Disponible |
| **Puntos de origen ponderados por población** | **Catastro INSPIRE (edificios residenciales con nº de viviendas)**; rejilla de 1 km del INE como alternativa en zona rural | Elegido frente al centroide geométrico |

- Reparto de la población de cada sección entre sus edificios en proporción al número de viviendas. La rejilla de 1 km es más gruesa que muchas secciones urbanas, así que solo sirve de respaldo.
- **Dimensión temporal:** foto actual de la accesibilidad. La única serie es la de la vulnerabilidad (renta desde 2015, paro).

## 3. Modelo
### A. Vulnerabilidad oculta: un mismo índice a dos escalas
- **Resultado principal:** índice por sección, agregado al municipio con la media ponderada por población.
- **Vulnerabilidad oculta** = secciones del quintil regional más vulnerable situadas en municipios cuya media no está en ese quintil (dispersión dentro del municipio).
- **El #10 municipal** (paro, discapacidad, dependencia…) se muestra **solo como capa de contexto**, sin cruce directo con la sección. Motivo: comparar índices con variables distintas confunde lo que oculta la media con lo que se mide distinto.

### B. Construcción de los índices (Handbook de composite indicators de la OCDE y el JRC)
1. Tasas por habitante.
2. Recorte de extremos (*winsorize*) en P1–P99.
3. Normalización con z-score.
4. Media aritmética con pesos iguales.
- Diagnóstico de redundancia con correlaciones y PCA (solo diagnóstico, no para fijar pesos).
- **Sensibilidad:** Monte Carlo con pesos Dirichlet y agregación geométrica frente a aritmética. Se publican el intervalo de ranking por zona y el Spearman medio. "Vulnerable robusta" = en el quintil superior en la mayoría de las simulaciones.

### C. Accesibilidad
| Servicio | Urbano / intermedio | Rural |
|---|---|---|
| DEA (de acceso público) | ≈3–4 min a pie (≈300 m) | igual |
| Parada de transporte | 5 min (≈400 m) | 10 min |
| Colegio (infantil / primaria) | 15 min a pie | 15 min en coche |
| Atención primaria | 15 min a pie | 15–20 min en coche |
- Velocidad a pie: 4,8 km/h general; **3,5 km/h para mayores, como opción en un desplegable** (se precalculan las dos).
- Métrica: tiempo al servicio más cercano y acceso binario según el umbral. Sin 2SFCA (no hay datos de cupos ni de plazas).
- Tipo de territorio según DEGURBA por municipio.

### D. Priorización: dónde intervenir
- **Candidatos:** rejilla de 250 m en suelo urbano, con **tiempo real por la red** (r5py) precalculado candidato → puntos de origen.
  - Pinchar en cualquier punto del mapa → se ajusta a la celda más cercana (error ≤ 125 m).
  - **Alternativa** si el tamaño de los datos no cabe en una web estática: distancia en línea recta calculada en el navegador.
- **Dos objetivos, a elegir en la app** (se precalculan los dos):
  1. **Ponderado:** Σ población × puntuación de vulnerabilidad.
  2. **Personas vulnerables:** solo la población del quintil más vulnerable ("N personas vulnerables más con acceso").
- La ganancia se calcula **a nivel de punto de origen**, no de sección: solo cuenta la población que hoy no tiene acceso.
- **Algoritmo voraz de cobertura máxima** (submodular: garantía ≥ 1 − 1/e ≈ 63 % del óptimo; en la app, la versión perezosa del algoritmo). El JS solo suma sobre la matriz precalculada.
- Estimación del tamaño: unos 16.000 candidatos × unos 60.000 puntos de origen (agregados a 100 m), guardando solo los pares dentro del umbral (matriz dispersa, binaria, un fichero por servicio y velocidad, cargado bajo demanda). **Verificar el tamaño real en la prueba.**

## 4. Análisis (dirigido a la Administración)
Preguntas que responde: ¿la media municipal oculta algo?, ¿la falta de acceso es regresiva? y ¿cuánto se gana priorizando con la sección?

1. **Mapa de vulnerabilidad por sección, con su robustez:** intervalo de ranking del Monte Carlo; se marcan las secciones "vulnerables" que solo lo son con ciertos pesos.
2. **Cuánta vulnerabilidad oculta la media:**
   - descomposición de la varianza del índice entre municipios y dentro de cada municipio;
   - **índice de Theil** de la renta, descompuesto igual. Titular: "el X % de la desigualdad está dentro de los municipios";
   - población vulnerable en municipios "sanos" y ranking de municipios con más dispersión interna.
3. **Equidad de acceso:** población sin acceso por quintil de renta y por edad, para cada servicio; **índice de concentración** con intervalo de confianza por *bootstrap*.
4. **Doble penalización:** secciones vulnerables y sin acceso (cuadrante crítico), y cuántas están en municipios que la media no señala. Es el mapa central.
5. **Medición del valor (contrafactual):** con el mismo número N de servicios nuevos, se comparan:
   - **(i) estrategia municipal:** se priorizan los municipios por su media y el servicio se coloca en el punto más poblado sin acceso;
   - **(ii) estrategia por sección:** nuestra optimización.

   Curva de población vulnerable cubierta frente a N. La diferencia entre las curvas es el valor demostrable del proyecto.
6. **Validación externa:**
   - correlación con la esperanza de vida, donde hay dato;
   - concordancia espacial (por solapamiento, no fila a fila) con el índice de vulnerabilidad por barrios del Ayuntamiento de Madrid y con los barrios vulnerables del Atlas de Vulnerabilidad Urbana del Ministerio.
7. **Evolución 2015–2023:** subíndice solo con las variables del Atlas de Renta, que tienen serie; secciones que han empeorado o mejorado. No se mezcla con el índice completo. Da la dimensión temporal del proyecto.

## 5. Herramienta
### Arquitectura (reutiliza la de la Propuesta A)
- **Pipeline en Python (offline, reproducible)** que exporta todo lo pesado:
  - índices por sección y municipio, con sus intervalos de ranking;
  - tiempos a servicios (dos velocidades);
  - matrices dispersas candidato → puntos de origen;
  - polígonos simplificados;
  - índice de calles.
- **App 100 % estática** en GitHub Pages: sin servidor, sin peticiones a terceros, librerías incluidas en el repositorio, mapa base propio en PMTiles.
  - Sin lógica pesada en JS: el JS solo consulta, suma, ejecuta el algoritmo voraz sobre la matriz precalculada y pinta.
  - **Pruebas de referencia:** Python genera casos con resultado conocido (cobertura, voraz, índice de concentración) y el JS tiene que reproducirlos.
  - Validación estricta de entradas; ninguna entrada se inserta como HTML.
- **Licencias:** MIT para el código y CC BY 4.0 para los datos derivados, citando las fuentes. Revisar las licencias del CRTM, el Catastro y CartoCiudad.

### Una sola app con dos pestañas
Comparten mapa, datos y código; en la demo se pasa de una a otra sin cortes.

**Pestaña Ciudadanía: "¿qué tengo a mano?"**
- Localización, de tres formas, todas sin enviar la dirección a terceros:
  1. pinchar en el mapa;
  2. **buscador de calles offline** (índice precalculado de calles por municipio, a partir de CartoCiudad o del Catastro; después se pincha en la calle);
  3. geolocalización del navegador, procesada en local.
- Salida:
  - tiempo a cada servicio y si cumple el umbral, según la velocidad elegida (general o mayores);
  - su sección frente a su municipio y frente a la Comunidad, en percentiles;
  - aviso si su zona es de "prioridad de intervención oculta".
- **Sin ranking público de secciones** en esta pestaña.

**Pestaña Administración: simulador**
- Capas: prioridad de intervención (vulnerabilidad por sección, con incertidumbre), acceso por servicio, doble penalización, #10 municipal como contexto, evolución 2015–2023.
- Controles: servicio, objetivo (ponderado o personas vulnerables) y velocidad.
- **Colocación manual** (pinchar → +X personas vulnerables con acceso) y **"sugerir N ubicaciones"** (algoritmo voraz perezoso).
- Métricas en vivo: población ganada, índice de concentración antes y después, curva frente a la estrategia municipal (contrafactual interactivo).
- **Rankings reales** de secciones y municipios disponibles en esta pestaña y en el informe.
- **Comparar dos escenarios guardados** lado a lado (métricas y mapa).
- **Exportar** el escenario a CSV o GeoJSON.

### Lenguaje y estigma
- En la interfaz se habla de **"prioridad de intervención"**, no de "barrio vulnerable".
- Se muestra la incertidumbre (intervalo de ranking).
- Los rankings completos están en la pestaña de Administración y en el informe, así que **en la exposición se pueden mostrar sin problemas**.
- Nota: en una web estática no hay control de acceso real; la separación es de diseño, no de seguridad. No supone un problema, porque todo deriva de datos abiertos.

### Informe de análisis
- Quarto publicado como página estática en el mismo repositorio, enlazado desde la app. Incluye los bloques 1–7 de la Fase 4 y la metodología.

### Servidor MCP (suma ante el jurado)
- Python (stdio), leyendo las mismas tablas precalculadas. Validación estricta de argumentos y sin credenciales.
- Herramientas:
  - `acceso_desde(lat, lon, velocidad)`;
  - `indicadores_seccion(codigo)`;
  - `vulnerabilidad_oculta(municipio)`;
  - `sugerir_ubicaciones(servicio, n, objetivo)`.
- Demo: preguntas en lenguaje natural desde Claude.

### Interoperabilidad: Smart Data Models
- Revisar los modelos existentes para puntos de servicio (sanitarios, POI) y los modelos GTFS de *UrbanMobility*.
- Publicar los indicadores por sección en un esquema existente o proponer uno nuevo (un indicador de accesibilidad y vulnerabilidad).
- Clave de cruce: código INE de sección y de municipio + año.

## 6. Presentación y entrega (SOLO ORIENTATIVA)
> Esta fase se detallará al final, cuando el equipo conozca el formato. **No se debe dedicar trabajo ni créditos a esta parte hasta entonces.** Las fechas las gestiona el equipo.

- Entregables previstos: web publicada, repositorio reproducible, informe de análisis y presentación.
- Narrativa orientativa:
  1. el titular: "la media municipal oculta el X % de la desigualdad";
  2. un caso concreto: una sección de prioridad oculta, vista desde la pestaña Ciudadanía;
  3. el simulador: sugerir N ubicaciones frente a la estrategia municipal (la curva del contrafactual);
  4. la parte técnica: datos de la Comunidad, Smart Data Models, código abierto, MCP.
- Responder explícitamente a cada criterio publicado: uso de datos regionales, viabilidad y código abierto.
- Exponer las limitaciones por iniciativa propia: antigüedad de la renta y del Censo, foto actual de los servicios, umbrales normativos elegidos, línea recta si se usa la alternativa.

## Pendientes y verificaciones
- [ ] Conjuntos de la Comunidad de centros sanitarios, DEA y centros educativos: existencia, coordenadas y fecha de actualización (la API CKAN bloquea el acceso automático; comprobar a mano).
- [ ] Último año publicado del Atlas de Renta por sección y del Padrón por sección.
- [ ] Catastro INSPIRE: descarga para la Comunidad y atributo de número de viviendas por edificio.
- [ ] Tabla de equivalencias de secciones del INE entre años.
- [ ] Índice de calles: CartoCiudad o Catastro; licencia y tamaño.
- [ ] Prueba de r5py: matriz candidato → origen para un municipio metropolitano; medir tiempo de cálculo y tamaño del fichero.
- [ ] Índice de vulnerabilidad del Ayuntamiento y Atlas de Vulnerabilidad Urbana: disponibilidad y geometrías para la validación.
- [ ] Revisar la carpeta `pysmartdatamodels/` del repositorio de la organización.
- [ ] (Gestión del equipo, al final) Confirmar con la organización: pesos de los criterios, formato de entrega, duración de la presentación y criba de 100 palabras.
