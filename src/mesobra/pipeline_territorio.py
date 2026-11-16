"""Escribe `app/datos/zonas.geojson` y `app/datos/tiempos.json` desde las tablas `zonas` y `tiempos`.

Ejecutar con `python -m mesobra.pipeline_territorio`. Supuesto: lee las tablas que dejan `python -m mesobra.zonas` y
`python -m mesobra.tiempos` en `data/processed/`, sin relanzar r5py (unos 30 min) en cada ejecución.
"""

import datetime as dt
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from mesobra import api_estatica
from mesobra.pipeline_euros import APP_DATOS
from mesobra.tiempos import (
    FACTOR_RODEO,
    FECHA_SALIDA,
    HORA_SALIDA,
    MAX_MINUTOS,
    MIN_INTERNO,
    VELOCIDAD_KMH,
    VENTANA,
)
from mesobra.zonas import PROCESSED

# supuesto: la menor tolerancia que deja zonas.geojson por debajo de 1 MB (752 KB; 10 m dan 1.045 KB). Es de área
# (Visvalingam-Whyatt), no de distancia: los bordes se mueven 10 m en mediana, 20 m en el p95 y 48 m como máximo
# (Talamanca de Jarama), invisible hasta zoom 13 y visible a nivel de calle
# shortcut: GEOS espera una cobertura válida y el seccionado no lo es del todo (624 m de aristas sin casar en 6
# zonas); hoy no abre huecos (lo mide test_ficheros_reales), revisar si cambia el seccionado
TOLERANCIA_M = 20
PRECISION_GRADOS = 1e-5  # unos 1,1 m de latitud; vértices compartidos redondean igual y no abren huecos
PROPIEDADES = ["zona_id", "nombre", "tipo", "municipio_id", "corona", "poblacion"]
INE = "CC BY 4.0, citando «Elaboración propia con datos extraídos del sitio web del INE: www.ine.es»"
CRTM = "Licencia de datos abiertos del CRTM (https://www.crtm.es/licencia-de-uso/)"
OSM = {
    "nombre": "OpenStreetMap, extracto de Geofabrik de la Comunidad de Madrid del 2026-11-13. © OpenStreetMap contributors",
    "url": "https://download.geofabrik.de/europe/spain/madrid-261113.osm.pbf",
    "licencia": "ODbL 1.0 (https://www.openstreetmap.org/copyright)",
}
ARCGIS = "https://www.arcgis.com/sharing/rest/content/items/{}/data"
# red: (item de ArcGIS, vigencia de su calendar.txt según data/README.md); la licencia del CRTM pide la fecha del GTFS
GTFS = {
    "Metro": ("5c7f2951962540d69ffe8f640d94c246", "2025-05-27 a 2026-05-27"),
    "Metro Ligero": ("aaed26cc0ff64b0c947ac0bc3e033196", "2026-10-28 a 2027-10-28"),
    "Cercanías": ("1a25440bf66f499bae2657ec7fb40144", "2026-10-30 a 2026-11-28"),
    "Autobuses Interurbanos": (
        "885399f83408473c8d815e40c5e702b7",
        "2026-10-27 a 2027-11-28",
    ),
    "EMT de Madrid": ("868df0e58fca47e79b942902dffd7da0", "2026-10-30 a 2026-12-31"),
    "Autobuses Urbanos del resto de municipios": (
        "357e63c2904f43aeb5d8a267a64346d8",
        "2026-10-27 a 2027-11-28",
    ),
}
FUENTES_ZONAS = [
    {
        "nombre": "INE, secciones censales a 1-1-2025",
        "url": "https://www.ine.es/prodyser/cartografia/seccionado_2025.zip",
        "licencia": INE,
    },
    {
        "nombre": "INE, Atlas de Distribución de Renta de los Hogares, tabla 31105 (población 2024)",
        "url": "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/31105.csv",
        "licencia": INE,
    },
    {
        "nombre": "Coronas tarifarias vigentes, Consorcio Regional de Transportes de Madrid. Powered by CRTM",
        "url": "https://datos.crtm.es/api/download/v1/items/076c812cd20341ecb9a1b37321ed2c90/geojson?layers=0",
        "licencia": CRTM,
    },
    OSM,
]
FUENTES_TIEMPOS = [
    {
        "nombre": f"GTFS de {red}, Consorcio Regional de Transportes de Madrid (calendario del {vigencia}, "
        "descargado el 2026-11-15). Powered by CRTM",
        "url": ARCGIS.format(item),
        "licencia": CRTM,
    }
    for red, (item, vigencia) in GTFS.items()
] + [OSM]


def _meta(anio_dato: int, fuentes: list[dict[str, str]], nota: str) -> dict:
    return {
        "generado": dt.date.today().isoformat(),
        "anio_dato": anio_dato,
        "fuentes": fuentes,
        "nota": nota,
    }


def simplificar(geometria: gpd.GeoSeries) -> gpd.GeoSeries:
    """Simplifica en EPSG:25830 como cobertura (sin huecos ni solapes entre vecinas) y pasa a EPSG:4326 (RFC 7946)."""
    if geometria.crs is None or geometria.crs.to_epsg() != 25830:
        raise ValueError(
            f"Se esperaba EPSG:25830 para medir la tolerancia y hay {geometria.crs}"
        )
    lonlat = geometria.simplify_coverage(TOLERANCIA_M).to_crs(4326)
    redondeada = shapely.set_precision(lonlat.values, PRECISION_GRADOS)
    return gpd.GeoSeries(
        shapely.orient_polygons(redondeada), index=geometria.index, crs=4326
    )


