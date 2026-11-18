"""`imputacion`: particiones sin fuga, exclusión espacial, conformal, elección y regla estimado o sin dato (#99)."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely import Point

from mesobra import contratos, imputacion
from mesobra.imputacion import (
    CENTRO,
    clasificar,
    cobertura,
    cuantil_conformal,
    distancias,
    elegir,
    elegir_buffer,
    particiones,
    validar_loo,
    vecinos,
)

RNG = np.random.default_rng(0)


def _obs(n=30):
    xy = RNG.uniform(0, 40_000, size=(n, 2))
    x = pd.DataFrame(
        RNG.normal(size=(n, len(imputacion.VARIABLES))), columns=imputacion.VARIABLES
    )
    y = 2 + xy[:, 0] / 40_000 + RNG.normal(0, 0.05, n)
    return {"x": x, "y": y, "d": distancias(xy, xy), "xy": xy}


def test_particiones_sin_repetidas_ni_vecinos_a_menos_de_b():
    obs, b = _obs(), 6_000.0
    test = np.arange(10)
    for i, train in particiones(obs["d"], test, b):
        assert i not in train
        assert (obs["d"][i, train] > b).all()
        assert set(train) == set(np.flatnonzero(obs["d"][i] > b))


def test_vecinos_a_mas_de_b_y_sin_la_propia_zona():
    d = _obs()["d"]
    v = vecinos(d, 5, 3_000.0)
    assert not (v == np.arange(len(d))[:, None]).any()
    assert (np.take_along_axis(d, v, 1) > 3_000).all()
    with pytest.raises(ValueError, match="Menos de"):
        vecinos(d, 5, 1e9)


@pytest.mark.parametrize("modelo", ["wy", "mco", "lgbm"])
def test_la_y_del_test_no_entra_en_su_prediccion(modelo):
    obs = _obs()
    conf = {"k": 5, "b": 4_000.0, "semilla": 1, "modelo": modelo}
    for i in (0, 1, 2):
        antes = validar_loo(obs, np.array([i]), conf)
        alterada = obs | {"y": obs["y"].copy()}
        alterada["y"][i] += 100
        despues = validar_loo(alterada, np.array([i]), conf)
        np.testing.assert_allclose(antes["pred"], despues["pred"])
        assert despues["y"].iloc[0] == antes["y"].iloc[0] + 100


def test_elegir_buffer_iguala_la_distancia_de_las_objetivo():
    xs = np.arange(0, 20_000, 1_000.0)
    obs = np.c_[xs, np.zeros_like(xs)]
    obj = np.c_[
        xs[2:-2], np.full(len(xs) - 4, 3_000.0)
    ]  # todas a 3 km de su dato más cercano
    b, ks = elegir_buffer(distancias(obs, obs), distancias(obj, obs))
    assert ks == 0
    assert 2_000 <= b < 3_000


def test_clasificar_en_el_borde():
    p50 = np.array([10.0, 10.0])
    assert list(clasificar(p50, np.array([8.0, 7.9]), np.array([13.0, 13.0]))) == [
        "estimado",
        "sin_dato",
    ]


def test_cuantil_conformal():
    s = np.arange(1, 10, dtype=float)  # n=9: ⌈0,9·10⌉ = 9.º
    assert cuantil_conformal(s, 0.9) == 9
    assert cuantil_conformal(s[:5], 0.9) == float("inf")


def _oof(n, escala=1.0):
    sigma = RNG.uniform(0.5, 2, n)
    return pd.DataFrame(
        {"y": RNG.normal(0, sigma * escala), "pred": 0.0, "sigma": sigma}
    )


def test_cobertura_cerca_de_la_nominal_si_calibracion_y_evaluadas_se_parecen():
    c = cobertura(_oof(400), imputacion.scores(_oof(400)), 0.9)
    assert c["n"] == 400
    assert 0.86 <= c["real"] <= 0.94
    assert c["wilson95"][0] < c["real"] < c["wilson95"][1]


def test_cobertura_detecta_que_no_se_transfiere():
    # con el LOO sobre el mismo conjunto saldría ⌈0,9·n⌉/n siempre; calibrando con otras zonas, no
    c = cobertura(_oof(400, escala=3.0), imputacion.scores(_oof(400)), 0.9)
    assert c["real"] < 0.6


def test_elegir_exige_el_margen_en_todas_las_variantes():
    base = pd.DataFrame({"wy": [1.0, 1.0], "mco": [0.91, 0.91], "lgbm": [0.85, 0.95]})
    assert elegir(base) == "wy"
    assert elegir(base.assign(mco=[0.89, 0.89])) == "mco"
    assert elegir(base.assign(lgbm=[0.5, 0.5])) == "lgbm"


def test_aplicable_nulo_y_distancia():
    train = pd.DataFrame({v: [0.0, 1.0] for v in imputacion.VARIABLES})
    pred = train.assign(dist_dato=[100.0, 900.0])
    pred.loc[0, "log_renta"] = np.nan
    assert list(imputacion._aplicable(pred, train, "mco", 500)) == [False, False]
    assert list(imputacion._aplicable(pred, train, "wy", 500)) == [True, False]


def _escenario(n_obs=50, n_obj=12, lejos=0.0):
    """Zonas sintéticas: n_obs con dato y una tendencia suave, n_obj sin dato en ningún año, entre ellas o `lejos` (m)."""
    xy = np.r_[
        RNG.uniform(0, 30_000, (n_obs, 2)),
        RNG.uniform(5_000, 25_000, (n_obj, 2)) + lejos,
    ]
    ids = [CENTRO] + [f"28{i:03d}" for i in range(1, n_obs + n_obj)]
    mitad = (
        n_obs // 2
    )  # pequeños (≤ 5.000, como las objetivo) y mayores, para calibrar la cobertura
    pob = np.r_[
        RNG.integers(300, 5_000, mitad), RNG.integers(6_000, 30_000, n_obs - mitad)
    ]
    pob = np.r_[pob, RNG.integers(100, 4_000, n_obj - 1), 5_000]
    zonas = gpd.GeoDataFrame(
        {"zona_id": ids, "poblacion": pob},
        geometry=[Point(x, y) for x, y in xy],
        crs=25830,
    ).to_crs(4326)
    rentas = pd.DataFrame(
        {
            "unidad_id": ids,
            "nivel": "zona",
            "anio": 2024,
            "renta_hogar": 40_000.0,
            "poblacion": pob,
        }
    )
    tp = np.full((len(ids), len(ids)), 60.0)
    tiempos = {
        "origenes": ids,
        "destinos": [{"destino_id": i} for i in ids],
        "tp": tp.tolist(),
    }
    p50 = np.r_[
        8 + xy[:n_obs, 0] / 10_000 + RNG.normal(0, 0.1, n_obs), [np.nan] * n_obj
    ]
    filas = []
    for anio in (2023, 2024):
        filas.append(pd.DataFrame({"zona_id": ids, "anio": anio, "eur_m2_p50": p50}))
    zona = pd.concat(filas, ignore_index=True)
    zona["eur_m2_p25"], zona["eur_m2_p75"] = (
        zona["eur_m2_p50"] * 0.8,
        zona["eur_m2_p50"] * 1.2,
    )
    zona["cuantia_p50"] = zona["eur_m2_p50"] * 70
    zona["cuantia_p25"], zona["cuantia_p75"] = (
        zona["cuantia_p50"] * 0.8,
        zona["cuantia_p50"] * 1.2,
    )
    zona["m2_p50"], zona["testigos"] = zona["eur_m2_p50"] * 0 + 70, 50
    zona["origen"] = (
        zona["eur_m2_p50"].notna().map({True: "observado", False: "sin_dato"})
    )
    zona["ic_inf"] = zona["ic_sup"] = np.nan
    zona["factor_ipc"] = np.where(zona["anio"] == 2024, 1.05, 1.1)
    zona = zona[list(contratos.CONTRATOS["alquiler_zona"]["columnas"])].astype(
        contratos.dtypes("alquiler_zona")
    )
    return zona, rentas, zonas, tiempos


def test_imputar_rellena_solo_2024_con_intervalo_y_cuantia_nula():
    zona, *resto = _escenario()
    out = imputacion.imputar(zona, *resto)
    inf = out.attrs["imputacion"]
    assert inf["imputar"], inf.get("motivo")
    est = out[out["origen"] == "estimado"]
    assert len(est) == sum(o["origen"] == "estimado" for o in inf["objetivo"]) > 0
    assert (est["anio"] == 2024).all() and (est["factor_ipc"] == 1.05).all()
    assert est["cuantia_p50"].isna().all() and est["m2_p50"].isna().all()
    assert (est["ic_inf"] < est["eur_m2_p50"]).all() and (
        est["eur_m2_p50"] < est["ic_sup"]
    ).all()
    assert (est["ic_sup"] - est["ic_inf"] <= 0.5 * est["eur_m2_p50"]).all()
    assert out[out["anio"] == 2023]["origen"].isin(["observado", "sin_dato"]).all()


def test_no_imputa_si_la_validacion_no_imita_la_distancia():
    zona, *resto = _escenario(lejos=200_000)
    out = imputacion.imputar(zona, *resto)
    assert not out.attrs["imputacion"]["imputar"]
    assert "KS" in out.attrs["imputacion"]["motivo"]
    pd.testing.assert_frame_equal(out, zona)


def test_no_imputa_sin_zonas_con_dato_tan_pequenas():
    zona, rentas, zonas, tiempos = _escenario()
    zonas["poblacion"] = np.where(
        zona.query("anio == 2024")["eur_m2_p50"].notna(), 50_000, 100
    )
    out = imputacion.imputar(zona, rentas, zonas, tiempos)
    assert out.attrs["imputacion"]["motivo"].startswith("solo 0 zonas")
