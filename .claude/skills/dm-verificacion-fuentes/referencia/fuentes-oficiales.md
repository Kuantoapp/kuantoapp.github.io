# Fuentes oficiales: dónde y cómo verificar

Cómo comprobar en cada publicador que un dato o una norma existe, qué contiene y si se descarga. Comprobado en vivo el 12 y 13/11/2026. **Las URL y las API cambian**: si una falla, búscala en el catálogo del propio portal antes de darla por perdida.

**Contenido:** 1. BOE (Agencia Estatal BOE) · 2. BOCM (Comunidad de Madrid) · 3. INE · 4. datos.comunidad.madrid (CKAN 2.9.0) · 5. datos.madrid.es (Ayuntamiento, ahora CKAN 2.9.11) · 6. datos.gob.es (catálogo nacional, Linked Data API) · 7. Eurostat (API de diseminación) · 8. Catastro (DGC) · 9. CRTM (datos.crtm.es, ArcGIS Hub) · 10. Agencia Tributaria: estadística de los declarantes del IRPF por municipios · 11. Movilidad (Ministerio de Transportes), Seguridad Social y SEPE · Pauta mínima para el agente verificador (solo WebFetch) · No verificado

Comprobado en vivo el 12 y 13 de noviembre de 2026. Cada URL marcada **OK-WF** respondió a **WebFetch** (la herramienta del agente verificador). **OK-curl** = respondió a una petición HTTP real con curl, pero no se probó con WebFetch. **FALLA-WF** = WebFetch devolvió error aunque curl funcione. Sin nada de memoria: lo no comprobado está en «No verificado».

> Aviso clave para el agente verificador: **la API de datos abiertos del BOE (`/datosabiertos/api/...`) devuelve HTTP 400 con WebFetch** porque exige la cabecera `Accept: application/json` o `application/xml`, y WebFetch no la manda. Con WebFetch hay que usar `diario_boe/xml.php`, ELI `/dof/spa/xml` y las páginas HTML (ver ficha 1).

---

## 1. BOE (Agencia Estatal BOE)

**Publica:** el diario oficial del Estado (disposiciones, anuncios) y la legislación consolidada (estatal y autonómica, también la de Madrid).

| Uso | URL que funcionó | Estado | Formato |
|---|---|---|---|
| Sumario del día (HTML) | `https://www.boe.es/boe/dias/2026/11/12/` | OK-WF (núm. 282, BOE-S-2026-282) | HTML |
| Sumario del día (API) | `https://www.boe.es/datosabiertos/api/boe/sumario/20261111` + `Accept: application/json` | OK-curl; **400 sin Accept** | JSON/XML |
| Sumario XML antiguo `diario_boe/xml.php?id=BOE-S-20261112` | — | **FALLA-WF (400)** | — |
| Documento + metadatos + análisis | `https://www.boe.es/diario_boe/xml.php?id=BOE-A-2015-11430` | OK-WF | XML |
| ELI, versión oficial en XML | `https://www.boe.es/eli/es/rdlg/2015/10/23/2/dof/spa/xml` | OK-WF (mismo XML que `xml.php`) | XML |
| ELI, consolidado en HTML (versión a una fecha) | `https://www.boe.es/eli/es/rdlg/2015/10/23/2/con/20240101/spa/html` | OK-curl | HTML |
| ELI `/con/spa/xml` | `https://www.boe.es/eli/es/rdlg/2015/10/23/2/con/spa/xml` | **404** (curl) | — |
| Texto consolidado (HTML) | `https://www.boe.es/buscar/act.php?id=BOE-A-2020-3824` | OK-WF | HTML (PDF y EPUB enlazados: `/buscar/pdf/2015/BOE-A-2015-11430-consolidado.pdf`) |
| API consolidada, metadatos | `https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2015-11430/metadatos` | OK-curl con Accept; **FALLA-WF (400)** | JSON |
| API consolidada, análisis | `.../id/BOE-A-2020-3824/analisis` | OK-curl con Accept | JSON |
| API consolidada, índice del texto | `.../id/BOE-A-2015-11430/texto/indice` | OK-curl con `Accept: application/xml` | XML |
| API consolidada, búsqueda | `https://www.boe.es/datosabiertos/api/legislacion-consolidada?query={"query":{"query_string":{"query":"titulo:vivienda and departamento@codigo:8131"}}}&limit=3` (URL-encoded) | OK-curl con Accept (devolvió leyes de vivienda de Madrid: BOE-A-1997-19084, BOE-A-2026-16360, BOE-A-2024-15001) | JSON |
| Tabla de códigos de relaciones | `https://www.boe.es/datosabiertos/api/datos-auxiliares/relaciones-anteriores` | OK-curl con Accept | JSON |

