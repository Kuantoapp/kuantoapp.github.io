"""Tests de `mesobra.lineas_estimadas` con trazados y GTFS de juguete (sin OSM ni r5py)."""

import datetime as dt
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, MultiLineString

from mesobra import lineas_estimadas as le

X0, Y0 = 440000.0, 4474000.0


def _paradas(filas: list[tuple[str, float, float, bool]]) -> gpd.GeoDataFrame:
    """`(stop_id, x, y, huerfana)` en metros, como `_paradas`."""
    ids, x, y, huerfana = zip(*filas, strict=True)
    return gpd.GeoDataFrame(
        {"stop_id": list(ids), "huerfana": list(huerfana)},
        geometry=gpd.points_from_xy(x, y),
        crs=25830,
    )


def test_encadenar_ordena_partes_sueltas_y_quita_los_anillos():
    # trazado de 0 a 3 km en tres trozos desordenados, el del medio al revés, y un andén como anillo
    trozos = [
        LineString([(X0 + 2000, Y0), (X0 + 3000, Y0)]),
        LineString([(X0 + 1900, Y0), (X0 + 1000, Y0)]),
        LineString([(X0, Y0), (X0 + 900, Y0)]),
        LineString([(X0 + 500, Y0 + 10), (X0 + 600, Y0 + 10), (X0 + 500, Y0 + 10)]),
    ]
    linea = le.encadenar(MultiLineString(trozos))
    xs = np.array(linea.coords)[:, 0]
    assert sorted([xs[0], xs[-1]]) == [X0, X0 + 3000]
    assert (np.diff(xs) > 0).all() or (np.diff(xs) < 0).all()  # sin ida y vuelta


def test_secuencia_huerfanas_en_orden_sin_duplicados_y_con_cabecera():
    trazado = LineString([(X0, Y0), (X0 + 3000, Y0)])
    paradas = _paradas(
        [
            ("c", X0 + 2000, Y0 + 10, True),
            ("a", X0 + 1000, Y0 - 10, True),
            ("a_enfrente", X0 + 1030, Y0 + 10, True),  # a 30 m de «a»: la misma
            ("usada", X0 + 1500, Y0, False),  # la usa otra línea: no es intermedia
            ("lejos", X0 + 2500, Y0 + 200, True),
            ("cabecera", X0 - 100, Y0, False),  # no huérfana, pero sirve el extremo
            ("otra_cabecera", X0 - 280, Y0, False),
        ]
    )
    # el final (3 km) no tiene ninguna parada a menos de 300 m: se queda sin ancla
    assert le.secuencia(trazado, paradas, 30.0) == ["cabecera", "a", "c"]


def test_referencia_km_velocidad_y_salidas_en_punta():
    xy = pd.DataFrame(
        {"x": [X0, X0 + 3000, X0 + 7000], "y": [Y0, Y0, Y0]}, index=["p", "q", "r"]
    )
    trips = pd.DataFrame(
        {
            "trip_id": ["t1", "t2", "t3", "t4"],
            "route_id": "R",
            "service_id": ["L", "L", "L", "D"],
            "direction_id": ["0", "0", "1", "0"],
        }
    )
    salidas = {"t1": "07:40", "t2": "09:00", "t3": "07:50", "t4": "07:45"}
    filas = []
    for trip, h in salidas.items():
        t0 = pd.Timedelta(f"{h}:00")
        for seq, (stop, minutos) in enumerate([("p", 0), ("q", 6), ("r", 14)]):
            hora = le._hhmmss(
                np.array([(t0 + pd.Timedelta(minutes=minutos)).total_seconds()])
            )[0]
            filas.append((trip, hora, hora, stop, str(seq)))
    st = pd.DataFrame(
        filas,
        columns=[
            "trip_id",
            "arrival_time",
            "departure_time",
            "stop_id",
            "stop_sequence",
        ],
    )
    ref = le.referencia(trips, st, xy, {"L"})
    assert ref.loc["R", "km"] == pytest.approx(7.0)
    assert ref.loc["R", "kmh"] == pytest.approx(30.0)  # 7 km en 14 min
    # t1 y t3 salen en punta (t2 tarde, t4 no circula ese día): 2 salidas entre 2 sentidos
    assert ref.loc["R", "salidas"] == pytest.approx(1.0)


def test_parecidas_prefiere_corredor_y_longitud_y_si_no_la_longitud():
    ref = pd.DataFrame(
        {
            "km": [20.0, 22.0, 60.0, 55.0, 30.0],
            "kmh": [30.0, 40.0, 50.0, 60.0, 99.0],
            "salidas": [6.0, 4.0, 1.0, 2.0, 0.0],
        },
        index=["8__712___", "8__713___", "8__191___", "8__545___", "8__715___"],
    )
    headway, kmh, refs = le.parecidas("8__721___", 21.0, ref)
    assert refs == ["8__712___", "8__713___"]  # el 715 no tiene salidas en punta
    assert (headway, kmh) == (720.0, 35.0)
    headway, kmh, refs = le.parecidas("8__725___", 58.0, ref)
    # rural y larga: otras largas de la red, no las suburbanas de su corredor
    assert refs == ["8__191___", "8__545___"]
    assert (headway, kmh) == (2400.0, 55.0)
    with pytest.raises(ValueError, match="ninguna línea"):
        le.parecidas("9__1__045_", 5.0, ref)


