# Guion de la versión de 5 diapositivas (respaldo)

Se usa solo si la organización limita el número de diapositivas. La versión principal es `index.html`; esta es `corta.html`, con los mismos textos de `guion.md`, condensados.

Cada diapositiva es una escena: `→` avanza un paso dentro de la misma diapositiva. El bloque del que se habla brilla y los que ya se han contado quedan a media luz; en el último paso, todo vuelve a plena luz.

Con `?corto` en la URL, el corto se ve primero dentro de la diapositiva 1. La tecla `W` abre la web con el estado de Lucía. El resto de teclas son las de la principal: `F`, `P`, `N` y `L`.

| Diapositiva | Orador | Tiempo | Pasos |
|---|---|---|---|
| 1. Apertura | Yeray | 1:00 | ciudad → ventana, tren y casa → la cuenta que no sale → 1 de cada 3 → creemos → merece una respuesta → Kuanto |
| 2. En directo | Alex | 3:30 | Lucía → las 7 capas → (demo con `W`) → Getafe, Parla y Centro |
| 3. Por qué | Izan | 2:00 | mapa de Lucía → Chamartín → 1 de cada 7 → Bono → ¿Y si…? → IA |
| 4. Cómo y rigor | Yeray | 1:30 | timeline → arquitectura → cifras clave → equipo → del dato a la cifra y lo que no hacemos |
| 5. Impacto y cierre | Yeray | 1:00 | privacidad → recomendaciones → mercados → quien nos ha ayudado → DataMad → frase final |

<!-- sin-fuente: tiempos y número de pasos del guion -->

## 1. Apertura (Yeray)

> Una ciudad es muchas cosas. [→] Es una luz que se enciende en una ventana. Es el trayecto de cada mañana. Es el sitio al que vuelves. [→] Y vivir en ella se ha convertido en una cuenta que no sale.
>
> [→] En la Comunidad de Madrid, uno de cada tres hogares que viven de alquiler dedica más del 40 % de lo que ingresa a la vivienda. En la ciudad de Madrid, el alquiler mediano ya pesa un 19,6 %. [^ecv]
>
> [→] Creemos que nadie debería descubrir demasiado tarde que su casa cuesta más de lo que parecía. Que el tiempo en el transporte público también es un precio. Y que una decisión así merece algo más que un presentimiento.
>
> [→] Merece una respuesta. [→] Esto es Kuanto. Alex.

## 2. En directo (Alex)

> Os presento a Lucía: 30 años, 24.000 euros brutos, trabaja en Getafe. Todos los portales le dicen cuánto cuesta el alquiler. Kuanto le dice cuánto le sobra. [^ejemplo]
>
> [→] Siete capas en una sola cifra.

Demo con `W`, igual que en `guion.md`.

> [→] Getafe, 291 euros y doce horas; Parla, 467 pero veintiséis horas; en Centro no le llega. Ahora lo decide sabiendo. Izan. [^ejemplo]

## 3. Por qué (Izan)

> La misma Lucía, con el mismo sueldo: de menos 482 euros en Salamanca a más 703 en Villarejo, con casi 70 horas de transporte público. [^lucia]
>
> [→] Mirar solo el alquiler engaña: Chamartín es más caro y pesa menos. [→] Con el sueldo mínimo, vivir lejos compensa en una de cada siete combinaciones. [^horas]
>
> [→] Casi cuatro de cada cinco solicitudes del Bono, sin ayuda; Madrid capital, fuera del tope por 79 euros. [^bono]
>
> [→] ¿Y si sube el alquiler y se acaba el descuento? Un 35 % menos cada mes. [^escenarios]
>
> [→] Y una IA miró entre cuatro y seis zonas; Kuanto, 99. Yeray os cuenta cómo. [^ia]

## 4. Cómo y rigor (Yeray)

> Quince días, cuatro líneas de trabajo y nueve hitos, con las reglas y la CI antes de analizar un solo dato. [→] De 89 descargas oficiales y abiertas a cinco salidas, sin servidor. [^git]
>
> [→] Detrás de cada número: casi medio millón de alquileres, 42.785 trayectos, viviendas cuadradas con Hacienda al 99,9 %, 393 veredictos de agentes y cero cifras sin fuente. [^met]
>
> [→] Tres personas y un equipo de agentes que audita cada cambio. [→] Cada capa, con su validación. Y lo que no hacemos, todavía, porque no queremos hacerlo a medias.

## 5. Impacto y cierre (Yeray)

> Tu sueldo nunca sale de tu móvil. [→] Tres decisiones que la Administración puede tomar mañana. [→] Un motor, tres mercados, cero euros de servidor.
>
> [→] Félix Peralta y Alberto Martos revisaron el proyecto; el post de LinkedIn tuvo 40 reacciones, según nuestro recuento. [^linkedin]
>
> [→] Lo que DataMad pide, cumplido. [→] Nadie debería descubrir demasiado tarde cuánto le cuesta su casa. Esto es Kuanto. Gracias.

[^ecv]: Las cifras y sus fuentes son las de `guion.md` y `index.html`: ECV 2025 (36,0 %, estimado), SERPAVI y ADRH 2024.
[^ejemplo]: `docs/como-funciona.md` y la ficha de Parla (estimado).
[^lucia]: `mesobra.calculo` con `app/datos` (estimado).
[^horas]: `app/datos/analisis.json`, 1.218 de 8.620 pares (estimado).
[^bono]: Catálogo regional, Bono Alquiler Joven 2022; simulación del tope (estimado).
[^escenarios]: `mesobra.calculo`: de 291 a 188 € (estimado).
[^ia]: `docs/kuanto-frente-a-ia.md`.
[^git]: GitHub y `data/README.md`.
[^met]: `docs/decisiones.md`, nota metodológica y cuerpos de los PR.
[^linkedin]: Cifras del post aportadas por el equipo, a 26-11-2026.
