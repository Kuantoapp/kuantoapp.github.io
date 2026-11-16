---
description: "Estima cuánto explica una variable de otra y predice con datos territoriales, contrastando cada resultado con la teoría: correlación parcial o regresión (MCO, SAR, SEM, SDM) entre indicadores por municipio o zona controlando por otras variables, conteos o tasas con GLM (binomial negativa con offset, binomial) y sus residuos; imputación con Wy sin fuga, validación espacial, kriging, intervalos y SHAP. No prepara geometrías (dm-cartografia) ni explora el patrón (dm-eda-espacial)."
when_to_use: "¿X explica Y entre municipios controlando por la renta?, correlación parcial con datos por zona, ¿es significativa esta relación entre municipios?, ¿MCO, SEM o SAR?, GLM binomial negativa con offset, ¿mi modelo tiene fuga?, spatial cross-validation, calcular intervalos, explicar una predicción."
---

# Modelado espacial

Método de la asignatura *Análisis de Datos Espaciales* (UCM), actualizado con literatura de 2018–2025 (Montero et al., Meyer et al., Geerts), en Python.

## Antes de empezar: conectar con el desarrollo del proyecto

Esta skill es general. Lo concreto (variable, unidad, uso, datos) sale del estado actual del proyecto, que cambia; no lo supongas ni lo copies de los ejemplos.

1. **Qué se busca:** lee `docs/decisiones.md` (idea elegida, variable objetivo, unidad territorial, uso del resultado) y, si hace falta, la ficha vigente en `ideas/`. Las fichas son borradores: manda lo decidido.
2. **Con qué datos:** lee `data/README.md` (fuentes, años, cobertura, licencias). Comprueba que los datos que vas a usar están ahí y en `data/`.
3. **Qué hay ya hecho:** busca y reutiliza lo existente antes de escribir nada:
   `grep -rnE "to_crs|libpysal|weights|GroupKFold|esda|spreg|conformal" src notebooks`.
   Si ya hay una W, una partición por bloques o una función de carga, úsala; no la dupliques.
4. **Qué falta por decidir:** si el uso (interpolar o extrapolar, explicar o predecir) o la variable no están decididos, **pregunta** a la persona; si tienes que suponer, escribe el supuesto en el código y en `docs/decisiones.md`.
5. Requisitos previos: datos unidos por código y con el CRS correcto (`dm-cartografia`), y una W revisada con su I de Moran (`dm-eda-espacial`).

## Regla de oro

Toda dependencia espacial que el modelo no explique acaba en los residuos. Un modelo con datos territoriales no está terminado hasta mirar la **I de Moran de sus residuos** junto a su error. Un Moran bajo con un error alto puede ser señal de variables omitidas, no de éxito.

## Primero: ¿interpolar o extrapolar?

La partición define qué pregunta responde la métrica, y la decide **el uso real del modelo**, no la comodidad.

| Escenario | Cuándo | Validación |
|---|---|---|
| **A. Interpolar** | Las zonas a predecir tienen vecinos con dato | Aleatoria |
| **B. Extrapolar** | Las zonas a predecir no tienen dato cerca (por ejemplo, completar zonas sin publicar) | **Bloques espaciales** (`GroupKFold`) o **buffer**, con tamaño según el correlograma o el alcance del semivariograma |

Validar el caso B al azar da un error engañosamente bajo. Ver [prediccion-y-validacion.md](referencia/prediccion-y-validacion.md).

## Flujo para predecir

1. **Modelos de referencia:** uno simple (media de vecinos con dato `Wy`, o lineal) y uno fuerte e interpretable (**GAM con deriva espacial**, el mejor en el estudio de Madrid de Montero et al.). Cualquier modelo más complejo tiene que batir a los dos con la misma validación.
2. **Variables** con significado para el fenómeno. En el caso B, **sin coordenadas ni identificadores de zona**. Elegidas con **selección hacia delante evaluada por bloques**.
3. **Retardos espaciales** `Wy` y `WX`, con `Wy` del test y de producción calculado **solo con vecinos de train**.
4. **Modelo de árboles** (por ejemplo, LightGBM) como punto de partida con datos tabulares; las redes profundas no suelen compensar.
5. **Residuos:** I de Moran y mapa. Si quedan patrones, una corrección cada vez (kriging o retardo de residuos), validada por bloques. **Una sola forma de recoger el espacio suele bastar.**
6. **Intervalos** conformales calibrados por grupo de zonas (Mondrian) o CQR; en logaritmos si la variable es positiva y asimétrica. Tabla de cobertura, anchura (MPIW o Winkler) y asimetría por grupo y por densidad de datos.
7. **Equidad:** error y cobertura por tipo de zona. Zonas fuera del **área de aplicabilidad** marcadas.
8. **Explicación:** SHAP por zona, con los retardos agrupados.

## Para explicar (inferencia)

Correlación parcial y GLM de conteos o tasas por zona: [correlacion-y-glm.md](referencia/correlacion-y-glm.md). Regresión espacial cuando la pregunta es «¿qué explica X?» y no «¿cuánto vale X aquí?»: MCO → Moran de residuos → tests LM (Anselin) o comparación por AIC (LeSage y Pace) → SAR, SEM o SDM por máxima verosimilitud → efectos directos e indirectos. Ver [regresion-espacial.md](referencia/regresion-espacial.md). Superficies continuas: [interpolacion.md](referencia/interpolacion.md).

## Contrastar cada resultado con la teoría

