# Preguntas frecuentes

Las dudas más habituales sobre Kuanto, con una respuesta corta y dónde ampliarla.

## ¿Mi sueldo sale de mi ordenador?

No. La web descarga los datos de las zonas y hace la cuenta en tu navegador, sin enviar lo que escribes a ningún sitio. No hay registro, ni analítica, ni recursos de otras webs, y una vez abierta funciona sin conexión. Lo que escribes solo queda en tu navegador, en la dirección de la página y en la pestaña mientras la tengas abierta: si compartes el enlace, compartes también tus datos ([por qué importa](como-funciona.md#por-qué-la-cuenta-se-hace-en-tu-navegador), [Hecho para que lo compruebes](https://kuantoapp.github.io/saber-mas.html#titulo-confianza)).

## ¿De qué año son los datos?

Cada pieza tiene su fecha. Las normas y las tarifas son las de 2026. El alquiler declarado llega hasta 2024 y se lleva a octubre de 2026 con el IPC. La tabla completa está en [Datos y fuentes](datos-y-fuentes.md).

## ¿Por qué algunas cifras dicen «estimado»?

Porque no son un dato publicado tal cual, sino el resultado de un modelo o de un supuesto, como llevar un alquiler de 2024 a hoy. Kuanto lo avisa para que sepas cuánto fiarte de cada cifra ([Qué significa «estimado»](como-funciona.md#qué-significa-estimado)).

## ¿Por qué mi zona sale en gris?

Porque no hay alquiler publicado para ella o no hay ruta en transporte público en menos de 120 minutos, el tiempo máximo que se calcula. En vez de inventar una cifra, Kuanto la deja sin dato. «Sin ruta» no siempre quiere decir que no haya transporte: a veces falta el horario de una línea en los datos del Consorcio. En el mapa del precio de la hora, el que se ve al abrir, una zona también sale en gris claro si tardas casi lo mismo que desde la zona de referencia (menos de 5 horas al mes de diferencia), y la referencia va en blanco ([Límites](https://kuantoapp.github.io/metodologia.html#titulo-limites), [cómo leer los colores](https://kuantoapp.github.io/saber-mas.html#titulo-colores)).

## El alquiler de mi zona me parece bajo. ¿Está mal?

Probablemente es más bajo que lo que verías en un portal de anuncios. Kuanto usa contratos declarados a Hacienda, no anuncios, y aunque los ajusta a contrato nuevo ([qué es ese ajuste](como-funciona.md#qué-es-el-ajuste-a-contrato-nuevo)), conviene leerlo como un suelo. Por eso la web da también una horquilla entre un alquiler barato y uno caro de la zona ([Límites](https://kuantoapp.github.io/metodologia.html#titulo-limites)).

Los contratos declarados tienen una ventaja: son lo que la gente paga de verdad, en todas las zonas y con una fuente oficial y abierta. Su límite es que van por detrás del mercado. Nos gustaría contar con una muestra mayor de anuncios de alquiler, que reflejan el precio al que se ofrece un piso hoy, y estudiaremos incorporarla si encontramos una fuente que se pueda reutilizar con una licencia abierta y que cubra toda la Comunidad.

## ¿Por qué me sobra más de lo que me queda en realidad?

Porque «lo que sobra» no es lo que ahorras: es el margen que te queda para todo lo que Kuanto no cuenta. La cuenta solo resta tres gastos (el alquiler, el transporte al trabajo y una cesta básica), y deja fuera muchos otros:

- La cesta básica es comida, luz, gas, agua, teléfono e Internet, y nada más. No incluye ropa, ocio, salud, seguros, gastos de la comunidad ni deudas. Tampoco las comidas fuera de casa, que en Madrid suman de media 1.852 € al año por unidad de consumo (fuente: INE, EPF de 2025, vía el catálogo de la Comunidad de Madrid; `hogares.json`).
- Es el gasto medio de los hogares de Madrid, no el tuyo. Si tu calefacción gasta más (en la sierra, por ejemplo) o comes fuera a diario, tu gasto real será mayor.
- El transporte solo cuenta los viajes al trabajo, salvo que añadas viajes de ocio en el formulario.
- El alquiler es un suelo (ver la pregunta anterior). Si firmas hoy, probablemente pagues más.
- El neto supone tributación individual, contrato indefinido y menos de 65 años. Si tu situación es otra, tu neto real puede ser distinto ([cómo se calcula](https://kuantoapp.github.io/saber-mas.html#titulo-piezas)).

Sirve para comparar zonas entre sí con la misma vara, no para hacer tu presupuesto al euro ([Supuestos](https://kuantoapp.github.io/metodologia.html#titulo-supuestos)).

## ¿Por qué mi neto no coincide con mi nómina?

Kuanto da el neto del año entre 12, aunque cobres en 14 pagas, y usa la cuota anual del IRPF, no la retención de la nómina. Tampoco resta deducciones como la de familia numerosa o la de alquiler de Madrid para menores de 40 años. El total del año debería ser parecido; la nómina de cada mes, no ([Por qué la cuota anual y no la retención](https://kuantoapp.github.io/metodologia.html#titulo-cuota)).

## ¿Me dice Kuanto dónde tengo que vivir?

No. Te dice cuánto dinero te queda y cuánto tiempo pasas viajando en cada zona, con las mismas reglas para todas, para que compares con datos. Lo demás lo decides tú: la familia y los amigos cerca, los colegios, el tipo de barrio o lo que te guste. Kuanto quita incertidumbre a una parte de la decisión; no la toma por ti ([Cómo funciona Kuanto](como-funciona.md)).

## ¿Por qué no sale mi barrio, solo mi municipio o mi distrito?

Porque es el nivel al que los datos son fiables para todas las piezas a la vez. Kuanto usa el alquiler por municipio y por distrito. También se publica por sección censal, pero en trozos tan pequeños hay tan pocos alquileres declarados que la cifra dependería de unos pocos pisos. Ya con zonas enteras, 39 de las 199 tienen menos de 70 alquileres declarados y se marcan como imprecisas (fuente: [Límites](https://kuantoapp.github.io/metodologia.html#titulo-limites)). Dentro de tu zona, la horquilla te da una idea de cuánto varía el precio de un piso a otro.

## ¿Sirve si vivo en pareja, con hijos o en un piso compartido?

Sí. El formulario tiene cuatro perfiles: persona sola, piso compartido, pareja con dos sueldos y familia monoparental. Puedes indicar hasta 5 hijos, si sois familia numerosa, los metros del piso y cuántos hogares pagáis el alquiler. En pareja, cada sueldo lleva su propio lugar de trabajo, y Kuanto suma los dos viajes. La cesta y el transporte se ajustan a cada caso, por ejemplo con el Abono Joven de los hijos de 15 a 25 años ([Supuestos](https://kuantoapp.github.io/metodologia.html#titulo-supuestos)).

## ¿Y si teletrabajo algunos días o voy en coche?

Puedes elegir de 1 a 5 días presenciales a la semana: con menos días, el viaje cuenta menos horas, y el título de transporte más barato puede cambiar, por ejemplo de un abono mensual a bonos de 10 viajes. También puedes elegir el coche. Entonces se cuentan 0,26 € por kilómetro, el coste que Hacienda acepta sin tributar, sin aparcamiento, peajes ni atascos, así que el coste real y el tiempo en hora punta serán mayores (fuente: [Qué se calcula](https://kuantoapp.github.io/metodologia.html#titulo-calculo), Orden HFP/792/2023).

## ¿Qué pasa si se acaba el descuento del abono?

Los precios del transporte de 2026 llevan un descuento (ayuda del Estado del RDL 17/2025 más la aportación de la Comunidad y los ayuntamientos) que solo está aprobado para ese año. En «Otros escenarios» del formulario puedes ver la cuenta con el precio oficial sin descuento. En el ejemplo de [Cómo funciona](como-funciona.md#un-ejemplo), a quien vive en Parla le sobrarían unos 19 € menos al mes (estimado; fuente: cálculo de Kuanto sobre `tarifas.json`). El [informe de análisis](https://kuantoapp.github.io/informe.html#titulo-descuento) estudia qué pasaría en toda la Comunidad.

## ¿Puedo reutilizar los datos?

Sí. Los ficheros que publica Kuanto son abiertos (CC BY 4.0, o ODbL 1.0 los que derivan de OpenStreetMap). Cómo citarlos y qué cita exige cada fuente está en [Datos abiertos de Kuanto](../app/datos/LEEME.md).

## ¿Cómo sé que las cifras son correctas?

Cada cifra de la web dice de dónde sale, la cuota del IRPF coincide con los ejemplos del manual de Renta de la Agencia Tributaria (la cotización y la deducción por SMI de 2026 aún no se han contrastado), y las afirmaciones sobre fuentes y normas se han comprobado con el publicador original. Lo que no se ha podido contrastar también está escrito ([Validación](https://kuantoapp.github.io/metodologia.html#titulo-validacion), [verificaciones](verificaciones/)).

## ¿Puedo reproducirlo todo?

Sí. El código es abierto (MIT) y un comando regenera los datos de la web desde las descargas originales, después de calcular una vez los tiempos de viaje ([Reproducir Kuanto](reproducir.md)).

## ¿Puedo preguntarle a un asistente de IA?

Sí. Orienta bien sobre dónde mirar, pero en [nuestra prueba](kuanto-frente-a-ia.md) falló en el neto y en alguna zona tarifaria, y no se podía saber de dónde salía cada importe. Con el servidor MCP de Kuanto el asistente recibe las mismas cifras que la web, con sus fuentes y supuestos ([Asistente MCP](reproducir.md#5-asistente-mcp)). Ten en cuenta que lo que escribas en un asistente en la nube, sueldo incluido, llega a su proveedor.

## He encontrado un error. ¿Dónde aviso?

En las [issues del repositorio](https://github.com/Kuantoapp/kuantoapp.github.io/issues).
