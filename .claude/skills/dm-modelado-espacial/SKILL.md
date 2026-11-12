---
description: Entrenar, validar, interpretar y ajustar modelos con datos territoriales. Predicción o imputación de zonas sin dato con ML y retardos espaciales (Wy sin fuga), validación aleatoria frente a espacial (bloques, buffer), selección de variables con validación espacial, kriging y regresión-kriging, intervalos conformales por grupo, equidad del error, SHAP, y regresión espacial SAR/SEM/SDM con tests LM. Úsala al partir train/test, elegir variables o modelo, leer residuos, variogramas o métricas y decidir qué ajustar. No es para preparar geometrías (dm-cartografia) ni para la exploración inicial (dm-eda-espacial).
when_to_use: Imputar o predecir un valor por zona, spatial cross-validation, ¿mi modelo tiene fuga?, ¿los residuos tienen patrón?, ¿SAR o SEM?, ¿cómo leo este variograma?, ¿por qué la validación por bloques da peor que la aleatoria?, calcular o evaluar intervalos de predicción, explicar una predicción por zona.
---

# Modelado espacial

Método de la asignatura *Análisis de Datos Espaciales* (UCM), actualizado con literatura de 2018–2025 (Montero et al., Meyer et al., Geerts), en Python.

**Contexto del proyecto:** las variables, unidades territoriales y usos concretos los decide el equipo y cambian con el desarrollo. Consúltalos en `docs/decisiones.md` y en `ideas/`; no los supongas. Los ejemplos de esta skill son orientativos.

Requisitos previos: datos unidos por código y con el CRS correcto (`dm-cartografia`), y una W revisada con su I de Moran (`dm-eda-espacial`).

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

Regresión espacial cuando la pregunta es «¿qué explica X?» y no «¿cuánto vale X aquí?»: MCO → Moran de residuos → tests LM (Anselin) o comparación por AIC (LeSage y Pace) → SAR, SEM o SDM por máxima verosimilitud → efectos directos e indirectos. Ver [regresion-espacial.md](referencia/regresion-espacial.md). Superficies continuas: [interpolacion.md](referencia/interpolacion.md).

## Razonar cada resultado

Ningún resultado se da por bueno sin estos cinco pasos:

1. **Qué dice:** el valor, su significación o su incertidumbre, en una frase.
2. **Si es fiable:** ¿se mantiene con otra W, otra partición, otra semilla, otro bloque?
3. **Si es coherente:** con la teoría (signos, magnitudes), con el ESDA previo y con el uso del modelo.
4. **Qué ajuste implica:** el siguiente paso concreto, o «no tocar», con su motivo.
5. **Registrarlo** en `docs/decisiones.md` si cambia el modelo, la validación o la interpretación.

Guía de lectura de residuos, tests LM, variogramas, métricas, intervalos y SHAP: [interpretar-resultados.md](referencia/interpretar-resultados.md).

## Errores que invalidan un resultado

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