**Metadatos que se pueden leer** (en `xml.php`, ELI `/dof/spa/xml` y en la API `/metadatos`): `fecha_actualizacion`, `rango`, `departamento` (8131 = Comunidad de Madrid), `fecha_disposicion`, `fecha_publicacion`, `fecha_vigencia`, `estatus_derogacion` (S/N), `estatus_anulacion`, `vigencia_agotada` (S/N), `estado_consolidacion` (3 = Finalizado), `url_eli`, `url_html_consolidada`.

**Vigente, derogada o convalidada:**
- **Vigencia:** `estatus_derogacion=N` y `vigencia_agotada=N`. Ejemplo comprobado: Estatuto de los Trabajadores (BOE-A-2015-11430): N/N, consolidación Finalizado, actualizado 20261110. La Ley 16/1998 de Madrid (BOE-A-1999-5470) sale con `vigencia_agotada=S`.
- **Derogación parcial y modificaciones:** bloque `<analisis>` → `referencias/posteriores` (en XML y en la API `/analisis`), con el código de relación: 210 = DEROGA, 270 = MODIFICA, 231 = SUSPENDE, 220 = ANULA, etc.
- **Convalidación de un real decreto-ley:** en referencias posteriores, la relación **301 «PUBLICA Acuerdo de convalidación»**. Ejemplo: el RDL 8/2020 (BOE-A-2020-3824) → `BOE-A-2020-4167`, «Resolución de 25 de marzo de 2020». Comprobado con curl en la API `/analisis`. En el XML de `xml.php` la palabra «convalidación» aparece (grep con curl), pero WebFetch no la llegó a leer porque el documento ocupa 396 000 caracteres: hay que pedir `offset`.
- La página `act.php` **no** dice el estado de forma explícita; usarla solo para el texto.

**Límites:** documentos XML muy largos (de 400 000 a 600 000 caracteres), así que WebFetch los trunca a 100 000 y hay que paginar con `offset`. El texto consolidado no tiene valor jurídico (lo dice la propia página).

---

## 2. BOCM (Comunidad de Madrid)

**Publica:** el diario oficial autonómico. CVE: `BOCM-AAAAMMDD-N`.

| Uso | Patrón y ejemplo | Estado |
|---|---|---|
| Anuncio en HTML | `https://www.bocm.es/bocm-20261111-1` | OK-curl |
| Anuncio en XML (metadatos) | `https://www.bocm.es/boletin/CM_Orden_BOCM/2026/11/11/BOCM-20261111-1.xml` | OK-WF |
| Anuncio en JSON-LD (schema.org Legislation) | `.../BOCM-20261111-1.json` | OK-curl (`application/ld+json`) |
| Anuncio en PDF firmado | `.../BOCM-20261111-1.PDF` | OK-curl (`application/pdf`) |
| EPUB | `.../BOCM-20261111-1.epub` | listado en el sumario, no descargado |
| Sumario del día en XML | `https://www.bocm.es/boletin/CM_Boletin_BOCM/2026/11/12/BOCM-20261112272.xml` (fecha + **número de boletín**, 272) | OK-WF |
| Sumario del día en HTML | `https://www.bocm.es/boletin/bocm-20261112-272` | OK-curl |
| Último boletín | `https://www.bocm.es/ultimo-bocm` | OK-curl |
| `bocm.es/cve/...`, `/boletin/bocm-20261111`, `/ultimo-boletin` | — | **404** |

**Cómo localizar un anuncio por fecha y número:** con el CVE se construye directamente `https://www.bocm.es/boletin/CM_Orden_BOCM/AAAA/MM/DD/BOCM-AAAAMMDD-N.xml` (el mismo patrón sirve para `.PDF` y `.json`). Para listar un día hace falta el número de boletín, que sale de `/ultimo-bocm` o de la home. Metadatos del XML: `identificador`, `origen_legislativo`, `departamento`, `rango`, `fecha_publicacion`, `titulo`, `url_pdf`. El sumario trae, por cada disposición, `url_html`, `url_xml`, `url_json_ld`, `url_pdf` y `url_epub`.

