"""Tests de `simulacion` (#101): umbrales, topes, base imponible a mano, propiedades y contrato."""

import json
import re
import unicodedata
from decimal import Decimal as D
from itertools import product

import pandas as pd
import pytest

from mesobra import bono, calculo, contratos, neto, simulacion, titulares
from mesobra.simulacion import requisitos, tope


def _api() -> dict:
    """API de ejemplo sin los orígenes B2 y C2, que no tienen tarifa en su `tarifas.json` (solo A y B1)."""
    api = calculo.leer_api(calculo.API_EJEMPLO)
    t = api["tiempos"]
    return {**api, "tiempos": {**t, "origenes": t["origenes"][:3], "tp": t["tp"][:3]}}


def test_umbral_de_ingresos():
    assert requisitos(30, D(25201), D(0), D(600)) == [
        "ingresos > 3 × IPREM (RD art. 6.1.d; Acuerdo, art. 4.1.d)"
    ]
    assert requisitos(30, D(25199), D(0), D(600)) == []
    assert requisitos(30, D(25200), D(0), D(600)) == []


@pytest.mark.parametrize(
    ("renta", "limite", "entra"),
    [(601, 600, False), (600, 600, True), (901, 900, False), (900, 900, True)]
    + [(301, 300, False), (300, 300, True), (451, 450, False), (450, 450, True)],
)
def test_umbral_de_renta(renta, limite, entra):
    assert (requisitos(30, D(0), D(renta), D(limite)) == []) is entra


def test_topes_por_municipio_y_tipo():
    assert [tope("28079", t) for t in ("vivienda", "habitacion")] == [900, 450]
    assert [tope("28001", t) for t in ("vivienda", "habitacion")] == [600, 300]


def test_edad():
    assert requisitos(35, D(0), D(0), None) == []
    for edad in (36, 17):
        assert requisitos(edad, D(0), D(0), None) == ["edad (RD 42/2022, art. 6.1.a)"]


def test_requisitos_devuelve_cada_articulo_que_falla():
    f = requisitos(40, D(30000), D(1000), D(600))
    assert len(f) == 3 and "6.1.a" in f[0] and "6.1.d" in f[1] and "art. 8" in f[2]


def _clave(nombre: str) -> str:
    """Letras sin tildes ordenadas: iguala «El Boalo» con «Boalo, El» y «En medio» con «Enmedio»."""
    sin = unicodedata.normalize("NFD", nombre.lower())
    return "".join(sorted(c for c in sin if c.isalpha() and ord(c) < 128))


def test_lista_de_55_municipios():
    t = simulacion.TOPE_900_2024
    assert len(t) == 55 == len(set(simulacion.NOMBRES_ANEXO_II))  # Anexo II en bruto
    assert set(bono.TOPE_900) <= set(t)


def test_nombres_de_la_faq_casan_con_zonas_geojson():
    ruta = calculo.RAIZ / "app/datos/zonas.geojson"
    if not ruta.exists():
        pytest.skip("sin app/datos/zonas.geojson")
    props = [f["properties"] for f in json.loads(ruta.read_text("utf-8"))["features"]]
    por_nombre = {
        _clave(p["nombre"]): p["municipio_id"]
        for p in props
        if p["tipo"] == "municipio"
    }
    por_nombre.setdefault(_clave("Madrid"), "28079")  # Madrid va por distritos
    # erratas del Anexo II: «Carmarma» y «Paracuellos del Jarama»
    errata = {
        "Carmarma de Esteruelas": "Camarma de Esteruelas",
        "Paracuellos del Jarama": "Paracuellos de Jarama",
    }
    codigos = {
        por_nombre[_clave(errata.get(n, n))] for n in simulacion.NOMBRES_ANEXO_II
    }
    assert codigos == set(simulacion.TOPE_900_2024)


def test_base_imponible_a_mano():
    # SMI: cotización 6,5 % = 1.111,11; rnt 15.982,89; art. 20 = 7.302 − 1,75 × (15.982,89 − 14.852) = 5.322,94
    assert neto._reduccion_art20(D("15982.89")) == D("5322.94")
    assert (
        simulacion.base_imponible(17094)
        == D("15982.89") - 2000 - D("5322.94")
        == D("8659.95")
    )
    # 25.209,48: cotización 1.638,62; rnt 23.570,86 ≥ 19.747,50: art. 20 = 0
    assert neto._reduccion_art20(D("23570.86")) == 0
    assert simulacion.base_imponible(25209.48) == D("21570.86")


RENTAS = [0, 100, 299.99, 300, 450, 600, 601, 900, 901, 1500]
INGRESOS = [0, 8000, 25199, 25200, 25201, 40000]


def _fila(renta=500.0, transporte=0.0, horas=0.0, **kw) -> dict:
    return {
        "municipio_id": "28079", "tipo": "vivienda", "edad": 30, "ingresos_base": 10000.0,
        "renta": renta, "transporte": transporte, "horas": horas, "neto": 1000.0,
        "horas_trab": 151.3, "beneficiarios": 1, **kw,
    }  # fmt: skip


def test_subir_renta_nunca_hace_entrar_por_tope():
    for tipo, ing in product(("vivienda", "habitacion"), INGRESOS):
        ok = [
            not requisitos(30, D(ing), D(str(r)), tope("28079", tipo)) for r in RENTAS
        ]
        assert ok == sorted(ok, reverse=True)


