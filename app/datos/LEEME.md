# Datos abiertos de Kuanto

Esta carpeta es la API estática de Kuanto, la herramienta del equipo de DataMad 2026 para la Comunidad de Madrid. Son ficheros JSON y GeoJSON que la web, el asistente y el informe leen tal cual, y que cualquiera puede reutilizar. Los datos son derivados: salen de fuentes oficiales y de OpenStreetMap, con cálculos del equipo encima. Lo estimado está marcado en la `nota` del bloque `meta` de cada fichero.

La descripción en DCAT-AP, legible por máquinas, está en [dcat.jsonld](dcat.jsonld). Ahí constan, por fichero, la licencia, la fecha, el tamaño, el periodo, la cobertura y las fuentes con su licencia y su cita.

## Dónde se descargan

Cada fichero se publica en `https://yeraybc.github.io/DataMad-hackaton-2026/datos/` seguido de su ruta. La web del proyecto está en https://yeraybc.github.io/DataMad-hackaton-2026/ y el código en https://github.com/yeraybc/DataMad-hackaton-2026. Para dudas o errores, abre una issue en https://github.com/yeraybc/DataMad-hackaton-2026/issues.

## Licencia por fichero

La licencia de cada fichero es la de los datos derivados. Las fuentes conservan sus propias condiciones, que se resumen más abajo.

| Fichero | Licencia | Motivo |
|---|---|---|
| `alquiler.json` | ODbL 1.0 | Reparte códigos postales con portales de OpenStreetMap |
| `tiempos.json` | ODbL 1.0 | Usa la red viaria y los edificios de OpenStreetMap |
| `zonas.geojson` | ODbL 1.0 | El centro de cada zona sale de los edificios de OpenStreetMap |
| `analisis.json` | CC BY 4.0 | No usa OpenStreetMap |
| `hogares.json` | CC BY 4.0 | No usa OpenStreetMap |
| `netos.json` | CC BY 4.0 | No usa OpenStreetMap |
| `tarifas.json` | CC BY 4.0 | No usa OpenStreetMap |
| `sdm/alquiler_eur_m2_p50.json` | CC BY 4.0 | Solo usa la mediana del SERPAVI, no OpenStreetMap, y sigue las condiciones del Ministerio de Vivienda y Agenda Urbana |
| `sdm/esfuerzo.json` | CC BY 4.0 | Combina el SERPAVI y la renta del INE |

Texto de las licencias: [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) y [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). La ODbL obliga a publicar con la misma licencia las bases de datos derivadas de OpenStreetMap, y la decisión sobre qué ficheros la llevan consta en `docs/decisiones.md`.

## Cómo citarlo

Texto sugerido, con el fichero que uses y su fecha de generación (`meta.generado`):

> Equipo Kuanto (DataMad 2026), `<fichero>`, generado el `<fecha>`. https://yeraybc.github.io/DataMad-hackaton-2026/datos/`<fichero>`. Datos derivados de fuentes oficiales y de OpenStreetMap, con licencia `<ODbL 1.0 o CC BY 4.0>`.

Además, cada fuente pide su cita. Quien reutilice un fichero debe incluir las de las fuentes que figuran en su `meta.fuentes` y en su distribución de [dcat.jsonld](dcat.jsonld), con la fecha de actualización del original que da `meta.nota`:

- INE: «Elaboración propia con datos extraídos del sitio web del INE: www.ine.es». El INE no participa, patrocina ni apoya este proyecto, y ninguna cifra derivada debe presentarse como si fuera del INE.
- Ministerio de Vivienda y Agenda Urbana (SERPAVI): «Origen de los datos: Ministerio de Vivienda y Agenda Urbana», con la fecha de actualización del fichero. El Ministerio no avala el proyecto.
- Comunidad de Madrid: «Fuente de los datos: Comunidad de Madrid», con la fecha de actualización, indicando que los datos se han modificado.
- OpenStreetMap: «© OpenStreetMap contributors».
- Consorcio Regional de Transportes de Madrid: «Powered by CRTM».
- Boletín Oficial del Estado: «Basado en datos de la Agencia Estatal Boletín Oficial del Estado».
- Agencia Tributaria: «Fuente: Agencia Tributaria», sin desnaturalizar la información.

## Qué está estimado

Los ficheros mezclan datos observados con estimaciones y supuestos. La `nota` de cada `meta` dice cuáles, y las palabras «estimado» y «supuesto» marcan cada uno. Entre ellos están el factor del IPC y el factor de contratos nuevos del alquiler, los kilómetros y el coste en coche, parte de los tiempos en transporte público, la cesta por tramo de ingresos y las simulaciones del Bono y del fin del descuento. Los totales de las simulaciones no son datos de los publicadores.

