# Datos y fuentes

De dónde sale cada pieza de la cuenta de Kuanto: quién publica el dato, de qué año es, a qué escala llega y con qué licencia. Es para quien quiera saber en qué se apoyan las cifras o reutilizarlas.

Todo sale de datos públicos. Ni el INE, ni el Ministerio de Vivienda y Agenda Urbana, ni la Agencia Tributaria, ni el CRTM, ni la Comunidad de Madrid participan en el proyecto ni lo patrocinan.

## Qué fuente aporta cada pieza

| Pieza | Fuente | Año o versión | Escala | Licencia |
|---|---|---|---|---|
| Zonas | Secciones censales del INE, población del Atlas de Distribución de Renta de los Hogares (ADRH), coronas tarifarias del CRTM y edificios de OpenStreetMap (centro de población) | Secciones a 1-1-2025, población de 2024 | 178 municipios y 21 distritos | CC BY 4.0 (INE); licencia del CRTM; ODbL 1.0 (OpenStreetMap) |
| Sueldo neto | Ley del IRPF, Decreto Legislativo 1/2010 de la Comunidad de Madrid, Orden PJC/297/2026 de cotización y RDL 5/2026 (BOE) | Parámetros de 2026 | Persona | Reutilización con cita del BOE |
| Alquiler | SERPAVI del Ministerio de Vivienda y Agenda Urbana: alquileres de vivienda colectiva declarados a Hacienda | Último año 2024, fichero actualizado el 2026-07-09 | Municipio y distrito de Madrid (las secciones censales solo se usan en el informe) | Condiciones de reutilización del Ministerio |
| Alquiler llevado a hoy | IPC del alquiler de la Comunidad de Madrid (INE) | Hasta 2026-10 | Comunidad | CC BY 4.0 |
| Ajuste a contrato nuevo | Estadística de viviendas declaradas en el IRPF de la Agencia Tributaria | 2024 | Municipio de más de 20.000 habitantes y código postal, repartido a distritos con portales de OpenStreetMap | Reutilización citando la fuente; ODbL 1.0 |
| Transporte | Tarifas del CRTM publicadas en el BOCM, descuento del RDL 17/2025, calendario laboral del Decreto 75/2025 y fichas de títulos del CRTM | Precios de 2026 | Corona tarifaria | Disposiciones oficiales; aviso legal y licencia de datos abiertos del CRTM; ODbL 1.0 |
| Tiempos de viaje | Horarios GTFS del CRTM y red de calles de OpenStreetMap, calculados con r5py | GTFS descargados el 2026-11-15; OpenStreetMap del 2026-11-13 | De zona a zona | Licencia del CRTM; ODbL 1.0 |
| Coche | Coste por kilómetro de la Orden HFP/792/2023 y red de calles de OpenStreetMap | 0,26 €/km, Orden de 2023 | De zona a zona | Reutilización con cita del BOE; ODbL 1.0 |
| Cesta básica | Encuesta de Presupuestos Familiares (EPF) de la Comunidad de Madrid, IPC por subgrupos del INE y EPF de España por nivel de ingresos | EPF de 2025, IPC hasta 2026-10 | Comunidad (España para el tramo de ingresos y el IPC del agua) | CC BY 4.0 |

Fuente de la tabla: la sección [De dónde sale cada pieza](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-fuentes) de la nota metodológica y el bloque `meta.fuentes` de cada fichero de [`app/datos/`](../app/datos/LEEME.md).

El [informe de análisis](https://yeraybc.github.io/DataMad-hackaton-2026/informe.html#titulo-fuentes) usa además la renta por sección del ADRH, el Bono Alquiler Joven del catálogo de la Comunidad de Madrid, la Encuesta de Condiciones de Vida (ECV) y el Censo de 2021 del INE. Sus fuentes están en la sección «Fuentes» del propio informe.

## Cómo se ponen de acuerdo las fuentes

Cada publicador da su dato a su manera: con su propio mapa, su año, su unidad y su formato. Para poder restarlos, Kuanto los lleva antes a una misma medida:

| Qué se iguala | Cómo |
|---|---|
| El territorio | Todo se expresa por zona, con un único código: el del INE para cada municipio y el de Madrid más el número de distrito para los distritos. Las secciones censales de 2021, que usa el SERPAVI, se pasan a las de 2025, que usa el INE, repartiendo según dónde vive la gente (`paso_secciones.py`). Los datos de Hacienda por código postal se reparten entre distritos con los portales de OpenStreetMap |
| El momento | Los precios de años anteriores se llevan a octubre de 2026 con el IPC, y las normas y tarifas son todas de 2026 |
| La unidad | Todo pasa a euros al mes de un hogar: el neto anual entre 12, la cesta anual por unidades de consumo entre 12, y las horas de viaje con las semanas laborables reales de 2026 |
| El formato | Cada fichero publicado tiene la misma estructura: un bloque `meta` con la fecha, el año del dato, las fuentes con su licencia y una nota de método. Lo que falta es `null`, nunca cero. Antes de publicarse, cada tabla se comprueba contra su esquema (`contratos.py` y `api_estatica.py`) |

Esa normalización también sirve hacia fuera. Los indicadores de alquiler y de esfuerzo se publican además en [Smart Data Models](https://smartdatamodels.org/), un estándar abierto de modelos de datos para ciudades y territorios. Se usa el modelo `KeyPerformanceIndicator` en formato NGSI-LD: una entidad por indicador, zona y año, con el código INE de la zona, el periodo y la descripción con su unidad ([`app/datos/sdm/`](../app/datos/sdm/LEEME.md)). Así otra plataforma que hable ese estándar, como un gestor de datos urbanos, puede leer los indicadores de Kuanto sin adaptarlos. La CI valida cada entidad contra el esquema oficial del modelo. El catálogo de todos los ficheros va además en DCAT-AP, el estándar de los catálogos de datos abiertos europeos ([`dcat.jsonld`](../app/datos/dcat.jsonld)).

## Qué es dato y qué es estimado

Un dato publicado se usa tal cual, con su fecha. Cuando hace falta un paso más, como llevar el alquiler de 2024 a hoy con el IPC, ajustarlo a contrato nuevo, repartir la cesta por tamaño de hogar o reconstruir un horario que falta, la cifra lleva la marca «estimado» y el supuesto queda escrito en la nota de su fichero. La lista está en [Qué está estimado](../app/datos/LEEME.md#qué-está-estimado).

## Dónde está cada cosa

| Necesitas… | Dónde |
|---|---|
| La licencia de cada fichero que publica Kuanto y la cita que exige cada fuente | [Datos abiertos de Kuanto](../app/datos/LEEME.md) |
| La URL, la fecha y la huella SHA-256 de cada descarga original | [`data/README.md`](../data/README.md) |
| La misma descripción, legible por máquinas (DCAT-AP) | [`app/datos/dcat.jsonld`](../app/datos/dcat.jsonld) |
| Las columnas de los ficheros descargados más grandes | [`docs/datos/`](datos/) |
| La comprobación de fuentes, normas y licencias con el publicador | [`docs/verificaciones/`](verificaciones/) |
| Cuándo caduca cada dato | [Mantenimiento](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-mantenimiento), en la nota metodológica |
