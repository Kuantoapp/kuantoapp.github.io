"""Inferencia espacial del Bono Alquiler Joven: regresión espacial, GLM de conteos y LISA bivariante.

Complementa la validación de `bono.py` (Pearson parcial, que es la especificación principal) con modelos que
tratan la autocorrelación (spreg), el conteo y la sobredispersión (statsmodels) y localizan clústeres (esda).
Lee `data/processed/bono.parquet`, `esfuerzo.parquet` y `renta.parquet` y escribe `bono_inferencia.json` con
las cifras para #90. No toca el contrato `bono`. Muestra: los municipios con esfuerzo y renta (134 en 2023).

Expectativas, escritas ANTES de ejecutar con los datos reales (si alguna falla, se diagnostica antes de
interpretar nada):
- β del esfuerzo en el MCO de spreg: igual que el MCO ya hecho (t = 1,573, p = 0,118, n = 134); positivo y
  pequeño en el modelo espacial (el Pearson parcial es r ≈ 0,14).
- Autocorrelación positiva de los residuos (I de Moran ≈ 0,15 con k = 5); λ (SEM) o ρ (SAR) entre 0 y 0,5.
- α de la binomial negativa > 0 (sobredispersión; el AIC prefiere la binomial negativa a Poisson).
- Moran de los residuos del SEM (filtrados) ≈ 0; el de los residuos de Pearson del GLM, cerca de 0 o algo
  positivo, porque el GLM no modela el espacio.
- La tasa de aceptación no tiene patrón espacial (su Moran ya era ≈ 0,04).
- Añadida en la revisión, tras ver el resultado (con 999 permutaciones no se podía rechazar nada): el I de Moran
  bivariante global (esfuerzo frente a aceptadas por 1.000 suavizadas) es ≈ 0, y el LISA, con permutaciones
  suficientes, deja a lo sumo uno o dos municipios, sin un patrón regional.
- Con k = 8 el signo del β del esfuerzo se mantiene.
- Añadidas ANTES de ejecutar el modelo principal nuevo (#221, `GM_Error_Het`): β del esfuerzo positivo; λ entre 0 y 0,5;
  error estándar de `GM_Error_Het` igual o mayor que el de `ML_Error` (la heterocedasticidad infraestima el del ML);
  Koenker-Bassett significativo (p < 0,05); y el error estándar HAC del MCO, parecido al del SEM heterocedástico.

Reglas de la regla de Anselin y de los modelos de referencia, fijadas antes de ver el resultado (#213):
- Regla de Anselin sobre los LM robustos del MCO (y = rechazadas por 1.000, X = esfuerzo 2023, renta ADRH 2023 y tope, estos
  dos en miles de €; W de k = 5, normalizada por filas): si solo el LM-error robusto tiene p < 0,05, SEM
  (`spreg.ML_Error`); si solo el LM-lag robusto, SAR (`spreg.ML_Lag`, con efectos directo, indirecto y total,
  nunca β); si los dos, el de menor p robusta; si ninguno, MCO. Siempre se informan además el SEM y el SLX
  (`OLS` con `slx_lags=1`), el SAR y el SDEM (`ML_Error` con `slx_lags=1`) con su AIC, y la robustez con k = 8. El AIC se calcula igual para todos, `2 * parámetros - 2 * logll` con λ o ρ
  contados (spreg no cuenta λ en `ML_Error`, y así el SEM y el SDEM salían favorecidos frente al SAR).

Regla de conclusión (#221, sustituye a la del #209; elegida DESPUÉS de ver los datos, no fijada de antemano):
- «robusta» si el β del esfuerzo de `spreg.GM_Error_Het` (SEM heterocedástico, W de k = 5) es positivo (el signo
  teórico: más esfuerzo, más rechazadas) con p < 0,05 y con k = 8 mantiene el signo y p < 0,05; si no, «no concluyente»
  (un NaN da «no concluyente» y un aviso en el log, porque la estimación falló). Estimador: GMM iterado de Arraiz et
  al. (2010) (`max_iter=10`, sin el paso 1c opcional; `iteraciones` dice si convergió), elegido DESPUÉS de ver la p
  (decisión del humano, #223): da p < 0,05 y el de dos pasos no. Iterar quita la dependencia de la estimación inicial
  de λ, pero no mejora la eficiencia asintótica: las dos variantes son válidas. El GMM en dos pasos (`max_iter=1,
  step1c=False`, el valor por defecto de spreg y el principal en el #221) se guarda como sensibilidad
  (`sem_het_dos_pasos`). El modelo principal se eligió DESPUÉS de ver los datos (decisión del humano, #221): por
  los LM robustos y el AIC (#213), que eligen el SEM, más la heterocedasticidad de las tasas de municipios pequeños,
  que el SEM por máxima verosimilitud (`ML_Error`) no admite; `GM_Error_Het` (Kelejian y Prucha, 2010; Arraiz et al.,
  2010) es consistente con heterocedasticidad de forma desconocida y válido haya o no heterocedasticidad. La Pearson parcial, el SEM por máxima verosimilitud
  y la regla de Anselin se siguen informando como referencia, pero ya no deciden.
- Segunda vía: MCO con errores estándar HAC espaciales (`spreg.OLS(robust="hac", gwk=...)`), con pesos de kernel de
  `libpysal.weights.Kernel` sobre las coordenadas: kernel triangular y ancho de banda adaptativo con
  `k = k + 1`: libpysal ya suma 1 por el propio municipio, así que el ancho llega al vecino k + 1, que queda con peso
  ≈ 1e-7; el soporte efectivo es el municipio y sus k vecinos. Se informa también Breusch-Pagan, Koenker-Bassett y
  Jarque-Bera del MCO.
- Los modelos de conteo (binomial negativa, con `offset = log(población joven)`) y la quasi-binomial de
  aceptadas sobre solicitudes (`scale = "X2"`) son robustez: no entran en la regla de conclusión.

Resultado del principal (#223, ejecución con los datos reales, 134 municipios): `GM_Error_Het` iterado da β = 87,49 (error
estándar 43,14, p = 0,0426, λ = 0,40, 5 iteraciones) con k = 5 y β = 87,05 (error estándar 44,01, p = 0,0479, λ = 0,46, 4
iteraciones) con k = 8: «robusta», al límite. Con el GMM en dos pasos (principal en el #221) β = 83,95 y 85,32, p = 0,0515 y
0,0525: «no concluyente». El SEM por máxima verosimilitud daba p = 0,030 con error estándar 39,4
(k = 5): la heterocedasticidad lo infraestimaba un 9 %. MCO-HAC: β = 60,8, error estándar 43,8 (k = 5) y 44,5 (k = 8),
p = 0,167 y 0,175. Se cumplen las expectativas de signo, λ, error estándar y HAC. Heterocedasticidad: Jarque-Bera del
MCO da p = 2,4e-10 (errores no normales), así que Breusch-Pagan (p = 0,0008) rechaza de más y el contraste válido es
Koenker-Bassett: p = 0,046 en los 134 (se cumple justo la expectativa) y p = 0,21 en los 112 (falla; ahí solo
Breusch-Pagan, p = 0,038, la detecta). Residuos filtrados del principal sin autocorrelación (Moran −0,020, p = 0,84
con k = 5; −0,010 con k = 8).
La etiqueta depende de la opción de estimación: con GMM iterado p = 0,043 / 0,048, «robusta»; con el GMM en dos pasos,
p = 0,0515 / 0,0525, «no concluyente». El iterado se eligió a la vista de esas p (#223): está al límite y no se debe leer
como un resultado firme.

Lectura (añadida en la revisión):
- λ es dependencia residual (una molestia que corrige el error), no un desbordamiento entre vecinos; en el SEM, β es
  el efecto marginal del esfuerzo y no hay efectos indirectos.
- El efecto del esfuerzo es positivo y estable entre W dentro del SEM (β ≈ 84-87, con k = 5 y k = 8), y su p queda
  alrededor de 0,05 una vez corregida la heterocedasticidad (0,043-0,053 según W y variante del GMM): «robusta» con la
  regla, pero por poco. Limitación: β varía según la especificación (MCO 61, WX 71-75, `GM_Combo_Het` 113, MCO ponderado por
  población 247; cifras de la revisión del #221), señal de una especificación incompleta o de un efecto que cambia con
  el tamaño del municipio. El p = 0,030 del SEM por máxima verosimilitud venía en parte de un error estándar infraestimado.
- Las p de la Pearson parcial (0,118) y de la binomial negativa (0,068) son optimistas: sus residuos tienen
  autocorrelación (Moran 0,157 y 0,176). El MCO-HAC (p ≈ 0,17) corrige eso, pero su β es el del MCO, más bajo que el
  del SEM (60,8 frente a 84): la diferencia no es significativa (Hausman espacial de la revisión del #213, p = 0,33).
- Con el retardo WX (SDEM o SLX), β baja a unos 71-75 y la p sube; el AIC prefiere los modelos sin WX (SEM 920,0
  frente a SDEM 923,5; MCO 926,1 frente a SLX 927,8), así que no es prueba en contra: el esfuerzo y su retardo
  están correlacionados y añadir WX quita potencia.

LISA bivariante: `Moran_Local_BV(x = esfuerzo del municipio, y = aceptadas por 1.000 suavizadas por Bayes empírico
(media a priori sin Madrid, como las rechazadas), W de k = 5)`, con `PERMUTACIONES_LISA` = 99.999 permutaciones, p
bilateral y corrección por comparaciones múltiples `esda.fdr(p, 0,05)`. Con 999 permutaciones la p mínima (0,003, es decir, 3/(R+1))
no llega al primer escalón de la FDR con n = 134 (0,05/134), y `lisa` falla si las permutaciones no bastan. Se ejecuta con k = 5 y k = 8 (estabilidad).
«alta_baja» es necesidad alta en el municipio y ayuda baja en su entorno; «baja_alta», el inverso. Es una
asociación local, sin lectura causal; si sale un solo municipio (28080, Majadahonda, en la ejecución con los datos
actuales) es un resultado frágil. Se informa junto al I de Moran bivariante global, que dice si hay patrón en conjunto.
Las p de Moran y Geary de `bono` son bilaterales: `min(1, 2 * p_sim)`.

Robustez con jóvenes en vivienda alquilada (`robustez_vivienda_alquilada`, #210; bloque `robustez_vivienda_alquilada` del
JSON; no cambia la conclusión principal ni el contrato `bono`):
- Expectativa (añadida en la revisión, tras ver el resultado): con el denominador de población × porcentaje en alquiler
  de 20-34 (Censo 2021, `censo2021`), r baja y la conclusión no mejora; el cambio de muestra (los municipios con
  porcentaje) y el del denominador son efectos distintos, y por eso la principal se repite en la MISMA submuestra.
- Descomposición (cifras del JSON, `lectura`). La regla del #221 con el estimador del #223 (los dos elegidos después de
  ver los datos) es la de los 134 («robusta», al límite; la Pearson, r = 0,137 y p = 0,118, es referencia); los 112 son una
  sensibilidad. En los municipios con al menos 300 jóvenes de 20-34 (los 112), la principal da «robusta» con más margen
  (r = 0,197, p = 0,039; SEM heterocedástico: p = 0,022 con k = 5 y 0,030 con k = 8), así que los 22 municipios pequeños,
  de tasas ruidosas, atenúan la relación; con el denominador de vivienda alquilada da «no concluyente» (p = 0,096 con k = 5
  y 0,205 con k = 8; MCO r = 0,153, p = 0,109). Quitar los 22 refuerza la relación y el denominador la atenúa, porque el
  porcentaje se correlaciona con el esfuerzo (+0,27) y con la renta (-0,35). El diagnóstico de Bayes empírico
  (`bono.validacion`, `pearson_parcial_eb`: r = 0,156, p = 0,075 en los 134) apunta también a que el ruido de los
  municipios pequeños atenúa r. El resultado no se apoya en el retardo WX: en los 112 el AIC prefiere el SEM al SDEM (736,2 frente a 740,8) y el
  MCO al SLX (744,0 frente a 747,9), y el esfuerzo y su retardo están correlacionados, de modo que añadir WX quita potencia.
- Sesgo de selección (JSON, `seleccion`): 22 municipios y 111 solicitudes fuera de la muestra, todos por el umbral de
  300 personas; mediana de población joven 257 de los excluidos frente a 1.893,5 de los incluidos, y renta media de
  35,3 frente a 45,6 miles de €. Del Bono se pierden 44 municipios y 166 solicitudes.
- Autocorrelación residual: la Pearson de la principal en los 112 es optimista. El Moran de los residuos del MCO es
  0,203 con k = 5 (principal) y 0,100 con k = 8 (denominador de vivienda alquilada; p = 0,032). La p que se cita es la de
  permutaciones y bilateral (`bono.moran`, clave `moran_mco`), no la analítica de spreg (`moran_ols`): con n pequeño no
  supone normalidad, y es la misma que usa el resto del módulo.

Control por el % de jóvenes en alquiler (#225, exploratorio; `control_alquiler`, elegido DESPUÉS de ver los datos; no cambia
la regla ni la conclusión principal). Entre quienes piden el Bono, el porcentaje de rechazo apenas cambia con el esfuerzo
(aceptadas + rechazadas = solicitudes, así que la quasi-binomial de `glm` es la tasa de rechazo con el signo cambiado;
p = 0,82 en los 134). Hay más rechazadas por joven donde el esfuerzo es mayor porque hay más solicitudes. En los 112
municipios con %, parte de ese volumen coincide con que allí alquilan más jóvenes (corr % y esfuerzo +0,27; % y
solicitudes por 1.000 +0,61; % y tasa de rechazo +0,01). Controlando el %, el β del esfuerzo baja de ~94 a ~46 (k = 5) y de
~88 a ~34 (k = 8), con p 0,22 y 0,37 e IC95 [-27,5; 118,9] y [-39,2; 106,5], que contienen tanto el 0 como el β sin control:
es pérdida de precisión, no un efecto nulo («no concluyente»). Cuánto se reduce depende del estimador (-51 % en el SEM y -22 %
en el MCO-HAC, β 83 a 65, p = 0,11: el sesgo de variable omitida β_% · δ, con δ = esfuerzo → % mayor tras el filtro espacial).
El error de medida del % (2021, 20-34, incluye a quien vive en un piso alquilado de sus padres) dejaría confusión residual
a favor del esfuerzo, no en contra. El % es anterior al Bono, así que no es un control posterior al tratamiento; actúa como
exposición (solo quien alquila puede pedir). Vale para los 112, no para los 134. Moran de los residuos filtrados ≈ 0
(0,000 y 0,005).
"""

