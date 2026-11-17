# ¿Me sobra?

**Lo que te queda de tu sueldo, zona a zona, después del alquiler, el transporte y lo básico, cuántas horas te cuesta ir a trabajar y a cuánto te pagan esas horas.**
Lemas alternativos: «Tu sueldo, después de Madrid» · «Cuánto te cuesta de verdad vivir donde vives».

Ficha unificada de la Propuesta A (plan1) para DataMad 2026 · 14 de noviembre de 2026.
Reúne en una sola idea las dos versiones previas:
- el [plan de Izan](../izan/plan_propuesta_A_Izan.md) (entrevista por fases, cerrada el 11/11/2026);
- la [ficha de Yeray](../yeray/ficha-salario-que-sobra.md) (10 rondas de entrevista, 11/11/2026).

Las dos versiones nacen de fusionar la idea 1 (*Salario que sobra*) con la idea 9 (*alquiler frente a renta*), reformulada como **esfuerzo** y no como legalidad.

> Las marcas **(verificar)** señalan datos o cifras que todavía no se han comprobado en la fuente primaria. Esta ficha es una **propuesta de idea**, no una decisión: antes de anotarla en `docs/decisiones.md` se pasa por `dm-abogado-del-diablo`.

## Cómo leer esta ficha

Esta ficha **describe y enmarca la idea** para saber cómo afrontarla. **No es una especificación de desarrollo.** Los métodos, fuentes y herramientas que aparecen son el **punto de partida**: lo que hoy parece mejor con lo que sabemos. Si al desarrollar aparece algo mejor, un dato que no existe o un resultado que obliga a cambiar de rumbo, se cambia y se anota el motivo.

El alcance se describe **completo**, sin recortes por plazo. Qué se hace primero y qué se deja si no da tiempo se decide al planificar (sección 15), no aquí.

**Lo que define la idea (si cambia esto, es otra idea):**
1. **La cuenta completa, con el tiempo en el centro.** Lo que sobra del sueldo después de vivienda, transporte y gastos básicos, y **cuánto te pagan por cada hora de viaje que añades** al vivir más lejos. No solo el precio del alquiler.
2. **Dos miradas sobre la misma cuenta.** La del particular que busca dónde vivir y la de la Administración que decide las ayudas.
3. **Esfuerzo, no legalidad.** Se mide qué parte de la renta se va en vivienda; no se juzga si un alquiler es legal.
4. **Datos abiertos y públicos**, con el catálogo regional en el centro, el portal del Ayuntamiento como complemento y fuentes nacionales para completar.
5. **Honestidad con los límites del dato.** Lo estimado se marca, la incertidumbre se muestra y los supuestos se declaran.
6. **Una decisión que cambia**, no solo un mapa bonito: el impacto se intenta medir.
7. **Abierto e interoperable.** Código, datos derivados, Smart Data Models y MCP, para que otros reutilicen el resultado.

**Lo que es enfoque de partida (puede cambiar):** modelos de imputación y de sobrecarga, cálculo de tiempos, umbrales y parámetros, perfiles de hogar, escenarios, herramientas, arquitectura, reparto, calendario y guion.

**Lo que está abierto:** las marcas **(verificar)**, la lista de la sección 16 y los titulares, que dependen de lo que digan los datos.

---

## 1. La idea en 30 segundos

Quien busca piso en la Comunidad de Madrid compara alquileres, pero casi nunca hace la cuenta completa: alquiler, transporte, gastos básicos y horas perdidas en ir a trabajar.

En euros, vivir lejos casi siempre sale más barato: el abono cambia poco de una zona a otra (y nada para los menores de 26), así que el ahorro en alquiler apenas se compensa. **El precio real se paga en tiempo.** Un piso 200 € más barato que añade 50 horas de viaje al mes te paga unos 4 € por cada hora extra. ¿Te compensa, si tu trabajo te paga 10 € la hora?

**¿Me sobra?** hace esa cuenta. El usuario mete su sueldo, dónde trabaja y cuántos días va a la oficina, y ve en un mapa, para cada zona (municipio y, en Madrid capital, distrito o barrio):
- cuánto dinero le queda a final de mes;
- cuántas horas al mes pasa en el transporte;
- **a cuánto le pagan cada hora extra de viaje** frente a vivir cerca del trabajo.

La misma cuenta, agregada por hogares, sirve a la **Administración** para tres cosas:
- ver dónde se concentran los hogares que dedican demasiado a vivienda y cómo ha evolucionado desde 2015;
- comprobar si el Bono Alquiler Joven llega a donde más se necesita;
- simular cómo cambiarían las ayudas si contaran el coste del transporte, y qué pasa si se acaba el descuento del abono.

**Pregunta central:** ¿cuánto dinero y cuánto tiempo te cuesta de verdad vivir en cada sitio, según dónde trabajas?

## 2. El problema

- **El alquiler se compara sin su coste asociado.** El precio de un piso no incluye el abono, el tiempo de viaje ni la diferencia de gastos según el tipo de hogar.
- **Las ayudas miden solo la renta.** El Bono Alquiler Joven fija requisitos de renta y de alquiler máximo, pero no mira cuánto cuesta desplazarse desde ese piso hasta el trabajo.
- **Solo se acepta una parte de las solicitudes de ayuda.** En la convocatoria de 2022 del Bono Alquiler Joven en la Comunidad hubo 51.735 solicitudes y 11.477 aceptadas, un 22,2 % (catálogo regional, `spacm_bono_alquiler_joven_2022`: 40.258 rechazadas; [verificación](../../../docs/verificaciones/renta-vivienda.md), fila 1a).
  - El dato es de 2022 y cuenta solicitudes, no personas.
  - **El dato no dice por qué se rechazó el resto.** Las bases excluyen por no cumplir requisitos o porque se agotó el crédito (Orden de 6-11-2023), sin recuento por motivo. No se puede decir que la demanda supera a la ayuda ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 1c y 1d).
- **El precio del transporte depende de una ayuda temporal.** En 2026 los abonos tienen un descuento que depende de que sigan las ayudas estatales. El descuento es del 50 % en el Abono Joven y del 40 % en el abono normal según el CRTM (41,8 % sobre la tarifa oficial de 2026), con la ayuda estatal del RDL 17/2025, art. 8 ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §1.1).
- **Madrid no limita el alquiler por ley.** Ningún municipio de la Comunidad figura como zona tensionada en el BOE (septiembre de 2026), y la Comunidad no aplica el mecanismo aunque el Tribunal Constitucional avaló la ley en febrero de 2026. Por eso se habla de **esfuerzo**, no de alquileres «ilegales» ni de «precio de referencia».

## 3. Para quién y qué decisión cambia

La idea tiene **dos partes** que comparten datos y cálculo:
- la **herramienta**, para particulares;
- el **análisis**, para la Administración.

| Usuario | Pregunta que responde | Decisión que cambia |
|---|---|---|
| **Particular**, sobre todo joven de 18 a 35 años que busca piso o habitación | «Con mi sueldo y mi trabajo, ¿dónde me sobra más dinero y cuánto tiempo me cuesta?» | Dónde buscar piso; si compensa compartir; cuántos días pedir de teletrabajo; transporte público o coche |
| **Administración** (Consejería de Vivienda, Consorcio Regional de Transportes, ayuntamientos) | «¿Dónde están los hogares sobrecargados, cómo ha evolucionado y a quién no llega la ayuda?» | A qué municipios dirigir el Bono; si incluir el transporte en el criterio; qué pasa si se acaba el descuento del abono; dónde falta transporte público |

La herramienta es el **gancho** de la demo. El análisis es donde está el **impacto**, porque puede cambiar una decisión pública.

**Eje regional:** el transporte (coste y tiempo) es un componente principal de la cuenta, no contexto. Así los datos de la Comunidad y del Consorcio están en el núcleo.

