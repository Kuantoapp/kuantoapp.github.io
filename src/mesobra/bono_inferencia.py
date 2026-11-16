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
- La p del SEM no es estable a la especificación: con el retardo WX (SDEM o SLX), β baja a unos 71-75 y la p
  vuelve a 0,11-0,16 con k = 5 y k = 8. El salto de β entre MCO y SEM (+40 %) apunta a una variable omitida con
  estructura espacial o a la falta de WX, así que el SEM no cuenta como corroboración: es una limitación. Tampoco es prueba en contra: el AIC prefiere el SEM
  sin WX al SDEM (920,0 frente a 923,5) y el MCO al SLX (926,1 frente a 927,8).

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
- Descomposición (cifras del JSON, `lectura`). La regla fijada de antemano es la de los 134 (r = 0,137, p = 0,118;
  «no concluyente»); los 112 son una sensibilidad. En los municipios con al menos 300 jóvenes de 20-34 (los 112), la
  principal da «robusta» (r = 0,197, p = 0,039; SEM p = 0,020 con k = 5), así que la conclusión depende de los 22
  municipios pequeños, que tienen tasas ruidosas; con el denominador de vivienda alquilada da «no concluyente»
  (r = 0,153, p = 0,109; MCO). Quitar los 22 refuerza la relación y el denominador la atenúa, porque el porcentaje se
  correlaciona con el esfuerzo (+0,27) y con la renta (-0,35). «No concluyente» descansa en la regla sobre los 134 y en
  el diagnóstico de Bayes empírico (`bono.validacion`, `pearson_parcial_eb`: r = 0,156, p = 0,075 en los 134), que apunta
  a que el ruido de los municipios pequeños atenúa r. No se apoya en el retardo WX: en los 112 el AIC prefiere el SEM
  al SDEM (736,2 frente a 740,8) y el MCO al SLX (744,0 frente a 747,9), y el esfuerzo y su retardo están
  correlacionados, de modo que añadir WX quita potencia.
- Sesgo de selección (JSON, `seleccion`): 22 municipios y 111 solicitudes fuera de la muestra, todos por el umbral de
  300 personas; mediana de población joven 257 de los excluidos frente a 1.893,5 de los incluidos, y renta media de
  35,3 frente a 45,6 miles de €. Del Bono se pierden 44 municipios y 166 solicitudes.
- Autocorrelación residual: la Pearson de la principal en los 112 es optimista. El Moran de los residuos del MCO es
  0,203 con k = 5 (principal) y 0,100 con k = 8 (denominador de vivienda alquilada; p = 0,032). La p que se cita es la de
  permutaciones y bilateral (`bono.moran`, clave `moran_mco`), no la analítica de spreg (`moran_ols`): con n pequeño no
  supone normalidad, y es la misma que usa el resto del módulo.
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


def _concluir_modelo(pearson: dict, elegido: dict) -> str:
    """Regla de conclusión con el modelo elegido (en el SAR, el efecto total)."""
    sar = elegido["modelo"] == "SAR"
    efecto = elegido["efectos"]["total"] if sar else elegido["beta"]
    return concluir(pearson["r"], pearson["p"], efecto, elegido["p"])


def _bloque(r: pd.DataFrame, puntos: np.ndarray, y: str, otras: list[str]) -> dict:
    """En los municipios de `r`: Pearson parcial de `y` (más el de `otras`), regresión espacial (k = 5 y 8), conclusión (k = 5) y Moran del MCO.

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
        "conclusion": _concluir_modelo(pearson, esp[f"k{K}"]["elegido"]),
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

    Lectura (la regla fijada de antemano es la de los 134; los 112 son una sensibilidad): «no concluyente» descansa en
    la regla sobre los 134 y en el diagnóstico de Bayes empírico (`pearson_parcial_eb`); en los municipios con porcentaje
    la regla da «robusta», así que la conclusión depende de los municipios pequeños, de tasas ruidosas. El denominador
    atenúa la relación porque el porcentaje se correlaciona con el esfuerzo. El Moran del MCO que se cita es el de
    permutaciones y bilateral (`bono.moran`), no el analítico de spreg: no supone normalidad con n pequeño.
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
    # solo cifras y conclusiones de la regla: la interpretación va en el docstring, que no se recalcula
    lectura = (
        f"Principal en los {len(d)} (regla fijada de antemano): {conclusion_principal}. Principal en los {len(r)} "
        f"municipios con porcentaje: {principal['conclusion']} (r = {pp['r']:.3f}, p = {pp['p']:.3f}; regresión "
        f"elegida k = {K}: p = {principal['espacial'][f'k{K}']['elegido']['p']:.3f}; Moran de los residuos del MCO "
        f"{principal['moran_mco'][f'k{K}']['I']:.3f}, p = {principal['moran_mco'][f'k{K}']['p']:.3f}). Con el "
        f"denominador de vivienda alquilada: {alq['conclusion']} (r = {pa['r']:.3f}, p = {pa['p']:.3f}). Correlación "
        f"del porcentaje en alquiler con el esfuerzo: {r['esfuerzo'].corr(pct[r.index]):+.2f}. Fuera de la "
        f"submuestra: {len(fuera)} municipios."
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
        "correlacion_porcentaje": {
            "esfuerzo": float(r["esfuerzo"].corr(pct[r.index])),
            "renta": float(r["renta"].corr(pct[r.index])),
        },
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
    conclusion = _concluir_modelo(pearson, esp[f"k{K}"]["elegido"])
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