import json
import logging

import esda
import numpy as np
import pandas as pd
import spreg
import statsmodels.api as sm
from libpysal.weights import Kernel, W
from statsmodels.discrete.discrete_model import NegativeBinomialResults

from mesobra import bono, censo2021

LOG = logging.getLogger(__name__)
SALIDA = bono.PROCESSED / "bono_inferencia.json"
X = ["esfuerzo", "renta", "tope"]
Y = "rechazadas_por_mil"
ALFA = 0.05
K = 5
PERMUTACIONES_LISA = 99_999
CUADRANTES = {1: "alta_alta", 2: "baja_alta", 3: "baja_baja", 4: "alta_baja"}


def elegir_modelo(p_error: float, p_lag: float) -> str:
    """Regla de Anselin con los p de los LM robustos: «SEM», «SAR» u «OLS»."""
    error, lag = p_error < ALFA, p_lag < ALFA
    if error and lag:
        return "SEM" if p_error <= p_lag else "SAR"
    if error:
        return "SEM"
    return "SAR" if lag else "OLS"


def concluir(k5: dict, k8: dict) -> str:
    """«robusta» si el β del esfuerzo del SEM heterocedástico es positivo con p < 0,05 (k = 5) y con k = 8 mantiene el signo y p < 0,05."""
    if np.isnan([k5["p"], k8["p"]]).any():
        LOG.warning("p del SEM heterocedástico es NaN: la estimación falló")
    ok = k5["p"] < ALFA and k8["p"] < ALFA and k5["beta"] > 0 and k8["beta"] > 0
    return "robusta" if ok else "no concluyente"


