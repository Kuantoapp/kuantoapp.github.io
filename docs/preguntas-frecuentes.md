# Preguntas frecuentes

Las dudas más habituales sobre Kuanto, con una respuesta corta y dónde ampliarla.

## ¿Mi sueldo sale de mi ordenador?

No. La web descarga los datos de las zonas y hace la cuenta en tu navegador, sin enviar lo que escribes a ningún sitio. No hay registro, ni analítica, ni recursos de otras webs, y una vez abierta funciona sin conexión ([Hecho para que lo compruebes](https://yeraybc.github.io/DataMad-hackaton-2026/saber-mas.html#titulo-confianza)).

## ¿De qué año son los datos?

Cada pieza tiene su fecha. Las normas y las tarifas son las de 2026. El alquiler declarado llega hasta 2024 y se lleva a octubre de 2026 con el IPC. La tabla completa está en [Datos y fuentes](datos-y-fuentes.md).

## ¿Por qué algunas cifras dicen «estimado»?

Porque no son un dato publicado tal cual, sino el resultado de un modelo o de un supuesto, como llevar un alquiler de 2024 a hoy. Kuanto lo avisa para que sepas cuánto fiarte de cada cifra ([Qué significa «estimado»](como-funciona.md#qué-significa-estimado)).

## ¿Por qué mi zona sale en gris?

Porque no hay alquiler publicado para ella o no hay ruta en transporte público en el tiempo máximo que se calcula. En vez de inventar una cifra, Kuanto la deja sin dato. «Sin ruta» no siempre quiere decir que no haya transporte: a veces falta el horario de una línea en los datos del Consorcio. En el mapa del precio de la hora, el que se ve al abrir, una zona también sale en gris claro si tardas casi lo mismo que desde la zona de referencia (menos de 5 horas al mes de diferencia), y la referencia va en blanco ([Límites](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-limites)).

## El alquiler de mi zona me parece bajo. ¿Está mal?

Probablemente es más bajo que lo que verías en un portal de anuncios. Kuanto usa contratos declarados a Hacienda, no anuncios, y aunque los ajusta a contrato nuevo, conviene leerlo como un suelo. Por eso la web da también una horquilla entre un alquiler barato y uno caro de la zona ([Límites](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-limites)).

## ¿Por qué mi neto no coincide con mi nómina?

Kuanto da el neto del año entre 12, aunque cobres en 14 pagas, y usa la cuota anual del IRPF, no la retención de la nómina. Tampoco incluye deducciones personales como la de alquiler de Madrid para menores de 40 años. El total del año debería ser parecido; la nómina de cada mes, no ([Por qué la cuota anual y no la retención](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-cuota)).

## ¿Puedo reutilizar los datos?

Sí. Los ficheros que publica Kuanto son abiertos (CC BY 4.0, o ODbL 1.0 los que derivan de OpenStreetMap). Cómo citarlos y qué cita exige cada fuente está en [Datos abiertos de Kuanto](../app/datos/LEEME.md).

## ¿Cómo sé que las cifras son correctas?

Cada cifra de la web dice de dónde sale, la cuota del IRPF coincide con los ejemplos del manual de Renta de la Agencia Tributaria (la cotización y la deducción por SMI de 2026 aún no se han contrastado), y las afirmaciones sobre fuentes y normas se han comprobado con el publicador original. Lo que no se ha podido contrastar también está escrito ([Validación](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-validacion), [verificaciones](verificaciones/)).

## ¿Puedo reproducirlo todo?

Sí. El código es abierto (MIT) y un comando regenera los datos de la web desde las descargas originales, después de calcular una vez los tiempos de viaje ([Reproducir Kuanto](reproducir.md)).

## ¿Puedo preguntarle a un asistente de IA?

Sí, con el servidor MCP de Kuanto, que da a un asistente las mismas cifras que la web, con sus fuentes y supuestos ([Asistente MCP](reproducir.md#5-asistente-mcp)).

## He encontrado un error. ¿Dónde aviso?

En las [issues del repositorio](https://github.com/yeraybc/DataMad-hackaton-2026/issues).
