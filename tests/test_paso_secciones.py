"""Tests de `mesobra.paso_secciones` con un recorte inventado: anidamiento, partición y fusión."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import paso_secciones as p

X0, Y0 = 440000, 4474000


def _capa(filas: dict[str, tuple[float, float, float, float]]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"CUSEC": list(filas), "geometry": [box(*b) for b in filas.values()]},
        crs=25830,
    )


@pytest.fixture
def capas() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, pd.Series]:
    """A queda entera, B se parte en B1 y B2 por la mitad, C y D se fusionan en CD."""
    o = _capa(
        {
            "A": (X0, Y0, X0 + 100, Y0 + 100),
            "B": (X0 + 100, Y0, X0 + 200, Y0 + 100),
            "C": (X0 + 200, Y0, X0 + 250, Y0 + 100),
            "D": (X0 + 250, Y0, X0 + 300, Y0 + 100),
        }
    )
    d = _capa(
        {
            "A2": (X0, Y0, X0 + 100, Y0 + 100),
            "B1": (X0 + 100, Y0, X0 + 150, Y0 + 100),
            "B2": (X0 + 150, Y0, X0 + 200, Y0 + 100),
            "CD": (X0 + 200, Y0, X0 + 300, Y0 + 100),
        }
    )
    return o, d, pd.Series({"A2": 100, "B1": 30, "B2": 10, "CD": 60})


def test_anida_parte_y_fusiona(capas) -> None:
    o, d, _ = capas
    tabla, cobertura = p.tabla_paso(*capas)
    p.comprobar_tabla(tabla)
    peso = tabla.set_index(["origen", "destino"])["peso"]
    assert peso["A", "A2"] == pytest.approx(1)
    # B reparte por la población de cada mitad: 30 frente a 10
    assert peso["B", "B1"] == pytest.approx(0.75)
    assert peso["B", "B2"] == pytest.approx(0.25)
    assert peso["C", "CD"] == pytest.approx(1)
    assert (cobertura > 0.99).all()
    c = p.secciones_cambiadas(tabla, pd.Index(o["CUSEC"]), pd.Index(d["CUSEC"]))
    assert list(c["partidos"]) == ["B"]
    assert list(c["fusionados"]) == ["CD"]
    assert c["sin_destino"].empty and c["sin_origen"].empty


def test_extensiva_se_conserva_e_intensiva_se_pondera(capas) -> None:
    tabla, _ = p.tabla_paso(*capas)
    testigos = pd.Series({"A": 10, "B": 40, "C": 6, "D": 4})
    repartido = p.pasar_extensiva(tabla, testigos)
    assert repartido.sum() == pytest.approx(testigos.sum())
    assert repartido["B1"] == pytest.approx(30)
    # CD fusiona C y D con la misma superficie: media de 10 y 20, no suma
    precio = p.pasar_intensiva(
        tabla, pd.Series({"A": 1.0, "B": 2.0, "C": 10.0, "D": 20.0})
    )
    assert precio["CD"] == pytest.approx(15)
    assert precio["B1"] == pytest.approx(2)


def test_total_por_municipio_falla_si_cae_en_otro(capas) -> None:
    tabla, _ = p.tabla_paso(*capas)
    municipio = pd.Series("28001", index=["A", "B", "C", "D"])
    # los destinos del recorte no empiezan por 28001: el total cae en otro municipio y debe fallar
    with pytest.raises(ValueError, match="no conservado"):
        p.total_por_municipio(tabla, pd.Series(1, index=municipio.index), municipio)


def test_origen_sin_poblacion_se_reparte_por_area(capas) -> None:
    o, d, _ = capas
    tabla, _ = p.tabla_paso(o, d, pd.Series({"A2": 100, "B1": 0, "B2": 0, "CD": 60}))
    b = tabla[tabla["origen"] == "B"]
    assert set(b["metodo"]) == {"area"}
    assert b["peso"].tolist() == pytest.approx([0.5, 0.5])