def preparar(
    tabla: pd.DataFrame, renta: pd.Series, xy: pd.DataFrame
) -> tuple[pd.DataFrame, np.ndarray]:
    """Municipios con esfuerzo, con sus variables (renta y tope en miles de €) y coordenadas, alineados por `municipio_id`."""
    t = tabla.set_index("municipio_id")
    t = t[t["necesidad"].notna()]
    d = t[["solicitudes", "aceptadas", "rechazadas", "poblacion_joven"]].copy()
    d["esfuerzo"] = t["necesidad"] / t["poblacion_joven"]
    d["renta"] = renta.reindex(d.index) / 1000
    # miles de €: en € la binomial negativa no converge
    d["tope"] = bono.tope_eur(d.index) / 1000
    d[Y] = 1000 * d["rechazadas"] / d["poblacion_joven"]
    if faltan := list(d.index[d[X].isna().any(axis=1)]):
        raise ValueError(f"Municipios con necesidad y sin renta: {faltan}")
    recuentos = d[["solicitudes", "aceptadas", "rechazadas"]]
    if malos := list(d.index[recuentos.isna().any(axis=1) | (d["solicitudes"] == 0)]):
        raise ValueError(f"Municipios con recuentos nulos o sin solicitudes: {malos}")
    return d, xy.loc[d.index].to_numpy(float)