**Límites:** no hay API de búsqueda probada. `/advanced-search` es un formulario HTML (responde 200, no se probaron sus parámetros).

---

## 3. INE

**Publica:** estadísticas oficiales. API Tempus3 en `https://servicios.ine.es/wstempus/js/ES/{FUNCIÓN}/{id}`, que devuelve JSON sin cabeceras especiales.

| Función | Ejemplo que funcionó | Estado |
|---|---|---|
| `DATOS_TABLA` | `.../DATOS_TABLA/2881?nult=1&tv=18:451` (padrón por municipio de Madrid: La Acebeda 2025 = 70) | OK-WF |
| `DATOS_TABLA` (con fechas legibles) | `.../DATOS_TABLA/2852?nult=1&tip=A` (`tip=A` da fecha ISO; sin él, la fecha va en milisegundos epoch) | OK-curl |
| `OPERACIONES_DISPONIBLES` | `.../OPERACIONES_DISPONIBLES` | OK-curl |
| `OPERACION` | `.../OPERACION/IPC` (Id 25, Cod_IOE 30138) | OK-curl |
| `TABLAS_OPERACION` | `.../TABLAS_OPERACION/IPC` (59 tablas; trae `Ultima_Modificacion`, `Anyo_Periodo_ini`, `FechaRef_fin`) | OK-curl |
| `SERIES_OPERACION` | `.../SERIES_OPERACION/IPC?page=1` | OK-curl |
| `SERIES_TABLA` | `.../SERIES_TABLA/50902?page=1` | OK-curl |
| `SERIE` (metadatos de una serie) | `.../SERIE/IPC251852?det=2` | OK-curl |
| `DATOS_SERIE` | `.../DATOS_SERIE/IPC251852?nult=2` | OK-curl |
| `GRUPOS_TABLA` (dimensiones de una tabla) | `.../GRUPOS_TABLA/2852` → Provincias, Sexo | OK-curl |
| `VARIABLES_OPERACION` | `.../VARIABLES_OPERACION/IPC` | OK-curl |
| `DATOS_METADATAOPERACION` | `.../DATOS_METADATAOPERACION/IPC?g1=115:29&p=1&nult=1` | OK-curl (295 KB) |
| `PUBLICACIONES`, `PUBLICACIONES_OPERACION/25` | — | OK-curl |
| `PUBLICACIONFECHA_PUBLICACION/8` (**calendario** de una publicación, con fechas futuras) | `.../PUBLICACIONFECHA_PUBLICACION/8` (IPC: noviembre de 2026 y avance de diciembre de 2026) | OK-WF |
| `TABLA/2852`, `CALENDARIO_OPERACION/IPC` | — | **no existen** («La operación indicada no existe») |
| JAXI, CSV de una tabla | `https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/2881.csv` | OK-WF (separador `;`, ISO-8859-15, miles con punto en 2852) |
| Calendario de publicaciones en HTML | `https://www.ine.es/dynt3/Calendario/calenHTML.htm` (`/daco/daco41/calen.htm` redirige aquí) | OK-WF (13/11/2026: IPC de octubre de 2026) |

**Último periodo publicado:** `DATOS_TABLA/{id}?nult=1` o `DATOS_SERIE/{cod}?nult=1` (campos `Anyo` y `FK_Periodo`); la fecha de modificación está en `TABLAS_OPERACION`. **Calendario:** `PUBLICACIONFECHA_PUBLICACION/{idPublicacion}` (el id se saca de `PUBLICACIONES_OPERACION/{idOperacion}`) o la página HTML.

**Límites:** una tabla municipal entera pesa mucho (2881 con `nult=1` ocupa 126 KB); conviene filtrar con `tv=`. Cuidado: `PUBLICACIONFECHA_PUBLICACION` no viene ordenada (aparece «Junio 2020» al final). La serie IPC251852 termina en 2025-12, posiblemente por un cambio de base (sin verificar).

---

## 4. datos.comunidad.madrid (CKAN 2.9.0)

