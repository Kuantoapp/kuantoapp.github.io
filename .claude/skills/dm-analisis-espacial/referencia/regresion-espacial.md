# Regresión espacial (modelos inferenciales)

Sirven para **explicar** y contrastar hipótesis sobre parámetros, no están pensados para predecir. Para predecir, ver [prediccion-y-validacion.md](prediccion-y-validacion.md).

## Procedimiento

1. Comprueba que `y` tiene autocorrelación (I de Moran).
2. Estima el modelo **sin** componente espacial (MCO) y revisa la heterocedasticidad.
3. I de Moran **sobre los residuos**. Si no es significativa, has terminado.
4. Si lo es, decide si la dependencia es:
   - **sustantiva:** falta `Wy` o `WX` en el modelo, y se ha ido al error → se añade el retardo;
   - **residual:** variables omitidas con patrón espacial o errores de medida → se modeliza el error.
5. Re-estima y vuelve al paso 3 hasta que los residuos sean ruido blanco espacial.

## Especificaciones

| Modelo | Ecuación | Cuándo |
|---|---|---|
| **SAR / SLM** (retardo) | y = ρWy + Xβ + u | Contagio en la propia variable |
| **SLX** | y = Xβ + WXγ + u | Influyen las características de los vecinos |
| **SDM** (Durbin) | y = ρWy + Xβ + WXγ + u | Ambos. Anida SAR y SLX |
| **SEM** (error) | y = Xβ + u, u = λWu + ε | Dependencia residual (variables omitidas) |
| **SDEM** | y = Xβ + WXγ + u, u = λWu + ε | SLX con error espacial |
| **SAC / Kelejian-Prucha** | y = ρW₁y + Xβ + u, u = λW₂u + ε | Retardo y error |
| **GNS / Manski** | Todo lo anterior | Anida a los demás (ρ, λ, γ = 0) |
| **SARMA** | Como SAC con error de media móvil | Variante del SAC |

Ojo: en SEM y SDEM el error es **u = λWu + ε** (la tabla 1 del artículo de Montero et al. tenía una errata en estas ecuaciones, corregida en su fe de erratas).

**Estimación:** con `Wy` en el modelo, MCO da estimaciones sesgadas e inconsistentes; usa máxima verosimilitud o MC2E/GMM con `WX`, `W²X` como instrumentos. En SEM, MCO es insesgado pero ineficiente: hay que corregir la matriz de varianzas.

## Cómo elegir

- **Enfoque de Anselin (de lo específico a lo general):** tests de multiplicadores de Lagrange sobre el MCO.
  - Ni LM-LAG ni LM-ERR significativos → MCO.
  - Solo LM-LAG → SAR. Solo LM-ERR → SEM.
  - Ambos → mira las versiones **robustas** (RLM-LAG, RLM-ERR) y quédate con la significativa. Si las dos lo son, la de mayor estadístico, o SAC.
  - LM-ERR-HET si hay heterocedasticidad.
- **Enfoque de LeSage y Pace (de lo general a lo específico):** prueba varias especificaciones (empezando por SDM), quédate con la que deja residuos sin dependencia y desempata con AIC o BIC.

## Interpretación: efectos directos e indirectos

En SAR y SDM un cambio en X de una zona afecta a esa zona (**efecto directo**) y, a través del multiplicador (I − ρW)⁻¹, a todas las demás (**efecto indirecto** o *spillover*). **β no es el efecto marginal.** Informa del efecto directo, el indirecto y el total.

## Precio de la vivienda en Madrid (Montero, Mínguez y Fernández-Avilés, 2018)

*Housing price prediction: parametric versus semi-parametric spatial hedonic models*, Journal of Geographical Systems 20:27–55. Usa unas 10.500 viviendas de Madrid y compara modelos hedónicos espaciales paramétricos (SAR, SEM, SDM, SDEM…) con semiparamétricos: splines penalizados (P-splines) para tendencias espaciales suaves y relaciones no lineales, estimados como modelos mixtos. Evalúa fuera de muestra. Conclusión: predicen mejor los modelos no lineales que recogen la **heterogeneidad espacial** y relaciones flexibles entre características y precio. Es la referencia natural para justificar que la imputación del alquiler no sea un modelo lineal simple.

## Referencias del curso

Anselin (1988), LeSage y Pace (2009), Elhorst (2014), Pebesma y Bivand (2023, *Spatial Data Science*), Rey, Arribas-Bel y Wolf (2020, *Geographic Data Science with Python*).

## Lecturas complementarias

- Chasco, C. (2025). *Basic Exploratory Spatial Data Analysis in GeoDa Software* (preprint, UAM). Mapas de caja, percentiles, Bayes empírico y ESDA de variables discretas, con ejemplos de Madrid.
- Moura, A. C. M. y Fonseca, B. M. (2020). ESDA of vegetation cover in urban areas. *Sustainability*. Moran y LISA bivariantes.
- Geerts, M. (2025). *Geospatial Machine Learning for Real Estate Valuation*. Tesis doctoral, KU Leuven. Árboles geoespaciales (geoRF), pérdida espacial para boosting (MI-GBT), GNN, cuantificación de la incertidumbre y LLMs.
- Kriging de residuos sobre ML: estudios de Varsovia (*Housing price prediction: machine learning and geostatistical methods*) y de Acapulco (Hernández-López y Wences, regresión hedónica con RF y kriging). Valoración catastral masiva en Primorie (Rusia): regresión con kriging para suelo, RuleFit para pisos.
- Trindade Neves, F., Aparicio, M. y de Castro Neto, M. (2024). The impacts of open data and XAI on real estate price predictions in smart cities. *Applied Sciences* 14, 2209. Datos abiertos de accesibilidad y SHAP.