Un resultado solo se acepta cuando **coincide con lo que la teoría dice que debe salir**, o cuando la diferencia está explicada y comprobada. El bucle es:

1. **Antes de ejecutar**, escribe qué esperas según la teoría y el ESDA (signo, rango, orden de magnitud, qué modelo debería ganar).
2. **Ejecuta** y compara con lo esperado y con los **valores de control** de abajo.
3. **Si no cuadra**, no lo expliques a posteriori: diagnostica la causa (dato, unión, fuga, W, partición, especificación) con una comprobación concreta.
4. **Ajusta** solo lo que el diagnóstico señala (un cambio cada vez) y vuelve al paso 2.
5. **Corrobora** con una segunda vía independiente: otra W, otra partición o semilla, otro método (LM y AIC; Moran y mapa de residuos; validación aleatoria y por bloques).
6. **Acepta** solo si cuadra y es estable. Si no se resuelve, se informa como limitación, no se presenta como resultado.
7. **Registra** en `docs/decisiones.md` lo que se ajustó y por qué.

Valores de control que la teoría exige (con W normalizada por filas):

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| ρ y λ | Entre −1 y 1 | Error de W o de estimación |
| Efecto total en SAR | β / (1 − ρ); el directo, algo mayor que β si ρ > 0 | Cálculo de efectos erróneo |
| Media de residuos | ≈ 0, también por grupo de zonas | Sesgo sistemático en ese grupo |
| Error por bloques frente a aleatorio | Mayor o igual | Si es menor: fuga, partición mal hecha o bloques que no separan |
| Modelo frente a referencias | Mejor, con la misma validación | No aporta: no se presenta |
| Cobertura del intervalo | ≈ nominal, en global y por grupo | Recalibrar (Mondrian, CQR, bloques) |
| Semivariograma | Pepita ≥ 0; meseta ≈ varianza del dato; alcance menor que la extensión del territorio | Modelo de variograma mal ajustado o tendencia |
| Varianza de kriging | Mínima junto a los datos, crece al alejarse | Error de ajuste o de coordenadas |
| Signos de SHAP o coeficientes | Los que predice la teoría del fenómeno | Investigar colinealidad, fuga o variable mal construida |

Guía completa de lectura y de qué ajustar: [interpretar-resultados.md](referencia/interpretar-resultados.md).

## Al terminar: dejar el trabajo conectado

- La lógica reutilizable va a `src/` (no se queda en un notebook) con un test pequeño de lo no trivial, según `AGENTS.md`.
- Las métricas finales se guardan junto con la validación que las produjo (partición, W, semilla).
- La decisión de modelo, validación y supuestos, en `docs/decisiones.md`.
- Antes de dar el resultado por bueno o de abrir el PR, pide la revisión de `dm-revisor-espacial`.

## Errores que invalidan un resultado

- AIC de spreg: `ML_Error` no cuenta λ y `ML_Lag` sí cuenta ρ; para comparar se calcula igual, `2·len(betas) − 2·logll`.
- La regla de elección de modelo y la de conclusión se fijan antes de ver el dato, y se escriben.
- Dos especificaciones se comparan sobre la misma submuestra; si cambian la muestra y el denominador a la vez, no se atribuye el efecto.
- Que añadir WX (SLX o SDEM) baje la significación no prueba inestabilidad si el AIC prefiere el modelo sin WX: puede ser colinealidad entre X y WX.
- Salidas generadas (JSON, log) con cifras y conclusiones de la regla; la interpretación va en el texto revisado, que no se recalcula.
- `Wy` del test calculado con el **propio y de test**, o codificaciones por objetivo ajustadas fuera del fold.
- Validación aleatoria presentada como error del caso B.
- Coordenadas o identificadores de zona como variables en el caso B, o variables elegidas por importancia del modelo completo (RFE). El modelo memoriza y el mapa muestra artefactos.
- No batir a los modelos de referencia y presentar el modelo igualmente.
- Intervalo con cobertura solo global: el conformal no garantiza la de cada grupo.
- Error informado solo en global: suele ser peor donde hay menos datos.
- SAR estimado por MCO, o β de SAR o SDM leído como efecto marginal.
- Signos contrarios a la teoría explicados a posteriori en lugar de investigados.
- Cifras generadas por un LLM: razonan mal con la localización. Todas las cifras salen del modelo.

## Python

| Tarea | Función |
|---|---|
| Bloques | `sklearn.model_selection.GroupKFold` con grupos de bloque |
| Selección espacial de variables | `sklearn.feature_selection.SequentialFeatureSelector(direction="forward", cv=folds_por_bloques)` |
| Buffer | Manual con `scipy.spatial.cKDTree` sobre coordenadas en metros |
| MCO con tests LM; SAR y SEM | `spreg.OLS(y, X, w=w, spat_diag=True, moran=True)`, `spreg.ML_Lag`, `spreg.ML_Error`, `spreg.GM_Lag` |
| GWR y MGWR | `mgwr.gwr.GWR`, `mgwr.gwr.MGWR` con `Sel_BW(..., multi=True)` |
| Kriging | `pykrige.ok.OrdinaryKriging`, `pykrige.uk.UniversalKriging` |
| GAM con deriva espacial | `pygam.LinearGAM(s(0) + s(1) + te(i_x, i_y))` |
| Explicabilidad | `shap.TreeExplainer(modelo).shap_values(X)` |

En R (curso): `spatialreg::lagsarlm`, `errorsarlm`, `impacts()`, `gstat`, `spatialsample`, `CAST::ffs`, `CAST::aoa`. Comprueba la firma exacta en la versión instalada.
