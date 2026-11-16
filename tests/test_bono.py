"""Tests de `mesobra.bono` con tablas pequeñas hechas a mano."""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

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
    for malo in ("X;;1;1;0", "X;12;1;1;0", "X;abc;1;1;0"):
        ruta.write_bytes((CSV + malo + "\n").encode("latin-1"))
        with pytest.raises(ValueError, match="no válidos"):
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
    # los empates caen en el grupo inferior
    assert empate.tolist() == ["baja"] * 4 + ["alta"] * 2
    con_nulo = bono.terciles(pd.Series([1, np.nan, 2, 3]))
    assert pd.isna(con_nulo[1]) and con_nulo.notna().sum() == 3


def test_por_mil_y_tope():
    tabla = bono.bono(_solicitudes(), _poblacion(), _indicador())
    mil = bono.por_mil(tabla)
    assert mil["aceptadas_por_mil"].iloc[0] == pytest.approx(10)
    assert mil["tasa_aceptacion"].iloc[1] == pytest.approx(0.25)
    assert bono.tope_eur(pd.Index(["28079", "28001"])).tolist() == [900, 600]
    # solo están en la lista de 2024, no en la de 2022
    solo_2024 = pd.Index(["28002", "28013", "28045", "28096"])
    assert (bono.tope_eur(solo_2024) == 600).all()
    assert (bono.tope_eur(pd.Index(["28127", "28903", "28123"])) == 900).all()


def test_renta_catalogo(tmp_path):
    ruta = tmp_path / "irpf.csv"
    ruta.write_text(
        "Año;Tipo territorio;Código territorio;Territorio;Medida;Valor;Unidad;Estado dato\n"
        "2023;Municipios;0796;Madrid;Per cápita;30000;Euros;\n"
        "2023;Municipios;0014;Acebeda;Per cápita;-;Euros;\n"
        "2023;Municipios;0796;Madrid;Total;5;Euros;\n",
        encoding="utf-8-sig",
    )
    assert bono._renta_catalogo(ruta, 2023).to_dict() == {"28079": 30000.0}


def test_comprobar_nombres():
    edades = pd.DataFrame({"municipio_id": ["28004"], "nombre": ["Álamo, El"]})
    solicitudes = pd.DataFrame(
        {"municipio_id": ["28004"], "municipio_nombre": ["álamo, el "]}
    )
    bono._comprobar_nombres(solicitudes, edades)
    with pytest.raises(ValueError, match="no coinciden"):
        bono._comprobar_nombres(solicitudes.assign(municipio_nombre="Otro"), edades)


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
    colineal = pd.Series(2 * ctrl["a"] + 1)
    with pytest.raises(ValueError, match="colineal"):
        bono.correlacion_parcial(colineal, y, ctrl)
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


def test_moran_igual_que_w_densa():
    rng = np.random.default_rng(3)
    xy, v = rng.uniform(0, 10, (30, 2)), rng.normal(size=30)
    dist = np.linalg.norm(xy[:, None] - xy[None], axis=2)
    corte = np.sort(dist, axis=1)[
        :, 4:5
    ]  # la distancia al 4.º vecino (la 0 es él mismo)
    w = ((dist <= corte) & (dist > 0)).astype(float)
    w /= w.sum(axis=1, keepdims=True)
    z = v - v.mean()
    assert bono.moran(v, xy, 4)["I"] == pytest.approx(
        len(z) / w.sum() * (z @ w @ z) / (z @ z)
    )


def test_bayes_empirico():
    p = pd.Series([10.0, 10000.0, 500.0, 800.0])
    c = pd.Series([5.0, 1000.0, 20.0, 100.0])
    eb, tasa, m = bono.bayes_empirico(c, p), c / p, c.sum() / p.sum()
    assert abs(eb[0] - m) < abs(tasa[0] - m) / 2  # el pequeño se acerca a la media
    assert abs(eb[1] - tasa[1]) < 0.01 * abs(tasa[1])  # el grande casi no cambia


def test_validacion():
    rng = np.random.default_rng(1)
    ids = [f"28{i:03d}" for i in range(40, 100)]  # incluye Madrid (28079)
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
    pr = res["rechazadas_por_mil"]
    assert set(pr) == {
        "pearson",
        "spearman",
        "moran_k5",
        "moran_k8",
        "moran_x_k5",
        "moran_x_k8",
    }
    assert pr["pearson"]["n"] == 60
    t = tabla.set_index("municipio_id")
    x = t["necesidad"] / t["poblacion_joven"]
    y = bono.por_mil(t)["rechazadas_por_mil"]
    ctrl = pd.DataFrame({"renta": renta, "tope": bono.tope_eur(t.index)})
    assert pr["pearson"]["r"] == pytest.approx(
        bono.correlacion_parcial(x, y, ctrl)["r"]
    )
    # la p de la parcial es la del t del coeficiente de x en el MCO de y sobre 1, x y los controles
    z = np.column_stack([np.ones(60), x, ctrl])
    beta = np.linalg.lstsq(z, y.to_numpy(), rcond=None)[0]
    e = y.to_numpy() - z @ beta
    se = np.sqrt(e @ e / (60 - 4) * np.linalg.inv(z.T @ z)[1, 1])
    assert pr["pearson"]["p"] == pytest.approx(2 * stats.t.sf(abs(beta[1] / se), 56))
    res_x = bono._residuos(x, ctrl)
    assert pr["moran_x_k5"]["I"] == pytest.approx(
        bono.moran(res_x, xy.to_numpy(float), 5)["I"]
    )
    # el prior se calcula sin Madrid, que conserva su tasa sin suavizar
    otros = t.index != bono.MADRID
    eb = 1000 * bono.bayes_empirico(
        t.loc[otros, "rechazadas"], t.loc[otros, "poblacion_joven"]
    )
    eb[bono.MADRID] = y[bono.MADRID]
    assert not np.isclose(
        eb.drop(bono.MADRID),
        1000
        * bono.bayes_empirico(t["rechazadas"], t["poblacion_joven"]).drop(bono.MADRID),
    ).all()
    assert res["rechazadas_por_mil_eb"]["pearson"]["r"] == pytest.approx(
        bono.correlacion_parcial(x, eb, ctrl)["r"]
    )
    with pytest.raises(ValueError, match="sin renta"):
        bono.validacion(tabla, renta.drop(ids[0]), xy)


def test_tope_900_en_el_csv_real():
    if not bono.BONO.exists():
        pytest.skip("falta data/raw")
    df = bono.leer_bono().dropna(subset=["municipio_id"]).set_index("municipio_id")
    assert len(bono.TOPE_900) == 29
    assert df.loc[list(bono.TOPE_900), "municipio_nombre"].tolist() == list(
        bono.TOPE_900.values()
    )
