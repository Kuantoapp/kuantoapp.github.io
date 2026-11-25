# Guion del informe (titulares de acción)

Paso 0 de #468. Se escribe antes que el informe: si se leen solo estos titulares, se entiende el argumento («prueba de los títulos»). Cada titular se sostiene con una cifra ya establecida del [registro de cifras](cifras.md); si no, se cae.

Revisado por `dm-abogado-del-diablo` (NO APTO en la primera versión, corregido aquí): el titular del Bono y su gráfico (la sobredispersión desmentía «la misma proporción en todas partes»), «más de un tercio» con un intervalo que baja de un tercio, el perfil del SMI, la mezcla de perfiles del cap. 9, el alcance de los cap. 4 y 5 y la lista cerrada de especificaciones de G7.

## Público y decisión

| Lector | Lo que trae | Lo que decide o se lleva |
|---|---|---|
| Jurado de DataMad | ¿Es riguroso, útil y nuevo? | Si el proyecto merece el premio |
| Técnico de la Administración (Consejería de Vivienda, CRTM, Dirección General de Juventud) | ¿Dónde actúo?, ¿qué cambio en el Bono o en el abono?, ¿qué dato me falta? | Qué revisar en la próxima convocatoria o tarifa y qué dato publicar |
| Ciudadano curioso | ¿Y yo?, ¿cómo se calcula? | Fiarse o no de la herramienta y usarla |

## Pregunta central y árbol

**¿En qué zonas de la Comunidad de Madrid puede permitirse vivir quien trabaja, y llegan allí las ayudas públicas?**

Ramas que no se solapan:

1. **El alquiler**: cuánto pesa, dónde y cómo ha cambiado (cap. 4 y 5).
2. **Los hogares**: qué le sobra a un sueldo real y cuántos inquilinos están sobrecargados (cap. 6 y 7).
3. **Las ayudas**: a quién llega el Bono y a quién deja fuera su diseño (cap. 8 y 9).
4. **El transporte**: qué pasa si se acaba el descuento del abono (cap. 10).

El tiempo de viaje entra en la rama 2 (cap. 6), porque se mide sobre cada sueldo. Cada rama responde con zonas concretas: dónde pesa más el alquiler (cap. 4), dónde no sobra nada (cap. 6), dónde el tope deja fuera (cap. 9) y qué coronas pagan más (cap. 10). Eje transversal: la calidad del dato (cap. 12), que limita qué se puede afirmar en cada rama.

## Titulares

| Cap. | Titular de acción | Gráficos |
|---|---|---|
| — | Puntos clave: seis frases, una por hallazgo, y el índice de recomendaciones | — |
| 1 | Resumen ejecutivo. Situación: el alquiler pesa sobre el sueldo de quien trabaja en Madrid. Complicación: los indicadores públicos miran medias y no dicen qué le queda a cada hogar en cada zona, ni si las ayudas llegan donde pesa más. Pregunta: dónde puede vivir quien trabaja. Respuesta: los seis hallazgos | — |
| 2 | Kuanto cruza 89 descargas de fuentes públicas en 199 zonas para responder una pregunta que ningún dato público responde solo | — |
| 3 | Lo que sobra es neto menos alquiler, transporte y cesta, y cada pieza sale de una norma o una estadística oficial | Diagrama (HTML) |
| 4 | El alquiler pesa más en el centro y el sur de la capital; en Chamartín sale más bajo porque la renta media del hogar es un 78 % más alta, no porque el alquiler sea más barato | G1, G2, G3 |
| 5 | Con los contratos declarados, el peso del alquiler apenas cambia entre 2015 y 2024 en conjunto, pero sube en 12 de los 21 distritos; quien firma hoy puede pagar bastante más | G4, G5 |
| 6 | Con el SMI no sobra nada en 18 de 158 zonas (entre 8 y 33), y vivir más lejos rara vez compensa: el ahorro llega al neto por hora en 1 de cada 7 pares | G8 |
| 7 | Uno de cada tres hogares inquilinos (36 %, entre 29 y 43 %) dedica a la vivienda más del 40 % de su renta; por zona, todavía no se puede medir | G10 |
| 8 | La proporción aceptada del Bono no depende del esfuerzo de alquiler (p = 0,82): hay más rechazos donde más se pide, y que se pida más donde el alquiler pesa más es solo un indicio | G6, G7 |
| 9 | Con un piso de 69 m² al alquiler mediano, quien cobra el SMI pasaría del tope en 16 municipios, 14 por menos de 80 €; para un joven con el sueldo mediano, cómo se definan los ingresos decide si cumple en 122 municipios o en ninguno | G11, G12 |
| 10 | Si en 2027 no se prorroga el descuento del abono, ir a trabajar costará entre 9 y 33 € más al mes | G13 |
| 11 | Recomendaciones a la Administración, ordenadas por solidez de la evidencia | — |
| 12 | Las cifras tienen error y el informe lo dibuja: el umbral de 70 alquileres declarados, clases más estrechas que el error y una validación declarada para cada resultado, también las que no pasaron | G14 |
| A–F | Anexos: métodos del Bono, IC de la mediana, fuentes y licencias, glosario, reproducibilidad, aviso sobre las estimaciones | — |

