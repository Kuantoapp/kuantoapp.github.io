"""Tests de `simulacion` (#101, #301): umbrales, topes, base imponible a mano, pesos, H, imputación y contrato."""

import copy
import json
import re
import unicodedata
from decimal import Decimal as D
from itertools import product

import pandas as pd
import pytest

from mesobra import (
    bono,
    calculo,
    contratos,
    matriz_trabajo,
    neto,
    simulacion,
    titulares,
)
from mesobra import transporte as tr
from mesobra.simulacion import Escenario, requisitos, tope


def _api() -> dict:
    """API de ejemplo sin los orígenes B2 y C2, que no tienen tarifa en su `tarifas.json` (solo A y B1)."""
    api = calculo.leer_api(calculo.API_EJEMPLO)
    t = api["tiempos"]
    return {**api, "tiempos": {**t, "origenes": t["origenes"][:3], "tp": t["tp"][:3]}}


def test_pares_no_usan_la_brecha_de_contrato_nuevo():
    api = _api2()
    doble = copy.deepcopy(api)
    for z in doble["alquiler"]["zonas"].values():
        z["factor_brecha"] = 2.0
    pares = []
    for a in (api, doble):
        imp, imputados = simulacion.imputar_tiempos(a, W)
        pares.append(simulacion.tabla_pares(imp, W, imputados))
    pd.testing.assert_frame_equal(pares[0], pares[1])


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


def _fila(renta=500.0, transporte=0.0, horas_extra=0.0, **kw) -> dict:
    return {
        "municipio_id": "28079", "tipo": "vivienda", "edad": 30, "ingresos_base": 10000.0,
        "ingresos_bruto": 12000.0, "renta": renta, "transporte": transporte, "horas_extra": horas_extra,
        "horas": 0.0, "minutos": 10, "neto": 1000.0, "horas_trab": 151.3, "n_sueldos": 1,
        "beneficiarios": 1, **kw,
    }  # fmt: skip


def _fallos(f: dict, criterio: str, corte: float = 0.3, vtt: float = 10.0) -> list[str]:
    return simulacion.fallos(f, criterio, "ingresos_base", vtt, corte)


def test_subir_renta_nunca_hace_entrar_por_tope():
    for tipo, ing in product(("vivienda", "habitacion"), INGRESOS):
        ok = [
            not requisitos(30, D(ing), D(str(r)), tope("28079", tipo)) for r in RENTAS
        ]
        assert ok == sorted(ok, reverse=True)


def test_subir_ingresos_nunca_hace_entrar():
    for c in (*simulacion.CRITERIOS, "lgss_2015"):
        ok = [
            not _fallos(_fila(ingresos_base=float(i), minutos=90, renta=900.0), c)
            for i in INGRESOS
        ]
        assert ok == sorted(ok, reverse=True)


def test_horas_viaje_incluye_alquiler_transporte_y_el_vtt_a_mano():
    for renta, transp, h in product(RENTAS, (0.0, 80.0, 300.0), (0.0, 20.0, 100.0)):
        f = _fila(renta=float(renta), transporte=transp, horas_extra=h)
        assert bool(_fallos(f, "alquiler_transporte")) or not _fallos(f, "horas_viaje")
    # (400 + 50 + 10 € × 5 h) ÷ 1.000 € = 0,50: entra con corte 0,45 y no con 0,55; sin horas, 0,45
    f = _fila(renta=400.0, transporte=50.0, horas_extra=5.0)
    assert _fallos(f, "horas_viaje", 0.45) == []
    assert _fallos(f, "horas_viaje", 0.55) and _fallos(f, "alquiler_transporte", 0.46)


def test_lgss_ida_y_vuelta_o_coste():
    # bruto de 24.000 (por encima del SMI tras el coste). 120 min de ida y vuelta = 25 % de 8 h: no pasa; 61 de ida,
    # sí. Coste: 20 % de 24.000 ÷ 12 = 400 €
    assert _fallos(_fila(minutos=60, ingresos_bruto=24000.0), "lgss_2015")
    assert _fallos(_fila(minutos=61, ingresos_bruto=24000.0), "lgss_2015") == []
    assert _fallos(_fila(transporte=400.0, ingresos_bruto=24000.0), "lgss_2015")
    assert _fallos(_fila(transporte=400.01, ingresos_bruto=24000.0), "lgss_2015") == []
    # dos sueldos: el coste es el de cada trabajador
    assert _fallos(
        _fila(transporte=600.0, n_sueldos=2, ingresos_bruto=24000.0), "lgss_2015"
    )


