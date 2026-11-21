# Gráficos

Contenido: forma según el dato · jerarquía · construcción · color · honestidad · accesibilidad · el mapa en la página.

Para gráficos de la web y de las diapositivas. En los mapas, la clasificación, la paleta y la proyección las decide `dm-cartografia`; su accesibilidad y su encaje en la página, esta referencia.

## Forma según el dato

| El dato es | La forma es |
|---|---|
| Un valor | Una cifra grande con su comparación y su fuente, nunca un gráfico de una barra |
| De dos a cinco valores comparados | Barras horizontales o una fila de cifras |
| Una serie en el tiempo | Una línea |
| Más de unas siete categorías | Una tabla, o barras ordenadas; más colores no es la respuesta |
| Partes de un todo | Una barra apilada horizontal; nunca tarta, rosco ni velocímetro |
| Un objetivo | Una barra de progreso |
| Dos medidas de unidades distintas | Dos gráficos pequeños, nunca dos ejes |

## Jerarquía

- Un gráfico principal por pantalla, claramente el más grande (al menos dos tercios del ancho del contenido). Lo demás que muestre datos es más pequeño y de otro tipo: una lista ordenada con barras finas o una tabla corta.
- Las tarjetas de cifra son números: etiqueta, cifra y cambio con su referencia. Sin minigráficos, iconos ni barritas de relleno.
- Anchos con ritmo: tres o cuatro cifras compactas encima de un gráfico ancho, o un gráfico ancho junto a una lista estrecha. Nunca una fila de tarjetas iguales con el mismo gráfico.

## Construcción

SVG o CSS escrito para el dato; una librería solo si ya está en el proyecto (`docs/decisiones.md`).

- **Barras:** como mucho 24 px de grueso, 2 a 4 px entre ellas, base en cero siempre, redondeo solo en el extremo del dato y de 2 px como mucho.
- **Líneas:** trazo de 2 px; marcadores solo en los puntos anotados.
- **Rejilla:** 1 px continua del color de línea fina, de 3 a 5 líneas horizontales; el eje es la primera línea de la rejilla, no un trazo más grueso.
- Sin sombras, 3D ni degradados en las marcas.
- Etiquetas de eje y valores en el color de texto apagado, con cifras tabulares y en formato español. Días y meses con mayúscula solo inicial.

## Color

- Una serie: el acento.
- Varias: lo que importa (el año actual, la zona elegida, la línea que se sigue) lleva el acento y el resto pasos neutros de la rampa. Varios tonos solo si hay que distinguir series de verdad, y aun así uno manda.
- Una paleta categórica solo con colores de la dirección, asignados en un orden fijo, nunca rotados.
- El texto nunca lleva el color del dato: la serie se identifica con una muestra junto a su etiqueta.

## Honestidad

- Datos reales con su fuente en el pie del gráfico y «estimado» si salen de un modelo; donde falta un dato, se dice que falta, no se rellena.
- Barras desde cero. Si los datos viven en una banda estrecha y se recorta el eje, el gráfico lo anota («el eje empieza en 90 %»).
- Los intervalos o la incertidumbre que tiene el dato se dibujan (banda, bigote) en vez de esconderse.

## Accesibilidad

- Nada solo por color: etiquetas directas en las series, formas o posiciones distintas.
- El gráfico tiene un título que dice la conclusión y una alternativa en texto o tabla (`<figcaption>`, `<table>` oculta visualmente o un resumen) con las mismas cifras.
- Los globos de ayuda se abren también con el teclado y el toque, no solo al pasar el ratón.
- Contraste de 3:1 para las marcas frente al fondo y entre series contiguas. Las coropletas quedan exentas en la clase más clara (ninguna paleta secuencial lo cumple): lo compensan el borde de las zonas y la ficha en texto.

## El mapa en la página

- La información de una zona se abre con el teclado y con el toque, no solo al pasar el ratón: una ficha o un panel con el nombre, las cifras y su fuente, que se puede leer con lector de pantalla.
- Hay una alternativa al mapa: una lista o tabla de zonas con las mismas cifras, que se puede buscar u ordenar.
- La leyenda dice los rangos en texto, no solo con color, y no tapa el mapa ni los controles a 390 px.
- Los controles del mapa (zoom, capas) tienen nombre accesible y objetivos de 44 px.
- Si el mapa base necesita red, la página sigue siendo útil sin él (ver `estados.md`).

Adaptado de `Nutlope/hallmark` (MIT, «Data viz»), `heydamir/unslop` de Damir Sokolovsky (CC BY 4.0, pasada de detalles) y `nextlevelbuilder/ui-ux-pro-max-skill` (MIT, gráficos y datos); traducido, reescrito y modificado.

Origen, autores y licencias: [licencias.md](licencias.md).
