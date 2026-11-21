"""Tests de `mesobra.fondo` con provincias y países inventados en EPSG:4326."""

import json

import geopandas as gpd
import pytest
import shapely
from shapely.geometry import box

from mesobra import fondo


@pytest.fixture
def capas() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Dos provincias vecinas de España, una de Portugal, Francia a caballo de la caja y Alemania fuera."""
    provincias = gpd.GeoDataFrame(
        {"adm0_a3": ["ESP", "ESP", "PRT"]},
        geometry=[box(-4, 40, -3, 41), box(-3, 40, -2, 41), box(-8, 40, -7, 41)],
        crs=4326,
    )
    paises = gpd.GeoDataFrame(
        {"ADM0_A3": ["FRA", "DEU", "ESP"]},
        geometry=[box(0, 43, 8, 48), box(7, 48, 14, 54), box(-9, 36, 3, 44)],
        crs=4326,
    )
    return provincias, paises


def test_provincias_de_espana_y_vecinos_recortados(capas):
    objeto = fondo.fondo(*capas)
    tipos = [f["properties"]["tipo"] for f in objeto["features"]]
    assert tipos == [
        "provincia",
        "provincia",
        "pais",
    ]  # sin Portugal-provincia, Alemania ni la propia España
    oeste, sur, este, norte = fondo.CAJA
    francia = shapely.geometry.shape(objeto["features"][2]["geometry"])
    assert francia.bounds[2] <= este and francia.bounds[3] <= norte
    assert francia.bounds[0] >= oeste and francia.bounds[1] >= sur


def test_provincias_vecinas_sin_hueco_ni_solape(capas):
    a, b = (
        shapely.geometry.shape(f["geometry"])
        for f in fondo.fondo(*capas)["features"][:2]
    )
    assert a.intersection(b).area == pytest.approx(0, abs=1e-9)
    assert a.union(b).area == pytest.approx(2, rel=1e-3)  # dos cuadrados de 1° × 1°


def test_meta_y_json_compacto(capas):
    objeto = fondo.fondo(*capas)
    assert {f["licencia"] for f in objeto["meta"]["fuentes"]} == {fondo.LICENCIA}
    assert "2 provincias" in objeto["meta"]["nota"]
    json.dumps(objeto, allow_nan=False)


def test_rechaza_otro_crs_o_sin_espana(capas):
    provincias, paises = capas
    with pytest.raises(ValueError, match="EPSG:4326"):
        fondo.fondo(provincias.to_crs(25830), paises)
    with pytest.raises(ValueError, match="Ningún país"):
        fondo.fondo(provincias, paises[paises["ADM0_A3"] == "DEU"])
    with pytest.raises(ValueError, match="Ninguna provincia"):
        fondo.fondo(provincias[provincias["adm0_a3"] == "PRT"], paises)


def test_nombres_de_zona_caben_en_los_glifos_del_mapa():
    """app/mapa/glifos solo trae el rango 0-255: un nombre con otro carácter saldría sin esa letra en el mapa."""
    zonas = json.loads((fondo.RAIZ / "app/datos/zonas.geojson").read_text("utf-8"))
    fuera = [
        f["properties"]["nombre"]
        for f in zonas["features"]
        if any(ord(c) > 255 for c in f["properties"]["nombre"])
    ]
    assert fuera == []
    assert (fondo.RAIZ / "app/mapa/glifos/Noto Sans Regular/0-255.pbf").exists()
