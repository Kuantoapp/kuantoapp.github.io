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

Reglas, fijadas antes de ver el resultado:
- Regla de Anselin sobre los LM robustos del MCO (y = rechazadas por 1.000, X = esfuerzo 2023, renta ADRH 2023 y tope, estos
  dos en miles de €; W de k = 5, normalizada por filas): si solo el LM-error robusto tiene p < 0,05, SEM
  (`spreg.ML_Error`); si solo el LM-lag robusto, SAR (`spreg.ML_Lag`, con efectos directo, indirecto y total,
  nunca β); si los dos, el de menor p robusta; si ninguno, MCO. Siempre se informan además el SEM y el SLX
  (`OLS` con `slx_lags=1`), el SAR y el SDEM (`ML_Error` con `slx_lags=1`) con su AIC, y la robustez con k = 8. El AIC se calcula igual para todos, `2 * parámetros - 2 * logll` con λ o ρ
  contados (spreg no cuenta λ en `ML_Error`, y así el SEM y el SDEM salían favorecidos frente al SAR).
- Regla de conclusión: «robusta» si la Pearson parcial (la principal de `bono.validacion`) y el modelo espacial
  elegido coinciden en signo y en p < 0,05; si no, «no concluyente». En el SAR el signo es el del efecto total
  y la p la del coeficiente del esfuerzo (shortcut: no hay p del efecto total, por simulación si hiciera falta).
- Los modelos de conteo (binomial negativa, con `offset = log(población joven)`) y la quasi-binomial de
  aceptadas sobre solicitudes (`scale = "X2"`) son robustez: no entran en la regla de conclusión.

Lectura (añadida en la revisión):
- λ es dependencia residual (una molestia que corrige el error), no un desbordamiento entre vecinos; en el SEM, β es
  el efecto marginal del esfuerzo y no hay efectos indirectos.
- La p de la principal (0,118) y la de la binomial negativa (0,068) son optimistas: sus residuos tienen
  autocorrelación (Moran 0,157 y 0,176), así que sus errores estándar están infraestimados. La p del SEM (0,030) baja
  porque β sube de 60,8 (MCO) a 85,4 (SEM) con un error estándar parecido (38,6 y 39,4), no porque se corrijan los
  errores estándar (corregir unos infraestimados subiría la p). La regla exige además la Pearson parcial: de ahí
  «no concluyente».

LISA bivariante: `Moran_Local_BV(x = esfuerzo del municipio, y = aceptadas por 1.000 suavizadas por Bayes empírico
(media a priori sin Madrid, como las rechazadas), W de k = 5)`, con `PERMUTACIONES_LISA` = 99.999 permutaciones, p
bilateral y corrección por comparaciones múltiples `esda.fdr(p, 0,05)`. Con 999 permutaciones la p mínima (0,003, es decir, 3/(R+1))
no llega al primer escalón de la FDR con n = 134 (0,05/134), y `lisa` falla si las permutaciones no bastan. Se ejecuta con k = 5 y k = 8 (estabilidad).
«alta_baja» es necesidad alta en el municipio y ayuda baja en su entorno; «baja_alta», el inverso. Es una
asociación local, sin lectura causal; si sale un solo municipio (28080, Majadahonda, en la ejecución con los datos
actuales) es un resultado frágil. Se informa junto al I de Moran bivariante global, que dice si hay patrón en conjunto.
Las p de Moran y Geary de `bono` son bilaterales: `min(1, 2 * p_sim)`.
"""

import json
import logging

import esda
import numpy as np
import pandas as pd
import spreg
import statsmodels.api as sm
from libpysal.weights import W
from statsmodels.discrete.discrete_model import NegativeBinomialResults

from mesobra import bono

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


def concluir(r: float, p: float, beta: float, p_modelo: float) -> str:
    """«robusta» si la Pearson parcial (r, p) y el modelo espacial (beta, p) coinciden en signo y en p < 0,05."""
    coinciden = np.sign(r) == np.sign(beta) and p < ALFA and p_modelo < ALFA
    return "robusta" if coinciden else "no concluyente"


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


def _coef(m: spreg.OLS | spreg.ML_Error | spreg.ML_Lag, i: int) -> dict:
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


def regresion(d: pd.DataFrame, puntos: np.ndarray, k: int) -> dict:
    """MCO con diagnósticos, SEM, SAR, SLX y SDEM siempre (con su AIC); el modelo elegido por la regla de Anselin.

    El esfuerzo es la columna 1 (la 0 es la constante). `elegido` lleva beta (o efectos), p y el Moran de sus residuos.
    """
    w, y, x = bono._w(puntos, k), d[[Y]].to_numpy(float), d[X].to_numpy(float)
    ols = spreg.OLS(y, x, w, spat_diag=True, moran=True)
    sem = spreg.ML_Error(y, x, w)
    sar = spreg.ML_Lag(y, x, w)
    slx = spreg.OLS(y, x, w, slx_lags=1)
    sdem = spreg.ML_Error(y, x, w, slx_lags=1)
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


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    tabla = pd.read_parquet(bono.PROCESSED / "bono.parquet")
    renta = bono._renta_adrh(
        pd.read_parquet(bono.PROCESSED / "renta.parquet"), bono.ANIO
    )
    xy = bono._municipios_xy()
    d, puntos = preparar(tabla, renta, xy)
    pearson = bono.validacion(tabla, renta, xy)[Y]["pearson"]
    esp = {f"k{k}": regresion(d, puntos, k) for k in (K, 8)}
    elegido = esp[f"k{K}"]["elegido"]
    sar = elegido["modelo"] == "SAR"
    efecto = elegido["efectos"]["total"] if sar else elegido["beta"]
    resultado = {
        "n": len(d),
        "pearson_parcial": pearson,
        "espacial": esp,
        "glm": glm(d, puntos),
        "geary_residuos_k5": bono.geary(bono._residuos(d[Y], d[X]), puntos, K),
        "lisa": _resumen_lisa(lisa(d, puntos)),
        "lisa_k8": _resumen_lisa(lisa(d, puntos, k=8)),
        "conclusion": concluir(pearson["r"], pearson["p"], efecto, elegido["p"]),
    }
    texto = json.dumps(resultado, indent=1, default=float)
    LOG.info("Inferencia del Bono:\n%s", texto)
    SALIDA.write_text(texto)


if __name__ == "__main__":
    main()
