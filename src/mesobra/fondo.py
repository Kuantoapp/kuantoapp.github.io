"""Escribe `app/mapa/fondo.geojson`: el mapa base propio de la herramienta, que funciona sin red (#382).

Provincias de España y países vecinos de Natural Earth 10m (dominio público), recortados a la caja de España y
simplificados. Solo contornos: los nombres de Natural Earth usan exónimos («Lérida», «Gerona») y no se pintan.
Va en `app/mapa/` y no en `app/datos/`: es un fondo de pantalla, no un fichero del contrato de la API.
Ejecutar con `python -m mesobra.fondo`.
"""

import datetime as dt
import json
import logging

import geopandas as gpd
import pandas as pd
import shapely

from mesobra.zonas import RAIZ, RAW

LOG = logging.getLogger(__name__)

PROVINCIAS = RAW / "naturalearth_provincias_2026-11-21.zip"
PAISES = RAW / "naturalearth_paises_2026-11-21.zip"
SALIDA = RAIZ / "app/mapa/fondo.geojson"
VERSION = "5.1.1"  # la de los ficheros VERSION.txt de los dos ZIP
ESPANA = "ESP"
VECINOS = ["PRT", "FRA", "AND", "GIB", "MAR", "DZA"]
CAJA = (
    -19.5,
    26.8,
    5.5,
    44.6,
)  # oeste, sur, este, norte: la de `maxBounds` en app/app.js
# supuesto: con 500 m el fichero queda muy por debajo de 1 MB y el borde no se nota hasta zoom 10, donde ya solo se ve
# la Comunidad de Madrid, que dibuja su propio contorno con las zonas
TOLERANCIA_M = 500
PRECISION_GRADOS = 1e-4  # unos 11 m: de sobra para un fondo simplificado a 500 m
LICENCIA = "Dominio público (https://www.naturalearthdata.com/about/terms-of-use/)"
FUENTES = [
    {
        "nombre": f"Natural Earth 10m, provincias (admin 1), versión {VERSION}",
        "url": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip",
        "licencia": LICENCIA,
    },
    {
        "nombre": f"Natural Earth 10m, países (admin 0), versión {VERSION}",
        "url": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip",
        "licencia": LICENCIA,
    },
]


def _capa(simplificada: gpd.GeoSeries, tipo: str) -> gpd.GeoDataFrame:
    """Geometrías ya simplificadas en EPSG:25830, pasadas a EPSG:4326 y redondeadas, con su `tipo`."""
    lonlat = shapely.set_precision(simplificada.to_crs(4326).values, PRECISION_GRADOS)
    return gpd.GeoDataFrame(geometry=lonlat, crs=4326).assign(tipo=tipo)


def fondo(provincias: gpd.GeoDataFrame, paises: gpd.GeoDataFrame) -> dict:
    """GeoJSON del fondo: las provincias de España (`adm0_a3`) y los países vecinos (`ADM0_A3`) dentro de `CAJA`."""
    for nombre, capa in (("provincias", provincias), ("paises", paises)):
        if capa.crs is None or capa.crs.to_epsg() != 4326:
            raise ValueError(f"Se esperaba EPSG:4326 en {nombre} y hay {capa.crs}")
    espana = provincias[provincias["adm0_a3"] == ESPANA]
    if espana.empty:
        raise ValueError("Ninguna provincia de España en la capa de provincias")
    vecinos = paises[paises["ADM0_A3"].isin(VECINOS)]
    recortados = vecinos.clip_by_rect(*CAJA)
    vecinos = vecinos.assign(geometry=recortados)[~recortados.is_empty]
    # las provincias como cobertura: al simplificar no se abren huecos entre vecinas
    capas = [
        _capa(
            espana.geometry.to_crs(25830).simplify_coverage(TOLERANCIA_M), "provincia"
        ),
        _capa(vecinos.geometry.to_crs(25830).simplify(TOLERANCIA_M), "pais"),
    ]
    geo = json.loads(pd.concat(capas, ignore_index=True).to_json(drop_id=True))
    nota = (
        f"{len(espana)} provincias y ciudades autónomas de España y {len(vecinos)} países vecinos, recortados a la caja "
        f"de España y simplificados con {TOLERANCIA_M} m de tolerancia (EPSG:25830). Solo es el fondo del mapa."
    )
    meta = {"generado": dt.date.today().isoformat(), "fuentes": FUENTES, "nota": nota}
    return {"type": "FeatureCollection", "meta": meta, "features": geo["features"]}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    objeto = fondo(gpd.read_file(PROVINCIAS), gpd.read_file(PAISES))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        json.dumps(objeto, ensure_ascii=False, separators=(",", ":")), "utf-8"
    )
    LOG.info(
        "%s: %d elementos, %d KB",
        SALIDA,
        len(objeto["features"]),
        SALIDA.stat().st_size // 1024,
    )


if __name__ == "__main__":
    main()
