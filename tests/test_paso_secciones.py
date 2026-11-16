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
    # CD fusiona C y D, misma superficie: pondera por testigos (6 y 4), no por área ni suma
    valor = pd.Series({"A": 1.0, "B": 2.0, "C": 10.0, "D": 20.0})
    precio = p.pasar_intensiva(tabla, valor, testigos)
    assert precio["CD"] == pytest.approx((6 * 10 + 4 * 20) / 10)
    assert precio["B1"] == pytest.approx(2)
    # un origen sin dato se excluye y el resto se renormaliza
    sin_c = p.pasar_intensiva(tabla, valor.drop("C"), testigos)
    assert sin_c["CD"] == pytest.approx(20)
    # la pureza mide el mismo conjunto: B1 solo recibe de B, que sin dato no cuenta
    assert "B1" not in p.pureza(tabla, valor.drop("B"), testigos).index
    assert p.pureza(tabla, valor, testigos)[
        ["A2", "B1", "CD"]
    ].tolist() == pytest.approx([1, 0, 1])


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


def test_extensiva_con_origen_fuera_de_la_tabla_falla(capas) -> None:
    tabla, _ = p.tabla_paso(*capas)
    with pytest.raises(ValueError, match="no están en la tabla"):
        p.pasar_extensiva(tabla, pd.Series({"A": 1, "B": 1, "C": 1, "D": 1, "Z": 99}))


def test_destino_sin_poblacion_pondera_por_area(capas) -> None:
    o, d, _ = capas
    tabla, _ = p.tabla_paso(o, d, pd.Series({"A2": 100, "B1": 0, "B2": 10, "CD": 60}))
    p.comprobar_tabla(tabla)  # peso_destino sin NaN
    assert tabla.set_index(["origen", "destino"]).loc[("B", "B1"), "peso_destino"] == 1


def test_astilla_se_descarta_y_el_peso_se_renormaliza() -> None:
    o = _capa({"A": (X0, Y0, X0 + 1000, Y0 + 100)})
    # B2 solo ocupa el 0,05 % del origen: borde que no coincide, no una partición
    d = _capa(
        {
            "B1": (X0, Y0, X0 + 999.5, Y0 + 100),
            "B2": (X0 + 999.5, Y0, X0 + 2000, Y0 + 100),
        }
    )
    tabla, cobertura = p.tabla_paso(o, d, pd.Series({"B1": 10, "B2": 10}))
    assert tabla["destino"].tolist() == ["B1"]
    assert tabla["peso"].tolist() == [1]
    assert cobertura["A"] == pytest.approx(1)


def test_total_por_municipio_conserva_con_codigos_del_mismo_municipio() -> None:
    o = _capa({"2800101001": (X0, Y0, X0 + 100, Y0 + 100)})
    d = _capa(
        {
            "2800101001": (X0, Y0, X0 + 50, Y0 + 100),
            "2800101002": (X0 + 50, Y0, X0 + 100, Y0 + 100),
        }
    )
    tabla, _ = p.tabla_paso(o, d, pd.Series({"2800101001": 1, "2800101002": 3}))
    cuadro = p.total_por_municipio(
        tabla, pd.Series({"2800101001": 8}), pd.Series({"2800101001": "28001"})
    )
    assert cuadro.loc["28001"].tolist() == [8, 8]


def test_destino_sin_poblacion_con_origenes_mixtos_pondera_por_area() -> None:
    # X solo toca D0 (sin población); Y toca D0 y D1: en D0 las piezas mezclarían m² y personas
    o = _capa(
        {"X": (X0, Y0, X0 + 100, Y0 + 100), "Y": (X0 + 100, Y0, X0 + 300, Y0 + 100)}
    )
    d = _capa(
        {"D0": (X0, Y0, X0 + 200, Y0 + 100), "D1": (X0 + 200, Y0, X0 + 300, Y0 + 100)}
    )
    tabla, _ = p.tabla_paso(o, d, pd.Series({"D0": 0, "D1": 10}))
    pd_ = tabla.set_index(["origen", "destino"])["peso_destino"]
    assert pd_["X", "D0"] == pytest.approx(0.5)
    assert pd_["Y", "D0"] == pytest.approx(0.5)
    fusion = p.secciones_cambiadas(tabla, pd.Index(["X", "Y"]), pd.Index(["D0", "D1"]))
    assert list(fusion["fusionados"]) == ["D0"]


def test_intensiva_y_pureza_con_origen_fuera_de_la_tabla_fallan(capas) -> None:
    tabla, _ = p.tabla_paso(*capas)
    valor = pd.Series({"A": 1.0, "Z": 9.0})
    with pytest.raises(ValueError, match="no están en la tabla"):
        p.pasar_intensiva(tabla, valor, pd.Series({"A": 1, "Z": 1}))
    with pytest.raises(ValueError, match="no están en la tabla"):
        p.pureza(tabla, pd.Series({"A": 1.0}), pd.Series({"A": 1, "Z": 1}))
