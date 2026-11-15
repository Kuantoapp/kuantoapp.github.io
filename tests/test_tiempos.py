"""Tests de `mesobra.tiempos` sin Java: línea base, mediana, tiempo interno, nulos y GTFS sintéticos."""

import importlib
import io
import logging
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import tiempos

X0, Y0 = 440000, 4474000  # cerca de la Puerta del Sol, en metros
CENTROS_M = {
    "A": (X0 + 500, Y0 + 500),
    "B": (X0 + 10500, Y0 + 500),
    "C": (X0 + 200500, Y0 + 500),
}


@pytest.fixture
def secciones() -> gpd.GeoDataFrame:
    """A con dos secciones (centroides a 0 y 2 km del centro), B con una y C con una, a 200 km."""
    filas = [
        ("A001", "A", box(X0, Y0, X0 + 1000, Y0 + 1000)),
        ("A002", "A", box(X0 + 2000, Y0, X0 + 3000, Y0 + 1000)),
        ("B001", "B", box(X0 + 10000, Y0, X0 + 11000, Y0 + 1000)),
        ("C001", "C", box(X0 + 200000, Y0, X0 + 201000, Y0 + 1000)),
    ]
    return gpd.GeoDataFrame(filas, columns=["CUSEC", "zona_id", "geometry"], crs=25830)


@pytest.fixture
def zonas() -> pd.DataFrame:
    centros = gpd.GeoSeries.from_xy(
        *zip(*CENTROS_M.values(), strict=True), crs=25830
    ).to_crs(4326)
    return pd.DataFrame(
        {"zona_id": list(CENTROS_M), "lon_centro": centros.x, "lat_centro": centros.y}
    )


def _minutos(km: float) -> float:
    return km * tiempos.FACTOR_RODEO / tiempos.VELOCIDAD_KMH * 60


def _par(tabla: pd.DataFrame, origen: str, destino: str) -> float:
    return tabla.set_index(["zona_id", "destino_id"]).loc[(origen, destino), "minutos"]


def test_linea_base_es_distancia_por_rodeo_entre_velocidad(zonas, secciones):
    tabla = tiempos.linea_base(zonas, secciones)
    assert _par(tabla, "A", "B") == pytest.approx(_minutos(10), abs=0.01)
    assert _par(tabla, "B", "A") == pytest.approx(_par(tabla, "A", "B"))


def test_linea_base_tiene_todos_los_pares_y_el_contrato(zonas, secciones):
    tabla = tiempos.linea_base(zonas, secciones)  # valida con contratos.validar
    assert len(tabla) == 9
    assert (tabla["modo"] == "tp").all()
    assert tabla["estimado"].all()
    assert tabla["km"].isna().all()


def test_tiempo_interno_es_la_mediana_de_las_secciones_y_nunca_cero(zonas, secciones):
    tabla = tiempos.linea_base(zonas, secciones)
    # A: centroides a 0 y 2 km del centro → mediana 1 km; B: una sola sección en el centro → suelo
    assert _par(tabla, "A", "A") == pytest.approx(_minutos(1), abs=0.01)
    assert _par(tabla, "B", "A") > 0
    assert _par(tabla, "B", "B") == tiempos.MIN_INTERNO


def test_por_encima_del_maximo_es_nulo(zonas, secciones):
    tabla = tiempos.linea_base(zonas, secciones)
    assert np.isnan(_par(tabla, "A", "C"))  # 200 km
    assert tabla["minutos"].isna().sum() == 4  # C con A y B, en los dos sentidos
    assert tabla["minutos"].dropna().le(tiempos.MAX_MINUTOS).all()


def test_zona_sin_secciones_falla(zonas, secciones):
    with pytest.raises(ValueError, match="sin tiempo interno"):
        tiempos.linea_base(zonas, secciones[secciones["zona_id"] != "C"])


def test_secciones_en_otro_crs_fallan(zonas, secciones):
    with pytest.raises(ValueError, match="EPSG:25830"):
        tiempos.linea_base(zonas, secciones.to_crs(4326))


def test_zona_sin_ruta_interna_falla():
    matriz = pd.DataFrame({"from_id": ["A"], "to_id": ["B"], "minutos": [10.0]})
    with pytest.raises(ValueError, match=r"sin tiempo interno.*'B'"):
        tiempos._tabla(matriz, pd.Series({"A": 5.0, "B": np.nan}))