@pytest.mark.parametrize("criterio", ["lgss_2015", "lgss_2015_14"])
def test_lgss_salario_menos_coste_bajo_el_smi(criterio):
    # bruto = SMI anual: sin coste es adecuada; con 0,01 € de coste el salario queda por debajo del SMI
    smi = float(simulacion.parametros_2026.SMI_ANUAL)
    assert _fallos(_fila(ingresos_bruto=smi), criterio)
    assert _fallos(_fila(ingresos_bruto=smi, transporte=0.01), criterio) == []


def test_lgss_solo_el_smi_sin_pasar_el_20_por_ciento():
    # 18.000 ÷ 12 = 1.500; SMI ÷ 12 = 1.424,50: con 76 € queda en 1.424 (< SMI) y 76 < 300 (20 %); con 75,50, no
    assert _fallos(_fila(ingresos_bruto=18000.0, transporte=76.0), "lgss_2015") == []
    assert _fallos(_fila(ingresos_bruto=18000.0, transporte=75.5), "lgss_2015")


def test_sin_transporte_ni_horas_coinciden_las_alternativas():
    for renta in RENTAS:
        a, h = (
            _fallos(_fila(renta=float(renta)), c)
            for c in ("alquiler_transporte", "horas_viaje")
        )
        assert bool(a) == bool(h)


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


def test_vtt_es_la_proporcion_del_coste_laboral_de_madrid():
    assert round(simulacion.VTT, 2) == 9.76
    assert [round(v, 2) for v in simulacion.BANDA_VTT] == [7.50, 12.01]
    assert round(simulacion.VTT_NACIONAL, 2) == 8.39


def test_mediana_de_zonas_por_municipio():
    medidas = ("alquiler", "alquiler_p75", "transporte", "horas")
    z = pd.DataFrame(
        {"perfil": "p", "municipio_id": "m", "zona_id": ["a", "b", "c"], "neto": 1.0}
        | {c: [1.0, 2.0, 10.0] for c in medidas}
    )
    m = simulacion._municipios(z, medidas)
    assert len(m) == 1 and m.loc[0, "alquiler"] == 2.0 and m.loc[0, "horas"] == 2.0


def test_cuantia_de_la_pareja_cuenta_dos_personas_y_no_pasa_de_la_renta():
    mun = pd.DataFrame(
        [{"perfil": "p", "municipio_id": "m", "beneficiarios": 2, "alquiler": 400.0}]
    )
    (f,) = simulacion._filas(mun, "bono_vigente", [100.0], Escenario())
    assert f[4] == 400.0
    mun["alquiler"] = 900.0
    assert simulacion._filas(mun, "bono_vigente", [49.9], Escenario())[0][3:5] == (
        False,
        0.0,
    )
    assert simulacion._filas(mun, "bono_vigente", [50.0], Escenario())[0][3:5] == (
        True,
        500.0,
    )


def _pares_a_mano() -> pd.DataFrame:
    """Un municipio, tres zonas y dos destinos con pesos 0,7 y 0,3; neto de 1.000 € y corte de 0,30."""
    base = {
        "perfil": "p",
        "municipio_id": "m",
        "tipo": "vivienda",
        "edad": 30,
        "ingresos_base": 1.0,
        "neto": 1000.0,
    }
    filas = []
    for zona, destino, w, alquiler, transporte, h in [
        ("a", "d1", 0.7, 300.0, 50.0, 0.0),  # 0,35: elegible
        ("a", "d2", 0.3, 250.0, 0.0, 10.0),  # 0,25 sin horas, 0,35 con 10 h × 10 €/h
        ("b", "d1", 0.7, 100.0, 0.0, 0.0),  # 0,10: nunca
        ("b", "d2", 0.3, 100.0, 0.0, 0.0),
        ("c", "d1", 0.7, 400.0, 0.0, 0.0),  # 0,40: siempre
        ("c", "d2", 0.3, 400.0, 0.0, 0.0),
    ]:  # fmt: skip
        filas.append(base | {"zona_id": zona, "destino": destino, "w": w, "alquiler": alquiler,
                             "transporte": transporte, "horas_extra": h})  # fmt: skip
    return pd.DataFrame(filas)


