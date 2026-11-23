"""Tests de `titulares` (#93): resumen sobre una tabla a mano y filas sobre la API de ejemplo."""

import copy
import json

import numpy as np
import pandas as pd
import pytest
from test_pipeline_analisis import _bono, _esfuerzo

from mesobra import api_estatica, calculo, pipeline_analisis, titulares


def _api() -> dict:
    """API de ejemplo sin los orígenes B2 y C2, que no tienen tarifa en su `tarifas.json` (solo A y B1)."""
    api = calculo.leer_api(calculo.API_EJEMPLO)
    t = api["tiempos"]
    return {**api, "tiempos": {**t, "origenes": t["origenes"][:3], "tp": t["tp"][:3]}}


def test_resumen_a_mano():
    # destino, origen, corona, sobra, bajo, alto, precio_hora, etiqueta
    f = [
        ("d", "a", "A", 100.0, -50.0, 200.0, None, "referencia"),
        ("d", "b", "A", 50.0, -100.0, 150.0, None, "mismo tiempo"),
        ("d", "c", "B1", 300.0, 100.0, 500.0, 5.0, None),
        ("d", "d", "B1", -20.0, -80.0, 10.0, 10.0, None),
        ("e", "c", "B1", 100.0, -300.0, 500.0, -2.0, None),
        ("e", "d", "B1", -60.0, -120.0, -10.0, 20.0, None),
        (
            "e",
            "e",
            "C2",
            None,
            None,
            None,
            None,
            None,
        ),  # sin alquiler: ni sobra ni precio
    ]
    df = pd.DataFrame(
        f,
        columns=[
            "destino",
            "origen",
            "corona",
            "sobra",
            "sobra_bajo",
            "sobra_alto",
            "precio_hora",
            "etiqueta",
        ],
    )
    r = titulares.resumen(df, neto_hora=8.0)
    # precios 5, 10, -2, 20 (ordenados −2, 5, 10, 20): mediana 7,5; Q1 = 3,25; Q3 = 12,5
    assert (r["n"], r["mediana"], r["q1"], r["q3"]) == (4, 7.5, 3.25, 12.5)
    assert (r["n_mismo_tiempo"], r["n_negativos"]) == (1, 1)
    assert (r["n_encima"], r["pct_encima"]) == (2, 50.0)  # 10 y 20 ≥ 8
    # B1: mediana 7,5 con n = 4 (todos los precios); A y C2 sin precios
    assert r["coronas"] == {"B1": (7.5, 4)} and r["coronas_encima"] == []
    assert r["veredicto"] == "tesis"
    assert titulares.resumen(df, neto_hora=7.0)["veredicto"] == "plan B"
    # sobrante por origen: a 100; b 50; c mediana(300, 100) = 200; d mediana(−20, −60) = −40; e sin dato
    assert (r["n_zonas"], r["n_zonas_negativas"]) == (4, 1)
    # d: sobra_alto mediana(10, −10) = 0, no < 0; sobra_bajo mediana(−80, −120) = −100 < 0
    # a, b: bajo −50 y −100 < 0; c: bajo mediana(100, −300) = −100 < 0
    assert r["banda_zonas_negativas"] == [0, 4]


def test_filas_no_usan_la_brecha_de_contrato_nuevo():
    api, perfil = _api(), titulares.PERFILES[0]
    doble = copy.deepcopy(api)
    for z in doble["alquiler"]["zonas"].values():
        z["factor_brecha"] = 2.0
    pd.testing.assert_frame_equal(
        titulares.filas(api, perfil), titulares.filas(doble, perfil)
    )


def test_filas_con_el_smi():
    api, perfil = _api(), titulares.PERFILES[0]
    df = titulares.filas(api, perfil)
    assert len(df) == 3 and set(df["destino"]) == {"2807901"}  # el polo no entra
    z = df.set_index("origen")
    r = z.loc[z["ref"].iloc[0]]  # la referencia
    otro = z.loc[
        "2807913"
    ]  # 26 min frente a 9 min de ida: más de 5 h/mes de diferencia
    esperado = (otro["sobra"] - r["sobra"]) / (otro["horas"] - r["horas"])
    assert otro["precio_hora"] == pytest.approx(esperado)
    assert np.isnan(r["precio_hora"]) and r["etiqueta"] == calculo.REFERENCIA