def test_subir_ingresos_nunca_hace_entrar():
    for c in simulacion.CRITERIOS:
        ok = [
            not simulacion.fallos(
                _fila(ingresos_base=float(i)), c, "ingresos_base", D("0.3")
            )
            for i in INGRESOS
        ]
        assert ok == sorted(ok, reverse=True)


def test_cuantia_en_rango_y_horas_incluyen_alquiler_transporte():
    for renta, transp, horas in product(RENTAS, (0.0, 80.0, 300.0), (0.0, 20.0, 100.0)):
        d = {}
        for c in simulacion.CRITERIOS:
            f = _fila(renta=float(renta), transporte=transp, horas=horas)
            d[c] = not simulacion.fallos(f, c, "ingresos_base", D("0.3"))
        assert not d["alquiler_transporte"] or d["horas_viaje"]
        t = pd.DataFrame([{"perfil": "p", "edad": 30, "tipo": "vivienda", "ingresos_base": 1.0}
                          | _fila(renta=float(renta), transporte=transp, horas=horas)])  # fmt: skip
        s = simulacion._evaluar(t, "base", "renta", D("0.3"))
        assert s["eur_mes"].between(0, 250).all() and (s["eur_mes"] <= renta).all()


def test_sin_transporte_ni_horas_coinciden_las_alternativas():
    for renta in RENTAS:
        a, h = (
            simulacion.fallos(_fila(renta=float(renta)), c, "ingresos_base", D("0.3"))
            for c in ("alquiler_transporte", "horas_viaje")
        )
        assert bool(a) == bool(h)


def test_simulacion_sobre_la_api_de_ejemplo_cumple_el_contrato():
    api = _api()
    df = simulacion.simulacion(simulacion.tabla_zonas(api))
    contratos.validar(df, "simulacion")
    assert not df.duplicated(["perfil", "municipio_id", "criterio"]).any()
    assert set(df["criterio"]) == set(simulacion.CRITERIOS) and df["estimado"].all()
    assert set(df["perfil"]) <= {v[0] for v in simulacion.variantes()}
    c = simulacion.cambios(simulacion.tabla_zonas(api))
    assert set(c["criterio"]) == set(simulacion.CRITERIOS)
    assert len(simulacion.IDS) == len(titulares.PERFILES)
    assert re.fullmatch(r"[a-z_0-9]+", "".join(simulacion.IDS))


@pytest.mark.parametrize(
    ("ingresos", "renta", "maximo", "falla"),
    [(D("25200.01"), D(0), D(600), "4.1.d"), (D(0), D("600.01"), D(600), "art. 5")]
    + [(D(0), D("450.01"), tope("28079", "habitacion"), "art. 5")]
    + [(D(0), D("300.01"), tope("28001", "habitacion"), "art. 5")],
)
def test_un_centimo_por_encima_falla(ingresos, renta, maximo, falla):
    (f,) = requisitos(30, ingresos, renta, maximo)
    assert falla in f


def test_edad_minima_y_moraleja():
    assert requisitos(18, D(0), D(0), None) == []
    assert tope("28089", "vivienda") == 900  # Anexo II; la ficha de la sede la omite


def test_base_de_la_pareja_y_la_madre():
    # cotización del 6,5 %; rnt > 19.747,50, así que el art. 20 es 0
    assert simulacion.base_imponible(titulares.EAES) == D("24215.30")
    assert simulacion.base_imponible(titulares.OFICINA) == D("24427.16")


def test_mediana_de_zonas_por_municipio():
    medidas = ("alquiler", "alquiler_p75", "transporte", "horas")
    z = pd.DataFrame(
        {"perfil": "p", "municipio_id": "m", "zona_id": ["a", "b", "c"], "neto": 1.0}
        | {c: [1.0, 2.0, 10.0] for c in medidas}
    )
    m = simulacion._municipios(z)
    assert len(m) == 1 and m.loc[0, "alquiler"] == 2.0 and m.loc[0, "horas"] == 2.0


def test_cuantia_de_la_pareja_cuenta_dos_personas():
    f = _fila(renta=400.0, beneficiarios=2) | {"perfil": "p"}
    s = simulacion._evaluar(pd.DataFrame([f]), alquiler="renta")
    assert s.set_index("criterio").loc["bono_vigente", "eur_mes"] == 400.0


def test_cambios_cuenta_a_mano_y_aplica_el_escenario():
    z = simulacion.tabla_zonas(_api())
    ok = simulacion.simulacion(z).pivot(
        index=["perfil", "municipio_id"], columns="criterio", values="elegible"
    )
    c = simulacion.cambios(z).set_index(["perfil", "criterio"])
    for (perfil, crit), r in c.iterrows():
        g = ok.loc[perfil]
        assert r["entran"] == (~g["bono_vigente"] & g[crit]).sum()
        assert r["salen"] == (g["bono_vigente"] & ~g[crit]).sum()
    # la suma del hogar de la pareja (48.430 €) pasa de 3 × IPREM: fuera de todo
    h = simulacion.cambios(z, ingresos="hogar").set_index(["perfil", "criterio"])
    assert (h.loc["pareja_mediana", "elegibles"] == 0).all()
    assert (c.loc["pareja_mediana", "elegibles"] > 0).any()


def test_por_transporte_cuenta_solo_lo_que_cruza_al_sumar_el_transporte():
    z = simulacion.tabla_zonas(_api())
    c = simulacion.cambios(z).set_index(["perfil", "criterio"])
    sin = simulacion.cambios(z.assign(transporte=0.0)).set_index(["perfil", "criterio"])
    assert (sin["por_transporte"] == 0).all()
    assert (c["por_transporte"] <= c["elegibles"]).all()
