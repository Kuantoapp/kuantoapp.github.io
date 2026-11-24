"""Tests de `matriz_trabajo` (#301) con un fragmento sintético en el formato de la hoja C23 del INE."""

import pandas as pd
import pytest

from mesobra import matriz_trabajo


def _hoja(filas: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(filas, columns=matriz_trabajo.COLUMNAS)


FILAS = [
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "079", "Madrid", "38887"),
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "092", "Móstoles", "13567"),
    ("28", "Madrid", "092", "Móstoles", "28", "Madrid", "No consta", None, "4952"),
    ("28", "Madrid", "092", "Móstoles", "08", "Barcelona", "019", "Barcelona", "10"),
    ("28", "Madrid", "092", "Móstoles", "No consta", None, "No consta", None, "598"),
    (
        "01",
        "Araba/Álava",
        "001",
        "Alegría-Dulantzi",
        "28",
        "Madrid",
        "079",
        "Madrid",
        "8",
    ),
]


def test_ordenar_solo_origen_en_la_comunidad_y_no_consta_nulo():
    df = matriz_trabajo.ordenar(_hoja(FILAS))
    assert df["origen"].tolist() == ["28092"] * 5
    assert df["destino"].tolist()[:2] == ["28079", "28092"]
    assert df["destino"].iloc[2:].isna().tolist() == [True, False, True]
    assert df["destino"].iloc[3] == "08019"
    assert df["prov_destino"].isna().tolist() == [False, False, False, False, True]
    assert df["ocupados"].sum() == 38887 + 13567 + 4952 + 10 + 598


def test_ordenar_falla_con_ocupados_no_numericos_o_sin_columna():
    with pytest.raises(ValueError, match="no enteros"):
        matriz_trabajo.ordenar(_hoja([(*FILAS[0][:8], "..")]))
    with pytest.raises(ValueError, match="columnas"):
        matriz_trabajo.ordenar(_hoja(FILAS).drop(columns="Municipio de trabajo"))


def test_leer_matriz_falla_si_no_estan_los_179_municipios(monkeypatch):
    monkeypatch.setattr(pd, "read_excel", lambda *a, **k: _hoja(FILAS))
    with pytest.raises(ValueError, match="179"):
        matriz_trabajo.leer_matriz()


def test_ordenar_falla_con_ocupados_decimales():
    with pytest.raises(ValueError, match="no enteros"):
        matriz_trabajo.ordenar(_hoja([(*FILAS[0][:8], "12.5")]))


def test_entradas_suma_todos_los_origenes_y_quita_no_consta():
    e = matriz_trabajo.entradas(_hoja(FILAS))
    assert e.to_dict() == {"28079": 38887 + 8, "28092": 13567}


def _afiliacion(tmp_path, filas: list[tuple]):
    cab = "Año;Tipo territorio;Código territorio;Territorio;Régimen;Valor;Unidad;Estado dato"
    lineas = [cab] + [";".join(map(str, f)) + ";Número;" for f in filas]
    ruta = tmp_path / "afil.csv"
    ruta.write_text("\n".join(lineas), encoding="utf-8-sig")
    return ruta


def _filas_afiliacion(n: int = matriz_trabajo.MUNICIPIOS) -> list[tuple]:
    filas = [
        (2022, "Municipios", f"{i:03d}{i % 10}", "x", r, 10)
        for i in range(1, n + 1)
        for r in ("general", "autónomos")
    ]
    filas.append((2022, "Municipios", "9999", "Sin municipio asignado", "general", 6))
    filas.append((2022, "Comunidad de Madrid", "", "Comunidad", "general", 20 * n + 6))
    return [*filas, (2021, "Municipios", "0014", "x", "general", 99)]


def test_leer_afiliacion_centro_suma_regimenes_y_quita_sin_municipio(tmp_path):
    ruta = _afiliacion(tmp_path, _filas_afiliacion())
    a = matriz_trabajo.leer_afiliacion_centro(ruta)
    assert len(a) == matriz_trabajo.MUNICIPIOS
    assert a["28001"] == 20
    assert a.sum() == 20 * matriz_trabajo.MUNICIPIOS


def test_leer_afiliacion_centro_falla_si_faltan_municipios_o_no_cuadra(tmp_path):
    with pytest.raises(ValueError, match="179"):
        matriz_trabajo.leer_afiliacion_centro(
            _afiliacion(tmp_path, _filas_afiliacion(178))
        )
    filas = [
        (*f[:5], 1) if f[1] == "Comunidad de Madrid" else f for f in _filas_afiliacion()
    ]
    with pytest.raises(ValueError, match="no cuadra"):
        matriz_trabajo.leer_afiliacion_centro(_afiliacion(tmp_path, filas))


