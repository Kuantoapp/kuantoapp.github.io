---
description: "Diseña, rediseña o pule pantallas web del proyecto (app/, informe, páginas de docs/) para que parezcan diseñadas y no generadas: dirección propia, suelo innegociable (tokens, contraste, foco, móvil, movimiento), pasadas en orden de espaciado, color, iconos, textos, tipografía, maquetación, detalles, gráficos y movimiento, y comprobación sobre el render. No elige clasificación ni paleta de un mapa (dm-cartografia), no reescribe prosa (dm-humanizar), no comprueba cifras (dm-trazador-cifras) ni hace diapositivas (dm-presentacion)."
when_to_use: "Diseña la página de la herramienta; esto parece hecho por IA; pule la app; mejora el aspecto del informe; ¿qué tipografía y colores uso?; la web se ve mal en el móvil; quita degradados y emojis; cómo presento este gráfico en la web; deja la demo bonita"
---

# Diseño web

Hace que lo que ve el jurado y el público en la web parezca hecho para este proyecto y no salido de una plantilla. Un jurado ve muchas webs generadas en un concurso: los tics visuales de IA restan la misma credibilidad que los tics de redacción.

Fusiona cinco skills externas (créditos al final). El suelo y las señales están en `referencia/` y los comparten [dm-revisor-diseno](../../agents/dm-revisor-diseno.md) y [dm-presentacion](../dm-presentacion/SKILL.md).

## Regla de oro

**Se cambia cómo se ve, no lo que dice.** Las funciones, el contenido, las cifras, sus fuentes y sus marcas de estimado se quedan; las etiquetas y los botones se pueden reformular sin cambiar su significado. Nunca se inventa una cifra, una cita, un logotipo, un usuario ni un dato de ejemplo que parezca real: donde falta material, un hueco con su tamaño y qué va en él.

## Antes de empezar: conectar con el desarrollo del proyecto

1. **Qué está decidido:** `docs/decisiones.md` (stack de la app, publicación, licencias que hay que citar en la página y fechas clave). **Si falta menos de tres días para una fecha clave, solo se pule:** sin familia ni acento nuevos y sin pasar todo el CSS a variables; lo grande va al informe como propuesta. La app es HTML, CSS y JS sin framework: no se mete un framework, Tailwind ni una librería de componentes para diseñar.
2. **Qué sistema hay:** lee `app/estilo.css` (variables de `:root` si las hay; si no, los colores y familias que usa) y un `DESIGN.md` si existe. Si el sistema es bueno, se conservan sus valores, se pasan a variables y se corrige cómo se usan.
3. **Qué pide la issue:** pulir (se conserva la identidad) o rediseñar (se sustituye la apariencia, no el contenido). Si no lo dice, es pulir.
4. **Material real:** capturas de la app, cifras con fuente y el nombre del proyecto salen del repo. Lo que falte se pide una vez, en un solo mensaje: material, para quién es, la única acción que debe provocar la página y un tono extremo (editorial, técnico, sobrio, cálido…; «limpio y moderno» no es un tono). Si el usuario dice «hazlo», se infiere y se dice qué se eligió en una línea.

## Flujo

1. **Mirar la pantalla:** sirve la app (`python -m http.server 8000 -d app`) y haz capturas a 390 y 1440 de ancho con la herramienta de navegador que haya. Se juzga lo que se ve, no solo el código.
2. **Auditar:** recorre [señales](referencia/senales.md) y anota cada una con dónde está, una línea por señal.
3. **Decidir cuánto cambiar,** con la auditoría delante:
   - **Mucho** (señales en color, tipografía, iconos y textos): flujo completo.
   - **Poco** (está diseñada, quedan restos): solo lo que encontró la auditoría; la dirección sale de lo que ya hay. Las ideas grandes van al informe como propuesta.
   - **Nada:** dilo y propone dos o tres ajustes con valores exactos. No se cambia una pantalla buena para que sea distinta.
4. **Dirección, en seis líneas, y para:**
   - **Producto:** qué hace y para quién, en una frase llana.
   - **Modo:** *operar* (el visitante hace una tarea: calculadora, mapa, filtros), *leer* (entiende algo: informe, nota metodológica) o *persuadir* (decide y actúa: portada). Se elige por la pantalla, no por el producto. Operar y leer piden precisión y contención; persuadir admite más ambición.
   - **Carácter:** dos o tres palabras concretas. Prohibidas: limpio, moderno, elegante, minimalista, premium.
   - **Mundo:** el lugar o material al que pertenece el tema del proyecto (sus objetos, documentos y lugares reales). Tiñe los neutros y da el acento.
   - **Momento:** uno o dos sitios donde la pantalla se permite color y detalle, sacados del contenido (el gráfico principal, el mapa, la cifra que importa). Todo lo demás, tranquilo.
   - **Firma:** un detalle que solo tendría este proyecto, usado siempre igual.

   **Prueba del espejo:** ¿otro proyecto del mismo concurso recibiría esta misma dirección? Si sí, cambia una decisión y di cuál. Enseña auditoría y dirección y espera respuesta antes de editar, salvo que ya hayan dicho «hazlo».