### Qué la hace distinta de un mapa de alquiler
- **Precedente:** el *H+T Affordability Index* del Center for Neighborhood Technology (EE. UU.) suma vivienda y transporte por zona (fuente: [htaindex.cnt.org](https://htaindex.cnt.org/about/), actualización de 2025; [verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), fila 6). Se cita para dejar claro qué es nuevo.
- **Lo nuevo de esta idea:**
  - el resultado es **individual** y depende de dónde trabaja cada persona, no es una media por zona;
  - el **tiempo** es la métrica central, con el precio de la hora de viaje, no un coste más;
  - hay una **evaluación de una política regional concreta** (el Bono Alquiler Joven y el descuento del abono) con datos de la Comunidad;
  - el resultado es **abierto e interoperable**: Smart Data Models, conjunto de datos y MCP.

### Personajes de la demo
1. **Enfermera de 26 años** en un gran hospital (La Paz o el 12 de Octubre), con turnos. Salario público conocido.
2. **Teleoperador de 23 años** con un sueldo cercano al SMI, en un polígono del sur. Es el caso «no llega».
3. **Madre sola de 34 años** con un sueldo administrativo. Es el perfil de mayor sobrecarga.
4. **Pareja de 29 años** con dos sueldos medianos y dos lugares de trabajo; uno teletrabaja tres días. Enseña el efecto del teletrabajo.

## 4. Unidad territorial

- **Base:** los 178 municipios de la Comunidad distintos de Madrid capital + los 21 distritos de la capital = 199 zonas.
  - Comprobado: los distritos censales de Madrid capital tienen los mismos 21 códigos y las mismas secciones que los distritos municipales. Los límites difieren en menos del 4 % del área de cada distrito ([verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), fila 2, #68).
- **Zoom en Madrid capital:** barrios, con el alquiler por código postal del catálogo regional llevado a barrio con una tabla de paso (sección 12).
- **Análisis de sobrecarga:** sección censal, porque es el nivel al que publican el ADRH y el SERPAVI. Se agrega a municipio y distrito para mostrarlo.
- **Clave de cruce común:** código INE de municipio + código de distrito (y de sección cuando aplique) + año.
- **Geometrías que no coinciden:** barrios municipales, distritos del MITMA, secciones del INE y códigos postales. Se construyen tablas de paso antes de cruzar nada (skill `dm-tablas-de-paso`).

## 5. Cómo funciona para el usuario

1. **Sueldo.** Escribe su sueldo bruto anual (como en una oferta de empleo) y el número de pagas, o directamente su neto mensual, con un selector. Si da el bruto, la herramienta calcula el neto (6.1), y el usuario lo puede corregir a mano.
2. **Hogar.** Elige uno de cuatro perfiles: vive solo en un piso entero, comparte piso, pareja con dos sueldos o familia monoparental. Cada perfil rellena por defecto los detalles del hogar, que se pueden ajustar:
   - adultos e hijos;
   - edad, que decide el Abono Joven y el Bono Alquiler Joven;
   - tamaño de la vivienda en m²;
   - número de personas con las que se comparte.
3. **Trabajo.** Hasta **dos sueldos y dos lugares de trabajo**. Cada lugar se elige de una lista de polos de empleo o marcando un punto en el mapa.
4. **Desplazamiento.** Modo (transporte público o coche) y días presenciales a la semana, de 1 a 5.
5. **Resultado:**
   - **mapa coloreado por el precio de la hora de viaje**, con un selector para cambiar a lo que sobra al mes o a las horas de viaje al mes;
   - lista de las 10 mejores zonas;
   - al pinchar una zona, ficha con el desglose: neto, alquiler (rango), transporte, cesta básica, horas de viaje, precio de la hora frente al salario por hora, esfuerzo y m² asequibles.
6. **¿Y si…?** Activa escenarios (sección 9) y ve cómo cambia el mapa.

**Avisos visibles en la herramienta:**
- el alquiler es de contratos declarados y se presenta como **suelo**;
- año del dato;
- zonas **estimadas**, con su intervalo;
- zonas **sin dato**, cuando ni la estimación es fiable.

Desde la herramienta hay un **enlace al informe de análisis**, que va aparte para no meter ruido.

## 6. El cálculo, paso a paso

Lo estable es **qué** se cuenta. **Cómo** se calcula cada término es el enfoque de partida y se puede sustituir por algo mejor. Todos los parámetros y supuestos están visibles en la herramienta y en la nota metodológica. El cálculo es mensual.

Para cada zona de residencia *z*:

```
sobra(z)       = neto − alquiler(z) − transporte(z) − cesta_básica
horas(z)       = horas de viaje al mes
precio_hora(z) = (sobra(z) − sobra(ref)) ÷ (horas(z) − horas(ref))
esfuerzo(z)    = alquiler(z) ÷ neto
```

- **Por qué el precio de la hora es la métrica central.** En transporte público, el coste en euros varía poco entre zonas: según el BOCM de 31-12-2025, el abono normal con bonificación va de 32,70 € en la zona A a 49,20 € en la C2, y el Abono Joven cuesta 10 € en todas ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §1.2). La cesta básica es igual en todas las zonas. Por tanto, el mapa del sobrante en euros se parece mucho al del alquiler con el signo cambiado. Lo que de verdad cambia entre zonas es el tiempo.
- **Qué mide.** Cuántos euros al mes ganas por cada hora extra de viaje al mes al vivir en *z* en lugar de en la zona de referencia.
  - **Zona de referencia:** la que el usuario elija (por ejemplo, donde vive ahora); por defecto, la zona con menos horas de viaje a su trabajo.
  - **Lectura:** se compara con su **salario neto por hora**. Si vivir lejos te paga menos por hora que tu trabajo, estás vendiendo tu tiempo barato.
  - **No obliga a poner precio al tiempo:** es un precio revelado que cada usuario juzga con su propio salario.
  - **Solo se calcula si la diferencia de horas es relevante:** con unas pocas horas al mes de diferencia el cociente se dispara, así que por debajo de un umbral (punto de partida: 5 horas al mes) se muestra «mismo tiempo».
- Todo se lee sin explicación («te sobran 180 € al mes», «vivir aquí te paga 4 € por hora de viaje») y cada término se ve por separado. No se fusiona en un índice opaco de 0 a 100.
- **Euros y horas no se suman.** Quien quiera restar su tiempo en euros tiene un deslizador opcional, apagado por defecto (6.5).
- **Incertidumbre propagada:** el sobrante se muestra como **una sola banda** que combina el rango del alquiler (P25–P75), el intervalo de la imputación si la zona es estimada y el margen del cálculo del neto.

### 6.1 Neto
- **Fórmula:** bruto − cotizaciones del trabajador a la Seguridad Social (hasta la base máxima) − cuota anual de IRPF, todo ÷ 12.
  - La cuota de IRPF tiene un tramo estatal y uno autonómico de Madrid, y descuenta la reducción por rendimientos del trabajo y los mínimos personales y familiares.
  - Tributación individual.
- **Se usa la cuota anual y no la retención de la nómina.** La retención mensual puede diferir (luego hay devolución o pago en la declaración); la cuota es lo que de verdad se paga. Se explica en la nota metodológica. El número de pagas (12 o 14) cambia el neto de cada mes, no el anual.
- Parámetros de 2026, cada uno citado a su norma (skill `dm-calculos-normativos`).
- **Control de calidad:**
  - se contrasta con nóminas reales;
  - lo audita `dm-auditor-calculos-normativos` antes de presentar ninguna cifra.

  Un error fiscal destruye la credibilidad de todo lo demás.

### 6.2 Alquiler
**Fuente base: alquiler de contratos declarados**, no precios de anuncios.
- **Municipios, distritos y secciones:** SERPAVI del Ministerio de Vivienda. Da €/m², cuantía y superficie, con mediana, P25 y P75, separando vivienda colectiva y unifamiliar.
- **Madrid capital por barrio:** alquiler medio mensual por código postal del catálogo regional (`1934258`, 2023 y 2024, solo códigos con más de 200 viviendas alquiladas), llevado a barrio con una tabla de paso.
- **Actualización a hoy:** variación del IPC de vivienda en alquiler de la Comunidad de Madrid, serie INE `IPC297196` (base 2025, mensual). El catálogo regional `1934665` queda como control; en él, la fila de Madrid es la segunda de cada año ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 5a y 5b).
- **Cálculo:** alquiler(z) = €/m²(z, colectiva, último año) × factor del IPC de alquiler × m² ÷ personas. Se calcula con la mediana, el P25 y el P75.
- **Por hogar:**
  - **compartido:** el alquiler del piso se divide entre las personas, como supuesto declarado. No hay dato oficial abierto del precio de una habitación. Si aparece una fuente legal de oferta de habitaciones, se calibra un recargo por habitación.
  - **pareja y monoparental:** se usa un piso de tamaño adecuado al hogar (superficie media del SERPAVI y del panel municipal).
- **Lectura:** el dato sale de contratos ya firmados, muchos antiguos, así que **va por debajo del precio que se encuentra hoy**. Se presenta como **suelo**: lo que sobra será, como mucho, lo que dice la herramienta.
- **Precio de oferta:**
  - No se hace scraping de portales inmobiliarios (sección 14).
  - Si se encuentra una fuente municipal legal con precio de oferta, se calcula un **factor de brecha** por zona (oferta ÷ contrato actualizado) y la banda pasa a ser «te sobran entre X con precio de contrato e Y con precio de anuncio».
  - La serie de Idealista por barrio que se creía publicada por el Ayuntamiento **no se ha encontrado** en datos.madrid.es.

### 6.3 Transporte
**Transporte público:**
- **Tarifas 2026 por zona** (A, B1, B2, B3, C1, C2), del BOCM de 31 de diciembre de 2025. El conjunto de tarifas del catálogo regional (`1919188`, 2007–2024) **no sirve**: solo trae la Corona Mínima y la Máxima y no llega a 2025–26.
- **Zona necesaria:** la más exterior entre la del origen y la del destino.
- **Título más barato** según los días presenciales: abono mensual, billetes de 10 viajes o sencillos.
- **Abono Joven:** tarifa plana para jóvenes. Se tiene desde los 15 años hasta cumplir 26 (ficha del CRTM; [referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §1.2).
- **Precios 2026 (BOCM-20251231-2):** joven 10 € con descuento y 20 € sin él; A 32,70 €; B1 38,20 €; B2 43,20 €; B3, C1 y C2 49,20 €.
- **Consecuencia:** para quien usa transporte público, el coste apenas diferencia zonas; para los jóvenes con Abono Joven no las diferencia nada. Se dice así, no se esconde (6, 7.4).

**Coche:**
- coste(z) = 2 × distancia × días × coste por km (parámetro justificado) + aparcamiento en destino.
- **Limitación:** el enrutado no tiene en cuenta el tráfico, así que el tiempo en coche sale subestimado. Se aplica un factor de congestión justificado o se declara la limitación.

### 6.4 Cesta básica
- Gasto en alimentación y suministros (luz, agua, gas) por tipo de hogar, de la Encuesta de Presupuestos Familiares del INE para la Comunidad de Madrid. No incluye el alquiler, para no contarlo dos veces.
- Sin este término, «no llega» engañaría: a alguien a quien le sobran 300 € después del alquiler puede no llegarle para el mes.

### 6.5 Tiempo de viaje
- **Cálculo:**
  - con los GTFS del CRTM (Metro, Metro Ligero, Cercanías, interurbanos, EMT y urbanos) y la red de OpenStreetMap, con r5py (u OpenTripPlanner);
  - tiempo puerta a puerta: mediana de las salidas entre las 7:30 y las 8:30 de un martes laborable;
  - el coche se enruta sobre la red viaria de OpenStreetMap.
- **Origen:** centro de población de cada zona, ponderado por secciones censales.
- **Destinos:**
  - **Polos de empleo, obtenidos de datos:** las zonas que más viajes de casa al trabajo reciben. Se usan dos fuentes que se comparan entre sí: la Encuesta Domiciliaria de Movilidad 2018 del CRTM (regional, flujos reales) y la movilidad con telefonía del MITMA (más reciente). Si coinciden, se refuerzan; si no, es un hallazgo. Alternativa: afiliación por municipio del centro de cotización.
  - **Destino libre:** la matriz de tiempos se precalcula desde cada zona hacia una rejilla fina (o hacia todas las secciones censales). El punto que marca el usuario se resuelve con la celda más cercana, sin servidor y sin depender de un servicio en vivo.
- **Horas al mes** = tiempo de ida y vuelta × días presenciales × 4,33.
- **Precio de la hora de viaje:** es la métrica central y se explica en la sección 6. No necesita fijar un valor del tiempo.
- **Valor del tiempo (opcional):** deslizador apagado por defecto. Al activarlo, resta horas × valor de la hora, con un 50 % del salario por hora como supuesto de partida, no como dato. La guía de la Comisión Europea (2014, pág. 90) valora el tiempo no laboral entre el 25 % y el 40 % del valor del tiempo de trabajo, que es el coste laboral por hora y no el salario ([verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), fila 7; [referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §3.1). Lleva un aviso visible de que poner precio al tiempo es una convención discutible.

### 6.6 Asequibilidad
- **Alquiler máximo asumible** y **m² que puedes pagar** en cada zona.
- **Umbrales:**
  - **30 %** del neto en alquiler: recomendación de la herramienta y umbral complementario en el análisis;
  - **40 %:** **sobrecarga** según Eurostat. Su definición cuenta **todos los gastos de vivienda**, suministros incluidos, así que para compararlo se usa alquiler + suministros de la EPF, no solo el alquiler.

### 6.7 Zonas sin dato de alquiler
El SERPAVI solo publica celdas con al menos 10 testigos. A nivel nacional, solo el 31,6 % de los municipios tiene dato de vivienda colectiva, así que habrá huecos en municipios pequeños, sobre todo en la corona C, justo donde los jóvenes buscan barato.

- **Imputación:** se estima el alquiler con un modelo que usa:
  - renta (ADRH del INE);
  - valor catastral;
  - precio de compraventa (Notariado, si la licencia lo permite);
  - tiempo a los polos de empleo;
  - población.
- **Modelo de partida:** gradient boosting (LightGBM) con **validación cruzada espacial**: las particiones son zonas, no filas al azar, para que no se cuele información de los vecinos.
  - Los intervalos se calculan con **predicción conformal**, que solo garantiza la cobertura si los casos que se predicen se parecen a los de calibración. Aquí no es así: los municipios sin dato son los pequeños, y el modelo se entrena con los grandes y extrapola. Por eso:
    - la validación oculta los **municipios más pequeños que sí tienen dato**, que son los más parecidos a los huecos;
    - el conformal se **estratifica por tamaño** de municipio;
    - la cobertura se **comprueba** en esa validación y se informa del resultado, sin prometerla.
  - Se compara siempre con un modelo de referencia simple; si no lo mejora, se usa el simple.
  - Skill: `dm-modelado-espacial`.
- **Alternativa por zona:** si se justifica, el dato de vivienda unifamiliar, señalado como tal.
- Las zonas estimadas aparecen como **«estimado»**, con su intervalo. Si el intervalo es tan ancho que no informa, la zona queda como **«sin dato»**.

## 7. El análisis para la Administración

Va en un **informe aparte**: un notebook o un Quarto publicado como página estática en el mismo repositorio, con la metodología. Hay **dimensión temporal** en todos los bloques en los que las series lo permiten. El SERPAVI empieza en 2011 y la renta del INE en 2015, así que la ventana común arranca en 2015.

### 7.1 Esfuerzo alquiler/renta por zona (idea #9)
- **Fórmula:** alquiler mediano del SERPAVI ÷ (renta neta media del hogar del ADRH ÷ 12).
- Mapa por año y evolución: dónde ha crecido más el esfuerzo desde 2015.
- **Limitación declarada:** la renta media incluye a los propietarios, que suelen ganar más que los inquilinos. Por eso el indicador **subestima** el esfuerzo de quien alquila. El bloque 7.2 lo corrige.

### 7.2 Hogares en sobrecarga
- **Definición:** un hogar está sobrecargado si sus gastos de vivienda (alquiler + suministros) superan el 40 % de su renta (Eurostat). Como indicador complementario, se da el porcentaje de hogares con un alquiler por encima del 30 %.
- **Renta:** ADRH 2024 del INE, publicado el 19 de octubre de 2026, por municipio, distrito y sección censal. El Gini del INE se calcula con las colas recortadas (1,5 % por lado), y el Gini y el P80/P20 solo se publican en unidades de 100 residentes o más ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 2b y 2d).
- **Unidad coherente:** en el ADRH, el Gini y el P80/P20 se calculan sobre la **renta por unidad de consumo** (de personas), no sobre la renta por hogar. Todo el cálculo se hace en esa escala: la media por unidad de consumo y el alquiler pasado a unidad de consumo con la escala de equivalencia de la OCDE modificada, con el tamaño medio del hogar de cada sección. El reescalado se declara.
- **Método:**
  - El INE publica la media, pero no la distribución completa. Por cada sección se ajusta una **distribución log-normal** de la renta por unidad de consumo.
    - En una log-normal, el Gini y el P80/P20 fijan el mismo parámetro de dispersión σ. Se estima σ con los dos y se usa su diferencia como comprobación de que la forma log-normal encaja; la media fija el otro parámetro.
  - El alquiler **no es único**: se integra sobre la distribución de alquileres de la sección (entre P25 y P75 del SERPAVI), no se aplica la mediana a todos los hogares.
  - Con las dos distribuciones se calcula qué porcentaje de hogares inquilinos supera cada umbral.
- **Corrección por inquilinos:**
  - Proporción de hogares en alquiler por zona: por municipio, el catálogo regional `censo_2021_viviendas_familiares_por_tenencia` (Censo 2021 del INE); por sección, el INE `C2021_Indicadores.csv`, variable `t20_2` (viviendas en alquiler, provisional). El identificador `19155xx` no existe ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 4a y 4b).
  - Diferencia de renta entre inquilinos y propietarios: cociente de la Encuesta de Condiciones de Vida del INE. Es un **supuesto declarado**: el cociente es regional y se aplica igual en todas las secciones.

  Sin esa corrección, la sobrecarga saldría infravalorada.
- **Validación (externa, no circular):**
  - El porcentaje bajo el 60 % de la mediana depende del mismo σ, así que no valida nada y no se usa para eso.
  - Se agrega la sobrecarga estimada a toda la Comunidad y se compara con la tasa de sobrecarga de la población de Madrid en la ECV (9,9 % en 2025, Eurostat `ilc_lvho07_r`). La tasa de los inquilinos de Madrid no está publicada ni tiene margen de error ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 3a, 3b y 3c). La validación queda pendiente de la fase S3.
