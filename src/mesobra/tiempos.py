"""Tabla `tiempos` en transporte público (`modo = tp`) entre las 199 zonas.

El destino de cada par es el centro de población de la zona de trabajo (`lon_centro`, `lat_centro` de `zonas`).
Dentro de una misma zona el tiempo no es cero: es la mediana, sin ponderar, sobre las secciones de la zona, del
tiempo desde el punto de población de la sección (`zonas.puntos_poblacion`, la geometría de `secciones`) hasta el
centro de población, con un suelo de `MIN_INTERNO` minutos.

Dos fuentes, mismo contrato:

- `linea_base`: distancia en línea recta × `FACTOR_RODEO` ÷ `VELOCIDAD_KMH`. No necesita Java; sale con `estimado = verdadero`.
- `matriz_r5py`: tiempo puerta a puerta con r5py (a pie + transporte público), mediana de las salidas entre las
  7:30 y las 8:30 de `FECHA_SALIDA`, con `estimado = falso`. r5py se importa dentro de la función para que el
  módulo y sus tests funcionen sin Java.
- `matriz_con_estimadas`: `matriz_r5py` dos veces, sin y con las líneas que el CRTM publica sin viajes o solo con
  cabecera y final, reconstruidas por `lineas_estimadas` (#173). Los pares que mejoran en más de
  `TOLERANCIA_MIN` toman el tiempo con ellas y salen con `estimado = verdadero`; los demás, el tiempo sin ellas.

Por encima de `MAX_MINUTOS` el tiempo es nulo (sin ruta).
"""

import datetime as dt
import hashlib
import io
import logging
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import contratos, lineas_estimadas
from mesobra.zonas import (
    PROCESSED,
    RAW,
    leer_edificios,
    leer_secciones,
    poblacion_secciones,
    puntos_poblacion,
    secciones_por_zona,
)

LOG = logging.getLogger(__name__)

MAX_MINUTOS = 120
# supuesto: la línea recta se alarga un 30 % por trazado de calles y vías
FACTOR_RODEO = 1.3
# supuesto: velocidad media puerta a puerta en transporte público, incluidas esperas y transbordos. Contraste con
# r5py (2026-11-17): Getafe → Madrid Centro 37 frente a 40 min y Móstoles → Centro 55 frente a 54, pero
# Alcalá → Centro 92 frente a 43, porque el tren rápido no se ve; en los 6.679 pares con ruta en ambas, la línea
# base es un 20 % más rápida en mediana y se desvía 18,5 min en mediana
VELOCIDAD_KMH = 25.0
# supuesto: ningún trayecto, ni dentro de la zona, baja de 1 minuto (la zona de una sola sección daría 0)
MIN_INTERNO = 1.0
# supuesto: un martes dentro de la vigencia de los GTFS (Cercanías acaba el 2026-11-28)
FECHA_SALIDA = dt.date(2026, 11, 17)
HORA_SALIDA = dt.time(7, 30)
VENTANA = dt.timedelta(hours=1)
# supuesto: las líneas reconstruidas mejoran un par si lo bajan más de 5 min. Es el ruido de r5py medido el 16-11
# con dos pasadas idénticas sin ellas: diferencia mediana 0 min, p99 2, p99,9 4 y máximo 7 (de 10.780 pares), y
# 83 pares que pasan de tener a no tener ruta cerca del límite de MAX_MINUTOS
TOLERANCIA_MIN = 5.0
FIN_CALENDARIO = "20271231"

OSM = RAW / "osm_madrid_2026-11-15.pbf"
REDES = ("metro", "metro_ligero", "cercanias", "interurbanos", "emt", "urbanos")
GTFS = [RAW / f"crtm_gtfs_{red}_2026-11-15.zip" for red in REDES]
GTFS_PREPARADOS = PROCESSED / "gtfs"


def _validada(tabla: pd.DataFrame) -> pd.DataFrame:
    """Columnas del contrato `tiempos`, con sus tipos, validadas."""
    tabla = tabla.assign(modo="tp", km=np.nan)[
        list(contratos.CONTRATOS["tiempos"]["columnas"])
    ]
    tabla = tabla.astype(contratos.dtypes("tiempos"))
    contratos.validar(tabla, "tiempos")
    return tabla