def _edm(distritos: range = range(1, 22)) -> dict[str, pd.DataFrame]:
    """Una persona por distrito de trabajo, en el hogar 1 (Ajalvir), más los casos que deben quedar fuera."""
    cols = ["ID_HOGAR", "ID_IND", "C8ACTIV", "C9PROF", "C11ZT1259", "ELE_G_POND"]
    filas = [("1", str(d), "1", "2", f"079-{d:02d}-001", "10") for d in distritos]
    filas += [
        (
            "2",
            "1",
            "2",
            "3",
            "079-02-001",
            "30",
        ),  # trabaja y estudia, cuenta propia, en su zona
        ("3", "1", "6", "", "079-03-001", "50"),  # estudiante: no trabaja
        ("4", "1", "1", "2", "002-002", "70"),  # trabaja fuera de Madrid
    ]
    hogares = pd.DataFrame(
        [
            ("1", "002", "002-002"),
            ("2", "079", "079-02-001"),
            ("3", "079", "079-05-001"),
        ]
        + [("4", "079", "079-05-001")],
        columns=["ID_HOGAR", "CODMUNI", "ZT1259"],
    )
    return {"INDIVIDUOS": pd.DataFrame(filas, columns=cols), "HOGARES": hogares}


def _leer(tablas: dict[str, pd.DataFrame]):
    return lambda _ruta, hoja, **_k: tablas[hoja]


def test_leer_edm_trabajo_solo_quien_trabaja_en_madrid(monkeypatch):
    monkeypatch.setattr(pd, "read_excel", _leer(_edm()))
    e = matriz_trabajo.leer_edm_trabajo()
    assert len(e) == 22
    assert e["peso"].sum() == 21 * 10 + 30
    quien = e[e["hogar"] == "2"].iloc[0]
    assert quien["municipio"] == "28079"
    assert bool(quien["cuenta_propia"]) and bool(quien["en_casa"])
    assert not e.loc[e["hogar"] == "1", "en_casa"].any()
    c = matriz_trabajo.cuotas_edm(e)
    assert c.sum() == pytest.approx(1)
    assert c["2807902"] == pytest.approx(40 / 240)


def test_leer_edm_trabajo_falla_si_falta_un_distrito_o_un_hogar(monkeypatch):
    tablas = _edm(range(2, 22))
    monkeypatch.setattr(pd, "read_excel", _leer(tablas))
    with pytest.raises(ValueError, match="21"):
        matriz_trabajo.leer_edm_trabajo()
    tablas = _edm()
    tablas["HOGARES"] = tablas["HOGARES"].iloc[1:]
    monkeypatch.setattr(pd, "read_excel", _leer(tablas))
    with pytest.raises(ValueError, match="sin hogar"):
        matriz_trabajo.leer_edm_trabajo()


def test_leer_afiliacion_cuenta_une_por_nombre_y_quita_no_distribuidos(tmp_path):
    nombres = [f"Municipio {i}" for i in range(1, matriz_trabajo.MUNICIPIOS + 1)]
    filas_centro = [
        (*f[:3], nombres[int(f[2][:3]) - 1], *f[4:]) if f[2] not in ("9999", "") else f
        for f in _filas_afiliacion()
    ]
    centro = _afiliacion(tmp_path, filas_centro)
    cuenta = tmp_path / "cuenta.csv"
    lineas = ["Año;Periodo;Territorio;Indicador;Valor;Unidad;Estado dato"]
    lineas += [f"2022;M12;{n.upper()};Serie;5.0;Personas;" for n in nombres]
    lineas += [
        "2022;M12;No distribuidos;Serie;7.0;Personas;",
        "2022;M11;Municipio 1;Serie;9.0;Personas;",
    ]
    cuenta.write_text("\n".join(lineas), encoding="utf-8-sig")
    a = matriz_trabajo.leer_afiliacion_cuenta(cuenta, centro)
    assert len(a) == matriz_trabajo.MUNICIPIOS
    assert a["28001"] == 5
    cuenta.write_text(
        "\n".join([*lineas, "2022;M12;Otro;Serie;1.0;Personas;"]), encoding="utf-8-sig"
    )
    with pytest.raises(ValueError, match="sin código"):
        matriz_trabajo.leer_afiliacion_cuenta(cuenta, centro)


def test_disimilitud_cero_entre_iguales_y_uno_entre_disjuntos():
    a = pd.Series({"x": 1.0, "y": 0.0})
    assert matriz_trabajo.disimilitud(a, a) == 0
    assert matriz_trabajo.disimilitud(a, pd.Series({"x": 0.0, "y": 1.0})) == 1