def test_pct_a_mano_con_tres_zonas_y_mediana_distinta_de_la_media():
    pares = _pares_a_mano()
    mun = pd.DataFrame([{"perfil": "p", "municipio_id": "m"}])
    e = Escenario(corte=0.3, vtt=10.0)
    # alquiler_transporte: zonas a = 70 %, b = 0, c = 100: mediana 70 (la media sería 56,7)
    assert simulacion._pct_municipios(
        pares, mun, "alquiler_transporte", e
    ) == pytest.approx([70.0])
    # horas_viaje: el viaje de más hace entrar a la zona a en d2: 100, 0 y 100: mediana 100 (media 66,7)
    assert simulacion._pct_municipios(pares, mun, "horas_viaje", e) == pytest.approx(
        [100.0]
    )
    # VTT = 0: horas_viaje = alquiler_transporte
    assert simulacion._pct_municipios(
        pares, mun, "horas_viaje", e._replace(vtt=0.0)
    ) == pytest.approx([70.0])


def _api2() -> dict:
    """API de ejemplo con dos destinos de zona y tres orígenes; Getafe sin tiempo ni a Centro ni a Vallecas."""
    api = _api()
    t = api["tiempos"]
    destinos = [{**t["destinos"][1], "tipo": "zona", "destino_id": "2807913"}]
    tp = [list(f) for f in t["tp"]]
    tp[2] = [None, None]
    return {
        **api,
        "tiempos": {**t, "destinos": [t["destinos"][0], *destinos], "tp": tp},
    }


W = pd.DataFrame(
    {
        "origen": ["28079", "28079", "28065"],
        "destino": ["2807901", "2807913", "2807913"],
        "w": [0.6, 0.4, 1.0],
    }
)


def _pares() -> pd.DataFrame:
    imp, imputados = simulacion.imputar_tiempos(_api2(), W)
    return simulacion.tabla_pares(imp, W, imputados)


def test_imputa_a_120_solo_con_peso_y_sin_tiempo():
    api = _api2()
    imp, pares = simulacion.imputar_tiempos(api, W)
    # Getafe → Centro tiene tp nulo pero w = 0: sigue nulo; Getafe → Vallecas, con w = 1: 120
    assert imp["tiempos"]["tp"][2] == [None, simulacion.TP_IMPUTADO]
    assert pares == {("28065", "2807913")}
    assert api["tiempos"]["tp"][2] == [None, None]  # la API original no cambia
    assert imp["tiempos"]["tp"][:2] == api["tiempos"]["tp"][:2]


def test_imputar_falla_con_un_destino_desconocido_o_que_no_es_zona():
    with pytest.raises(ValueError, match="destinos con peso"):
        simulacion.imputar_tiempos(_api2(), W.assign(destino="28999"))
    api = _api2()
    t = api["tiempos"]
    no_zona = {
        **api,
        "tiempos": {
            **t,
            "destinos": [{**t["destinos"][0], "tipo": "polo"}, t["destinos"][1]],
        },
    }
    with pytest.raises(ValueError, match="como zona"):
        simulacion.imputar_tiempos(no_zona, W)


def test_la_referencia_no_sale_de_un_par_imputado():
    # Getafe → Vallecas imputado a 1 min sería el mínimo; la referencia sigue siendo Centro (observado): H = 0
    imp, imputados = simulacion.imputar_tiempos(_api2(), W, 1)
    pares = simulacion.tabla_pares(imp, W, imputados)
    assert (pares.loc[pares["zona_id"] == "2807901", "horas_extra"] == 0).all()


