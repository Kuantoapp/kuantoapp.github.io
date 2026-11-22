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
    alquiler = 19.6 * 1.19 * 45  # contrato nuevo: P50 × factor_brecha del fixture
    assert z["alquiler"] == pytest.approx(alquiler)
    assert z["alquiler_contrato"] == pytest.approx(19.6 * 45)
    assert z["transporte"] == 16.57  # 10 viajes prorrateado, A-A 3 días
    assert z["cesta"] == pytest.approx(275.37 + 81.08 + 43.72)
    assert z["sobra"] == pytest.approx(neto - alquiler - 16.57 - 400.17)
    assert z["horas"] == pytest.approx(9 * 2 * 3 * 3.7833 / 60)
    assert z["esfuerzo"] == pytest.approx(alquiler / neto)


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
    assert _zona(_entrada(hogar=joven), "28065")["transporte"] == 9.31
    assert (
        _zona(_entrada(hogar=joven, escenario={"tarifas": "sin_descuento"}), "28065")[
            "transporte"
        ]
        == 18.61
    )
    assert (
        _zona(_entrada(hogar=joven, escenario={"edad": 26}), "28065")["transporte"]
        == 16.57
    )
    base, caro = (
        _zona(_entrada(escenario={"subida_alquiler": s}), "28065") for s in (0, 10)
    )
    assert caro["alquiler"] == pytest.approx(base["alquiler"] * 1.1)
    assert (
        _zona(_entrada(sueldos=[CENTRO | {"viajes_dia": 4}]), "2807901")["transporte"]
        == 30.43
    )


def test_banda_con_percentiles_e_intervalo() -> None:
    api = copy.deepcopy(API)
    api["alquiler"]["zonas"]["28065"] |= {"origen": "estimado", "ic": [9.0, 15.0]}
    obs, est = _zona(_entrada(), "28065"), _zona(_entrada(), "28065", api)
    k = 1.035 * 1.19 * 45
    fijo = obs["neto"] - obs["transporte"] - obs["cesta"]
    assert obs["sobra_banda"] == pytest.approx([fijo - 14.3 * k, fijo - 11.0 * k])
    assert est["sobra_banda"] == pytest.approx([fijo - 15.0 * k, fijo - 9.0 * k])
    assert obs["sobra_banda"][0] < obs["sobra"] < obs["sobra_banda"][1]


def test_alquiler_de_contrato_nuevo_y_referencia_de_contratos_en_vigor() -> None:
    z = _zona(_entrada(), "28065")
    assert z["alquiler"] == pytest.approx(12.6 * 1.035 * 1.19 * 45)
    assert z["alquiler"] / z["alquiler_contrato"] == pytest.approx(1.19)
    assert z["sobra_contrato"] - z["sobra"] == pytest.approx(
        z["alquiler"] - z["alquiler_contrato"]
    )
    assert z["sobra_contrato"] > z["sobra"]


def test_api_precio_contrato_quita_la_brecha_sin_tocar_la_original() -> None:
    sin = calculo.api_precio_contrato(API)
    a, b = _zona(_entrada(), "28065"), _zona(_entrada(), "28065", sin)
    assert b["alquiler"] == pytest.approx(b["alquiler_contrato"])
    assert b["alquiler"] == pytest.approx(a["alquiler_contrato"])
    assert API["alquiler"]["zonas"]["28065"]["factor_brecha"] == 1.19


@pytest.mark.parametrize("brecha", [None, 0, -1.2, "1.2", True])
def test_factor_brecha_ausente_o_invalido_falla(brecha: object) -> None:
    api = copy.deepcopy(API)
    api["alquiler"]["zonas"]["28065"]["factor_brecha"] = brecha
    with pytest.raises(ValueError, match="factor_brecha"):
        calculo.calcular(api, _entrada())
    del api["alquiler"]["zonas"]["28065"]["factor_brecha"]
    with pytest.raises(ValueError, match="factor_brecha"):
        calculo.calcular(api, _entrada())


def test_zona_sin_dato_da_nulos() -> None:
    api = copy.deepcopy(API)
    api["alquiler"]["zonas"]["2807913"] = api["alquiler"]["zonas"]["28001"]
    r = calculo.calcular(api, _entrada())
    z = r["zonas"]["2807913"]
    assert [
        z[k]
        for k in (
            "alquiler",
            "alquiler_contrato",
            "sobra",
            "sobra_contrato",
            "sobra_banda",
            "esfuerzo",
            "precio_hora",
        )
    ] == [None] * 7
    assert z["horas"] > 0
    assert r["ref"] == "2807901"
    assert r["zonas"]["2807901"]["etiqueta"] == "referencia"


def test_sin_ruta_no_hay_coste_ni_sobra() -> None:
    api = copy.deepcopy(API)
    api["tiempos"]["tp"][1][0] = None
    z = _zona(_entrada(), "2807913", api)
    assert [z[k] for k in ("horas", "transporte", "sobra", "precio_hora")] == [None] * 4
    assert z["alquiler"] is not None
    assert z["viajes"] == [{"horas": None, "coste": None, "titulo": None}]


