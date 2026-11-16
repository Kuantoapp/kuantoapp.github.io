"""Tests de `mesobra.bono_inferencia` con datos sintéticos de resultado conocido."""

import numpy as np
import pandas as pd
import pytest
import spreg
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
    assert res["elegido"]["modelo"] == "SEM"
    # el SEM generado gana al MCO y al SAR con el mismo criterio de AIC (el SDEM lo anida y puede empatar)
    assert res["sem"]["aic"] < min(res["ols"]["aic"], res["sar"]["aic"])
    # spreg no cuenta λ en el AIC de ML_Error y sí ρ en ML_Lag: `_aic` los cuenta igual
    w5 = bono._w(xy, 5)
    xs = d[bi.X].to_numpy()
    sem = spreg.ML_Error(d[[bi.Y]].to_numpy(), xs, w=w5)
    sar = spreg.ML_Lag(d[[bi.Y]].to_numpy(), xs, w=w5)
    assert bi._aic(sem) == pytest.approx(sem.aic + 2)
    assert bi._aic(sar) == pytest.approx(sar.aic)


def test_sar_se_elige_y_recupera_rho_y_efectos():
    rng = np.random.default_rng(0)
    xy = _rejilla(20)
    n = len(xy)
    x = rng.normal(size=(n, 3))
    w = bono._w(xy, 5).full()[0]
    y = np.linalg.solve(
        np.eye(n) - 0.4 * w, 2 + x @ [1.0, 0.5, -0.5] + rng.normal(size=n)
    )
    d = pd.DataFrame(x, columns=bi.X).assign(**{bi.Y: y})
    el = bi.regresion(d, xy, 5)["elegido"]
    assert el["modelo"] == "SAR"
    assert el["rho"] == pytest.approx(0.4, abs=0.15)
    assert el["efectos"]["total"] == pytest.approx(
        el["beta"] / (1 - el["rho"]), rel=1e-9
    )
    assert el["efectos"]["directo"] + el["efectos"]["indirecto"] == pytest.approx(
        el["efectos"]["total"]
    )


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
    return bi.lisa(d, _rejilla(n), permutaciones=9999)


def test_lisa_detecta_bloque_alta_baja_y_ruido_no_da_nada():
    n = 10
    rng = np.random.default_rng(2)
    x, y = rng.normal(size=n * n), rng.normal(size=n * n)
    ruido, _, _ = _lisa(x, y, n)
    assert (ruido == "ns").all()
    bloque = np.array([i < 4 and j < 4 for i, j in _rejilla(n)])
    x[bloque] += 4  # esfuerzo alto en el bloque, ayuda baja en su entorno
    y[bloque] -= 4
    cuadrante, p, bv = _lisa(x, y, n)
    assert (cuadrante[bloque] == "alta_baja").sum() >= 4
    assert (cuadrante[~bloque] == "alta_baja").sum() == 0
    assert p[cuadrante == "alta_baja"].max() < 0.001 and bv["I"] < 0 and bv["p"] < 0.05
    with pytest.raises(ValueError, match="permutaciones"):
        bi.lisa(pd.DataFrame({"esfuerzo": x}, index=range(n * n)), _rejilla(n), 999)


def test_reglas():
    assert bi.elegir_modelo(0.01, 0.5) == "SEM"
    assert bi.elegir_modelo(0.5, 0.01) == "SAR"
    assert bi.elegir_modelo(0.01, 0.02) == "SEM"
    assert bi.elegir_modelo(0.03, 0.02) == "SAR"
    assert bi.elegir_modelo(0.2, 0.3) == "OLS"


def _c(beta, p):
    return {"beta": beta, "p": p}


def test_concluir_sem_het_con_k5_y_k8():
    assert bi.concluir(_c(80, 0.03), _c(70, 0.04)) == "robusta"
    assert bi.concluir(_c(80, 0.03), _c(70, 0.2)) == "no concluyente"  # k = 8 no
    assert bi.concluir(_c(80, 0.2), _c(70, 0.01)) == "no concluyente"  # k = 5 no
    assert bi.concluir(_c(80, 0.01), _c(-70, 0.01)) == "no concluyente"  # signos
    assert (
        bi.concluir(_c(-80, 0.01), _c(-70, 0.01)) == "no concluyente"
    )  # signo teórico
    assert bi.concluir(_c(80, float("nan")), _c(70, 0.01)) == "no concluyente"
    assert bi.concluir(_c(80, 0.01), _c(70, float("nan"))) == "no concluyente"