def test_interno_mediana_por_zona():
    matriz = pd.DataFrame(
        {
            "from_id": ["A001", "A002", "A003", "B001", "A001"],
            "to_id": ["A", "A", "A", "B", "B"],
            "minutos": [4.0, 10.0, 6.0, 3.0, 99.0],
        }
    )
    secciones = pd.DataFrame(
        {"CUSEC": ["A001", "A002", "A003", "B001"], "zona_id": ["A", "A", "A", "B"]}
    )
    interno = tiempos._interno_mediana(matriz, secciones, pd.Index(["A", "B", "C"]))
    assert interno["A"] == 6.0  # mediana de 4, 10 y 6; el par A001 → B no cuenta
    assert interno["B"] == 3.0
    assert np.isnan(interno["C"])


def test_tabla_completa_pares_ausentes_y_sustituye_la_diagonal():
    interno = pd.Series({"A": 7.0, "B": 0.0}, name="minutos")
    matriz = pd.DataFrame(
        {
            "from_id": ["A", "A", "B"],
            "to_id": ["A", "B", "A"],
            "minutos": [0.0, 30.0, 150.0],
        }
    )
    tabla = tiempos._tabla(matriz, interno)
    assert len(tabla) == 4
    assert _par(tabla, "A", "A") == 7.0  # la diagonal de r5py (0) no vale
    assert _par(tabla, "B", "B") == tiempos.MIN_INTERNO  # suelo
    assert _par(tabla, "A", "B") == 30.0
    assert np.isnan(_par(tabla, "B", "A"))  # 150 > 120


def test_preparar_gtfs_arregla_lo_que_r5py_rechaza(tmp_path: Path, caplog):
    def zip_de(ruta: Path, ficheros: dict[str, str]) -> Path:
        with zipfile.ZipFile(ruta, "w") as z:
            for nombre, texto in ficheros.items():
                z.writestr(nombre, texto)
        return ruta

    calendario = "service_id,start_date,end_date\r\nL,20250527,20260527\r\n"
    metro = zip_de(
        tmp_path / "metro.zip",
        {
            "calendar.txt": calendario,
            "fare_rules.txt": "fare_id,route_id\r\n",
            "feed_info.txt": "a\r\n1\r\n2\r\n",
            "trips.txt": "trip_id\r\nT1\r\n",
        },
    )
    urbanos = zip_de(
        tmp_path / "urbanos.zip",
        {
            "google/": "",
            "google/calendar.txt": "service_id,start_date,end_date\r\nL,20261027,20271128\r\n",
            "google/trips.txt": "trip_id\r\nT1\r\n",
        },
    )
    with caplog.at_level(logging.WARNING):
        salida = tiempos.preparar_gtfs([metro, urbanos], tmp_path / "gtfs")
    assert [ruta.name.split("_")[0] for ruta in salida] == ["metro", "urbanos"]
    with zipfile.ZipFile(salida[0]) as z:
        assert sorted(z.namelist()) == ["calendar.txt", "trips.txt"]
        cal = pd.read_csv(io.BytesIO(z.read("calendar.txt")), dtype=str)
    assert cal.loc[0, "end_date"] == tiempos.FIN_CALENDARIO  # caducado: prolongado
    assert cal.loc[0, "start_date"] == "20250527"
    assert "metro.zip" in caplog.text and "caducado" in caplog.text
    with zipfile.ZipFile(salida[1]) as z:
        assert sorted(z.namelist()) == ["calendar.txt", "trips.txt"]  # sin subcarpeta
        assert "20271128" in z.read("calendar.txt").decode()  # vigente: intacto
    assert caplog.text.count("caducado") == 1


def test_el_modulo_se_importa_sin_r5py(monkeypatch, zonas, secciones):
    monkeypatch.setitem(sys.modules, "r5py", None)  # simula que r5py (o Java) no está
    recargado = importlib.reload(tiempos)
    assert len(recargado.linea_base(zonas, secciones)) == 9
    with pytest.raises(ImportError):
        recargado.matriz_r5py(zonas, secciones, Path("no.pbf"), [])
