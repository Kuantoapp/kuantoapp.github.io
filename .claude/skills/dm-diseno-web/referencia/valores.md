# Valores de partida

Contenido: espaciado · rampas neutras · acento · tipografía · radio · iconos · profundidad · movimiento · por modo.

Puntos de partida, no un estilo de la casa: si el proyecto ya tiene un sistema bueno se conservan sus valores, y la dirección puede moverlos.

## Espaciado

Escala: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128. Cualquier múltiplo de 4 vale; 2 px solo para ajustes dentro de un control pequeño.

| Uso | Valor |
|---|---|
| Dentro de un control | 4 a 12 |
| Entre elementos relacionados (filas de una lista) | 2 a 8 |
| Entre grupos (una etiqueta y su lista, dos tarjetas) | 12 a 24 |
| Entre secciones | 32 a 64; en una portada, 80 a 128 |
| Altura de fila | 32 compacta, 36 normal, 44 táctil |
| Relleno | paneles compactos 16, tarjetas 20 a 24, bordes de página 16 en móvil y 24 a 32 en escritorio |

Más espacio encima de un titular que debajo: el titular pertenece a lo que sigue.

## Rampas neutras

Una rampa para todo: fondo, superficies, bordes y texto. En modo operar, casi gris; en una portada se puede teñir más hacia el mundo del tema. La saturación se queda muy baja para que ninguna superficie se lea como un color.

| Rol | Claro, grafito | Claro, cálido | Claro, tinta | Oscuro, grafito |
|---|---|---|---|---|
| Fondo de página | #fafafa | #f7f4ee | #f5f7fa | #141415 |
| Tarjeta | #ffffff | #fdfbf7 | #ffffff | #19191b |
| Elevado (fila activa, campo) | #f4f4f5 | #efe9df | #eceff4 | #232325 |
| Línea fina | texto principal al 8 % | igual | igual | igual |
| Texto principal | #171717 | #1f1b16 | #111827 | #ededed |
| Texto secundario | #525252 | #5e554a | #4b5565 | #a1a1a6 |
| Texto apagado | #6e6e6e | #70675b | #626b7e | #8b8b91 |

El texto apagado es solo para metadatos y pies. Con estos valores da ≥ 4,5:1 sobre las tres superficies de su columna (calculado el 2026-11-21); si cambias un valor, vuelve a calcularlo.

Semánticos como texto: positivo #15803d y negativo #b91c1c en claro (≥ 4,5:1 sobre las superficies grafito; sobre las teñidas el positivo baja a 4,2: oscurécelo); positivo #4cc38a y negativo #f2555a en oscuro (≥ 4,6:1).

## Acento

- Si hay un color de marca real, es el acento y sale de las superficies.
- Si no, sale del mundo del tema: cálido (ámbar, coral, teja), frío (cobalto, verde azulado, azul cielo) o natural (musgo, salvia). La familia violeta-azul se evita salvo que la marca lo sea.
- Ocupa un porcentaje pequeño de la pantalla: la acción principal, la selección y una cifra clave.
- Texto sobre el acento ≥ 4,5:1; si no llega, oscurece el acento o usa texto oscuro. Como texto sobre fondo claro, un tono más oscuro del acento.

## Tipografía

Familias libres y autoalojables, según el carácter de la dirección; una para la interfaz y como mucho una pareja.

| Carácter | Interfaz | Pareja opcional |
|---|---|---|
| Preciso, técnico, sereno | IBM Plex Sans, Inter, Geist | IBM Plex Mono o JetBrains Mono para cifras |
| Cálido, cercano | Instrument Sans, DM Sans, Figtree | Newsreader o Instrument Serif solo en titulares grandes |
| Editorial, de lectura | Source Sans 3, Instrument Sans | Fraunces o Newsreader en titulares |

Una serif de titulares nunca va en etiquetas ni botones. En modo operar suele bastar una familia.

| Uso | Tamaño (px) | Interlineado | Peso |
|---|---|---|---|
| Metadatos, recuentos | 12 a 13 | 16 a 18 | 400 |
| Pies, texto secundario | 14 | 20 | 400 |
| Cuerpo | 16 a 17 | 24 a 26 | 400 |
| Cifra de tarjeta | 28 a 32 | 1 | 500, tabular |
| Título de página | 28 a 36 | 1,15 | 400 a 500 |
| Titular de portada | 48 a 64 en escritorio, 32 a 40 en móvil | 1,05 | 400 a 500 |

Espaciado entre letras: 0 por debajo de 16 px; desde 40 px, hasta −0,02 em; nunca por debajo de −0,04 em. Titulares con `text-wrap: balance`.

## Radio

| Elemento | Radio (px) |
|---|---|
| Etiqueta, botón pequeño | 4 a 6 |
| Fila, campo, botón | 8 a 10 |
| Tarjeta | 12 a 16 |
| Panel | 14 a 20 |

Anidado: interior = exterior − relleno, nunca menos de 4. No todo es una píldora.

## Iconos

Un juego de línea (el que ya use el proyecto o SVG propio), 16 o 18 px, trazo 1,5, del color del texto secundario o apagado, a 8 o 10 px de su etiqueta.

## Profundidad

- Claro: sombras neutras pequeñas, `0 1px 2px rgb(0 0 0 / 0.05)`; flotantes, `0 8px 24px rgb(0 0 0 / 0.06)`. Siempre con desplazamiento y desenfoque.
- Oscuro: pasos de superficie y líneas finas, no sombras.

## Movimiento

Una curva para todo: `cubic-bezier(0.22, 1, 0.36, 1)`.

| Uso | Duración |
|---|---|
| Encima, pulsar, interruptores | 120 a 180 ms |
| Menús, globos de ayuda | 160 a 220 ms |
| Entradas, cambios de disposición | 300 a 500 ms |
| Escalonado entre elementos | 40 a 60 ms, como mucho seis |

Subida al entrar de 6 a 12 px; reducción al pulsar de 0,97 a 0,98.

## Por modo

- **Operar** (calculadora, mapa, filtros): la familiaridad es una virtud; el que conoce el tipo de herramienta debe fiarse al momento. Escala tipográfica fija en `rem`, no fluida, con pasos de 1,125 a 1,2. Color contenido: el acento para acción, selección y estado. Movimiento de 150 a 250 ms que solo comunica estados; sin coreografía al cargar. Sin fuentes de titular en etiquetas, botones ni datos. Antes de una modal, agota la opción en línea.
- **Leer** (informe, nota metodológica): medida de 65 a 75 caracteres, jerarquía clara de encabezados, notas y fuentes fáciles de encontrar, tablas legibles en el móvil.
- **Persuadir** (portada): más ambición permitida; la visual es la herramienta real; una sola acción principal visible sin desplazar a 1280 × 800.

Adaptado de `heydamir/unslop` de Damir Sokolovsky (CC BY 4.0, «Tokens») y `pbakaus/impeccable` (Apache-2.0, «Operate mode»); traducido, reescrito y modificado (tamaños de cuerpo subidos a 16 px por el suelo, colores apagados y semánticos oscurecidos hasta 4,5:1, familias limitadas a las autoalojables).

Origen, autores y licencias: [licencias.md](licencias.md).
