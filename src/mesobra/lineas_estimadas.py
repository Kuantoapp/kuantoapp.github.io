"""Líneas que los GTFS del CRTM publican sin viajes o con solo cabecera y final, reconstruidas como estimadas (#173).

Decisión de Izan del 2026-11-15 (`docs/decisiones.md`). Para cada línea de `RUTAS`:

- **Paradas:** las de su GTFS que no usa ningún viaje («huérfanas») a menos de `BUFFER_M` del trazado de la
  relación de OpenStreetMap (© los colaboradores de OpenStreetMap, ODbL), ordenadas a lo largo de él. Si un extremo
  del trazado no tiene ninguna, se añade la parada más cercana a ese extremo, la use o no algún viaje.
- **Líneas con viajes de solo dos paradas** (336, 339, 415, 1 de Rivas): `completar_viajes` mete las intermedias en
  sus viajes reales, con la hora repartida en proporción a la distancia. Horarios y duración son los del CRTM.
- **Líneas sin viajes:** `construir` escribe un GTFS propio con un viaje por sentido y `frequencies.txt` en
  `FRANJA`. Frecuencia y velocidad salen de `_parecidas` (autobús) o de `HEADWAY_METRO_S` y la mediana de las demás
  líneas de Metro (línea 3).

- **Líneas con horario de relleno** (#311): el CRTM publica unas 30 líneas (495-499 y N808 de Arroyomolinos, 480-493 de
  Leganés y Fuenlabrada, 350-355 de Arganda, nocturnos, urbanos 1A, 1B y 1 de Leganés) con todas las paradas de cada
  viaje a las 01:00:00, y r5py no las ve en la franja de punta. `rellenar_horarios` toma la salida real del
  `trip_id` y reparte la hora por distancia con la velocidad de las líneas parecidas (`parecidas`).

Las distancias son en línea recta entre paradas consecutivas, igual en las líneas de referencia y en las
reconstruidas, para que la velocidad medida y la aplicada sean la misma magnitud (los GTFS no traen
`shape_dist_traveled`).
"""

import datetime as dt
import hashlib
import io
import logging
import re
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import LineString, Point

from mesobra.zonas import RAW

LOG = logging.getLogger(__name__)