## Limitaciones abiertas

- [#438](https://github.com/yeraybc/DataMad-hackaton-2026/issues/438): con transbordo, la ruta en interurbano hasta la terminal T4 del aeropuerto no cobra el suplemento de Metro en `tarifas.json`, y ni `nota_ruta` ni la metodología lo explican. <!-- sin-fuente: número de issue -->
- [#439](https://github.com/yeraybc/DataMad-hackaton-2026/issues/439): faltan en las fuentes de `netos.json` y `tarifas.json` las fechas de última actualización de los textos consolidados del BOE. <!-- sin-fuente: número de issue -->

## Estructura común

Salvo `sdm/`, cada fichero lleva un bloque `meta` con `generado` (fecha de generación), `anio_dato` (año del dato), `fuentes` (nombre, URL y licencia de cada una) y `nota`. Algunos añaden `ipc_hasta` (mes del último IPC aplicado), `min_testigos`, `nota_ruta` o `fuentes_ruta`. Todo va en UTF-8 y `null` marca lo que falta. Las claves de zona son `zona_id`: el código INE de 5 dígitos del municipio, o `28079` seguido del distrito de 2 dígitos en los distritos de Madrid. Los recuentos que siguen salen de un script que cuenta los propios ficheros.[^recuento]

[^recuento]: fuente: recuento de elementos de los propios ficheros de `app/datos/`, hecho con un script sobre la versión congelada el 2026-11-23.

## Diccionario por fichero

### `zonas.geojson`

Grano: una zona por feature (178 municipios y 21 distritos de Madrid).[^recuento] Clave: `properties.zona_id`. Año del dato: 2024, la población del ADRH del INE. Generado el 2026-11-21.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `zona_id` | texto | código INE de la zona |
| `nombre` | texto | |
| `tipo` | texto | `municipio` o `distrito` |
| `municipio_id` | texto | código INE del municipio |
| `corona` | texto | corona tarifaria del CRTM: `A`, `B1`, `B2`, `B3`, `C1`, `C2` |
| `poblacion` | entero | habitantes en 2024 |
| `geometry` | Polygon o MultiPolygon | EPSG:4326, simplificada con 20 m de tolerancia, sin huecos entre zonas vecinas <!-- sin-fuente: código EPSG y tolerancia, no datos --> |

Las zonas salen de disolver las secciones censales del INE a 1-1-2025. Fuentes: INE (seccionado y tabla de población), CRTM (coronas) y OpenStreetMap (centro de población).

### `tiempos.json`

Grano: origen por destino. Clave: la posición en `origenes` y en `destinos`. Año del dato: 2026, con salidas el martes 2026-11-17 entre las 7:30 y las 8:30. Generado el 2026-11-21.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `origenes` | lista de texto | `zona_id` de cada fila, 199 zonas[^recuento] |
| `destinos` | lista de objetos | `destino_id`, `nombre`, `tipo` (`zona` o `polo`) y, solo en los polos, `zona_id`; 215 destinos, 16 de ellos polos de empleo con nombre[^recuento] |
| `tp` | matriz de enteros | minutos puerta a puerta en transporte público, `tp[origen][destino]`; `null` si pasa de 120 min, no hay ruta o falta el horario <!-- sin-fuente: umbral del cálculo --> |
| `coche` | matriz de enteros | minutos en coche, sin tráfico |
| `km_coche` | matriz de decimales | kilómetros, estimados: línea recta por un factor de rodeo |
| `coste_coche.eur_km` | decimal | euros por kilómetro, un supuesto |

Parte de los tiempos en transporte público es estimada: se reconstruyen líneas u horarios que el CRTM publica incompletos, y el fichero no dice cuáles. La nota da los detalles y el calendario supuesto de Metro. Fuentes: CRTM (GTFS y coronas), OpenStreetMap y el BOE para el coste por kilómetro.

### `alquiler.json`

Grano: una zona. Clave: `zonas[zona_id]`, con las 199 zonas.[^recuento] Año del dato: 2024, el último con dato de cada zona (`anio` lo dice, y alguna zona va con 2023). Generado el 2026-11-23.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `anio` | entero o null | último año con dato de la zona |
| `p25`, `p50`, `p75` | decimal o null | euros por m² al mes de vivienda colectiva, en euros de `anio`; null si no hay dato |
| `m2` | decimal o null | metros cuadrados de la vivienda mediana |
| `testigos` | entero o null | inmuebles con alquiler declarado, solo en las zonas observadas |
| `factor_ipc` | decimal | factor que actualiza el precio al mes de `meta.ipc_hasta` con el IPC de alquiler, estimado |
| `factor_brecha` | decimal | factor que lleva el precio al de los contratos nuevos, estimado |
| `brecha_ambito` | texto | de dónde sale el factor: `municipio`, `codigo_postal` o `tramo` |
| `brecha_pureza` | decimal o null | parte del peso que viene de códigos postales enteros, entre 0 y 1; con pureza baja el valor depende del reparto |
| `origen` | texto | `observado`, `estimado` o `sin_dato` |
| `ic` | lista o null | intervalo `[inf, sup]`, solo si el origen es `estimado` |

Los valores del SERPAVI son medianas de contratos declarados a la Agencia Tributaria, no de anuncios. En esta versión las zonas son `observado` o `sin_dato`, y `ic` va siempre en null. Fuentes: SERPAVI (MIVAU), IPC del INE y de la Comunidad de Madrid, Agencia Tributaria y OpenStreetMap.

### `netos.json`

Grano: bruto anual por configuración familiar. Clave: la posición en `brutos` y en `configuraciones`. Año del dato: 2026. Generado el 2026-11-23.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `brutos` | lista de enteros | euros brutos al año, de 12.000 a 120.000 <!-- sin-fuente: rango de la rejilla, un parámetro del fichero y no un dato --> |
| `configuraciones` | lista de objetos | `hijos` (de 0 a 5) y `monoparental` (booleano) |
| `neto_anual` | matriz de decimales | euros netos al año de 2026, `neto_anual[bruto][configuracion]` |

Es el neto tras la cotización del trabajador y el IRPF estatal y de Madrid, con tributación individual, contrato indefinido y menor de 65 años. No incluye las deducciones reembolsables de la LIRPF para familias ni la de Madrid por alquiler, y fuera de la rejilla no extrapola. <!-- sin-fuente: edad del supuesto del cálculo --> Fuentes: BOE (LIRPF y normas de cotización) y el Decreto Legislativo de Madrid sobre tributos cedidos.

### `tarifas.json`

Grano: título de transporte por escenario, edad, corona y días de trabajo. Año del dato: 2026. Generado el 2026-11-23.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `orden_coronas` | lista de texto | `A` a `C2` |
| `edad_max_joven` | entero | edad máxima del Abono Joven |
| `viajes_dia` | lista de enteros | 2 (ida y vuelta directa) o 4 (con cambio de operador en cada sentido) |
| `semanas_mes` | decimal | semanas por mes que usa el cálculo |
| `escenarios` | objeto | `escenarios[escenario][edad][viajes_dia][corona]` es una lista de cinco objetos, uno por días de trabajo a la semana de 1 a 5, con `titulo` y `coste_mes` (euros al mes) |
| `clave_estimada` | booleano | si el rango de coronas de cada ruta es una estimación |
| `origenes`, `destinos` | listas de texto | `zona_id` de origen y `destino_id` de destino de las rutas: los mismos que en `tiempos.json`, pero los destinos van en otro orden, así que se cruzan por `destino_id` y no por posición |
| `claves` | lista de texto | rango de coronas y producto de cada ruta, con la forma `A-B1\|interurbano` |
| `clave_tarifa` | matriz de enteros | posición en `claves` de cada ruta, `clave_tarifa[origen][destino]` |
| `transbordo` | lista de enteros o null | para cada clave, la posición de la misma ruta con transbordo |
| `colectivos`, `edades` | listas de texto | colectivos de precio (ordinario, discapacidad y familia numerosa) y tramos de edad |
| `no_laborables` | lista de enteros | viajes de ocio al mes que admite el cálculo |
| `tarifas_ruta` | objeto | `[escenario][colectivo][edad][clave][ocio]` es la lista de cinco costes mensuales por días de trabajo |

Los escenarios son `vigente_2026`, con el descuento que solo vale en 2026, y `sin_descuento`, con los precios oficiales. `coste_mes` es una media mensual del año, estimada con los supuestos de días de trabajo que detalla la `nota`. El rango de coronas de cada ruta se estima con la recta entre los centros de las zonas y subestima el coste entre periferias. Limitación abierta: #438 <!-- sin-fuente: número de issue -->. Fuentes: BOCM, CRTM y BOE.

### `hogares.json`

Grano: perfil de hogar. Clave: nombre del perfil. Año del dato: 2025, en euros de 2025 actualizados con el IPC hasta `meta.ipc_hasta`. Generado el 2026-11-23.

| Campo | Tipo | Unidad o valores |
|---|---|---|
| `perfiles` | objeto | cuatro perfiles: `solo`, `comparte`, `pareja` y `monoparental` |
| `perfiles.*.m2` | entero | metros cuadrados por defecto, el mismo para todos |
| `perfiles.*.adultos`, `hijos`, `personas_comparten` | entero | composición del hogar |
| `perfiles.*.alimentacion`, `suministros`, `comunicaciones` | decimal | euros al mes, gasto medio estimado |
| `cesta_uc` | objeto | `alimentacion`, `suministros` y `comunicaciones` en euros al mes por unidad de consumo, para recalcular la cesta con el hogar del visitante |
| `cesta_tramos` | lista de objetos | `desde` (ingresos netos mensuales del hogar, en euros) y `factor` (cociente de alimentación del tramo, estimado) |

Es un gasto medio, no un mínimo. Los metros cuadrados por defecto repiten la mediana ponderada del SERPAVI para todos los perfiles, lo que sobrestima el alquiler de quien vive solo. Fuentes: EPF del catálogo de la Comunidad de Madrid, IPC del INE, EPF del INE y SERPAVI (MIVAU).

### `analisis.json`

Cuatro bloques, cada uno con su grano. Año del dato: 2024; el bloque `esfuerzo` lleva la serie de 2015 a 2024, con el año en cada fila. Generado el 2026-11-23.

| Bloque | Grano y clave | Campos |
|---|---|---|
| `esfuerzo` | zona por año: `zona_id`, `anio` | `alquiler_mes_p50` y `renta_hogar_mes` (decimales, euros al mes); `esfuerzo` (decimal, fracción de la renta); null si falta alguno. Además de las 199 zonas lleva `28079`, Madrid entero[^recuento] |
| `bono` | municipio: `municipio_id` | `solicitudes`, `aceptadas`, `rechazadas` y `poblacion_joven` (enteros, convocatoria de 2022); `necesidad` (decimal); `indicador_necesidad` (texto); `grupo` (texto, cruce de necesidad y ayuda, o `sin_dato`) |
| `simulacion` | perfil por municipio por criterio | `perfil`, `municipio_id`, `criterio` (textos); `elegible` (booleano); `eur_mes` (decimal, euros al mes); `estimado` (booleano); `pct_ocupados_elegibles` (decimal, % de los ocupados de la zona, null si no aplica); `marca_imputada`, `marca_excluida` y `marca_pocos` (calidad del municipio) |
| `titulares` | titular | `texto` y `fuente` |

Todo lo del bloque `simulacion` es estimado: la simulación del Bono, la del fin del descuento del transporte y las horas de viaje. Fuentes: SERPAVI (MIVAU), tablas del INE, catálogo de la Comunidad de Madrid, BOCM y BOE. La lista completa está en [dcat.jsonld](dcat.jsonld).

### `sdm/`

Indicadores `alquiler_eur_m2_p50` y `esfuerzo` como entidades NGSI-LD del modelo KeyPerformanceIndicator de Smart Data Models: 158 entidades el primero y 1.512 el segundo.[^recuento] Sus valores salen de `alquiler.json` (`p50`) y de `analisis.json` (`esfuerzo`), sin recalcularse. Los campos, la procedencia y la cita de cada indicador están en [sdm/LEEME.md](sdm/LEEME.md). Los dos ficheros no llevan `meta`: su fecha es la del fichero de origen.

## Fuentes y sus licencias

| Publicador | Licencia | Ficheros |
|---|---|---|
| INE | CC BY 4.0 | `zonas`, `alquiler`, `analisis`, `hogares`, `sdm/esfuerzo` |
| Ministerio de Vivienda y Agenda Urbana (SERPAVI) | Condiciones de reutilización del MIVAU (RD 1495/2011) <!-- sin-fuente: número de la norma --> | `alquiler`, `analisis`, `hogares`, `sdm` |
| Comunidad de Madrid, catálogo de datos abiertos | CC BY 4.0 | `alquiler`, `analisis`, `hogares` |
| OpenStreetMap (extracto de Geofabrik) | ODbL 1.0 | `zonas`, `tiempos`, `alquiler` |
| CRTM | Licencia de datos abiertos del CRTM y aviso legal de crtm.es | `zonas`, `tiempos`, `tarifas` |
| Boletín Oficial del Estado | Reutilización con cita de la fuente | `netos`, `tarifas`, `tiempos`, `analisis` |
| BOCM | Disposición oficial, sin derechos de propiedad intelectual (art. 13 del TRLPI) <!-- sin-fuente: número de artículo --> | `analisis`, `tarifas` |
| Agencia Tributaria | Reutilización citando la fuente y sin desnaturalizar | `alquiler` |

Cada fuente, con su URL y el texto exacto de su licencia, está en [dcat.jsonld](dcat.jsonld) y en la sección de fuentes de `data/README.md`.
