# Interpretar resultados de modelos espaciales y decidir el siguiente paso

Cada salida se lee con cuatro preguntas: **qué dice**, **si es fiable**, **si es coherente con la teoría y con lo anterior**, y **qué ajuste implica**. Un número sin esa lectura no se da por bueno.

## Qué esperar según la teoría (escríbelo antes de ejecutar)

- Si el ESDA dio una I de Moran fuerte en `y`, un modelo sin estructura espacial dejará residuos con I > 0, y uno con estructura espacial debería reducirla.
- Si la dependencia viene de variables no observadas que comparten los vecinos, ganará el SEM; si viene de contagio real entre zonas, el SAR. La teoría del fenómeno dice cuál es más plausible.
- La validación por bloques dará más error que la aleatoria, y la brecha crecerá cuanto más dependa el modelo de la cercanía.
- Añadir variables con significado reduce el error y el Moran de residuos a la vez; añadir coordenadas reduce el error aleatorio pero no el de bloques.
- La cobertura de un intervalo calibrado coincide con la nominal en global y se degrada en los grupos con menos datos.
- El signo de cada variable es el que predice la teoría del fenómeno (escríbelo por variable).

Si lo obtenido se aparta de esto, el bucle de contraste de la skill decide qué comprobar y qué ajustar.

## I de Moran de los residuos

| Resultado | Lectura | Siguiente paso |
|---|---|---|
| I > 0 y significativa | Queda dependencia sin explicar: faltan variables con patrón espacial o falta estructura espacial | Añadir variables con significado; si no hay, `Wy`/`WX`, deriva espacial o kriging de residuos. Una cosa cada vez, validada por bloques |
| I ≈ 0, no significativa, **error bajo** | El modelo recoge el espacio | Comprobar con una segunda W antes de cerrarlo |
| I ≈ 0, **error alto** | Probablemente variables omitidas que cambian mucho entre vecinos, no éxito espacial | Buscar variables, revisar calidad del dato; no añadir más estructura espacial |
| I < 0 y significativa | Sobrecorrección (por ejemplo, `Wy` demasiado fuerte o kriging que sobreajusta) o artefacto de la W | Quitar el último componente espacial añadido; probar otra W |
| Cambia de signo o de significación con otra W | Resultado frágil | Informar de ambas; no basar decisiones en él |

Mira también el **mapa de residuos**: bandas, bloques o franjas rectas indican artefactos por coordenadas o por una variable mal construida.

## Tests LM (regresión espacial)

- Sigue la regla de Anselin (ver [regresion-espacial.md](regresion-espacial.md)). Si los robustos tampoco distinguen, prueba SAR, SEM y SDM y elige por **verosimilitud/AIC y Moran de residuos**, no por el R².
- **ρ (SAR)** pequeño (< 0,2) y no significativo: no hay contagio en la variable; el SAR sobra. **λ (SEM)** alto: la dependencia está en lo no observado; prioriza buscar variables.
- Coherencia teórica: ¿tiene sentido que el fenómeno se contagie entre vecinos (SAR) o que comparta factores no medidos (SEM)? Si el test elige uno sin explicación teórica, dilo.
- Efectos: en SAR y SDM, informa de efectos **directo, indirecto y total**. Un efecto indirecto mayor que el directo merece una explicación (o es un problema de W).

## Semivariograma y kriging

| Lectura | Implicación |
|---|---|
| Pepita / meseta > 0,5 | Más de la mitad de la variación es de microescala o error: el kriging aportará poco |
| Alcance | Distancia hasta la que hay dependencia: **tamaño mínimo de bloque o radio del buffer** en la validación |
| Sin meseta | Hay tendencia: quitarla con regresión y modelar residuos |
| Ajuste teórico malo en distancias cortas | Las predicciones locales no son fiables; probar otro modelo (exponencial frente a esférico) o más datos |
| Semivariogramas direccionales distintos | Anisotropía: usar un modelo anisótropo o variables que la expliquen (ejes de transporte) |
| Varianza de kriging alta lejos de los datos | Esperado; úsala para ensanchar intervalos y marcar zonas poco fiables |

## Métricas de validación

- **Siempre frente a los modelos de referencia.** Si no se bate al simple con la misma validación, el modelo no aporta: parar y revisar variables, no ajustar hiperparámetros.
- **Brecha entre validación aleatoria y por bloques.** Pequeña: el modelo generaliza. Grande: depende de la cercanía (interpola). Si el uso real es extrapolar, la cifra válida es la de bloques.
- **Dispersión entre folds.** Si un bloque tiene un error muy distinto, mira qué zona es: suele ser una región con características fuera del rango de entrenamiento (ver área de aplicabilidad).
- **Error relativo y absoluto.** Con variables asimétricas, el RMSE lo dominan las zonas de valores altos; informa también del error relativo (MAPE o error en logaritmos).
- **Mejoras pequeñas** (< 1–2 %) con más complejidad no compensan si cuestan interpretabilidad o validación; menos aún si caen dentro de la variabilidad entre folds.

## Intervalos

| Resultado | Lectura | Ajuste |
|---|---|---|
| Cobertura global < nominal | Intervalo optimista | Calibrar con la validación por bloques; revisar intercambiabilidad |
| Cobertura bien en global, mal en un grupo | El conformal no garantiza cobertura condicional | Mondrian por grupo o CQR |
| Cobertura > nominal y anchura enorme | Intervalo inútil | CQR, modelar en logaritmos, mejores variables |
| Valor real casi siempre en un lado | Sesgo del modelo en ese grupo | Revisar el modelo, no solo el intervalo |

## Explicación (SHAP, GWR)

- **Signos contra la teoría** (por ejemplo, más renta → menos precio) son una señal de alarma: colinealidad, fuga o variable mal construida. No se explican a posteriori.
- **Si `Wy` o las coordenadas dominan** la importancia, el modelo está interpolando: aceptable en el caso A, sospechoso en el B.
- **GWR / MGWR:** anchos de banda muy pequeños o coeficientes que cambian de signo de una zona a la vecina suelen ser sobreajuste o colinealidad local, no heterogeneidad real.

## Área de aplicabilidad

Si un porcentaje alto de las zonas a predecir cae fuera, el modelo no debe usarse para ellas: o se buscan variables que las acerquen al entrenamiento, o se presentan como no estimables.

## Registrar la decisión

Cada ajuste que cambie el modelo, la validación o la interpretación se anota en `docs/decisiones.md` con el resultado que lo motivó.