# route_id del CRTM → patrón del nombre de la relación de OSM; de las que casan se usa la más larga.
# Quedan fuera: 728, N702, N908 e I1 de Algete (no están en OSM), 414 (ninguna parada huérfana junto al trazado),
# N301 y N302 (nocturnos, fuera de la ventana de 7:30 a 8:30), los SE de la EMT (poco impacto) y el Ramal
# Ópera–Príncipe Pío (solo tiene esas dos estaciones).
RUTAS = {
    "4__3___": r"^Línea 3: ",
    **{f"8__{n}___": rf"^Bus {n}: " for n in range(720, 728)},
    "8__635___": r"^Bus 635: ",
    "8__336___": r"^Bus 336: ",
    "8__339___": r"^Bus 339: ",
    "8__415___": r"^Bus 415: ",
    "9__SE__161_": r"^Bus SE: ",
    "9__3_A_065_": r"Línea 3A: Circular de Getafe",
    "9__1__045_": r"^Línea 1: Las Adelfillas",
    "9__2__045_": r"^Línea 2: Avenida de los Remedios",
    "9__1__123_": r"^Bus L1: Barrio de la Luna",
}
# el primer carácter del route_id dice la red; interurbanos y urbanos comparten `stops.txt`
REDES = {
    "4": RAW / "crtm_gtfs_metro_2026-11-15.zip",
    "8": RAW / "crtm_gtfs_interurbanos_2026-11-15.zip",
    "9": RAW / "crtm_gtfs_urbanos_2026-11-15.zip",
}
# supuesto: los andenes de Metro quedan a menos de 50 m de la vía de OSM y las paradas de autobús a 30 m de la calzada
BUFFER_M = {"4": 50.0, "8": 30.0, "9": 30.0}
# supuesto: dos paradas a menos de 60 m a lo largo del trazado son la misma a cada lado de la calle; queda la primera
SEPARACION_M = 60.0
# supuesto: un extremo del trazado está servido si hay una parada a menos de 300 m (y si los dos extremos distan
# menos que eso, la línea es circular y va en un solo sentido)
ANCLA_M = 300.0
# dato de Izan (2026-11-15): la línea 3 pasa cada 3 min en hora punta
HEADWAY_METRO_S = 180
PUNTA = ("07:30:00", "08:30:00")
# supuesto: la frecuencia de punta solo se aplica de 6:30 a 9:30; cubre la ventana de cálculo y los viajes largos
FRANJA = ("06:30:00", "09:30:00")
# supuesto: «longitud parecida» es entre 1/1,33 y 1,33 veces la de la línea reconstruida
RAZON_KM = 1.33
SERVICIO = "estimado"
# aviso si empalmar las partes sueltas de la relación alarga el trazado más de un 10 %
ALARGAMIENTO = 1.1
# el CRTM publica sin horario real algunas líneas: todas las paradas de cada viaje a esta hora (#311)
RELLENO = ("01:00:00", "01:00:01")
HORA_EN_ID = r"_(\d{2}:\d{2}:\d{2})_"
HORA_CORTA = r"_(\d{1,2})(\d{2})$"
SEMANA = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _leer(zip_path: Path, nombre: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as z:
        ruta = next((n for n in z.namelist() if Path(n).name == nombre), None)
        if ruta is None:
            raise FileNotFoundError(f"{nombre} no está en {zip_path}")
        return pd.read_csv(io.BytesIO(z.read(ruta)), dtype=str, encoding="utf-8-sig")


def _paradas(stops: pd.DataFrame, usadas: set[str]) -> gpd.GeoDataFrame:
    """Paradas físicas (`location_type` 0) en EPSG:25830 con la columna `huerfana`."""
    # sin la columna (GTFS opcional) todas son paradas, por defecto del formato
    tipo = stops.get("location_type", "0")
    stops = stops[pd.Series(tipo, index=stops.index).fillna("0") == "0"]
    return gpd.GeoDataFrame(
        {
            "stop_id": stops["stop_id"].to_numpy(),
            "huerfana": ~stops["stop_id"].isin(usadas).to_numpy(),
        },
        geometry=gpd.points_from_xy(
            stops["stop_lon"].astype(float), stops["stop_lat"].astype(float)
        ),
        crs=4326,
    ).to_crs(25830)


def _xy(paradas: gpd.GeoDataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {"x": paradas.geometry.x.to_numpy(), "y": paradas.geometry.y.to_numpy()},
        index=paradas["stop_id"].to_numpy(),
    )


def _km(ids: list[str], xy: pd.DataFrame) -> np.ndarray:
    """Km acumulados en línea recta a lo largo de `ids` (0 en la primera)."""
    p = xy.loc[ids].to_numpy()
    return np.r_[0.0, np.hypot(*np.diff(p, axis=0).T).cumsum()] / 1000


def encadenar(geom: shapely.Geometry) -> LineString:
    """Una sola línea con el trazado: une las partes contiguas y empalma las sueltas sin fiarse del orden de OSM.

    Empieza por el extremo más aislado (el más lejano de las demás partes, una cabecera) y añade cada vez la parte
    con un extremo más cerca del final actual, girada si hace falta.
    """
    unido = shapely.line_merge(geom)
    partes = [np.asarray(p.coords)[:, :2] for p in getattr(unido, "geoms", [unido])]
    # los andenes entran en la relación como anillos cerrados sueltos; solo una línea circular entera es un anillo
    partes = [p for p in partes if not (p[0] == p[-1]).all()] or partes
    extremos = np.array([[p[0], p[-1]] for p in partes])
    puntas = extremos.reshape(-1, 2)
    d = np.hypot(*(puntas[:, None] - puntas[None]).transpose(2, 0, 1))
    parte = np.repeat(np.arange(len(partes)), 2)
    d[parte[:, None] == parte[None]] = np.inf
    i, giro = divmod(int(d.min(axis=1).argmax()) if len(partes) > 1 else 0, 2)
    tramos = [partes[i][:: 1 - 2 * giro]]
    quedan = set(range(len(partes))) - {i}
    while quedan:
        fin = tramos[-1][-1]
        _, j, k = min(
            (np.hypot(*(extremos[j, k] - fin)), j, k) for j in quedan for k in (0, 1)
        )
        tramos.append(partes[j][:: 1 - 2 * k])
        quedan.remove(j)
    return LineString(np.vstack(tramos))


def secuencia(
    trazado: LineString, paradas: gpd.GeoDataFrame, buffer_m: float
) -> list[str]:
    """Paradas huérfanas junto al trazado, en su orden, con los extremos asegurados (ver el docstring del módulo)."""
    pos = pd.Series(
        shapely.line_locate_point(trazado, paradas.geometry.to_numpy()),
        index=paradas.index,
    )
    cerca = paradas["huerfana"] & (paradas.distance(trazado) <= buffer_m)
    elegidas = pos[cerca].sort_values()
    # shortcut: compara con la candidata anterior, no con la última conservada; con los datos del 15-11 el hueco
    # mínimo es de 64 m y no cambia nada; hacerlo con un bucle si se baja SEPARACION_M o cambian las paradas
    elegidas = elegidas[elegidas.diff().fillna(np.inf) >= SEPARACION_M]
    for donde, punto in (
        (0.0, Point(trazado.coords[0])),
        (trazado.length, Point(trazado.coords[-1])),
    ):
        distancia = paradas.distance(punto)
        if not (elegidas - donde).abs().le(ANCLA_M).any() and (
            distancia.min() <= ANCLA_M
        ):
            elegidas[distancia.idxmin()] = donde
    return paradas.loc[elegidas.sort_values().index, "stop_id"].tolist()


def _activos(zip_path: Path, fecha: dt.date) -> set[str]:
    """Servicios que circulan en `fecha` según `calendar.txt` y `calendar_dates.txt`."""
    dia = fecha.strftime("%Y%m%d")
    cal = _leer(zip_path, "calendar.txt")
    cd = _leer(zip_path, "calendar_dates.txt")
    cd = cd[cd["date"] == dia]
    activos = cal.loc[
        (cal[SEMANA[fecha.weekday()]] == "1")
        & (cal["start_date"] <= dia)
        & (cal["end_date"] >= dia),
        "service_id",
    ]
    altas = cd.loc[cd["exception_type"] == "1", "service_id"]
    bajas = cd.loc[cd["exception_type"] == "2", "service_id"]
    return (set(activos) | set(altas)) - set(bajas)


def referencia(
    trips: pd.DataFrame, stop_times: pd.DataFrame, xy: pd.DataFrame, activos: set[str]
) -> pd.DataFrame:
    """Por `route_id`: mediana de `km` y `kmh` de sus viajes y `salidas` por sentido en `PUNTA` (servicios activos)."""
    st = stop_times.assign(seq=stop_times["stop_sequence"].astype(int)).sort_values(
        ["trip_id", "seq"]
    )
    p = xy.reindex(st["stop_id"]).to_numpy()
    tramo = np.r_[0.0, np.hypot(*np.diff(p, axis=0).T)] / 1000
    st = st.assign(km=np.where(st["trip_id"].ne(st["trip_id"].shift()), 0.0, tramo))
    viajes = st.groupby("trip_id").agg(
        km=("km", "sum"),
        salida=("departure_time", "first"),
        llegada=("arrival_time", "last"),
    )
    horas = (
        pd.to_timedelta(viajes["llegada"]) - pd.to_timedelta(viajes["salida"])
    ).dt.total_seconds() / 3600
    viajes = viajes.assign(kmh=viajes["km"] / horas.where(horas > 0)).join(
        trips.set_index("trip_id")[["route_id", "service_id", "direction_id"]]
    )
    hoy = viajes[viajes["service_id"].isin(activos)]
    en_punta = hoy["salida"].between(*PUNTA, inclusive="left")
    salidas = (
        hoy[en_punta].groupby("route_id").size()
        / hoy.groupby("route_id")["direction_id"].nunique()
    )
    tabla = viajes.groupby("route_id")[["km", "kmh"]].median()
    return tabla.assign(salidas=salidas.reindex(tabla.index).fillna(0.0))


def _corredor(route_id: str) -> str | None:
    """Interurbanos: primera cifra de la línea (el corredor del CRTM). Urbanos: el código del municipio."""
    m = re.match(r"8__(\d)", route_id) or re.match(r"9_.*_(\d{3})_$", route_id)
    return f"{route_id[0]}:{m.group(1)}" if m else None


def parecidas(
    route_id: str, km: float, ref: pd.DataFrame
) -> tuple[float, float, list[str]]:
    """Headway (s) y velocidad (km/h) de las líneas parecidas con salidas en punta, y cuáles son.

    supuesto (#173): parecida es del mismo corredor (`_corredor`) y de longitud entre 1/`RAZON_KM` y `RAZON_KM`
    veces; si no hay ninguna, de la misma red y longitud parecida (una línea rural larga no se parece a las
    suburbanas cortas de su corredor); luego cualquiera del corredor y, por último, de la red. Mediana de cada una.
    """
    # las de RUTAS no sirven de referencia: no tienen viajes o su velocidad sale de la recta entre cabeceras
    ref = ref[(ref["salidas"] > 0) & ~ref.index.isin(list(RUTAS)) & ref["kmh"].notna()]
    red = ref[ref.index.str[0] == route_id[0]]
    mismo = red.index.map(_corredor) == _corredor(route_id)
    largo = red["km"].between(km / RAZON_KM, km * RAZON_KM).to_numpy()
    elegidas = next(
        (t for t in (red[mismo & largo], red[largo], red[mismo], red) if len(t)),
        None,
    )
    if elegidas is None:
        raise ValueError(f"{route_id}: ninguna línea de su red con salidas en punta")
    return (
        3600 / elegidas["salidas"].median(),
        float(elegidas["kmh"].median()),
        elegidas.index.tolist(),
    )


def _hhmmss(segundos: np.ndarray) -> list[str]:
    h, resto = np.divmod(segundos.astype(int), 3600)
    m, s = np.divmod(resto, 60)
    return [f"{a:02d}:{b:02d}:{c:02d}" for a, b, c in zip(h, m, s, strict=True)]


def _tramo(seq: list[str], s0: str, s1: str, xy: pd.DataFrame) -> list[str]:
    """Paradas de `seq` entre la más cercana a `s0` y la más cercana a `s1`, en ese sentido y sin `s0` ni `s1`.

    Un viaje parcial (que empieza o acaba a mitad de línea) solo recibe las paradas de su tramo.
    """
    p = xy.loc[seq].to_numpy()
    i, j = (int(np.hypot(*(p - xy.loc[s].to_numpy()).T).argmin()) for s in (s0, s1))
    tramo = seq[min(i, j) : max(i, j) + 1]
    return [s for s in (tramo[::-1] if i > j else tramo) if s not in (s0, s1)]


def completar_viajes(
    trips: pd.DataFrame,
    stop_times: pd.DataFrame,
    xy: pd.DataFrame,
    secuencias: dict[str, list[str]],
) -> pd.DataFrame:
    """`stop_times` con las paradas de `secuencias` metidas entre la primera y la última de cada viaje de esas rutas.

    La primera y la última parada y sus horas no cambian; las intermedias van en el sentido del viaje y su hora se
    reparte en proporción a la distancia acumulada. Los demás viajes quedan igual.
    """
    viajes = trips.loc[trips["route_id"].isin(secuencias), ["trip_id", "route_id"]]
    st = stop_times[stop_times["trip_id"].isin(viajes["trip_id"])]
    if st.empty:
        return stop_times
    st = st.assign(seq=st["stop_sequence"].astype(int)).sort_values(["trip_id", "seq"])
    extremos = (
        st.groupby("trip_id")
        .agg(
            s0=("stop_id", "first"),
            s1=("stop_id", "last"),
            t0=("departure_time", "first"),
            t1=("arrival_time", "last"),
        )
        .join(viajes.set_index("trip_id"))
    )
    nuevas = []
    for (route_id, s0, s1), grupo in extremos.groupby(["route_id", "s0", "s1"]):
        ids = [s0, *_tramo(secuencias[route_id], s0, s1, xy), s1]
        km = _km(ids, xy)
        frac = km / km[-1] if km[-1] > 0 else np.linspace(0, 1, len(ids))
        t0 = pd.to_timedelta(grupo["t0"]).dt.total_seconds().to_numpy()
        t1 = pd.to_timedelta(grupo["t1"]).dt.total_seconds().to_numpy()
        hora = _hhmmss(
            np.round(t0[:, None] + frac[None, :] * (t1 - t0)[:, None]).ravel()
        )
        nuevas.append(
            pd.DataFrame(
                {
                    "trip_id": np.repeat(grupo.index.to_numpy(), len(ids)),
                    "arrival_time": hora,
                    "departure_time": hora,
                    "stop_id": np.tile(ids, len(grupo)),
                    "stop_sequence": np.tile(np.arange(len(ids)), len(grupo)).astype(
                        str
                    ),
                }
            )
        )
    resto = stop_times[~stop_times["trip_id"].isin(extremos.index)]
    return pd.concat([resto, *nuevas], ignore_index=True)


def rellenar_horarios(
    trips: pd.DataFrame, stop_times: pd.DataFrame, xy: pd.DataFrame
) -> pd.DataFrame:
    """`stop_times` con horas reales en los viajes cuyas paradas están todas a la hora de relleno (`RELLENO`).

    La salida es la hora que lleva el `trip_id` (`..._06:56:00_...`); cada parada va a esa hora más su distancia
    acumulada en línea recta entre la velocidad mediana de las líneas parecidas de su red (`parecidas`, medida en
    viajes con horario real). Un viaje de relleno sin hora en el `trip_id` es un error, no se adivina.
    """
    sin_hora = (
        stop_times["departure_time"].isin(RELLENO).groupby(stop_times["trip_id"]).all()
    )
    relleno = sin_hora.index[sin_hora]
    if relleno.empty:
        return stop_times
    ids = relleno.to_series()
    # 11 viajes (352 y 499) llevan la hora al final sin dos puntos: `..._1515` o `..._620` (6:20)
    corta = ids.str.extract(HORA_CORTA).dropna()
    salida = ids.str.extract(HORA_EN_ID)[0].fillna(
        corta[0].str.zfill(2) + ":" + corta[1] + ":00"
    )
    if salida.isna().any():
        raise ValueError(
            f"Viajes de relleno sin hora en el trip_id: {salida.index[salida.isna()][:5].tolist()}"
        )
    es = stop_times["trip_id"].isin(relleno)
    st = stop_times[es].assign(seq=lambda d: d["stop_sequence"].astype(int))
    st = st.sort_values(["trip_id", "seq"])
    p = xy.reindex(st["stop_id"])
    if p.isna().any(axis=None):
        raise ValueError("Paradas de viajes de relleno sin coordenadas en stops.txt")
    p = p.to_numpy()
    tramo = np.r_[0.0, np.hypot(*np.diff(p, axis=0).T)] / 1000
    km = np.where(st["trip_id"].ne(st["trip_id"].shift()), 0.0, tramo)
    acum = pd.Series(km, index=st.index).groupby(st["trip_id"]).cumsum()
    ruta = trips.set_index("trip_id")["route_id"].reindex(relleno)
    largo = acum.groupby(st["trip_id"]).max().groupby(ruta).median()
    ref = referencia(trips, stop_times[~es], xy, set(trips["service_id"]))
    kmh = pd.Series({r: parecidas(r, km_r, ref)[1] for r, km_r in largo.items()})
    t0 = pd.to_timedelta(salida.reindex(st["trip_id"]).to_numpy()).total_seconds()
    velocidad = kmh.reindex(ruta.reindex(st["trip_id"]).to_numpy()).to_numpy()
    hora = _hhmmss(np.round(t0 + acum.to_numpy() / velocidad * 3600))
    st = st.drop(columns="seq").assign(arrival_time=hora, departure_time=hora)
    return pd.concat([stop_times[~es], st], ignore_index=True)


def completar_tablas(
    tablas: dict[str, bytes], secuencias: dict[str, list[str]]
) -> dict[str, bytes]:
    """Horas de relleno y paradas intermedias sobre las tablas de un GTFS (`tiempos.preparar_gtfs`); si no hay nada, igual."""

    def leer(nombre: str) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(tablas[nombre]), dtype=str, encoding="utf-8-sig")

    trips, stop_times = leer("trips.txt"), leer("stop_times.txt")
    xy = _xy(_paradas(leer("stops.txt"), set()))
    st = rellenar_horarios(trips, stop_times, xy)
    rellenadas = st is not stop_times
    if rellenadas:
        LOG.warning("Horas estimadas en viajes con horario de relleno del CRTM (#311)")
    if trips["route_id"].isin(secuencias).any():
        st = completar_viajes(trips, st, xy, secuencias)
        LOG.warning(
            "Paradas intermedias estimadas en %s",
            sorted(set(trips.loc[trips["route_id"].isin(secuencias), "route_id"])),
        )
    elif not rellenadas:
        return tablas
    return {**tablas, "stop_times.txt": st.to_csv(index=False).encode()}


