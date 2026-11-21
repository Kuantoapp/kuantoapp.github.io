# Señales de interfaz generada

Contenido: superficies y color · tipografía · iconos · espaciado · textos · componentes · portada · visuales · movimiento · aspecto de plantilla.

Cada línea empareja la señal con su arreglo. En la auditoría se anota cada una con el fichero y la línea, o la zona de la captura.

## Superficies y color

- Degradados de violeta a azul o de violeta a rosa en fondos, tarjetas, botones o el elemento activo → una superficie neutra; el acento solo donde significa algo.
- Texto en degradado en titulares, cifras o el logotipo → color sólido de texto principal.
- Brillos de color (`box-shadow` de color sin desplazamiento, `drop-shadow` en emoji) → fuera; la profundidad sale de pasos de superficie y líneas finas.
- Manchas o lavados de color difuminados tras el contenido → fuera.
- Bordes de neón o de mucho contraste → línea fina del color del texto al 6-10 % de opacidad.
- Cinco tonos casi iguales para el texto → tres roles (principal, secundario, apagado) de una rampa.
- Todo resaltado, así que nada destaca → un acento, una o dos veces por pantalla.
- Tarjetas de cristal con reflejo blanco y sombra de color → superficie elevada con línea fina.
- Claro u oscuro elegido por la categoría («es tecnología, va en oscuro») → se elige por la escena de uso: quién, dónde y con qué luz.

## Tipografía

- Titulares en peso 800 o 900 → 400 a 500 y el tamaño hace la jerarquía.
- Etiquetas en mayúsculas espaciadas (`RESUMEN`, `ALQUILER MEDIO`) → mayúscula inicial y espaciado normal.
- Demasiados tamaños y pesos en una pantalla → unos pocos de la escala, pesos 400 y 500.
- Cifras en formatos mezclados (`12.500 €` junto a `12500,00€`) → un formato, el que ya use la app, con cifras tabulares.
- Espaciado negativo en texto pequeño → cero o ligeramente positivo.
- Cursiva para enfatizar → color o peso.
- Monoespaciada como disfraz de «técnico» → solo para código, datos o medidas.

## Iconos

- Emoji como icono de navegación, de etiqueta o de estado (🏠 🚀 💰 📈 ⚠️) → un juego de iconos de línea o ninguno.
- Iconos de varios tamaños y colores → un tamaño, un trazo, el color de su texto.
- Iconos fuera de su columna → la misma caja de icono en cada fila.
- Un destello ✨ para todo lo que tenga IA → fuera.

## Espaciado

- Valores sueltos (13 px, 7 px, 31 px) → pasos de la escala de 4 px.
- Filas de una lista con alturas o separaciones distintas → una altura y una separación.
- Grupos más pegados a sus vecinos que a sus propios elementos → menos espacio dentro, más entre grupos.
- Relleno desigual en tarjetas hermanas → un relleno.

## Textos

- Saludos como titular (`¡Bienvenido! 👋`) → el nombre de la página o del periodo.
- Exclamaciones → enunciado llano.
- Cambios sin referencia (`+12 %`) → la referencia que dan los datos (`+12 % frente a <periodo>`); si los datos no la dan, se pide, no se inventa.
- Marcadores de posición largos (`Busca lo que quieras...`) → `Buscar`.
- Palabras infladas (revoluciona, potencia, sin fisuras, descubre, desbloquea, impulsado por IA) → lo que hace de verdad.
- Punto final en etiquetas y botones → sin punto.
- Datos que parecen falsos (`123.456`, `[X]`) → los reales de la app.
- Afirmaciones que no se pueden comprobar (`Miles de usuarios`) → fuera, salvo que haya fuente.

## Componentes

- Píldoras brillantes para recuentos o estados → texto discreto.
- Insignias `Nuevo ✨` o `Beta 🚀` → fuera, o una de texto si de verdad hace falta.
- Todo en forma de píldora → radio según el tamaño, con radios anidados.
- Tarjetas iguales en fila, cada una con icono, título y frase vaga, como estructura de la página → menos elementos, contenido concreto y anchos con ritmo.
- La plantilla de «cifra gigante, etiqueta pequeña y tres cifras de apoyo» → la cifra que importa, con su comparación y su fuente.
- Minigráficos o anillos de progreso en cada tarjeta de cifra → la cifra, su etiqueta y su cambio.
- Números de sección (01 / 02 / 03) sin que la secuencia importe → fuera.
- Una ventana modal para algo que no necesita interrumpir → en línea.

## Portada

- Píldora sobre el titular (`✨ Presentamos…`) → fuera.
- Un titular que serviría para cualquier proyecto → qué hace este, con sus propios sustantivos.
- Manchas, orbes, rejillas y líneas brillantes tras la portada → fondo liso o una vista real de la herramienta.
- Todo apilado y centrado (titular, texto, botones, imagen debajo) → texto a un lado y la visual con al menos la mitad del ancho, o texto sobre una vista grande de la herramienta.
- Tres botones o más → uno principal y, como mucho, uno secundario.

## Visuales

- Formas 3D brillantes, cromo líquido, nebulosas, robots, cerebros o circuitos → la propia herramienta o una metáfora concreta de lo que hace.
- Texto o botones falsos dentro de una imagen → texto real en la página.
- Una visual en cada sección → una donde ayuda.

## Movimiento

- Pulsos o latidos en cosas que no están vivas → estático.
- `transition: all` y `scale` al pasar por encima de tarjetas → cambio de color o de superficie; una leve reducción al pulsar.
- Muelles y rebotes → una curva de salida suave.
- Cada sección entrando al desplazar, desde lados distintos → como mucho una entrada al cargar.

## Aspecto de plantilla

No son errores, pero son lo que queda cuando nadie decidió nada. Se miran tras las pasadas.

- Fondo gris puro, Inter, texto blanco y el color de marca en un botón, en un tema cálido → rampa teñida hacia el mundo y acento sacado de él.
- Las tres apariencias que más repiten los generadores: crema cálido con serif de mucho contraste y acento terracota; casi negro con un único acento verde ácido o bermellón; y «periódico» de líneas finas, radio cero y columnas densas. Sin una razón que salga del tema, son un valor por defecto, no una elección.
- Una visual que es una caja vacía o una imagen genérica → una vista de la herramienta o una imagen del mundo del tema.

Adaptado de `heydamir/unslop` de Damir Sokolovsky (CC BY 4.0, «Signs of slop»), con añadidos de `pbakaus/impeccable` (Apache-2.0) y `Leonxlnx/taste-skill` (MIT) y una idea de `dickwu/apple-design-skill` reescrita; traducido, reescrito y modificado.

Origen, autores y licencias: [licencias.md](licencias.md).
