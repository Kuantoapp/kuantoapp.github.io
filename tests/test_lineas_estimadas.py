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
    tablas = {
        "trips.txt": b"route_id,trip_id,service_id,direction_id\r\nS,t1,L,0\r\n",
        "stop_times.txt": (
            b"trip_id,arrival_time,departure_time,stop_id,stop_sequence\r\n"
            b"t1,08:00:00,08:00:00,A,0\r\nt1,08:10:00,08:10:00,B,1\r\n"
        ),
        # sin `location_type`, como el de Cercanías
        "stops.txt": b"stop_id,stop_lon,stop_lat\r\nA,-3.7,40.4\r\n",
    }
    assert le.completar_tablas(tablas, {"R": ["A", "B"]}) is tablas


COLS = ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"]
XY3 = pd.DataFrame(
    {"x": [X0, X0 + 3000, X0 + 7000], "y": [Y0, Y0, Y0]}, index=["p", "q", "r"]
)
RELLENO3 = ("01:00:00", "01:00:00", "01:00:00")


def _viaje(trip_id: str, horas: tuple[str, ...]) -> list[tuple[str, ...]]:
    return [
        (trip_id, h, h, s, str(i))
        for i, (s, h) in enumerate(zip("pqr", horas, strict=True))
    ]


def _escenario(*viajes: tuple[str, str, tuple[str, ...]]):
    """Una línea real (30 km/h: 3 km en 6 min, 7 km en 14) y los viajes `(trip_id, route_id, horas)` dados."""
    filas = _viaje("t1", ("07:40:00", "07:46:00", "07:54:00"))
    rutas = {"t1": "8__101___"}
    for trip_id, route_id, horas in viajes:
        filas += _viaje(trip_id, horas)
        rutas[trip_id] = route_id
    trips = pd.DataFrame(
        {
            "trip_id": list(rutas),
            "route_id": list(rutas.values()),
            "service_id": "L",
            "direction_id": "0",
        }
    )
    return trips, pd.DataFrame(filas, columns=COLS)


def _horas(st: pd.DataFrame, trip_id: str) -> list[str]:
    q = st[st["trip_id"] == trip_id].sort_values("stop_sequence")
    return q["departure_time"].tolist()


def test_rellenar_horarios_usa_la_salida_del_trip_id_y_la_velocidad_de_las_parecidas():
    largo, corto = "x_8__102___-1_06:56:00_1_-__1", "x_8__102___-1_620"
    trips, st = _escenario(
        (largo, "8__102___", RELLENO3), (corto, "8__102___", RELLENO3)
    )
    salida = le.rellenar_horarios(trips, st, XY3)
    assert _horas(salida, largo) == ["06:56:00", "07:02:00", "07:10:00"]
    assert _horas(salida, corto) == ["06:20:00", "06:26:00", "06:34:00"]  # hora corta
    assert _horas(salida, "t1") == ["07:40:00", "07:46:00", "07:54:00"]


def test_rellenar_horarios_sin_nada_que_hacer_devuelve_el_mismo_objeto():
    trips, st = _escenario()
    assert le.rellenar_horarios(trips, st, XY3) is st


def test_rellenar_horarios_falla_si_no_hay_hora_valida_o_viaje():
    trips, st = _escenario(("x_8__102___-sin_hora", "8__102___", RELLENO3))
    with pytest.raises(ValueError, match="sin hora"):
        le.rellenar_horarios(trips, st, XY3)
    for imposible in (
        "x_8__102___-1_2075",
        "x_8__102___-1_9915",
        "x_8__102___-1_99:15:00_",
    ):
        trips, st = _escenario((imposible, "8__102___", RELLENO3))
        with pytest.raises(ValueError, match="Hora imposible"):
            le.rellenar_horarios(trips, st, XY3)
    trips, st = _escenario(("x_8__102___-1_620", "8__102___", RELLENO3))
    with pytest.raises(ValueError, match="no están en trips.txt"):
        le.rellenar_horarios(trips[trips["trip_id"] == "t1"], st, XY3)


def test_rellenar_horarios_no_toca_los_viajes_con_solo_la_primera_parada_de_relleno():
    # la 483: primera parada a 01:00:01 y el resto con horas reales; es de #349, no se reconstruye
    parcial = "x_8__483___-1_07:30:00_1_-__1"
    recorrido = ("01:00:01", "07:30:51", "07:32:06")
    trips, st = _escenario((parcial, "8__483___", recorrido))
    assert le.rellenar_horarios(trips, st, XY3) is st


def test_hhmmss_rechaza_segundos_negativos_o_no_finitos():
    assert le._hhmmss(np.array([0.0, 3661.0])) == ["00:00:00", "01:01:01"]
    for malo in (-4500.0, np.nan, np.inf):
        with pytest.raises(ValueError, match="Segundos"):
            le._hhmmss(np.array([malo]))


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
