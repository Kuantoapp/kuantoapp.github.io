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
- La tasa de aceptación no tiene patrón espacial (su Moran ya era ≈ 0,04): sin clústeres relevantes.
- Con k = 8 el signo del β del esfuerzo se mantiene.

Reglas, fijadas antes de ver el resultado:
- Regla de Anselin sobre los LM robustos del MCO (y = rechazadas por 1.000, X = esfuerzo 2023, renta ADRH 2023 y tope, estos
  dos en miles de €; W de k = 5, normalizada por filas): si solo el LM-error robusto tiene p < 0,05, SEM
  (`spreg.ML_Error`); si solo el LM-lag robusto, SAR (`spreg.ML_Lag`, con efectos directo, indirecto y total,
  nunca β); si los dos, el de menor p robusta; si ninguno, MCO. Siempre se informan además el SEM y el SLX
  (`OLS` con `slx_lags=1`) con su AIC, y la robustez con k = 8.
- Regla de conclusión: «robusta» si la Pearson parcial (la principal de `bono.validacion`) y el modelo espacial
  elegido coinciden en signo y en p < 0,05; si no, «no concluyente». En el SAR el signo es el del efecto total
  y la p la del coeficiente del esfuerzo (shortcut: no hay p del efecto total, por simulación si hiciera falta).
- Los modelos de conteo (binomial negativa, con `offset = log(población joven)`) y la quasi-binomial de
  aceptadas sobre solicitudes (`scale = "X2"`) son robustez: no entran en la regla de conclusión.

