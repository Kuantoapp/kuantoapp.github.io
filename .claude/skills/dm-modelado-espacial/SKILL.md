---
description: Modelos con datos territoriales del proyecto. Imputación y predicción espacial con ML (retardos Wy sin fuga, selección de variables con validación espacial, kriging de residuos), validación aleatoria frente a bloques o buffer, intervalos conformales por grupo, equidad del error, SHAP, y regresión espacial SAR/SEM/SDM para explicar. Úsala al entrenar, validar o explicar cualquier modelo cuyas observaciones sean municipios, barrios, secciones o puntos del territorio.
when_to_use: Imputar el alquiler en municipios sin dato, predecir el alquiler a 12 meses por municipio, elegir variables para LightGBM, decidir cómo partir train y test, calcular intervalos de predicción, comprobar si los residuos tienen patrón espacial, explicar una estimación en la ficha de un municipio.
---

# Modelado espacial

Método de la asignatura *Análisis de Datos Espaciales* (UCM), actualizado con literatura de 2018–2025 (Montero et al., Meyer et al., Geerts), en Python. Parte del jurado conoce este método: las decisiones de validación se defienden en la presentación.

Requisitos previos: datos unidos por código y en EPSG:25830 (`dm-cartografia`), y una W revisada con su I de Moran (`dm-eda-espacial`).

## Regla de oro

Toda dependencia espacial que el modelo no explique acaba en los residuos. Un modelo con datos territoriales no está terminado hasta mirar la **I de Moran de sus residuos** junto a su error. Un Moran bajo con un error alto puede ser señal de variables omitidas, no de éxito.

## Primero: ¿interpolar o extrapolar?

La partición define qué pregunta responde la métrica.

| Escenario | Ejemplo | Validación |
|---|---|---|
| **A. Interpolar** (hay vecinos con dato) | Alquiler por barrio en Madrid capital | Aleatoria |
| **B. Extrapolar** (zonas sin dato cerca) | **Alquiler de municipios sin dato (corona C)** | **Bloques espaciales** (`GroupKFold`) o **buffer**. Tamaño según el correlograma o el alcance del semivariograma |

Validar el caso B al azar da un error engañosamente bajo. Ver [prediccion-y-validacion.md](referencia/prediccion-y-validacion.md).

## Flujo para predecir (imputación)

1. **Modelo de referencia** simple: media de vecinos con dato (`Wy`) o regresión lineal. El modelo final tiene que batirlo.
2. **Variables:** con significado (renta, valor catastral, tiempo a polos, accesibilidad con datos abiertos). En el caso B, **sin coordenadas ni identificadores de zona**. Elegidas con **selección hacia delante evaluada por bloques**.
3. **Retardos espaciales** `Wy` y `WX`, con `Wy` del test y de producción calculado **solo con vecinos de train**.
4. **Modelo de árboles** (LightGBM). Las redes profundas no compensan aquí.
5. **Residuos:** I de Moran. Si quedan patrones, corrige con kriging o el retardo de residuos de vecinos, validado por bloques.
6. **Intervalos conformales calibrados por grupo** (corona) o CQR; cobertura y anchura medidas por grupo.
7. **Equidad:** error y cobertura por corona y quintil de renta. Zonas fuera del **área de aplicabilidad** del modelo marcadas.
8. **Explicación:** SHAP por municipio, con los retardos agrupados.

## Para explicar (inferencia)

Regresión espacial cuando la pregunta es «¿qué explica X?» y no «¿cuánto vale X aquí?»: MCO → Moran de residuos → tests LM (Anselin) o comparación por AIC (LeSage y Pace) → SAR, SEM o SDM por máxima verosimilitud → efectos directos e indirectos. Ver [regresion-espacial.md](referencia/regresion-espacial.md). Superficies continuas: [interpolacion.md](referencia/interpolacion.md).

## Errores que invalidan un resultado

- `Wy` del test calculado con el **propio y de test**, o codificaciones por objetivo ajustadas fuera del fold.
- Validación aleatoria presentada como error del caso B.
- Coordenadas o identificadores de zona como variables en el caso B, o variables elegidas por importancia del modelo completo (RFE). El modelo memoriza y el mapa muestra artefactos.
- Intervalo con cobertura solo global: el conformal no garantiza la cobertura de cada corona.
- Error informado solo en global: suele ser peor justo donde la Administración debe actuar.
- SAR estimado por MCO, o β de SAR o SDM leído como efecto marginal.
- Cifras generadas por un LLM: los LLMs razonan mal con la localización. Todas las cifras salen del modelo.

## Python

| Tarea | Función |
|---|---|
| Bloques | `sklearn.model_selection.GroupKFold` con grupos de bloque |
| Selección espacial de variables | `sklearn.feature_selection.SequentialFeatureSelector(direction="forward", cv=folds_por_bloques)` |
| Buffer | Manual con `scipy.spatial.cKDTree` sobre coordenadas en EPSG:25830 |
| MCO con tests LM; SAR y SEM | `spreg.OLS(y, X, w=w, spat_diag=True, moran=True)`, `spreg.ML_Lag`, `spreg.ML_Error`, `spreg.GM_Lag` |
| GWR y MGWR | `mgwr.gwr.GWR`, `mgwr.gwr.MGWR` con `Sel_BW(..., multi=True)` |
| Kriging | `pykrige.ok.OrdinaryKriging`, `pykrige.uk.UniversalKriging` |
| Explicabilidad | `shap.TreeExplainer(modelo).shap_values(X)` |

En R (curso): `spatialreg::lagsarlm`, `errorsarlm`, `impacts()`, `gstat`, `spatialsample`, `CAST::ffs`, `CAST::aoa`. Comprueba la firma exacta en la versión instalada.
