# DATAMAD26 · Plan de la Propuesta A: «Salario que sobra» + #9 Esfuerzo alquiler/renta

Plan de alto nivel resultado de la entrevista por fases. Se refinará con Fable 5.2.
Última actualización: 11/11/2026 · Final: 26/11/2026 (URJC Vicálvaro).

## Estado de las fases
| Fase | Estado |
|---|---|
| 1. Enfoque y alcance | ✅ Cerrada |
| 2. Datos | ✅ Cerrada (quedan verificaciones prácticas) |
| 3. Modelo de cálculo | ✅ Cerrada |
| 4. Análisis (#9 y hallazgos) | ✅ Cerrada |
| 5. Herramienta (app, stack, código abierto) | ✅ Cerrada |
| 6. Presentación y entrega | 📝 Orientativa (se detallará al final) |

**Plan cerrado el 11/11/2026.** El orden de trabajo, el reparto y las fechas los gestiona el equipo y no forman parte de este documento. Siguiente paso: iterar el plan con Fable 5.2 para llegar al máximo detalle.

---

## 1. Enfoque y alcance
- **Pregunta central:** ¿cuánto dinero y cuánto tiempo te cuesta de verdad vivir en cada sitio, según dónde trabajas?
- **Dos partes:**
  - **Análisis**, dirigido a la Administración: mapa de esfuerzo alquiler/renta (#9) y hallazgos.
  - **Herramienta**, dirigida a **particulares**: introduces tu sueldo y tu lugar de trabajo y obtienes, por zona, lo que te sobra cada mes y las horas de desplazamiento.
- **Unidad territorial:** 179 municipios + 21 distritos de Madrid capital (unas 199 zonas). La sección censal queda como posible ampliación.
  - Supuesto a verificar: que los distritos censales de Madrid capital coinciden con los 21 distritos municipales.
- **Eje regional:** el transporte (coste + tiempo) es un componente principal, no contexto, para reforzar el criterio de uso de datos de la Comunidad.
- **Fuera de alcance:** capa predictiva, vistas para pyme y Administración dentro de la app, modo "comprar" (hipoteca).
- No se ha enviado todavía ninguna propuesta ni texto de 100 palabras.

## 2. Datos
| Componente | Fuente | Origen | Estado |
|---|---|---|---|
| Neto | Cálculo IRPF + Seguridad Social | Fórmula | Supuestos en la Fase 3 |
| Alquiler | SERPAVI (MIVAU): €/m², cuantía y superficie; mediana, P25 y P75; colectiva/unifamiliar | Externo | Accesible. **Descarga manual pendiente** |
| Actualización del alquiler | IPC de alquiler de la Comunidad (`1927681`) | **Regional** | Disponible |
| Coste del transporte público | Tarifas (`1919188`, 2007–2024) + zonificación | **Regional** | **Faltan las tarifas vigentes 2025–26** |
| Tiempo en transporte público | GTFS del CRTM (Metro, EMT, interurbanos, Cercanías, Metro Ligero) + OpenStreetMap + r5py | Regional (CRTM) + externo | Los feeds existen; **falta probar el enrutado** |
| Tiempo y distancia en coche | Red viaria de OpenStreetMap + r5py | Externo | Pendiente |
| Renta (#9) | INE, Atlas de Distribución de Renta de los Hogares | Externo | Disponible |
| Contexto e indicadores | Bono Alquiler Joven (160 municipios), paro, afiliados por residencia | **Regional** | Disponible |

### SERPAVI: lo que sabemos
- Excel de 67,8 MB, titulado "2011–2024": `https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03_09_bd_SERPAVI_2011-2024%20-%20DEFINITIVO%20WEB_v2.xlsx`
  - Se guarda en `data/raw/serpavi/`.
  - El proxy del equipo bloquea la descarga automática (403), así que hay que bajarlo a mano.
- Capas *shape* (sección censal, distrito, municipio): mismo dominio `cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/`.
- Metodología (18/03/2026): `https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03-18_Metodologia_SERPAVI.pdf`
- Origen de los datos: IRPF (modelo 100) cruzado con el Catastro. Madrid incluida (474.935 testigos de vivienda colectiva en 2024).
- **Riesgos:**
  1. La metodología dice que las descargas llegan hasta 2023; el nombre del fichero dice 2024. Comprobar al abrirlo.
  2. Solo se publican celdas con al menos 10 testigos. A nivel nacional, solo el 31,6 % de los municipios tiene dato de vivienda colectiva, así que habrá huecos en municipios pequeños. **Tratamiento: sin imputación; marcar "sin dato" o, si se justifica, usar el dato de unifamiliar señalándolo.**
  3. Son contratos declarados, no precios de oferta: el dato se trata como **cota inferior** y se muestra como rango.

## 3. Modelo de cálculo (mensual; todas las asunciones parametrizadas y visibles)
### Entradas del usuario
- Bruto anual y número de pagas.
- Hogar: adultos, hijos y edad (la edad determina el Abono Joven y el Bono Alquiler Joven).
- **Hasta dos sueldos y dos lugares de trabajo.** Es viable porque la matriz origen-destino de unas 199 × 199 zonas se precalcula; un segundo destino es solo otra consulta a esa matriz.
  - Si surgen complicaciones: dos sueldos y un solo lugar de trabajo, y la pareja prueba cada destino por separado.
- Tamaño de la vivienda (m²) y número de personas con las que se comparte (alquiler dividido entre ellas).
- Modo de transporte: público o coche.
- Días presenciales a la semana.

### Cálculo para cada zona de residencia z
- **Neto** = bruto − Seguridad Social del trabajador (hasta la base máxima) − cuota anual de IRPF (estatal + autonómico de Madrid, reducción por rendimientos del trabajo, mínimos personales y familiares) ÷ 12. Tributación individual.
- **Alquiler(z)** = €/m²(z, colectiva, último año) × factor IPC de alquiler regional × m² ÷ personas. Se calcula con mediana, P25 y P75.
- **Transporte público(z)** = mínimo entre el abono de la zona tarifaria correspondiente y los billetes sencillos según los días presenciales. Abono Joven para menores de 26.
- **Coche(z)** = 2 × distancia × días × coste por km (parámetro justificado) + aparcamiento en destino.
  - Limitación: r5py no tiene en cuenta el tráfico, así que el tiempo en coche sale subestimado. Se aplicará un factor de congestión o se declarará la limitación.
- **Tiempo(z)** = 2 × tiempo puerta a puerta (mediana entre 7:30 y 8:30) × días.

### Salidas
- **Sobrante(z)** = neto − alquiler − transporte. El rango sale de P25 y P75 del alquiler.
- **Horas al mes de desplazamiento**, mostradas aparte. **No se monetiza el tiempo**: euros y horas van separados para no inflar las cifras.
- **Esfuerzo(z)** = alquiler ÷ neto.
- **Asequibilidad:** alquiler máximo asumible y m² que puedes pagar en cada zona.
- **Umbrales:** 30 % para la recomendación de la app; 40 % para la sobrecarga en el análisis #9 (definición de Eurostat).

## 4. Análisis (dirigido a la Administración)
Hay **dimensión temporal** en todos los bloques en los que las series lo permiten: SERPAVI desde 2011 y renta del INE desde 2015, así que la ventana común empieza en 2015.

1. **Esfuerzo alquiler/renta por zona (#9).**
   - Fórmula: alquiler mediano de SERPAVI ÷ (renta neta media del hogar, INE ÷ 12).
   - Se muestra un mapa por año y la evolución: dónde ha crecido más el esfuerzo.
   - Limitación declarada: la renta media incluye a los propietarios, que suelen ganar más que los inquilinos. Por eso el indicador **subestima** el esfuerzo de quien alquila.
2. **Hogares en sobrecarga (más del 40 %), como rango y con la metodología explícita.**
   - Se cruzan los hogares en alquiler por municipio con la distribución de renta del INE.
   - Para los hogares en alquiler, preferir el Censo de edificios y viviendas por municipio de la Comunidad (serie `19155xx`, régimen de tenencia), porque es dato regional. Alternativa: Censo 2021 del INE.
3. **Euros frente a tiempo hacia los polos de empleo.**
   - Los polos se eligen **con datos**: las zonas con más empleo por lugar de trabajo.
   - Fuente a localizar: afiliación por municipio del centro de cotización (Comunidad o Seguridad Social).
   - Alternativa mejor si está disponible: los flujos origen-destino de la Encuesta Domiciliaria de Movilidad del CRTM (EDM2018), que son desplazamientos reales.
   - Hallazgos buscados: zonas donde el coche gana con mucha diferencia al transporte público (déficit de transporte) y el efecto del Abono Joven de tarifa plana, con el que el coste de vivir lejos se paga en tiempo y no en dinero (pendiente de verificar).
4. **Bloque propio: ¿llega el Bono Alquiler Joven a donde más se necesita?**
   - Se cruzan las solicitudes y aceptaciones por municipio (160 municipios, 2022) con el esfuerzo de los jóvenes y con la población joven.
   - Es una evaluación de política pública hecha con datos regionales.
   - Limitación: solo hay datos de un año y no de todos los municipios.
5. **Rentabilidad implícita** (opcional; ver el Apéndice A).

### Interoperabilidad: Smart Data Models
- Lo impulsa el autor del repositorio de la organización, que forma parte del jurado. Usarlo suma puntos.
- Existen modelos GTFS en *UrbanMobility* (`GtfsStop`, `GtfsStopTime`, `GtfsAgency`, …). Se usan para normalizar paradas y horarios del CRTM.
- Hay que revisar qué modelos encajan para zonas administrativas, vivienda e indicadores.
- Propuesta: publicar la salida (indicadores por zona y año) en un esquema de Smart Data Models. Si no existe ninguno adecuado, proponer un modelo nuevo (por ejemplo, un indicador de asequibilidad de la vivienda), aprovechando su proceso de creación rápida de modelos.
- Clave de cruce común: código INE de municipio + código de distrito + año.

## 5. Herramienta
### Arquitectura
- **Pipeline en Python (offline, reproducible)** que calcula todo lo pesado y lo exporta a JSON:
  - matrices de tiempo y distancia en transporte público y en coche (unas 199 × 199 zonas, salida entre 7:30 y 8:30);
  - alquiler por zona y año (mediana, P25 y P75);
  - tarifas de transporte;
  - polígonos simplificados de las zonas.
- **App 100 % estática** publicada en GitHub Pages: sin servidor, gratis y **privada** (el sueldo nunca sale del navegador).
  - El JS lo escribimos con ayuda de Claude; nadie del equipo lo domina.
  - **Mitigación del riesgo de JS: no hay lógica fiscal en JS.** El neto se precalcula en Python sobre una rejilla de brutos (por ejemplo, cada 250 €) × configuraciones de hogar, y el JS solo interpola linealmente. La cuota de IRPF es lineal por tramos, así que el error es despreciable.
  - El JS se limita a: interpolar el neto, consultar las tablas, sumar, pintar el mapa y validar las entradas.
  - **Pruebas de referencia:** Python genera casos con resultado conocido y el JS tiene que reproducirlos.
  - **Sin peticiones a terceros:** las librerías van incluidas en el propio repositorio, no se cargan de un CDN. Mapa de coropletas sin teselas externas, o con un mapa base propio en PMTiles servido desde el mismo sitio.
  - Validación estricta de todas las entradas (rangos y tipos). Ninguna entrada se inserta como HTML.
- **Licencias:** MIT para el código y CC BY 4.0 para los datos derivados, citando las fuentes. Revisar la cláusula de la licencia del CRTM sobre redistribuir con la misma licencia.

### Pantalla principal
- Formulario: bruto anual, número de pagas, hogar, hasta dos lugares de trabajo, m² y personas con las que se comparte, modo de transporte y días presenciales.
- **Mapa coloreado por sobrante**, con un selector para cambiar a horas al mes, y una lista de las 10 mejores zonas.
- Al pinchar una zona: desglose con el neto, el alquiler (rango P25–P75), el transporte, las horas, el esfuerzo y los m² asequibles.
- Avisos visibles: dato de "cota inferior", año del dato y "sin dato" en las zonas con menos de 10 testigos.
- **Enlace al informe de análisis**, que va aparte para no meter ruido en la herramienta.

### Informe de análisis (aparte)
- Notebook o Quarto publicado como página estática en el mismo repositorio. Incluye los bloques 1–5 de la Fase 4 y la metodología.

### Servidor MCP (forma parte del plan: suma ante el jurado)
- Servidor MCP en Python (stdio) que lee las mismas tablas precalculadas.
- Herramientas propuestas: `calcular_sobrante(bruto, hogar, trabajo, …)`, `ranking_zonas(…)`, `indicadores_zona(zona, año)`.
- Validación estricta de los argumentos y sin credenciales.
- Demo: hacerle preguntas en lenguaje natural desde Claude.

## 6. Presentación y entrega (SOLO ORIENTATIVA)
> Esta fase es solo orientativa. Se detallará al final, cuando el equipo conozca el formato, y se iterará con Fable 5.2. **No se debe dedicar trabajo ni créditos a esta parte hasta entonces.** Fechas y plazos los gestiona el equipo.

- Entregables previstos: web publicada, repositorio reproducible, informe de análisis y presentación.
- Narrativa orientativa:
  1. un caso individual en la app (euros frente a horas);
  2. el problema colectivo (sobrecarga, evolución desde 2015, Bono Alquiler Joven);
  3. la parte técnica (datos de la Comunidad, Smart Data Models, código abierto, MCP).
- Responder explícitamente a cada criterio publicado: uso de datos regionales, viabilidad y código abierto.
- Exponer las limitaciones por iniciativa propia: SERPAVI como cota inferior, coche sin tráfico, zonas sin dato.

---

## Apéndice A · API del Notariado (€/m² de compraventa)
- Tiene datos estratificados por nivel territorial (comunidad, municipio…). Es precio de **compraventa**, no de alquiler.
- **Uso previsto, si se incorpora: solo la rentabilidad implícita** = alquiler anual (SERPAVI) ÷ precio de compraventa (Notariado), por zona. Es un indicador para el análisis dirigido a la Administración: muestra dónde comprar compensa frente a alquilar.
- Descartado: usarla para actualizar el alquiler y el modo "comprar".
- Pendiente: enlace a la API, licencia de reutilización (si permite publicarlo en código abierto) y cobertura municipal real.

## Pendientes y verificaciones
- [ ] Descargar el Excel de SERPAVI y explorarlo: años, cobertura en Madrid, huecos.
- [ ] Probar r5py (transporte público + coche) con 3–5 pares origen-destino.
- [ ] Tarifas de transporte vigentes en 2025–26 y condiciones del Abono Joven.
- [ ] Coincidencia entre distritos censales y municipales en Madrid capital.
- [ ] Enlace, licencia y cobertura de la API del Notariado.
- [ ] Encontrar un dataset de afiliación por lugar de trabajo a nivel municipal, o la matriz origen-destino de la EDM2018 del CRTM.
- [ ] Comprobar el régimen de tenencia en el Censo de edificios y viviendas de la Comunidad (serie `19155xx`).
- [ ] Revisar la carpeta `pysmartdatamodels/` del repositorio de la organización y los modelos aplicables.
- [ ] Nota: la API CKAN de la Comunidad también da 403 desde el proxy del equipo. Las descargas tienen que hacerse a mano o desde otra red.
- [ ] (Gestión del equipo, al final) Confirmar con la organización: pesos de los criterios, formato de entrega, duración de la presentación y criba de 100 palabras.