def test_cesta_con_el_hogar_del_visitante() -> None:
    uc = API["hogares"]["cesta_uc"]
    comparte = {"adultos": 1, "hijos": 0, "personas_comparten": 3}
    assert calculo.cesta(uc, comparte, 1.0) == pytest.approx(
        275.37 + (81.08 + 43.72) * 2 / 3
    )
    # el factor del tramo solo toca la alimentación
    assert calculo.cesta(uc, comparte, 0.5) == pytest.approx(
        275.37 * 0.5 + (81.08 + 43.72) * 2 / 3
    )


# Cortes de la EPF: un céntimo a cada lado de cada uno (#312). Fixture: 0,7 · 0,8 · 0,85 · 0,95 · 0,9 · 0,97 · 1,02 · 1,15.
CORTES = [
    (0.01, 0.7), (499.99, 0.7), (500, 0.8), (999.99, 0.8), (1000, 0.85),
    (1499.99, 0.85), (1500, 0.95), (1999.99, 0.95), (2000, 0.9), (2499.99, 0.9),
    (2500, 0.97), (2999.99, 0.97), (3000, 1.02), (4999.99, 1.02), (5000, 1.15),
    (90000, 1.15),
]  # fmt: skip


@pytest.mark.parametrize(("neto", "factor"), CORTES)
def test_tramo_de_la_cesta_en_los_cortes(neto: float, factor: float) -> None:
    assert calculo.tramo_cesta(API["hogares"]["cesta_tramos"], neto)["factor"] == factor


def test_escenario_cesta_del_tramo() -> None:
    """Con 1.400 €/mes de neto propio (tramo 1.000-1.499, 0,85) en «comparte» solo baja la alimentación."""
    sueldo = {**CENTRO, "neto_mes": 1400}
    sueldo.pop("bruto", None)
    hogar = {"perfil": "comparte", "edad": 28}
    media = _zona(_entrada(hogar=hogar, sueldos=[sueldo]), "2807913")
    tramo = _zona(
        _entrada(hogar=hogar, sueldos=[sueldo], escenario={"cesta": "tramo"}), "2807913"
    )
    assert media["cesta"] - tramo["cesta"] == pytest.approx(275.37 * 0.15)
    assert tramo["sobra"] - media["sobra"] == pytest.approx(275.37 * 0.15)


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
        ({"escenario": {"cesta": "baja"}}, "cesta"),
        ({"sueldos": [CENTRO | {"dias": 6}]}, "dias = 6"),
        ({"sueldos": [CENTRO | {"modo": "bici"}]}, "modo 'bici'"),
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


def _con_clave(api: dict, origen: str, destino: str, clave: str | None) -> dict:
    """Copia de `api` con la clave de tarifa del par; `None` la quita."""
    api = copy.deepcopy(api)
    t = api["tarifas"]
    k = None if clave is None else t["claves"].index(clave)
    t["clave_tarifa"][t["origenes"].index(origen)][t["destinos"].index(destino)] = k
    return api


def test_la_clave_de_un_polo_sale_de_su_columna() -> None:
    polo = CENTRO | {"destino": "polo:ifema"}
    assert _zona(_entrada(sueldos=[polo]), "2807901")["transporte"] == 16.57
    api = _con_clave(API, "2807901", "polo:ifema", "A-C2|interurbano")
    assert _zona(_entrada(sueldos=[polo]), "2807901", api)["transporte"] == 45.78


def test_un_par_sin_clave_falla_claro() -> None:
    api = _con_clave(API, "2807901", "2807901", None)
    with pytest.raises(ValueError, match="sin clave de tarifa"):
        calculo.calcular(api, _entrada())


def test_edad_por_sueldo_y_colectivo_de_cada_persona() -> None:
    h = {"perfil": "pareja", "edad": 30}
    joven = CENTRO | {"edad": 24, "dias": 5}
    gral = CENTRO | {"dias": 5}
    z = _zona(_entrada(hogar=h, sueldos=[joven, gral]), "2807901")
    assert z["transporte"] == pytest.approx(9.31 + 27.62)  # Abono Joven + 10 viajes
    z = _zona(
        _entrada(hogar=h, sueldos=[joven | {"discapacidad": True}, gral]), "2807901"
    )
    assert z["transporte"] == pytest.approx(7.44 + 27.62)  # discapacidad ≥ 65 %: BOCM
    # el escenario de edad es el valor por defecto de quien no tiene la suya
    z = _zona(
        _entrada(hogar=h, sueldos=[joven, gral], escenario={"edad": 26}), "2807901"
    )
    assert z["transporte"] == pytest.approx(9.31 + 27.62)


def test_hijos_por_edad_suman_abono_joven_solo_de_15_a_25() -> None:
    cinco = CENTRO | {"dias": 5}
    h = {"perfil": "solo", "edad": 33, "hijos": 2}
    base = _zona(_entrada(hogar=h, sueldos=[cinco]), "2807901")["transporte"]
    assert base == 27.62  # sin edades_hijos no se cuentan
    for edades, extra in [([3, 14], 0), ([14, 15], 9.31), ([15, 25], 2 * 9.31)]:
        z = _zona(
            _entrada(hogar=h | {"edades_hijos": edades}, sueldos=[cinco]), "2807901"
        )
        assert z["transporte"] == pytest.approx(base + extra)


