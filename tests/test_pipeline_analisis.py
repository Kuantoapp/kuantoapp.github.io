"""Tests del pipeline y las figuras del informe de análisis (#90), con tablas de juguete en memoria."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import api_estatica, figuras, pipeline_analisis, sdm, simulacion


def _esfuerzo() -> pd.DataFrame:
    filas = [
        ("28079", 2015, 1000.0, 5000.0, 0.20),
        ("28079", 2020, 1050.0, 5000.0, 0.21),
        ("28079", 2024, 1100.0, 5000.0, 0.22),
        ("28001", 2015, 500.0, 2500.0, 0.20),
        ("28001", 2024, 600.0, 2500.0, 0.24),
        ("28002", 2015, np.nan, np.nan, np.nan),  # renta secreta: no entra en el JSON
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
    g = figuras._marcar(g, pd.Series({"2807901": True}))
    textos = ("Prueba", figuras._rangos([0.1, 0.25, 0.4]), "")
    figuras._mapa(g, [0.1, 0.25, 0.4], "YlOrRd", textos, tmp_path / "m.png")
    assert (tmp_path / "m.png").stat().st_size > 0
    with pytest.raises(ValueError, match="sin geometría"):
        figuras._unir(zonas, pd.Series({"28999": 0.1}))


def test_analisis_json_falla_si_la_renta_nula_tiene_alquiler():
    tabla = _esfuerzo()
    tabla.loc[tabla["renta_hogar_mes"].isna(), "alquiler_mes_p50"] = 400.0
    with pytest.raises(ValueError, match="se perderían"):
        pipeline_analisis.analisis_json(tabla, _bono())


def test_pocos_contratos():
    t = pd.DataFrame(
        {
            "zona_id": ["a", "a", "b", "b"],
            "anio": [2015, 2024, 2015, 2024],
            "testigos": [100, 49, 80, np.nan],
        }
    )
    assert figuras._pocos(t, [2015, 2024]).to_dict() == {"a": True, "b": False}
    assert figuras._pocos(t, [2015]).to_dict() == {"a": False, "b": False}


def _simulacion() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "perfil": ["smi_30", "smi_30_habitacion", "pareja_mediana"],
            "municipio_id": ["28001", "28001", "28002"],
            "criterio": "bono_vigente",
            "elegible": [True, True, False],
            "eur_mes": [250.0, 250.0, 0.0],
            "estimado": True,
            "pct_ocupados_elegibles": [100.0, 100.0, 0.0],
        }
    )


def _fin() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "perfil": ["adulto", "joven", "adulto", "joven"],
            "municipio_id": ["28001", "28001", "28002", "28002"],
            "criterio": ["fin_descuento", "fin_descuento", "fin_descuento_rdl", "fin_descuento_rdl"],
            "elegible": True,
            "eur_mes": [32.76, 9.30, 15.26, 9.30],
            "estimado": True,
            "pct_ocupados_elegibles": np.nan,
        }
    )  # fmt: skip


def _calidad() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "municipio_id": ["28001", "28002"],
            "marca_imputada": [True, False],
            "marca_excluida": [False, False],
            "marca_pocos": [False, True],
        }
    )


def _bloque() -> pd.DataFrame:
    horas = _simulacion().assign(criterio="horas_viaje")
    return pipeline_analisis.bloque_simulacion(
        _simulacion(), _simulacion(), horas, _fin(), _calidad()
    )


def test_bloque_simulacion_sin_habitacion_con_banda_y_marcas():
    b = _bloque()
    assert not b["perfil"].str.endswith("_habitacion").any()
    assert set(b["criterio"]) == {
        "bono_vigente", "bono_vigente_bruto", "horas_viaje_sin_imputar", "fin_descuento", "fin_descuento_rdl"
    }  # fmt: skip
    assert set(b[b["criterio"] == "bono_vigente_bruto"]["perfil"]) == {"pareja_mediana"}
    smi = b[(b["perfil"] == "smi_30") & (b["criterio"] == "bono_vigente")].iloc[0]
    assert smi["marca_imputada"] and not smi["marca_pocos"]
    fin = b[b["criterio"].str.startswith("fin_")]
    assert fin[["marca_imputada", "pct_ocupados_elegibles"]].isna().all().all()


def test_analisis_json_publica_simulacion_y_valida():
    obj = pipeline_analisis.analisis_json(_esfuerzo(), _bono(), _bloque())
    api_estatica.validar("analisis.json", obj)
    assert len(obj["simulacion"]) == len(_bloque())
    fila = next(f for f in obj["simulacion"] if f["perfil"] == "adulto")
    assert fila["pct_ocupados_elegibles"] is None and fila["marca_pocos"] is None
    assert "simulacion" not in pipeline_analisis.analisis_json(_esfuerzo(), _bono())


def test_analisis_json_rechaza_perfil_desconocido():
    obj = pipeline_analisis.analisis_json(
        _esfuerzo(), _bono(), _bloque().assign(perfil="solo")
    )
    with pytest.raises(ValueError, match="perfil"):
        api_estatica.validar("analisis.json", obj)


def test_perfiles_publicados_son_los_de_la_simulacion():
    ids = {*simulacion.IDS, *simulacion.EDADES_FIN}
    assert set(api_estatica.PERFILES_SIMULACION) == ids


def test_fin_por_corona_y_falla_si_no_es_constante():
    coronas = pd.Series({"28001": "C2", "28002": "C2"})
    fin = _fin().assign(criterio="fin_descuento", eur_mes=[32.76, 9.30, 32.76, 9.30])
    t = figuras.fin_por_corona(fin, coronas)
    assert t.loc["C2", ("fin_descuento", "adulto")] == 32.76
    with pytest.raises(ValueError, match="corona"):
        figuras.fin_por_corona(fin.assign(eur_mes=[1.0, 2.0, 3.0, 4.0]), coronas)


def test_con_signo():
    assert figuras.con_signo(0.023) == "+2,3"
    assert figuras.con_signo(-0.01) == "−1,0"
    assert figuras.con_signo(0.0) == "0,0"
