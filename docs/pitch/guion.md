# Guion del pitch de Kuanto (DataMad 2026, ante el jurado)

Duración prevista: 9:00. Orden: Yeray, Alex, Izan, Yeray. <!-- sin-fuente: duración y orden del equipo -->

Se presenta con `docs/pitch/index.html`. Teclas:

- `→` o espacio: siguiente diapositiva, o siguiente paso dentro de ella.
- `←`: atrás.
- `F`: pantalla completa.
- `P`: modo orador en otra ventana, con el guion, la diapositiva siguiente y el reloj de cada bloque.
- `N`: notas sobre la diapositiva.
- `B`: plan B de la demo, con capturas reales de hoy.
- `A`: anexo para las preguntas.
- `L`: modo ligero, que quita las animaciones pesadas.

[→] marca un paso dentro de la misma diapositiva.

| Bloque | Orador | Tiempo | Diapositivas |
|---|---|---|---|
| Apertura | Yeray | 1:30 | corto → cierre del «Merece una respuesta» |
| Qué: demo | Alex | 3:30 | Lucía → en directo → tres zonas |
| Por qué | Izan | 1:45 | capas → IA |
| Cómo y despedida | Yeray | 2:15 | fuentes → cierre |

<!-- sin-fuente: tiempos del guion -->

## 1. Yeray · Apertura (1:30, con el corto)

**Corto (30-45 s).** Se reproduce solo y pasa a la siguiente al acabar. Yeray sale durante el fundido a negro. Si el corto dura 45 s, recorta la pausa de las tres frases «Creemos que…». <!-- sin-fuente: duración del corto -->

> Una ciudad es muchas cosas. [PAUSA]
>
> Es una luz que se enciende en una ventana. [→] Es el trayecto de cada mañana. [→] Es el sitio al que vuelves cuando todo lo demás ha terminado. [PAUSA]
>
> Y durante años, vivir en ella se ha convertido en una cuenta que no sale. [→ fórmula] [PAUSA LARGA]
>
> En la ciudad de Madrid, el alquiler mediano pesa un 19,6 % de la renta neta de los hogares. [^serpavi]
>
> [→] Y no pesa igual en todas partes: del 12,6 % de Villanueva de la Cañada al 24,0 % de Centro. [PAUSA] [^rango]
>
> Creemos que nadie debería descubrir demasiado tarde que su casa cuesta más de lo que parecía.
>
> Creemos que el tiempo que pasas en un tren también es un precio.
>
> Y creemos que una decisión así merece algo más que un presentimiento. [PAUSA]
>
> Merece una respuesta. [→ mapa y logo] Esto es Kuanto. Alex.

## 2. Alex · Qué: demo en vivo (3:30)

> Os presento a Lucía. Treinta años, vive sola, gana 24.000 euros brutos y trabaja en Getafe. Busca piso, y todos los portales le dicen lo mismo: cuánto cuesta el alquiler. [^ejemplo]
>
> [→] Pero lo que Lucía necesita saber es otra cosa: dónde le sobra más dinero a final de mes.
>
> Vamos a verlo.

**Demo en directo (unos 2:30).** Antes de empezar, deja abierta la pestaña con el enlace del túnel y el estado de Lucía en la URL. Recorrido: <!-- sin-fuente: duración de la demo -->

1. **Tarjetas.**
   - Hogar: sola.
   - Sueldo: 24.000 € brutos en 12 pagas, 30 años. <!-- [^ejemplo] -->
   - Trabajo: Getafe, 5 días, transporte público.
2. **«Ver el mapa».** Métrica «Lo que sobra».
3. **Parla.** «Si firmas hoy un contrato nuevo, te sobran unos 467 € al mes», con 25,9 h de viaje y una horquilla de 338 a 575 € según el piso. <!-- [^ejemplo] -->
4. **Filtro principal.** Pasar a «Horas de viaje» y después a «Precio de la hora».
5. **Otros escenarios.** Activar el fin del descuento del abono.
6. **Vuelta a la presentación** con la flecha.

