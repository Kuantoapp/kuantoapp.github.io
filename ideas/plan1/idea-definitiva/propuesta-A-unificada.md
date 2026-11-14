# Propuesta A unificada: «¿Me sobra?» (visión del jurado)

Análisis comparado de las dos versiones de la Propuesta A y propuesta de unificación.
Fecha: 14 de noviembre de 2026. Fuentes:
- [Plan de Izan](../izan/plan_propuesta_A_Izan.md) (11/11/2026)
- [Ficha de Yeray](../yeray/ficha-salario-que-sobra.md) (11/11/2026)

> **Estado: propuesta, no decisión.** Antes de anotarla en `docs/decisiones.md` hay que pasarla por `dm-abogado-del-diablo`. No se ha verificado ninguna marca «(verificar)» de los planes de origen ni los identificadores del catálogo citados.

## Marco de evaluación

- **Criterios:** uso de la información pública regional, viabilidad y código abierto (oficiales, según la ficha de Yeray), más el valor económico, social o medioambiental (citado por la URJC y la prensa). Los pesos no están publicados.
- **Jurado relevante:**
  - Alberto Abella: autor de Smart Data Models e impartió la formación de APIs, MCP y espacios de datos.
  - Olga Quirós (ASEDIE): economía del dato y reutilización.
- **Tiempo:** congelación de datos el 22 de noviembre y presentación el 26 de noviembre.

## Diagnóstico