Denominadores que cambian y por qué (se explica en el cap. 2): 199 zonas en total; 158 con alquiler publicado; 157 con esfuerzo en 2024; 142 con esfuerzo en 2015 y 2024; 159 municipios con solicitudes del Bono, 134 con esfuerzo; 138 municipios en la simulación.

## Gráficos (comparación de Zelazny → forma)

| N.º | Titular | Comparación | Forma |
|---|---|---|---|
| G1 | Centro y sur de la capital, en el quintil más alto | Elementos en el espacio | Coropleta en quintiles con los distritos ampliados |
| G2 | En más de la mitad de las zonas, el error cruza un corte de quintil | Frecuencia | Franja de las 157 zonas ordenadas con IC 95 % y cortes de quintil |
| G3 | Los distritos del norte pagan alquileres altos, pero su renta media lo es más | Correlación | Alquiler mediano frente a renta del hogar con isolíneas de esfuerzo |
| G4 | Madrid entero vuelve en 2024 casi a 2015 tras el máximo de 2020 | Serie temporal | Línea sobre la banda de los distritos |
| G5 | Doce distritos suben, tres bajan y seis sin cambio claro | Elementos (cambio) | Dumbbell 2015 → 2024 coloreado por la clase frente al error de cada distrito |
| G6 | La proporción aceptada no sube ni baja con el esfuerzo | Correlación | Proporción aceptada frente al esfuerzo de 2023, punto proporcional a las solicitudes, con la media de la convocatoria |
| G7 | El efecto del esfuerzo depende de cómo se mida | Elementos | Forest plot de todas las especificaciones de `bono_inferencia.json`; la correlación parcial, fijada antes de ver los datos, en un panel aparte |
| G8 | Lo que rinde la hora extra de viaje no llega al neto por hora | Elementos | Cuartiles y mediana de lo que rinde la hora extra, con el neto por hora de cada perfil |
| G10 | El modelo por zona no pasó el control de la ECV | Elementos | Intervalo de la ECV frente a la estimación del modelo |
| G11 | Fuera del tope por poco | Elementos | Lollipop de € sobre el tope, 600 y 900 |
| G12 | Quién cumple depende del criterio y de cómo se midan los ingresos | Componentes | Matriz perfiles × criterios con recuentos |
| G13 | El coste del fin del descuento crece con la corona | Elementos | Barras de rango baja–alta por corona y joven |
| G14 | Una de cada cuatro zonas con alquiler tiene menos de 70 alquileres declarados | Frecuencia | Histograma de testigos con el umbral |

G9 (cascada de un caso con importes) se descarta: exigiría una cifra nueva calculada para el informe. El motor se explica con un diagrama sin importes en HTML.
