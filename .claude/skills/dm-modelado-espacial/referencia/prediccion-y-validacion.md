# Modelos predictivos espaciales y su validación

Los modelos de regresión espacial son inferenciales. Para **predecir**, el curso propone incorporar la dependencia espacial a modelos de ML (las «dos culturas» de Breiman: explicar frente a predecir).

## Procedimiento

1. Mapa y I de Moran de `y`: ¿hay dependencia?
2. Modelos sin componente espacial (lineal, kNN, random forest, XGBoost, red neuronal).
3. **I de Moran de los residuos de cada modelo.** En el ejemplo del curso con viviendas, todos los modelos de ML dejaban dependencia significativa en los residuos (I entre 0,13 y 0,28). El ML no capta solo la dependencia espacial.
4. Añade variables espaciales: `Wy` (retardo de la variable objetivo, especificación tipo SAR) y `WX` (retardos de las explicativas, tipo Durbin). También coordenadas o distancias a polos si tienen sentido.
5. Repite la validación y el Moran de residuos.
6. Ensamble de modelos si mejora, e intervalo de predicción.

## Qué funciona mejor, según la literatura reciente

- **Árboles sí, redes profundas no.** En la tesis de Geerts (KU Leuven, 2025), los modelos de árboles (LightGBM, CatBoost, RF) siguen siendo lo mejor para valorar viviendas. Las redes de grafos (GNN) no superan a un árbol que tenga las coordenadas. El aprendizaje profundo solo compensa si los árboles no pueden con los datos. Es un argumento para no complicar la imputación.
- **Distancias derivadas ≈ coordenadas.** En la misma tesis, LightGBM rinde algo mejor con un buen conjunto de distancias derivadas (43 distancias a ciudades, autovías, servicios…) que con las coordenadas en bruto. Lo que peor funciona es usar el municipio como variable ficticia más la distancia al centro.
- **Kriging de residuos (regresión-kriging).** Se entrena el modelo de ML, se interpolan sus residuos con kriging y se suman a la predicción. Mejora la precisión en Varsovia (ML + kriging ordinario de residuos), en Acapulco (RF + kriging) y en la valoración catastral de suelo de Primorie (regresión lineal + kriging). Con zonas en lugar de puntos, la alternativa equivalente es corregir con el retardo `W·residuo` de los vecinos con dato. **Valídalo por bloques**: si no, el kriging de residuos parece mejor de lo que es.
- **Pérdida espacial en boosting (MI-GBT).** Geerts propone sumar al error cuadrático una penalización por la autocorrelación local (I de Moran local) de los residuos, para reducir a la vez el error y el patrón espacial que queda. Hay implementación en Python. Es una opción innovadora si los retardos `Wy` no bastan, no un punto de partida.
- **Ojo al leer la I de Moran de los residuos.** Si los residuos no tienen patrón espacial pero el error es grande, puede ser por **variables omitidas** que varían mucho entre vecinos, no porque el modelo haya captado bien el espacio. Mira siempre el error junto al Moran.

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

## Selección de variables con validación espacial

Meyer, Reudenbach, Wöllauer y Nauss (2019) muestran que la validación espacial **no basta**: las variables muy autocorrelacionadas (coordenadas, distancias a las esquinas del área, altitud) dejan que el modelo **reproduzca los datos de entrenamiento** sin saber predecir zonas nuevas. El síntoma es visual: el mapa de predicciones tiene artefactos en bandas o bloques que siguen a esas variables.

- **Selección hacia delante con validación espacial** (*spatial forward feature selection*): se empieza con los mejores pares de variables y se añaden de una en una, **evaluando cada modelo con validación por bloques**. Se queda solo lo que mejora la predicción espacial. En R es `CAST::ffs`. En Python, `SequentialFeatureSelector` de scikit-learn con `cv` = los folds de `GroupKFold` por bloques.
- La **eliminación recursiva** (RFE) con importancias del modelo completo no detecta el problema: la importancia de las coordenadas sale alta precisamente porque sobreajustan.
- **Cómo encaja con Geerts (2025)**, que encuentra útiles las coordenadas: él trabaja con transacciones densas (caso A, interpolar). Para imputar municipios sin dato (caso B), no metas coordenadas ni identificadores de zona en bruto. Usa variables con significado (renta, tiempo a polos, valor catastral) y deja que la selección espacial decida.
- **Área de aplicabilidad** (Meyer y Pebesma, 2021; `CAST::aoa`): para cada zona a predecir se mide cuánto se parecen sus variables a las de entrenamiento. Las que caen fuera se marcan como «fuera del ámbito del modelo». Para la corona C es un buen complemento de la marca «estimado»: hay estimaciones con modelo y estimaciones fuera de su ámbito.

