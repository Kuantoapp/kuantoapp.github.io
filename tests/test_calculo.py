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
    assert r["zonas"]["2807901"]["etiqueta"] == "referencia"


def test_sin_ruta_no_hay_coste_ni_sobra() -> None:
    api = copy.deepcopy(API)
    api["tiempos"]["tp"][1][0] = None
    z = _zona(_entrada(), "2807913", api)
    assert [z[k] for k in ("horas", "transporte", "sobra", "precio_hora")] == [None] * 4
    assert z["alquiler"] is not None


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
        ({"zonas": ["28092"]}, "sin tarifa"),
        ({"hogar": {"perfil": "otro", "edad": 30}}, "perfil desconocido"),
        ({"sueldos": [CENTRO | {"neto_mes": 1500}]}, "uno de los dos"),
        (
            {
                "hogar": {"perfil": "solo", "edad": 30, "hijos": 3},
                "sueldos": [
                    {"neto_mes": 1500, "destino": "2807901", "dias": 3, "modo": "tp"}
                ],
            },
            "hijos = 3",
        ),
        (
            {"sueldos": [{"destino": "2807901", "dias": 3, "modo": "tp"}]},
            "uno de los dos",
        ),
        ({"escenario": {"subida": 10}}, "claves desconocidas"),
        ({"escenario": {"subida_alquiler": -150}}, "mayor que"),
        (
            {
                "sueldos": [CENTRO | {"modo": "coche"}],
                "ref": "28001",
                "zonas": ["2807901"],
            },
            "referencia 28001",
        ),
    ],
)
def test_entradas_invalidas_fallan(cambios: dict, mensaje: str) -> None:
    with pytest.raises(ValueError, match=mensaje):
        calculo.calcular(API, _entrada(**cambios))


def test_la_corona_de_un_polo_es_la_de_su_zona() -> None:
    assert (
        calculo._corona(API, "2807901", "polo:ifema") == "A"
    )  # zona_id 2807913, corona A
    api = copy.deepcopy(API)
    polo = next(d for d in api["tiempos"]["destinos"] if d["tipo"] == "polo")
    polo["zona_id"] = "28065"
    assert calculo._corona(api, "2807901", "polo:ifema") == "B1"
    polo["zona_id"] = "28092"  # la corona B2 no tiene tarifa en el ejemplo
    with pytest.raises(ValueError, match="sin tarifa"):
        calculo._corona(api, "2807901", "polo:ifema")


@pytest.mark.parametrize("edad", [16, 64])
def test_edades_limite_calculan(edad: int) -> None:
    assert calculo.calcular(API, _entrada(hogar={"perfil": "solo", "edad": edad}))[
        "ref"
    ]


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"hogar": {"perfil": "solo", "edad": 15}}, "edad = 15"),
        (
            {"hogar": {"perfil": "solo", "edad": 70}, "escenario": {"edad": 30}},
            "edad = 70",
        ),
        ({"sueldos": [CENTRO | {"bruto": 14999.99}]}, "fuera de la tabla"),
    ],
)
def test_limites_fallan(cambios: dict, mensaje: str) -> None:
    with pytest.raises(ValueError, match=mensaje):
        calculo.calcular(API, _entrada(**cambios))


@pytest.mark.parametrize(
    ("entrada", "mensaje"),
    [
        (_entrada(zonas=["99999"]), "zonas sin entrada"),
        (_entrada(ref="99999"), "zonas sin entrada"),
        ({"hogar": {"perfil": "solo", "edad": 30}}, "entrada sin"),
        ({"sueldos": [CENTRO]}, "entrada sin"),
        (_entrada(sueldos=[{"bruto": 22000, "modo": "tp"}]), "sueldo sin"),
        (_entrada(sueldos=[CENTRO | {"bruto": "22000"}]), "debe ser un número"),
        (_entrada(sueldos=[CENTRO | {"destino": "00000"}]), "no tiene tp"),
        (_entrada(ref=""), "zonas sin entrada"),
        (_entrada(ref=0), "zonas y ref"),
        (_entrada(zonas="2807901"), "zonas: debe ser"),
        (_entrada(zonas=[2807901]), "zonas y ref"),
        (_entrada(hogar="solo"), "hogar: debe ser"),
        (_entrada(hogar={"perfil": ["solo"], "edad": 30}), "perfil desconocido"),
        (_entrada(hogar={"perfil": "solo", "edad": 30, "m2": "40"}), "m2 = '40'"),
        (_entrada(hogar={"perfil": "solo", "edad": 30, "m2": None}), "m2 = None"),
        (_entrada(sueldos=None), "sueldos: debe ser"),
        (_entrada(sueldos=["tp"]), "cada sueldo"),
        (_entrada(sueldos=[CENTRO | {"viajes_dia": 2.0}]), "viajes_dia"),
        (_entrada(sueldos=[{**CENTRO, "bruto": float("nan")}]), "fuera de la tabla"),
        (_entrada(escenario=["sin_descuento"]), "escenario: debe ser"),
        (_entrada(escenario={"tarifas": ["x"]}), "inválido"),
        (_entrada(escenario={"subida_alquiler": float("inf")}), "mayor que"),
        (
            _entrada(sueldos=[{"neto_mes": float("inf")} | CENTRO | {"bruto": None}]),
            "uno de los dos",
        ),
        (
            _entrada(
                sueldos=[
                    {k: v for k, v in CENTRO.items() if k != "bruto"}
                    | {"neto_mes": float("inf")}
                ]
            ),
            "neto_mes = inf",
        ),
    ],
)
def test_entradas_incompletas_dan_value_error(entrada: dict, mensaje: str) -> None:
    with pytest.raises(ValueError, match=mensaje):
        calculo.calcular(API, entrada)
    assert "error" in calculo.resolver(API, entrada)


def test_escenario_aplicado_en_la_salida() -> None:
    r = calculo.calcular(API, _entrada(escenario={"subida_alquiler": 5}))
    assert r["escenario"] == {
        "tarifas": "vigente_2026",
        "subida_alquiler": 5,
        "edad": 30,
    }


NETOS_REALES = calculo.RAIZ / "app/datos/netos.json"


@pytest.mark.skipif(not NETOS_REALES.exists(), reason="sin app/datos/netos.json")
@pytest.mark.parametrize(
    ("bruto", "hogar", "tolerancia"),
    [
        (22000, {"adultos": 1, "hijos": 0}, 0.01),
        (22100, {"adultos": 2, "hijos": 1}, 1.0),
        (37777, {"adultos": 1, "hijos": 2}, 1.0),
    ],
)
def test_neto_cuadra_con_neto_py(bruto: int, hogar: dict, tolerancia: float) -> None:
    from mesobra import neto

    netos = json.loads(NETOS_REALES.read_text("utf-8"))
    mono = hogar["adultos"] == 1 and hogar["hijos"] >= 1
    exacto = float(neto.neto_anual(bruto, hijos=hogar["hijos"], monoparental=mono)) / 12
    assert calculo.neto_mes(netos, bruto, hogar) == pytest.approx(
        exacto, abs=tolerancia
    )