| Uso | URL | Estado |
|---|---|---|
| Búsqueda | `https://datos.comunidad.madrid/api/3/action/package_search?q=poblacion&rows=2` (747 resultados) | OK-curl |
| Ficha de un conjunto | `https://datos.comunidad.madrid/api/3/action/package_show?id=1930748` | OK-WF |
| Datos por API (datastore) | `.../api/3/action/datastore_search?resource_id=58ffa899-970e-4559-9e8a-550e21b29b3c&limit=2` | OK-curl |
| Organizaciones | `.../api/3/action/organization_list` → `comunidad-de-madrid`, `estadistica` | OK-curl |
| Versión | `.../api/3/action/status_show` → ckan 2.9.0 | OK-curl |
| Descarga | `https://datos.comunidad.madrid/dataset/81592bc2-.../resource/58ffa899-.../download/densidad-de-poblacion.-municipios.csv` | OK-curl (CSV `;`, 464 KB) |

**Metadatos:** `license_id` (`cc-by`), `license_title`, `license_url` (CC BY 4.0), `metadata_modified` (fecha de **edición del registro**: 2026-11-05) y **`extras` → «Fecha Actualización»** (fecha real de los datos: 21-01-2026), «Ámbito» (nivel territorial: «Municipal y zonas estadísticas»), «Fuente», «Unidad». Por recurso: `format`, `size`, `last_modified`, `datastore_active`. La cobertura temporal está en `notes` (texto libre). La raíz `datos.comunidad.madrid/` redirige a una página de comunidad.madrid; la API está en `/api/3/action/`.

**Límites:** `metadata_modified` ≠ actualización de los datos; usar el extra «Fecha Actualización». El servidor descarga por id de recurso aunque el nombre de fichero no coincida, así que no se puede tomar el nombre como prueba.

---

## 5. datos.madrid.es (Ayuntamiento, ahora CKAN 2.9.11)

| Uso | URL | Estado |
|---|---|---|
| Búsqueda | `https://datos.madrid.es/api/3/action/package_search?q=padron&rows=1` (8 resultados) | OK-WF |
| Ficha | `https://datos.madrid.es/api/3/action/package_show?id=200076-0-padron` | OK-curl |
| Descarga | `https://datos.madrid.es/dataset/200076-0-padron/resource/200076-2-padron-csv/download/200076_20261029_160704.csv` | OK-curl (CSV `;`; el XML pesa 165 MB) |
| Catálogo antiguo `egob/catalogo.json` | — | **404** |

**Metadatos (esquema DCAT-AP ampliado):** `license_title` (CC BY 4.0), `metadata_modified` y `modified`, `frequency` (URI de la UE, MONTHLY), `temporal_coverage` (`[{"end":"2026-09-30"}]`), `granularity`, `districts_data`, `geolocation_data`, `issued`. Por recurso: `format`, `size`, `hash` (MD5) y `last_modified`. El nivel territorial va en `notes` (distrito, barrio, sección censal) y en indicadores como `districts_data`.

**Límites:** respuestas grandes (`package_search` con `rows=2` ocupó 610 KB); usar `rows=1` o `fl`. Las URL de descarga llevan una marca de fecha, `AAAAMMDD_HHMMSS`, que cambia con cada actualización.

---

## 6. datos.gob.es (catálogo nacional, Linked Data API)

| Uso | URL | Estado |
|---|---|---|
| Por palabra del título | `https://datos.gob.es/apidata/catalog/dataset/title/padron.json?_pageSize=2` | OK-curl |
| Por publicador (A13002908 = Comunidad de Madrid) | `https://datos.gob.es/apidata/catalog/dataset/publisher/A13002908.json?_pageSize=2` | OK-WF |
| Por título (IRPF) | `.../dataset/title/IRPF.json?_pageSize=30` | OK-curl |

**Campos:** `_about` (ficha), `identifier` (URL de origen), `title`, `description`, `issued`, `modified` (en formato de texto, p. ej. «jue, 05 nov 2026 16:27:36 GMT+0000»), `publisher`, `theme`, `keyword`, `distribution[].accessURL` + `format` + `byteSize`. **No apareció ningún campo de licencia en los ítems probados** (hay que mirarla en el portal de origen).

**Límites:** paginación con `_pageSize` y `_page`. Federa: la `accessURL` apunta al portal de origen.

---

## 7. Eurostat (API de diseminación)