def test_h_es_cero_en_la_zona_de_referencia_y_nunca_negativa():
    pares = _pares()
    assert (pares["horas_extra"].dropna() >= 0).all()
    # Centro es la referencia hacia los dos destinos (9 y 38 min): H = 0
    assert (pares.loc[pares["zona_id"] == "2807901", "horas_extra"] == 0).all()
    assert (pares.loc[pares["zona_id"] == "2807913", "horas_extra"] > 0).all()
    assert pares.loc[pares["imputado"], "w"].gt(0).all()
    assert set(pares.loc[pares["imputado"], "zona_id"]) == {"28065"}


def test_con_vtt_cero_horas_viaje_es_alquiler_transporte_y_el_pct_esta_en_rango():
    pares = _pares()
    s = simulacion.simulacion(pares, vtt=0.0)
    a, h = (
        s[s["criterio"] == c].drop(columns="criterio").reset_index(drop=True)
        for c in simulacion.CRITERIOS[1:]
    )
    pd.testing.assert_frame_equal(a, h)
    base = simulacion.simulacion(pares)
    assert base["pct_ocupados_elegibles"].between(0, 100).all()
    assert not base.duplicated(["perfil", "municipio_id", "criterio"]).any()
    assert base["estimado"].all() and set(base["criterio"]) == set(simulacion.CRITERIOS)
    assert {v[0] for v in simulacion.variantes()} >= set(simulacion.IDS)


def test_sensibilidades_sobre_la_api_de_ejemplo():
    pares = _pares()
    lgss = simulacion.simulacion(pares, ("bono_vigente", "lgss_2015"))
    assert set(lgss["criterio"]) == {"bono_vigente", "lgss_2015"}
    s296 = simulacion.simulacion_296(simulacion.tabla_zonas(pares))
    assert set(s296["criterio"]) == {"bono_vigente", *simulacion.CRITERIOS_296}
    assert set(s296["pct_ocupados_elegibles"]) <= {0.0, 100.0}
    c = simulacion.cambios(simulacion.simulacion(pares)).set_index(
        ["perfil", "criterio"]
    )
    assert (
        (c.xs("bono_vigente", level="criterio")[["entran", "salen"]] == 0).all().all()
    )
    assert set(simulacion.curva(pares).columns) == {0.25, 0.3, 0.35, 0.4, 0.45, 0.5}
    assert len(simulacion.IDS) == len(titulares.PERFILES)
    assert re.fullmatch(r"[a-z_0-9]+", "".join(simulacion.IDS))


def test_el_contrato_exige_pct_ocupados_elegibles():
    df = pd.read_csv(
        calculo.RAIZ / "tests/fixtures/processed/simulacion.csv",
        dtype=contratos.dtypes("simulacion"),
    )
    contratos.validar(df, "simulacion")
    with pytest.raises(ValueError, match="pct_ocupados_elegibles"):
        contratos.validar(df.drop(columns="pct_ocupados_elegibles"), "simulacion")


MATRIZ = pd.DataFrame(
    {
        "origen": ["28001"] * 5 + ["28002"],
        "prov_destino": ["28", "28", "28", "19", None, "28"],
        "destino": ["28079", "28065", None, "19001", None, "28065"],
        "ocupados": [60, 40, 10, 30, 20, 5],
    }
)
CUOTAS = pd.Series({"2807901": 0.25, "2807902": 0.75})


def test_pesos_suman_uno_por_origen_y_declaran_la_masa_excluida():
    w, excluida = matriz_trabajo.pesos(MATRIZ, CUOTAS)
    assert w.groupby("origen")["w"].sum().tolist() == pytest.approx([1.0, 1.0])
    # 28001: con municipio en la Comunidad, 100 de 160 (fuera: 10 sin municipio, 30 de Guadalajara, 20 sin provincia)
    assert excluida["28001"] == pytest.approx(60 / 160) and excluida["28002"] == 0
    assert matriz_trabajo.ocupados_observados(MATRIZ).to_dict() == {
        "28001": 100,
        "28002": 5,
    }
    # un origen sin destinos observados en la Comunidad: 0 observados, no NaN
    fuera = pd.DataFrame(
        {
            "origen": ["28003"],
            "prov_destino": ["19"],
            "destino": ["19001"],
            "ocupados": [7],
        }
    )
    assert matriz_trabajo.ocupados_observados(fuera).to_dict() == {"28003": 0}