Otras técnicas de selección revisadas y descartadas para este proyecto:
- **Boosting geoaditivo** (Kneib, Hothorn y Tutz, 2009; R `mboost`): elige entre efectos lineales, suaves, espaciales y coeficientes variables. Elegante y cercano a los P-splines de Montero et al., pero sin equivalente directo en Python.
- **Penalización en modelos mixtos** (SCAD, LASSO adaptativo).
- **PCA** sobre indicadores socioeconómicos: reduce la colinealidad, pero cada componente mezcla variables y se pierde la explicación en la ficha de cada municipio.

## Intervalos conformales

- Conformal partido sencillo: con un conjunto de calibración (o el test, en la versión más simple del curso), calcula el cuantil 95 % del error absoluto, o del relativo, y da `pred ± q95` o `pred · (1 ± q95_rel)`.
- La garantía de cobertura supone intercambiabilidad. Con dependencia espacial y caso B, **calibra con la misma partición por bloques** y comprueba la cobertura real por zonas, no solo la global.
- **El conformal garantiza la cobertura media, no la de cada grupo.** Geerts (2025, cap. 7) compara métodos de incertidumbre en tres mercados: los conformales dan intervalos estrechos pero pierden cobertura en clases de precio extremas y en atípicos geográficos. Si importa la cobertura por corona, calibra **por grupos** (conformal de Mondrian: un cuantil por corona) o usa **regresión cuantílica conformalizada** (CQR), cuyo ancho se adapta a cada zona.
- Mide cuatro cosas: cobertura, anchura media del intervalo, asimetría y cómo varían ambas entre grupos. Un intervalo que cubre el 90 % pero es enorme no sirve para la demo.

## Variables de accesibilidad con datos abiertos

Trindade Neves, Aparicio y de Castro Neto (2024, Lisboa) reducen un 8 % el error de un XGBoost con variables de datos abiertos: **distancia al punto de interés más cercano** (metro, tren, salud, colegios, parques) y **número de puntos de interés en radios** de 75, 250 y 500 m alrededor de cada vivienda.

- Calcula las distancias en EPSG:25830 o, mejor, el **tiempo en red** (la ficha ya tiene matrices de tiempo GTFS).
- **Sesgo geográfico del dato abierto:** los propios autores avisan de que los puntos de interés están más completos en zonas urbanas que en periurbanas. En la corona C, «no hay farmacia a menos de 1 km» puede ser falta de dato. Comprueba la cobertura de cada capa por corona antes de usarla.
- Su validación es una partición aleatoria 80/20. Con la localización exacta como variable, eso es el caso A. **No sirve como referencia de error para extrapolar.** Es un buen argumento para justificar la validación por bloques ante el jurado.

## Explicabilidad

- **SHAP** (`shap.TreeExplainer` en modelos de árboles) da la contribución de cada variable a cada predicción. Es útil para la ficha de un municipio estimado: «se estima alto sobre todo por su renta y su tiempo a Madrid».
- Con retardos espaciales (`Wy`, `WX`), SHAP reparte entre variables correlacionadas y la contribución del «vecindario» puede quedar repartida. Agrupa los retardos al interpretar e informa de su peso conjunto.
- Mapa de los valores SHAP de una variable por municipio: muestra dónde pesa más, una forma visual de **heterogeneidad espacial**.
- Para heterogeneidad con inferencia: GWR o **MGWR** (GWR multiescala, un ancho de banda por variable: unas relaciones son locales y otras regionales).

## Equidad territorial del error

Los modelos con datos públicos fallan más donde hay menos dato, y eso suele coincidir con las zonas de menor renta o más rurales. Antes de publicar una estimación:

- error y cobertura del intervalo **por corona y por quintil de renta**, no solo globales;
- si el error es mayor en las zonas que la Administración debería priorizar, se dice y se ensancha el intervalo.

**LLMs y cifras:** en Geerts (2025, cap. 8), los LLMs con diez ejemplos cercanos estiman precios de forma razonable, pero razonan mal con la localización y dan intervalos poco fiables. Refuerza la regla del asistente: las cifras salen siempre del modelo y del MCP, nunca del LLM.

Las decisiones automatizadas con datos de localización que afecten a personas son de alto riesgo en el marco europeo. Este proyecto **simula** criterios de ayuda y no decide por nadie, y así debe decirse.

## Para «¿Me sobra?»

- **Imputación del alquiler en municipios sin dato = caso B.** Validación por bloques (por ejemplo, `GroupKFold` con grupos de municipios contiguos o por corona) o buffer. Reporta el error de esta validación, no el de la aleatoria.
- Moran de residuos del modelo final, por municipio.
- Comparación obligatoria con un modelo de referencia simple (media de vecinos `Wy` o regresión lineal).
- Intervalo conformal calibrado por bloques y cobertura real en la tabla de resultados.
