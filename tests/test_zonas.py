"""Tests de `mesobra.zonas` con un recorte inventado de secciones en EPSG:25830."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import zonas

X0, Y0 = 440000, 4474000  # cerca de la Puerta del Sol, en metros
# sin edificios cada sección usa su punto representativo, que en un rectángulo es su centro
SIN_EDIFICIOS = gpd.GeoSeries([], crs=25830)


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
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS).set_index("zona_id")
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
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS).set_index("zona_id")
    centros = gpd.GeoSeries.from_xy(
        z["lon_centro"], z["lat_centro"], crs=4326, index=z.index
    ).to_crs(25830)
    # Centro: pesos 100 y 300 en y = Y0+500 y Y0+1500; Getafe: 10 y 30 en x = +30500 y +31500
    assert centros["2807901"].x == pytest.approx(X0 + 500, abs=1e-3)
    assert centros["2807901"].y == pytest.approx(Y0 + 1250, abs=1e-3)
    assert centros["28065"].x == pytest.approx(X0 + 31250, abs=1e-3)
    assert centros["28065"].y == pytest.approx(Y0 + 500, abs=1e-3)


def test_punto_de_poblacion_es_la_media_de_sus_edificios(secciones):
    # dos edificios en la esquina de la primera sección de Getafe; la segunda no tiene ninguno
    edificios = gpd.GeoSeries.from_xy(
        [X0 + 30100, X0 + 30300], [Y0 + 100, Y0 + 100], crs=25830
    )
    puntos = zonas.puntos_poblacion(secciones, edificios)
    getafe = secciones["CUSEC"].to_numpy()
    p1, p2 = (
        puntos[getafe == "2806501001"].iloc[0],
        puntos[getafe == "2806501002"].iloc[0],
    )
    assert (p1.x, p1.y) == pytest.approx((X0 + 30200, Y0 + 100))
    assert (p2.x, p2.y) == pytest.approx((X0 + 31500, Y0 + 500))  # punto representativo


def test_punto_de_poblacion_no_sale_de_su_seccion():
    # sección en L con un núcleo en cada brazo: la media (+1.500, +1.500) cae en el hueco de la L
    ele = box(X0, Y0, X0 + 3000, Y0 + 1000).union(box(X0, Y0, X0 + 1000, Y0 + 3000))
    seccion = gpd.GeoDataFrame({"CUSEC": ["2800101001"]}, geometry=[ele], crs=25830)
    edificios = gpd.GeoSeries.from_xy(
        [X0 + 2900, X0 + 2800, X0 + 100], [Y0 + 500, Y0 + 500, Y0 + 2900], crs=25830
    )
    punto = zonas.puntos_poblacion(seccion, edificios).iloc[0]
    assert punto.within(ele)
    assert (punto.x, punto.y) == pytest.approx(
        (X0 + 2800, Y0 + 500)
    )  # el edificio más cercano a la media


def test_el_centro_sigue_a_los_edificios(secciones, poblacion, coronas):
    # Getafe: con todos sus edificios al oeste de su primera sección, el centro deja de estar en el medio
    edificios = gpd.GeoSeries.from_xy(
        [X0 + 30100, X0 + 31100], [Y0 + 500, Y0 + 500], crs=25830
    )
    z = zonas.zonas(secciones, poblacion, coronas, edificios).set_index("zona_id")
    centro = gpd.GeoSeries.from_xy(
        [z.loc["28065", "lon_centro"]], [z.loc["28065", "lat_centro"]], crs=4326
    ).to_crs(25830)[0]
    # pesos 10 y 30 en x = +30100 y +31100
    assert centro.x == pytest.approx(X0 + 30850, abs=1e-3)


def test_leer_edificios_quita_los_que_no_son_vivienda(tmp_path):
    ruta = tmp_path / "osm.gpkg"
    gpd.GeoDataFrame(
        {
            "building": ["house", "industrial", "yes", None],
            "geometry": [
                box(X0 + i * 100, Y0, X0 + i * 100 + 10, Y0 + 10) for i in range(4)
            ],
        },
        crs=25830,
    ).to_crs(4326).to_file(ruta, layer="multipolygons")
    edificios = zonas.leer_edificios(ruta)
    assert edificios.crs.to_epsg() == 25830
    assert sorted(round(p.x) for p in edificios) == [X0 + 5, X0 + 205]


def test_centro_en_un_hueco_entre_nucleos_pasa_al_nucleo_mas_cercano(
    secciones, poblacion, coronas, caplog
):
    # Getafe continuo, pero la segunda sección mide 7 km y su núcleo está al fondo (+37.900):
    # la media (+36.050) queda dentro de la zona y a 1.850 m de todo núcleo
    ancha = secciones["CUSEC"] == "2806501002"
    secciones.loc[ancha, "geometry"] = box(X0 + 31000, Y0, X0 + 38000, Y0 + 1000)
    edificios = gpd.GeoSeries.from_xy(
        [X0 + 30500, X0 + 37900], [Y0 + 500] * 2, crs=25830
    )
    z = zonas.zonas(secciones, poblacion, coronas, edificios).set_index("zona_id")
    centro = gpd.GeoSeries.from_xy(
        [z.loc["28065", "lon_centro"]], [z.loc["28065", "lat_centro"]], crs=4326
    ).to_crs(25830)[0]
    assert centro.x == pytest.approx(X0 + 37900, abs=1e-3)
    assert "28065" in caplog.text


def test_corona_del_centro(secciones, poblacion, coronas):
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS).set_index("zona_id")
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
        zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)


def test_secciones_sin_poblacion_fallan(secciones, poblacion, coronas):
    with pytest.raises(ValueError, match="no casan"):
        zonas.zonas(secciones, poblacion.drop("2806501002"), coronas, SIN_EDIFICIOS)


@pytest.mark.parametrize("cambio", ["prefijo", "falta_distrito"])
def test_distritos_que_no_casan_fallan(secciones, cambio):
    if cambio == "prefijo":
        secciones.loc[secciones["CUSEC"] == "2807902001", "CDIS"] = "03"
    else:
        secciones = secciones[secciones["CDIS"] != "21"]
    with pytest.raises(ValueError, match="Plan B"):
        zonas.comprobar_distritos(secciones)


def test_centro_en_dos_coronas_falla(secciones, poblacion, coronas):
    solape = coronas.assign(
        corona="B2", geometry=box(X0 + 30000, Y0, X0 + 32000, Y0 + 1000)
    )
    with pytest.raises(ValueError, match="dos coronas"):
        zonas.zonas(secciones, poblacion, pd.concat([coronas, solape]), SIN_EDIFICIOS)


def test_zona_sin_poblacion_falla(secciones, poblacion, coronas):
    poblacion[["2806501001", "2806501002"]] = 0
    with pytest.raises(ValueError, match="sin población"):
        zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)


def test_centro_fuera_de_su_zona_pasa_a_la_seccion_mas_cercana(
    secciones, poblacion, coronas, caplog
):
    # Getafe partido en dos trozos: la media (+33.500) cae en el hueco; la sección más cercana es la de +34.500
    lejos = secciones["CUSEC"] == "2806501002"
    secciones.loc[lejos, "geometry"] = box(X0 + 34000, Y0, X0 + 35000, Y0 + 1000)
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS).set_index("zona_id")
    centro = gpd.GeoSeries.from_xy(
        [z.loc["28065", "lon_centro"]], [z.loc["28065", "lat_centro"]], crs=4326
    ).to_crs(25830)[0]
    assert centro.x == pytest.approx(X0 + 34500, abs=1e-3)
    assert "28065" in caplog.text


def _coronas(frontera_x: float, suelo_b1: float = Y0 - 1000) -> gpd.GeoDataFrame:
    """A hasta `frontera_x` y B1 desde ahí, con B1 empezando en `suelo_b1` por abajo."""
    return gpd.GeoDataFrame(
        {
            "corona": ["A", "B1"],
            "geometry": [
                box(X0 - 1000, Y0 - 1000, frontera_x, Y0 + 3000),
                box(frontera_x, suelo_b1, X0 + 40000, Y0 + 3000),
            ],
        },
        crs=25830,
    )


def test_sin_coronas_dudosas(secciones, poblacion, coronas):
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)
    por_zona = zonas.secciones_por_zona(secciones, poblacion)
    assert zonas.coronas_dudosas(por_zona, z, coronas).empty


# Getafe: 10 personas en [+30, +31] km y 30 en la segunda sección; cada caso cumple una sola condición
ANCHA = box(
    X0 + 31000, Y0, X0 + 35000, Y0 + 1000
)  # centro en +32,375 km, a 1.375 m de +31 km
CASOS_DUDOSOS = {
    # la primera sección entera en A: cuota 0,75 por las dos vías
    "cuota": (ANCHA, _coronas(X0 + 31000), (0.75, 0.75, 1375)),
    # B1 empieza 400 m por debajo de Getafe: centro a 900 m del borde
    "distancia": (None, _coronas(X0 + 30000, Y0 - 400), (1.0, 1.0, 900)),
    # la frontera deja el 45 % de la primera sección en A y su punto en B1: solo baja la cuota por área
    "area": (ANCHA, _coronas(X0 + 30450), (1.0, (5.5 + 30) / 40, 1500)),
}


@pytest.mark.parametrize("caso", CASOS_DUDOSOS)
def test_coronas_dudosas_por_cada_condicion(secciones, poblacion, caso):
    segunda, coronas, esperado = CASOS_DUDOSOS[caso]
    if segunda is not None:
        secciones.loc[secciones["CUSEC"] == "2806501002", "geometry"] = segunda
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)
    dudosas = zonas.coronas_dudosas(
        zonas.secciones_por_zona(secciones, poblacion), z, coronas
    )
    assert dudosas.index.tolist() == ["28065"]
    fila = dudosas.loc["28065", ["cuota_punto", "cuota_area", "distancia_borde_m"]]
    assert fila.tolist() == pytest.approx(esperado, abs=1e-3)


def test_seccion_sin_corona_cuenta_cero(secciones, poblacion):
    # sin A: la primera sección de Getafe no cae en ninguna corona y su población no cuenta
    solo_b1 = _coronas(X0 + 31000).iloc[[1]]
    madrid = gpd.GeoDataFrame(
        {"corona": ["A"], "geometry": [box(X0, Y0, X0 + 21000, Y0 + 2000)]}, crs=25830
    )
    coronas = pd.concat([solo_b1, madrid])
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)
    dudosas = zonas.coronas_dudosas(
        zonas.secciones_por_zona(secciones, poblacion), z, coronas
    )
    assert dudosas.loc["28065", ["cuota_punto", "cuota_area"]].tolist() == [0.75, 0.75]


def test_coronas_dudosas_compara_sin_redondear(secciones, poblacion):
    # 8.996 de 10.000 en B1: 0,8996 se redondea a 0,900 pero está por debajo del umbral
    secciones.loc[secciones["CUSEC"] == "2806501002", "geometry"] = ANCHA
    poblacion[["2806501001", "2806501002"]] = [1004, 8996]
    coronas = _coronas(X0 + 31000)
    z = zonas.zonas(secciones, poblacion, coronas, SIN_EDIFICIOS)
    dudosas = zonas.coronas_dudosas(
        zonas.secciones_por_zona(secciones, poblacion), z, coronas
    )
    assert dudosas.index.tolist() == ["28065"]
    assert dudosas.loc["28065", "cuota_punto"] == 0.9


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