def _aic(m: spreg.OLS | spreg.ML_Error | spreg.ML_Lag) -> float:
    """AIC comparable: `betas` de spreg incluye λ o ρ en los modelos de máxima verosimilitud, `m.aic` no los cuenta igual."""
    return float(2 * len(m.betas) - 2 * m.logll)


def _coef(
    m: spreg.OLS | spreg.ML_Error | spreg.ML_Lag | spreg.GM_Error_Het, i: int
) -> dict:
    """Coeficiente `i` de un modelo de spreg: beta, error estándar, estadístico (t o z) y p."""
    est = getattr(m, "z_stat", None) or m.t_stat
    return {
        "beta": float(m.betas[i, 0]),
        "se": float(m.std_err[i]),
        "estadistico": float(est[i][0]),
        "p": float(est[i][1]),
    }


def _efectos_sar(m: spreg.ML_Lag, w: W, i: int) -> dict:
    """Efectos directo (media de la diagonal), indirecto y total de la X `i` en un SAR: (I - ρW)^-1 β."""
    n = w.n
    s = np.linalg.inv(np.eye(n) - m.rho * w.full()[0]) * m.betas[i, 0]
    total = float(s.sum() / n)
    directo = float(np.trace(s) / n)
    return {"directo": directo, "indirecto": total - directo, "total": total}


def _gmm_iterado(y: np.ndarray, x: np.ndarray, w: W, k: int) -> spreg.GM_Error_Het:
    """`GM_Error_Het` con GMM iterado (`max_iter=10`); avisa si llegó al máximo, porque puede no haber convergido."""
    m = spreg.GM_Error_Het(y, x, w=w, max_iter=10)
    if (
        m.iteration == 10
    ):  # spreg no distingue «sin converger» de «convergió justo en la décima»
        LOG.warning(
            "GMM iterado: alcanzó max_iter=10 con k = %s; puede no haber convergido", k
        )
    return m


