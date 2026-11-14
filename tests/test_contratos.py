"""Contratos de `data/processed/`: los fixtures los cumplen y `validar` detecta cada incumplimiento."""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest

from mesobra.contratos import CONTRATOS, dtypes, validar

FIXTURES = Path(__file__).parent / "fixtures" / "processed"
ZONAS = {"2807901", "2807913", "28065", "28092", "28001"}


def _leer(nombre):
    df = pd.read_csv(FIXTURES / f"{nombre}.csv", dtype=dtypes(nombre))
    if "geometry" in df:
        df = gpd.GeoDataFrame(
            df.drop(columns="geometry"),
            geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
            crs=25830,
        )
    return df


@pytest.mark.parametrize("nombre", CONTRATOS)
def test_fixture_cumple_su_contrato(nombre):
    assert (FIXTURES / f"{nombre}.csv").exists()
    validar(_leer(nombre), nombre)


@pytest.mark.parametrize(
    "nombre", [n for n, c in CONTRATOS.items() if "zona_id" in c["columnas"]]
)
def test_tablas_con_zona_incluyen_las_cinco_zonas(nombre):
    assert ZONAS <= set(_leer(nombre)["zona_id"])


def test_zona_sin_dato_de_alquiler():
    df = _leer("alquiler_zona")
    assert df.loc[df["zona_id"] == "28001", "origen"].item() == "sin_dato"


def test_falta_columna():
    with pytest.raises(
        ValueError, match=r"^hogares: .*faltan columnas: \['suministros'\]"
    ):
        validar(_leer("hogares").drop(columns="suministros"), "hogares")


def test_sobra_columna():
    with pytest.raises(ValueError, match=r"^hogares: .*sobran columnas: \['extra'\]"):
        validar(_leer("hogares").assign(extra=1), "hogares")


def test_tipo_cambiado():
    df = _leer("hogares").astype({"adultos": "string"})
    with pytest.raises(ValueError, match="adultos: se esperaba entero"):
        validar(df, "hogares")


def test_clave_repetida():
    df = pd.concat([_leer("hogares"), _leer("hogares").head(1)], ignore_index=True)
    with pytest.raises(ValueError, match="clave .* repetida"):
        validar(df, "hogares")


def test_zonas_con_otro_crs():
    with pytest.raises(ValueError, match="EPSG:25830"):
        validar(_leer("zonas").to_crs(4326), "zonas")


def test_reune_todos_los_problemas():
    df = _leer("hogares").drop(columns="anio").assign(extra=1)
    with pytest.raises(ValueError, match="faltan.*sobran"):
        validar(df, "hogares")