Las dos versiones son **la misma idea**: lo que sobra del sueldo es neto − alquiler − transporte, junto con el esfuerzo alquiler/renta (#9) y el Bono Alquiler Joven. No compiten, se complementan:
- Izan aporta **la ingeniería y el rigor**.
- Yeray aporta **el relato y el impacto**.

Cada una es débil justo donde la otra es fuerte.

## Propuesta de Izan

### A favor
- **Viable en el plazo.** Son unas 199 zonas, la matriz de tiempos se precalcula y el alcance está acotado de forma explícita: sin capa predictiva y sin modo compra.
- **Rigor creíble:**
  - euros y horas separados, sin monetizar el tiempo;
  - alquiler como rango P25–P75;
  - SERPAVI declarado como cota inferior;
  - limitación declarada de la renta media, que incluye a los propietarios y por eso subestima el esfuerzo;
  - sin imputación.
- **Resuelve el mayor riesgo de la ficha de Yeray.** Tiene localizada la URL del Excel completo del SERPAVI; la descarga es manual.
- **Smart Data Models y servidor MCP** de forma explícita, que es lo que más valora la organización.
- **App estática y privada:**
  - el sueldo no sale del navegador;
  - la demo no depende de un servidor;
  - la lógica fiscal está en Python y el JS solo interpola sobre una rejilla, con casos de referencia.
- **Dimensión temporal desde 2015.** Da evolución, no una foto fija.

### En contra
- **Narrativa débil.** No hay personajes, guion ni una decisión pública concreta que cambie: buen mapa, poco impacto.
- **Sin cesta básica.** El «sobrante» puede engañar, porque alguien con sobrante positivo puede no llegar a fin de mes. Es una pregunta probable del jurado.
- **Huecos «sin dato»** en los municipios pequeños y baratos, justo donde buscan los jóvenes.
- **Poco peso regional en el núcleo.** SERPAVI e INE son fuentes nacionales. Lo regional queda en las tarifas, el IPC de alquiler, el Bono y el contexto.
- **Modo coche sin tráfico.** Es trabajo extra con un resultado subestimado que hay que justificar.
- **Impacto sin medir.** Analiza el Bono, pero no simula ninguna alternativa.

## Propuesta de Yeray

### A favor
- **Gancho y relato.** Abre con el dato del Bono Alquiler Joven 2022 (solicitudes frente a aceptadas, del catálogo regional), tiene cuatro personajes reconocibles y un guion de 5 minutos.
- **Decisiones públicas concretas:**
  - focalizar el Bono;
  - un criterio de elegibilidad que incluya el transporte;
  - el escenario «se acaba el descuento del abono».

  Es lo que convierte el estudio en un servicio con impacto.
- **Cuenta completa.** La cesta básica (EPF del INE) evita el sobrante engañoso.
- **Más datos regionales y municipales:**
  - alquiler por código postal del catálogo regional (`1934258`);
  - panel de indicadores de distritos del Ayuntamiento;
  - desahucios por la LAU;
  - polos de empleo obtenidos de datos.
- **Validación externa e impacto medido:** correlación con desahucios e IGUALA, y test con usuarios antes y después.
- **Entregables reutilizables.** Conjunto de datos con metadatos DCAT-AP, API y MCP. Encaja con la economía del dato.

### En contra
- **Inviable en el plazo.** Reúne demasiadas piezas para 8 días:
  - LightGBM con predicción conformal;
  - predicción a 12 meses;
  - scraping;
  - asistente conversacional;
  - backend FastAPI;
  - destino libre;
  - log-normal por sección con corrección por inquilinos;
  - test con 15–30 personas.

  La ficha rechaza recortar porque «el código no es el cuello de botella». Pero el cuello de botella real es **verificar datos y cifras**, y cada número estimado más es un frente de ataque.
- **Scraping contra las condiciones de uso** de Idealista y Fotocasa. En un evento oficial, con ASEDIE en el jurado, resta puntos aunque solo se publique el factor agregado.
- **Monetizar el tiempo mezcla unidades.** La convención del 50 % del salario está sin verificar.
- **Predicción con pocos años de datos.** Los intervalos serán tan anchos que no aportan.
- **No menciona Smart Data Models.**
- **Muchas marcas «(verificar)»** en cifras que irían al pitch: tarifas 2026, reglas del Bono, licencia del CRTM y valor del tiempo.
- **El backend es un punto único de fallo** en la demo, aunque tiene respaldo estático.

## Propuesta unificada

La regla es **la arquitectura y el rigor de Izan, más el relato y la capa de decisión de Yeray, sin lo que no cabe antes del 22 de noviembre.**

| Pieza | Qué se queda | Origen |
|---|---|---|
| Unidad territorial | 179 municipios + 21 distritos de Madrid capital; barrios solo si sobra tiempo | Izan |
| Fórmula | sobra = neto − alquiler − transporte − **cesta básica**. Horas de viaje aparte. Deslizador de valor del tiempo opcional y **apagado por defecto** | Izan + Yeray |
| Alquiler | SERPAVI (Excel, descarga manual), P25–P75 + `1934258` regional para Madrid capital + IPC de alquiler regional. Se presenta como suelo | Izan + Yeray |
| Huecos de alquiler | «Sin dato» por defecto. Si hay tiempo, un modelo simple marcado como «estimado», con intervalo conformal y comparado con un modelo de referencia | Izan; Yeray como opcional |
| Habitación o piso compartido | Alquiler × m² ÷ personas, declarado como supuesto | Izan |
| Transporte | Tarifas BOCM 2026 por zona + matriz GTFS precalculada (r5py). Polos de empleo a partir de datos (EDM2018 regional o MITMA) | ambos |
| Neto | Rejilla precalculada en Python, contrastada con nóminas reales y auditada con `dm-auditor-calculos-normativos` | Izan + Yeray |
| App | Estática en GitHub Pages, sin backend y sin peticiones a terceros | Izan |
| Vista de la Administración | Esfuerzo #9 desde 2015 + Bono frente a sobrecarga + **escenario fin del descuento del abono** (es cambiar un parámetro) + simulación del criterio con transporte, solo si se verifican las reglas del Bono | Izan + Yeray |
| Interoperabilidad | Smart Data Models + servidor MCP (stdio) sobre las mismas tablas + conjunto de datos CC BY 4.0 con DCAT-AP | Izan + Yeray |
| Validación | 1–2 correlaciones externas (desahucios por la LAU, IGUALA), declarando que en Madrid capital solo hay 21 distritos | Yeray |
| Relato | Personajes + guion + apertura con el dato del Bono | Yeray |
| Impacto | Test con usuarios reducido (8–10 personas), solo si alguien queda libre desde el 20 de noviembre | Yeray, recortado |

### Se descarta
- Scraping de portales inmobiliarios.
- Predicción del alquiler a 12 meses, del sobrante futuro y de la sobrecarga futura.
- Asistente conversacional dentro de la web.
- Backend FastAPI y destino libre en vivo.
- Modo coche.
- Calibración de habitaciones con precios de oferta.

### Qué gana ante el jurado
- **Datos regionales:** forman parte del núcleo (alquiler por código postal, tarifas, IPC de alquiler, Bono), no solo del contexto.
- **Viabilidad:** alcance que cabe en 8 días y una demo estática que no se cae.
- **Código abierto e interoperabilidad:** MIT, CC BY 4.0, Smart Data Models y MCP.
- **Valor social:** una decisión pública simulada (Bono y fin del descuento) y una validación externa.
- **Superficie de ataque mínima:** pocas cifras estimadas, todas marcadas y con intervalo.

## Pendientes antes de cerrar la decisión
- [ ] Aclarar el identificador del IPC de alquiler regional: `1927681` en el plan de Izan, `1934665` en la ficha de Yeray.
- [ ] Pasar esta propuesta por `dm-abogado-del-diablo`.
- [ ] Resolver las marcas «(verificar)» que afectan a piezas que se quedan: tarifas 2026, reglas del Bono, licencia del CRTM y tabla de la EPF.
- [ ] Confirmar con la organización los pesos de los criterios y el formato de entrega.
- [ ] Anotar la idea elegida en `docs/decisiones.md`.