def regresion(d: pd.DataFrame, puntos: np.ndarray, k: int) -> dict:
    """Principal: SEM heterocedástico (`sem_het`, GMM iterado; `sem_het_dos_pasos` es la sensibilidad con GMM en dos pasos). Referencias: MCO con diagnósticos, SEM, SAR, SLX y SDEM (con su AIC), MCO-HAC y el modelo de la regla de Anselin.

    En `sem_het`, `lambda` es un dict `{valor, se, p}` (en `sem` y `sdem` es el float).

    El esfuerzo es la columna 1 (la 0 es la constante). `elegido` lleva beta (o efectos), p y el Moran de sus residuos.
    """
    w, y, x = bono._w(puntos, k), d[[Y]].to_numpy(float), d[X].to_numpy(float)
    ols = spreg.OLS(y, x, w, spat_diag=True, moran=True)
    sem = spreg.ML_Error(y, x, w)
    sar = spreg.ML_Lag(y, x, w)
    slx = spreg.OLS(y, x, w, slx_lags=1)
    sdem = spreg.ML_Error(y, x, w, slx_lags=1)
    # principal, GMM iterado (#223); el de dos pasos (por defecto de spreg) es la sensibilidad: ver el docstring
    het = _gmm_iterado(y, x, w, k)
    dos_pasos = spreg.GM_Error_Het(y, x, w=w, max_iter=1, step1c=False)
    lam = _coef(het, -1)
    hac = spreg.OLS(
        y,
        x,
        robust="hac",
        gwk=Kernel(puntos, k=k + 1, fixed=False, function="triangular"),
    )
    p_error, p_lag = ols.rlm_error[1], ols.rlm_lag[1]
    elegido = elegir_modelo(p_error, p_lag)
    m = {"OLS": ols, "SEM": sem, "SAR": sar}[elegido]
    residuos = sem.e_filtered if elegido == "SEM" else m.u
    sal = {
        "lm": {
            "error": ols.lm_error[1],
            "lag": ols.lm_lag[1],
            "error_robusto": p_error,
            "lag_robusto": p_lag,
        },
        "moran_ols": {"I": ols.moran_res[0], "p": ols.moran_res[2]},
        "ols": {**_coef(ols, 1), "aic": _aic(ols)},
        "sem_het": {
            **_coef(het, 1),
            "lambda": {"valor": lam["beta"], "se": lam["se"], "p": lam["p"]},
            "moran_residuos": bono.moran(het.e_filtered.ravel(), puntos, k),
            "iteraciones": het.iteration,
        },
        "sem_het_dos_pasos": _coef(dos_pasos, 1),
        "ols_hac": _coef(hac, 1),
        "heterocedasticidad": {
            "breusch_pagan": {
                "estadistico": ols.breusch_pagan["bp"],
                "p": ols.breusch_pagan["pvalue"],
            },
            "koenker_bassett": {
                "estadistico": ols.koenker_bassett["kb"],
                "p": ols.koenker_bassett["pvalue"],
            },
            "jarque_bera": {
                "estadistico": ols.jarque_bera["jb"],
                "p": ols.jarque_bera["pvalue"],
            },
        },
        "sem": {**_coef(sem, 1), "lambda": sem.lam, "aic": _aic(sem)},
        "sar": {**_coef(sar, 1), "rho": sar.rho, "aic": _aic(sar)},
        "slx": {**_coef(slx, 1), "beta_lag": slx.betas[4, 0], "aic": _aic(slx)},
        "sdem": {**_coef(sdem, 1), "lambda": sdem.lam, "aic": _aic(sdem)},
        "elegido": {
            "modelo": elegido,
            **_coef(m, 1),
            "moran_residuos": bono.moran(residuos, puntos, k),
        },
    }
    if elegido == "SAR":
        sal["elegido"]["rho"] = m.rho
        sal["elegido"]["efectos"] = _efectos_sar(m, w, 1)
    return sal


def control_alquiler(r: pd.DataFrame, puntos: np.ndarray) -> dict:
    """EXPLORATORIO (#225, elegido después de ver los datos): el esfuerzo con el % de jóvenes en alquiler como covariable.

    `r` lleva las columnas de `X`, `Y` y `alquiler_joven` (fracción 0-1). SEM heterocedástico (GMM iterado) con k = 5 y 8
    (`alquiler_joven` es el coeficiente 4), MCO-HAC y la conclusión con la misma regla que la principal.
    """
    cols = X + ["alquiler_joven"]
    y, x = r[[Y]].to_numpy(float), r[cols].to_numpy(float)
    sal = {}
    for k in (K, 8):
        m = _gmm_iterado(y, x, bono._w(puntos, k), k)
        c = _coef(m, 1)
        sal[f"k{k}"] = {
            **c,
            "ic95": [c["beta"] - 1.96 * c["se"], c["beta"] + 1.96 * c["se"]],
            "alquiler_joven": _coef(m, 4),
            "moran_residuos": bono.moran(m.e_filtered.ravel(), puntos, k),
            "iteraciones": m.iteration,
        }
    hac = spreg.OLS(
        y,
        x,
        robust="hac",
        gwk=Kernel(puntos, k=K + 1, fixed=False, function="triangular"),
    )
    sal["ols_hac"] = _coef(hac, 1)
    sal["conclusion"] = concluir(sal[f"k{K}"], sal["k8"])
    return sal