def test_el_reparto_de_madrid_conserva_su_peso():
    w, _ = matriz_trabajo.pesos(MATRIZ, CUOTAS)
    o = w[w["origen"] == "28001"].set_index("destino")["w"]
    assert o["2807901"] + o["2807902"] == pytest.approx(0.6)
    assert o["2807902"] == pytest.approx(3 * o["2807901"]) and o[
        "28065"
    ] == pytest.approx(0.4)
    assert "28079" not in o.index


def _csv_distritos(nombres: list[str]) -> str:
    cab = "Año;Concepto;Tipo territorio;Código territorio;Territorio;Estrato Empleo;Medida;Valor;Unidad;Estado dato"
    pre = (
        "Ocupados en unidades productivas en el distrito de {} del municipio de Madrid"
    )
    filas = [
        f"2023;{pre.format(n)};Otros;;;Total;Ocupados;{100 * (i + 1)};Número;"
        for i, n in enumerate(nombres)
    ]
    filas += [
        f"2023;{pre.format('las que no consta distrito')};Otros;;;Total;Ocupados;9999;Número;",
        f"2023;{pre.format(nombres[0])};Otros;;;De 3 a 9 trabajadores;Ocupados;7;Número;",
        f"2015;{pre.format(nombres[0])};Otros;;;Total;Ocupados;7;Número;",
        f"2023;Unidades productivas en el distrito de {nombres[0]} del municipio de Madrid;Otros;;;Total;Unidades productivas;7;Número;",
    ]  # fmt: skip
    return "﻿" + "\r\n".join([cab, *filas]) + "\r\n"


def test_cuotas_de_distritos_con_un_csv_sintetico(tmp_path):
    nombres = [f"Distrito {i}" for i in range(1, 22)]
    nombres[0], nombres[1] = "Fuencarral - El Pardo", "Moncloa - Aravaca"
    geo = ["Fuencarral-El Pardo", "Moncloa-Aravaca", *nombres[2:]]
    zonas = {
        "features": [
            {"properties": {"zona_id": f"28079{i:02d}", "nombre": n, "tipo": "distrito", "municipio_id": "28079"}}
            for i, n in enumerate(geo, 1)
        ]
    }  # fmt: skip
    (tmp_path / "zonas.geojson").write_text(json.dumps(zonas), "utf-8")
    csv = tmp_path / "d.csv"
    csv.write_text(_csv_distritos(nombres), "utf-8", newline="")
    c = matriz_trabajo.leer_cuotas_distritos(csv, tmp_path / "zonas.geojson")
    assert len(c) == 21 and c.sum() == pytest.approx(1.0)
    assert c["2807901"] == pytest.approx(100 / sum(100 * (i + 1) for i in range(21)))
    csv.write_text(
        _csv_distritos(nombres[:20]), "utf-8", newline=""
    )  # falta un distrito
    with pytest.raises(ValueError, match="distritos"):
        matriz_trabajo.leer_cuotas_distritos(csv, tmp_path / "zonas.geojson")


def test_tabla_pares_tiene_una_fila_por_variante_zona_y_destino_y_filas_sin_peso():
    api = _api2()
    pares = _pares()
    zonas = sum(
        api["alquiler"]["zonas"][z]["origen"] != "sin_dato"
        for z in api["tiempos"]["origenes"]
    )
    assert len(pares) == len(simulacion.variantes()) * zonas * 2
    assert (pares["w"] == 0).any() and (pares["w"] > 0).any()


def test_un_par_con_peso_sin_tiempo_falla():
    # sin imputar, Getafe → Vallecas (w = 1) no tiene tiempo: ni transporte ni horas
    with pytest.raises(ValueError, match="sin transporte, horas o neto"):
        simulacion.tabla_pares(_api2(), W, set())