def test_el_abono_joven_del_hijo_no_lleva_viajes_no_laborables() -> None:
    # desde una zona lejana (A-C2) el Abono Joven con 16 viajes de ocio costaría más de 9,31 €
    h = {"perfil": "solo", "edad": 33, "hijos": 1, "no_laborables": 16}
    sin, con = (
        _zona(_entrada(hogar=h | extra, zonas=["28001"]), "28001")["transporte"]
        for extra in ({}, {"edades_hijos": [18]})
    )
    assert con == pytest.approx(sin + 9.31)


def test_viajes_no_laborables_y_familia_numerosa() -> None:
    cinco = CENTRO | {"dias": 5}
    z = _zona(
        _entrada(
            hogar={"perfil": "solo", "edad": 30, "no_laborables": 16}, sueldos=[cinco]
        ),
        "2807901",
    )
    assert z["transporte"] > 27.62
    h = {"perfil": "pareja", "edad": 40, "hijos": 2, "familia": "fn_general"}
    z = _zona(_entrada(hogar=h, sueldos=[cinco]), "2807901")
    assert z["transporte"] == 21.94  # columna de familia numerosa general del BOCM


@pytest.mark.parametrize(
    ("hogar", "sueldo", "mensaje"),
    [
        ({"edades_hijos": [7]}, {}, "edades_hijos"),
        ({"hijos": 1, "edades_hijos": [26]}, {}, "edades_hijos"),
        ({"familia": "fn_general"}, {}, "familia numerosa con 0 hijos"),
        ({"familia": "grande"}, {}, "familia = 'grande'"),
        ({"no_laborables": 4}, {}, "no_laborables"),
        ({"no_laborables": False}, {}, "no_laborables"),
        ({}, {"discapacidad": 1}, "discapacidad"),
        ({}, {"edad": 15}, "edad = 15"),
    ],
)
def test_entradas_de_transporte_invalidas(
    hogar: dict, sueldo: dict, mensaje: str
) -> None:
    entrada = _entrada(
        hogar={"perfil": "solo", "edad": 30, **hogar}, sueldos=[CENTRO | sueldo]
    )
    with pytest.raises(ValueError, match=mensaje):
        calculo.calcular(API, entrada)


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
        "cesta": "media",
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


def test_cuatro_viajes_en_un_par_sin_zona_a_cuenta_la_a() -> None:
    # B1 → B2 a 5 días: con Metro de A el abono tiene que cubrir desde A: A-B2 (43,20 € × 335/360 = 40,20)
    sueldo = {
        "dias": 5,
        "viajes_dia": 4,
        "edad": 30,
        "colectivo": "ordinario",
        "no_laborables": 0,
    }
    cuatro = calculo.tarifa(API, "28065", "28092", sueldo, "vigente_2026")
    assert cuatro["coste_mes"] == 40.2
    dos = calculo.tarifa(
        API, "28065", "28092", sueldo | {"viajes_dia": 2}, "vigente_2026"
    )
    assert dos["coste_mes"] < cuatro["coste_mes"]


def test_cuatro_viajes_dentro_de_una_zona_pagan_por_viaje_el_rango_real() -> None:
    # C2 → C2, 2 días: 15,13 viajes × (0,51 interurbano de una zona + 0,73 Metro de A) = 18,77 €
    # (BOCM-20251231-2, pág. 67); el abono desde A (A-C2) saldría a 45,78 €
    sueldo = {
        "dias": 2,
        "viajes_dia": 4,
        "edad": 30,
        "colectivo": "ordinario",
        "no_laborables": 0,
    }
    z = calculo.tarifa(API, "28001", "28001", sueldo, "vigente_2026")
    assert z["coste_mes"] == 18.77


@pytest.mark.parametrize(("edad", "coste"), [(25, 9.31), (26, 27.62)])
def test_edad_de_un_sueldo_en_el_borde_del_abono_joven(edad: int, coste: float) -> None:
    sueldo = CENTRO | {"edad": edad, "dias": 5}
    z = _zona(
        _entrada(hogar={"perfil": "pareja", "edad": 30}, sueldos=[sueldo]), "2807901"
    )
    assert z["transporte"] == coste


def test_hijos_de_familia_numerosa_especial_pagan_su_abono_joven() -> None:
    h = {"perfil": "pareja", "edad": 40, "hijos": 2, "familia": "fn_especial"}
    cinco = [CENTRO | {"dias": 5}]
    sin = _zona(_entrada(hogar=h, sueldos=cinco), "2807901")["transporte"]
    con = _zona(
        _entrada(hogar=h | {"edades_hijos": [15, 16]}, sueldos=cinco), "2807901"
    )["transporte"]
    assert con == pytest.approx(
        sin + 2 * 4.65
    )  # 5,00 € × 335/30 ÷ 12 (BOCM-20251231-2, pág. 66)