LISA bivariante: `Moran_Local_BV(x = esfuerzo del municipio, y = aceptadas por 1.000 suavizadas por Bayes empírico
(media a priori sin Madrid, como las rechazadas), W de k = 5)`, con 999 permutaciones y corrección por
comparaciones múltiples `esda.fdr(p, 0,05)`. «alta_baja» es necesidad alta en el municipio y ayuda baja en su
entorno; «baja_alta», el inverso. Es una asociación local, sin lectura causal. Control: la suma de los Is
locales es proporcional al I global bivariante. El p es bilateral (`alternative="two-sided"`).
"""

import json
import logging

import esda
import numpy as np
import pandas as pd
import spreg
import statsmodels.api as sm

from mesobra import bono

LOG = logging.getLogger(__name__)
SALIDA = bono.PROCESSED / "bono_inferencia.json"
X = ["esfuerzo", "renta", "tope"]
Y = "rechazadas_por_mil"
ALFA = 0.05
K = 5
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
    coinciden = np.sign(r) == np.sign(beta) and max(p, p_modelo) < ALFA
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
    d["tope"] = (
        bono.tope_eur(d.index) / 1000
    )  # miles de €: en € la binomial negativa no converge
    d[Y] = 1000 * d["rechazadas"] / d["poblacion_joven"]
    if faltan := list(d.index[d[X].isna().any(axis=1)]):
        raise ValueError(f"Municipios con necesidad y sin renta: {faltan}")
    return d, xy.loc[d.index].to_numpy(float)


def _coef(m: object, i: int) -> dict:
    """Coeficiente `i` de un modelo de spreg: beta, error estándar, estadístico (t o z) y p."""
    est = getattr(m, "z_stat", None) or m.t_stat
    return {
        "beta": float(m.betas[i, 0]),
        "se": float(m.std_err[i]),
        "estadistico": float(est[i][0]),
        "p": float(est[i][1]),
    }


def _efectos_sar(m: spreg.ML_Lag, w: object, i: int) -> dict:
    """Efectos directo (media de la diagonal), indirecto y total de la X `i` en un SAR: (I - ρW)^-1 β."""
    n = w.n
    s = np.linalg.inv(np.eye(n) - m.rho * w.full()[0]) * m.betas[i, 0]
    total = float(s.sum() / n)
    directo = float(np.trace(s) / n)
    return {"directo": directo, "indirecto": total - directo, "total": total}


def regresion(d: pd.DataFrame, puntos: np.ndarray, k: int) -> dict:
    """MCO con diagnósticos, SEM y SLX siempre; el modelo elegido por la regla de Anselin (SAR solo si se elige).

    El esfuerzo es la columna 1 (la 0 es la constante). `elegido` lleva beta (o efectos), p y el Moran de sus residuos.
    """
    w, y, x = bono._w(puntos, k), d[[Y]].to_numpy(float), d[X].to_numpy(float)
    ols = spreg.OLS(y, x, w, spat_diag=True, moran=True)
    sem = spreg.ML_Error(y, x, w)
    slx = spreg.OLS(y, x, w, slx_lags=1)
    p_error, p_lag = ols.rlm_error[1], ols.rlm_lag[1]
    elegido = elegir_modelo(p_error, p_lag)
    modelos = {"OLS": ols, "SEM": sem}
    if elegido == "SAR":
        modelos["SAR"] = spreg.ML_Lag(y, x, w)
    m = modelos[elegido]
    residuos = sem.e_filtered if elegido == "SEM" else m.u
    sal = {
        "lm": {
            "error": ols.lm_error[1],
            "lag": ols.lm_lag[1],
            "error_robusto": p_error,
            "lag_robusto": p_lag,
        },
        "moran_ols": {"I": ols.moran_res[0], "p": ols.moran_res[2]},
        "ols": {**_coef(ols, 1), "aic": ols.aic},
        "sem": {**_coef(sem, 1), "lambda": sem.lam, "aic": sem.aic},
        "slx": {**_coef(slx, 1), "beta_lag": slx.betas[4, 0], "aic": slx.aic},
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


def _nb(y: pd.Series, x: pd.DataFrame, offset: pd.Series) -> object:
    """Binomial negativa (NB2) con offset; falla si no converge."""
    res = sm.NegativeBinomial(y, x, offset=offset).fit(disp=0, maxiter=500)
    if not res.mle_retvals["converged"]:
        raise RuntimeError(f"La binomial negativa de {y.name} no converge")
    return res


def _pearson_nb(res: object, y: pd.Series) -> np.ndarray:
    mu = res.predict()
    return ((y - mu) / np.sqrt(mu + res.params["alpha"] * mu**2)).to_numpy()


def glm(d: pd.DataFrame, puntos: np.ndarray) -> dict:
    """Binomial negativa de rechazadas y solicitudes (offset log población joven) y quasi-binomial de aceptadas."""
    x = sm.add_constant(d[X])
    offset = np.log(d["poblacion_joven"])
    sal = {}
    for y in ("rechazadas", "solicitudes"):
        nb = _nb(d[y], x, offset)
        poisson = sm.Poisson(d[y], x, offset=offset).fit(disp=0)
        sal[y] = {
            "esfuerzo": {"beta": nb.params["esfuerzo"], "p": nb.pvalues["esfuerzo"]},
            "alpha": nb.params["alpha"],
            "p_alpha": nb.pvalues["alpha"],
            "aic_nb": nb.aic,
            "aic_poisson": poisson.aic,
            "moran_pearson": bono.moran(_pearson_nb(nb, d[y]), puntos, K),
        }
    qb = sm.GLM(
        d["aceptadas"] / d["solicitudes"],
        x,
        family=sm.families.Binomial(),
        var_weights=d["solicitudes"],
    ).fit(scale="X2")
    sal["aceptadas_sobre_solicitudes"] = {
        "esfuerzo": {"beta": qb.params["esfuerzo"], "p": qb.pvalues["esfuerzo"]},
        "escala": qb.scale,
        "moran_pearson": bono.moran(qb.resid_pearson.to_numpy(), puntos, K),
    }
    return sal


def lisa(d: pd.DataFrame, puntos: np.ndarray) -> tuple[pd.Series, float]:
    """Cuadrante significativo tras la FDR por `municipio_id` («ns» si no) y la razón Σ Is locales / I global.

    x = esfuerzo del municipio, y = aceptadas por 1.000 suavizadas (el retardo Wy es el entorno).
    """
    ayuda = bono.eb_por_mil(d["aceptadas"], d["poblacion_joven"])
    w = bono._w(puntos, K)
    x, y = d["esfuerzo"].to_numpy(), ayuda.to_numpy()
    local = esda.Moran_Local_BV(
        x,
        y,
        w,
        permutations=bono.PERMUTACIONES,
        seed=bono.SEMILLA,
        alternative="two-sided",
    )
    umbral = esda.fdr(local.p_sim, ALFA)
    significativo = local.p_sim <= umbral
    cuadrante = pd.Series(np.vectorize(CUADRANTES.get)(local.q), index=d.index)
    razon = local.Is.sum() / esda.Moran_BV(x, y, w, permutations=0).I
    return cuadrante.where(significativo, "ns"), float(razon)


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
    cuadrante, razon = lisa(d, puntos)
    elegido = esp[f"k{K}"]["elegido"]
    sar = elegido["modelo"] == "SAR"
    efecto = elegido["efectos"]["total"] if sar else elegido["beta"]
    resultado = {
        "n": len(d),
        "pearson_parcial": pearson,
        "espacial": esp,
        "glm": glm(d, puntos),
        "geary_residuos_k5": bono.geary(bono._residuos(d[Y], d[X]), puntos, K),
        "lisa": {
            "cuadrantes": cuadrante.value_counts().to_dict(),
            "alta_baja": sorted(cuadrante.index[cuadrante == "alta_baja"]),
            "razon_suma_is_i_global": razon,
        },
        "conclusion": concluir(pearson["r"], pearson["p"], efecto, elegido["p"]),
    }
    texto = json.dumps(resultado, indent=1, default=float)
    LOG.info("Inferencia del Bono:\n%s", texto)
    SALIDA.write_text(texto)


if __name__ == "__main__":
    main()
