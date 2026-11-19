"""`pipeline_territorio`: simplificación sin huecos, matriz de tiempos y los dos ficheros reales de `app/datos/`."""

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import shapely
from shapely.geometry import Polygon, shape

from mesobra import api_estatica
from mesobra.pipeline_territorio import simplificar, tiempos_json

APP_DATOS = Path(__file__).parent.parent / "app" / "datos"
X0, Y0 = 440_000, 4_470_000  # EPSG:25830, en Madrid


def _vecinos() -> gpd.GeoSeries:
    """Dos zonas de forma distinta con una frontera irregular (±15 m cada 10 m).

    Simplificadas una a una con 20 m, se solapan 2.240 m² y dejan 11.276 m² de hueco; como cobertura, 0.
    """
    rng = np.random.default_rng(0)
    frontera = [(X0 + 1000 + rng.uniform(-15, 15), Y0 + 10 * i) for i in range(101)]
    izq = Polygon([(X0, Y0), *frontera, (X0, Y0 + 1000)])
    der = Polygon([(X0 + 2000, Y0 - 300), (X0 + 2000, Y0 + 1000), *frontera[::-1]])
    return gpd.GeoSeries([izq, der], crs=25830)


def _solape_y_union(g: gpd.GeoSeries) -> tuple[float, shapely.Geometry]:
    metros = g.to_crs(25830)
    union = metros.union_all()
    return metros.area.sum() - union.area, union


def test_simplificar_no_abre_huecos_ni_solapes():
    original = _vecinos()
    s = simplificar(original)
    assert s.crs.to_epsg() == 4326
    assert (
        shapely.get_num_coordinates(s.values).sum()
        < shapely.get_num_coordinates(original.values).sum()
    )
    solape, union = _solape_y_union(s)
    assert abs(solape) < 1  # m²
    # sin hueco en la frontera: queda el redondeo a 1e-5° del borde exterior (272 m² en 6 km), no los 11.276 m²
    assert abs(union.area - original.union_all().area) < 1000
    assert union.geom_type == "Polygon" and not list(union.interiors)
    assert all(g.exterior.is_ccw for g in s)


def test_simplificar_exige_metros():
    with pytest.raises(ValueError, match="EPSG:25830"):
        simplificar(_vecinos().to_crs(4326))


def _zonas() -> pd.DataFrame:
    return pd.DataFrame(
        {"zona_id": ["28001", "28002", "2807901"], "nombre": ["A", "B", "Centro"]}
    )


def _tiempos(minutos: list[float]) -> pd.DataFrame:
    pares = pd.MultiIndex.from_product(
        [["2807901", "28002", "28001"]] * 2, names=["zona_id", "destino_id"]
    )
    return pares.to_frame(index=False).assign(
        modo="tp", minutos=minutos, estimado=False
    )


def _polos() -> pd.DataFrame:
    return pd.DataFrame(
        {"destino_id": ["polo:x"], "nombre": ["Polo X"], "zona_id": ["28002"]}
    )


def _tiempos_a_polo(minutos: list[float]) -> pd.DataFrame:
    """Los pares hacia `polo:x` desde las tres zonas."""
    return pd.DataFrame(
        {
            "zona_id": ["2807901", "28002", "28001"],
            "destino_id": "polo:x",
            "modo": "tp",
            "minutos": minutos,
            "estimado": False,
        }
    )


def test_tiempos_json_redondea_y_ordena():
    minutos = [1.0, 2.5, np.nan, 3.49, 4.0, 120.5, 6.0, 7.0, 119.6]
    t = tiempos_json(_tiempos(minutos), _zonas(), _polos().iloc[0:0])
    assert t["origenes"] == ["28001", "28002", "2807901"]
    assert [d["destino_id"] for d in t["destinos"]] == t["origenes"]
    # filas y columnas en el orden de las zonas: 28001 era la tercera de _tiempos; 120,5 → 121 → null
    assert t["tp"] == [[120, 7, 6], [None, 4, 3], [None, 3, 1]]
    assert "r5py" in t["meta"]["nota"] and "7:30 y las 8:30" in t["meta"]["nota"]