- El resultado se presenta **como rango**, con la metodología explícita.
- **Relación con la herramienta:** la herramienta trabaja con el sueldo de una persona; el análisis, con la renta de los hogares. Son dos lecturas de la misma cuenta, una individual y otra agregada.

### 7.3 ¿Llega el Bono Alquiler Joven a donde más se necesita?
- Se cruzan las solicitudes, aceptaciones y rechazos del Bono por municipio (convocatoria de 2022) con un indicador de **necesidad joven** = sobrecarga de los inquilinos (7.2) × población joven del municipio.
  - El ADRH no desagrega la renta por edad, así que no se puede calcular una «sobrecarga de los jóvenes» propiamente dicha. El indicador supone que los jóvenes inquilinos se reparten la sobrecarga como el resto de inquilinos de su zona, y se declara así.
- Se marcan los municipios con mucha necesidad y poca ayuda.
- Antes de leer los rechazos como falta de ayuda, se comprueba su motivo (sección 2).
- Es una evaluación de política pública hecha con datos regionales.
- **Limitación:** solo hay datos de un año, no de todos los municipios (160 según el plan de Izan; hay 3.352 solicitudes sin municipio).

### 7.4 Simulación: un criterio del Bono que cuente el transporte
- Se simula un criterio de elegibilidad que cuente alquiler + transporte, no solo la renta.
- **Con casos tipo, no con personas.** No hay microdatos abiertos que junten renta, alquiler y lugar de trabajo de los jóvenes, así que no se puede contar cuántos jóvenes reales entrarían o saldrían.
  - Se simulan **perfiles tipo**: los personajes y los deciles de salario del INE por edad, en cada municipio y hacia los polos de empleo.
  - **Resultado:** qué perfiles cambian de grupo y dónde. Si se da un orden de magnitud de personas o de coste, se escala con la población joven y la proporción de inquilinos, y se marca como **estimado**.