**Si falla la red:** tecla `B`. Son 4 capturas reales de hoy: tarjetas, mapa de lo que sobra, ficha de Parla y precio de la hora. Con `B` otra vez se vuelve. <!-- sin-fuente: número de diapositivas del plan B -->

> Getafe: le sobran 291 euros, con doce horas de viaje al mes. Parla: 467. Parece mejor… pero son veintiséis horas. Y en Centro, directamente, no le llega: le faltan 378. [^ejemplo]
>
> [→] 176 euros más al mes a cambio de catorce horas más de tren. ¿Le compensa? Eso lo decide Lucía. Pero ahora lo decide sabiendo. Izan. [^ejemplo]

## 3. Izan · Por qué (1:45)

> Hay muchos proyectos que miran el alquiler. Algunos añaden el tiempo de viaje. Nosotros hacemos la cuenta entera: el neto con el IRPF de 2026 del BOE, el abono más barato para cada persona, la cesta según ingresos, el hogar y, sobre todo, desde dónde trabajas tú. Siete capas. Una sola cifra. <!-- sin-fuente: año de la norma y número de capas -->
>
> ¿Por qué hace falta? Porque mirar solo el alquiler engaña. En Chamartín el alquiler mediano es de 1.126 euros, más que en Centro. Y aun así pesa menos: un 16 % frente a un 24 %. [^chamartin]
>
> [→] No es más barato. Es que allí se gana un 78 % más. [^chamartin]
>
> Y el tiempo. Con el sueldo mínimo, irse lejos para pagar menos solo compensa las horas de tren, valoradas a lo que ganas por hora, en una de cada siete combinaciones. En las otras seis, lo pagas con tu tiempo. [^horas]
>
> Y no es solo un problema de cada persona. En 2022 hubo 51.735 solicitudes del Bono Alquiler Joven. Se aceptó el 22 %. Y la proporción aceptada no cambia con lo que pesa el alquiler en cada municipio. [^bono]
>
> [→] Con el sueldo mínimo, 16 municipios quedan fuera del tope del Bono. Catorce, por menos de 80 euros. [^bono]
>
> Y lo que viene. Si todo el descuento del abono termina con 2026, cada adulto puede pagar hasta 33 euros más al mes. A 21 de noviembre no se había publicado ninguna prórroga. Kuanto ya lo calcula, zona a zona. [^abono]
>
> ¿Por qué no preguntárselo a una IA? Lo hicimos. ChatGPT y Gemini miraron entre cuatro y seis zonas, erraron el neto y cada uno puso un municipio en la zona de abono equivocada. Kuanto da cifra en 99 zonas, con la ley en la mano. Yeray os cuenta cómo. [^ia]

## 4. Yeray · Cómo y despedida (2:15)

> Detrás de cada cifra hay una fuente oficial. 89 descargas: INE, Consorcio de Transportes, BOE, BOCM, el catálogo de la Comunidad, Hacienda, el Ministerio de Vivienda. Cada una con su huella digital: si cambia un solo byte, lo sabemos. [^fuentes]
>
> Y cada cifra se puede seguir hasta su origen. Los 467 euros de Lucía salen de un cálculo en su navegador, de un fichero de alquileres y de una descarga del Ministerio con esta huella. [^ejemplo]
>
> [→] Si alguien intenta publicar una cifra sin fuente, el sistema la rechaza.
>
> Somos tres personas. Pero hemos construido un equipo: agentes de IA que escriben el código y otros que lo auditan. Doce especialistas, ocho revisores, un abogado del diablo incluido, y dieciséis guardias automáticos. Ningún cambio de un área con revisor entra sin su veredicto. [^harness]
>
> En quince días: 259 cambios fusionados, 993 tests y 131 decisiones fechadas y justificadas. Rápido. Y revisado. [^git]
>
> Y en un momento en que nuestros datos valen más que nunca, una promesa sencilla: tu sueldo nunca sale de tu móvil. Sin servidor, sin cuentas, sin rastreo.
>
> Kuanto está hecho para conectarse: el estándar europeo DCAT-AP, 1.670 entidades de Smart Data Models y un servidor MCP para que cualquier IA responda con nuestras cifras. Y para durar: cero euros de servidor y un comando que lo regenera todo. [^sdm]
>
> Datos de la Comunidad dentro del cálculo. Viable. Abierto. Y útil para quien busca piso y para quien hace política de vivienda.
>
> Empezamos diciendo que una ciudad es muchas cosas. Para demasiada gente, también es una cuenta que no sale. [PAUSA] Nadie debería descubrir demasiado tarde cuánto le cuesta su casa. [→] Esto es Kuanto. Gracias.

