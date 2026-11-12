# Matrices de pesos y autocorrelación espacial

## Dependencia frente a heterogeneidad

- **Autocorrelación (dependencia) espacial:** el valor en una zona depende de los valores de sus vecinas (primera ley de Tobler). Puede ser positiva (los valores parecidos se agrupan), negativa (los vecinos son distintos) o nula.
- **Heterogeneidad espacial:** la relación entre variables cambia según el sitio (parámetros no estables o heterocedasticidad). Se trata con técnicas estándar o con modelos locales (GWR); la dependencia, no.
- Las causas típicas de la autocorrelación son: límites administrativos que no siguen el fenómeno, agregación, variables omitidas con patrón espacial y efectos de contagio entre zonas.
- A diferencia de la temporal, la autocorrelación espacial va en todas las direcciones, así que hay endogeneidad. Por eso no vale MCO cuando el modelo incluye `Wy`.

## Matriz W

Matriz n×n, no aleatoria, con ceros en la diagonal. `w_ij` mide la intensidad de la relación entre i y j.

| Tipo | Cuándo | Notas |
|---|---|---|
| Contigüidad **reina** (lado o vértice) | Polígonos: municipios, barrios, secciones | La habitual. Torre = solo lado; alfil = solo vértice |
| Contigüidad de **orden 2** | Si el orden 1 deja pocos vecinos | Rara vez hace falta ir más allá |
| **k vecinos** más próximos | Puntos, o zonas de tamaños muy desiguales | Asegura que nadie quede aislado. No es simétrica |
| **Banda de distancia** (binaria o 1/d^α, α=2 en Anselin) | Puntos con densidad parecida | Elige el radio para que nadie quede sin vecinos |
| Híbrida: 1/d² dentro de un radio | Viviendas o puntos (ejemplo del curso: 500 m) | Combina cercanía e intensidad |
| Por **bloques** | Pertenencia a un grupo (comunidad, distrito) | Todos los del bloque son vecinos |

- **Normalización por filas**: cada fila suma 1, así que `Wy` es la media ponderada de los vecinos. Hace comparables las zonas con muchos y pocos vecinos.
- **W debe ser exógena:** se define con la geografía (contigüidad, distancia) o con algo que no dependa del fenómeno estudiado. No construyas W con la renta o el alquiler si luego son la variable o una explicativa del modelo.
- Ante la duda, menos orden: un modelo con vecindad de orden bajo antes que uno de orden alto.
- W es el punto débil del método: los resultados pueden cambiar con ella. Prueba al menos dos (por ejemplo, reina y k=5) y declara cuál usas.
- Revisa las **islas** (zonas sin vecinos, como enclaves o municipios separados): o les asignas vecinos (k vecinos) o las excluyes, y lo dices.

## Retardo espacial

`Wy`: para cada zona, la media ponderada de `y` en sus vecinas. Es la base del diagrama de Moran, de los modelos SAR y SDM y de las variables espaciales para ML.

## Estadísticos globales

| Estadístico | Mide | Lectura |
|---|---|---|
| **I de Moran** | Covarianza entre `y` y `Wy` | > 0 agrupamiento, < 0 dispersión, ≈ E[I] = −1/(n−1) aleatoriedad |
| **C de Geary** | Diferencias entre vecinos | < 1 positiva, > 1 negativa, ≈ 1 aleatoria |
| **G(d) de Getis-Ord** | Concentración de valores altos o bajos a distancia d | > E[G] concentración de altos, < E[G] de bajos |

Contrasta con **permutaciones** (999) en lugar de suponer normalidad. Acompaña la I de Moran con el **diagrama de dispersión de Moran** (`y` frente a `Wy`, con la pendiente igual a I).

## Estadísticos locales (LISA)

- **I de Moran local:** una por zona. Su suma es proporcional a la I global, así que mide cuánto aporta cada zona al patrón.
- Cuadrantes del diagrama de Moran: **alto-alto** y **bajo-bajo** (clústeres), **alto-bajo** y **bajo-alto** (atípicos espaciales).
- **Mapa de significación:** solo se pintan las zonas con p < 0,05 tras las permutaciones. Con muchas zonas, mencionar el problema de las comparaciones múltiples (por ejemplo, umbral más estricto o FDR).
- **Gi y Gi\* de Getis-Ord local:** puntos calientes y fríos. Gi\* incluye la propia zona, así que funciona también con zonas sin vecinos.
- Un patrón global nulo puede esconder clústeres locales. Mira siempre las dos escalas.

## Análisis bivariante

- **I de Moran bivariante:** relaciona x en cada zona con el retardo `Wy` de **otra** variable en sus vecinas. Responde a si donde hay mucho de x, alrededor hay poco o mucho de y.
- **LISA bivariante:** lo mismo zona a zona. Por ejemplo, alto-bajo = zona con x alto rodeada de y bajo (Moura y Fonseca, 2020, relacionan vegetación y renta así).
- Ojo: no controla la autocorrelación de x consigo misma. Es exploratorio y no sustituye a un modelo.

## Para este proyecto

- **Focalizar el Bono Alquiler Joven:** LISA bivariante entre la sobrecarga y la tasa de solicitudes aceptadas del Bono por municipio. Los clústeres de mucha sobrecarga con poca ayuda alrededor son exactamente la decisión 6.2.1 de la ficha.

- Sobrecarga por sección censal: LISA para localizar clústeres alto-alto, que son las zonas a señalar a la Administración.
- Variable «lo que sobra» por municipio: I de Moran para afirmar o descartar que «vivir lejos no compensa» tiene patrón territorial.