- **Resultado esperado y válido:** como el Abono Joven cuesta lo mismo en todas las zonas, puede que el criterio con transporte apenas cambie nada en euros. Si sale así, es un hallazgo: «el Abono Joven ya iguala el coste del transporte; lo que no iguala es el tiempo». Se puede probar también un criterio que cuente las horas de viaje.
- **Reglas de referencia** (Real Decreto 42/2022): de 18 a 35 años, ingresos de hasta 3 veces el IPREM, alquiler máximo de 600 € o 300 € por habitación (ampliable por la comunidad) y ayuda de 250 € al mes. La convocatoria de Madrid de la ronda «2024» (BOCM-20250110-20) usa las mismas reglas, con 900 € / 450 € en 54 municipios ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/ayudas-vivienda.md), §1 y §2.2). El umbral de 3 × IPREM se calcula con el IPREM de 14 pagas (8.400 € al año en 2023); su vigencia en 2026 no está verificada en una norma de 2026.

### 7.5 Fin del descuento del abono
Para cada municipio: euros al mes que se pierden y hogares que pasan a estar sobrecargados si el descuento del 50 % desaparece.

### 7.6 Euros frente a tiempo hacia los polos de empleo
- Coste y tiempo desde cada zona hacia los polos de la 6.5.
- **Hallazgos buscados:**
  - **déficit de transporte:** zonas donde el coche gana con mucha diferencia al transporte público, declarando que el tiempo en coche no tiene en cuenta el tráfico;
  - **efecto del Abono Joven de tarifa plana:** con él, vivir lejos se paga en tiempo y no en dinero (hipótesis que el análisis tiene que contrastar).

### 7.7 Rentabilidad implícita
- **Fórmula:** alquiler anual (SERPAVI) ÷ precio de compraventa (Notariado), por zona.
- Muestra dónde comprar compensa frente a alquilar.
- Depende de la licencia del Notariado (sección 12.3).

## 8. Qué esperamos encontrar

Hay dos tesis complementarias. Las confirma o las descarta el dato, no al revés:
1. **«Vivir lejos te paga X € por hora de viaje».** En euros casi siempre compensa vivir lejos, porque el abono apenas cambia entre zonas. Pero, dividido entre las horas extra, el ahorro en alquiler paga cada hora de viaje por debajo del salario por hora de un sueldo típico. Vivir lejos se paga en tiempo, no en dinero.
2. **«Ningún sueldo típico llega».** Con sueldos de referencia, en muchos municipios no sobra nada después de los gastos básicos.

**Plan B del titular.** Si la primera tesis no se cumple en todas partes (por ejemplo, en ejes del sur con Cercanías el precio de la hora puede ser alto), el titular pasa a ser **«Dónde vivir lejos te paga bien tu tiempo y dónde no»**, explicado por la red de transporte. Un resultado matizado da más credibilidad ante un jurado técnico.

**Primer indicio** (MITMA, un solo día, el 15 de octubre de 2025, sin validar). Entre los residentes de la Comunidad que van de casa al trabajo o al estudio:
- **Menores de 25 años:** 9,4 km de media en zonas de renta de 10.000 a 15.000 €, frente a 8,6 km en zonas de más de 15.000 €.
- **De 25 a 45 años:** 8,1 km frente a 7,0 km.
- **Más de 10 km:** los hace el 29 % de las zonas de renta menor, frente al 24 %.

Apunta a la primera tesis, pero no es un resultado: falta repetirlo con un mes completo, por distrito y teniendo en cuenta dónde está el empleo.

**Sueldos de referencia:**
- **Deciles de salario del INE por edad** (Encuesta de Estructura Salarial y EPA): permiten decir «el joven mediano de 25 a 34 años».
- **IRPF por municipio** de la Agencia Tributaria: el sueldo de quien ya vive en cada sitio, para el análisis (**verificar** el último año; sin verificar en F0-04/F0-05, porque ninguna fila de `docs/verificaciones/` lo cubre).
- **Salarios por ocupación del INE:** dan cifras reconocibles para los personajes.

## 9. Escenarios «¿y si…?»

Son la parte prospectiva de la idea, porque responden a decisiones concretas:
- Se acaba el descuento del 50 % del abono.
- El alquiler sube un X % (deslizador).
- El usuario cumple la edad límite y pierde el Abono Joven.
- Cambia el número de días presenciales.
- Cambia el lugar de trabajo o el modo de transporte.

Los escenarios aparecen en la herramienta (efecto individual) y en el análisis (efecto agregado, 7.4 y 7.5).

## 10. Validación e impacto

