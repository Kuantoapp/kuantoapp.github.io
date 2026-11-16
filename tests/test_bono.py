"""Tests de `mesobra.bono` con tablas pequeñas hechas a mano."""

import numpy as np
import pandas as pd
import pytest

from mesobra import bono, contratos

CSV = (
    "municipio_nombre;municipio;solicitudes;aceptadas;rechazadas\n"
    "Álamo, El;004;10;4;6\nMadrid;079;100;20;80\nOtro;-;5;0;5\n"
)


def _solicitudes():
    df = pd.DataFrame(
        {
            "municipio_id": ["28001", "28002", "28003", "28004"],
            "municipio_nombre": list("abcd"),
            "solicitudes": [10, 20, 30, 40],
            "aceptadas": [1, 5, 9, 0],
            "rechazadas": [9, 15, 21, 40],
        }
    )
    return pd.concat([df, pd.DataFrame({"municipio_id": [None], "solicitudes": [7]})])


def _poblacion(**cambios):
    datos = {"28001": 100, "28002": 200, "28003": 300, "28004": 100} | cambios
    return pd.Series(datos, name="poblacion_joven")


def _indicador(valores=(0.2, 0.3, np.nan, 0.5), nombre="esfuerzo"):
    return pd.Series(valores, index=["28001", "28002", "28003", "28004"], name=nombre)


def test_leer_bono(tmp_path):
    ruta = tmp_path / "bono.csv"
    ruta.write_bytes(CSV.encode("latin-1"))
    df = bono.leer_bono(ruta)
    assert df["municipio_id"].tolist()[:2] == ["28004", "28079"]
    assert df["municipio_id"].isna().tolist() == [False, False, True]
    ruta.write_bytes(CSV.replace("100;20;80", "100;20;70").encode("latin-1"))
    with pytest.raises(ValueError, match="solicitudes"):
        bono.leer_bono(ruta)


def test_poblacion_joven(tmp_path):
    ruta = tmp_path / "censo.csv"
    filas = ["Total Nacional;28 Madrid;28001 A;Total;%s;%s;%s"]
    lineas = [
        f % (e, a, v)
        for f in filas
        for e, a, v in [
            ("17 años", 2023, "9"),
            ("18 años", 2023, "1.000"),
            ("35 años", 2023, "20"),
            ("36 años", 2023, "9"),
            ("20 años", 2022, "9"),
            ("Todas las edades", 2023, "9"),
        ]
    ]
    lineas += ["Total Nacional;28 Madrid;28001 A;Hombres;20 años;2023;9"]
    lineas += ["Total Nacional;08 Barcelona;08019 B;Total;20 años;2023;9"]
    ruta.write_text(
        "Total Nacional;Provincias;Municipios;Sexo;Edad;Periodo;Total\n"
        + "\n".join(lineas)
    )
    pob = bono.poblacion_joven(bono._edades(ruta, 2023))
    assert pob.to_dict() == {"28001": 1020}


def test_bono_cruza_y_calcula():
    tabla = bono.bono(_solicitudes(), _poblacion(), _indicador())
    contratos.validar(tabla, "bono")
    assert len(tabla) == 4
    assert tabla["necesidad"].iloc[0] == pytest.approx(20)
    assert tabla["necesidad"].isna().tolist() == [False, False, True, False]
    assert tabla.loc[2, "grupo"] == "sin_dato"
    # por joven 0,2 / 0,3 / 0,5 y aceptadas por mil 10 / 25 / 0 entre los que tienen dato
    assert tabla.loc[[0, 1, 3], "grupo"].tolist() == [
        "necesidad_baja_ayuda_media",
        "necesidad_media_ayuda_alta",
        "necesidad_alta_ayuda_baja",
    ]


def test_bono_indicador_y_poblacion():
    tabla = bono.bono(_solicitudes(), _poblacion(), _indicador(nombre="sobrecarga"))
    assert set(tabla["indicador_necesidad"]) == {"sobrecarga"}
    with pytest.raises(ValueError, match="indicador"):
        bono.bono(_solicitudes(), _poblacion(), _indicador(nombre="otro"))
    with pytest.raises(ValueError, match="sin población"):
        bono.bono(_solicitudes(), _poblacion().drop("28004"), _indicador())


def test_terciles():
    t = bono.terciles(pd.Series(range(9)))
    assert t.value_counts().to_dict() == {"baja": 3, "media": 3, "alta": 3}
    empate = bono.terciles(pd.Series([0, 0, 0, 0, 1, 2]))
    assert empate.tolist().count("baja") >= 4  # los empates caen en el grupo inferior
    con_nulo = bono.terciles(pd.Series([1, np.nan, 2, 3]))
    assert pd.isna(con_nulo[1]) and con_nulo.notna().sum() == 3


