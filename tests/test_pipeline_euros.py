"""`pipeline_euros`: cada JSON cumple el contrato y las reglas de elección de datos."""

import json
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely import Point

from mesobra import alquiler, imputacion, neto, pipeline_euros, transporte
from mesobra.api_estatica import COLECTIVOS, validar
from mesobra.pipeline_euros import (
    alquiler_json,
    hogares_json,
    m2_por_defecto,
    netos_json,
    tarifas_json,
)

PROCESSED = Path(__file__).parent / "fixtures" / "processed"


def _zona(filas):
    columnas = ["zona_id", "anio", "eur_m2_p50", "m2_p50", "testigos"]
    df = pd.DataFrame(filas, columns=columnas)
    df["eur_m2_p25"], df["eur_m2_p75"] = df["eur_m2_p50"] - 1, df["eur_m2_p50"] + 1
    df["origen"] = df["eur_m2_p50"].notna().map({True: "observado", False: "sin_dato"})
    df["ic_inf"] = df["ic_sup"] = float("nan")
    df["factor_ipc"] = 1.0
    df["factor_brecha"], df["brecha_ambito"], df["brecha_pureza"] = 1.1, "tramo", None
    df.attrs["ipc_hasta"] = "2026-10"
    return df


def test_alquiler_ultimo_anio_sin_madrid_y_sin_dato():
    zona = _zona(
        [
            ("28079", 2024, 15.0, 70.0, 99),
            ("28001", 2023, 10.0, 60.0, 20),
            ("28001", 2024, None, None, 5),
            ("28002", 2023, 8.0, 50.0, 20),
            ("28002", 2024, 9.0, 55.0, 20),
            ("28003", 2024, None, None, 5),
        ]
    )
    obj = alquiler_json(zona)
    validar("alquiler.json", obj)
    z = obj["zonas"]
    assert list(z) == ["28001", "28002", "28003"]
    assert (z["28001"]["anio"], z["28001"]["p50"]) == (2023, 10.0)
    assert (z["28002"]["anio"], z["28002"]["p50"]) == (2024, 9.0)
    assert z["28003"]["origen"] == "sin_dato"
    assert z["28003"]["anio"] is None
    assert (z["28001"]["testigos"], z["28002"]["testigos"], z["28003"]["testigos"]) == (
        20,
        20,
        None,
    )
    assert obj["meta"]["min_testigos"] == alquiler.MIN_TESTIGOS
    assert obj["meta"]["anio_dato"] == 2024


def test_m2_por_defecto_es_la_mediana_ponderada():
    zona = _zona(
        [
            ("28001", 2024, 10.0, 40.0, 1),
            ("28002", 2024, 10.0, 60.0, 1),
            ("28003", 2024, 10.0, 80.0, 10),
            ("28001", 2023, 10.0, 300.0, 50),  # año anterior de 28001: no cuenta
            ("28079", 2024, 10.0, 10.0, 999),
        ]
    )
    assert m2_por_defecto(zona) == 80


def test_alquiler_del_fixture_cumple_el_contrato():
    zona = pd.read_csv(PROCESSED / "alquiler_zona.csv", dtype={"zona_id": str})
    zona["factor_brecha"], zona["brecha_ambito"], zona["brecha_pureza"] = (
        1.2,
        "municipio",
        None,
    )
    zona.attrs["ipc_hasta"] = "2026-10"  # el fixture trae un factor_ipc de 1,035
    obj = alquiler_json(zona)
    validar("alquiler.json", obj)
    assert obj["zonas"]["28092"]["ic"] == [10.3, 13.4]
    assert imputacion.FUENTE_ADRH in obj["meta"]["fuentes"]
    assert "origen estimado" in obj["meta"]["nota"]


def test_estimado_sin_m2_y_fuera_del_m2_por_defecto():
    zona = _zona([("28001", 2024, 10.0, 40.0, 1), ("28002", 2024, 12.0, None, 0)])
    zona.loc[1, ["origen", "ic_inf", "ic_sup"]] = ["estimado", 10.0, 14.0]
    obj = alquiler_json(zona)
    validar("alquiler.json", obj)
    assert obj["zonas"]["28002"]["m2"] is None
    assert obj["zonas"]["28002"]["testigos"] is None
    assert m2_por_defecto(zona) == 40