| Uso | URL | Estado |
|---|---|---|
| Datos (JSON-stat 2.0) | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjangrp3?geo=ES30&sex=T&age=TOTAL&lastTimePeriod=1` → ES30, 2025 = 7 113 886 | OK-WF |
| Índice de contenidos (TSV con «last update of data», «data start», «data end») | `https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` | OK-curl (2 MB) |
| Estructura SDMX | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/ESTAT/demo_r_pjangrp3?detail=allstubs` | OK-curl |
| Metabase | `.../catalogue/metabase.txt.gz` | OK-curl (gzip, no sirve con WebFetch) |
| Metadatos de referencia (ESMS) | `https://ec.europa.eu/eurostat/cache/metadata/en/demo_r_gind3_esms.htm` | OK-curl |

**Fecha de actualización:** el campo `updated` del JSON-stat y las anotaciones `extension.annotation` (`DISSEMINATION_TIMESTAMP_DATA`, `CREATED`, DOI). En el TOC, la línea de `demo_r_pjangrp3` dice: actualizado el 12.11.2026, datos de 2014 a 2025. **Límite:** `lastTimePeriod=1` es imprescindible para no traer la serie entera. Llama la atención que `updated` valía «2026-11-12T23:00:00+0100», una hora posterior al momento de la consulta.

---

## 8. Catastro (DGC)

| Uso | URL | Estado |
|---|---|---|
| Callejero JSON: provincias | `https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/ObtenerProvincias` | OK-curl |
| Callejero JSON: municipios | `.../COVCCallejero.svc/json/ObtenerMunicipios?Provincia=MADRID&Municipio=ALCORCON` | OK-curl |
| Números de portal → referencia catastral | `.../COVCCallejero.svc/json/ObtenerNumerero?Provincia=MADRID&Municipio=MADRID&TipoVia=CL&NomVia=ALCALA&Numero=50` | OK-curl |
| Datos no protegidos por referencia catastral | `.../COVCCallejero.svc/json/Consulta_DNPRC?RefCat=1047206VK4714G` (C/ Alcalá 45, Oficinas, 15 786 m², 1933) | OK-WF |
| Referencia catastral → coordenadas | `.../COVCCoordenadas.svc/json/Consulta_CPMRC?RefCat=1047206VK4714G&SRS=EPSG:4326` | OK-curl |
| Coordenadas → referencia (`Consulta_RCCOOR`, SOAP/asmx y JSON) | — | respondió, pero con error 16 «no hay referencia» en 4 puntos de Madrid; **no se consiguió un caso positivo** |
| ATOM INSPIRE de edificios, Madrid | `https://www.catastro.hacienda.gob.es/INSPIRE/buildings/28/ES.SDGC.bu.atom_28.xml` (actualizado el 2026-08-21) | OK-WF (truncado, usar `offset`) |
| Fichero zip de Madrid capital | `https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/28/28900-MADRID/A.ES.SDGC.BU.28900.zip` | OK-curl HEAD: 200, 117 MB, Last-Modified 21/08/2026 |
| WMS INSPIRE | `https://ovc.catastro.meh.es/cartografia/INSPIRE/spadgcwms.aspx?service=WMS&request=GetCapabilities` | OK-curl |
| Página de difusión | `https://www.sedecatastro.gob.es/Accesos/SECAccDescargaDatos.aspx` | OK-curl |

**Qué requiere certificado o Cl@ve** (según la página de difusión): la descarga masiva de datos alfanuméricos por provincia (formato CAT), la cartografía vectorial en Shapefile, la cartografía histórica y la consulta masiva por XML. Además hay que aceptar una licencia de uso. Los servicios de datos protegidos (titular y valor catastral) solo los usan usuarios registrados o la Administración mediante la Plataforma de Intermediación. **Sin certificado:** los servicios OVC de datos no protegidos, ATOM e INSPIRE (WMS/WFS). En Catastro, Madrid capital tiene el código **900** (INE 28079).

---

## 9. CRTM (datos.crtm.es, ArcGIS Hub)