def test_alquiler_transporte_y_horas_viaje_ignoran_el_tope_y_bono_vigente_no():
    f = _fila(renta=1500.0, municipio_id="28001", horas_extra=1.0)
    assert any("tope" in x for x in _fallos(f, "bono_vigente"))
    assert _fallos(f, "alquiler_transporte") == [] == _fallos(f, "horas_viaje")


def test_exactamente_el_corte_sigue_siendo_asequible():
    f = _fila(renta=400.0, transporte=50.0)  # 450 ÷ 1.000 = 0,45
    for c in ("alquiler_transporte", "horas_viaje", "horas_viaje_296"):
        assert _fallos(f, c, 0.45) and _fallos(f | {"renta": 400.01}, c, 0.45) == []
    assert simulacion.TP_IMPUTADO == 120 and simulacion.CORTE == 0.45


def test_criterio_desconocido_falla():
    with pytest.raises(ValueError, match="criterio desconocido"):
        _fallos(_fila(), "horas_viajes")


def test_bono_vigente_es_todo_o_nada():
    s = simulacion.simulacion(_pares())
    b = s[s["criterio"] == "bono_vigente"]
    assert b["pct_ocupados_elegibles"].isin([0.0, 100.0]).all()
    assert ((b["pct_ocupados_elegibles"] == 100.0) == b["elegible"]).all()


def test_pareja_tiene_dos_beneficiarios_y_los_demas_uno():
    por = _pares().groupby("perfil")["beneficiarios"].first()
    assert por["pareja_mediana"] == 2 and por.drop("pareja_mediana").eq(1).all()


def test_horas_viaje_296_suma_horas_entre_horas_trabajadas():
    f = _fila(renta=400.0, transporte=50.0, horas=15.13, horas_trab=151.3)
    assert simulacion._carga(f, "horas_viaje_296", 0.0) == pytest.approx(0.55)
    assert simulacion._carga(f, "alquiler_transporte_296", 0.0) == pytest.approx(0.45)


def test_tabla_zonas_excluye_los_pares_imputados():
    z = simulacion.tabla_zonas(_pares())
    assert "28065" not in set(z["zona_id"]) and "2807901" in set(z["zona_id"])


def test_sensibilidades_de_ingresos_y_de_alquiler_cambian_lo_que_deben():
    f = _fila(renta=500.0, municipio_id="28001", ingresos_base=10000.0)
    f |= {
        "alquiler": 500.0,
        "ingresos_bruto": 30000.0,
        "ingresos_hogar": 40000.0,
        "alquiler_p75": 700.0,
    }
    t = pd.DataFrame([f])
    for ing, ok in [("base", True), ("bruto", False), ("hogar", False)]:
        assert simulacion._ok(t, "bono_vigente", Escenario(ingresos=ing)) == [ok]
    # el tope de vivienda del 28001 es 600: con el P75 (700) falla
    assert simulacion._ok(t, "bono_vigente", Escenario(alquiler="alquiler_p75")) == [
        False
    ]


def test_lgss_con_14_pagas_baja_el_umbral_de_coste():
    # 20 % de 24.000 ÷ 12 = 400 €; ÷ 14 = 342,86 €: con 380 € solo pasa con 14 pagas
    f = _fila(transporte=380.0, ingresos_bruto=24000.0)
    assert _fallos(f, "lgss_2015") and _fallos(f, "lgss_2015_14") == []


def test_calidad_por_municipio_con_sus_marcas():
    excluida = pd.Series({"28079": 0.30, "28065": 0.0})
    observados = pd.Series({"28079": 50, "28065": 500})
    c = simulacion.calidad(_pares(), excluida, observados).set_index("municipio_id")
    marcas = ["marca_imputada", "marca_excluida", "marca_pocos"]
    assert (
        c.loc["28065", "masa_imputada"] == 1.0
        and c.loc["28079", "masa_imputada"] == 0.0
    )
    assert c.loc["28065", marcas].tolist() == [True, False, False]
    assert c.loc["28079", marcas].tolist() == [False, True, True]


def test_imputar_con_otros_minutos():
    imp, _ = simulacion.imputar_tiempos(_api2(), W, 60)
    assert imp["tiempos"]["tp"][2] == [None, 60]