def test_netos_tarifas_y_hogares_cumplen_el_contrato():
    netos = pd.read_csv(PROCESSED / "netos.csv").query("bruto_anual <= 30000")
    validar("netos.json", netos_json(netos))
    validar("netos.json", netos_json(neto.rejilla()))
    validar("tarifas.json", _tarifas())
    tabla = pd.read_csv(PROCESSED / "hogares.csv")
    tabla.attrs["ipc_hasta"] = "2026-10"
    tabla.attrs["nota"] = "Estimado"
    cesta = pd.Series(
        {"alimentacion": 275.0, "suministros": 81.0, "comunicaciones": 43.7}
    )
    tramos = pd.Series([0.73, 1.14], index=pd.Index([0, 5000], name="desde"))
    obj = hogares_json(tabla, cesta, tramos, 69)
    validar("hogares.json", obj)
    assert {p["m2"] for p in obj["perfiles"].values()} == {69}
    assert obj["cesta_tramos"] == [
        {"desde": 0, "factor": 0.73},
        {"desde": 5000, "factor": 1.14},
    ]
    assert type(obj["cesta_tramos"][1]["desde"]) is int


def _tarifas():
    claves = pd.DataFrame(
        {
            "zona_id": ["28065", "28065", "28092", "28092"],
            "destino_id": ["28065", "28092", "28065", "28092"],
            "clave_tarifa": [
                "B1-B1|interurbano",
                "B1-B2|interurbano",
                "B1-B2|interurbano",
                None,
            ],
            "clave_estimada": True,
        }
    )
    lista = ["B1-B1|interurbano", "B1-B2|interurbano"]
    return tarifas_json(
        transporte.tabla_v1(),
        transporte.tabla(pipeline_euros._con_transbordo(lista)),
        claves,
        ["28065", "28092"],
    )


def test_tarifas_trae_los_dos_viajes_al_dia():
    # 10 viajes prorrateado (#162): 3 días = 22,7 viajes × 0,73; con 4 viajes al día, 45,4 × 0,73 = 33,14
    a = _tarifas()["escenarios"]["vigente_2026"]["general"]
    assert a["2"]["A"][2] == {"titulo": "10 viajes", "coste_mes": 16.57}
    assert a["4"]["A"][2] == {"titulo": "Abono 30 días", "coste_mes": 30.43}


def test_rutas_usa_la_ruta_de_161_sin_marcarla_estimada(tmp_path, monkeypatch):
    ids = ["28065", "28092"]
    zonas = gpd.GeoDataFrame({"zona_id": ids}, geometry=[Point(0, 0)] * 2, crs=25830)
    zonas.to_parquet(tmp_path / "zonas.parquet")
    pd.DataFrame(
        {
            "zona_id": ["28065", "28065", "28092", "28092"],
            "destino_id": ids * 2,
            "modo": "tp",
            "corona_min": ["B1", "A", "A", "B2"],
            "corona_max": ["B1", "B2", "B2", "B2"],
            "sistemas": ["urbano", "interurbano+metro", "interurbano+metro", None],
            "validaciones": [1, 2, 2, 1],
            "estimado": True,  # de los tiempos (#173): no dice nada de la clave
        }
    ).to_parquet(tmp_path / "tiempos.parquet")
    monkeypatch.setattr(pipeline_euros, "PROCESSED", tmp_path)
    claves, orden = pipeline_euros.rutas()
    assert orden == ids
    assert not claves["clave_estimada"].any()
    assert claves["clave_tarifa"].tolist() == [
        "B1-B1|urbano",
        "A-B2|interurbano+metro_a",
        "A-B2|interurbano+metro_a",
        "B2-B2|interurbano",
    ]


