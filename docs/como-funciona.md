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

Parla le deja más dinero que Getafe, pero a cambio de unas 14 horas más de viaje al mes: unos 12,7 € por cada hora extra, la cifra que pinta el mapa al abrir. Kuanto pone las dos cifras juntas para que cada cual decida qué le compensa. La web también da una horquilla del sobrante, porque el alquiler de una zona no es un precio único.

## Por qué la cuenta se hace en tu navegador

Los datos de las 199 zonas ya están calculados y publicados como ficheros abiertos. La web los descarga y hace la última resta con lo que escribes, en tu dispositivo. Tu sueldo no se envía a ningún sitio, y una vez abierta la página funciona sin conexión.

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