def test_sem_het_recupera_beta_y_lambda_con_heterocedasticidad_y_hac_finito():
    rng = np.random.default_rng(3)
    xy = _rejilla(20)
    n = len(xy)
    x = rng.normal(size=(n, 3))
    w = bono._w(xy, 5).full()[0]
    # heterocedasticidad plantada: la desviación típica de la innovación crece con |x0|
    sd = 0.2 + 1.5 * np.abs(x[:, 0])
    u = np.linalg.solve(np.eye(n) - 0.5 * w, rng.normal(size=n) * sd)
    y = 2 + x @ [1.0, 0.5, -0.5] + u
    d = pd.DataFrame(x, columns=bi.X).assign(**{bi.Y: y})
    res = bi.regresion(d, xy, 5)
    het = res["sem_het"]
    assert het["lambda"]["valor"] == pytest.approx(0.5, abs=0.2)
    assert het["beta"] == pytest.approx(1.0, abs=0.3)
    assert het["beta"] - 1.96 * het["se"] <= 1.0 <= het["beta"] + 1.96 * het["se"]
    # distingue el estimador heterocedástico del homocedástico: ML_Error infraestima el error estándar
    assert het["se"] > res["sem"]["se"]
    assert abs(het["moran_residuos"]["I"]) < 0.15
    # el principal es el GMM iterado (#223): converge en más de un paso y no coincide con el de dos pasos
    assert 1 < het["iteraciones"] < 10
    assert het["beta"] != pytest.approx(res["sem_het_dos_pasos"]["beta"], rel=1e-9)
    assert np.isfinite(res["ols_hac"]["se"]) and res["ols_hac"]["se"] > 0
    assert res["heterocedasticidad"]["koenker_bassett"]["p"] < 0.05


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
    # xy desordenado: `preparar` alinea por `municipio_id`
    xy = pd.DataFrame({"x": [1.0, 0.0], "y": [1.0, 0.0]}, index=["28002", "28001"])
    renta = pd.Series([3e4, 4e4], index=tabla["municipio_id"])
    d, puntos = bi.preparar(tabla, renta, xy)
    assert d["esfuerzo"].tolist() == [0.2, 0.3] and d["renta"].iloc[0] == 30
    assert puntos.tolist() == [[0.0, 0.0], [1.0, 1.0]]
    with pytest.raises(ValueError, match="sin renta"):
        bi.preparar(tabla, renta.iloc[:1], xy)
    with pytest.raises(ValueError, match="recuentos"):
        bi.preparar(tabla.assign(solicitudes=[10, 0]), renta, xy)
    with pytest.raises(ValueError, match="recuentos"):
        bi.preparar(tabla.assign(aceptadas=[4, np.nan]), renta, xy)


