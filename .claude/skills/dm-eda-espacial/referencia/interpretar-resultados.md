# Interpretar resultados exploratorios y decidir el siguiente paso

Cada salida se lee con cuatro preguntas: **qué dice**, **si es fiable**, **si es coherente con la teoría y con lo anterior**, y **qué implica para el análisis siguiente**.

## I de Moran global

- **Compara con E[I] = −1/(n−1)**, no con 0. Con pocas zonas, E[I] se aleja de 0.
- **Significación por permutaciones** (pseudo-p con 999). Con 999 permutaciones el p mínimo es 0,001: no informes de p más pequeños.
- **Magnitud orientativa** (con W normalizada): < 0,1 débil; 0,1–0,3 moderada; > 0,3 fuerte. Es una guía, no un umbral.
- **Siempre con una segunda W.** Si la conclusión cambia, el patrón depende de cómo se define la vecindad: dilo y no lo uses para decidir.
- **Diagrama de Moran:** busca puntos aislados que tiren de la pendiente (apalancamiento). Si al quitarlos I cambia mucho, el «patrón» son unas pocas zonas.
- **I negativa** en datos socioeconómicos es rara: sospecha de la W (por ejemplo, k vecinos que saltan entre zonas muy distintas) o de una variable que es un cociente con denominador muy variable.

**Qué implica:** I alta y robusta → el modelo posterior necesitará estructura espacial y validación espacial; I nula → la validación aleatoria es aceptable y un modelo sin estructura espacial puede bastar.

## LISA y Getis-Ord

- Solo cuentan las zonas **significativas tras corregir** comparaciones múltiples (FDR o umbral más estricto). Sin corregir, aparecerán clústeres por azar.
- **Coherencia con el global:** muchos clústeres significativos con un Moran global nulo indican heterogeneidad (el patrón es local), no un error.
- **Clústeres de una sola zona** o en bordes del mapa son poco fiables (pocos vecinos).
- Atípicos alto-bajo y bajo-alto: revisa primero si son errores de dato.
- Gi\* da calor o frío respecto a la media global; LISA, semejanza con los vecinos. Si discrepan, explica por qué antes de elegir uno.

## Moran y LISA bivariantes

Una asociación bivariante puede venir solo de que cada variable tiene su propio patrón espacial. Antes de afirmar relación, mira el Moran univariante de cada una. Exploratorio, nunca causal.

## Tasas suavizadas

Compara rankings antes y después de suavizar. Las zonas que más se mueven son las de menor población: no deben aparecer como extremos en ningún mensaje.

## Correlograma

La distancia u orden de vecindad a la que la I deja de ser significativa es la **escala del patrón**. Se usa como tamaño mínimo de bloque en la validación espacial. Si nunca deja de serlo, hay tendencia: el modelo debe incluirla.

## Patrones de puntos (G, K, L)

- La curva **fuera de la envolvente** de simulación indica agrupación (por encima) o regularidad (por debajo) **a esa escala de distancia**. Dentro de la envolvente, no hay evidencia.
- Agrupación frente a aleatoriedad completa en datos urbanos es esperable; la conclusión válida sale de la versión **no homogénea** (con la población como referencia).

## Registrar la decisión

Las decisiones que salgan del ESDA (W elegida, escala, variables a suavizar, familia de modelo) se anotan en `docs/decisiones.md` con el resultado que las justifica.
