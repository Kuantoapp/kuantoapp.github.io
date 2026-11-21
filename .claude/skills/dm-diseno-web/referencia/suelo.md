# Suelo

Contenido: tokens · accesibilidad · móvil · movimiento · honestidad · sistema · prohibiciones · comprobación.

Reglas que valen para toda pantalla y toda diapositiva del proyecto. No se negocian por gusto: solo las cambia una decisión escrita en `docs/decisiones.md`. Cada una se comprueba sobre el resultado, no se da por supuesta.

## Tokens

1. Todo color, familia tipográfica, radio y paso de espaciado sale de una variable declarada en `:root` (o en un bloque de tema). Ningún literal de color ni `font-family` fuera de ese bloque.
2. Un color significa una cosa en toda la web: el acento marca la acción principal, la selección o la cifra que importa; los colores semánticos (bien, mal, aviso) solo llevan ese significado.

## Accesibilidad

3. Contraste calculado con los valores reales: texto de menos de 24 px (o de menos de 18,7 px en negrita) ≥ 4,5:1; a partir de ahí, ≥ 3:1 (WCAG: 18 pt, o 14 pt en negrita); bordes de controles, iconos con significado y anillos de foco ≥ 3:1. El texto secundario sobre un fondo de color se tiñe de ese color, no se pone gris.
4. Todo lo interactivo tiene `:focus-visible` que aparece al instante, y el teclado llega a todo en el orden de lectura. Elementos nativos (`button`, `a`, `select`, `input`) antes que `div` con eventos.
5. Nada se comunica solo con color: una serie, un estado o un error lleva también texto, forma o posición.
6. Cada control tiene nombre accesible (un botón solo con icono lleva `aria-label`), cada imagen con contenido lleva `alt` y las decorativas `alt=""`. Encabezados de un nivel en uno, `lang="es"` en `<html>`.

## Móvil

7. Sin desplazamiento horizontal a 320 px: `overflow-x: clip` en `html` y `body` (nunca `hidden` ni `100vw`), pistas de rejilla con imágenes en `minmax(0, 1fr)` y titulares con `overflow-wrap: break-word; min-width: 0`.
8. Objetivos táctiles de 44 × 44 px como mínimo fuera del texto corrido (WCAG pone 24 como mínimo absoluto), con al menos 8 px entre ellos.
9. Nunca se desactiva el zoom (`user-scalable=no` o `maximum-scale=1`): eso es accesibilidad. Cuerpo de texto de 16 px o más; en paneles densos del modo operar, 14 px como mínimo (no es un umbral de WCAG, es legibilidad en el móvil).
10. El contenedor tiene un ancho máximo y se centra: en pantallas grandes crecen los márgenes, no la medida de línea (65 a 75 caracteres en prosa).

## Movimiento

11. Nunca `transition: all`; nunca se animan `width`, `height`, `top`, `left` ni márgenes. Se transicionan `transform`, `opacity`, color, fondo y borde, nombrados.
12. Toda animación tiene su versión con `prefers-reduced-motion: reduce`, que conserva el cambio de estado sin el desplazamiento. Ningún contenido depende de una animación para verse.
13. Nada se repite en bucle si no está vivo de verdad; nada se mueve al desplazar la página.

## Honestidad

14. Ninguna cifra, testimonio, logotipo, recuento de usuarios ni caso de uso inventado. Cada cifra visible lleva su nota `[^id]` o «fuente: …» y «estimado» si sale de un modelo (regla de `AGENTS.md`; la comprueba `cifras_con_fuente.py`).
15. Los datos de ejemplo de una captura o maqueta son los reales de la app, no números redondos plausibles.
16. Un eje que no empieza en cero lo dice en el propio gráfico.

## Sistema

17. Un estilo de botón principal, un ancho de contenedor, un radio por nivel de anidado (interior = exterior − relleno, nunca menos de 4 px), un estilo de enlace y como mucho dos familias tipográficas.
18. Cifras con `font-variant-numeric: tabular-nums` y un solo formato en toda la pantalla: el que ya use la app (normalmente `Intl.NumberFormat('es-ES')`: coma decimal, punto de miles desde cinco cifras y el símbolo detrás con espacio, así que da `1250,00 €` y `12.500 €`). No se mezcla otro criterio en una sola cifra.
19. Cada control tiene sus estados: reposo, encima, foco, pulsado, desactivado, cargando y error.

## Prohibiciones

20. Sin antetítulo (la etiqueta pequeña sobre un titular) ni etiquetas en mayúsculas con espaciado ancho: etiquetas, cabeceras de tabla y navegación en la fuente del texto, un paso más pequeñas y con mayúscula solo inicial.
21. Sin degradado de violeta a azul (ni de un tono a otro en superficies), texto en degradado, brillos o sombras de color, manchas de color tras el contenido, ni cristal o desenfoque decorativo.
22. Sin tarjeta dentro de tarjeta, sin barra de color en un solo lado de una caja redondeada, sin emoji como icono y sin ventanas de navegador o de sistema dibujadas a mano.
23. Sin cadenas de metadatos unidas con puntos medios, flechas pegadas al texto de un enlace ni puntos de estado decorativos.
24. Sin una palabra en cursiva dentro de un titular en redonda.

## Comprobación

Sobre el render, en una sola tanda por ronda: anchos 390 y 1440, y 320 si hay tablas o mapas; recorrido completo con el teclado; contraste de cada par texto y fondo distinto; modo de movimiento reducido. Lo que no se pudo comprobar se dice como no comprobado.

Adaptado de `Nutlope/hallmark` (MIT, «The Floor»), `pbakaus/impeccable` (Apache-2.0, «craft floor»), `heydamir/unslop` de Damir Sokolovsky (CC BY 4.0) y `nextlevelbuilder/ui-ux-pro-max-skill` (MIT); traducido, reescrito y modificado.

Origen, autores y licencias: [licencias.md](licencias.md).
