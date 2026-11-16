"""Tests del cálculo de referencia (#73) sobre los ejemplos de tests/fixtures/api/."""

import copy
import json

import pytest

from mesobra import calculo

API = calculo.leer_api(calculo.API_EJEMPLO)
CASOS = json.loads(calculo.CASOS.read_text("utf-8"))["casos"]
CENTRO = {"bruto": 22000, "destino": "2807901", "dias": 3, "modo": "tp"}
ZONAS = ["2807901", "2807913", "28065"]


def _entrada(**cambios: object) -> dict:
    return {
        "hogar": {"perfil": "solo", "edad": 30},
        "sueldos": [CENTRO],
        "zonas": ZONAS,
    } | cambios


def _zona(entrada: dict, zona: str, api: dict = API) -> dict:
    return calculo.calcular(api, entrada)["zonas"][zona]


def test_caso_de_control_de_la_ficha() -> None:
    assert calculo.precio_hora(500, 70, 300, 20) == (pytest.approx(4.00), None)


def test_menos_de_5_horas_es_mismo_tiempo() -> None:
    assert calculo.precio_hora(500, 24.9, 300, 20) == (None, "mismo tiempo")
    assert calculo.precio_hora(None, 70, 300, 20) == (None, None)


def test_casos_de_referencia_al_dia() -> None:
    assert len(CASOS) >= 12
    for c in CASOS:
        esperado = {k: c[k] for k in ("salida", "error") if k in c}
        obtenido = json.loads(json.dumps(calculo.resolver(API, c["entrada"])))
        assert obtenido == esperado, (
            f"{c['nombre']}: regenera con python -m mesobra.calculo"
        )


def test_un_sueldo_a_mano() -> None:
    z = _zona(_entrada(), "2807901")
    neto = (13447.5 + 7000 / 15000 * (23795.0 - 13447.5)) / 12
    assert z["neto"] == pytest.approx(neto)
    assert z["alquiler"] == pytest.approx(19.6 * 45)
    assert z["transporte"] == 21.9
    assert z["cesta"] == pytest.approx(275.37 + 81.08)
    assert z["sobra"] == pytest.approx(neto - 19.6 * 45 - 21.9 - 356.45)
    assert z["horas"] == pytest.approx(9 * 2 * 3 * 3.7833 / 60)
    assert z["esfuerzo"] == pytest.approx(19.6 * 45 / neto)


def test_referencia_por_defecto_y_precio_hora() -> None:
    r = calculo.calcular(API, _entrada())
    assert r["ref"] == "2807901"
    a, b = r["zonas"]["2807901"], r["zonas"]["2807913"]
    assert b["precio_hora"] == pytest.approx(
        (b["sobra"] - a["sobra"]) / (b["horas"] - a["horas"])
    )


def test_dos_sueldos_suman_neto_horas_y_transporte() -> None:
    coche = {"bruto": 18000, "destino": "polo:ifema", "dias": 4, "modo": "coche"}
    h = {"perfil": "pareja", "edad": 32}
    z2, z1 = (
        _zona(_entrada(hogar=h, sueldos=s), "2807913")
        for s in ([CENTRO, coche], [CENTRO])
    )
    km = 2 * 16.8 * 4 * 3.7833 * 0.26
    assert z2["transporte"] == pytest.approx(z1["transporte"] + km)
    assert z2["horas"] == pytest.approx(z1["horas"] + 30 * 2 * 4 * 3.7833 / 60)
    assert z2["neto"] > z1["neto"]
    with pytest.raises(ValueError, match="sueldos para 1 adultos"):
        calculo.calcular(API, _entrada(sueldos=[CENTRO, coche]))


def test_abono_joven_y_escenarios() -> None:
    joven = {"perfil": "solo", "edad": 25}
    assert _zona(_entrada(hogar=joven), "28065")["transporte"] == 10.0
    assert (
        _zona(_entrada(hogar=joven, escenario={"tarifas": "sin_descuento"}), "28065")[
            "transporte"
        ]
        == 20.0
    )
    assert (
        _zona(_entrada(hogar=joven, escenario={"edad": 26}), "28065")["transporte"]
        == 21.9
    )
    base, caro = (
        _zona(_entrada(escenario={"subida_alquiler": s}), "28065") for s in (0, 10)
    )
    assert caro["alquiler"] == pytest.approx(base["alquiler"] * 1.1)
    assert (
        _zona(_entrada(sueldos=[CENTRO | {"viajes_dia": 4}]), "2807901")["transporte"]
        == 32.7
    )


def test_banda_con_percentiles_e_intervalo() -> None:
    api = copy.deepcopy(API)
    api["alquiler"]["zonas"]["28065"] |= {"origen": "estimado", "ic": [9.0, 15.0]}
    obs, est = _zona(_entrada(), "28065"), _zona(_entrada(), "28065", api)
    k = 1.035 * 45
    fijo = obs["neto"] - obs["transporte"] - obs["cesta"]
    assert obs["sobra_banda"] == pytest.approx([fijo - 14.3 * k, fijo - 11.0 * k])
    assert est["sobra_banda"] == pytest.approx([fijo - 15.0 * k, fijo - 9.0 * k])
    assert obs["sobra_banda"][0] < obs["sobra"] < obs["sobra_banda"][1]


def test_zona_sin_dato_da_nulos() -> None:
    api = copy.deepcopy(API)
    api["alquiler"]["zonas"]["2807913"] = api["alquiler"]["zonas"]["28001"]
    r = calculo.calcular(api, _entrada())
    z = r["zonas"]["2807913"]
    assert [
        z[k] for k in ("alquiler", "sobra", "sobra_banda", "esfuerzo", "precio_hora")
    ] == [None] * 5
    assert z["horas"] > 0
    assert r["ref"] == "2807901"


def test_cesta_con_el_hogar_del_visitante() -> None:
    uc = API["hogares"]["cesta_uc"]
    comparte = {"adultos": 1, "hijos": 0, "personas_comparten": 3}
    assert calculo.cesta(uc, comparte) == pytest.approx(275.37 + 81.08 * 2 / 3)


def test_monoparental_por_hogar_y_pareja_con_hijos() -> None:
    netos = API["netos"]
    assert calculo.neto_mes(netos, 15000, {"adultos": 1, "hijos": 1}) == pytest.approx(
        13897.5 / 12
    )
    assert calculo.neto_mes(netos, 15000, {"adultos": 2, "hijos": 1}) == pytest.approx(
        13667.5 / 12
    )
    assert calculo.neto_mes(netos, 30000, {"adultos": 2, "hijos": 0}) == pytest.approx(
        23795.0 / 12
    )


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"sueldos": [CENTRO | {"bruto": 120001}]}, "fuera de la tabla"),
        ({"hogar": {"perfil": "solo", "edad": 30, "hijos": 3}}, "hijos = 3"),
        ({"hogar": {"perfil": "solo", "edad": 65}}, "edad = 65"),
        ({"sueldos": [CENTRO | {"dias": 6}]}, "dias = 6"),
        ({"sueldos": [CENTRO | {"modo": "bici"}]}, "modo 'bici'"),
        ({"sueldos": [CENTRO | {"destino": "polo:ifema"}]}, "sin tarifa"),
        ({"zonas": ["28092"]}, "sin tarifa"),
        ({"hogar": {"perfil": "otro", "edad": 30}}, "perfil desconocido"),
    ],
)
def test_entradas_invalidas_fallan(cambios: dict, mensaje: str) -> None:
    with pytest.raises(ValueError, match=mensaje):
        calculo.calcular(API, _entrada(**cambios))