### 10.1 ¿El índice mide lo que dice? (validación externa)
Si el mapa de sobrecarga es correcto, debería ir en la misma dirección que señales independientes:
- **desahucios por la Ley de Arrendamientos Urbanos** por distrito (panel municipal): más sobrecarga, más desahucios;
- **vivienda como problema principal** por distrito (Encuesta de Calidad de Vida del Ayuntamiento);
- **vulnerabilidad territorial** (índice IGUALA del Ayuntamiento);
- **rechazos del Bono Alquiler Joven** por municipio, frente a la sobrecarga estimada.

**Cómo se lee la correlación:**
- **Control por renta.** Desahucios, IGUALA y vivienda como problema están ligados a la renta baja, y la sobrecarga se construye con la renta. Saldría correlación aunque el componente del alquiler fuera ruido. Por eso se usa la **correlación parcial controlando por renta**, y se compara con un índice que use solo la renta: el de sobrecarga tiene que explicar algo más.
- **Poca potencia en Madrid capital.** Con 21 distritos, una correlación solo es significativa al 5 % si supera r ≈ 0,43. Se declara, y donde el dato lo permite se trabaja por barrio o por municipio (rechazos del Bono), con más observaciones.
- Se informa de la correlación y de su signo también cuando no sale la esperada.

### 10.2 ¿El dato es fiable? (validación del dato)
- Error del modelo de imputación en validación cruzada espacial, frente al modelo de referencia.
- Cobertura real de los intervalos conformales.
- Ajuste de la log-normal: coherencia entre el σ que da el Gini y el que da el P80/P20, y sobrecarga agregada frente a la de la ECV.
- Neto frente a nóminas reales y casos de referencia.
- Tamaño de la brecha entre oferta y contrato, si se encuentra una fuente legal de oferta.

### 10.3 ¿Cambia decisiones? (impacto medido)
En los concursos revisados, casi ningún ganador mide su impacto. Esta idea lo intenta con dos piezas:
- **Simulación del Bono** (7.4): cuántos jóvenes y cuánto dinero cambiarían de grupo con un criterio que incluya el transporte.
- **Test piloto con usuarios, antes y después.** Se presenta como **piloto**: sin grupo de control y con respuestas autodeclaradas, no demuestra un efecto causal.
  - **Participantes:** 15 a 30 jóvenes que **estén buscando piso de verdad**, o que lo hayan buscado hace poco, no estudiantes en general. Se reclutan en la red del equipo, en organismos de juventud y en aulas de la URJC y la UCM.
  - **Procedimiento:** primero dicen dónde buscarían piso y cuánto creen que les sobraría; después usan la herramienta y responden de nuevo.
  - **Métricas fijadas por escrito antes del test:**
    - porcentaje que cambia la zona donde buscaría piso;
    - diferencia entre lo que creían que les sobraría y lo que calcula la herramienta.

    Como métrica secundaria, usabilidad con el cuestionario estándar SUS.
  - **Ética:** consentimiento informado y sin datos personales identificables (RGPD).
  - **Plan B:** si el piloto no se puede hacer con una herramienta que funcione, la pieza de impacto es solo la simulación del Bono.

## 11. Apertura, interoperabilidad e IA

### 11.1 Smart Data Models
- Los impulsa el autor del repositorio de la organización, que forma parte del jurado.
- **Uso:**
  - normalizar paradas y horarios del CRTM con los modelos GTFS de *UrbanMobility* (`GtfsStop`, `GtfsStopTime`, `GtfsAgency`…);
  - revisar qué modelos encajan para zonas administrativas, vivienda e indicadores (carpeta `pysmartdatamodels/` del repositorio de la organización).
- **Salida:** los indicadores por zona y año se publican en un esquema de Smart Data Models.
- **Contribución:** si no existe un modelo adecuado, se propone uno nuevo, por ejemplo un indicador de asequibilidad de la vivienda, mediante su proceso de creación de modelos (un PR a su repositorio).

### 11.2 Datos abiertos derivados
- El índice y sus componentes como conjunto de datos por municipio, distrito y barrio.
  - Formatos: CSV y GeoParquet.
  - Metadatos DCAT-AP y licencia CC BY 4.0, citando las fuentes.
- Se **propone formalmente** al catálogo regional o a datos.gob.es. Cierra el ciclo que repite la organización: «Abrir → Conectar → Analizar → Reutilizar → Crear».
- **API estática:** los mismos ficheros, publicados con URL estable junto a la web, sin servidor.

### 11.3 Servidor MCP
- **Servidor MCP en Python, local (stdio) y distribuible:** cualquiera lo instala desde el repositorio con un comando y lo conecta a su asistente. Así es «público» sin que nosotros mantengamos un servidor, coherente con la arquitectura sin servidor (13).
- **Lee la API estática de la web** (11.2): descarga y cachea los ficheros publicados, o usa los del repositorio sin conexión.
  - El cálculo se hace en la máquina de quien pregunta, así que su sueldo tampoco sale de su equipo.
  - Las cifras del MCP y de la web son las mismas, porque salen de los mismos ficheros.
- **Ejemplo:** cualquier asistente puede preguntar «¿dónde me sobra más con 24.000 € trabajando en Getafe?» y recibir cifras calculadas con su fuente.
- **Instancia remota alojada:** solo como extra opcional (un servicio gratuito de solo lectura), independiente de la web. Si cae, no afecta a nada más. No forma parte de lo que define la idea.
- **Herramientas propuestas:** `calcular_sobrante(bruto, hogar, trabajo, …)`, `ranking_zonas(…)` e `indicadores_zona(zona, año)`.
- Validación estricta de los argumentos y sin credenciales.
- **Demo:** preguntas en lenguaje natural desde Claude. El 100 % de las cifras sale de las herramientas, nunca del modelo.
- Encaja con la formación oficial de DataMad (APIs, MCP y espacios de datos; IA aplicada a datos abiertos).

### 11.4 Código
Repositorio con licencia MIT que:
- regenera todo con un comando desde las fuentes oficiales;
- incluye pruebas del neto, del índice y de los cruces;
- incluye una nota metodológica de 2 o 3 páginas con supuestos, límites y validación.

## 12. Datos

Hay que leer los metadatos de cada fuente antes de usarla: estado del dato, unidad y año. Cada fuente se incorpora con la skill `dm-nueva-fuente`: descarga con fecha en `data/raw/`, SHA-256 y fila en `data/README.md`.

### 12.1 Catálogo regional (datos.comunidad.madrid, CKAN, CC BY 4.0) · obligatorio
| Conjunto | Qué aporta | Límite |
|---|---|---|
| `spacm_bono_alquiler_joven_2022` | Solicitudes, aceptadas y rechazadas por municipio (51.735 / 11.477 / 22 %) | Solo 2022; 3.352 solicitudes sin municipio |
| `1934258`, `1934261` | Alquiler medio mensual y días alquilados por código postal | Solo Madrid capital, 2023–2024, códigos con más de 200 viviendas |
| `1934246` | Alquiler, m², rentabilidad y valor de referencia | Solo el total de la Comunidad |
| `valor_referencia_viviendas_arrendadas_…_mas_20000` | Valor catastral de referencia (no es alquiler) | 38 municipios con valor en 2024 |
| `1934665` (base 2025) | IPC de vivienda en alquiler, control | Índice, no nivel de precio; la fila de Madrid es la segunda de cada año. El factor usa `IPC297196` del INE |
| `1919188` | Tarifas 2007–2024 | Solo Corona Mínima y Máxima: no sirve para las zonas |
| `1916304` | Renta neta media de la ECV (Base 2013) | Solo la Comunidad entera: sirve como contraste regional, no por zona |
| `censo_2021_viviendas_familiares_por_tenencia` | Viviendas principales por régimen de tenencia, por municipio (Censo 2021 del INE) | Sin distrito; por sección, INE `C2021_Indicadores.csv` (`t20_2`) |
| `afiliados_por_residencia_*` | Afiliados por municipio de residencia (edad, contrato, jornada) | Por residencia, no por lugar de trabajo |
| Paro registrado por municipio | Contexto e indicadores | — |
| `zt84`, `resultados-edm2018` | Zonificación de transporte y Encuesta Domiciliaria de Movilidad 2018 | Datos de 2018 |