def _trazados(osm: Path) -> gpd.GeoDataFrame:
    """Relaciones `route=bus|subway` de OSM en EPSG:25830, con `name` y su longitud."""
    g = gpd.read_file(
        osm, layer="multilinestrings", where="other_tags LIKE '%\"route\"=>%'"
    )
    g = g[
        g["other_tags"].str.contains(r'"route"=>"(?:bus|subway)"', regex=True)
        & g["name"].notna()
    ].to_crs(25830)
    return g.assign(largo=g.length)


def _linea(route_id: str, km: np.ndarray, ref: pd.DataFrame) -> tuple[float, float]:
    """Headway (s) y velocidad (km/h) de una línea sin viajes, con el supuesto que toque según su red."""
    if route_id[0] == "4":
        return HEADWAY_METRO_S, float(ref["kmh"].median())
    headway, kmh, refs = parecidas(route_id, km[-1], ref)
    LOG.info("%s: frecuencia y velocidad de %s", route_id, refs)
    return headway, kmh


def _feed_frecuencias(
    route_id: str, ids: list[str], xy: pd.DataFrame, ref: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """Viajes plantilla (uno por sentido, uno solo si es circular) con su `frequencies.txt`."""
    km = _km(ids, xy)
    headway, kmh = _linea(route_id, km, ref)
    circular = np.hypot(*(xy.loc[ids[0]] - xy.loc[ids[-1]])) <= ANCLA_M
    sentidos = [ids] if circular else [ids, ids[::-1]]
    trips, st = [], []
    for d, paradas in enumerate(sentidos):
        trip_id = f"{route_id}_{SERVICIO}_{d}"
        hora = _hhmmss(np.round(_km(paradas, xy) / kmh * 3600))
        trips.append((route_id, SERVICIO, trip_id, str(d)))
        st.append(
            pd.DataFrame(
                {
                    "trip_id": trip_id,
                    "arrival_time": hora,
                    "departure_time": hora,
                    "stop_id": paradas,
                    "stop_sequence": np.arange(len(paradas)).astype(str),
                }
            )
        )
    LOG.info(
        "%s: %d paradas, %.1f km, cada %.0f s a %.1f km/h",
        route_id,
        len(ids),
        km[-1],
        headway,
        kmh,
    )
    return {
        "trips.txt": pd.DataFrame(
            trips, columns=["route_id", "service_id", "trip_id", "direction_id"]
        ),
        "stop_times.txt": pd.concat(st),
        "frequencies.txt": pd.DataFrame(
            {
                "trip_id": [t[2] for t in trips],
                "start_time": FRANJA[0],
                "end_time": FRANJA[1],
                "headway_secs": str(round(headway)),
                "exact_times": "0",
            }
        ),
    }


def _red(
    red: str, osm: gpd.GeoDataFrame, fecha: dt.date
) -> tuple[dict[str, list[str]], list[dict[str, pd.DataFrame]]]:
    """Secuencias de las rutas de `red` y, para las que no tienen viajes, sus tablas GTFS."""
    zip_path = REDES[red]
    stops, trips = _leer(zip_path, "stops.txt"), _leer(zip_path, "trips.txt")
    st = _leer(zip_path, "stop_times.txt")
    # una parada de autobús es huérfana si no la usa ningún viaje de interurbanos ni de urbanos
    otras = [] if red == "4" else [REDES[r] for r in "89" if r != red]
    usadas = set(st["stop_id"]).union(
        *(set(_leer(p, "stop_times.txt")["stop_id"]) for p in otras)
    )
    paradas = _paradas(stops, usadas)
    xy = _xy(paradas)
    ref = referencia(trips, st, xy, _activos(zip_path, fecha))
    routes = _leer(zip_path, "routes.txt").set_index("route_id")
    secuencias, tablas = {}, []
    for route_id, patron in RUTAS.items():
        if route_id[0] != red:
            continue
        casan = osm[osm["name"].str.contains(patron, regex=True)]
        if casan.empty:
            raise ValueError(f"{route_id}: ninguna relación de OSM casa con {patron!r}")
        relacion = casan.loc[casan["largo"].idxmax()]
        trazado = encadenar(relacion["geometry"])
        if trazado.length > ALARGAMIENTO * relacion["largo"]:
            LOG.warning(
                "%s: el trazado encadenado mide %.1f km y la relación de OSM %.1f (saltos entre partes)",
                route_id,
                trazado.length / 1000,
                relacion["largo"] / 1000,
            )
        ids = secuencia(trazado, paradas, BUFFER_M[red])
        if len(ids) < 2:
            raise ValueError(f"{route_id}: {len(ids)} paradas junto al trazado de OSM")
        if len(ids) == 2:
            # sin intermedias no aporta nada a un viaje de dos paradas, y sin viajes sería una lanzadera inventada
            LOG.warning(
                "%s: solo 2 paradas junto al trazado de OSM; no se reconstruye",
                route_id,
            )
            continue
        secuencias[route_id] = ids
        if route_id not in set(trips["route_id"]):
            t = _feed_frecuencias(route_id, ids, xy, ref)
            t["routes.txt"] = (
                routes.loc[[route_id]].reset_index().assign(agency_id=SERVICIO)
            )
            t["stops.txt"] = stops.loc[
                stops["stop_id"].isin(ids),
                ["stop_id", "stop_name", "stop_lat", "stop_lon"],
            ]
            tablas.append(t)
    return secuencias, tablas


def construir(
    osm: Path, destino: Path, fecha: dt.date
) -> tuple[dict[str, list[str]], Path]:
    """Secuencias de paradas de todas las `RUTAS` y el GTFS propio de las que no tienen viajes.

    El GTFS solo circula en `fecha` (la de cálculo) y su nombre lleva la huella del contenido, como los de
    `tiempos.preparar_gtfs`, porque r5py cachea por nombre.
    """
    trazados = _trazados(osm)
    secuencias, partes = {}, []
    for red in REDES:
        s, t = _red(red, trazados, fecha)
        secuencias |= s
        partes += t
    dia = fecha.strftime("%Y%m%d")
    tablas = {
        n: pd.concat([p[n] for p in partes]).drop_duplicates()
        for n in (
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
            "frequencies.txt",
        )
    }
    tablas["agency.txt"] = pd.DataFrame(
        {
            "agency_id": [SERVICIO],
            "agency_name": ["Líneas reconstruidas (estimado, DataMad #173)"],
            "agency_url": ["https://www.crtm.es"],
            "agency_timezone": ["Europe/Madrid"],
        }
    )
    tablas["calendar.txt"] = pd.DataFrame(
        {
            "service_id": [SERVICIO],
            **{d: ["1"] for d in SEMANA},
            "start_date": [dia],
            "end_date": [dia],
        }
    )
    datos = {n: t.to_csv(index=False).encode() for n, t in tablas.items()}
    huella = hashlib.sha256(b"".join(datos[n] for n in sorted(datos))).hexdigest()[:8]
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"lineas_estimadas_{huella}.zip"
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in datos.items():
            z.writestr(nombre, contenido)
    return secuencias, ruta
