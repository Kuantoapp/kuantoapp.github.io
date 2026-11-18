"""`pipeline_euros`: cada JSON cumple el contrato y las reglas de elección de datos."""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import Point

from mesobra import imputacion, neto, pipeline_euros, transporte
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
    assert m2_por_defecto(zona) == 40


def test_netos_tarifas_y_hogares_cumplen_el_contrato():
    netos = pd.read_csv(PROCESSED / "netos.csv").query("bruto_anual <= 30000")
    validar("netos.json", netos_json(netos))
    validar("netos.json", netos_json(neto.rejilla()))
    validar("tarifas.json", _tarifas())
    tabla = pd.read_csv(PROCESSED / "hogares.csv")
    tabla.attrs["nota"] = "Estimado"
    cesta = pd.Series({"alimentacion": 275.0, "suministros": 81.0})
    obj = hogares_json(tabla, cesta, 69)
    validar("hogares.json", obj)
    assert {p["m2"] for p in obj["perfiles"].values()} == {69}


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
        transporte.tabla_v1(), transporte.tabla(lista), claves, ["28065", "28092"]
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
    assert o["claves"] == ["B1-B1|interurbano", "B1-B2|interurbano"]
    assert o["clave_tarifa"] == [[0, 1], [1, None]]
    assert o["clave_estimada"]
    assert o["colectivos"] == COLECTIVOS
    por_colectivo = o["tarifas_ruta"]["vigente_2026"]
    assert sorted(por_colectivo) == sorted(COLECTIVOS)
    cinco = por_colectivo["ordinario"]["general"]["B1-B2|interurbano"]["0"][4]
    assert cinco == {"titulo": "Abono 30 días B1-B2", "coste_mes": 26.71}
    # 14,30 € del interzonal para FN especial (BOCM-20251231-2 pág. 66) × 335/30 / 12
    cinco = por_colectivo["fn_especial"]["general"]["B1-B2|interurbano"]["0"][4]
    assert cinco == {"titulo": "Abono 30 días B1-B2", "coste_mes": 13.31}
