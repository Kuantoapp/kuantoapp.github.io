"""`pipeline_euros`: cada JSON cumple el contrato y las reglas de elección de datos."""

from pathlib import Path

import pandas as pd
import pytest

from mesobra import neto, transporte
from mesobra.api_estatica import validar
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
    validar("alquiler.json", alquiler_json(zona.query("origen != 'estimado'")))
    # alquiler_zona aún no produce estimados
    with pytest.raises(ValueError, match=r"\.ic:"):
        validar("alquiler.json", alquiler_json(zona))


def test_netos_tarifas_y_hogares_cumplen_el_contrato():
    netos = pd.read_csv(PROCESSED / "netos.csv").query("bruto_anual <= 30000")
    validar("netos.json", netos_json(netos))
    validar("netos.json", netos_json(neto.rejilla()))
    validar("tarifas.json", tarifas_json(transporte.tabla()))
    tabla = pd.read_csv(PROCESSED / "hogares.csv")
    tabla.attrs["nota"] = "Estimado"
    cesta = pd.Series({"alimentacion": 275.0, "suministros": 81.0})
    obj = hogares_json(tabla, cesta, 69)
    validar("hogares.json", obj)
    assert {p["m2"] for p in obj["perfiles"].values()} == {69}


def test_tarifas_trae_los_dos_viajes_al_dia():
    a = tarifas_json(transporte.tabla())["escenarios"]["vigente_2026"]["general"]
    assert a["2"]["A"][2] == {"titulo": "10 viajes", "coste_mes": 21.9}
    assert a["4"]["A"][2] == {"titulo": "Abono 30 días", "coste_mes": 30.43}