def test_tiempos_json_con_polos_es_rectangular_y_valida_el_contrato():
    tabla = pd.concat([_tiempos([1.0] * 9), _tiempos_a_polo([10.4, 125.0, 30.5])])
    t = tiempos_json(tabla, _zonas(), _polos())
    assert [d["destino_id"] for d in t["destinos"]] == [*t["origenes"], "polo:x"]
    assert t["destinos"][-1] == {
        "destino_id": "polo:x",
        "nombre": "Polo X",
        "tipo": "polo",
        "zona_id": "28002",
    }
    # filas en el orden de las zonas (28001, 28002, 2807901): 30,5 → 31; 125 → null; 10,4 → 10
    assert [fila[-1] for fila in t["tp"]] == [31, None, 10]
    assert {len(fila) for fila in t["tp"]} == {4}
    assert "polos de empleo" in t["meta"]["nota"]
    api_estatica.validar("tiempos.json", t)


def test_tiempos_json_falla_si_falta_un_par():
    with pytest.raises(ValueError, match="Faltan pares"):
        tiempos_json(_tiempos([1.0] * 9).iloc[1:], _zonas(), _polos().iloc[0:0])


def test_tiempos_json_falla_si_faltan_los_pares_de_un_polo():
    with pytest.raises(ValueError, match="Faltan pares"):
        tiempos_json(_tiempos([1.0] * 9), _zonas(), _polos())


def test_tiempos_json_plan_b_lo_dice():
    t = tiempos_json(
        _tiempos([1.0] * 9).assign(estimado=True), _zonas(), _polos().iloc[0:0]
    )
    assert "todos los tiempos son estimados" in t["meta"]["nota"]


def test_tiempos_json_falla_si_faltan_zonas():
    zonas = pd.DataFrame(
        {"zona_id": ["28001", "28002", "28003"], "nombre": list("ABC")}
    )
    with pytest.raises(ValueError, match="mismos ids"):
        tiempos_json(_tiempos([1.0] * 9), zonas, _polos().iloc[0:0])


def _real(nombre: str) -> dict:
    ruta = APP_DATOS / nombre
    if not ruta.exists():
        pytest.skip(f"app/datos/{nombre} todavía no existe")
    assert (
        ruta.stat().st_size < 1_000_000
    )  # supuesto de la issue #76, para que la web cargue rápido
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_ficheros_reales():
    zonas, tiempos = _real("zonas.geojson"), _real("tiempos.json")
    ids = [f["properties"]["zona_id"] for f in zonas["features"]]
    assert len(ids) == 199
    assert sum(f["properties"]["tipo"] == "distrito" for f in zonas["features"]) == 21
    assert tiempos["origenes"] == ids
    # destinos = las 199 zonas y, desde F3-01, los polos; la matriz es origen × destino
    destinos = [d["destino_id"] for d in tiempos["destinos"]]
    assert destinos[:199] == ids and all(d.startswith("polo:") for d in destinos[199:])
    assert len(tiempos["tp"]) == 199 and {len(fila) for fila in tiempos["tp"]} == {
        len(destinos)
    }
    geom = gpd.GeoSeries([shape(f["geometry"]) for f in zonas["features"]], crs=4326)
    assert geom.is_valid.all()
    poligonos = [p for g in geom for p in getattr(g, "geoms", [g])]
    # RFC 7946: exteriores en sentido antihorario e interiores en horario
    assert all(p.exterior.is_ccw for p in poligonos)
    assert not any(r.is_ccw for p in poligonos for r in p.interiors)
    solape, union = _solape_y_union(geom)
    assert solape < 1000  # m², redondeo de coordenadas en toda la Comunidad
    # dos partes como en el seccionado: la Comunidad y el enclave de Santa María de la Alameda (13,8 km²)
    assert sorted(round(p.area / 1e6, 1) for p in union.geoms) == [13.8, 8011.0]
    huecos = [Polygon(r).area for p in union.geoms for r in p.interiors]
    # el único hueco visible es el enclave de Torrejón del Rey (Guadalajara, sección 1928001001) entre Fresno
    # de Torote, Ribatejada y Valdeavero, que no es de la Comunidad; el resto son astillas de redondeo de unos m²
    assert [round(h / 1e6, 2) for h in huecos if h > 100] == [1.23]