### 12.2 Portal del Ayuntamiento (datos.madrid.es, CKAN, CC BY 4.0) · zoom a barrio y validación
| Conjunto | Qué aporta |
|---|---|
| `300087-0-indicadores-distritos` | Renta neta media por hogar por barrio 2016–2023 (en 2023, Puente de Vallecas 32.666 € frente a Chamartín 79.274 €) · renta por persona por barrio · valor catastral residencial · superficie media en compraventa · desahucios por la LAU · hogares monoparentales · paro |
| `300438-0-hogares-tamano` | Hogares por tamaño y composición por sección censal |
| `300431-0-personas-viven-solas` | Personas que viven solas por edad y barrio |
| `300588-0-estudio-panel-hogares` | Panel de Hogares (revisar si pregunta por el gasto en vivienda) |
| `319934-0-encuesta-calidad-de-vida-resultados` | La vivienda como problema percibido |
| `300577-0-iguala-vulnerabilidad`, `300301-0-ranking-vulnerabilidad` | Vulnerabilidad territorial |
| `300526-0-promociones-viviendas-emvs` | Vivienda pública municipal por distrito y año |
| `900030-0-emt-autobus-gtfs`, `900031-0-emt-autobus-api` | Red de EMT |
| `300496-0-barrios-madrid` | Geometría de los barrios |

### 12.3 Fuentes nacionales y otras
| Fuente | Qué aporta | Estado |
|---|---|---|
| **SERPAVI (Ministerio de Vivienda)** | Alquiler de contratos por municipio, distrito y sección: €/m², cuantía, superficie, mediana, P25 y P75, colectiva y unifamiliar | Excel completo localizado; descarga manual pendiente (ver abajo) |
| **INE ADRH 2024** | Renta por hogar y persona, Gini, P80/P20, % por debajo del 60 % de la mediana **nacional** por unidad de consumo, % de salarios sobre la renta **bruta**; por municipio, distrito y sección | Publicado el 19 de octubre de 2026. Gini y P80/P20 solo en unidades de 100 residentes o más ([verificación](../../../docs/verificaciones/renta-vivienda.md), fila 2a) |
| **INE IPVA** | Índice de alquiler por municipio y por distrito de las capitales | Último año 2024 |
| **INE EPF** | Gasto en alimentación y suministros por unidad de consumo (catálogo `gasto_por_subgrupo_gasto_3_digitos_coicop_epf_base_2006`); no hay cruce con el tipo de hogar | Catálogo regional ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 6a y 6c) |
| **INE ECV y Censo 2021** | Renta de inquilinos frente a propietarios; tenencia de la vivienda | Tenencia por sección (`t20_2`, provisional) y por municipio en el catálogo regional ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 4a y 4b) |
| **INE, salarios** | Deciles por edad y salarios por ocupación | Por descargar |
| **MITMA, movilidad con telefonía** | Viajes diarios de casa al trabajo por municipio y distrito, con distancia, tramo de renta del origen (<10, 10–15, >15 mil €), edad y sexo | CC BY 4.0. Ficheros diarios hasta octubre de 2025 como mínimo |
| **CRTM** | GTFS de las seis redes | **Licencia sin confirmar** (su página de licencia devolvió error 500); revisar la cláusula sobre redistribuir con la misma licencia |
| **BOCM 31/12/2025** | Tarifas 2026 por zona | Leído: BOCM-20251231-2, pág. 66 ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §1.2) |
| **Agencia Tributaria** | IRPF por municipio | Verificar el último año |
| **Notariado** | Precio de compraventa por municipio y código postal | El equipo tiene acceso a la API; **licencia, enlace y cobertura municipal pendientes** |
| **OpenStreetMap** | Red peatonal y viaria para el enrutado | ODbL: citar «© OpenStreetMap contributors» |

### 12.4 SERPAVI: lo que sabemos
- **Excel de 67,8 MB** titulado «2011–2024»: `https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03_09_bd_SERPAVI_2011-2024%20-%20DEFINITIVO%20WEB_v2.xlsx`. Se guarda en `data/raw/serpavi/`.
- **Capas shape** (sección censal, distrito, municipio) en el mismo dominio: `cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/`.
- **Metodología** (18/03/2026): `https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03-18_Metodologia_SERPAVI.pdf`.
- **Origen de los datos:** IRPF (modelo 100) cruzado con el Catastro. Madrid está incluida, con 474.935 testigos de vivienda colectiva en 2024.
- **Riesgos:**
  1. La metodología dice que las descargas llegan hasta 2023; el nombre del fichero dice 2024. Se comprueba al abrirlo.
  2. Solo se publican celdas con al menos 10 testigos, lo que deja huecos (6.7).
  3. Son contratos declarados, no precios de oferta, así que el dato es un **suelo** (6.2).

### 12.5 Gotchas de acceso
- El proxy del equipo bloquea con un 403 la descarga automática del SERPAVI y también la API CKAN de la Comunidad. Las descargas se hacen a mano o desde otra red, y quedan documentadas.
- La API CKAN devuelve pocos registros por llamada: hay que paginar o descargar el fichero completo.
- Normalizar el formato numérico español y forzar UTF-8.

## 13. Arquitectura

Lo importante es que la demo no dependa de un servidor, que el sueldo del usuario no salga de su navegador y que todo sea reproducible y abierto. Las herramientas concretas son la opción de partida.

### 13.1 Pipeline
Pipeline en **Python con DuckDB**, offline y reproducible. Descarga las fuentes, las cruza, calcula los indicadores, entrena la imputación y precalcula todo lo pesado:
- matrices de tiempo y distancia en transporte público y en coche, salida entre 7:30 y 8:30, entre zonas y hacia la rejilla del destino libre;
- alquiler por zona y año (mediana, P25, P75 y estimados con su intervalo);
- tarifas de transporte;
- rejilla de netos;
- polígonos simplificados de las zonas.

Lo exporta a JSON, CSV o GeoParquet.

### 13.2 Herramienta web
**App 100 % estática** publicada en GitHub Pages: sin servidor, gratis y **privada**.

- **Sin lógica fiscal en JS.** El neto se precalcula en Python sobre una rejilla de brutos (por ejemplo, cada 250 €) × configuraciones de hogar, y el JS solo interpola linealmente. La cuota de IRPF es lineal por tramos, así que el error es despreciable.
- **Lo que hace el JS:** interpolar el neto, consultar las tablas, sumar, pintar el mapa y validar las entradas.
- **Pruebas de referencia:** Python genera casos con resultado conocido y el JS tiene que reproducirlos.
- **Sin peticiones a terceros:**
  - las librerías van dentro del repositorio, no en un CDN;
  - mapa de coropletas con MapLibre, sin teselas externas o con un mapa base propio en PMTiles servido desde el mismo sitio.
- **Seguridad:** validación estricta de todas las entradas (rangos y tipos); ninguna entrada se inserta como HTML.
- **Desarrollo:** el JS se escribe con ayuda de IA; nadie del equipo lo domina, y por eso la lógica pesada vive en Python.

### 13.3 Resto de piezas
- **Informe de análisis:** notebook o Quarto estático en el mismo sitio (sección 7).
- **Servidor MCP:** Python local, que se instala desde el repositorio y lee la API estática (11.3). No necesita servidor propio; una instancia alojada sería un extra independiente de la web.
- **Licencias:** MIT para el código y CC BY 4.0 para los datos derivados, citando las fuentes.

## 14. Lo que queda fuera y por qué

No es una cuestión de plazo: son piezas que restarían credibilidad o que no aportan. Si cambian las condiciones que se indican, se puede reconsiderar.

| Pieza | Por qué queda fuera | Qué tendría que cambiar |
|---|---|---|
| Scraping de Idealista y Fotocasa | Lo prohíben sus condiciones de uso y ha habido pleitos; en un evento oficial resta aunque solo se publique un agregado | Una fuente legal de precio de oferta |
| Predicción del alquiler a 12 meses, del sobrante futuro y de la sobrecarga futura | Con tan pocos años de serie, los intervalos salen tan anchos que no informan; los escenarios cubren la parte prospectiva | Una serie más larga o un indicador adelantado que demuestre poder predictivo en validación temporal |
| Asistente conversacional dentro de la web | Exige clave de API, coste, servidor, defensa contra prompt injection y las obligaciones del artículo 50 del Reglamento de IA, para aportar poco más que el MCP | Que el MCP no baste para la demo. En ese caso, la puerta de calidad de la ficha de Yeray: 50 preguntas, incluidas trampas, 100 % de cifras exactas y con fuente, y un solo fallo numérico lo deja fuera |
| Backend (FastAPI) | Con el destino libre precalculado no hace falta, y la app estática es más segura en la demo y mejor para la privacidad | Que aparezca una función que no se pueda precalcular |
| Monetizar el tiempo por defecto | Mezcla unidades e infla las cifras; queda como deslizador opcional | — |
| Modo «comprar» (hipoteca) | Otra pregunta y otro usuario; el Notariado solo se usa para la rentabilidad implícita y como variable de la imputación | — |
| Vistas para pymes o para la Administración dentro de la app | La Administración tiene su informe aparte | — |

