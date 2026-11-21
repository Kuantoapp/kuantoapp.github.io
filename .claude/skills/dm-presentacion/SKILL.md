---
description: "Maqueta las diapositivas del pitch ante el jurado con el sistema visual de la web: una idea por diapositiva con su titular-conclusión, arco del relato, cifras grandes con su fuente, capturas reales de la app, gráficos legibles al fondo de la sala, demo con plan B, exportación a PDF y ensayo cronometrado. No escribe el contenido del guion (lo da la issue del pitch), no humaniza el texto (dm-humanizar) ni comprueba cifras (dm-trazador-cifras)."
when_to_use: "Maqueta las diapositivas del pitch; hazme la presentación; ¿cómo queda esta diapositiva?; pasa el guion a diapositivas; la presentación parece de plantilla; ¿se lee desde el fondo?; prepara el PDF de la presentación; ¿cuántas diapositivas para cinco minutos?"
---

# Presentación

Convierte el contenido del pitch en diapositivas que el jurado entienda de un vistazo y que parezcan del mismo proyecto que la web. El contenido (qué se dice y con qué cifras) lo dan el guion y la issue de diapositivas; esta skill decide cómo se ve y comprueba que se lee.

## Regla de oro

**Una diapositiva, una idea, y su titular es esa idea.** Si el titular no se entiende sin la persona que habla, no es un titular. Y como en la web: ninguna cifra sin fuente ni dato inventado.

## Antes de empezar: conectar con el desarrollo del proyecto

1. **Qué está decidido:** `docs/decisiones.md` (duración de la presentación si ya se sabe, criterios del jurado, sistema visual). La herramienta la elige quien presenta; si no lo ha dicho, pregúntalo una vez. Las reglas de abajo valen para cualquiera; para HTML hay plantilla.
2. **El contenido:** el guion y el contenido de las diapositivas que dejan en `docs/pitch/` las issues del pitch (`gh issue list --search "docs(pitch)"`). Cada diapositiva corresponde a un bloque del guion; si falta el guion, se pide, no se escribe aquí.
3. **El sistema visual:** el de `app/estilo.css` (sus variables de `:root` si las tiene; si no, los colores y la familia que usa). La presentación usa la misma familia, rampa y acento; no se inventa otro estilo.
4. **El material:** capturas reales de la app (se hacen sirviéndola en local), gráficos con los datos de `app/datos/` y las fuentes de cada cifra.

## Flujo

1. **Arco:** ordena los bloques del guion alternando *lo que pasa* (el problema, con un dato) y *lo que podría ser* (lo que la herramienta permite), y cierra con la acción que se pide. Para un jurado de datos abiertos, un orden que funciona: problema con dato → a quién afecta → qué hace la herramienta (demo) → cómo se calcula y con qué datos públicos → validación y límites → impacto → viabilidad y mantenimiento → código abierto y reutilización → cierre. Ajústalo a los criterios de `docs/decisiones.md`.
2. **Cuántas:** de 30 a 60 segundos por diapositiva, con la duración que fije `docs/decisiones.md` (si no la fija, pregúntala); por ejemplo, para cinco minutos, entre 6 y 10. Si sobran, se funden; nunca se encoge la letra para que quepan.
3. **Cada diapositiva**, antes de maquetar, en una línea: titular-conclusión (una frase con verbo, como mucho 12 palabras), la única visual que la prueba y la fuente de su cifra.
4. **Maquetar** con [plantilla-html](referencia/plantilla-html.md) o en la herramienta elegida, con estas reglas:
   - Como mucho unas 30 palabras visibles; lo demás va a las notas de quien habla.
   - Una visual por diapositiva: la captura real, un gráfico o una cifra grande. Las formas de gráfico, en `dm-diseno-web` ([gráficos](../dm-diseno-web/referencia/graficos.md)).
   - Legible desde el fondo de la sala: en un lienzo de 1920 × 1080, cuerpo de 28 px o más, titular de 56 px o más, cifras grandes de 120 px o más, etiquetas de gráfico de 20 px o más. Contraste alto (≥ 7:1 en el texto, los proyectores lo bajan) y nunca texto sobre una foto sin un fondo liso.
   - Cada cifra con su fuente en una línea pequeña al pie de la misma diapositiva, y «estimado» si lo es.
   - Una plantilla de diapositiva por tipo (portada, cifra, captura, gráfico, cierre), repetida igual: mismo margen, misma posición del titular, mismo pie.
   - Sin animaciones salvo una que explique algo (revelar la segunda serie); sin transiciones entre diapositivas.
   - El [suelo](../dm-diseno-web/referencia/suelo.md) y las [señales](../dm-diseno-web/referencia/senales.md) de la web valen igual: sin antetítulos, degradados, emoji ni tarjetas de relleno.
5. **Demo:** si hay demo en vivo, una diapositiva antes que diga qué se va a ver y un plan B dentro de la propia presentación (capturas o un vídeo corto en local) por si falla la red o el proyector.
6. **Comprobar** y **ensayar** (tabla de abajo).

## Contrastar cada resultado con lo que debe salir

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Leer solo los titulares, en orden | Cuentan la historia entera | Reescribe los que describen («Resultados») en vez de concluir |
| Captura a 1280 × 720 reducida a la mitad | Titular y cifra se leen | Menos palabras, letra más grande |
| Cada cifra | Su fuente en la misma diapositiva; coincide con la web y el guion | `dm-trazador-cifras` |
| `python .github/scripts/cifras_con_fuente.py` si las diapositivas están en `docs/pitch/` | En verde | Añade la nota o `<!-- sin-fuente: motivo -->` |
| Exportación a PDF (imprimir a PDF, 16:9) | Una diapositiva por página, sin cortes ni fuentes sustituidas | Revisa `@page` y que las fuentes se sirvan en local |
| Sin red | Se abre y se ve igual | Quita los recursos externos |
| Ensayo cronometrado en voz alta | Dentro del tiempo con margen de un 10 % | Quita una diapositiva, no aceleres |

## Al terminar: dejar el trabajo conectado

- Las diapositivas van a `docs/pitch/` (con su PDF exportado si la herramienta no es HTML) y se enlazan desde la issue del pitch.
- Antes del ensayo: `dm-trazador-cifras` sobre las cifras, `dm-humanizar` sobre los textos y `dm-revisor-diseno` sobre el aspecto.
- Si cambia el sistema visual para la presentación, se cambia también en la web, o no se cambia.

## Errores que invalidan un resultado

- Una cifra sin fuente, o distinta de la de la web o el guion.
- Una captura retocada o una maqueta que enseña algo que la app no hace.
- Diapositivas que son párrafos leídos en voz alta.
- Depender de la red o de un recurso externo el día de la presentación sin plan B.

## Referencia

- [plantilla-html.md](referencia/plantilla-html.md): esqueleto de presentación en un solo HTML, con teclado, notas, impresión a PDF y los tokens de la app.

## Origen y licencias

El arco que alterna «lo que pasa» y «lo que podría ser» es el patrón de Nancy Duarte, tal como lo recoge `nextlevelbuilder/ui-ux-pro-max-skill` (MIT, skill `slides`); de esa skill también se toma la idea de una plantilla HTML con lienzo 16:9. El resto se escribió para este repo; las reglas visuales son las de `dm-diseno-web`. Licencias y enlaces en [licencias.md](../dm-diseno-web/referencia/licencias.md).
