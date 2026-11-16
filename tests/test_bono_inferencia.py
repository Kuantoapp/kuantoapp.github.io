"""Tests de `mesobra.bono_inferencia` con datos sintéticos de resultado conocido."""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from mesobra import bono
from mesobra import bono_inferencia as bi


def _rejilla(n):
    return np.array([(i, j) for i in range(n) for j in range(n)], float)


def test_sem_recupera_lambda_y_beta():
    rng = np.random.default_rng(0)
    xy = _rejilla(20)
    n = len(xy)
    x = rng.normal(size=(n, 3))
    w = bono._w(xy, 5).full()[0]
    u = np.linalg.solve(np.eye(n) - 0.5 * w, rng.normal(size=n))
    y = 2 + x @ [1.0, 0.5, -0.5] + u
    d = pd.DataFrame(x, columns=bi.X).assign(**{bi.Y: y})
    res = bi.regresion(d, xy, 5)
    assert res["sem"]["lambda"] == pytest.approx(0.5, abs=0.15)
    assert res["sem"]["beta"] == pytest.approx(1.0, abs=0.15)
    assert res["lm"]["error"] < 0.05  # el SEM generado deja autocorrelación en el MCO
    assert abs(res["elegido"]["moran_residuos"]["I"]) < 0.1


def test_binomial_negativa_recupera_beta():
    rng = np.random.default_rng(1)
    n = 600
    x = sm.add_constant(pd.DataFrame({"esfuerzo": rng.normal(size=n)}))
    pob = pd.Series(rng.integers(100, 5000, n), name="y")
    mu = pob * np.exp(-4 + 0.5 * x["esfuerzo"])
    # NB2 con α = 0,5: gamma de media mu y varianza α·mu²
    y = pd.Series(rng.poisson(rng.gamma(2, mu / 2)), name="y")
    res = bi._nb(y, x, np.log(pob))
    assert res.params["esfuerzo"] == pytest.approx(0.5, abs=0.1)
    assert res.params["alpha"] == pytest.approx(0.5, abs=0.15)


def _lisa(x, y, n):
    d = pd.DataFrame(
        {"esfuerzo": x, "aceptadas": 5000 + 1000 * y, "poblacion_joven": 1e6},
        index=range(n * n),
    )
    return bi.lisa(d, _rejilla(n))


def test_lisa_detecta_bloque_alta_baja_y_ruido_no_da_nada():
    n = 10
    rng = np.random.default_rng(2)
    x, y = rng.normal(size=n * n), rng.normal(size=n * n)
    ruido, _ = _lisa(x, y, n)
    assert (ruido == "ns").all()
    bloque = np.array([i < 4 and j < 4 for i, j in _rejilla(n)])
    x[bloque] += 4  # esfuerzo alto en el bloque, ayuda baja en su entorno
    y[bloque] -= 4
    cuadrante, razon = _lisa(x, y, n)
    assert (cuadrante[bloque] == "alta_baja").sum() >= 4
    assert (cuadrante[~bloque] == "alta_baja").sum() == 0
    assert razon > 0


def test_reglas():
    assert bi.elegir_modelo(0.01, 0.5) == "SEM"
    assert bi.elegir_modelo(0.5, 0.01) == "SAR"
    assert bi.elegir_modelo(0.01, 0.02) == "SEM"
    assert bi.elegir_modelo(0.03, 0.02) == "SAR"
    assert bi.elegir_modelo(0.2, 0.3) == "OLS"
    assert bi.concluir(0.14, 0.01, 0.3, 0.02) == "robusta"
    assert (
        bi.concluir(0.14, 0.01, 0.3, 0.2) == "no concluyente"
    )  # el espacial no es significativo
    assert bi.concluir(0.14, 0.2, 0.3, 0.01) == "no concluyente"  # la Pearson no lo es
    assert bi.concluir(0.14, 0.01, -0.3, 0.01) == "no concluyente"  # signos opuestos


def test_preparar_exige_renta():
    tabla = pd.DataFrame(
        {
            "municipio_id": ["28001", "28002"],
            "solicitudes": [10, 10],
            "aceptadas": [4, 4],
            "rechazadas": [6, 6],
            "poblacion_joven": [100, 100],
            "necesidad": [20.0, 30.0],
        }
    )
    xy = pd.DataFrame({"x": [0.0, 1.0], "y": [0.0, 1.0]}, index=tabla["municipio_id"])
    renta = pd.Series([3e4, 4e4], index=tabla["municipio_id"])
    d, puntos = bi.preparar(tabla, renta, xy)
    assert d["esfuerzo"].tolist() == [0.2, 0.3] and d["renta"].iloc[0] == 30
    assert puntos.shape == (2, 2)
    with pytest.raises(ValueError, match="sin renta"):
        bi.preparar(tabla, renta.iloc[:1], xy)


def test_suma_de_is_locales_proporcional_al_global():
    n = 10
    razones = [
        _lisa(*np.random.default_rng(s).normal(size=(2, n * n)), n)[1] for s in (3, 4)
    ]
    assert razones[0] == pytest.approx(razones[1])
