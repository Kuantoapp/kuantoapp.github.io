"""Tests de `mesobra.zonas` con un recorte inventado de secciones en EPSG:25830."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import zonas

X0, Y0 = 440000, 4474000  # cerca de la Puerta del Sol, en metros


def _seccion(cusec: str, x: float, y: float) -> dict:
    return {
        "CUSEC": cusec,
        "CUMUN": cusec[:5],
        "CDIS": cusec[5:7],
        "NMUN": "Madrid" if cusec.startswith("28079") else "Getafe",
        "geometry": box(x, y, x + 1000, y + 1000),
    }


@pytest.fixture
def secciones() -> gpd.GeoDataFrame:
    """Una sección por distrito de Madrid en fila, otra más en el 01 y dos de Getafe (28065)."""
    filas = [
        _seccion(f"28079{d}001", X0 + i * 1000, Y0)
        for i, d in enumerate(zonas.DISTRITOS)
    ]
    filas += [
        _seccion("2807901002", X0, Y0 + 1000),
        _seccion("2806501001", X0 + 30000, Y0),
        _seccion("2806501002", X0 + 31000, Y0),
    ]
    return gpd.GeoDataFrame(filas, crs=25830)


@pytest.fixture
def poblacion(secciones: gpd.GeoDataFrame) -> pd.Series:
    p = pd.Series(100, index=secciones["CUSEC"].rename("CUSEC"), name="poblacion")
    p[["2807901002", "2806501001", "2806501002"]] = [300, 10, 30]
    return p


@pytest.fixture
def coronas() -> gpd.GeoDataFrame:
    """A cubre Madrid; B1, Getafe."""
    return gpd.GeoDataFrame(
        {
            "corona": ["A", "B1"],
            "geometry": [
                box(X0 - 1000, Y0 - 1000, X0 + 22000, Y0 + 3000),
                box(X0 + 22000, Y0 - 1000, X0 + 40000, Y0 + 3000),
            ],
        },
        crs=25830,
    )


def test_disuelve_en_municipios_y_distritos(secciones, poblacion, coronas):
    z = zonas.zonas(secciones, poblacion, coronas).set_index("zona_id")
    assert len(z) == 22 and (z["tipo"] == "distrito").sum() == 21
    assert z.loc["2807901", ["nombre", "municipio_id", "tipo"]].tolist() == [
        "Centro",
        "28079",
        "distrito",
    ]
    assert z.loc["28065", ["nombre", "municipio_id", "tipo"]].tolist() == [
        "Getafe",
        "28065",
        "municipio",
    ]
    assert z.loc["2807901"].geometry.area == pytest.approx(2e6)
    assert z["poblacion"].sum() == poblacion.sum()
    assert z.loc[["2807901", "28065"], "poblacion"].tolist() == [400, 40]


def test_centro_ponderado_por_poblacion(secciones, poblacion, coronas):
    z = zonas.zonas(secciones, poblacion, coronas).set_index("zona_id")
    centros = gpd.GeoSeries.from_xy(
        z["lon_centro"], z["lat_centro"], crs=4326, index=z.index
    ).to_crs(25830)
    # Centro: pesos 100 y 300 en y = Y0+500 y Y0+1500; Getafe: 10 y 30 en x = +30500 y +31500
    assert centros["2807901"].x == pytest.approx(X0 + 500, abs=1e-3)
    assert centros["2807901"].y == pytest.approx(Y0 + 1250, abs=1e-3)
    assert centros["28065"].x == pytest.approx(X0 + 31250, abs=1e-3)
    assert centros["28065"].y == pytest.approx(Y0 + 500, abs=1e-3)


def test_corona_del_centro(secciones, poblacion, coronas):
    z = zonas.zonas(secciones, poblacion, coronas).set_index("zona_id")
    assert (z.loc[z["tipo"] == "distrito", "corona"] == "A").all()
    assert z.loc["28065", "corona"] == "B1"


@pytest.mark.parametrize("en_madrid", [[], ["E1"]])  # ninguna corona, o una de fuera
def test_centro_sin_corona_de_la_comunidad_falla(
    secciones, poblacion, coronas, en_madrid
):
    coronas = coronas[coronas["corona"] == "B1"]
    madrid = gpd.GeoDataFrame(
        {
            "corona": en_madrid,
            "geometry": [box(X0, Y0, X0 + 21000, Y0 + 2000)] * len(en_madrid),
        },
        crs=25830,
    )
    coronas = pd.concat([coronas, madrid])
    with pytest.raises(ValueError, match="sin corona"):
        zonas.zonas(secciones, poblacion, coronas)


def test_secciones_sin_poblacion_fallan(secciones, poblacion, coronas):
    with pytest.raises(ValueError, match="no casan"):
        zonas.zonas(secciones, poblacion.drop("2806501002"), coronas)


@pytest.mark.parametrize("cambio", ["prefijo", "falta_distrito"])
def test_distritos_que_no_casan_fallan(secciones, cambio):
    if cambio == "prefijo":
        secciones.loc[secciones["CUSEC"] == "2807902001", "CDIS"] = "03"
    else:
        secciones = secciones[secciones["CDIS"] != "21"]
    with pytest.raises(ValueError, match="Plan B"):
        zonas.comprobar_distritos(secciones)


def test_en_dos_coronas_ignora_astillas():
    zona = gpd.GeoDataFrame(
        {
            "zona_id": ["28001", "28002"],
            "geometry": [box(0, 0, 10000, 1000), box(0, 2000, 10000, 3000)],
        },
        crs=25830,
    )
    coronas = gpd.GeoDataFrame(
        {
            "corona": ["A", "B1", "A", "B1"],
            "geometry": [
                box(0, 0, 3000, 1000),  # 30 % de 28001
                box(3000, 0, 10000, 1000),
                box(0, 2000, 10, 3000),  # 0,1 % de 28002
                box(10, 2000, 10000, 3000),
            ],
        },
        crs=25830,
    )
    dos = zonas.en_dos_coronas(zona, coronas)
    assert dos.index.tolist() == ["28001"]
    assert dos.loc["28001", ["A", "B1"]].tolist() == [0.3, 0.7]


CABECERA = "Municipios;Distritos;Secciones;Indicadores demográficos;Periodo;Total"
FILAS = [
    "28001 X;;;Población;2024;1.234",
    "28001 X;2800101 X distrito 01;;Población;2024;1.234",
    "28001 X;2800101 X distrito 01;2800101001 X sección 01001;Población;2024;1.000",
    "28001 X;2800101 X distrito 01;2800101002 X sección 01002;Población;2024;234",
    "28001 X;2800101 X distrito 01;2800101003 X sección 01003;Población;2024;",
    "28001 X;2800101 X distrito 01;2800101001 X sección 01001;Población;2023;999",
    "28001 X;2800101 X distrito 01;2800101001 X sección 01001;Edad media de la población;2024;45,1",
]


def _csv(tmp_path, filas):
    ruta = tmp_path / "adrh.csv"
    ruta.write_text("\n".join([CABECERA, *filas]), encoding="utf-8-sig")
    return ruta


def test_poblacion_secciones_de_2024(tmp_path):
    p = zonas.poblacion_secciones(_csv(tmp_path, FILAS))
    assert p.to_dict() == {"2800101001": 1000, "2800101002": 234}


@pytest.mark.parametrize(
    ("fila", "error"),
    [
        (
            2,
            "28001 X;2800101 X distrito 01;2800101001 X sección 01001;Población;2024;.",
        ),
        (0, "28001 X;;;Población;2024;1.235"),
    ],
)
def test_poblacion_sin_dato_o_que_no_cuadra_falla(tmp_path, fila, error):
    filas = FILAS.copy()
    filas[fila] = error
    with pytest.raises(ValueError, match="sin dato|suman"):
        zonas.poblacion_secciones(_csv(tmp_path, filas))


def test_leer_secciones_solo_madrid(tmp_path, secciones):
    otra = secciones.iloc[[0]].assign(CUSEC="0100101001", CUMUN="01001", NMUN="Alegría")
    capa = pd.concat([secciones, otra]).assign(CPRO=lambda d: d["CUSEC"].str[:2])
    ruta = tmp_path / "secc.shp"
    capa.to_file(ruta)
    leidas = zonas.leer_secciones(ruta)
    assert len(leidas) == len(secciones) and (leidas["CUMUN"] != "01001").all()