def _nb(y: pd.Series, x: pd.DataFrame, offset: pd.Series) -> NegativeBinomialResults:
    """Binomial negativa (NB2) con offset; falla si no converge."""
    res = sm.NegativeBinomial(y, x, offset=offset).fit(disp=0, maxiter=500)
    if not res.mle_retvals["converged"]:
        raise RuntimeError(f"La binomial negativa de {y.name} no converge")
    return res


def glm(d: pd.DataFrame, puntos: np.ndarray) -> dict:
    """Binomial negativa de rechazadas y solicitudes (offset log población joven) y quasi-binomial de aceptadas."""
    x = sm.add_constant(d[X])
    offset = np.log(d["poblacion_joven"])
    sal = {}
    for y in ("rechazadas", "solicitudes"):
        nb = _nb(d[y], x, offset)
        poisson = sm.Poisson(d[y], x, offset=offset).fit(disp=0)
        if not poisson.mle_retvals["converged"]:
            raise RuntimeError(f"El Poisson de {y} no converge")
        sal[y] = {
            "esfuerzo": {"beta": nb.params["esfuerzo"], "p": nb.pvalues["esfuerzo"]},
            "alpha": nb.params["alpha"],
            "p_alpha": nb.pvalues["alpha"],
            "aic_nb": nb.aic,
            "aic_poisson": poisson.aic,
            "moran_pearson": bono.moran(nb.resid_pearson, puntos, K),
        }
    qb = sm.GLM(
        d["aceptadas"] / d["solicitudes"],
        x,
        family=sm.families.Binomial(),
        var_weights=d["solicitudes"],
    ).fit(scale="X2")
    if not qb.converged:
        raise RuntimeError("La quasi-binomial no converge")
    sal["aceptadas_sobre_solicitudes"] = {
        "esfuerzo": {"beta": qb.params["esfuerzo"], "p": qb.pvalues["esfuerzo"]},
        "escala": qb.scale,
        "moran_pearson": bono.moran(qb.resid_pearson.to_numpy(), puntos, K),
    }
    return sal


def lisa(
    d: pd.DataFrame,
    puntos: np.ndarray,
    permutaciones: int = PERMUTACIONES_LISA,
    k: int = K,
) -> tuple[pd.Series, pd.Series, dict]:
    """Cuadrante significativo (W de k vecinos) tras la FDR, p bilateral por `municipio_id` y el Moran_BV global (I, p bilateral).

    x = esfuerzo del municipio, y = aceptadas por 1.000 suavizadas (el retardo Wy es el entorno).
    """
    if 3 / (permutaciones + 1) >= ALFA / len(d):
        raise ValueError(
            f"Con {permutaciones} permutaciones la p mínima no llega al umbral de la FDR con n = {len(d)}"
        )
    w = bono._w(puntos, k)
    x = d["esfuerzo"].to_numpy()
    y = bono.eb_por_mil(d["aceptadas"], d["poblacion_joven"]).to_numpy()
    local = esda.Moran_Local_BV(
        x, y, w, permutations=permutaciones, seed=bono.SEMILLA, alternative="two-sided"
    )
    significativo = local.p_sim <= esda.fdr(local.p_sim, ALFA)
    cuadrante = pd.Series(local.q, index=d.index).map(CUADRANTES)
    np.random.seed(bono.SEMILLA)  # esda permuta con el generador global
    bv = esda.Moran_BV(x, y, w, permutations=bono.PERMUTACIONES)
    global_ = {"I": float(bv.I), "p": min(1.0, 2 * float(bv.p_sim))}
    return (
        cuadrante.where(significativo, "ns"),
        pd.Series(local.p_sim, index=d.index),
        global_,
    )


def _resumen_lisa(res: tuple) -> dict:
    cuadrante, p, bv = res
    return {
        "cuadrantes": cuadrante.value_counts().to_dict(),
        "alta_baja": sorted(cuadrante.index[cuadrante == "alta_baja"]),
        "p_alta_baja": p[cuadrante == "alta_baja"].to_dict(),
        "moran_bv_global": bv,
        "lectura": "asociación local, no causal; un solo municipio es un resultado frágil",
    }


