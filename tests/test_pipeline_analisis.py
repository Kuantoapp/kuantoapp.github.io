"""Tests del pipeline y las figuras del informe de análisis (#90), con tablas de juguete en memoria."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import api_estatica, figuras, pipeline_analisis, sdm


def _esfuerzo() -> pd.DataFrame:
    filas = [
        ("28079", 2015, 1000.0, 5000.0, 0.20),
        ("28079", 2020, 1050.0, 5000.0, 0.21),
        ("28079", 2024, 1100.0, 5000.0, 0.22),
        ("28001", 2015, 500.0, 2500.0, 0.20),
        ("28001", 2024, 600.0, 2500.0, 0.24),
        ("28002", 2015, 400.0, np.nan, np.nan),  # renta secreta: no entra en el JSON
        ("28002", 2024, np.nan, 2000.0, np.nan),  # sin alquiler: entra con null
    ]
    return pd.DataFrame(
        filas,
        columns=["zona_id", "anio", "alquiler_mes_p50", "renta_hogar_mes", "esfuerzo"],
    )


def _bono() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "municipio_id": ["28001", "28002"],
            "solicitudes": [10, 4],
            "aceptadas": [2, 1],
            "rechazadas": [8, 3],
            "poblacion_joven": [1000, 500],
            "necesidad": [240.0, np.nan],
            "indicador_necesidad": ["esfuerzo", "esfuerzo"],
            "grupo": ["necesidad_alta_ayuda_baja", "sin_dato"],
        }
    )


def test_analisis_json_valida_y_cita_las_fuentes():
    obj = pipeline_analisis.analisis_json(_esfuerzo(), _bono())
    api_estatica.validar("analisis.json", obj)
    assert len(obj["esfuerzo"]) == 6  # sin la fila de renta nula
    assert {f["zona_id"] for f in obj["esfuerzo"]} >= {"28002"}
    assert obj["titulares"]
    assert sdm._citas_que_faltan(obj["meta"]) == []


def test_titulares_cifras():
    madrid, sube, bono = pipeline_analisis.titulares(_esfuerzo(), _bono())
    assert all(c in madrid["texto"] for c in ("22,0 %", "20,0 %", "21,0 %"))
    assert "1 de las 1 zonas" in sube["texto"] and "4,00 puntos" in sube["texto"]
    assert "21,4 %" in bono["texto"]  # 3 aceptadas de 14 solicitudes


def test_cortes_simetricos():
    cortes = figuras.cortes_simetricos(
        pd.Series([-0.04, -0.01, np.nan, 0.01, 0.02, 0.03])
    )
    assert len(cortes) == 7 and 0 in cortes
    assert cortes == sorted(cortes)
    assert cortes == [-c for c in reversed(cortes)]


def test_mapa_escribe_png(tmp_path):
    zonas = gpd.GeoDataFrame(
        {
            "zona_id": ["2807901", "28001"],
            "tipo": ["distrito", "municipio"],
            "municipio_id": ["28079", "28001"],
        },
        geometry=[box(0, 0, 1, 1), box(2, 0, 3, 1)],
        crs=figuras.CRS,
    )
    g = figuras._unir(zonas, pd.Series({"2807901": 0.2, "28001": 0.3}))
    figuras._mapa(g, [0.1, 0.25, 0.4], "YlOrRd", "Prueba", tmp_path / "m.png")
    assert (tmp_path / "m.png").stat().st_size > 0
    with pytest.raises(ValueError, match="sin geometría"):
        figuras._unir(zonas, pd.Series({"28999": 0.1}))