def _centros(zonas: pd.DataFrame) -> pd.DataFrame:
    """Centro de población de cada zona en metros (EPSG:25830): columnas `x` e `y`, índice `zona_id`."""
    zonas = zonas.set_index("zona_id")
    centros = gpd.GeoSeries.from_xy(
        zonas["lon_centro"], zonas["lat_centro"], crs=4326, index=zonas.index
    )
    centros = centros.to_crs(25830)
    return pd.DataFrame({"x": centros.x, "y": centros.y})


def _en_metros(secciones: gpd.GeoDataFrame) -> None:
    """Los centroides y las distancias solo valen en EPSG:25830."""
    if secciones.crs is None or secciones.crs.to_epsg() != 25830:
        raise ValueError(f"Se esperaban secciones en EPSG:25830 y hay {secciones.crs}")


def _minutos(km: np.ndarray | pd.Series) -> np.ndarray | pd.Series:
    return km * FACTOR_RODEO / VELOCIDAD_KMH * 60


def _tabla(matriz: pd.DataFrame, interno: pd.Series) -> pd.DataFrame:
    """199 × 199 pares con la diagonal en `interno` (suelo `MIN_INTERNO`) y nulo por encima de `MAX_MINUTOS`.

    `matriz` trae `from_id`, `to_id` y `minutos`; los pares que falten quedan nulos.
    """
    ids = interno.index
    if interno.isna().any():
        raise ValueError(
            f"Zonas sin tiempo interno (sin secciones o sin ruta): {ids[interno.isna()].tolist()}"
        )
    pares = pd.MultiIndex.from_product([ids, ids], names=["zona_id", "destino_id"])
    tabla = (
        matriz.set_index(["from_id", "to_id"])["minutos"]
        .reindex(pares)
        .rename("minutos")
        .reset_index()
    )
    propia = tabla["zona_id"] == tabla["destino_id"]
    tabla.loc[propia, "minutos"] = (
        tabla.loc[propia, "zona_id"].map(interno.clip(lower=MIN_INTERNO)).to_numpy()
    )
    tabla["minutos"] = tabla["minutos"].where(tabla["minutos"] <= MAX_MINUTOS)
    return tabla


def _interno_mediana(
    matriz: pd.DataFrame, secciones: pd.DataFrame, ids: pd.Index
) -> pd.Series:
    """Mediana por zona del tiempo de sus secciones (`from_id` = CUSEC) a su propio centro (`to_id` = zona_id)."""
    m = matriz.merge(
        secciones[["CUSEC", "zona_id"]],
        left_on="from_id",
        right_on="CUSEC",
        validate="many_to_one",
    )
    propios = m[m["to_id"] == m["zona_id"]]
    if (sin_ruta := propios.loc[propios["minutos"].isna(), "zona_id"]).size:
        LOG.warning(
            "Secciones sin ruta a su centro, fuera de la mediana: %s",
            sin_ruta.value_counts().to_dict(),
        )
    return propios.groupby("zona_id")["minutos"].median().reindex(ids)


def linea_base(zonas: pd.DataFrame, secciones: gpd.GeoDataFrame) -> pd.DataFrame:
    """Tabla `tiempos` por distancia (plan B3): sin Java y siempre completa, con `estimado = verdadero`.

    `secciones` trae `zona_id` y como geometría su punto de población en EPSG:25830 (ver `main`).
    """
    _en_metros(secciones)
    centros = _centros(zonas)
    xy = centros.to_numpy()
    km = (
        np.hypot(xy[:, 0, None] - xy[None, :, 0], xy[:, 1, None] - xy[None, :, 1])
        / 1000
    )
    ids = centros.index
    matriz = pd.DataFrame(
        {
            "from_id": np.repeat(ids, len(ids)),
            "to_id": np.tile(ids, len(ids)),
            "minutos": _minutos(km).ravel(),
        }
    )
    c = secciones.centroid
    centro = centros.reindex(secciones["zona_id"])
    km_sec = pd.Series(
        np.hypot(
            c.x.to_numpy() - centro["x"].to_numpy(),
            c.y.to_numpy() - centro["y"].to_numpy(),
        )
        / 1000,
        index=secciones["zona_id"].to_numpy(),
    )
    interno = _minutos(km_sec.groupby(level=0).median()).reindex(ids)
    return _validada(_tabla(matriz, interno).assign(estimado=True))


