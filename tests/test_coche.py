"""`mesobra.coche` sin Java: coste con valores a mano, comprobación de tiempos y km, y matriz de km por rodeo."""

import copy
import importlib
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import calculo, coche, tiempos

X0, Y0 = 440000, 4474000  # en metros, cerca de la Puerta del Sol
SEMANAS_MES = 3.7833  # tarifas.json: calculo.viaje usa el mismo valor, no 4,33


def test_coste_en_coche_con_valores_a_mano():
    api = copy.deepcopy(calculo.leer_api(calculo.API_EJEMPLO))
    t = api["tiempos"]
    t["coche"][0][1], t["km_coche"][0][1] = 10, 20.0
    t["coste_coche"] = {"eur_km": coche.EUR_KM}
    sueldo = {"destino": "polo:ifema", "dias": 3, "modo": "coche"}
    assert api["tarifas"]["semanas_mes"] == SEMANAS_MES
    horas, coste = calculo.viaje(api, sueldo, "2807901", {})
    assert coste == pytest.approx(2 * 20 * 3 * SEMANAS_MES * 0.26)
    assert horas == pytest.approx(10 * 2 * 3 * SEMANAS_MES / 60)


XY = pd.DataFrame(
    {"x": [X0, X0 + 10000, X0 + 20000], "y": [Y0] * 3},
    index=["A", "B", "polo:p"],
)
POLOS = pd.DataFrame({"destino_id": ["polo:p"], "zona_id": ["B"]})


def _tabla(km: list[float], minutos: list[float]) -> pd.DataFrame:
    """A → B (10 km en línea recta), A → polo:p (20 km) y B → B (diagonal)."""
    return pd.DataFrame(
        {
            "zona_id": ["A", "A", "B"],
            "destino_id": ["B", "polo:p", "B"],
            "km": km,
            "minutos": minutos,
        }
    )


def test_comprobar_acepta_datos_buenos_y_nulos():
    coche.comprobar(_tabla([13.0, 26.0, 0.5], [15, 30, 1]), XY, POLOS)
    coche.comprobar(_tabla([13.0, np.nan, 0.5], [15, np.nan, 1]), XY, POLOS)


@pytest.mark.parametrize(
    ("km", "minutos", "causa"),
    [
        ([9.9, 26.0, 0.5], [15, 30, 1], "línea recta"),
        ([13.0, 26.0, 0.5], [15, 0, 1], "tiempo <= 0"),
        ([13.0, 26.0, 0.0], [15, 30, 1], "km <= 0"),
        ([13.0, 60.1, 0.5], [15, 30, 1], "velocidad > 120"),
    ],
)
def test_comprobar_falla_con_datos_malos(km, minutos, causa):
    with pytest.raises(ValueError, match=causa):
        coche.comprobar(_tabla(km, minutos), XY, POLOS)


def test_comprobar_no_pone_tope_de_velocidad_a_la_diagonal():
    coche.comprobar(_tabla([13.0, 26.0, 3.0], [15, 30, 1]), XY, POLOS)


def test_comprobar_falla_si_falta_una_coordenada():
    with pytest.raises(ValueError, match="Sin coordenadas"):
        coche.comprobar(_tabla([13.0, 26.0, 0.5], [15, 30, 1]), XY.drop("B"), POLOS)


def test_km_rodeo_con_mediana_de_edificios_en_la_diagonal_y_el_polo_propio():
    # A: edificios a 0 y 2 km del centro y a 3 y 1 km del polo; B: uno a 1 km de su centro
    edificios = pd.DataFrame(
        {
            "x": [X0 + 500, X0 + 2500, X0 + 11500],
            "y": [Y0 + 500] * 3,
            "zona_id": ["A", "A", "B"],
        }
    )
    centros = pd.DataFrame(
        {"x": [X0 + 500, X0 + 10500], "y": [Y0 + 500] * 2}, index=["A", "B"]
    )
    polo = pd.DataFrame({"x": [X0 + 3500], "y": [Y0 + 500]}, index=["polo:p"])
    lista = pd.DataFrame({"destino_id": ["polo:p"], "zona_id": ["A"]})
    km = coche._km_rodeo(centros, pd.concat([centros, polo]), edificios, lista)
    r = tiempos.FACTOR_RODEO
    assert km[("A", "B")] == pytest.approx(10 * r)
    assert km[("A", "A")] == pytest.approx(1 * r)  # mediana de 0 y 2 km
    assert km[("B", "B")] == pytest.approx(1 * r)  # nunca 0 km
    assert km[("B", "polo:p")] == pytest.approx(
        7 * r
    )  # centro a centro, no es el polo de su zona
    assert km[("A", "polo:p")] == pytest.approx(2 * r)  # mediana de 3 y 1 km


def test_edificios_por_zona_asigna_la_seccion_que_los_contiene():
    secciones = gpd.GeoDataFrame(
        {
            "zona_id": ["A", "B"],
            "geometry": [
                box(X0, Y0, X0 + 1000, Y0 + 1000),
                box(X0 + 5000, Y0, X0 + 6000, Y0 + 1000),
            ],
        },
        crs=25830,
    )
    puntos = gpd.GeoSeries.from_xy(
        [X0 + 10, X0 + 5500, X0 + 9000], [Y0 + 10] * 3, crs=25830
    )
    e = coche.edificios_por_zona(puntos, secciones)
    assert e["zona_id"].tolist() == ["A", "B"]  # el tercero cae fuera de toda sección
    assert e["x"].tolist() == [X0 + 10, X0 + 5500]


def test_el_modulo_se_importa_sin_r5py(monkeypatch):
    monkeypatch.setitem(sys.modules, "r5py", None)
    recargado = importlib.reload(coche)
    with pytest.raises(ImportError):
        recargado.matriz_r5py(
            pd.DataFrame(), gpd.GeoDataFrame(), pd.DataFrame(), pd.DataFrame()
        )