def test_tarifas_matriz_de_claves():
    o = _tarifas()
    # cada clave de ruta lleva al lado su gemela con cambio de operador (4 viajes al día, #164)
    assert o["claves"] == [
        "B1-B1|interurbano",
        "B1-B1|interurbano+metro_a",
        "B1-B2|interurbano",
        "B1-B2|interurbano+metro_a",
    ]
    assert o["clave_tarifa"] == [[0, 2], [2, None]]
    assert o["clave_estimada"]
    assert o["colectivos"] == COLECTIVOS
    por_colectivo = o["tarifas_ruta"]["vigente_2026"]
    assert sorted(por_colectivo) == sorted(COLECTIVOS)
    cinco = por_colectivo["ordinario"]["general"]["B1-B2|interurbano"]["0"][4]
    assert cinco == {"titulo": "Abono 30 días B1-B2", "coste_mes": 26.71}
    # 14,30 € del interzonal para FN especial (BOCM-20251231-2 pág. 66) × 335/30 / 12
    cinco = por_colectivo["fn_especial"]["general"]["B1-B2|interurbano"]["0"][4]
    assert cinco == {"titulo": "Abono 30 días B1-B2", "coste_mes": 13.31}


def test_tarifas_transbordo_apunta_a_la_clave_con_cambio_de_operador():
    claves = ["B1-B1|interurbano", "B1-B2|interurbano"]
    gemelas = [transporte.clave_transbordo(c) for c in claves]
    assert gemelas == ["B1-B1|interurbano+metro_a", "B1-B2|interurbano+metro_a"]
    o = _tarifas()
    assert o["claves"] == sorted(claves + gemelas)
    posicion = {c: i for i, c in enumerate(o["claves"])}
    assert [o["transbordo"][posicion[c]] for c in claves] == [
        posicion[g] for g in gemelas
    ]
    assert [o["transbordo"][posicion[g]] for g in gemelas] == [
        None,
        None,
    ]  # el transbordo no se encadena


TARIFAS_APP = Path(__file__).parent.parent / "app" / "datos" / "tarifas.json"
REGENERA = "regenera app/datos/tarifas.json con pipeline_euros.tarifas_json (#234)"


def _publicadas(arbol: dict, niveles: list[str]) -> pd.DataFrame:
    """Aplana el árbol {nivel: {nivel: ... [fila por día]}} de tarifas.json en una tabla."""
    filas = []

    def baja(nodo, claves):
        if isinstance(nodo, list):
            filas.extend(
                (*claves, dias, f["titulo"], f["coste_mes"])
                for dias, f in enumerate(nodo, 1)
            )
            return
        for k, hijo in nodo.items():
            baja(hijo, (*claves, k))

    baja(arbol, ())
    return pd.DataFrame(filas, columns=[*niveles, "dias", "titulo", "coste_mes"])


def _distintas(publicada: pd.DataFrame, codigo: pd.DataFrame, claves: list[str]):
    """Filas que faltan, sobran o cambian de título o de coste entre el fichero y el código."""
    m = publicada.merge(
        codigo, on=claves, how="outer", indicator=True, validate="one_to_one"
    )
    return m[
        (m["_merge"] != "both")
        | (m["titulo_x"] != m["titulo_y"])
        | (m["coste_mes_x"] != m["coste_mes_y"])
    ]


def _meta_tarifas():
    return _tarifas()["meta"], json.loads(TARIFAS_APP.read_text("utf-8"))["meta"]


def test_meta_visible_describe_solo_la_v1():
    for meta in _meta_tarifas():
        for v2 in ("tarifas_ruta", "Renfe", "+65", "79 %"):
            assert v2 not in meta["nota"]
        assert not re.search(r"#\d", meta["nota"])
        assert "2023" not in meta["nota"]
        assert "ayuntamientos" in meta["nota"]
        assert "ordinario" in meta["nota"] and "sin ocio" in meta["nota"]
        nombres = " ".join(f["nombre"] for f in meta["fuentes"])
        assert (
            "capítulo III" in nombres
            and "arts. 5 a 17" in nombres
            and "art. 3" not in nombres
        )
        assert not any("verificar" in f["licencia"] for f in meta["fuentes"])
        fichas = [
            f for f in meta["fuentes"] if "crtm.es/billetes-y-tarifas" in f["url"]
        ]
        assert fichas and not any("datos abiertos" in f["licencia"] for f in fichas)
        urls = " ".join(f["url"] for f in meta["fuentes"])
        assert "renfe.com" not in urls and "abono-plus65" not in urls
        assert "BOE-A-2025-26459" in urls