def preparar_gtfs(
    origenes: list[Path],
    destino: Path = GTFS_PREPARADOS,
    completar: dict[str, list[str]] | None = None,
) -> list[Path]:
    """Reempaqueta los GTFS del CRTM para que r5py los acepte y devuelve las rutas de los nuevos.

    Con `completar` (`route_id` → paradas en orden, de `lineas_estimadas.construir`), los viajes de esas rutas llevan
    además las paradas intermedias (`lineas_estimadas.completar_tablas`).

    Quita las tablas vacías y `feed_info.txt` (r5py los rechaza), saca los ficheros de subcarpetas y, si el
    calendario ya ha caducado en `FECHA_SALIDA` (Metro, hasta 2026-05-27), lo prolonga hasta `FIN_CALENDARIO`:
    es un supuesto y se avisa en el log. El nombre lleva la huella del contenido porque r5py cachea por nombre.
    """
    destino.mkdir(parents=True, exist_ok=True)
    fecha = FECHA_SALIDA.strftime("%Y%m%d")
    preparados = []
    for origen in origenes:
        with zipfile.ZipFile(origen) as z:
            tablas = {
                Path(n).name: z.read(n) for n in z.namelist() if not n.endswith("/")
            }
        tablas = {
            n: d
            for n, d in tablas.items()
            if n != "feed_info.txt" and d.strip().count(b"\n") > 0
        }
        if completar:
            tablas = lineas_estimadas.completar_tablas(tablas, completar)
        cal = pd.read_csv(
            io.BytesIO(tablas["calendar.txt"]), dtype=str, encoding="utf-8-sig"
        )
        if cal["end_date"].max() < fecha:
            LOG.warning(
                "%s: calendario caducado (%s); prolongado hasta %s",
                origen.name,
                cal["end_date"].max(),
                FIN_CALENDARIO,
            )
            # shortcut: prolonga todos los servicios a la vez (Metro: 4 con el mismo periodo); con servicios de
            # temporada quedarían activos juntos, revisarlo si se prolonga otra red
            cal["end_date"] = FIN_CALENDARIO
            cal["start_date"] = cal["start_date"].where(
                cal["start_date"] < fecha, fecha
            )
            tablas["calendar.txt"] = cal.to_csv(index=False).encode()
        huella = hashlib.sha256(
            b"".join(tablas[n] for n in sorted(tablas))
        ).hexdigest()[:8]
        ruta = destino / f"{origen.stem}_{huella}.zip"
        if not ruta.exists():
            with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
                for nombre, datos in tablas.items():
                    z.writestr(nombre, datos)
        preparados.append(ruta)
    return preparados


def _puntos(ids: pd.Series, lon: pd.Series, lat: pd.Series) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"id": ids.to_numpy()}, geometry=gpd.points_from_xy(lon, lat), crs=4326
    )


def matriz_r5py(
    zonas: pd.DataFrame, secciones: gpd.GeoDataFrame, osm: Path, gtfs: list[Path]
) -> pd.DataFrame:
    """Tabla `tiempos` con r5py: mediana puerta a puerta de las salidas de 7:30 a 8:30 de `FECHA_SALIDA`.

    El destino es el centro de población de la zona de trabajo. `gtfs` son los zips de `preparar_gtfs`.
    """
    from r5py import TransportMode, TransportNetwork, TravelTimeMatrix

    _en_metros(secciones)
    centros = _puntos(zonas["zona_id"], zonas["lon_centro"], zonas["lat_centro"])
    puntos_seccion = secciones.centroid.to_crs(4326)
    sec = _puntos(secciones["CUSEC"], puntos_seccion.x, puntos_seccion.y)
    # supuesto: el tiempo interno se mide del centro a cada sección y no al revés; con las 4.518 secciones
    # como origen r5py tarda horas (~3,5 s por origen) y dentro de una zona domina el trayecto a pie
    m = TravelTimeMatrix(
        TransportNetwork(osm, [str(g) for g in gtfs]),
        origins=centros,
        destinations=pd.concat([centros, sec], ignore_index=True),
        departure=dt.datetime.combine(FECHA_SALIDA, HORA_SALIDA),
        departure_time_window=VENTANA,
        percentiles=[50],
        transport_modes=[TransportMode.TRANSIT, TransportMode.WALK],
        max_time=dt.timedelta(minutes=MAX_MINUTOS),
    )
    columna = m.columns.difference(["from_id", "to_id"])
    if len(columna) != 1:
        raise ValueError(f"r5py devolvió columnas inesperadas: {m.columns.tolist()}")
    m = m.rename(columns={columna[0]: "minutos"}).astype({"minutos": "float64"})
    a_seccion = m["to_id"].isin(sec["id"])
    interno = _interno_mediana(
        m[a_seccion].rename(columns={"from_id": "to_id", "to_id": "from_id"}),
        secciones,
        pd.Index(zonas["zona_id"]),
    )
    return _validada(_tabla(m[~a_seccion], interno).assign(estimado=False))