## 15. Equipo, bloques y calendario

**Equipo:** 3 científicos de datos. Nadie tiene perfil de frontend ni de presentación. El frontend se apoya en desarrollo asistido por IA, y una persona se reserva para el piloto con usuarios y el relato. El reparto lo decide el equipo.

**Bloques de trabajo:**
1. **Alquiler y renta:** SERPAVI, alquiler regional por código postal, IPC, ADRH, imputación, sobrecarga, Bono y rentabilidad implícita.
2. **Movilidad y coste:** GTFS, OpenStreetMap, polos de empleo (EDM2018 y MITMA), matrices de tiempo, tarifas, neto y cesta básica.
3. **Producto y relato:** herramienta web, informe, Smart Data Models, conjunto de datos, MCP, piloto con usuarios, validación y presentación.

**Fechas:**

| Fecha | Hito |
|---|---|
| 22 nov | **Datos y cálculos congelados** (propuesta, por confirmar en `docs/decisiones.md`) |
| 26 nov | **Presentación ante el jurado** en la URJC (fecha de la organización) |

La ficha describe el alcance completo. La prioridad entre piezas se fija al planificar contra estas fechas, empezando por lo que define la idea (sobrante, esfuerzo, Bono) y siguiendo por lo que la refuerza.

## 16. Riesgos y verificaciones

### Riesgos
| Riesgo | Mitigación |
|---|---|
| El mapa en euros se parece al de alquiler, porque el abono apenas cambia entre zonas | El precio de la hora de viaje es la métrica central (6) y la idea se diferencia de forma explícita (3) |
| Sobrecarga mal calculada por mezclar unidades o por validarla con el mismo parámetro | Renta y alquiler por unidad de consumo, alquiler integrado entre P25 y P75 y validación con la ECV (7.2) |
| Descarga del SERPAVI bloqueada por el proxy | Descarga manual del Excel localizado y documentada; comprobar el último año que trae |
| Dato de contratos por debajo del precio actual | Presentarlo como suelo y, si aparece una fuente legal, la banda con el precio de oferta |
| Huecos en municipios pequeños | Imputación validada y marcada como estimada; «sin dato» si el intervalo no informa |
| Error en el cálculo de bruto a neto | Cuota anual con parámetros citados, nóminas reales y auditoría normativa |
| Sobrecarga infravalorada por incluir a todos los hogares | Corrección por inquilinos (7.2), declarada como supuesto |
| Licencias del Notariado y del CRTM | Confirmarlas por escrito antes de publicar derivados |
| Tiempo en coche sin tráfico | Factor de congestión justificado o limitación declarada |
| Fallo en la demo | App estática sin servidor ni peticiones a terceros; el MCP es independiente |
| Equipo sin frontend ni relato | Lógica en Python, JS mínimo asistido por IA y una persona dedicada al relato |
| Datos personales en el test | Consentimiento informado y anonimato |

### Verificaciones pendientes
- [x] Abrir el Excel del SERPAVI: años, cobertura en Madrid y huecos. Trae los años 2011 a 2024 y tiene los 21 distritos de Madrid. En 2024 tienen dato 157 de las 199 zonas. Las 42 sin dato son municipios pequeños con menos de 10 testigos, y su lista está en el PR #151. En 2024, los testigos de vivienda colectiva de la Comunidad suman 474.935 (fuente: SERPAVI, MIVAU).
- [ ] Probar r5py (transporte público y coche) con 3–5 pares origen-destino.
- [x] Tarifas 2026 por zona en el BOCM y condiciones del Abono Joven (límite de edad): resuelto con BOCM-20251231-2 y la ficha del CRTM (15 a 26 años).
- [ ] Reglas vigentes del Bono Alquiler Joven en la Comunidad. Quedan **abiertas** en parte: las reglas de la ronda «2024» están comprobadas; no se encontró convocatoria con crédito de 2025 o 2026 ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/ayudas-vivienda.md), §2.3).
- [x] Coincidencia entre distritos censales y municipales en Madrid capital. Tienen los mismos 21 códigos y las mismas secciones. Los límites difieren en menos del 4 % del área de cada distrito, porque las cartografías son de fechas distintas: [verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), #68.
- [x] Identificador correcto del IPC de alquiler regional (`1927681` o `1934665`). El factor se calcula con la serie del INE `IPC297196` (Comunidad de Madrid, mensual), y `1934665` se cita como control: [decisión del 2026-11-14](../../../docs/decisiones.md), #67.
- [x] Régimen de tenencia en el Censo de edificios y viviendas de la Comunidad (`19155xx`) y nivel territorial del Censo 2021: `19155xx` no existe; se usa `censo_2021_viviendas_familiares_por_tenencia` (municipio) y el Censo 2021 por sección ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 4a y 4b).
- [x] Nivel territorial de la renta del catálogo regional (`1916304`): solo la Comunidad entera ([verificación](../../../docs/verificaciones/renta-vivienda.md), fila 7).
- [ ] Licencia de los GTFS del CRTM.
- [ ] Enlace, licencia y cobertura de la API del Notariado, por escrito.
- [ ] Dataset de afiliación por lugar de trabajo a nivel municipal, o la matriz origen-destino de la EDM2018.
- [ ] Mes completo del MITMA por distrito, para confirmar o descartar el indicio de la sección 8.
- [x] Cita del valor del tiempo en las guías de evaluación de transporte: la CE (2014, pág. 90) da 25–40 %, no 40–50 % ([verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), fila 7).
- [x] Descuento del abono (50 % en el joven; cifra del normal) y su dependencia de las ayudas estatales: 50 % joven y 40 % normal según el CRTM, con la ayuda del RDL 17/2025 ([referencia](../../../.claude/skills/dm-calculos-normativos/referencia/transporte-tiempo-y-otros.md), §1.1).
- [x] Motivo de los rechazos del Bono Alquiler Joven 2022: resuelto como «no publicado». Las bases excluyen por requisitos o por crédito agotado, sin recuento por motivo ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 1c y 1d).
- [x] Unidad de la renta del ADRH (por hogar o por unidad de consumo) en cada indicador que se use ([verificación](../../../docs/verificaciones/renta-vivienda.md), fila 2a).
- [x] Tasa de sobrecarga de los inquilinos de la ECV para la Comunidad de Madrid: resultado, **no publicada**. Se valida contra la población total de Madrid (9,9 % en 2025) ([verificación](../../../docs/verificaciones/renta-vivienda.md), filas 3a–3c).
- [x] Referencia del *H+T Affordability Index* (CNT): verificada en htaindex.cnt.org ([verificación](../../../docs/verificaciones/movilidad-interoperabilidad.md), fila 6).
- [ ] Modelos aplicables en `pysmartdatamodels/` del repositorio de la organización.
- [ ] Confirmar con la organización los pesos de los criterios, el formato de entrega, la duración de la presentación y la criba de 100 palabras.

## 17. Encaje con los criterios de DataMad

| Criterio | Cómo lo cumple |
|---|---|
| **Uso de la información pública regional** (oficial) | El núcleo usa el catálogo regional: Bono Alquiler Joven, alquiler por código postal, IPC de alquiler, valor catastral de referencia, tenencia de la vivienda, afiliados, EDM2018 y zonificación de transporte. El transporte regional es un componente principal de la cuenta. Lo completan el portal del Ayuntamiento y fuentes nacionales abiertas (INE, MITMA, CRTM, SERPAVI) |
| **Viabilidad** (oficial) | Pipeline reproducible con un comando; web estática que funciona sin servidor; lógica pesada precalculada en Python con pruebas de referencia; piezas de riesgo independientes de la demo |
| **Código abierto** (oficial) | Repositorio MIT, librerías abiertas (DuckDB, r5py, LightGBM, MapLibre), conjunto de datos CC BY 4.0 con DCAT-AP, Smart Data Models y MCP que cualquiera puede instalar |
| **Valor económico, social o medioambiental** (citado por la URJC y la prensa) | Decisión pública concreta (focalizar el Bono, criterio con transporte, fin del descuento del abono), piloto con usuarios antes y después, y validación externa controlada por renta |