def _bloque(r: pd.DataFrame, puntos: np.ndarray, y: str, otras: list[str]) -> dict:
    """En los municipios de `r`: Pearson parcial de `y` (más el de `otras`), regresión espacial (k = 5 y 8), conclusión (SEM heterocedástico, k = 5 y 8) y Moran del MCO.

    El Moran del MCO es el de permutaciones y bilateral de `bono.moran` (el de spreg es analítico y se queda en `espacial`).
    """
    controles = r[["renta", "tope"]]
    pearson = bono.correlacion_parcial(r["esfuerzo"], r[y], controles)
    esp = {f"k{k}": regresion(r.assign(**{Y: r[y]}), puntos, k) for k in (K, 8)}
    residuos = bono._residuos(r[y], r[X])
    return {
        "n": len(r),
        "pearson_parcial": pearson,
        "pearson_otras": {
            c: bono.correlacion_parcial(r["esfuerzo"], r[c], controles) for c in otras
        },
        "espacial": esp,
        "moran_mco": {f"k{k}": bono.moran(residuos, puntos, k) for k in (K, 8)},
        "conclusion": concluir(esp[f"k{K}"]["sem_het"], esp["k8"]["sem_het"]),
    }


def robustez_vivienda_alquilada(
    tabla: pd.DataFrame,
    d: pd.DataFrame,
    puntos: np.ndarray,
    pct: pd.Series,
    conclusion_principal: str,
) -> dict:
    """Robustez: la ayuda por 1.000 jóvenes en vivienda alquilada (población 18-35 de 2023 × porcentaje en alquiler de 20-34 de 2021).

    Mismo esfuerzo y controles que la principal; solo cambia el denominador de la ayuda. Cambia a la vez la muestra
    (los municipios con porcentaje: el INE lo suprime o hay menos de `censo2021.MIN_JOVENES_20_34` personas), así que se
    guarda también la principal (rechazadas por 1.000 jóvenes de 18-35) en la MISMA submuestra: la diferencia entre las dos
    es el efecto del denominador, y la que hay entre la principal en `d` y en la submuestra es el de quitar municipios.
    Cada bloque lleva la Pearson parcial de las rechazadas (la de la regla), la de las solicitudes y las aceptadas, la
    regresión espacial con k = 5 y 8 y la conclusión. `tabla` es la del Bono (159 municipios), `d` y `puntos` los de
    `preparar`, y `conclusion_principal` la de la principal en `d`. Se declara el sesgo de selección (población joven y
    renta de excluidos e incluidos) y las correlaciones del porcentaje con el esfuerzo y la renta. Supuestos en
    `censo2021`. El porcentaje no puede ser 0: sería dividir por cero.

    Lectura (la regla es la del SEM heterocedástico del #221, con el GMM iterado del #223, en los 134; los 112 son una
    sensibilidad): en los 134 queda «robusta» por poco (p ≈ 0,043); en los municipios con porcentaje la misma regla da
    «robusta» con más margen, así que los municipios pequeños, de tasas ruidosas, atenúan la relación. El denominador
    atenúa la relación porque el porcentaje se correlaciona con el esfuerzo. El Moran del MCO que se cita es el de
    permutaciones y bilateral (`bono.moran`), no el analítico de spreg: no supone normalidad con n pequeño.

    Lleva también `control_alquiler` (#225, exploratorio): el esfuerzo controlando el % de jóvenes en alquiler.
    """
    if (pct == 0).any():
        raise ValueError(f"Municipios con 0 % en alquiler: {list(pct.index[pct == 0])}")
    ok = pct.reindex(d.index).notna().to_numpy()
    r, fuera = d[ok].copy(), d[~ok]
    jovenes_alquilados = r["poblacion_joven"] * pct[r.index]
    for c in ("solicitudes", "aceptadas", "rechazadas"):
        r[f"{c}_por_mil_alq"] = 1000 * r[c] / jovenes_alquilados
        r[f"{c}_por_mil"] = 1000 * r[c] / r["poblacion_joven"]
    bloques = {
        nombre: _bloque(
            r,
            puntos[ok],
            f"rechazadas_por_mil{sufijo}",
            [f"solicitudes_por_mil{sufijo}", f"aceptadas_por_mil{sufijo}"],
        )
        for nombre, sufijo in (
            ("alquiler", "_alq"),
            ("principal_misma_submuestra", ""),
        )
    }
    alq, principal = bloques["alquiler"], bloques["principal_misma_submuestra"]
    en_bono = tabla["municipio_id"].isin(pct.index[pct.notna()])
    pa, pp = alq["pearson_parcial"], principal["pearson_parcial"]
    ca = control_alquiler(r.assign(alquiler_joven=pct[r.index]), puntos[ok])
    c5, c8 = ca[f"k{K}"], ca["k8"]
    corr = {
        "esfuerzo": float(r["esfuerzo"].corr(pct[r.index])),
        "renta": float(r["renta"].corr(pct[r.index])),
        "solicitudes_por_mil": float(r["solicitudes_por_mil"].corr(pct[r.index])),
        "tasa_rechazo": float((r["rechazadas"] / r["solicitudes"]).corr(pct[r.index])),
    }
    # solo cifras y conclusiones de la regla: la interpretación va en el docstring, que no se recalcula
    lectura = (
        f"Principal en los {len(d)} (regla del #221 con el GMM iterado del #223, elegidos después de ver los datos; la Pearson es referencia): {conclusion_principal}. Principal en los {len(r)} "
        f"municipios con porcentaje: {principal['conclusion']} (r = {pp['r']:.3f}, p = {pp['p']:.3f}; regresión "
        f"SEM heterocedástico p = {principal['espacial'][f'k{K}']['sem_het']['p']:.3f} (k = {K}) y "
        f"{principal['espacial']['k8']['sem_het']['p']:.3f} (k = 8); Moran de los residuos del MCO "
        f"{principal['moran_mco'][f'k{K}']['I']:.3f}, p = {principal['moran_mco'][f'k{K}']['p']:.3f}). Con el "
        f"denominador de vivienda alquilada: {alq['conclusion']} (r = {pa['r']:.3f}, p = {pa['p']:.3f}). Correlación "
        f"del porcentaje en alquiler con el esfuerzo: {corr['esfuerzo']:+.2f}. Fuera de la "
        f"submuestra: {len(fuera)} municipios. Controlando el porcentaje (exploratorio, #225), el esfuerzo da β = "
        f"{c5['beta']:.1f}, p = {c5['p']:.3f}, IC95 [{c5['ic95'][0]:.1f}, {c5['ic95'][1]:.1f}] (k = {K}) y β = "
        f"{c8['beta']:.1f}, p = {c8['p']:.3f}, IC95 [{c8['ic95'][0]:.1f}, {c8['ic95'][1]:.1f}] (k = 8): "
        f"{ca['conclusion']}. Correlación del porcentaje con las solicitudes por 1.000: "
        f"{corr['solicitudes_por_mil']:+.2f}; con la tasa de rechazo: {corr['tasa_rechazo']:+.2f}."
    )
    return {
        **bloques,
        "municipios_con_porcentaje": int(pct.notna().sum()),
        "perdidos_del_bono": int((~en_bono).sum()),
        "solicitudes_perdidas_del_bono": int(tabla.loc[~en_bono, "solicitudes"].sum()),
        "seleccion": {
            "excluidos": len(fuera),
            "solicitudes_excluidas": int(fuera["solicitudes"].sum()),
            "poblacion_joven_mediana": {
                "excluidos": float(fuera["poblacion_joven"].median()),
                "incluidos": float(r["poblacion_joven"].median()),
            },
            "renta_media_miles": {
                "excluidos": float(fuera["renta"].mean()),
                "incluidos": float(r["renta"].mean()),
            },
        },
        "control_alquiler": ca,
        "correlacion_porcentaje": corr,
        "lectura": lectura,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    tabla = pd.read_parquet(bono.PROCESSED / "bono.parquet")
    renta = bono._renta_adrh(
        pd.read_parquet(bono.PROCESSED / "renta.parquet"), bono.ANIO
    )
    xy = bono._municipios_xy()
    d, puntos = preparar(tabla, renta, xy)
    val = bono.validacion(tabla, renta, xy)
    pearson = val[Y]["pearson"]
    esp = {f"k{k}": regresion(d, puntos, k) for k in (K, 8)}
    conclusion = concluir(esp[f"k{K}"]["sem_het"], esp["k8"]["sem_het"])
    resultado = {
        "n": len(d),
        "pearson_parcial": pearson,
        "espacial": esp,
        "glm": glm(d, puntos),
        "geary_residuos_k5": bono.geary(bono._residuos(d[Y], d[X]), puntos, K),
        "lisa": _resumen_lisa(lisa(d, puntos)),
        "lisa_k8": _resumen_lisa(lisa(d, puntos, k=8)),
        "conclusion": conclusion,
        "pearson_parcial_eb": val["rechazadas_por_mil_eb"]["pearson"],
        "robustez_vivienda_alquilada": {
            **robustez_vivienda_alquilada(
                tabla,
                d,
                puntos,
                censo2021.pct_alquiler_joven(),
                conclusion,
            ),
            "recuento_censo": censo2021.recuento(),
        },
    }
    eb = resultado["pearson_parcial_eb"]
    resultado["robustez_vivienda_alquilada"]["lectura"] += (
        f" Diagnóstico: con las rechazadas suavizadas por Bayes empírico en los {len(d)}, r = {eb['r']:.3f} y "
        f"p = {eb['p']:.3f}."
    )
    texto = json.dumps(resultado, indent=1, default=float)
    LOG.info("Inferencia del Bono:\n%s", texto)
    SALIDA.write_text(texto)


if __name__ == "__main__":
    main()