| Uso | URL | Estado |
|---|---|---|
| Búsqueda (OGC API Records, limitada al CRTM) | `https://datos.crtm.es/api/search/v1/collections/dataset/items?q=estaciones%20metro&limit=2` | OK-WF |
| Catálogo DCAT completo (281 conjuntos) | `https://datos.crtm.es/data.json` | OK-curl (720 KB) |
| `api/v3/datasets?q=` | `https://datos.crtm.es/api/v3/datasets?q=metro` | responde, pero **mezcla capas de otros propietarios de ArcGIS** (p. ej. `haidar_geomatic`): no usar para verificar |
| Metadatos de una capa | `https://services5.arcgis.com/UxADft6QPcvFyDU1/arcgis/rest/services/M4_Red/FeatureServer/0?f=json` | OK-curl (`editingInfo.dataLastEditDate`, `maxRecordCount`=1000, EPSG:25830) |
| Recuento | `.../M4_Red/FeatureServer/0/query?where=1%3D1&returnCountOnly=true&f=json` → `{"count":293}` | OK-WF |
| Datos | `.../query?where=1%3D1&outFields=*&resultRecordCount=1&outSR=4326&f=json` (o `f=geojson`) | OK-curl |

**Metadatos:** en la búsqueda, `modified` (epoch en ms), `owner` (ConsorcioRegional), `licenseInfo`/`license` → `https://www.crtm.es/licencia-de-uso` (licencia **propia**, «custom»). En `data.json` están `modified` en ISO, `spatial` (bbox) y `license`. **Límite:** como mucho 1000 registros por consulta, así que hay que paginar con `resultOffset`. Los GTFS son ficheros zip (p. ej. `google_transit_M4.zip`).

---

## 10. Agencia Tributaria: estadística de los declarantes del IRPF por municipios

- Ficha oficial: `https://sede.agenciatributaria.gob.es/Sede/datosabiertos/catalogo/hacienda/Estadistica_de_los_declarantes_del_IRPF_por_municipios.shtml`: OK-curl. Describe la estadística: renta bruta y disponible, municipios de más de 1000 habitantes y territorio fiscal común (**ni País Vasco ni Navarra**). La renta media es por declaración, no por persona ni por hogar.
- **Último año: 2024**: `https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2024/home.html` OK-curl (título «...por municipios 2024»; enlaces a Metodología, «Detalle de los municipios con más de 1.000 habitantes», mapa EGEO y `metadatos.html`). `.../2025/home.html` → 404.
- La misma ruta en `www.agenciatributaria.es`: **404 con WebFetch** y error de certificado TLS con curl. Usar el host `sede.agenciatributaria.gob.es`.
- Índice: `https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto.html` (también enlaza la estadística por código postal).
- En datos.gob.es hay series de IRPF de la Comunidad de Madrid (publicador A13002908, p. ej. `a13002908-base-imponible-general-del-irpf4`, modificada el 05/11/2026).

---

## 11. Movilidad (Ministerio de Transportes), Seguridad Social y SEPE

**Open data de movilidad (estudio con big data):**
- Página del ministerio `https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data/opendata-movilidad`: **403 con WebFetch y con curl**.
- Bucket público: `https://movilidad-opendata.mitma.es/` OK-curl (listado S3 en XML, truncado a 1000 claves).
- RSS: `https://movilidad-opendata.mitma.es/RSS.xml` OK-WF. Lo último: `estudios_basicos/por-distritos/viajes/meses-completos/202512_Viajes_distritos.tar` (publicado el 23/02/2026; solo trae 3 días, 0,33 GB) y un LEEME de cambio de metodología para los datos posteriores al 01/07/2025.
- La licencia está en un PDF en la raíz: «LICENCIA de datos abiertos del MITMA 20201203.pdf» (listado, no leído). Las especificaciones están en `LEEME_Especificaciones_indicadores_OpenDataMovilidad.xlsx`.
- **Último mes completo: junio de 2025** (`202506_Viajes_distritos.tar`, 7,38 GB). Desde el cambio de metodología del 1-07-2025 solo hay semanas sueltas: agosto (7 días entre el 8 y el 17), octubre (del 13 al 19) y diciembre (del 6 al 8). Julio, septiembre y noviembre no tienen ficheros diarios. Comprobado en el listado del bucket el 2026-11-16 (fila 5a de `docs/verificaciones/movilidad-interoperabilidad.md`).

**Seguridad Social, afiliados por municipio:**
- `https://www.seg-social.es/wps/portal/wss/internet/EstadisticasPresupuestosEstudios/Estadisticas/EST8/EST10/EST305/c43ad8ea-fe79-4329-ac8e-e5758f3c4d7a/6609c55f-65e4-4e64-b1ab-8917fce27a84` (Total afiliados por régimen, a nivel municipal): OK-WF.
- Último fichero: **septiembre de 2026**, `/descarga/es/Muni092026` (XLSX, 509 KB, publicado el 14/10/2026).
- Hay otras dos subpáginas: por régimen, CNAE a 2 dígitos y sexo, y cuentas de cotización.
- Portal PX-Web: `https://w6.seg-social.es/PXWeb` (enlazado, no probado).