def test_titulares_validan_y_son_estimados():
    api = _api()
    res = titulares.titulares(titulares.resumenes(api))
    assert len(res) == 2 * len(titulares.PERFILES)
    obj = pipeline_analisis.analisis_json(_esfuerzo(), _bono())
    api_estatica.validar("analisis.json", {**obj, "titulares": obj["titulares"] + res})
    assert all("estimado" in t["texto"] and t["fuente"] for t in res)
    ipc = f"IPC297196) hasta {api['alquiler']['meta']['ipc_hasta']}"
    assert all(ipc in t["fuente"] for t in res)


def test_titulares_publicados_coinciden_con_su_recalculo():
    # Si cambian zonas, tiempos o el cálculo, hay que regenerar analisis.json (#401)
    datos = pipeline_analisis.APP_DATOS
    publicado = json.loads((datos / "analisis.json").read_text(encoding="utf-8"))
    nuevos = titulares.titulares(titulares.resumenes(calculo.leer_api(datos)))
    assert publicado["titulares"][-len(nuevos) :] == nuevos


def test_sin_precios_falla():
    df = pd.DataFrame({"precio_hora": [None], "corona": ["A"], "sobra": [1.0]})
    with pytest.raises(ValueError, match="sin precio_hora"):
        titulares.resumen(df, neto_hora=8.0)


def test_neto_hora_smi_y_pareja():
    api = _api()
    horas = api["tarifas"]["semanas_mes"] * 40  # 151,33 h/mes
    smi, _, pareja, *_ = (r for _, r in titulares.resumenes(api))
    solo = {**api["hogares"]["perfiles"]["solo"], "perfil": "solo"}
    assert smi["neto_hora"] == pytest.approx(
        calculo.neto_mes(api["netos"], 17094, solo) / horas
    )
    par = {**api["hogares"]["perfiles"]["pareja"], "perfil": "pareja"}
    # dos sueldos iguales: el neto del hogar entre 2 × horas = el neto de uno entre horas
    assert pareja["neto_hora"] == pytest.approx(
        calculo.neto_mes(api["netos"], titulares.EAES, par) / horas
    )


def test_umbral_exacto_cuenta_como_encima():
    df = pd.DataFrame(
        {
            "precio_hora": [8.0, 7.99, 8.01],
            "corona": ["A", "A", "A"],
            "origen": ["a", "b", "c"],
            "sobra": [1.0, 1.0, 1.0],
            "sobra_bajo": [0.0, 0.0, 0.0],
            "sobra_alto": [2.0, 2.0, 2.0],
            "etiqueta": [None, None, None],
        }
    )
    r = titulares.resumen(df, neto_hora=8.0)  # mediana de A = 8,0 = neto/hora
    assert r["n_encima"] == 2 and r["coronas_encima"] == ["A"]
    assert r["veredicto"] == "plan B"


def test_madre_y_enfermera_desde_sus_fuentes():
    # P50 mujeres administrativas Madrid 2022 (t=36846) × mediana mujeres Madrid 2024 / 2022 (t=28191)
    assert titulares.MADRE == 23874.79
    # total año de la fila del BOCM-20260209-6, anexo V tabla 2.1.a, igual al del BOCM-20260630-6, anexo II
    assert titulares.ENFERMERA == 30421.38
    perfiles = {p["fuente"]: p for p in titulares.PERFILES}
    madre = perfiles[titulares.FUENTE_MADRE]
    enfermera = perfiles[titulares.FUENTE_ENFERMERA]
    assert (
        madre["sueldos"] == [(titulares.MADRE, 5)] and madre["perfil"] == "monoparental"
    )
    assert (
        enfermera["sueldos"] == [(titulares.ENFERMERA, 5)] and enfermera["edad"] == 26
    )
    assert all(s in madre["fuente"] for s in ("estimado", "36846", "28191"))
    assert "sin trienios, noches ni guardias" in enfermera["fuente"]


def test_joven_mediano_desde_las_tablas_del_ine():
    # P50 de 25-34 en Madrid 2022 (t=36850) × media del tramo 2024 / 2022 (t=28201), redondeado al céntimo
    assert titulares.JOVEN == 25209.48
    i, joven = next(
        (i, p)
        for i, p in enumerate(titulares.PERFILES)
        if p["fuente"] is titulares.FUENTE_JOVEN
    )
    assert joven["sueldos"] == [(titulares.JOVEN, 5)]
    assert all(s in joven["fuente"] for s in ("estimado", "36850", "28201"))
    api = _api()
    horas = api["tarifas"]["semanas_mes"] * 40
    r = list(titulares.resumenes(api))[i][1]
    solo = {**api["hogares"]["perfiles"]["solo"], "perfil": "solo"}
    assert r["neto_hora"] == pytest.approx(
        calculo.neto_mes(api["netos"], titulares.JOVEN, solo) / horas
    )