def _api_fin(coronas: dict[str, str]) -> dict:
    """`tarifas.json` publicada (al día con `transporte`, lo comprueba test_pipeline_euros) y una zona por municipio."""
    tarifas = calculo.leer_api(calculo.RAIZ / "app/datos")["tarifas"]
    zonas = [
        {"properties": {"municipio_id": m, "corona": c}} for m, c in coronas.items()
    ]
    return {"tarifas": tarifas, "zonas": {"features": zonas}}


CORONAS_FIN = {"28079": "A", "28005": "B1", "28006": "B2", "28007": "B3"}
CORONAS_FIN |= {"28008": "C1", "28009": "C2"}


def test_fin_descuento_control_de_la_issue():
    # control (#102, referencia §1.2): por abono, 84,40 − 49,20 = 35,20 € y joven 20,00 − 10,00 = 10,00 €
    for precios, control in [
        (tr.ABONO_30["C2"], D("35.20")),
        (tr.ABONO_JOVEN, D("10.00")),
    ]:
        sin, con = (precios[e, "ordinario"] for e in tr.ESCENARIOS[::-1])
        assert sin - con == control
    # media del año: × 335/360 (decisión 30); el joven redondea cada escenario (18,61 − 9,31)
    df = simulacion.fin_descuento(_api_fin(CORONAS_FIN))
    df = df[df["criterio"] == "fin_descuento"]
    df = df.set_index(["perfil", "municipio_id"])["eur_mes"]
    assert float(D("35.20") * tr.ABONOS_ANIO / 12) == pytest.approx(32.76, abs=0.005)
    for m in ("28007", "28008", "28009"):  # B3, C1 y C2: el mismo abono
        assert df["adulto", m] == pytest.approx(32.76, abs=0.005)
    assert df["joven", "28009"] == pytest.approx(9.30, abs=0.005)
    # A y B1: 10 viajes en los dos escenarios, 227 × 2 ÷ 12 × (12,50 − 7,30) ÷ 10 (BOCM -3 pág. 72, -2 pág. 67)
    for m in ("28079", "28005"):
        assert df["adulto", m] == pytest.approx(19.67, abs=0.005)


def test_fin_descuento_propiedades_y_contrato():
    todo = simulacion.fin_descuento(_api_fin(CORONAS_FIN))
    contratos.validar(todo, "simulacion")
    assert set(todo["criterio"]) == {"fin_descuento", "fin_descuento_rdl"}
    assert todo["estimado"].all() and todo["pct_ocupados_elegibles"].isna().all()
    assert (todo["eur_mes"] > 0).all() and todo["elegible"].all()
    for _, df in todo.groupby("criterio"):
        # Abono Joven: tarifa plana en todas las coronas
        assert df[df["perfil"] == "joven"]["eur_mes"].nunique() == 1
        adulto = df[df["perfil"] == "adulto"].set_index("municipio_id")["eur_mes"]
        assert adulto[list(CORONAS_FIN)].is_monotonic_increasing  # de A a C2


def test_tarifa_2025_por_1_03_da_la_oficial_de_2026():
    # BOCM-20251231-3 pág. 69: +3 % sobre la vigente; el BOCM redondea a 0,10 a la baja (contraste de la decisión 32)
    def sube(p):
        return (p * D("1.03")).quantize(D("0.1"), rounding="ROUND_FLOOR")

    ofi = ("sin_descuento", "ordinario")
    for c, p in simulacion.ABONO_2025.items():
        assert sube(p) == tr.ABONO_30[c][ofi], c
    assert (
        sube(simulacion.DIEZ_VIAJES_2025["metro_a"]) == tr.DIEZ_VIAJES["metro_a"][ofi]
    )
    for p, hoy in zip(
        simulacion.DIEZ_VIAJES_INTERURBANO_2025, tr.DIEZ_VIAJES_INTERURBANO, strict=True
    ):
        assert sube(p) == hoy[ofi]


