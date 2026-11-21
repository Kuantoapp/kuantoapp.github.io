# Estados y casos

Contenido: formularios · carga · vacíos · errores · modo oscuro · demo sin red · impresión.

Para cuando la pantalla los necesite: no todas los tienen. Si aparecen, se diseñan con el mismo sistema, no se dejan con el aspecto por defecto.

## Formularios

- Etiqueta visible encima de cada campo; el marcador de posición no es una etiqueta.
- Opciones antes que escribir: un `select`, botones de opción o un deslizador con su valor escrito cuando el conjunto es pequeño.
- Validación al salir del campo, con el error debajo de su campo, que diga el problema y cómo arreglarlo («Escribe un valor entre <mínimo> y <máximo>»).
- `inputmode` y `autocomplete` correctos (cifras con `inputmode="decimal"`); se acepta coma decimal.
- Texto de ayuda corto bajo el campo cuando hace falta; divulgación progresiva antes que todo de golpe.

## Carga

- Algo aparece al momento; si tarda, un esqueleto con la forma del contenido, no un indicador giratorio en mitad de la página.
- El espacio se reserva para que nada salte al llegar (sin desplazamiento acumulado del diseño).
- Si hay progreso medible, se muestra.

## Vacíos

Un estado vacío enseña qué hacer: qué falta y la acción para empezar, en una frase. Nunca «No hay nada aquí».

## Errores

- En la interfaz, no en ventanas emergentes del navegador (`alert`).
- Dicen qué pasó y cómo salir, con la voz de la herramienta y sin disculpas.
- Una zona sin dato es un estado, no un error: se dice que no hay dato y por qué, con la misma regla de fuente.

## Modo oscuro

- Solo si se decide; si existe, sigue `prefers-color-scheme` y se comprueba el contraste de cada par otra vez.
- Las marcas de los gráficos se recalculan para el fondo oscuro (menos saturación, más luz); no se invierten.
- La profundidad sale de pasos de superficie, no de sombras.

## Demo sin red

- Fuentes, iconos, librerías y datos servidos desde el repo; nada de CDN en la demo.
- Si algo necesita red (teselas de un mapa base), tiene un plan B visible que no rompe la página.

## Impresión

`@media print` deja el informe legible en papel: sin navegación, fondos claros, enlaces con su URL y saltos de página que no parten una tabla.

Adaptado de `pbakaus/impeccable` (Apache-2.0, «Operate mode» y «harden») y `nextlevelbuilder/ui-ux-pro-max-skill` (MIT, formularios y respuesta); traducido, reescrito y modificado.

Origen, autores y licencias: [licencias.md](licencias.md).