def zonas_geojson(zonas: gpd.GeoDataFrame) -> dict:
    capa = zonas[PROPIEDADES].assign(geometry=simplificar(zonas.geometry))
    geo = json.loads(gpd.GeoDataFrame(capa, crs=4326).to_json(drop_id=True))
    tipos = zonas["tipo"].value_counts()
    nota = (
        f"{tipos['municipio']} municipios y los {tipos['distrito']} distritos de Madrid, disolviendo las secciones censales del INE a 1-1-2025. "
        "poblacion: habitantes de 2024 (ADRH). corona: la del CRTM en la que cae el centro de población de la zona, "
        "media de los edificios de vivienda de OpenStreetMap (© OpenStreetMap contributors, ODbL). Polígonos "
        f"simplificados con {TOLERANCIA_M} m de tolerancia (EPSG:25830) sin huecos entre zonas vecinas. Powered by CRTM."
    )
    return {
        "type": "FeatureCollection",
        "meta": _meta(2024, FUENTES_ZONAS, nota),
        "features": geo["features"],
    }


def _nota_tiempos(tiempos: pd.DataFrame) -> str:
    estimados = tiempos["estimado"]
    if estimados.all():
        rodeo = f"{FACTOR_RODEO}".replace(".", ",")
        origen = (
            f"Plan B: línea base por distancia (línea recta × {rodeo} a {VELOCIDAD_KMH:.0f} km/h); "
            "todos los tiempos son estimados."
        )
    else:
        # cifras en formato español: 1.076 pares (2,7 %)
        n = f"{estimados.sum():,}".replace(",", ".")
        pct = f"{100 * estimados.mean():.1f}".replace(".", ",")
        fin = (dt.datetime.combine(FECHA_SALIDA, HORA_SALIDA) + VENTANA).time()
        origen = (
            "Calculado con r5py (a pie + transporte público), mediana de las salidas entre las "
            f"{HORA_SALIDA.hour}:{HORA_SALIDA.minute:02d} y las {fin.hour}:{fin.minute:02d} del martes "
            f"{FECHA_SALIDA}. Estimado: {n} pares ({pct} %) mejoran con líneas que el CRTM publica sin viajes, "
            "reconstruidas con el trazado de OpenStreetMap (#173); el fichero no dice cuáles. Supuesto (estimado): "
            "el calendario del GTFS de Metro, caducado el 2026-05-27, se prolonga hasta el 2027-12-31."
        )
    return (
        "Minutos puerta a puerta en transporte público del centro de población de la zona de origen al de la de "
        f"destino; dentro de la zona, mediana desde sus secciones, con un mínimo de {MIN_INTERNO:.0f} min. null: "
        f"más de {MAX_MINUTOS} min o sin ruta. {origen} Datos de OpenStreetMap (© OpenStreetMap contributors, "
        "ODbL). Powered by CRTM."
    )


def tiempos_json(tiempos: pd.DataFrame, zonas: pd.DataFrame) -> dict:
    ids = zonas["zona_id"]
    tiempos = tiempos[tiempos["modo"] == "tp"]
    # un par que falte saldría null («sin ruta») sin avisar; los duplicados ya los rechaza pivot
    if len(tiempos) != len(ids) ** 2:
        raise ValueError(f"Faltan pares en tiempos: {len(tiempos)} de {len(ids) ** 2}")
    matriz = tiempos.pivot(index="zona_id", columns="destino_id", values="minutos")
    if set(matriz.index) != set(ids) or set(matriz.columns) != set(ids):
        raise ValueError(
            "La tabla tiempos no tiene los mismos ids de origen y destino que zonas"
        )
    # floor(x + 0,5) y no round: el redondeo bancario de numpy llevaría 2,5 a 2
    minutos = np.floor(matriz.loc[ids, ids].to_numpy() + 0.5)
    # 120,5 redondea a 121: pasa del máximo y va como null
    minutos[minutos > MAX_MINUTOS] = np.nan
    tp = [[None if np.isnan(m) else int(m) for m in fila] for fila in minutos]
    return {
        "meta": _meta(2026, FUENTES_TIEMPOS, _nota_tiempos(tiempos)),
        "origenes": ids.tolist(),
        "destinos": [
            {"destino_id": z, "nombre": n, "tipo": "zona"}
            for z, n in zip(ids, zonas["nombre"], strict=True)
        ],
        "tp": tp,
    }


def main() -> None:
    faltan = [
        f for f in ("zonas", "tiempos") if not (PROCESSED / f"{f}.parquet").exists()
    ]
    if faltan:
        raise FileNotFoundError(
            f"Faltan {faltan} en {PROCESSED}: ejecuta python -m mesobra.zonas y python -m mesobra.tiempos"
        )
    zonas = gpd.read_parquet(PROCESSED / "zonas.parquet").sort_values("zona_id")
    tiempos = pd.read_parquet(PROCESSED / "tiempos.parquet")
    # primero las zonas: escribir comprueba los ids de tiempos.json contra el zonas.geojson de la carpeta
    api_estatica.escribir("zonas.geojson", zonas_geojson(zonas), APP_DATOS)
    api_estatica.escribir("tiempos.json", tiempos_json(tiempos, zonas), APP_DATOS)


if __name__ == "__main__":
    main()
