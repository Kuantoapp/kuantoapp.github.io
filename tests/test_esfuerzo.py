"""Tests de `mesobra.esfuerzo` con tablas pequeñas hechas a mano."""

from pathlib import Path

import pandas as pd
import pytest

from mesobra import contratos, esfuerzo

FIXTURES = Path(__file__).parent / "fixtures/processed"


def _tabla(nombre, columnas, filas, **fijas):
    df = pd.DataFrame(filas, columns=columnas).assign(**fijas)
    df = df.reindex(columns=list(contratos.CONTRATOS[nombre]["columnas"]))
    return df.astype(contratos.dtypes(nombre))


def _alquiler(filas):
    """Filas (zona_id, anio, cuantia_p50); nulo = sin_dato. €/m² × m² (1200) no es la cuantía."""
    df = pd.DataFrame(filas, columns=["zona_id", "anio", "cuantia_p50"])
    origen = df["cuantia_p50"].notna().map({True: "observado", False: "sin_dato"})
    return _tabla(
        "alquiler_zona",
        df.columns,
        df.values.tolist(),
        origen=origen,
        eur_m2_p50=20.0,
        m2_p50=60.0,
    )


def _renta(filas, nivel="zona"):
    """Filas (unidad_id, anio, renta_hogar, poblacion)."""
    columnas = ["unidad_id", "anio", "renta_hogar", "poblacion"]
    return _tabla("renta", columnas, filas, nivel=nivel)


def _fila(tabla, zona, anio):
    return tabla[(tabla["zona_id"] == zona) & (tabla["anio"] == anio)].iloc[0]


def test_caso_a_mano():
    tabla = esfuerzo.esfuerzo(
        _alquiler([("28001", 2024, 900.0)]),
        _renta([("28001", 2024, 36000, 5000)]),
    )
    fila = tabla.iloc[0]
    assert fila["alquiler_mes_p50"] == pytest.approx(900)
    assert fila["renta_hogar_mes"] == pytest.approx(3000)
    assert fila["esfuerzo"] == pytest.approx(0.30)


def test_sin_alquiler_esfuerzo_nulo():
    tabla = esfuerzo.esfuerzo(
        _alquiler([("28001", 2024, None)]),
        _renta([("28001", 2024, 36000, 5000)]),
    )
    assert pd.isna(tabla.loc[0, "esfuerzo"])
    assert tabla.loc[0, "renta_hogar_mes"] == pytest.approx(3000)


def test_renta_comun_de_zonas_pequenas():
    alquiler = _alquiler(
        [
            ("28001", 2019, 600.0),
            ("28001", 2020, 600.0),
            ("28002", 2020, 600.0),
        ]
    )
    renta = _renta(
        [
            ("28001", 2019, 36000, 60),
            ("28001", 2020, 36000, 60),
            ("28002", 2020, 36000, None),
        ]
    )
    tabla = esfuerzo.esfuerzo(alquiler, renta)
    assert pd.isna(_fila(tabla, "28001", 2020)["esfuerzo"])
    assert _fila(tabla, "28001", 2020)["renta_hogar_mes"] == pytest.approx(3000)
    assert _fila(tabla, "28001", 2019)["esfuerzo"] == pytest.approx(0.20)
    assert _fila(tabla, "28002", 2020)["esfuerzo"] == pytest.approx(0.20)


def test_ventana_comun_y_nivel():
    alquiler = _alquiler([("28001", 2014, 600.0), ("28001", 2015, 600.0)])
    renta = pd.concat(
        [
            _renta([("28001", 2015, 36000, 5000)]),
            _renta([("28001", 2015, 36000, 5000)], nivel="seccion"),
        ]
    )
    tabla = esfuerzo.esfuerzo(alquiler, renta)
    assert list(tabla["anio"]) == [2015]
    assert len(tabla) == 1


def test_cambio():
    tabla = pd.DataFrame(
        {
            "zona_id": ["a", "a", "b", "b", "c", "c"],
            "anio": [2015, 2024, 2015, 2024, 2015, 2024],
            "esfuerzo": [0.20, 0.30, 0.25, None, None, 0.40],
        }
    )
    resultado = esfuerzo.cambio(tabla)
    assert resultado["a"] == pytest.approx(0.10)
    assert pd.isna(resultado["b"]) and pd.isna(resultado["c"])


def test_cambio_exige_dos_anios():
    tabla = pd.DataFrame({"zona_id": ["a"], "anio": [2024], "esfuerzo": [0.3]})
    with pytest.raises(ValueError, match="dos años"):
        esfuerzo.cambio(tabla)


def test_fixtures_dan_el_esfuerzo_esperado():
    def leer(nombre):
        return pd.read_csv(FIXTURES / f"{nombre}.csv", dtype=contratos.dtypes(nombre))

    tabla = esfuerzo.esfuerzo(leer("alquiler_zona"), leer("renta"))
    esperado = leer("esfuerzo").sort_values(esfuerzo.CLAVE).reset_index(drop=True)
    pd.testing.assert_frame_equal(tabla, esperado, atol=0.01, rtol=0)