def test_meta_ruta_lleva_la_v2_y_sus_fuentes():
    for meta in _meta_tarifas():
        assert "tarifas_ruta" in meta["nota_ruta"]
        assert not re.search(r"#\d", meta["nota_ruta"])
        urls = " ".join(f["url"] for f in meta["fuentes_ruta"])
        assert "abono-plus65" in urls and "renfe.com" not in urls
        assert "3.2.a).2.º" in " ".join(f["nombre"] for f in meta["fuentes_ruta"])
        assert not any("verificar" in f["licencia"] for f in meta["fuentes_ruta"])


def test_tarifas_publicadas_v1_al_dia_con_transporte():
    j = json.loads(TARIFAS_APP.read_text("utf-8"))
    niveles = ["escenario", "edad", "viajes_dia", "corona"]
    codigo = transporte.tabla_v1()
    codigo["edad"] = codigo.pop("joven").map({True: "joven", False: "general"})
    codigo["viajes_dia"] = codigo["viajes_dia"].astype(str)
    mal = _distintas(_publicadas(j["escenarios"], niveles), codigo, [*niveles, "dias"])
    assert mal.empty, (
        f"{len(mal)} filas v1 distintas; {REGENERA}:\n{mal.head(10).to_string()}"
    )
    assert j["semanas_mes"] == pytest.approx(227 / 60)


def test_tarifas_publicadas_v2_al_dia_con_transporte():
    j = json.loads(TARIFAS_APP.read_text("utf-8"))
    niveles = ["escenario", "colectivo", "edad", "clave_tarifa", "no_laborables"]
    codigo = transporte.tabla(j["claves"])
    codigo["no_laborables"] = codigo["no_laborables"].astype(str)
    mal = _distintas(
        _publicadas(j["tarifas_ruta"], niveles), codigo, [*niveles, "dias"]
    )
    assert mal.empty, (
        f"{len(mal)} filas v2 distintas; {REGENERA}:\n{mal.head(10).to_string()}"
    )


def test_tarifas_publicadas_controles_joven_b2():
    b2 = json.loads(TARIFAS_APP.read_text("utf-8"))["escenarios"]["vigente_2026"]
    b2 = b2["joven"]["2"]["B2"]
    # 1 día: 2 × 227/60 = 7,567 viajes × 9,60 €/10 (10 viajes interurbano de dos saltos, con descuento);
    # desde el prorrateo de #271 baja del Abono Joven (el 9,31 de la auditoría de #73 era con paquetes enteros)
    assert b2[0] == {"titulo": "10 viajes", "coste_mes": 7.26}
    # 5 días: Abono Joven, 10 € con descuento × 335/30 compras al año / 12
    assert b2[4] == {"titulo": "Abono Joven", "coste_mes": 9.31}


def test_tarifas_publicadas_controles_oficial_y_colectivo():
    j = json.loads(TARIFAS_APP.read_text("utf-8"))
    # sin descuento, A, 5 días: 2 × 5 × 227/60 viajes × 12,50 €/10 (BOCM-20251231-3 pág. 72) < abono 52,30
    a = j["escenarios"]["sin_descuento"]["general"]["2"]["A"][4]
    assert a == {"titulo": "10 viajes", "coste_mes": 47.29}
    # FN especial, A-B2, 5 días: 37,833 viajes × 4,80 €/10 (BOCM-20251231-2 pág. 67) < abono 20,10
    ruta = j["tarifas_ruta"]["vigente_2026"]["fn_especial"]["general"]
    assert ruta["A-B2|interurbano"]["0"][4] == {
        "titulo": "10 viajes",
        "coste_mes": 18.16,
    }