def test_fin_descuento_rdl_control_y_cota_inferior():
    df = simulacion.fin_descuento(_api_fin(CORONAS_FIN))
    eur = df.set_index(["criterio", "perfil", "municipio_id"])["eur_mes"]
    # A y B1: 10 viajes (7,30 + 0,20 × 12,20) × 227 × 2 ÷ 120 = 36,85 − 27,62; B2: (9,60 + 0,20 × 16,10) → 48,50 − 36,32
    # B3-C2: abono (49,20 + 0,20 × 82,00) × 335/360 = 61,04 − 45,78; joven: (10 + 0,50 × 20) → 18,61 − 9,31
    esperado = {"28079": 9.23, "28005": 9.23, "28006": 12.18}
    esperado |= dict.fromkeys(("28007", "28008", "28009"), 15.26)
    for m, x in esperado.items():
        assert eur["fin_descuento_rdl", "adulto", m] == pytest.approx(x, abs=0.005)
        assert eur["fin_descuento_rdl", "adulto", m] < eur["fin_descuento", "adulto", m]
        assert eur["fin_descuento_rdl", "joven", m] == eur["fin_descuento", "joven", m]


def test_fin_descuento_rdl_mantiene_el_titulo_mas_barato():
    # con los precios del escenario RDL, el título de vigente_2026 sigue siendo el más barato
    vig = ("vigente_2026", "ordinario")
    abono, diez = tr.ABONOS_ANIO / 12, 2 * simulacion.DIAS_FIN * tr.SEMANAS_MES / 10
    for i, c in enumerate(tr.ORDEN_CORONAS):
        p_abono = tr.ABONO_30[c][vig] + simulacion.PCT_RDL * simulacion.ABONO_2025[c]
        hoy = (
            tr.DIEZ_VIAJES["metro_a"] if c == "A" else tr.DIEZ_VIAJES_INTERURBANO[i]
        )[vig]
        ref = (
            simulacion.DIEZ_VIAJES_2025["metro_a"]
            if c == "A"
            else simulacion.DIEZ_VIAJES_INTERURBANO_2025[i]
        )
        gana_abono = p_abono * abono < (hoy + simulacion.PCT_RDL * ref) * diez
        titulo = tr.coste_mes(
            vig,
            "general",
            tr.clave_v1(c, simulacion.VIAJES_FIN),
            simulacion.DIAS_FIN,
            0,
        )[0]
        assert gana_abono == (titulo == "Abono 30 días"), c


def test_fin_descuento_falla_si_un_municipio_cae_en_dos_coronas():
    api = _api_fin({"28079": "A"})
    api["zonas"]["features"].append(
        {"properties": {"municipio_id": "28079", "corona": "B1"}}
    )
    with pytest.raises(ValueError, match="dos coronas"):
        simulacion.fin_descuento(api)


def test_fin_descuento_con_los_datos_publicados():
    api = calculo.leer_api(calculo.RAIZ / "app/datos")
    df = simulacion.fin_descuento(api)
    municipios = {f["properties"]["municipio_id"] for f in api["zonas"]["features"]}
    assert set(df["municipio_id"]) == municipios and (df["eur_mes"] > 0).all()


def test_fin_coronas_no_es_monotona_con_3_dias():
    s = simulacion.fin_coronas(_api_fin({}))
    s = s.set_index(["corona", "perfil", "dias", "viajes_dia"])["eur_mes"]
    assert len(s) == 6 * 2 * 2 * 2 and (s > 0).all()
    # caso base (5 días, 2 viajes): lo mismo que `fin_descuento` en todas las coronas y perfiles
    fin = simulacion.fin_descuento(_api_fin(CORONAS_FIN))
    fin = fin[fin["criterio"] == simulacion.CRITERIO_FIN]
    for perfil, m, eur in fin[["perfil", "municipio_id", "eur_mes"]].itertuples(
        index=False
    ):
        assert s[CORONAS_FIN[m], perfil, 5, 2] == pytest.approx(eur, abs=0.005)
    # con 3 días C1 pierde más que C2: con descuento C1 usa el 10 viajes (40,41) y C2 el abono (45,78); sin él,
    # los dos pasan al sencillo (68,10)
    assert s["C1", "adulto", 3, 2] == pytest.approx(68.10 - 40.41, abs=0.005)
    assert s["C2", "adulto", 3, 2] == pytest.approx(68.10 - 45.78, abs=0.005)
