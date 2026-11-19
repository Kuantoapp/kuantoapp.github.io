"""Tests de `matriz_trabajo` (#301) con un fragmento sintético en el formato de la hoja C23 del INE."""

import pandas as pd
import pytest

from mesobra import matriz_trabajo


def _bruto(filas: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(filas, columns=matriz_trabajo.COLUMNAS)


FILAS = [
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "079", "Madrid", "38887"),
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "092", "Móstoles", "13567"),
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "No consta", None, "4952"),
    ("28", "Madrid", "092", "Móstoles", "08", "Barcelona", "019", "Barcelona", "10"),
    ("28", "Madrid", "092", "Móstoles", "No consta", None, "No consta", None, "598"),
    (
        "01",
        "Araba/Álava",
        "001",
        "Alegría-Dulantzi",
        "28",
        "Madrid",
        "079",
        "Madrid",
        "8",
    ),
]


def test_ordenar_solo_origen_en_la_comunidad_y_no_consta_nulo():
    df = matriz_trabajo.ordenar(_bruto(FILAS))
    assert df["origen"].tolist() == ["28092"] * 5
    assert df["destino"].tolist()[:2] == ["28079", "28092"]
    assert df["destino"].iloc[2:].isna().tolist() == [True, False, True]
    assert df["destino"].iloc[3] == "08019"
    assert df["prov_destino"].isna().tolist() == [False, False, False, False, True]
    assert df["ocupados"].sum() == 38887 + 13567 + 4952 + 10 + 598


def test_ordenar_falla_con_ocupados_no_numericos_o_sin_columna():
    with pytest.raises(ValueError, match="no numéricos"):
        matriz_trabajo.ordenar(_bruto([(*FILAS[0][:8], "..")]))
    with pytest.raises(ValueError, match="columnas"):
        matriz_trabajo.ordenar(_bruto(FILAS).drop(columns="Municipio de trabajo"))