**SEPE, paro registrado y contratos por municipio:**
- `https://www.sepe.es/HomeSepe/que-es-el-sepe/estadisticas/datos-estadisticos/municipios.html`: OK-WF. Último mes: **octubre de 2026**.
- Madrid: `https://www.sepe.es/HomeSepe/dam/jcr:a01d7184-f6a3-4241-9643-6f1075800c67/MUNI_MADRID_1026.xls` (y el PDF), enlazados desde `.../municipios/2026/octubre.html` (OK-WF). Los `jcr:` son opacos: hay que sacarlos de la página del mes.

---

## Pauta mínima para el agente verificador (solo WebFetch)

1. **¿Existe?** Hacer la búsqueda en el catálogo (CKAN `package_search`, `apidata`, CRTM `api/search/v1`, INE `TABLAS_OPERACION`) y luego leer la ficha (`package_show` o la URL `_about`).
2. **¿Qué contiene?** Comparar el título, la cobertura (`temporal_coverage`, `notes`, TOC de Eurostat, `nult=1` del INE), el nivel territorial y los formatos.
3. **¿Está al día?** Usar la fecha de los datos (extra «Fecha Actualización», `modified`, `updated`, `Ultima_Modificacion`), no solo `metadata_modified`.
4. **¿Se descarga?** Hacer WebFetch de la URL del recurso. Si es binario (zip o tar), basta con la cabecera o con su entrada en el ATOM o el RSS.
5. **¿Licencia?** Leer `license_id`/`license_url` (CKAN), `licenseInfo` (CRTM) o el PDF de licencia (movilidad). En datos.gob.es no viene.
6. **¿Norma vigente?** Con `https://www.boe.es/diario_boe/xml.php?id=BOE-A-...` leer `estatus_derogacion`, `vigencia_agotada` y el bloque `analisis` (códigos 210, 270 y 301). Paginar con `offset`.

---

## No verificado

- **WebSearch no se usó para verificar nada.** En la primera sesión dio error de límite de uso; las URL salen de las páginas oficiales enlazadas.
- Muchas filas marcadas OK-curl **no se repitieron con WebFetch** (CKAN `package_search` de la Comunidad, INE salvo `DATOS_TABLA` y `PUBLICACIONFECHA`, Catastro salvo `Consulta_DNPRC` y ATOM, el TOC de Eurostat, `data.json` del CRTM). Es probable que funcionen, porque no exigen cabeceras, pero no está probado.
- La API del BOE con WebFetch: **falla** (400). No hay forma comprobada de pasar la cabecera `Accept` desde WebFetch, y tampoco se probó un parámetro de formato en la URL.
- El buscador HTML del BOE (`/buscar/legislacion.php` y `/buscar/boe.php` con parámetros): solo se comprobó que la página carga (200), no sus parámetros.
- El buscador avanzado del BOCM y una API de búsqueda del BOCM: no probados.
- Una forma de obtener el número de BOCM a partir solo de la fecha (sin pasar por `/ultimo-bocm`): no encontrada.
- `Consulta_RCCOOR` del Catastro con resultado positivo: no conseguido.
- El WFS INSPIRE del Catastro, la descarga de Shapefile con certificado y la licencia del Catastro: no probados ni leídos.
- El texto de la licencia del CRTM (`crtm.es/licencia-de-uso`) y el PDF de licencia del Ministerio de Transportes: no leídos.
- Las tablas de la estadística de IRPF por municipios de 2024 (página `jrubik...` de detalle municipal y formato de descarga): no abiertas. Tampoco el calendario de publicaciones de la AEAT (la página carga, pero no se vio la fecha de 2025).
- La página del Ministerio de Transportes sobre el estudio de movilidad (403).
- El fichero de la Seguridad Social `/descarga/es/Muni092026`: no se comprobó la descarga ni su host completo (se supone `www.seg-social.es`). PX-Web no probado.
- El fichero `.xls` del SEPE: no se descargó.
- Por qué la serie del IPC IPC251852 acaba en 2025-12 (posible cambio de base).
- INEbase (páginas `operacion.htm`): no probadas.