def marcar_estimados(con: pd.DataFrame, sin: pd.DataFrame) -> pd.DataFrame:
    """`con` donde las líneas reconstruidas mejoran el par, con `estimado = verdadero`; `sin` en los demás.

    Mejora es bajar más de `TOLERANCIA_MIN` o pasar a tener ruta con margen de `TOLERANCIA_MIN` hasta
    `MAX_MINUTOS`. Por debajo es ruido de r5py, y añadir servicio no puede alargar un viaje: si `con` sale peor (o
    pierde la ruta), vale `sin`. No se toma el mínimo de los dos para no sesgar el tiempo a la baja.
    """
    clave = list(contratos.CONTRATOS["tiempos"]["clave"])
    antes = (
        con[clave]
        .merge(sin, on=clave, how="left", validate="one_to_one")["minutos"]
        .to_numpy()
    )
    despues = con["minutos"].to_numpy()
    mejora = (despues < antes - TOLERANCIA_MIN) | (
        np.isnan(antes) & (despues <= MAX_MINUTOS - TOLERANCIA_MIN)
    )
    minutos = np.where(mejora, despues, antes)
    return _validada(
        con.assign(minutos=minutos, estimado=con["estimado"].to_numpy() | mejora)
    )


def matriz_con_estimadas(
    zonas: pd.DataFrame, secciones: gpd.GeoDataFrame
) -> pd.DataFrame:
    """`matriz_r5py` con las líneas reconstruidas de #173, con `estimado` en los pares que mejoran por ellas.

    La matriz sin ellas queda en `data/processed/tiempos_sin_estimadas.parquet` como evidencia del marcado.
    """
    sin = matriz_r5py(zonas, secciones, OSM, preparar_gtfs(GTFS))
    sin.to_parquet(PROCESSED / "tiempos_sin_estimadas.parquet")
    secuencias, propio = lineas_estimadas.construir(OSM, GTFS_PREPARADOS, FECHA_SALIDA)
    gtfs = [*preparar_gtfs(GTFS, completar=secuencias), propio]
    con = marcar_estimados(matriz_r5py(zonas, secciones, OSM, gtfs), sin)
    LOG.info(
        "Líneas reconstruidas: %d pares cambian; pares con ruta %d → %d",
        con["estimado"].sum(),
        sin["minutos"].notna().sum(),
        con["minutos"].notna().sum(),
    )
    return con


def main(modo: str = "r5py") -> None:
    """Escribe `data/processed/tiempos.parquet`; `modo` es `r5py` o `base` (línea base por distancia)."""
    zonas = gpd.read_parquet(PROCESSED / "zonas.parquet")
    secciones = secciones_por_zona(leer_secciones(), poblacion_secciones())
    # el tiempo interno se mide desde donde vive la gente, no desde el centroide del polígono (#175)
    secciones = secciones.assign(geometry=puntos_poblacion(secciones, leer_edificios()))
    if modo == "base":
        tabla = linea_base(zonas, secciones)
    elif modo == "r5py":
        tabla = matriz_con_estimadas(zonas, secciones)
    else:
        raise ValueError(f"modo desconocido: {modo!r} (r5py o base)")
    sin_ruta = (
        tabla.groupby("zona_id")["minutos"].count().le(1)
    )  # solo su propia diagonal
    LOG.info(
        "%.1f %% de pares nulos; zonas sin ruta a ninguna otra: %s",
        100 * tabla["minutos"].isna().mean(),
        sin_ruta.index[sin_ruta].tolist(),
    )
    tabla.to_parquet(PROCESSED / "tiempos.parquet")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1] if len(sys.argv) > 1 else "r5py")