def test_robustez_vivienda_alquilada_denominador_perdidos_y_regla():
    rng = np.random.default_rng(1)
    xy = _rejilla(5)
    ids = [f"280{i:02d}" for i in range(1, 26)]
    esfuerzo = rng.uniform(0.1, 0.5, 25)
    pob = rng.uniform(500, 5000, 25)
    pct = pd.Series(rng.uniform(0.2, 0.6, 25), index=ids)
    # la ayuda por 1.000 jóvenes en alquiler es lineal en el esfuerzo: solo sale bien con población × porcentaje
    y = 2 + 30 * esfuerzo + rng.normal(0, 0.3, 25)
    rechazadas = y * pob * pct.to_numpy() / 1000
    d = pd.DataFrame(
        {
            "solicitudes": 2 * rechazadas + 1,
            "aceptadas": rechazadas,
            "rechazadas": rechazadas,
            "poblacion_joven": pob,
            "esfuerzo": esfuerzo,
            "renta": rng.normal(30, 5, 25),
            "tope": rng.normal(1, 0.3, 25),
        },
        index=pd.Index(ids, name="municipio_id"),
    )
    d[bi.Y] = 1000 * d["rechazadas"] / d["poblacion_joven"]
    # sin porcentaje: nulo (28003 y 28011) y ausente (28007); 28099 tiene porcentaje pero no está en la muestra
    pct["28003"] = np.nan
    pct["28011"] = np.nan
    pct = pct.drop("28007")
    pct["28099"] = 0.4
    tabla = pd.DataFrame(
        {
            "municipio_id": [*ids, "28098", "28099"],
            "solicitudes": [*d["solicitudes"], 7.0, 5.0],
        }
    )
    sal = bi.robustez_vivienda_alquilada(tabla, d, xy, pct, "PRINCIPAL")
    perdidos = ["28003", "28007", "28011"]
    assert sal["alquiler"]["n"] == 22 == sal["principal_misma_submuestra"]["n"]
    assert sal["seleccion"]["excluidos"] == 3
    assert sal["seleccion"]["solicitudes_excluidas"] == int(
        d.loc[perdidos, "solicitudes"].sum()
    )
    # del Bono se pierden además 28098 (sin porcentaje); 28099 sí lo tiene
    assert sal["perdidos_del_bono"] == 4
    assert sal["solicitudes_perdidas_del_bono"] == int(
        d.loc[perdidos, "solicitudes"].sum() + 7
    )
    ok = d.drop(perdidos)
    r = sal["alquiler"]["pearson_parcial"]
    esperado = bono.correlacion_parcial(
        ok["esfuerzo"], pd.Series(y, index=ids).drop(perdidos), ok[["renta", "tope"]]
    )
    # si se rompe el denominador (p. ej. solo población), r deja de coincidir con la relación plantada
    assert r["r"] == pytest.approx(esperado["r"])
    assert r["n"] == 22 and esperado["r"] > 0.9
    e = sal["alquiler"]["espacial"]
    assert sal["alquiler"]["conclusion"] == bi.concluir(
        e["k5"]["sem_het"], e["k8"]["sem_het"]
    )
    assert sal["alquiler"]["conclusion"] == "robusta"
    assert set(sal["alquiler"]["espacial"]) == {"k5", "k8"}
    # los dos bloques tienen la misma forma y la lectura lleva la conclusión de la principal que se le pasa
    assert sal["alquiler"].keys() == sal["principal_misma_submuestra"].keys()
    assert set(sal["alquiler"]["pearson_otras"]) == {
        "solicitudes_por_mil_alq",
        "aceptadas_por_mil_alq",
    }
    assert "PRINCIPAL" in sal["lectura"]
    # la principal sobre la misma submuestra usa la población de 18-35 sin el porcentaje: otra r
    assert sal["principal_misma_submuestra"]["pearson_parcial"]["r"] != pytest.approx(
        r["r"]
    )
    assert sal["correlacion_porcentaje"]["esfuerzo"] == pytest.approx(
        ok["esfuerzo"].corr(pct[ok.index])
    )
    assert {"k5", "k8", "ols_hac", "conclusion"} <= set(sal["control_alquiler"])
    for c in ("solicitudes_por_mil", "tasa_rechazo"):
        assert np.isfinite(sal["correlacion_porcentaje"][c])
    with pytest.raises(ValueError, match="0 %"):
        bi.robustez_vivienda_alquilada(
            tabla, d, xy, pct.where(pct.index != "28001", 0.0), "x"
        )


def test_control_alquiler_quita_el_efecto_que_solo_pasa_por_el_porcentaje():
    rng = np.random.default_rng(0)
    xy = _rejilla(20)
    n = len(xy)
    pct = rng.normal(size=n)
    x = np.column_stack([0.8 * pct + 0.6 * rng.normal(size=n), rng.normal(size=(n, 2))])
    w = bono._w(xy, 5).full()[0]
    u = np.linalg.solve(np.eye(n) - 0.4 * w, rng.normal(size=n))
    # el esfuerzo (columna 0) no entra en y: solo el porcentaje, la renta y el tope
    y = 2 + pct + 0.5 * x[:, 1] - 0.5 * x[:, 2] + u
    d = pd.DataFrame(x, columns=bi.X).assign(**{bi.Y: y, "alquiler_joven": pct})
    assert bi.regresion(d, xy, 5)["sem_het"]["p"] < 0.05  # sin el %, parece un efecto
    res = bi.control_alquiler(d, xy)
    for k in ("k5", "k8"):
        assert res[k]["p"] > 0.05
        assert res[k]["ic95"][0] < 0 < res[k]["ic95"][1]
        assert res[k]["alquiler_joven"]["p"] < 0.05
        assert res[k]["alquiler_joven"]["beta"] == pytest.approx(1.0, abs=0.2)
        assert 1 < res[k]["iteraciones"] < 10
    assert res["conclusion"] == "no concluyente"
