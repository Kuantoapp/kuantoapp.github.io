"""Polos de empleo con nombre: destinos `polo:<slug>` de la matriz `tiempos` (F3-01, #95).

Supuesto declarado: la lista de `datos/polos.csv` no sale de datos de movilidad, la eligió el equipo. Incluye los
lugares de trabajo de los personajes de la ficha §3 (Hospital La Paz, Hospital 12 de Octubre, un polígono del sur) y
grandes centros de empleo de la región, cada uno con su motivo. Los polos obtenidos de la EDM2018 y del MITMA quedan
para N2. La nota metodológica lo dirá.

Cada polo es un punto (EPSG:4326) del polígono de OpenStreetMap que dice `osm_id`: su centroide o, si el centroide no engancha a la red (IFEMA, Distrito Telefónica, Ciudad Financiera), el punto del borde más cercano a una parada
(© OpenStreetMap contributors, ODbL, extracto de Geofabrik del 2026-11-13).

`ubicar` asigna cada polo a la zona en la que cae. Su corona tarifaria es la de esa zona (`calculo._corona`), la del
centro de población de la zona y no la del punto: el CRTM traza las coronas por municipio y Madrid capital es
toda corona A, pero una zona grande puede tener un punto en una corona distinta a la de su centro (lo comprueba
`coronas_distintas` en la generación y `tests/test_polos.py`).
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

POLOS = Path(__file__).parent / "datos" / "polos.csv"
COLUMNAS = ["slug", "nombre", "tipo", "lon", "lat", "osm_id", "motivo"]
SLUG = r"[a-z0-9_-]+"  # el mismo patrón que `polo:<slug>` en api_estatica
OSM_ID = r"(?:way|relation)/[0-9]+"


def leer(ruta: Path = POLOS) -> pd.DataFrame:
    """Polos validados, con `destino_id = polo:<slug>` y `lon`, `lat` numéricas."""
    polos = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    if polos.columns.tolist() != COLUMNAS:
        raise ValueError(
            f"{ruta.name}: columnas {polos.columns.tolist()}, se esperaban {COLUMNAS}"
        )
    if polos.empty or polos.isna().any(axis=None):
        raise ValueError(f"{ruta.name}: vacío o con celdas sin valor")
    for columna, patron in (("slug", SLUG), ("osm_id", OSM_ID)):
        if (mal := polos.loc[~polos[columna].str.fullmatch(patron), columna]).size:
            raise ValueError(f"{ruta.name}: {columna} no válido {mal.tolist()}")
    if (repetidos := polos.loc[polos["slug"].duplicated(), "slug"]).size:
        raise ValueError(f"{ruta.name}: slug repetido {repetidos.tolist()}")
    polos = polos.astype({"lon": float, "lat": float})
    return polos.assign(destino_id="polo:" + polos["slug"])


def ubicar(polos: pd.DataFrame, zonas: gpd.GeoDataFrame) -> pd.DataFrame:
    """`polos` con la `zona_id` de la zona en la que cae cada uno; `zonas` en cualquier CRS definido.

    Falla si un polo cae fuera de las zonas (fuera de la Comunidad) o en el borde de dos.
    """
    puntos = gpd.GeoDataFrame(
        {"destino_id": polos["destino_id"]},
        geometry=gpd.points_from_xy(polos["lon"], polos["lat"], crs=4326),
        index=polos.index,
    ).to_crs(zonas.crs)
    union = gpd.sjoin(
        puntos, zonas[["zona_id", "geometry"]], how="left", predicate="intersects"
    )
    if (fuera := union.loc[union["zona_id"].isna(), "destino_id"]).size:
        raise ValueError(f"Polos fuera de las zonas de la Comunidad: {fuera.tolist()}")
    if (dobles := union.loc[union.index.duplicated(), "destino_id"]).size:
        raise ValueError(f"Polos en el borde de dos zonas: {dobles.tolist()}")
    return polos.assign(zona_id=union["zona_id"])


def coronas_distintas(
    polos: pd.DataFrame, zonas: gpd.GeoDataFrame, coronas: gpd.GeoDataFrame
) -> list[str]:
    """`destino_id` de los polos cuyo punto no cae en la corona CRTM de su zona (`corona` de `zonas`).

    `polos` ya trae `zona_id` (`ubicar`); `coronas`, `corona` y polígono. Un polo fuera de toda corona o
    en el borde de dos (una de sus filas no coincide) cuenta como distinto: la zona no puede decir cuál es la suya.
    """
    puntos = gpd.GeoDataFrame(
        {"destino_id": polos["destino_id"]},
        geometry=gpd.points_from_xy(polos["lon"], polos["lat"], crs=4326),
        index=polos.index,
    ).to_crs(coronas.crs)
    union = gpd.sjoin(puntos, coronas[["corona", "geometry"]], how="left")
    de_la_zona = polos["zona_id"].map(zonas.set_index("zona_id")["corona"])
    igual = union["corona"].eq(de_la_zona.loc[union.index])
    return sorted(union.loc[~igual, "destino_id"].unique())