def test_completar_viajes_mete_las_intermedias_en_el_sentido_del_viaje():
    xy = pd.DataFrame(
        {"x": [X0, X0 + 1000, X0 + 3000, X0 + 4000], "y": Y0},
        index=["A", "m1", "m2", "B"],
    )
    trips = pd.DataFrame(
        {"trip_id": ["ida", "vuelta", "otra"], "route_id": ["R", "R", "S"]}
    )
    horas = ["08:00:00", "08:40:00", "09:00:00", "09:40:00", "10:00:00", "10:05:00"]
    st = pd.DataFrame(
        {
            "trip_id": ["ida", "ida", "vuelta", "vuelta", "otra", "otra"],
            "arrival_time": horas,
            "departure_time": horas,
            "stop_id": ["A", "B", "B", "A", "A", "m1"],
            "stop_sequence": ["0", "1", "0", "1", "0", "1"],
        }
    )
    salida = le.completar_viajes(trips, st, xy, {"R": ["A", "m1", "m2", "B"]})
    salida = salida.assign(seq=salida["stop_sequence"].astype(int)).sort_values(
        ["trip_id", "seq"]
    )
    paradas = salida.groupby("trip_id")["stop_id"].apply(list).to_dict()
    assert paradas == {
        "ida": ["A", "m1", "m2", "B"],
        "vuelta": ["B", "m2", "m1", "A"],
        "otra": ["A", "m1"],  # de otra ruta: intacto
    }
    hora = salida.groupby("trip_id")["arrival_time"].apply(list)
    assert hora["ida"] == ["08:00:00", "08:10:00", "08:30:00", "08:40:00"]
    assert hora["vuelta"] == ["09:00:00", "09:10:00", "09:30:00", "09:40:00"]


def test_completar_viajes_un_viaje_parcial_solo_recibe_su_tramo():
    xy = pd.DataFrame(
        {"x": [X0, X0 + 1000, X0 + 2000, X0 + 3000, X0 + 4000], "y": Y0},
        index=["A", "m1", "m2", "m3", "B"],
    )
    trips = pd.DataFrame({"trip_id": ["corto"], "route_id": ["R"]})
    st = pd.DataFrame(
        {
            "trip_id": ["corto", "corto"],
            "arrival_time": ["08:00:00", "08:20:00"],
            "departure_time": ["08:00:00", "08:20:00"],
            "stop_id": ["m3", "m1"],  # a mitad de línea y en sentido contrario
            "stop_sequence": ["0", "1"],
        }
    )
    salida = le.completar_viajes(trips, st, xy, {"R": ["A", "m1", "m2", "m3", "B"]})
    salida = salida.sort_values("stop_sequence")
    assert salida["stop_id"].tolist() == ["m3", "m2", "m1"]  # sin A ni B
    assert salida["arrival_time"].tolist() == ["08:00:00", "08:10:00", "08:20:00"]


def test_completar_tablas_sin_esas_rutas_no_toca_nada():
    tablas = {"trips.txt": b"route_id,trip_id\r\nS,t1\r\n"}
    assert le.completar_tablas(tablas, {"R": ["A", "B"]}) is tablas


def test_activos_cuenta_dia_de_la_semana_vigencia_altas_y_bajas(tmp_path):
    ruta = tmp_path / "gtfs.zip"
    dias = ",".join(le.SEMANA)
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr(
            "carpeta/calendar.txt",
            f"service_id,{dias},start_date,end_date\r\n"
            "LAB,1,1,1,1,1,0,0,20260101,20261231\r\n"
            "BAJA,1,1,1,1,1,0,0,20260101,20261231\r\n"
            "SAB,0,0,0,0,0,1,0,20260101,20261231\r\n"
            "VIEJO,1,1,1,1,1,0,0,20250101,20251231\r\n",
        )
        z.writestr(
            "carpeta/calendar_dates.txt",
            "service_id,date,exception_type\r\n"
            "BAJA,20261117,2\r\nSAB,20261117,1\r\nLAB,20261118,2\r\n",
        )
    assert le._activos(ruta, dt.date(2026, 11, 17)) == {"LAB", "SAB"}  # un martes
    with pytest.raises(FileNotFoundError, match="trips.txt"):
        le._leer(ruta, "trips.txt")


def test_feed_frecuencias_circular_en_un_sentido_y_lineal_en_dos():
    xy = pd.DataFrame(
        {"x": [X0, X0 + 3000, X0 + 3000, X0 + 100], "y": [Y0, Y0, Y0 + 3000, Y0]},
        index=["a", "b", "c", "a2"],
    )
    ref = pd.DataFrame(
        {"km": [6.0], "kmh": [30.0], "salidas": [4.0]}, index=["8__712___"]
    )
    circular = le._feed_frecuencias("8__721___", ["a", "b", "c", "a2"], xy, ref)
    assert len(circular["trips.txt"]) == 1
    assert circular["frequencies.txt"]["headway_secs"].tolist() == ["900"]
    lineal = le._feed_frecuencias("8__721___", ["a", "b", "c"], xy, ref)
    assert lineal["stop_times.txt"].groupby("trip_id")["stop_id"].apply(
        list
    ).tolist() == [
        ["a", "b", "c"],
        ["c", "b", "a"],
    ]
    # 3 km a 30 km/h: 6 min hasta «b»
    assert lineal["stop_times.txt"]["arrival_time"].tolist()[:2] == [
        "00:00:00",
        "00:06:00",
    ]
