# Modelos predictivos espaciales y su validación

Los modelos de regresión espacial son inferenciales. Para **predecir**, el curso propone incorporar la dependencia espacial a modelos de ML (las «dos culturas» de Breiman: explicar frente a predecir).

## Procedimiento

1. Mapa y I de Moran de `y`: ¿hay dependencia?
2. Modelos sin componente espacial (lineal, kNN, random forest, XGBoost, red neuronal).
3. **I de Moran de los residuos de cada modelo.** En el ejemplo del curso con viviendas, todos los modelos de ML dejaban dependencia significativa en los residuos (I entre 0,13 y 0,28). El ML no capta solo la dependencia espacial.
4. Añade variables espaciales: `Wy` (retardo de la variable objetivo, especificación tipo SAR) y `WX` (retardos de las explicativas, tipo Durbin). También coordenadas o distancias a polos si tienen sentido.
5. Repite la validación y el Moran de residuos.
6. Ensamble de modelos si mejora, e intervalo de predicción.

## Fuga espacial: cómo calcular `Wy` en el test

`Wy` del test es la media ponderada del `y` de las observaciones de **train** que rodean a cada observación de test. **Nunca** con el `y` del propio test, que es lo que se quiere predecir.

- Construye una W de test frente a train (vecinos de cada punto de test buscados solo entre los de train).
- Lo mismo en producción: para un municipio sin dato, su `Wy` sale de los municipios con dato.
- Cualquier transformación que use `y` (medias por zona, codificación por objetivo) se ajusta dentro de cada fold, solo con train.

## Validación: primero el escenario

La partición define la pregunta que responde la métrica:

| Escenario | Pregunta | Validación |
|---|---|---|
| **A. Interpolar** | ¿Mejora la predicción si conozco valores cercanos? | **Aleatoria**. Hay vecinos de train cerca de cada test. Opcional: limitar test y predicción a la envolvente cóncava de los datos de train |
| **B. Extrapolar** | ¿Generaliza a una zona donde no hay ningún dato? | **Bloques espaciales**: divide el territorio en bloques disjuntos y usa bloques enteros como test. **Buffer**: quita de train todo lo que esté a menos de r del punto de test (`Train*(s0) = {si : d(si, s0) > r}`) |

- Los métodos que aprovechan la cercanía brillan con validación aleatoria y fallan al extrapolar. Si el uso real es el caso B, la validación aleatoria **sobreestima** el rendimiento.
- Elige el tamaño de bloque o el radio del buffer con el **alcance** del semivariograma o la distancia a la que la I de Moran deja de ser significativa (correlograma).

## Intervalos conformales

- Conformal partido sencillo: con un conjunto de calibración (o el test, en la versión más simple del curso), calcula el cuantil 95 % del error absoluto, o del relativo, y da `pred ± q95` o `pred · (1 ± q95_rel)`.
- La garantía de cobertura supone intercambiabilidad. Con dependencia espacial y caso B, **calibra con la misma partición por bloques** y comprueba la cobertura real por zonas, no solo la global.

## Para «¿Me sobra?»

- **Imputación del alquiler en municipios sin dato = caso B.** Validación por bloques (por ejemplo, `GroupKFold` con grupos de municipios contiguos o por corona) o buffer. Reporta el error de esta validación, no el de la aleatoria.
- Moran de residuos del modelo final, por municipio.
- Comparación obligatoria con un modelo de referencia simple (media de vecinos `Wy` o regresión lineal).
- Intervalo conformal calibrado por bloques y cobertura real en la tabla de resultados.