5. **Pasadas, en este orden,** cada una sobre toda la pantalla antes de la siguiente; los valores de partida están en [valores](referencia/valores.md):
   1. **Espaciado:** escala de 4 px; lo igual mide igual; menos espacio dentro de un grupo que entre grupos; todo alineado a columnas.
   2. **Color:** una rampa neutra teñida hacia el mundo, tres roles de texto, un acento que se usa poco. En modo operar, superficies neutras: el color lo llevan los datos.
   3. **Iconos:** un solo juego de línea (el que ya use el proyecto, o SVG propio), un tamaño y un trazo, del color de su texto. Fuera los emoji y los iconos que no aportan.
   4. **Textos de interfaz:** etiquetas, botones, errores y vacíos, sin cambiar su significado. Un botón dice su acción; un error, el problema y cómo salir; un cambio, con qué se compara (si los datos no lo dicen, se pide). Sin exclamaciones ni palabras infladas. Los párrafos y el tono van a `dm-humanizar`.
   5. **Tipografía:** una familia para la interfaz y, como mucho, una pareja (mono para cifras o una de titulares). Jerarquía por tamaño y color, pesos 400 a 600, mayúscula solo inicial, cifras tabulares en formato español.
   6. **Maquetación:** se conservan secciones y orden. Una acción principal por pantalla. Titulares largos alineados a la izquierda. En el móvil, todo en orden de lectura y nada más ancho que la pantalla.
   7. **Detalles:** radios anidados, estados de todos los controles, foco visible, superficies del navegador (selección, barra de desplazamiento, `accent-color`) con la paleta.
   8. **Gráficos, mapa y visuales:** [gráficos](referencia/graficos.md). Un gráfico principal, el resto más pequeño y de otro tipo. Nada de relleno decorativo (manchas, orbes, rejillas brillantes). Del mapa, aquí van su accesibilidad y su encaje en la página; la clasificación y la paleta, a `dm-cartografia`.
   9. **Movimiento:** solo el que explica algo (un cambio de estado, un número que se actualiza). `transform` y `opacity`, una curva, alternativa con movimiento reducido.
6. **Comprobar:** [suelo](referencia/suelo.md) entero sobre el render, otra vez a 390 y 1440 (y a 320 si hay tablas o mapas). Lo que siga en la lista de la auditoría se arregla. Como mucho tres rondas de render: agrupa los arreglos.
7. **Informe:** dirección, qué cambió en cada pasada en pocas líneas y los huecos de material que quedan, con su tamaño.

## Contrastar cada resultado con lo que debe salir

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Contraste calculado con los valores reales | Texto normal ≥ 4,5:1, grande ≥ 3:1, foco y bordes de control ≥ 3:1 | Oscurece el color o cambia el fondo; da el par de valores y la ratio |
| Ancho 320 y 390 | Sin desplazamiento horizontal; objetivos táctiles ≥ 44 px; nada tapado | Pistas `minmax(0, 1fr)`, `min-width: 0`, reordena |
| Teclado solo | Se llega a todo con Tab, en orden, con foco visible | `:focus-visible`, orden del DOM, elementos nativos |
| Prueba de la plantilla: cambia el nombre del proyecto por otro | Ya no encaja | Empuja la dirección en textos, visual y firma |
| Cifras visibles | Mismas cifras y notas `[^id]` que antes del cambio | Restaura; las cifras no se tocan |
| `python .github/scripts/cifras_con_fuente.py` y tests JS de `app/` | En verde | Corrige la línea que indica |

## Al terminar: dejar el trabajo conectado

- Los tokens nuevos van a `:root` de `app/estilo.css`; si el sistema cambia, una línea en `docs/decisiones.md` (familia, acento, escala), para que la presentación use el mismo.
- Antes del PR: `dm-revisor-diseno` sobre la pantalla; `dm-trazador-cifras` si se tocó cualquier texto con cifras; `dm-revisor-seguridad` si se añadió HTML dinámico o un recurso externo.
- Las fuentes tipográficas y los iconos se sirven desde el repo (la demo debe funcionar sin red; ver `docs/decisiones.md`) y su licencia se cita como la de `app/vendor/`.

## Errores que invalidan un resultado

- Una cifra, un testimonio, un logotipo o un dato de ejemplo inventado, o una cifra que pierde su fuente.
- Quitar foco visible, contraste o alternativa de teclado para que «quede más limpio».
- Cambiar un tic por otro de moda (glass, grano, neón, rejilla de tarjetas iguales) en vez de decidir.
- Una dependencia nueva (framework, CDN, librería de componentes) para algo que hacen CSS y HTML.
- Dar por bueno el diseño sin haber mirado el render en móvil.

## Referencia

- [suelo.md](referencia/suelo.md): reglas que nunca se saltan, comprobables sobre el render. Las usan también el revisor y la presentación.
- [senales.md](referencia/senales.md): catálogo de señales de interfaz generada y su arreglo.
- [valores.md](referencia/valores.md): escalas de espaciado, tipografía, radio y movimiento, rampas neutras y lo propio de cada modo.
- [graficos.md](referencia/graficos.md): forma según el dato, construcción, color y honestidad de los gráficos.
- [estados.md](referencia/estados.md): formularios, carga, vacíos, errores, modo oscuro y demo sin red, para cuando la pantalla los necesite.
- [licencias.md](referencia/licencias.md): obras de origen, autores, licencias y lo que se dejó fuera.

## Origen y licencias

Adaptado y reescrito en español a partir de: `heydamir/unslop` de Damir Sokolovsky (CC BY 4.0: pasadas, dirección, señales y valores), `Nutlope/hallmark` (MIT: suelo, pregunta única, prueba del espejo, gráficos), `pbakaus/impeccable` (Apache-2.0: modos, suelo de oficio, operar), `nextlevelbuilder/ui-ux-pro-max-skill` (MIT: prioridades de accesibilidad e interacción) y `Leonxlnx/taste-skill` (MIT: prohibiciones). De `dickwu/apple-design-skill`, sin licencia, solo se toman ideas generales reescritas (prueba de la plantilla, «números, no adjetivos»), nada de su texto ni de las páginas de Apple. Se modificaron todos los textos; ninguno conserva el original. Enlaces, avisos de copyright y licencias en [licencias.md](referencia/licencias.md).