## Antes de salir

- **Material:** el corto en `docs/pitch/video/corto.mp4`; no se versiona.
- **Demo:** la pestaña del túnel ya abierta con el estado de Lucía.
- **Plan B:** probar la tecla `B`.
- **Pantalla:** proyector en espejo y modo orador (`P`) en el portátil si se puede extender la pantalla; si no, este guion impreso.
- **PDF de respaldo:** `docs/pitch/pitch.pdf`, sin animaciones.

[^serpavi]: SERPAVI (MIVAU) y ADRH (INE), 2024: alquiler mediano entre renta neta media mensual del hogar en la ciudad de Madrid. `app/datos/analisis.json` (titulares) y `docs/informe/cifras.md`.
[^rango]: Esfuerzo 2024 entre zonas con al menos 70 alquileres declarados: Villanueva de la Cañada 12,6 %, Centro 24,0 %. `docs/informe/cifras.md`.
[^cambio]: 142 zonas con dato en 2015 y 2024; sube en 68. Solo 31 suben más que su margen de error y la mediana del cambio es −0,06 puntos (estimado). `docs/informe/cifras.md`.
[^ejemplo]: Caso de ejemplo de `docs/como-funciona.md` y ficha de Parla de la herramienta (26-11-2026). Lo que sobra es de 291 € en Getafe, 467 € en Parla y −378 € en Centro; las horas al mes, 12, 26 y 26. Estimado.
[^chamartin]: Chamartín: 1.126 €/mes de alquiler y 16,0 %. Centro: 950 € y 24,0 %. La renta de Chamartín es un 78 % mayor. SERPAVI y ADRH 2024, `docs/informe/cifras.md`.
[^horas]: 1.218 de 8.620 pares con el SMI (14,1 %). `app/datos/analisis.json`, estimado.
[^bono]: Bono Alquiler Joven 2022: 51.735 solicitudes y 11.477 aceptadas (22,2 %); p = 0,82 (GLM, estimado). 16 de 138 municipios quedan fuera del tope, 14 de ellos por menos de 80 € (simulación, estimado). Catálogo regional y `docs/informe/cifras.md`.
[^abono]: Fin del descuento del RDL 17/2025: de 9,23 a 32,76 €/mes por adulto; 9,30 € con el Abono Joven. BOCM-20251231-2 y -3; simulación de Kuanto, estimado.
[^ia]: `docs/kuanto-frente-a-ia.md`, prueba del 25-11-2026. Son cuatro respuestas: ilustra, no mide.
[^fuentes]: `data/README.md`: 89 filas con SHA-256.
[^harness]: `.claude/skills` (12), `.claude/agents` (8) y 16 hooks configurados en `.claude/settings.json`.
[^git]: GitHub, del 11 al 25-11-2026: 259 PR fusionados. `pytest --collect-only`: 993 tests. `docs/decisiones.md`: 131 entradas.
[^sdm]: `app/datos/sdm`: 158 + 1.512 entidades. GitHub Pages sin coste (nota metodológica, «Mantenimiento»).
