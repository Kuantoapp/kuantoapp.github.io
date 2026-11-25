# Cómo funciona Kuanto

Qué cuenta hace Kuanto, con qué datos y qué no sabe, explicado sin tecnicismos. Es para cualquiera que quiera entender las cifras antes de fiarse de ellas. El detalle completo, con cada fórmula y cada supuesto, está en la [nota metodológica](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html).

## La pregunta

¿Cuánto dinero te queda a final de mes si vives en un sitio u otro de la Comunidad de Madrid? Para responderla no basta con el alquiler: un piso más barato lejos del trabajo puede comerse la diferencia en transporte, y además cuesta horas.

## La cuenta

Kuanto divide la Comunidad en 199 zonas: los 178 municipios distintos de la capital y los 21 distritos de Madrid (fuente: [`zonas.geojson`](../app/datos/LEEME.md#zonasgeojson)). Para cada zona hace esta resta, en euros al mes:

| Pieza | Qué es | De dónde sale |
|---|---|---|
| Sueldo neto | Lo que queda del bruto tras las cotizaciones y el IRPF de 2026 | Normas del BOE y de la Comunidad de Madrid |
| − Alquiler | Precio del metro cuadrado en la zona por los metros del hogar, llevado a hoy | Alquileres declarados a Hacienda (SERPAVI) y el IPC del INE |
| − Transporte | El abono o título más barato para ir al trabajo los días que vas | Tarifas oficiales del Consorcio de Transportes (BOCM) |
| − Cesta básica | Comida, luz, gas, agua, teléfono e Internet de un hogar como el tuyo | Encuesta de Presupuestos Familiares del INE |
| **= Lo que sobra** | | |

Al lado da las horas al mes que pasas yendo y volviendo del trabajo, calculadas con los horarios reales del transporte público y el mapa de calles de OpenStreetMap. Qué fuente aporta cada pieza, de qué año y con qué licencia está en [Datos y fuentes](datos-y-fuentes.md).

## Un ejemplo

Una persona de 30 años que vive sola, gana 24.000 € brutos al año y trabaja en Getafe cinco días a la semana en transporte público. Su neto es de unos 1.617 € al mes y su cesta básica, de unos 410 €. Lo que le sobra cambia según dónde viva:

| Si vive en… | Le sobra al mes | Horas de viaje al mes |
|---|---|---|
| Getafe | unos 291 € | unas 12 |
| Parla | unos 467 € | unas 26 |
| Madrid, distrito Centro | unos −378 € (no le llega) | unas 26 |

Fuente: cálculo de Kuanto (`mesobra.calculo`) sobre los ficheros de `app/datos/` del 2026-11-24, con los valores por defecto de la web (piso de 69 m², tarifas de 2026 con descuento, alquiler de un contrato nuevo); estimado, porque el neto se calcula con la normativa, el alquiler se actualiza con el IPC y se ajusta a contrato nuevo, y las horas salen de un simulador. Con lo que pagan los inquilinos actuales sobrarían unos 435 €, 574 € y −127 €.

Parla le deja más dinero que Getafe, pero a cambio de más horas de viaje. Kuanto pone las dos cifras juntas para que cada cual decida qué le compensa. La web también da una horquilla del sobrante, porque el alquiler de una zona no es un precio único.

### Qué quiere decir «12,7 € por cada hora extra»

Es la cifra que pinta el mapa al abrir, y responde a una pregunta: si me voy a vivir más lejos, ¿lo que ahorro compensa el tiempo que pierdo?

Kuanto compara cada zona con una de referencia: por defecto, la zona desde la que menos tardas en llegar al trabajo. En el ejemplo es Getafe, con unas 12 horas de viaje al mes. Viviendo en Parla:

- Viajas unas 13,9 horas más al mes (25,9 − 12,0).
- Te sobran unos 176 € más al mes (467 − 291).
- Cada hora extra de viaje te deja, por tanto, unos 176 ÷ 13,9 ≈ 12,7 € (estimado; fuente: el ejemplo de arriba).

Para saber si eso es mucho o poco, compáralo con lo que ganas por hora de trabajo. Esta persona cobra unos 10,7 € netos por hora (1.617 € al mes entre 40 horas a la semana durante las 3,78 semanas laborables del mes; estimado, que es lo que la web muestra en la ficha). Cada hora que pasa en el tren hacia Parla le rinde más que una hora trabajando, así que el traslado le sale a cuenta en dinero. Si la cifra fuera de 3 €, estaría cambiando su tiempo muy barato.

Cuando la cifra es negativa, la zona es peor por los dos lados: viajas más y te sobra menos. Es lo que pasa en el distrito Centro: tarda unas 14 horas más que desde Getafe y le sobran unos 669 € menos al mes. Si una zona tarda casi lo mismo que la de referencia (menos de 5 horas de diferencia al mes), no se calcula y sale en gris claro.

Lo que aporta: el alquiler solo, o el sobrante solo, esconden el tiempo. Esta cifra pone el dinero y las horas en la misma medida, euros por hora, y deja comparar zonas que de otra forma no se pueden comparar. La zona de referencia se puede cambiar en el formulario, por ejemplo por donde vives ahora.

### Qué es el ajuste a contrato nuevo

El alquiler que publica el SERPAVI es lo que pagan todos los inquilinos que declaran su alquiler a Hacienda, también quienes firmaron hace años y pagan menos que el precio de hoy. Si alguien busca piso ahora, firma un contrato nuevo, y eso suele costar más.

Para acercarse a ese precio, Kuanto usa una estadística de la Agencia Tributaria que compara, en cada municipio, lo que se paga por metro cuadrado en los contratos firmados en 2024 con lo que se paga en todos los contratos. Si en un municipio los nuevos son un 19 % más caros, el alquiler de esa zona se multiplica por 1,19. Es lo que pasa en Getafe: en el ejemplo, lo que paga un inquilino de siempre ronda los 753 € al mes y un contrato nuevo, los 896 € (estimado; fuente: `alquiler.json`, Agencia Tributaria).

Para los distritos de Madrid se usan sus códigos postales. Los municipios pequeños, que la estadística no detalla, toman un valor típico de los municipios medianos ([registro de decisiones](decisiones.md), 2026-11-20).

Aun así, la cifra es un suelo y no el precio de un anuncio: sale de contratos declarados, y se lleva a hoy con el IPC de los alquileres en vigor, que sube menos que el de los nuevos ([Límites](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-limites)). En la ficha de cada zona, la cifra principal es la del contrato nuevo, y la de los inquilinos de siempre sale como referencia.

## Por qué la cuenta se hace en tu navegador

Para calcular lo que te sobra, Kuanto necesita datos que dicen mucho de ti: cuánto ganas, dónde trabajas, con quién vives y cuántos hijos tienes. Por eso Kuanto nunca los recibe.

Los datos de las 199 zonas ya están calculados y publicados como ficheros abiertos. La web los descarga y hace la última resta en tu dispositivo, con lo que escribes. Lo que escribes no se envía a ningún servidor ni se guarda en ningún sitio. No hay registro, ni cuentas, ni analítica, ni recursos de otras webs, y una vez abierta la página funciona sin conexión ([Hecho para que lo compruebes](https://yeraybc.github.io/DataMad-hackaton-2026/saber-mas.html#titulo-confianza)).

La alternativa habitual es preguntar a un chat de inteligencia artificial o rellenar una calculadora en una web. En ese caso, tu sueldo y tu situación familiar viajan a los servidores de otra empresa. Según el servicio y su configuración, pueden quedarse guardados en tu historial, revisarse o usarse para entrenar modelos, y dejas de controlar dónde acaban. Con Kuanto ese riesgo no existe, porque no hay ningún servidor que los reciba. Además, el código es abierto: cualquiera puede comprobar que es así.

Si usas el asistente MCP de Kuanto, la cuenta también se hace en tu equipo. Pero la pregunta que le escribes la lee el asistente de IA que uses, con sus propias condiciones de privacidad.

## Qué significa «estimado»

Algunas cifras no son un dato publicado tal cual, sino el resultado de un modelo o de un supuesto: el alquiler llevado a 2026 con el IPC, el ajuste a contrato nuevo, la cesta por tamaño de hogar o parte de los tiempos de viaje. Esas cifras llevan la marca «estimado». Lo que no se sabe no se inventa: las zonas sin alquiler publicado salen en gris.

## Lo que Kuanto no sabe

- El alquiler sale de contratos declarados, no de anuncios, así que es un suelo: firmar hoy suele costar más.
- El neto supone tributación individual y no incluye deducciones como la de alquiler de Madrid para menores de 40 años, así que en esos casos el neto real puede ser mayor.
- Los tiempos de viaje salen de un simulador. No los leas al minuto.

La lista completa, con cifras y fuentes, está en [Supuestos](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-supuestos) y [Límites](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-limites) de la nota metodológica.

## Para saber más

- [Cómo funciona Kuanto](https://yeraybc.github.io/DataMad-hackaton-2026/saber-mas.html), en la web: los cuatro pasos de los datos al mapa y cómo leer los colores.
- [Informe de análisis](https://yeraybc.github.io/DataMad-hackaton-2026/informe.html): lo que dicen los datos sobre alquiler, sueldos y ayudas en la Comunidad.
- [Glosario](glosario.md): qué significa cada término.