def test_por_mil_y_tope():
    tabla = bono.bono(_solicitudes(), _poblacion(), _indicador())
    mil = bono.por_mil(tabla)
    assert mil["aceptadas_por_mil"].iloc[0] == pytest.approx(10)
    assert mil["tasa_aceptacion"].iloc[1] == pytest.approx(0.25)
    assert bono.tope_eur(pd.Index(["28079", "28001"])).tolist() == [900, 600]


def _datos(n=200, semilla=0):
    rng = np.random.default_rng(semilla)
    z = rng.normal(size=(n, 2))
    return z, rng


def test_correlacion_parcial():
    z, rng = _datos()
    ctrl = pd.DataFrame(z, columns=["a", "b"])
    x = pd.Series(z[:, 0] + rng.normal(size=200))
    y = pd.Series(z[:, 0] + rng.normal(size=200))
    # con z fuera, x e y comparten solo ruido independiente: r pequeña
    res = bono.correlacion_parcial(x, y, ctrl)
    assert abs(res["r"]) < 0.2 and res["k"] == 2 and res["n"] == 200
    assert res["ic95"][0] < res["r"] < res["ic95"][1]
    assert bono.correlacion_parcial(x, x, ctrl)["r"] == pytest.approx(1)
    # sin controlar, el mismo par sí correlaciona: el control quita lo compartido
    sin = bono.correlacion_parcial(x, y, ctrl.assign(a=0.0, b=0.0))
    assert sin["r"] > 0.3


def test_correlacion_parcial_nulos_y_rangos():
    z, rng = _datos()
    ctrl = pd.DataFrame(z[:, :1], columns=["a"])
    x = pd.Series(rng.normal(size=200))
    y = np.exp(x) + 0.0
    x.iloc[:5] = np.nan
    res = bono.correlacion_parcial(x, y, ctrl)
    assert res["n"] == 195 and res["k"] == 1
    mono = bono.correlacion_parcial(x.rank(), y.rank(), ctrl.rank())
    assert mono["r"] == pytest.approx(
        bono.correlacion_parcial(x.rank(), np.exp(y).rank(), ctrl.rank())["r"]
    )
    with pytest.raises(ValueError, match="Faltan datos"):
        bono.correlacion_parcial(x.iloc[:5], y.iloc[:5], ctrl.iloc[:5])


def _rejilla(n=8):
    return np.array([(i, j) for i in range(n) for j in range(n)], float)


def test_moran():
    xy = _rejilla()
    gradiente = bono.moran(xy[:, 0], xy, 4)
    assert gradiente["I"] > 0.5 and gradiente["p"] < 0.05
    tablero = bono.moran((xy[:, 0] + xy[:, 1]) % 2, xy, 4)
    assert tablero["I"] < 0
    vecinos = bono._vecinos(xy, 4)
    assert vecinos.shape == (64, 4)
    assert not (vecinos == np.arange(64)[:, None]).any()  # nadie es vecino de sí mismo


def test_validacion_devuelve_las_tres_y():
    rng = np.random.default_rng(1)
    ids = [f"28{i:03d}" for i in range(60)]
    jov = pd.Series(rng.integers(100, 1000, 60), index=ids, name="poblacion_joven")
    ind = pd.Series(rng.uniform(0.1, 0.5, 60), index=ids, name="esfuerzo")
    acept = rng.integers(0, 20, 60)
    sol = pd.DataFrame(
        {
            "municipio_id": ids,
            "solicitudes": acept + 10,
            "aceptadas": acept,
            "rechazadas": 10,
        }
    )
    tabla = bono.bono(sol, jov, ind)
    renta = pd.Series(rng.uniform(2e4, 5e4, 60), index=ids)
    xy = pd.DataFrame(rng.uniform(0, 1e4, (60, 2)), index=ids, columns=["x", "y"])
    res = bono.validacion(tabla, renta, xy)
    assert set(res) == set(bono.Y)
    assert set(res["rechazadas_por_mil"]) == {
        "pearson",
        "spearman",
        "moran_k5",
        "moran_k8",
    }
    assert res["rechazadas_por_mil"]["pearson"]["n"] == 60


def test_tope_900_en_el_csv_real():
    if not bono.BONO.exists():
        pytest.skip("falta data/raw")
    df = bono.leer_bono().dropna(subset=["municipio_id"]).set_index("municipio_id")
    assert len(bono.TOPE_900) == 29
    assert df.loc[list(bono.TOPE_900), "municipio_nombre"].tolist() == list(
        bono.TOPE_900.values()
    )