## 18. Guion de 5 minutos (borrador)

Combina abrir con un dato y contar el resto con un personaje. Las cifras y los titulares se sustituirán por los que salgan del análisis:
- **0:00** De 51.735 solicitudes del Bono Alquiler Joven en 2022, solo se aceptó el 22 %. Y a quien vive de alquiler, ¿cuánto le queda a fin de mes?
- **0:20** La enfermera de 26 años mete su sueldo en directo y aparece el mapa: euros, horas y a cuánto le pagan cada hora de viaje.
- **1:10** Cambia los días de teletrabajo; después se acaba el descuento del abono. El mapa se mueve.
- **2:00** Titulares: a cuánto paga vivir lejos cada hora de viaje y dónde, y en cuántos municipios no llega un sueldo típico.
- **2:40** Análisis para la Administración: evolución del esfuerzo desde 2015, el Bono frente a la sobrecarga y la simulación del criterio con transporte.
- **3:40** Validación, resultados del piloto con usuarios y limitaciones contadas por iniciativa propia: el alquiler es un suelo, el coche no tiene en cuenta el tráfico, zonas estimadas.
- **4:20** Parte técnica: datos de la Comunidad, Smart Data Models, conjunto de datos abierto, MCP (pregunta en directo desde Claude).
- **4:45** Cierre y URL.

**Entregables previstos:** web publicada, informe de análisis, repositorio reproducible, conjunto de datos, servidor MCP, nota metodológica y presentación. El formato exacto se ajusta cuando la organización lo publique.

---

## Anexo A · Cómo se unificaron las dos versiones

### Qué aportaba cada una
- **Plan de Izan:**
  - viabilidad, con zonas acotadas y matrices precalculadas;
  - rigor: euros y horas separados, alquiler como rango, SERPAVI como suelo y limitaciones declaradas;
  - el Excel del SERPAVI localizado;
  - Smart Data Models y MCP;
  - app estática y privada, sin lógica fiscal en JS;
  - dimensión temporal desde 2015;
  - modo coche, dos sueldos y m² asequibles.
- **Ficha de Yeray:**
  - relato: dato de apertura, personajes y guion;
  - decisiones públicas concretas: focalizar el Bono, criterio con transporte y fin del descuento;
  - cesta básica;
  - más datos regionales y municipales: alquiler por código postal, panel del Ayuntamiento y polos obtenidos de datos;
  - imputación validada y sobrecarga por sección;
  - validación externa y test con usuarios;
  - conjunto de datos con DCAT-AP.

### Qué se resolvió al unir
| Punto | Plan de Izan | Ficha de Yeray | Versión unificada |
|---|---|---|---|
| Término de gastos básicos | No | Cesta básica | Sí (6.4) |
| Valor del tiempo | No se monetiza | 50 % del salario por hora, con deslizador | Horas aparte y deslizador opcional, apagado por defecto (6.5) |
| Zonas sin dato | «Sin dato», sin imputar | Imputación con LightGBM y predicción conformal | Imputación validada; «sin dato» si el intervalo no informa (6.7) |
| Precio de oferta | No | Scraping con agregado | Solo con una fuente legal (6.2, 14) |
| Habitación | m² ÷ personas | Piso ÷ dormitorios + recargo calibrado con oferta | Piso ÷ personas; recargo solo con fuente legal (6.2) |
| Perfiles de hogar | Adultos, hijos, edad, m² y personas | Cuatro perfiles | Los perfiles rellenan los detalles, que se pueden ajustar (5) |
| Entrada del sueldo | Bruto y pagas | Bruto o neto con selector | Las dos opciones (5) |
| IRPF | Cuota anual | Retención 2026 | Cuota anual, explicando la diferencia (6.1) |
| Lugares de trabajo | Hasta dos | Uno, o punto libre en vivo | Hasta dos; punto libre precalculado (5, 6.5) |
| Modo coche | Sí | No | Sí, con la limitación declarada (6.3) |
| Polos de empleo | Afiliación o EDM2018 | MITMA | EDM2018 y MITMA comparados (6.5) |
| Hora de salida | Mediana 7:30–8:30 | Martes a las 8:00 | Mediana de 7:30 a 8:30 de un martes laborable (6.5) |
| Sobrecarga | Rango por municipio | Log-normal por sección con corrección por inquilinos | Log-normal por sección en renta por unidad de consumo, alquiler integrado, corrección con el Censo regional, validación con la ECV y presentada como rango (7.2) |
| Umbrales | 30 % en la app, 40 % en el análisis | 30 % sobrecarga, 40 % grave | 30 % recomendación e indicador complementario; 40 % sobrecarga según Eurostat, con suministros (6.6) |
| Métrica central | Sobrante en euros, horas aparte | Sobrante con el tiempo monetizado | Precio de la hora de viaje, sin monetizar el tiempo (6) |
| Notariado | Solo rentabilidad implícita | Imputación y predicción | Rentabilidad implícita y variable de la imputación; sin predicción (6.7, 7.7) |
| Predicción | Fuera | Alquiler, sobrante y sobrecarga a futuro | Fuera; la parte prospectiva son los escenarios (9, 14) |
| Arquitectura | Estática | Backend FastAPI con respaldo estático | Estática; MCP independiente (13) |
| Asistente | No | Con puerta de calidad | Fuera; IA mediante el MCP (11.3, 14) |
| Smart Data Models | Sí | No | Sí, con propuesta de modelo nuevo (11.1) |
| MCP | Local (stdio) | Público | Local e instalable por cualquiera, leyendo la API estática; instancia alojada solo como extra (11.3) |

### Cambios tras la revisión de `dm-abogado-del-diablo` (14/11/2026)
La revisión dio NO APTO por un problema de enfoque, no de idea. Se corrigió así:
- **Crítico:** el transporte en euros apenas diferencia zonas, así que el mapa del sobrante se parecía al de alquiler. El precio de la hora de viaje pasa a ser la métrica central (6) y se reformula la tesis 1 (8).
- **Sobrecarga:**
  - se usa una sola unidad, la renta por unidad de consumo;
  - el alquiler se integra entre P25 y P75 en lugar de aplicar la mediana;
  - la validación circular con el 60 % de la mediana se sustituye por la ECV (7.2).
- **Análisis sin dato que lo alimente:** necesidad joven = sobrecarga × población joven (7.3); simulación del Bono con casos tipo (7.4).
- **Conformal:** sin «garantiza»; validación en los municipios pequeños y estratificada por tamaño (6.7).
- **Validación externa:** correlación parcial controlando por renta y potencia declarada (10.1).
- **Test con usuarios:** pasa a piloto, con dos métricas fijadas y un plan B (10.3).
- **Menores:**
  - motivo de los rechazos del Bono y descuento del abono normal, por verificar (2);
  - el 40 % de Eurostat es la sobrecarga estándar y cuenta los suministros (6.6);
  - límite de edad del Abono Joven (6.3);
  - el MCP no necesita servidor propio (11.3);
  - las zonas son 178 municipios + 21 distritos (4);
  - se cita el precedente H+T (3).

### Registro de decisiones de origen
- **Plan de Izan:** seis fases (enfoque, datos, modelo de cálculo, análisis, herramienta y presentación), las cinco primeras cerradas el 11/11/2026. Todas sus decisiones están en las secciones 3 a 13, salvo las que cambian según la tabla anterior.
- **Ficha de Yeray:** diez rondas de entrevista. Su registro completo está en el anexo de la [ficha](../yeray/ficha-salario-que-sobra.md). Todas las respuestas están incorporadas aquí, salvo las que cambian según la tabla anterior:
  - el recorte de alcance que se rechazó en la ronda 5 se respeta: el alcance es completo;
  - el scraping aceptado en la ronda 1 queda fuera por motivos legales;
  - la capa predictiva de las rondas 1 y 4 queda fuera por los datos, no por el plazo;
  - el backend que atraía en la ronda 5 se sustituye por precálculo.
